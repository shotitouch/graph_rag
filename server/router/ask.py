from fastapi import APIRouter, HTTPException
from schemas import ChatRequest
from graph.workflow import agent_app as agent_graph  # Import the COMPILED graph

router = APIRouter(prefix="/ask", tags=["ask"])

@router.post("/")
async def ask_question(request: ChatRequest):
    try:
        # Prepare the initial State (TypedDict)
        initial_state = {
            "question": request.question,
            "documents": [],
            "generation": "",
            "retry_count": 0,
            "is_grounded": "",
            "is_useful": "",
            "messages": []
        }
        

        
        config = {"configurable": {"thread_id": request.thread_id}}

        # check existing state by thread_id
        existing_state = await agent_graph.aget_state(config)

        if existing_state.values:
            # We found history! 
            # Reset the control flags so the new question starts fresh,
            # but the 'messages' will automatically merge because of your State definition.
            inputs = {
                "question": request.question,
                "retry_count": 0,    # Reset!
                "is_grounded": "",   # Reset!
                "is_useful": "",     # Reset!
                "documents": []      # Clear old docs from the last turn
            }
        else:
            # First time user? Use your full initial_state
            inputs = initial_state

        # 3. Run the Graph!
        # This will trigger: Retrieve -> Rerank -> Grade -> (Rewrite Loop) -> Generate
        final_state = await agent_graph.ainvoke(inputs, config=config)
        
        # 4. Return the result
        return {
            "question": request.question,
            "answer": final_state.get("generation"),
            "metadata": {
                "retries": final_state.get("retry_count"),
                "sources_count": len(final_state.get("documents", []))
            }
        }
        
    except Exception as e:
        # Professional error handling
        raise HTTPException(status_code=500, detail=str(e))