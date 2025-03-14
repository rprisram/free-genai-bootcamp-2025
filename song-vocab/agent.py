import json
import httpx
import instructor
from typing import List, Dict, Any, Optional
import ollama
from pydantic import BaseModel, Field
from tools.search_web import search_web
from tools.get_page_content import get_page_content
from tools.extract_vocabulary import extract_vocabulary
from prompts import REACT_PROMPT

class VocabularyItem(BaseModel):
    word: str
    definition: str
    example: Optional[str] = None

class AgentResponse(BaseModel):
    lyrics: str
    vocabulary: List[VocabularyItem]

async def call_ollama(prompt: str) -> str:
    """Call the Ollama model with a prompt and return the response."""
    response = ollama.chat(
        model='gemma3:4b',
        messages=[{'role': 'user', 'content': prompt}],
        stream=False
    )
    return response['message']['content']

async def call_ollama_with_instructor(prompt: str, output_class: Any) -> Any:
    """Call the Ollama model with a prompt and parse the response using instructor."""
    client = instructor.from_ollama(model="gemma3:4b")
    response = await client.chat.completions.create(
        messages=[{'role': 'user', 'content': prompt}],
        response_model=output_class
    )
    return response

async def process_request(
    message_request: str,
    lyrics_language: str = "english",
    vocabulary_language: str = "english"
) -> AgentResponse:
    """
    Process the song/artist request through the reAct framework:
    1. Search for lyrics in the specified language
    2. Get page content from search results
    3. Extract the correct lyrics
    4. Generate vocabulary from the lyrics in the target language
    """
    # Initialize conversation with the reAct prompt and include language specifications
    conversation = [
        {"role": "system", "content": REACT_PROMPT},
        {"role": "user", "content": f"Find lyrics in {lyrics_language} and create vocabulary in {vocabulary_language} for: {message_request}"}
    ]
    
    # Track the state of the reAct process
    search_results = []
    lyrics_content = []
    final_lyrics = ""
    vocabulary_list = []
    
    # Execute up to 5 steps of reAct reasoning
    for step in range(5):
        # Create the current prompt from the conversation
        current_prompt = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        
        # Get the model's thought process
        response = await call_ollama(current_prompt)
        
        # Extract action from the response
        if "Action:" in response:
            action_part = response.split("Action:")[1].strip()
            action_lines = action_part.split("\n")
            action_name = action_lines[0].strip()
            
            # Execute the appropriate tool based on the action
            if action_name == "search_web":
                query = action_lines[1].strip().replace("Query: ", "")
                search_results = await search_web(query, lyrics_language)
                action_result = f"Found {len(search_results)} search results."
            
            elif action_name == "get_page_content":
                if not search_results:
                    action_result = "Error: No search results available."
                else:
                    url_index = int(action_lines[1].strip().replace("URL index: ", ""))
                    if url_index < len(search_results):
                        url = search_results[url_index]["link"]
                        content = await get_page_content(url)
                        lyrics_content.append({"url": url, "content": content})
                        action_result = f"Retrieved content from {url}"
                    else:
                        action_result = "Error: URL index out of range."
            
            elif action_name == "extract_vocabulary":
                lyrics_index = int(action_lines[1].strip().replace("Lyrics index: ", ""))
                if lyrics_index < len(lyrics_content):
                    lyrics_text = lyrics_content[lyrics_index]["content"]
                    final_lyrics = lyrics_text
                    vocabulary_list = await extract_vocabulary(lyrics_text, vocabulary_language)
                    action_result = f"Extracted {len(vocabulary_list)} vocabulary items from lyrics."
                else:
                    action_result = "Error: Lyrics index out of range."
            
            elif action_name == "finish":
                break
            
            else:
                action_result = f"Unknown action: {action_name}"
            
            # Add the action result to the conversation
            conversation.append({"role": "system", "content": f"Observation: {action_result}"})
            conversation.append({"role": "user", "content": "Continue with the next step."})
        
        # If no action is found, assume the process is complete
        else:
            break
    
    # If we didn't extract any lyrics or vocabulary, raise an error
    if not final_lyrics:
        raise Exception("Failed to extract lyrics for the requested song.")
    
    # Return the final results
    return AgentResponse(
        lyrics=final_lyrics,
        vocabulary=vocabulary_list
    )
