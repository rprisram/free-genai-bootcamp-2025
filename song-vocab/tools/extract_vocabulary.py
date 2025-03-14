## This tool takes a body of text and spits out the vocabulary in a structured json output. 
import ollama
from typing import List
from pydantic import BaseModel
from prompts import VOCABULARY_EXTRACTION_PROMPT
from openai import OpenAI
import instructor

class VocabularyItem(BaseModel):
    word: str
    definition: str
    example: str = None

async def extract_vocabulary(lyrics: str, vocabulary_language: str = "english") -> List[VocabularyItem]:
    """
    Extract vocabulary items from song lyrics using the LLM.
    """
    try:
        # Use instructor to get structured output
       # client = instructor.from_ollama(model="gemma3:4b")
        client = instructor.from_openai(
            OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",  # required but unused
            ),
            mode=instructor.Mode.JSON,
        )
        # Create the prompt with the lyrics and target language
        prompt = VOCABULARY_EXTRACTION_PROMPT.format(
            lyrics=lyrics,
            vocabulary_language=vocabulary_language
        )
        # Then use:
        response = await client.chat.completions.create(
            model="gemma3:4b",
            messages=[{"role": "user", "content": prompt}],
            response_model=List[VocabularyItem]
        )
        
        # Return the structured vocabulary items
        return response
    except Exception as e:
        print(f"Error extracting vocabulary: {e}")
        # Return a minimal set of vocabulary if extraction fails
        return [
            VocabularyItem(
                word="error", 
                definition="An error occurred during vocabulary extraction", 
                example=str(e)
            )
        ]
