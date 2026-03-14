What you probably need to add, in practical order:

1.Clean up the app behavior
harden retry logic
define fallback responses
make citation/source behavior consistent
fix misleading metadata like sources_count
2.Add structured logging
replace print with JSON logs
log request ID, thread ID, question hash, node name, latency, decision, retry count, model, token usage, error type
3.Add evaluation
create 30-100 question answer set over known PDFs
track retrieval hit rate, groundedness, answer correctness, abstention rate, latency
4.Add experiment tracking
use MLflow if you want the skill visible
track prompt version, model name, reranker version, chunking params, top-k, eval scores
5.Add deployment packaging
Docker for frontend/backend
proper env config
production server config
persistent storage plan for Chroma or move to a managed vector store
6.Add cloud + CI/CD
deploy on AWS only if you want infra credibility
otherwise Vercel + Render/Railway is enough for a first portfolio version
CI should run lint/tests/eval smoke tests