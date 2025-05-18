from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import json

class WriterRequest(BaseModel):
    query: str
    analysis_steps: List[Dict[str, Any]]
    conclusion: str
    recommendations: List[str]
    user_preferences: Optional[Dict[str, Any]] = None
    tone: Optional[str] = "professional"
    language: Optional[str] = "en"
    format: Optional[str] = "text"  # text, html, markdown

class WriterResponse(BaseModel):
    content: str
    format: str
    metadata: Optional[Dict[str, Any]] = None
    alternative_phrasings: Optional[List[str]] = None

class WriterAgent:
    """The Writer Agent transforms analysis into clear, human-friendly content.
    
    Main Steps:
    1. Initialization:
       - Sets up language model with higher temperature for creative writing
       - Configures response templates for different content formats
    2. Process:
       - Takes query, analysis steps, and conclusions from previous agents
       - Considers user preferences and tone requirements
       - Structures the content for readability
       - Adapts language style based on target audience
       - Generates alternative phrasings if needed
    3. Output:
       - Returns formatted content in specified format (text, HTML, markdown)
       - Includes metadata about the generated content
    """
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        from core.config import Settings
        settings = Settings()
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.7,  # Higher temperature for more creative writing
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial communication expert who excels at explaining complex topics clearly.
            Adapt your writing style based on the specified tone and user preferences.
            Focus on making the information accessible while maintaining accuracy.
            
            Available tones:
            - professional: Clear, formal, and authoritative
            - friendly: Warm, approachable, and conversational
            - simple: Basic vocabulary, straightforward explanations
            - technical: Detailed, precise, using industry terminology
            
            Format the response according to the specified format (text, html, markdown)."""),
            ("user", """Query: {query}
            Analysis: {analysis}
            Conclusion: {conclusion}
            Recommendations: {recommendations}
            Tone: {tone}
            Format: {format}
            User Preferences: {preferences}
            
            Generate a well-structured response that:
            1. Addresses the user's query directly
            2. Explains the analysis in an understandable way
            3. Provides clear conclusions and actionable recommendations
            4. Uses appropriate tone and terminology
            5. Includes relevant examples or analogies when helpful""")
        ])
        
        self.chain = LLMChain(llm=self.llm, prompt=self.response_prompt)

    def _format_content(self, content: str, format_type: str) -> str:
        """Format content according to specified format type."""
        if format_type == "html":
            paragraphs = content.split("\n\n")
            return "".join([f"<p>{p}</p>" for p in paragraphs if p.strip()])
        elif format_type == "markdown":
            # Basic markdown formatting
            return content
        else:  # text
            return content

    def _adapt_to_preferences(self, content: str, preferences: Dict[str, Any]) -> str:
        """Adapt content based on user preferences."""
        if not preferences:
            return content
            
        # Example adaptations
        if preferences.get("simplify_terms", False):
            # Replace complex terms with simpler alternatives
            financial_terms = {
                "volatility": "price changes",
                "diversification": "spreading investments",
                "appreciation": "increase in value",
                # Add more term mappings
            }
            for term, simple_term in financial_terms.items():
                content = content.replace(term, f"{simple_term} ({term})")
                
        return content

    async def process(self, request: WriterRequest) -> WriterResponse:
        """Process the request and generate a user-friendly response."""
        try:
            # Prepare context for LLM
            context = {
                "query": request.query,
                "analysis": json.dumps(request.analysis_steps, indent=2),
                "conclusion": request.conclusion,
                "recommendations": json.dumps(request.recommendations, indent=2),
                "tone": request.tone,
                "format": request.format,
                "preferences": json.dumps(request.user_preferences or {}, indent=2)
            }

            # Generate content
            content = await self.chain.arun(**context)
            
            # Format content
            formatted_content = self._format_content(content, request.format)
            
            # Adapt to user preferences
            if request.user_preferences:
                formatted_content = self._adapt_to_preferences(
                    formatted_content,
                    request.user_preferences
                )
            
            return WriterResponse(
                content=formatted_content,
                format=request.format,
                metadata={
                    "tone": request.tone,
                    "language": request.language,
                    "content_length": len(formatted_content)
                }
            )
            
        except Exception as e:
            return WriterResponse(
                content=f"Error generating response: {str(e)}",
                format="text",
                metadata={"error": str(e)}
            )

    @staticmethod
    def get_supported_formats() -> List[str]:
        """Return list of supported output formats."""
        return ["text", "html", "markdown"]

    @staticmethod
    def get_supported_tones() -> List[str]:
        """Return list of supported writing tones."""
        return [
            "professional",
            "friendly",
            "simple",
            "technical"
        ]
