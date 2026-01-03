"""
Local LLM Response Generator using Ollama (FREE!)
Alternative to OpenAI GPT-4
"""

import requests
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def generate_response_local(
    user_text: str,
    context_chunks: Optional[List[str]] = None,
    model: str = "llama3.2:3b"
) -> str:
    """
    Generate response using local Ollama model (100% FREE)
    
    Args:
        user_text: User's question
        context_chunks: Retrieved context from RAG
        model: Ollama model name
        
    Returns:
        Generated response text
    """
    try:
        # Build prompt with context
        if context_chunks:
            context = "\n\n".join(context_chunks)
            prompt = f"""You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question: {user_text}

Answer (be concise and helpful):"""
        else:
            prompt = f"""You are a helpful assistant. Answer this question concisely:

Question: {user_text}

Answer:"""
        
        # Call local Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 150  # Max tokens
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "").strip()
            logger.info(f"Local LLM generated response: {answer[:100]}...")
            return answer
        else:
            logger.error(f"Ollama API error: {response.status_code}")
            return "I'm having trouble generating a response right now."
            
    except requests.exceptions.ConnectionError:
        logger.error("Ollama server not running. Start with: ollama serve")
        return "AI service unavailable. Please start Ollama server."
    except Exception as e:
        logger.error(f"Error generating local response: {e}")
        return "I'm having trouble generating a response right now."


def test_local_llm():
    """Test if local LLM is working"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return True, [m["name"] for m in models]
        return False, []
    except:
        return False, []


if __name__ == "__main__":
    # Test the local LLM
    print("Testing Local LLM (Ollama)...")
    
    working, models = test_local_llm()
    if working:
        print(f"✓ Ollama is running!")
        print(f"✓ Available models: {', '.join(models)}")
        
        # Test generation
        print("\nTesting response generation...")
        response = generate_response_local(
            "What are your operating hours?",
            context_chunks=["We are open Monday-Friday 9 AM to 5 PM EST."]
        )
        print(f"Response: {response}")
    else:
        print("✗ Ollama not running. Start with: ollama serve")
