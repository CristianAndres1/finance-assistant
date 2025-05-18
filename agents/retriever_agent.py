from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import aiohttp
import json
from datetime import datetime
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

class FinancialData(BaseModel):
    timestamp: str
    value: float
    source: str
    metadata: Optional[Dict[str, Any]] = None

class RetrieverRequest(BaseModel):
    query: str
    intent: str
    specific_topic: str
    time_range: Optional[str] = "1y"  # 1d, 1w, 1m, 1y
    data_sources: Optional[List[str]] = ["knowledge_base", "market_data"]

class RetrieverResponse(BaseModel):
    context: List[Dict[str, Any]]
    live_data: Optional[Dict[str, Any]] = None
    sources: List[str]
    timestamp: str

class RetrieverAgent:
    def __init__(self):
        from core.config import Settings
        settings = Settings()
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.vector_store = None
        self.initialize_vector_store()

    def initialize_vector_store(self):
        """Initialize FAISS vector store with financial knowledge base."""
        # Example financial knowledge base documents
        documents = [
            Document(
                page_content="Inflation is the rate at which the general level of prices for goods and services is rising.",
                metadata={"topic": "inflation", "type": "definition"}
            ),
            Document(
                page_content="Exchange rates represent how much one currency is worth in terms of another.",
                metadata={"topic": "forex", "type": "definition"}
            ),
            # Add more financial documents as needed
        ]
        
        self.vector_store = FAISS.from_documents(documents, self.embeddings)

    async def fetch_market_data(self, symbol: str, interval: str = "1d") -> List[FinancialData]:
        """Fetch financial market data from Alpha Vantage API."""
        async with aiohttp.ClientSession() as session:
            # Example using Alpha Vantage API
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": "your-api-key"  # Should be loaded from environment
            }
            
            try:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if "Time Series (Daily)" not in data:
                        return []
                    
                    time_series = data["Time Series (Daily)"]
                    return [
                        FinancialData(
                            timestamp=date,
                            value=float(values["4. close"]),
                            source="alpha_vantage",
                            metadata=values
                        )
                        for date, values in time_series.items()
                    ]
            except Exception as e:
                print(f"Error fetching market data: {e}")
                return []

    async def search_knowledge_base(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search the vector store for relevant financial information."""
        if not self.vector_store:
            return []
            
        results = self.vector_store.similarity_search_with_score(query, k=n_results)
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": score
            }
            for doc, score in results
        ]

    async def process(self, request: RetrieverRequest) -> RetrieverResponse:
        """Process the retrieval request and gather relevant information."""
        context = []
        live_data = {}
        sources = []

        # Get relevant information from knowledge base
        if "knowledge_base" in request.data_sources:
            kb_results = await self.search_knowledge_base(
                f"{request.specific_topic} {request.query}"
            )
            context.extend(kb_results)
            sources.append("knowledge_base")

        # Fetch market data if needed
        if "market_data" in request.data_sources:
            # Map topics to symbols (expand as needed)
            topic_to_symbol = {
                "stocks": "SPY",
                "forex": "EURUSD",
                "commodities": "GLD"
            }
            
            if request.specific_topic in topic_to_symbol:
                symbol = topic_to_symbol[request.specific_topic]
                market_data = await self.fetch_market_data(symbol, request.time_range)
                if market_data:
                    live_data[symbol] = market_data
                    sources.append("market_data")

        return RetrieverResponse(
            context=context,
            live_data=live_data,
            sources=sources,
            timestamp=datetime.utcnow().isoformat()
        )

    @staticmethod
    def get_supported_data_sources() -> List[str]:
        """Return list of supported data sources."""
        return [
            "knowledge_base",
            "market_data",
            "news_feeds",
            "economic_indicators"
        ]
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import aiohttp
import json
from datetime import datetime
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

class FinancialData(BaseModel):
    timestamp: str
    value: float
    source: str
    metadata: Optional[Dict[str, Any]] = None

class RetrieverRequest(BaseModel):
    query: str
    intent: str
    specific_topic: str
    time_range: Optional[str] = "1y"  # 1d, 1w, 1m, 1y
    data_sources: Optional[List[str]] = ["knowledge_base", "market_data"]

class RetrieverResponse(BaseModel):
    context: List[Dict[str, Any]]
    live_data: Optional[Dict[str, Any]] = None
    sources: List[str]
    timestamp: str

class RetrieverAgent:
    def __init__(self):
        from core.config import Settings
        settings = Settings()
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.vector_store = None
        self.initialize_vector_store()

    def initialize_vector_store(self):
        """Initialize FAISS vector store with financial knowledge base."""
        # Example financial knowledge base documents
        documents = [
            Document(
                page_content="Inflation is the rate at which the general level of prices for goods and services is rising.",
                metadata={"topic": "inflation", "type": "definition"}
            ),
            Document(
                page_content="Exchange rates represent how much one currency is worth in terms of another.",
                metadata={"topic": "forex", "type": "definition"}
            ),
            # Add more financial documents as needed
        ]
        
        self.vector_store = FAISS.from_documents(documents, self.embeddings)

    async def fetch_market_data(self, symbol: str, interval: str = "1d") -> List[FinancialData]:
        """Fetch financial market data from Alpha Vantage API."""
        async with aiohttp.ClientSession() as session:
            # Example using Alpha Vantage API
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": "your-api-key"  # Should be loaded from environment
            }
            
            try:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if "Time Series (Daily)" not in data:
                        return []
                    
                    time_series = data["Time Series (Daily)"]
                    return [
                        FinancialData(
                            timestamp=date,
                            value=float(values["4. close"]),
                            source="alpha_vantage",
                            metadata=values
                        )
                        for date, values in time_series.items()
                    ]
            except Exception as e:
                print(f"Error fetching market data: {e}")
                return []

    async def search_knowledge_base(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search the vector store for relevant financial information."""
        if not self.vector_store:
            return []
            
        results = self.vector_store.similarity_search_with_score(query, k=n_results)
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": score
            }
            for doc, score in results
        ]

    async def process(self, request: RetrieverRequest) -> RetrieverResponse:
        """Process the retrieval request and gather relevant information."""
        context = []
        live_data = {}
        sources = []

        # Get relevant information from knowledge base
        if "knowledge_base" in request.data_sources:
            kb_results = await self.search_knowledge_base(
                f"{request.specific_topic} {request.query}"
            )
            context.extend(kb_results)
            sources.append("knowledge_base")

        # Fetch market data if needed
        if "market_data" in request.data_sources:
            # Map topics to symbols (expand as needed)
            topic_to_symbol = {
                "stocks": "SPY",
                "forex": "EURUSD",
                "commodities": "GLD"
            }
            
            if request.specific_topic in topic_to_symbol:
                symbol = topic_to_symbol[request.specific_topic]
                market_data = await self.fetch_market_data(symbol, request.time_range)
                if market_data:
                    live_data[symbol] = market_data
                    sources.append("market_data")

        return RetrieverResponse(
            context=context,
            live_data=live_data,
            sources=sources,
            timestamp=datetime.utcnow().isoformat()
        )

    @staticmethod
    def get_supported_data_sources() -> List[str]:
        """Return list of supported data sources."""
        return [
            "knowledge_base",
            "market_data",
            "news_feeds",
            "economic_indicators"
        ]
