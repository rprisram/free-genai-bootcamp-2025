import sqlite3
from typing import List
from pydantic import BaseModel

class VocabularyItem(BaseModel):
    word: str
    definition: str
    example: str = None

def init_db():
    """Initialize the SQLite database with necessary tables."""
    conn = sqlite3.connect('song_vocabulary.db')
    cursor = conn.cursor()
    
    # Create songs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT,
        lyrics TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create vocabulary table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER,
        word TEXT NOT NULL,
        definition TEXT NOT NULL,
        example TEXT,
        FOREIGN KEY (song_id) REFERENCES songs (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def save_song_with_vocabulary(title: str, artist: str, lyrics: str, vocabulary: List[VocabularyItem]):
    """Save a song and its vocabulary to the database."""
    conn = sqlite3.connect('song_vocabulary.db')
    cursor = conn.cursor()
    
    # Insert song
    cursor.execute('''
    INSERT INTO songs (title, artist, lyrics)
    VALUES (?, ?, ?)
    ''', (title, artist, lyrics))
    
    song_id = cursor.lastrowid
    
    # Insert vocabulary items
    for item in vocabulary:
        cursor.execute('''
        INSERT INTO vocabulary (song_id, word, definition, example)
        VALUES (?, ?, ?, ?)
        ''', (song_id, item.word, item.definition, item.example))
    
    conn.commit()
    conn.close()
    
    return song_id
