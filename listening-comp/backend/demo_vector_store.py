#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from vector_store import VectorStore
from question_generator import QuestionGenerator

# Load environment variables
load_dotenv()

# Check if API key is set
if not os.getenv("PERPLEXITY_API_KEY"):
    print("Error: PERPLEXITY_API_KEY environment variable not set")
    print("Please set it in the .env file")
    sys.exit(1)

def main():
    # Initialize vector store
    vector_store = VectorStore()
    vector_store.initialize()
    
    # Load questions from transcripts folder
    script_dir = Path(__file__).parent
    transcripts_dir = script_dir / "transcripts"
    vector_store.load_questions_from_folder(transcripts_dir)
    
    print("Vector store initialized and loaded questions from transcripts folder\n")
    
    # Search for questions about a specific topic
    search_term = "restaurant"
    print(f"Searching for questions about '{search_term}'...")
    results = vector_store.search(search_term, limit=3)
    
    # Display search results
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Source: {result.get('source', 'Unknown')}")
        print(f"Question: {result.get('question_number', '')}")
        print(f"Introduction: {result.get('introduction', '')}")
        print(f"Conversation: {result.get('conversation', '')}")
        print(f"Question: {result.get('question', '')}")
    
    # Generate derivative questions
    print("\nGenerating derivative questions...")
    generator = QuestionGenerator()
    
    # Get the first result with a conversation
    seed_question = None
    for result in results:
        if result.get('conversation'):
            seed_question = result
            break
    
    if not seed_question:
        print("No suitable seed question found with conversation content")
        return
    
    # Generate questions based on the seed question
    questions = generator.generate_questions(
        seed_question.get('conversation', ''),
        count=2,
        level="N3",
        topic="restaurant conversation about ordering food"
    )
    
    if questions:
        print(f"\nGenerated {len(questions)} questions:\n")
        for i, q in enumerate(questions, 1):
            print(f"Question {i}:")
            print(f"Number: {q.get('number', f'Generated Question {i}')}")
            print(f"Introduction: {q.get('introduction', '')}")
            print(f"Conversation: {q.get('conversation', '')}")
            print(f"Question: {q.get('question', '')}\n")
    else:
        print("Failed to generate questions. Check API response.")
    
    # Show total question count
    count = vector_store.get_question_count()
    print(f"Total questions in vector store: {count}")

if __name__ == "__main__":
    main()
