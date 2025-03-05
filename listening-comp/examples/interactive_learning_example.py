import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.vector_store import VectorStore
from backend.question_generator import QuestionGenerator

# Load environment variables
load_dotenv()

# Initialize vector store
vector_store = VectorStore()

# Initialize question generator
question_generator = QuestionGenerator()

def demonstrate_vector_search():
    """Demonstrate how vector search works with a simple example."""
    print("\n=== Vector Search Demonstration ===")
    
    # Example topic
    topic = "Japanese greetings"
    print(f"\nSearching for content related to: '{topic}'")
    
    # Perform vector search
    search_results = vector_store.search(topic, top_k=3)
    
    print(f"\nFound {len(search_results)} relevant documents:")
    for i, result in enumerate(search_results):
        print(f"\nResult {i+1}:")
        print(f"Content: {result['document']}")
        print(f"Metadata: {result['metadata']}")
        print(f"Relevance Score: {result['score']:.4f}")
    
    return search_results

def demonstrate_question_generation(search_results):
    """Demonstrate how questions are generated based on search results."""
    print("\n=== Question Generation Demonstration ===")
    
    # Example topic
    topic = "Japanese greetings"
    
    # Generate context from search results
    context = "\n".join([result["document"] for result in search_results])
    
    print(f"\nGenerating questions about '{topic}' based on retrieved content...")
    
    # Generate questions
    questions = question_generator.generate_questions(topic, context)
    
    print(f"\nGenerated {len(questions)} questions:")
    for i, question in enumerate(questions):
        print(f"\nQuestion {i+1}: {question['question']}")
        print(f"Answer: {question['answer']}")
        print(f"Options: {', '.join(question['options'])}")
    
    return questions

def main():
    print("Interactive Learning Example")
    print("=============================")
    
    # Check if vector store is initialized
    if not vector_store.is_initialized():
        print("\nInitializing vector store with sample data...")
        # Add some sample data
        vector_store.add_documents([
            "In Japanese, 'ohayou gozaimasu' means 'good morning'.",
            "'Konnichiwa' is used as a greeting during the day, similar to 'hello' or 'good afternoon'.",
            "'Konbanwa' means 'good evening' in Japanese.",
            "When meeting someone for the first time, Japanese people often say 'hajimemashite' followed by their name.",
            "'Sayounara' is a formal way to say goodbye in Japanese.",
            "'Arigatou gozaimasu' means 'thank you very much' in Japanese."
        ])
    
    # Demonstrate vector search
    search_results = demonstrate_vector_search()
    
    # Demonstrate question generation
    questions = demonstrate_question_generation(search_results)
    
    print("\n=== How This Works in the Streamlit App ===")
    print("1. User selects a topic from the dropdown menu")
    print("2. Vector search finds relevant content based on the topic")
    print("3. Question generator creates questions using the retrieved content")
    print("4. Questions are presented to the user in a multiple-choice format")
    print("5. User receives immediate feedback on their answers")

if __name__ == "__main__":
    main()
