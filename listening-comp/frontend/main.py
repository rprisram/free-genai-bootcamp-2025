import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import time

# Get the absolute path to the project root directory
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Load environment variables from backend/.env
env_path = root_dir / 'backend' / '.env'
load_dotenv(env_path)

# Debug: Print API key availability (safely)
perplexity_key = os.getenv("PERPLEXITY_API_KEY")
if perplexity_key:
    print(f"API key found: {perplexity_key[:5]}...{perplexity_key[-5:]}")
else:
    print("API key not found in environment variables")

# Now import your module
from backend.chat import BedrockChat
from backend.vector_store import VectorStore
from backend.question_generator import QuestionGenerator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from typing import Dict, List
import json
from collections import Counter
import re
import random
from backend.get_transcript import YouTubeTranscriptDownloader

# Page config
st.set_page_config(
    page_title="Japanese Learning Assistant",
    page_icon="🎌",
    layout="wide"
)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'transcript' not in st.session_state:
        st.session_state.transcript = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'vector_store' not in st.session_state:
        try:
            print("Initializing vector store...")
            # Use the existing persistent database directory
            backend_dir = root_dir / 'backend'
            persist_dir = backend_dir / "chroma_db_persistent"  # Use the directory with existing embeddings
            print(f"Using existing database directory: {persist_dir}")
            
            if persist_dir.exists():
                vector_store = VectorStore(persist_directory=str(persist_dir))
                # Initialize without loading questions since we have existing embeddings
                vector_store.initialize(load_questions=False)
                # Get collection info
                info = vector_store.get_collection_info()
                print(f"Found {info['count']} questions in existing collection")
                st.session_state.vector_store = vector_store
                print("Vector store initialized successfully with existing embeddings")
            else:
                st.error("No existing vector store found. Please run the initial setup first.")
                st.session_state.vector_store = None
        except Exception as e:
            st.session_state.vector_store = None
            print(f"Error initializing vector store: {str(e)}")
            st.error(f"Error initializing vector store: {str(e)}")
    
    if 'question_generator' not in st.session_state:
        st.session_state.question_generator = None
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None
    
    if 'bedrock_chat' not in st.session_state:
        st.session_state.bedrock_chat = BedrockChat()
    
    if 'selected_answer' not in st.session_state:
        st.session_state.selected_answer = None
    
    if 'questions_loaded' not in st.session_state:
        st.session_state.questions_loaded = True  # Set to True since we're using existing embeddings

# Initialize session state at startup
initialize_session_state()

def render_header():
    """Render the header section"""
    st.title("🎌 Japanese Learning Assistant")
    st.markdown("""
    Transform YouTube transcripts into interactive Japanese learning experiences.
    
    This tool demonstrates:
    - Base LLM Capabilities
    - RAG (Retrieval Augmented Generation)
    - Amazon Bedrock Integration
    - Agent-based Learning Systems
    """)

def render_sidebar():
    """Render the sidebar with component selection"""
    with st.sidebar:
        st.header("Development Stages")
        
        # Main component selection
        selected_stage = st.radio(
            "Select Stage:",
            [
                "1. Chat with Nova",
                "2. Raw Transcript",
                "3. Structured Data",
                "4. RAG Implementation",
                "5. Interactive Learning"
            ]
        )
        
        # Stage descriptions
        stage_info = {
            "1. Chat with Nova": """
            **Current Focus:**
            - Basic Japanese learning
            - Understanding LLM capabilities
            - Identifying limitations
            """,
            
            "2. Raw Transcript": """
            **Current Focus:**
            - YouTube transcript download
            - Raw text visualization
            - Initial data examination
            """,
            
            "3. Structured Data": """
            **Current Focus:**
            - Text cleaning
            - Dialogue extraction
            - Data structuring
            """,
            
            "4. RAG Implementation": """
            **Current Focus:**
            - Bedrock embeddings
            - Vector storage
            - Context retrieval
            """,
            
            "5. Interactive Learning": """
            **Current Focus:**
            - Scenario generation
            - Audio synthesis
            - Interactive practice
            """
        }
        
        st.markdown("---")
        st.markdown(stage_info[selected_stage])
        
        # Debug: Print API key availability (safely)
        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        if perplexity_key:
            st.success("✅ Perplexity API key found")
        else:
            st.error("❌ Perplexity API key not found")
        
        return selected_stage

