# JLPT Listening Comprehension Tool

This tool extracts and processes JLPT listening comprehension questions from transcripts, stores them in a vector database, and can generate new derivative questions.

## Features

- Extract structured questions from JLPT listening transcripts
- Store questions in a ChromaDB vector database with Perplexity API embeddings
- Generate derivative questions using Perplexity API (with OpenAI fallback)

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:

```
PERPLEXITY_API_KEY=your_perplexity_api_key  # Required
OPENAI_API_KEY=your_openai_api_key  # Optional fallback
```

## Usage

### Extracting Questions from Transcripts

```bash
# Process a single transcript file
python structured_data.py path/to/transcript.txt --output path/to/output.txt

# Process all transcripts in a directory
python structured_data.py path/to/transcripts/directory

# Use manual extraction instead of Perplexity API
python structured_data.py path/to/transcript.txt --manual

# Don't add questions to vector store
python structured_data.py path/to/transcript.txt --no-vector
```

### Searching Questions in Vector Store

```bash
# Get question count
python vector_store.py --count

# Import questions from directory
python vector_store.py --import path/to/transcripts/directory

# Search for questions
python vector_store.py --search "restaurant conversation"
```

### Generating Derivative Questions

```bash
# Generate questions based on a query
python question_generator.py --query "A conversation at a restaurant" --level N3 --num 3 --output generated_questions.txt
```

### Demo

Run the demo script to see all features in action:

```bash
python demo_vector_store.py
```

## File Structure

- `structured_data.py`: Extracts structured questions from transcripts
- `vector_store.py`: Manages the ChromaDB vector store with Perplexity API embeddings
- `question_generator.py`: Generates derivative questions using Perplexity API
- `demo_vector_store.py`: Demonstrates all features

## Notes

- The vector store is persisted in the `./chroma_db` directory
- Perplexity API is required for both embeddings and question generation
- OpenAI API is optional and only used as a fallback for question generation if Perplexity fails
- The embedding function now tries to use the Perplexity API's `sonar` model for embeddings first, with a fallback to a hash-based approach if the API call fails
- The system prioritizes using Perplexity API for all operations, with OpenAI as a fallback only when necessary
