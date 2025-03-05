import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.structured_data import JLPTTranscriptStructurer, main

def test_manual_extraction():
    """Test the manual extraction method with a sample transcript"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to a sample transcript
    transcript_path = os.path.join(script_dir, "transcripts", "sY7L5cfCWno.txt")
    
    # Create output path
    output_path = os.path.join(script_dir, "transcripts", "sY7L5cfCWno.structured.txt")
    
    # Run manual extraction (without Perplexity API)
    structured_data = main(transcript_path, output_path, use_perplexity=False)
    
    print(f"Extracted {len(structured_data)} questions from the transcript")
    print(f"Output saved to: {output_path}")
    
    # Print the first question as an example
    if structured_data:
        print("\nExample of the first extracted question:")
        print(f"Question Number: {structured_data[0]['question_number']}")
        print(f"Introduction: {structured_data[0]['introduction'][:100]}...")
        print(f"Conversation: {structured_data[0]['conversation'][:100]}...")
        print(f"Question: {structured_data[0]['question'][:100]}...")

if __name__ == "__main__":
    test_manual_extraction()