def render_chat_stage():
    """Render an improved chat interface"""
    st.header("Chat with Nova")

    # Introduction text
    st.markdown("""
    Start by exploring Nova's base Japanese language capabilities. Try asking questions about Japanese grammar, 
    vocabulary, or cultural aspects.
    """)

    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Chat input area
    if prompt := st.chat_input("Ask about Japanese language..."):
        # Process the user input
        process_message(prompt)

    # Example questions in sidebar
    with st.sidebar:
        st.markdown("### Try These Examples")
        example_questions = [
            "How do I say 'Where is the train station?' in Japanese?",
            "Explain the difference between は and が",
            "What's the polite form of 食べる?",
            "How do I count objects in Japanese?",
            "What's the difference between こんにちは and こんばんは?",
            "How do I ask for directions politely?"
        ]
        
        for q in example_questions:
            if st.button(q, use_container_width=True, type="secondary"):
                # Process the example question
                process_message(q)
                st.rerun()

    # Add a clear chat button
    if st.session_state.messages:
        if st.button("Clear Chat", type="primary"):
            st.session_state.messages = []
            st.rerun()

def process_message(message: str):
    """Process a message and generate a response"""
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(message)

    # Generate and display assistant's response
    with st.chat_message("assistant", avatar="🤖"):
        response = st.session_state.bedrock_chat.generate_response(message)
        if response:
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})



def count_characters(text):
    """Count Japanese and total characters in text"""
    if not text:
        return 0, 0
        
    def is_japanese(char):
        return any([
            '\u4e00' <= char <= '\u9fff',  # Kanji
            '\u3040' <= char <= '\u309f',  # Hiragana
            '\u30a0' <= char <= '\u30ff',  # Katakana
        ])
    
    jp_chars = sum(1 for char in text if is_japanese(char))
    return jp_chars, len(text)

def render_transcript_stage():
    """Render the raw transcript stage"""
    st.header("Raw Transcript Processing")
    
    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="Enter a Japanese lesson YouTube URL"
    )
    
    # Download button and processing
    if url:
        if st.button("Download Transcript"):
            try:
                downloader = YouTubeTranscriptDownloader()
                transcript = downloader.get_transcript(url)
                if transcript:
                    # Store the raw transcript text in session state
                    transcript_text = "\n".join([entry['text'] for entry in transcript])
                    st.session_state.transcript = transcript_text
                    st.success("Transcript downloaded successfully!")
                else:
                    st.error("No transcript found for this video.")
            except Exception as e:
                st.error(f"Error downloading transcript: {str(e)}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Transcript")
        if st.session_state.transcript:
            st.text_area(
                label="Raw text",
                value=st.session_state.transcript,
                height=400,
                disabled=True
            )
    
        else:
            st.info("No transcript loaded yet")
    
    with col2:
        st.subheader("Transcript Stats")
        if st.session_state.transcript:
            # Calculate stats
            jp_chars, total_chars = count_characters(st.session_state.transcript)
            total_lines = len(st.session_state.transcript.split('\n'))
            
            # Display stats
            st.metric("Total Characters", total_chars)
            st.metric("Japanese Characters", jp_chars)
            st.metric("Total Lines", total_lines)
        else:
            st.info("Load a transcript to see statistics")

def render_structured_stage():
    """Render the structured data stage"""
    st.header("Structured Data Processing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dialogue Extraction")
        # Placeholder for dialogue processing
        st.info("Dialogue extraction will be implemented here")
        
    with col2:
        st.subheader("Data Structure")
        # Placeholder for structured data view
        st.info("Structured data view will be implemented here")

def render_rag_stage():
    """Render the RAG implementation stage"""
    st.header("RAG System")
    
    # Query input
    query = st.text_input(
        "Test Query",
        placeholder="Enter a question about Japanese..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retrieved Context")
        # Placeholder for retrieved contexts
        st.info("Retrieved contexts will appear here")
        
    with col2:
        st.subheader("Generated Response")
        # Placeholder for LLM response
        st.info("Generated response will appear here")

