from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from helloworld_langgraph import financial_agent_node, state_schema
import logging
from rich.console import Console
from rich.panel import Panel

app = FastAPI()
console = Console()
logging.basicConfig(level=logging.INFO)

def log_step(title, content):
    console.print(Panel(content, title=title, style="bold green"))

class FinancialQuery(BaseModel):
    query: str

@app.post("/financial-agent/")
def run_financial_agent(query: FinancialQuery):
    state = {"financial_query": query.query}
    try:
        state = financial_agent_node(state)
        return {
            "input": query.query,
            "output": state["financial_response"]
        }
    except Exception as e:
        log_step("Error", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
