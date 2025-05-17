import os
import logging
from rich.console import Console
from rich.panel import Panel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.graph import StateGraph, END

# Configuración de logging bonito
console = Console()
logging.basicConfig(level=logging.INFO)
def log_step(title, content):
    console.print(Panel(content, title=title, style="bold green"))

# Estado: guarda mensajes y respuestas
state_schema = dict

# --- Financial Assistant Agent ---
fin_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Eres un asistente financiero inteligente con conocimientos en gestión de finanzas personales, inversiones, planificación financiera y optimización de gastos. Tu objetivo es ayudar al usuario a tomar decisiones financieras informadas, brindando análisis claros, recomendaciones personalizadas y explicaciones detalladas sobre conceptos financieros.
"""),
    ("placeholder", "{messages}")
])

def _modify_state_messages(state: AgentState):
    return fin_prompt.invoke({"messages": state["messages"]}).to_messages()

from dotenv import load_dotenv
load_dotenv()

fin_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-04-17",
    google_api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.1
)
tools = []
langgraph_agent_executor = create_react_agent(
    fin_llm,
    tools,
    state_modifier=_modify_state_messages
)

def financial_agent_node(state):
    if "financial_query" in state:
        query = state["financial_query"]
    else:
        query = "Quiero ahorrar para la inicial de una casa en 3 años. ¿Cómo puedo planificar mis finanzas?"
    messages = [("human", query)]
    result = langgraph_agent_executor.invoke({"messages": messages})
    output = result["messages"][-1].content
    log_step("Asistente Financiero", f"[bold cyan]Consulta:[/bold cyan] {query}\n[bold yellow]Respuesta:[/bold yellow] {output}")
    state["financial_response"] = output
    state["messages"] = [output]
    return state

if __name__ == "__main__":
    graph = StateGraph(state_schema)
    graph.add_node("financial_agent", financial_agent_node)
    graph.add_edge("financial_agent", END)
    graph.set_entry_point("financial_agent")
    compiled_graph = graph.compile()
    compiled_graph.invoke({
        "financial_query": "Quiero ahorrar para la inicial de una casa en 3 años. ¿Cómo puedo planificar mis finanzas?"
    })