def render_interactive_stage():
    """Render the interactive learning stage with vector search and RAG"""
    st.header("JLPT Listening Practice")
    
    # Check if vector store is initialized
    if not st.session_state.vector_store:
        st.error("Vector store not initialized. Please check your API keys and try again.")
        return
    
    # Load questions only if needed
    if not st.session_state.questions_loaded:
        with st.spinner("Loading practice questions..."):
            try:
                transcript_dir = Path(st.session_state.vector_store.transcripts_directory)
                if transcript_dir.exists():
                    count = st.session_state.vector_store.load_questions_from_folder(transcript_dir)
                    st.session_state.questions_loaded = True
                    st.success(f"Loaded {count} practice questions successfully!")
                else:
                    st.error("No practice questions found. Please check the transcripts directory.")
                    return
            except Exception as e:
                st.error(f"Error loading questions: {str(e)}")
                return
    
    # Initialize question generator only when needed
    if not st.session_state.question_generator:
        try:
            print("Initializing question generator...")
            st.session_state.question_generator = QuestionGenerator()
            print("Question generator initialized successfully")
        except Exception as e:
            st.error(f"Error initializing question generator: {str(e)}")
            return
    
    # Practice type selection
    practice_type = st.selectbox(
        "Select Exercise Type",
        [
            "JLPT Listening Comprehension",
            "Japanese Vocabulary Quiz",
            "Daily Conversation Practice"
        ],
        key="practice_type"
    )
    
    # Topic selection for search
    topics = [
        "Daily Life",
        "School and Education",
        "Transportation",
        "Shopping and Dining",
        "Weather and Seasons",
        "Travel and Tourism",
        "Work and Business",
        "Home and Family"
    ]
    selected_topic = st.selectbox(
        "Choose Conversation Topic:",
        topics,
        key="selected_topic"
    )
    
    # Generate new question button
    if st.button("Generate Practice Question", key="generate_question"):
        with st.spinner("Creating a new practice question..."):
            try:
                # Map display topics to search terms
                topic_mapping = {
                    "Daily Life": "daily life",
                    "School and Education": "school",
                    "Transportation": "transportation",
                    "Shopping and Dining": "shopping restaurant",
                    "Weather and Seasons": "weather season",
                    "Travel and Tourism": "travel tourism",
                    "Work and Business": "work business",
                    "Home and Family": "home family"
                }
                
                search_topic = topic_mapping.get(selected_topic, selected_topic.lower())
                
                # Use vector search to find similar questions
                search_results = st.session_state.vector_store.search(search_topic, limit=3)
                
                if not search_results:
                    st.warning(f"No questions found for topic '{selected_topic}'. Try another topic.")
                    return
                
                # Reset selected answer when generating new question
                st.session_state.selected_answer = None
                st.session_state.feedback = None
                
                # Select a random result to use as seed
                seed_question = random.choice(search_results)
                
                # Generate question with options
                try:
                    # Extract answer from search results
                    correct_answer = None
                    
                    # First try to get answer directly from seed question
                    if 'answer' in seed_question:
                        correct_answer = seed_question['answer']
                    elif 'correct_answer' in seed_question:
                        correct_answer = seed_question['correct_answer']
                    
                    # If no answer found, try to extract from conversation using question
                    if not correct_answer:
                        # Generate answer using question generator
                        generated = st.session_state.question_generator.generate_questions(
                            seed_question.get('conversation', ''),
                            count=1,
                            level="N3",
                            topic=f"{selected_topic} conversation"
                        )
                        
                        if generated and len(generated) > 0:
                            # Try different possible answer fields
                            answer_fields = ['answer', 'correct_answer', 'response']
                            for field in answer_fields:
                                if field in generated[0]:
                                    correct_answer = generated[0][field]
                                    break
                    
                    # If still no answer, use a default
                    if not correct_answer:
                        correct_answer = "申し訳ありません。答えが見つかりませんでした。"
                        st.warning("Could not find the correct answer. Using a placeholder.")
                    
                    # Generate incorrect options using Perplexity with robust JSON extraction
                    prompt = f"""Based on this Japanese conversation and question, generate 3 INCORRECT but plausible Japanese answer options.
                    IMPORTANT: All options MUST be in Japanese (using Japanese characters).
                    
                    Conversation: {seed_question.get('conversation', '')}
                    Question: {seed_question.get('question', '')}
                    Correct Answer: {correct_answer}
                    
                    Rules:
                    1. Each option MUST be a complete Japanese sentence
                    2. Each option MUST use proper Japanese grammar
                    3. Each option MUST be written in Japanese characters (mix of kanji, hiragana, katakana as appropriate)
                    4. Each option should be plausible but incorrect
                    5. Each option should be different from the correct answer
                    
                    Return ONLY a JSON array with 3 incorrect Japanese options. Format: ["incorrect_option1", "incorrect_option2", "incorrect_option3"]
                    """
                    
                    incorrect_options = st.session_state.question_generator._generate_with_perplexity(prompt)
                    
                    # Use robust JSON extraction to handle various response formats
                    if isinstance(incorrect_options, list):
                        if len(incorrect_options) > 0:
                            if isinstance(incorrect_options[0], dict) and 'option' in incorrect_options[0]:
                                incorrect_answers = [item.get('option', f"選択肢 {i+1}") for i, item in enumerate(incorrect_options[:3])]
                            elif isinstance(incorrect_options[0], str):
                                incorrect_answers = incorrect_options[:3]
                            else:
                                incorrect_answers = [f"選択肢 {i+1}" for i in range(3)]
                        else:
                            incorrect_answers = [f"選択肢 {i+1}" for i in range(3)]
                    else:
                        # Try to extract JSON from the response
                        try:
                            import re
                            json_match = re.search(r'```json\s*(.*?)\s*```', str(incorrect_options), re.DOTALL)
                            if json_match:
                                import json
                                json_str = json_match.group(1)
                                parsed_options = json.loads(json_str)
                                if isinstance(parsed_options, list):
                                    incorrect_answers = parsed_options[:3]
                                else:
                                    incorrect_answers = [f"選択肢 {i+1}" for i in range(3)]
                            else:
                                incorrect_answers = [f"選択肢 {i+1}" for i in range(3)]
                        except Exception:
                            incorrect_answers = [f"選択肢 {i+1}" for i in range(3)]
                    
                    # Combine and shuffle options
                    all_options = [correct_answer] + incorrect_answers
                    random.shuffle(all_options)
                    
                    # Store question data in session state
                    st.session_state.current_question = {
                        'conversation': seed_question.get('conversation', ''),
                        'question': seed_question.get('question', ''),
                        'options': all_options,
                        'correct_answer': correct_answer
                    }
                except Exception as e:
                    st.error(f"Error generating options: {str(e)}")
                    return
            except Exception as e:
                st.error(f"Error generating question: {str(e)}")
                return
    
    # Display current question if available
    if st.session_state.current_question:
        question = st.session_state.current_question
        
        # Display conversation
        st.markdown("### Conversation")
        st.write(question.get('conversation', ''))
        
        # Display question
        st.markdown("### Question")
        st.write(question.get('question', ''))
        
        # Display options
        st.markdown("### Options")
        options = question.get('options', [])
        if not options:
            st.warning("No options available for this question.")
            return
            
        # Create labeled options with Japanese numbering
        options_with_labels = [f"選択肢{i+1}：{opt}" for i, opt in enumerate(options)]
        
        # Radio button for answer selection
        selected_option = st.radio(
            "以下から一つ選んでください (Select one answer):",
            options_with_labels,
            index=None if st.session_state.selected_answer is None else options_with_labels.index(st.session_state.selected_answer),
            key="answer_selection"
        )
        
        # Update selected answer in session state
        if selected_option:
            st.session_state.selected_answer = selected_option
        
        # Check answer button
        if st.button("答えを確認する (Check Answer)", key="check_answer"):
            if not st.session_state.selected_answer:
                st.warning("答えを選んでください。(Please select an answer first.)")
            else:
                # Get selected answer and correct answer
                selected_index = options_with_labels.index(st.session_state.selected_answer)
                correct_answer = question.get('correct_answer', '')
                
                # Check if answer is correct
                if options[selected_index] == correct_answer:
                    st.session_state.feedback = {
                        "correct": True,
                        "message": "正解です！ Correct! Well done!"
                    }
                else:
                    st.session_state.feedback = {
                        "correct": False,
                        "message": f"残念です。正解は「{correct_answer}」です。"
                    }
        
        # Display feedback if available
        if st.session_state.feedback:
            if st.session_state.feedback["correct"]:
                st.success(st.session_state.feedback["message"])
            else:
                st.error(st.session_state.feedback["message"])
    else:
        st.info("Click 'Generate Practice Question' to start practicing")

def main():
    render_header()
    selected_stage = render_sidebar()
    
    # Render appropriate stage
    if selected_stage == "1. Chat with Nova":
        render_chat_stage()
    elif selected_stage == "2. Raw Transcript":
        render_transcript_stage()
    elif selected_stage == "3. Structured Data":
        render_structured_stage()
    elif selected_stage == "4. RAG Implementation":
        render_rag_stage()
    elif selected_stage == "5. Interactive Learning":
        render_interactive_stage()
    
    # Debug section at the bottom
    with st.expander("Debug Information"):
        st.json({
            "selected_stage": selected_stage,
            "transcript_loaded": st.session_state.transcript is not None,
            "chat_messages": len(st.session_state.messages)
        })

if __name__ == "__main__":
    main()