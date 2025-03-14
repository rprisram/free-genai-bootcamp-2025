from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import agent
from database import init_db, save_song_with_vocabulary
from datetime import datetime

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Song Vocabulary API")

class MessageRequest(BaseModel):
    message_request: str = Field(
        ..., description="A string that describes the song and/or artist to get lyrics for"
    )
    lyrics_language: Optional[str] = Field(
        default="english", description="The language of the lyrics to find"
    )
    vocabulary_language: Optional[str] = Field(
        default="english", description="The language to use for vocabulary definitions"
    )

class VocabularyItem(BaseModel):
    word: str
    definition: str
    example: Optional[str] = None

class AgentResponse(BaseModel):
    lyrics: str
    vocabulary: List[VocabularyItem]

def extract_song_info(message: str) -> tuple:
    """Extract title and artist from the message."""
    title = message
    artist = ""
    if " by " in message:
        parts = message.split(" by ", 1)
        title = parts[0].strip()
        artist = parts[1].strip()
    return title, artist

def save_to_db_background(title: str, artist: str, lyrics: str, vocabulary: List[VocabularyItem]):
    """Background task to save data to the database."""
    try:
        save_song_with_vocabulary(title, artist, lyrics, vocabulary)
        logging.info(f"Saved song '{title}' by '{artist}' to database")
    except Exception as e:
        logging.error(f"Failed to save to database: {e}", exc_info=True)

@app.post("/api/agent", response_model=AgentResponse)
async def get_lyrics(request: MessageRequest, background_tasks: BackgroundTasks):
    """Process a song request and return lyrics and vocabulary."""
    try:
        result = await agent.process_request(
            request.message_request,
            lyrics_language=request.lyrics_language,
            vocabulary_language=request.vocabulary_language
        )
        
        # Extract song info
        title, artist = extract_song_info(request.message_request)
        
        # Save to database in the background (non-blocking)
        background_tasks.add_task(
            save_to_db_background, 
            title, 
            artist, 
            result.lyrics, 
            result.vocabulary
        )
        
        return result
    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    # Initialize the database
    init_db()
    logging.info("Database initialized")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info", workers=1)
