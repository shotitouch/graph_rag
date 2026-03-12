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

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. "
        "If context is provided, use it to answer the question accurately. "
        "If no useful context exists or context is empty, answer normally. "
        "For every part of your answer, connect it to one of the citations. "
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