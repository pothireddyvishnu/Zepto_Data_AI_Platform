from fastapi import FastAPI, HTTPException
from graph import run_graph
from schemas import AskRequest, AskResponse

app = FastAPI(
    title="Support Assistant",
    version="1.0.0"
)


@app.get("/")
def status_check():
    return {"status": "running", "service": app.title, "version": app.version}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        return run_graph(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
