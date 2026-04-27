from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

router_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert intent classifier for a RAG system. "
               "The user has uploaded documents (PDFs) to a knowledge base. "
               "Your goal is to decide if the user's question requires searching these documents."
               "\n\nCLASSIFICATION CRITERIA:"
               "\n- 'technical': Any question asking for facts, summaries, 'what is this about', "
               "details from 'the report', 'the project', or 'the uploaded file'."
               "\n- 'conversational': Greetings, small talk, or meta-comments about the chat itself."
               "\n\nIf the user refers to 'this', 'it', or 'the project', ASSUME they mean the PDF."),
    ("human", "{question}")
])

query_analysis_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You analyze technical questions for a grounded SEC 10-Q filing assistant. "
        "Extract structured query information only. Do not answer the question.\n\n"
        "Return:\n"
        "- question_type: one of fact_lookup, metric_lookup, performance_summary, risk_or_disclosure, general_technical\n"
        "- coverage_type: one of default_technical, focused_lookup, retrieval_heavy, token_heavy, computation_heavy\n"
        "- scope_type: one of current_filing, single_company, multi_company_comparison, market_wide, aggregate, unknown\n"
        "- query_tickers: uppercase ticker symbols explicitly mentioned or clearly implied by a well-known company name\n"
        "- query_year: explicit year if requested, otherwise null\n"
        "- query_period: only Q1, Q2, or Q3 if explicitly requested, otherwise null\n"
        "- multi_question: true only if the user asks multiple distinct filing questions\n"
        "- focus_terms: a short list of high-signal financial search terms or segment names\n\n"
        "Coverage type guidance for this first pass:\n"
        "- default_technical: use when uncertain, unsupported, ambiguous, cross-company, multi-filing, market-wide, aggregate, or otherwise risky to specialize.\n"
        "- focused_lookup: one bounded fact, metric, section, or short explanation from a single filing.\n"
        "- retrieval_heavy: broader evidence gathering within a single filing, usually across multiple passages or sections, without deterministic arithmetic.\n"
        "- token_heavy: long-form single-filing synthesis that needs more evidence and context compression before answering.\n"
        "- computation_heavy: deterministic arithmetic over explicit facts from a single filing.\n\n"
        "Guidance:\n"
        "- Use safe company-to-ticker mappings only when unambiguous.\n"
        "- Microsoft -> MSFT, Nvidia -> NVDA, Apple -> AAPL.\n"
        "- Google or Alphabet -> GOOG and GOOGL.\n"
        "- Do not guess a ticker if the company is unclear.\n"
        "- Use current_filing when the user refers implicitly to the active filing without naming a company.\n"
        "- Use multi_company_comparison only for bounded comparisons between specific companies.\n"
        "- Use market_wide for ranking or market-level questions like 'top companies' or 'most profitable companies'.\n"
        "- Use aggregate for questions asking for averages, totals, medians, or other rolled-up statistics across companies.\n"
        "- This phase supports only single-filing specialization. If the request is not clearly a single-filing task, use default_technical.\n"
        "- If you are unsure between a specialized coverage type and the baseline path, use default_technical.\n"
        "- Keep focus_terms concise and useful for retrieval."
    ),
    ("human", "{question}"),
])

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. "
        "If context is provided, use it to answer the question accurately. "
        "If no useful context exists or context is empty, answer normally. "
        "When context is provided, cite factual claims with the source IDs exactly as given, for example [S1] or [S2]. "
        "Do not invent citation IDs. "
        "If context exists but does not contain the answer, reply: 'Not found in context'."
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "Question: {question}\n\nContext:\n{context}")
])

re_write_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert at query expansion and search optimization. "
        "Your goal is to create a single, standalone search query for a vector database. "
        "\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Incorporate conversation history to resolve context (names, dates).\n"
        "2. If a 'Failure Reason' is provided, adapt your query to solve that specific issue:\n"
        "   - If documents were missing: Broaden search terms/use synonyms.\n"
        "   - If hallucination occurred: Add keywords for factual grounding.\n"
        "   - If not useful: Focus more on the specific user intent.\n"
        "3. Do not answer the question; only output the optimized query."
    ),
    MessagesPlaceholder(variable_name="history"),
    (
        "human", 
        "Failure Reason: {reason}\n\n"
        "Original Question: {question}\n\n"
        "Provide the optimized standalone search query:"
    )
])

# Prompt 1: Document Relevance
# Logic: Does the PDF match the User Question?
grader_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a grader assessing relevance of a retrieved document to a user question. "
               "If the document contains keyword(s) or semantic meaning related to the question, "
               "grade it as relevant. Give a binary score 'yes' or 'no'."),
    ("human", "Retrieved document: \n\n {context} \n\n User question: {question}"),
])

# Prompt 2: Hallucination Check
# Logic: Does the Answer match the Documents?
hallucination_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. "
               "Give a binary score 'yes' or 'no'. 'yes' means the answer is grounded in the facts."),
    ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
])

# Prompt 3: Answer Utility
# Logic: Does the Answer match the Question?
answer_grader_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a grader assessing whether an LLM generation is useful to the user. "
               "If the answer is 'I don't know', 'not found', or 'Not found in context', grade it as 'no'."
               "If it answers the question, grade it as 'yes'."),
    ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
])

context_compression_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You compress evidence from a single SEC filing for a downstream answer step. "
        "Keep only evidence that directly helps answer the user's question. "
        "Preserve source IDs exactly as given, such as [S1] or [S2]. "
        "Do not answer the question directly. "
        "Output concise evidence bullets with source IDs."
    ),
    ("human", "Question: {question}\n\nEvidence:\n{context}"),
])

computation_extraction_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You extract numeric facts from a single SEC filing context for deterministic computation. "
        "Use only facts explicitly supported by the provided evidence and source IDs. "
        "If the question cannot be answered safely from explicit numeric evidence, return operation='unsupported'.\n\n"
        "Supported operations:\n"
        "- difference: compute facts[0] - facts[1]\n"
        "- percentage_change: compute ((facts[1] - facts[0]) / facts[0]) * 100 where facts[0] is the baseline\n"
        "- percentage_of_total: compute (facts[0] / facts[1]) * 100\n"
        "- ratio: compute facts[0] / facts[1]\n"
        "- sum: compute the sum of all fact values\n"
        "- unsupported: use when none of the above can be applied safely\n\n"
        "Return facts in the exact computation order required by the selected operation. "
        "Keep citation IDs exactly as provided."
    ),
    ("human", "Question: {question}\n\nEvidence:\n{context}"),
])
