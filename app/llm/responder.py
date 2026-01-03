import os
from openai import OpenAI
from typing import Optional, List
from app.utils.logger import get_logger

logger = get_logger("llm")


def generate_response(user_text: str, context_chunks: Optional[List[str]] = None) -> str:
    """Generate a textual response for given user_text using OpenAI GPT.
    
    Args:
        user_text: The user's question or statement
        context_chunks: Optional list of relevant document chunks from RAG
    
    Returns:
        AI-generated response text
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Build prompt with optional RAG context
        system_prompt = "You are a helpful AI assistant for an organization. Provide clear, concise, and accurate answers."
        
        if context_chunks:
            context = "\n\n".join(context_chunks)
            user_message = f"""Context from our knowledge base:
{context}

User question: {user_text}

Please answer based on the context provided. If the context doesn't contain relevant information, say so politely."""
        else:
            user_message = user_text
        
        logger.info(f"Generating response for: {user_text}")
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        logger.info(f"Generated response: {answer}")
        
        return answer
    
    except Exception as e:
        logger.exception(f"Error generating response: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later." 
