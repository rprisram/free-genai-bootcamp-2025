#!/usr/bin/env python3

import sys
from vector_store import VectorStore

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_questions.py <search_query>")
        sys.exit(1)
    
    search_query = sys.argv[1]
    
    # Initialize vector store
    vector_store = VectorStore()
    vector_store.initialize()
    
    # Search for questions
    print(f"Searching for: {search_query}")
    results = vector_store.search(search_query, limit=5)
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Source: {result.get('source', 'Unknown')}")
        print(f"Question: {result.get('question_number', '')}")
        print(f"Introduction: {result.get('introduction', '')}")
        print(f"Conversation: {result.get('conversation', '')}")
        print(f"Question: {result.get('question', '')}")
    
    print(f"\nTotal questions in vector store: {vector_store.get_question_count()}")

if __name__ == "__main__":
    main()