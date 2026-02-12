from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.config import get_settings
from pydantic import BaseModel, Field

class SentimentResult(BaseModel):
    sentiment: str = Field(description="positive, negative, or neutral")
    urgency: str = Field(description="low, medium, high, or critical")
    score: float = Field(description="sentiment score from -1.0 to 1.0")
    reasoning: str = Field(description="brief explanation")

async def analyze_sentiment(text: str) -> SentimentResult:
    """
    Analyze sentiment and urgency of text using LLM.
    """
    settings = get_settings()
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_URL,
        format="json", # Force JSON mode
        temperature=0,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert customer support analyst. Analyze the following ticket text for sentiment and urgency. Output valid JSON."),
        ("user", "{text}")
    ])
    
    chain = prompt | llm | JsonOutputParser(pydantic_object=SentimentResult)
    
    try:
        result = await chain.ainvoke({"text": text})
        return SentimentResult(**result)
    except Exception as e:
        print(f"Sentiment Analysis Failed: {e}")
        return SentimentResult(sentiment="neutral", urgency="medium", score=0.0, reasoning="Analysis failed")
