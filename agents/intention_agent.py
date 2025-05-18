from typing import Dict, Any, Optional
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

class IntentionRequest(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = None

class IntentionResponse(BaseModel):
    intent: str
    question: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

class IntentionAgent:
    """The Intention Agent analyzes user queries to determine their intent and context.
    
    Main Steps:
    1. Initialization: Sets up the language model with OpenAI API key
    2. Process: Takes a user query and:
       - Analyzes the text to determine the primary intent (e.g., market analysis, price check)
       - Identifies any specific topics or focus areas
       - Calculates a confidence score for the intent classification
       - Extracts relevant metadata (e.g., time period, specific assets)
    3. Output: Returns structured information about the user's intent for other agents
    """
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        from core.config import Settings
        settings = Settings()
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.prompt = PromptTemplate(
            input_variables=["query"],
            template="""Analyze the following financial query and classify its intention.
            Query: {query}
            
            Respond in JSON format with:
            - intent: The main intention (explanation, calculation, comparison, prediction, or advice)
            - specific_topic: The financial topic being discussed
            - confidence: Your confidence in this classification (0.0 to 1.0)
            """
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    async def process(self, request: IntentionRequest) -> IntentionResponse:
        """Process the user query and determine its intention."""
        try:
            # Get LLM response
            result = await self.chain.arun(query=request.text)
            
            # Parse the response (assuming JSON string)
            parsed_result = eval(result)  # In production, use proper JSON parsing
            
            return IntentionResponse(
                intent=parsed_result["intent"],
                question=request.text,
                confidence=parsed_result["confidence"],
                metadata={
                    "specific_topic": parsed_result["specific_topic"]
                }
            )
        except Exception as e:
            return IntentionResponse(
                intent="unclear",
                question=request.text,
                confidence=0.0,
                metadata={"error": str(e)}
            )

    @staticmethod
    def get_supported_intents() -> list[str]:
        """Return list of supported intention types."""
        return [
            "explanation",
            "calculation",
            "comparison",
            "prediction",
            "advice"
        ]
