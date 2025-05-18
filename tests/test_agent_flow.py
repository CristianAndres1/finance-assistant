import pytest
import asyncio
from agents.intention_agent import IntentionAgent, IntentionRequest
from agents.retriever_agent import RetrieverAgent, RetrieverRequest
from agents.reasoner_agent import ReasonerAgent, ReasonerRequest
from agents.writer_agent import WriterAgent, WriterRequest
from agents.designer_agent import DesignerAgent, DesignerRequest

async def test_full_agent_flow():
    # Test query in Spanish
    query = "como me afecta el precio del dolar"
    
    # 1. Intention Agent
    intention_agent = IntentionAgent()
    intention_result = await intention_agent.process(
        IntentionRequest(text=query)
    )
    print("\n1. Intention Agent Output:")
    print(f"Intent: {intention_result.intent}")
    print(f"Confidence: {intention_result.confidence}")
    print(f"Metadata: {intention_result.metadata}")
    
    # 2. Retriever Agent
    retriever_agent = RetrieverAgent()
    retriever_result = await retriever_agent.process(
        RetrieverRequest(
            query=query,
            intent=intention_result.intent,
            specific_topic=intention_result.metadata.get('specific_topic', 'forex')
        )
    )
    print("\n2. Retriever Agent Output:")
    print(f"Retrieved Context: {retriever_result.context}")
    print(f"Sources: {retriever_result.sources}")
    
    # 3. Reasoner Agent
    reasoner_agent = ReasonerAgent()
    reasoner_result = await reasoner_agent.process(
        ReasonerRequest(
            query=query,
            intent=intention_result.intent,
            context=retriever_result.context
        )
    )
    print("\n3. Reasoner Agent Output:")
    print(f"Analysis Steps: {reasoner_result.analysis_steps}")
    print(f"Conclusion: {reasoner_result.conclusion}")
    print(f"Confidence Score: {reasoner_result.confidence_score}")
    if reasoner_result.recommendations:
        print(f"Recommendations: {reasoner_result.recommendations}")
    
    # 4. Writer Agent
    writer_agent = WriterAgent()
    writer_result = await writer_agent.process(
        WriterRequest(
            query=query,
            analysis_steps=[step.dict() for step in reasoner_result.analysis_steps],
            conclusion=reasoner_result.conclusion,
            recommendations=reasoner_result.recommendations or []
        )
    )
    print("\n4. Writer Agent Output:")
    print(f"Content: {writer_result.content}")
    print(f"Format: {writer_result.format}")
    
    # 5. Designer Agent
    designer_agent = DesignerAgent()
    designer_result = await designer_agent.process(
        DesignerRequest(
            text=query,
            intent=intention_result.intent,
            analysis=reasoner_result.analysis,
            response=writer_result.response
        )
    )
    print("\n5. Designer Agent Output:")
    print(f"Visualization Type: {designer_result.visualization_type}")
    print(f"Data: {designer_result.data}")

if __name__ == "__main__":
    asyncio.run(test_full_agent_flow())
