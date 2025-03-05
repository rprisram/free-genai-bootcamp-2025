# language-learning-assistant
This is for the generative AI bootcamp

**Difficulty:** Level 200 *(Due to RAG implementation and multiple AWS services integration)*

**Business Goal:**
A progressive learning tool that demonstrates how RAG and agents can enhance language learning by grounding responses in real Japanese lesson content. The system shows the evolution from basic LLM responses to a fully contextual learning assistant, helping students understand both the technical implementation and practical benefits of RAG.

**Technical Uncertainty:**
1. How effectively can we process and structure bilingual (Japanese/English) content for RAG?
2. What's the optimal way to chunk and embed Japanese language content?
3. How can we effectively demonstrate the progression from base LLM to RAG to students?
4. Can we maintain context accuracy when retrieving Japanese language examples?
5. How do we balance between giving direct answers and providing learning guidance?
6. What's the most effective way to structure multiple-choice questions from retrieved content?

**Technical Restrictions:**
* Must use Amazon Bedrock for:
   * API (converse, guardrails, embeddings, agents) (https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
     * Aamzon Nova Micro for text generation (https://aws.amazon.com/ai/generative-ai/nova)
   * Titan for embeddings
* Must implement in Streamlit, pandas (data visualization)
* Must use SQLite for vector storage
* Must handle YouTube transcripts as knowledge source (YouTubeTranscriptApi: https://pypi.org/project/youtube-transcript-api/)
* Must demonstrate clear progression through stages:
   * Base LLM
   * Raw transcript
   * Structured data
   * RAG implementation
   * Interactive features
* Must maintain clear separation between components for teaching purposes
* Must include proper error handling for Japanese text processing
* Must provide clear visualization of RAG process
* Should work within free tier limits where possible

This structure:
1. Sets clear expectations
2. Highlights key technical challenges
3. Defines specific constraints
4. Keeps focus on both learning outcomes and technical implementation

## KnowledgeBase

https://github.com/chroma-core/chroma

## Interactive Learning Feature

The application now includes an interactive learning feature that uses vector search and RAG (Retrieval Augmented Generation) to create a dynamic, context-aware language learning experience.

### Features

- **Topic-Based Learning**: Select from various Japanese language topics to practice
- **Vector Search**: Uses semantic search to find relevant questions based on your selected topic
- **Dynamic Question Generation**: Creates new questions based on retrieved content
- **Multiple-Choice Format**: Practice with interactive multiple-choice questions
- **Immediate Feedback**: Get instant feedback on your answers

### How to Use

1. Run the Streamlit app: `streamlit run frontend/main.py`
2. Navigate to the "Interactive Learning" tab
3. Select a topic from the dropdown menu
4. Click "Generate Questions" to create practice questions
5. Answer the multiple-choice questions and receive immediate feedback

### Technical Implementation

- Uses ChromaDB for vector storage and semantic search
- Leverages Perplexity API for embeddings and question generation
- Implements RAG techniques to generate contextually relevant questions
- Stores vector embeddings in a persistent ChromaDB database

### Requirements

- Perplexity API key (stored in `.env` file)
- Python packages: streamlit, chromadb, perplexity, python-dotenv

### Future Enhancements

- Audio playback integration
- Expanded topic coverage
- User progress tracking
- Difficulty level progression