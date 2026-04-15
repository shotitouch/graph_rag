Ideal mental model
The system should behave like this:

understand what the user is asking
understand what filing(s) are currently loaded
decide whether the question is answerable from those filings
choose the right retrieval strategy
validate the evidence
generate only if evidence is good enough
refuse or ask for clarification when it isn’t
That is the core difference between:

generic RAG
and
a trustworthy 10-Q assistant
Ideal pipeline
1. Query Understanding
First node should extract structured intent from the question.

It should identify:

company / ticker mentioned
year
quarter / period
question type
whether it’s multi-part
whether it asks for unsupported things like prediction/opinion
Example outputs:

company = Microsoft
ticker = MSFT
period = Q3
year = 2025
question_type = performance_summary
multi_question = false
This node should not answer anything. It should only structure the request.

2. Filing Scope Understanding
The system should also know the scope of the indexed filing set.

For each ingested filing, we want normalized metadata like:

company name
canonical ticker set
filing type
fiscal period
fiscal year
source file
This is the “ground truth context” the rest of the pipeline uses.

3. Scope Validation
Now compare the query scope to the filing scope.

Questions to answer here:

does the user mention a different company than the indexed filing?
does the user ask for a different year/quarter?
are they asking something outside a 10-Q’s scope?
are they asking multiple distinct things at once?
Possible decisions:

in_scope
clarification_needed
out_of_scope
unsupported
This is where the Microsoft-vs-Google case should stop immediately.

4. Question-Type Routing
If the question is in scope, the system should decide what kind of analysis path to use.

Useful categories:

fact_lookup
metric_lookup
performance_summary
segment_analysis
risk_disclosure
liquidity_cashflow
unsupported_forward_looking
This matters because different questions need different retrieval and answer styles.

5. Retrieval Planning
Before retrieval, decide how to search.

Examples:

fact_lookup
narrower retrieval
prioritize cover page / key facts
metric_lookup
prioritize financial statement/table chunks
performance_summary
broader narrative + results sections
risk_disclosure
prioritize risk/legal narrative
Ideal system does not use one retrieval strategy for everything.

6. Retrieval
Now retrieve candidate evidence from the vector store.

This should use:

semantic similarity
metadata filtering where possible
maybe company/ticker filtering
maybe chunk-type preference later (text, table, image)
At this stage, retrieval is producing candidates, not truth.

7. Evidence Validation
This is one of the most important steps.

Check:

do retrieved chunks belong to the right company?
right filing?
right period?
are they actually relevant to the question?
is there enough evidence?
are we mixing unrelated evidence?
Possible outcomes:

sufficient
weak
mismatched
insufficient
If evidence is weak or mismatched, the system should retry or abstain.

8. Answerability Decision
Before generation, the system should explicitly decide:

do we have enough validated evidence to answer?
or should we refuse / ask the user to narrow the question?
This is the “fail closed” gate.

Without this, the model will fill gaps fluently.

9. Grounded Generation
Only now should the model answer.

Generation should be constrained to:

validated evidence
correct company/period
concise financial style
citation-aware output
For finance questions, the answer should prefer:

direct numeric facts
short synthesis
source-backed statements
Not broad speculation.

10. Post-Answer Validation
After generating, check:

is the answer grounded in retrieved evidence?
does it answer the question asked?
did it preserve company/entity consistency?
did it introduce unsupported claims?
This is different from retrieval validation:

retrieval validation checks the evidence
answer validation checks what the model did with it
11. Response Policy
Final output should depend on system confidence.

Possible response types:

answer
answer_with_caution
clarification_request
refusal
Examples:

“The indexed filing is for Alphabet, not Microsoft.”
“This 10-Q does not provide a basis for forecasting next quarter’s stock performance.”
“I can answer revenue and operating income separately; please ask one at a time.”
Ideal node layout
If we turn that into a graph, the ideal high-level flow is:

route_intent
analyze_query
validate_scope
classify_finance_question
plan_retrieval
retrieve
validate_evidence
decide_answerability
generate_grounded_answer
validate_answer
return_answer_or_refusal
That is what a mature 10-Q orchestration pipeline wants to become.

Ideal state
The system should carry structured state like:

query_company
query_tickers
query_year
query_period
question_type
multi_question
scope_status
scope_reason
retrieval_plan
evidence_status
answerability_status
That gives the graph memory for real decisions, not just prompt strings.

What makes this “ideal”
This design is ideal because it separates four concerns clearly:

understanding the question
understanding the document scope
validating evidence
generating an answer
Most weak RAG systems collapse all four into one prompt. That’s why they sound smart but fail badly.

If we simplify for v1
The ideal design is bigger than what we should build first.

For v1, I’d keep only the highest-value parts:

analyze_query
validate_scope
retrieve
validate_evidence
generate
validate_answer
That already gets you most of the trust improvement.

If you want, next we can do one of two things:

turn this ideal design into a minimal v1 design
map this ideal design onto your current LangGraph workflow node by node