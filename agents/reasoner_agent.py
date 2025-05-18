from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import numpy as np
from datetime import datetime

class ReasonerRequest(BaseModel):
    query: str
    intent: str
    context: List[Dict[str, Any]]
    live_data: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None

class AnalysisStep(BaseModel):
    step_number: int
    description: str
    reasoning: str
    confidence: float
    data_points: Optional[List[Dict[str, Any]]] = None

class ReasonerResponse(BaseModel):
    analysis_steps: List[AnalysisStep]
    conclusion: str
    confidence_score: float
    recommendations: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class ReasonerAgent:
    """The Reasoner Agent analyzes the retrieved information to draw insights and conclusions.
    
    Main Steps:
    1. Initialization:
       - Sets up language model with OpenAI API key
       - Configures analysis chain with specialized prompts
    2. Process:
       - Takes query, intent, and context from previous agents
       - Performs step-by-step analysis of the information
       - Evaluates confidence for each analysis step
       - Draws conclusions based on the analysis
       - Generates actionable recommendations
    3. Output:
       - Returns structured analysis with confidence scores
       - Provides clear conclusions and recommendations
    """
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        from core.config import Settings
        settings = Settings()
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.2,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial analysis expert. Analyze the given information and provide step-by-step reasoning.
            Focus on key insights, trends, and implications. Be precise and data-driven in your analysis.
            
            For each step:
            1. Clearly state what you're analyzing
            2. Provide your reasoning
            3. Support with data when available
            4. Assign a confidence score (0-1)
            
            End with a clear conclusion and actionable recommendations."""),
            ("user", """Query: {query}
            Intent: {intent}
            Context: {context}
            Live Data: {live_data}
            
            Provide your analysis in JSON format with:
            - analysis_steps: list of steps with number, description, reasoning, confidence, and data_points
            - conclusion: overall conclusion
            - confidence_score: overall confidence (0-1)
            - recommendations: list of actionable recommendations""")
        ])
        
        self.chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)

    def _analyze_numerical_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform statistical analysis on numerical data."""
        if not data:
            return {}
            
        df = pd.DataFrame(data)
        
        try:
            analysis = {
                "mean": float(df["value"].mean()),
                "std": float(df["value"].std()),
                "trend": self._calculate_trend(df),
                "volatility": float(df["value"].std() / df["value"].mean()),
            }
            return analysis
        except Exception as e:
            print(f"Error in numerical analysis: {e}")
            return {}

    def _calculate_trend(self, df: pd.DataFrame) -> str:
        """Calculate trend direction and strength."""
        if len(df) < 2:
            return "insufficient_data"
            
        try:
            values = df["value"].values
            z = np.polyfit(range(len(values)), values, 1)
            slope = z[0]
            
            if abs(slope) < 0.001:
                return "stable"
            elif slope > 0:
                return "upward" if slope > 0.01 else "slightly_upward"
            else:
                return "downward" if slope < -0.01 else "slightly_downward"
        except Exception:
            return "unknown"

    async def process(self, request: ReasonerRequest) -> ReasonerResponse:
        """Process the request and generate reasoned analysis."""
        try:
            # Perform numerical analysis if live data is available
            numerical_analysis = {}
            if request.live_data:
                for symbol, data in request.live_data.items():
                    numerical_analysis[symbol] = self._analyze_numerical_data(data)

            # Prepare context for LLM
            context_with_analysis = {
                "query": request.query,
                "intent": request.intent,
                "context": request.context,
                "live_data": {
                    "raw": request.live_data,
                    "analysis": numerical_analysis
                }
            }

            # Get LLM analysis
            result = await self.chain.arun(**context_with_analysis)
            parsed_result = eval(result)  # In production, use proper JSON parsing
            
            # Convert to ReasonerResponse
            return ReasonerResponse(
                analysis_steps=[
                    AnalysisStep(**step) for step in parsed_result["analysis_steps"]
                ],
                conclusion=parsed_result["conclusion"],
                confidence_score=parsed_result["confidence_score"],
                recommendations=parsed_result["recommendations"],
                metadata={
                    "numerical_analysis": numerical_analysis,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            # Return error response
            return ReasonerResponse(
                analysis_steps=[
                    AnalysisStep(
                        step_number=1,
                        description="Error in analysis",
                        reasoning=str(e),
                        confidence=0.0
                    )
                ],
                conclusion="Analysis failed",
                confidence_score=0.0,
                recommendations=["Please try again with different parameters"],
                metadata={"error": str(e)}
            )
