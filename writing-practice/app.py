import streamlit as st
import requests
from PIL import Image
import io
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
import logging
import json
import os
from dotenv import load_dotenv
import time
import random
import functools
import re

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppState(Enum):
    SETUP = "setup"
    PRACTICE = "practice"
    REVIEW = "review"

@dataclass
class GradingResult:
    transcription: str
    translation: str
    score: str
    feedback: str

@dataclass
class GeneratedContent:
    japanese_word: str
    japanese_sentence: str
    english_sentence: str

# Cache the fetch_words function to prevent multiple API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_fetch_words(group_id: str) -> List[dict]:
    try:
        logger.info(f"Fetching words for group {group_id} (should only see this once)")
        response = requests.get(
            f"http://127.0.0.1:5000/api/groups/{group_id}/words",
            headers={
                "Origin": "http://localhost:8501",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 403:
            logger.error(f"CORS error (403 Forbidden): {response.text}")
            return []
        
        if response.ok:
            words = response.json().get("items", [])
            logger.info(f"Successfully fetched {len(words)} words")
            return words
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.exception(f"Failed to fetch words: {str(e)}")
        return []

# Define callback functions
def on_generate_click():
    st.session_state.pending_generate = True
    logger.info("Generate button clicked, pending_generate set to True")

def on_submit_click():
    # Capture the file uploader's current value
    if 'upload_practice' in st.session_state:
        # Store a reference to the uploaded file
        st.session_state.file_for_processing = st.session_state.upload_practice
        logger.info(f"File captured for processing: {st.session_state.file_for_processing is not None}")
    
    st.session_state.pending_submit = True
    logger.info("Submit button clicked, pending_submit set to True")

def on_next_click():
    st.session_state.pending_next = True
    logger.info("Next button clicked, pending_next set to True")

class WritingPracticeApp:
    def __init__(self):
        # Get group_id from query params
        query_params = st.query_params
        self.group_id = query_params.get("group_id", "1")
        
        # Initialize session state variables
        self._initialize_session_state()
        
        # Process any pending actions from previous run
        self._process_pending_actions()

    def _initialize_session_state(self):
        """Initialize all session state variables if they don't exist"""
        if "app_initialized" not in st.session_state:
            logger.info("Initializing app for first time")
            
            # App state - store as string instead of enum
            if "state" not in st.session_state:
                st.session_state.state = AppState.SETUP.value
        
            # Words data
            if "words" not in st.session_state:
                st.session_state.words = cached_fetch_words(self.group_id)
            
            # Content
            if "generated_content" not in st.session_state:
                st.session_state.generated_content = None
            
            if "grading_result" not in st.session_state:
                st.session_state.grading_result = None
            
            # Action flags
            if "pending_generate" not in st.session_state:
                st.session_state.pending_generate = False
            
            if "pending_submit" not in st.session_state:
                st.session_state.pending_submit = False
            
            if "pending_next" not in st.session_state:
                st.session_state.pending_next = False
            
            # API call tracking
            if "api_call_made" not in st.session_state:
                st.session_state.api_call_made = False
                
            st.session_state.app_initialized = True
            logger.info("App initialization complete")

    def _process_pending_actions(self):
        """Process any pending actions from button clicks"""
        if st.session_state.pending_generate:
            logger.info("Processing pending generate action")
            # Only generate if we haven't already made the API call
            if not st.session_state.api_call_made:
                self.generate_sentence()
                st.session_state.api_call_made = True
                logger.info("API call flag set to prevent duplicate calls")
            st.session_state.pending_generate = False
        
        # Add debug logging
        logger.info(f"Pending submit: {st.session_state.pending_submit}")
        logger.info(f"File_for_processing exists: {'file_for_processing' in st.session_state}")
        if 'file_for_processing' in st.session_state:
            logger.info(f"File_for_processing value: {st.session_state.file_for_processing is not None}")
        
        if st.session_state.pending_submit and 'file_for_processing' in st.session_state and st.session_state.file_for_processing is not None:
            logger.info("Processing pending submit action")
            try:
                image = Image.open(st.session_state.file_for_processing)
                result = self.grade_submission(image)
                st.session_state.grading_result = result
                # Force state transition
                st.session_state.state = AppState.REVIEW.value
                logger.info(f"Set state to REVIEW: {st.session_state.state}")
            except Exception as e:
                logger.exception(f"Error processing image: {str(e)}")
            finally:
                st.session_state.pending_submit = False
        
        if st.session_state.pending_next:
            logger.info("Processing pending next action")
            # Reset API call flag so we can make a new call
            st.session_state.api_call_made = False
            self.generate_sentence()
            st.session_state.grading_result = None
            st.session_state.state = AppState.PRACTICE.value
            st.session_state.pending_next = False

    def parse_perplexity_response(self, response_text: str) -> tuple:
        """Parse the Perplexity API response to extract Japanese and English sentences"""
        # Remove thinking part
        response_text = re.sub(r'<think>[\s\S]*?<\/think>', '', response_text).strip()
        
        # Extract Japanese and English parts
        japanese_match = re.search(r'Japanese:\s*(.*?)(?=English:|$)', response_text, re.DOTALL)
        english_match = re.search(r'English:\s*(.*?)$', response_text, re.DOTALL)
        
        japanese_sentence = japanese_match.group(1).strip() if japanese_match else ""
        english_sentence = english_match.group(1).strip() if english_match else ""
        
        return japanese_sentence, english_sentence

    def generate_sentence(self):
        """Generate a sentence using Perplexity API based on a Japanese word from the current word list"""
        logger.info("Generate sentence method called")
        
        if not st.session_state.words:
            logger.warning("No words available for practice")
            st.session_state.generated_content = GeneratedContent(
                japanese_word="N/A",
                japanese_sentence="No words available for practice",
                english_sentence="No words available for practice"
            )
            st.session_state.state = AppState.PRACTICE.value
            return
        
        # Use a random word from the list
        word = random.choice(st.session_state.words) 
        #word = st.session_state.words[0] #Using Hello
        japanese_word = word.get('japanese', '')
        logger.info(f"Selected word: {japanese_word}")
        
        # Show loading message
        with st.spinner(f"Generating a sentence with '{japanese_word}'..."):
            try:
                generated_response = self.generate_sentence_with_perplexity(japanese_word) 
                #Not calling Perplexity again adn again for testing.
                #generated_response = f"""<think>Thus, the sentence would be: こんにちは、私は先生です。 (Hello, I am a teacher.) It meets all requirements: uses the given word, N5 grammar, and simple vocabulary.</think>
                #Japanese: こんにちは、私は先生です。  
                #English: Hello, I am a teacher.
                #"""
                logger.info(f"API returned response: {generated_response}")
                
                if generated_response:
                    japanese_sentence, english_sentence = self.parse_perplexity_response(generated_response)
                    
                    # Store the generated content in session state
                    st.session_state.generated_content = GeneratedContent(
                        japanese_word=japanese_word,
                        japanese_sentence=japanese_sentence,
                        english_sentence=english_sentence
                    )
                else:
                    # Fallback if API fails
                    st.session_state.generated_content = GeneratedContent(
                        japanese_word=japanese_word,
                        japanese_sentence=f"Please write a sentence using the word: {japanese_word}",
                        english_sentence="API failed to generate a sentence"
                    )
            except Exception as e:
                logger.exception(f"Failed to generate sentence: {str(e)}")
                # Fallback if exception
                st.session_state.generated_content = GeneratedContent(
                    japanese_word=japanese_word,
                    japanese_sentence=f"Please write a sentence using the word: {japanese_word}",
                    english_sentence="Error generating sentence"
                )
        
        logger.info(f"Final content set: {st.session_state.generated_content}")
        st.session_state.state = AppState.PRACTICE.value
    
    def generate_sentence_with_perplexity(self, word: str) -> Optional[str]:
        """Generate a sentence using the Perplexity API"""
        logger.info(f"Generating sentence with Perplexity API for word: {word}")
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            logger.error("PERPLEXITY_API_KEY environment variable not set")
            return None
        
        prompt = f"""Generate a simple Japanese sentence using the following word: {word}
                    The grammar should be scoped to JLPTN5 grammar.
                    You can use the following vocabulary to construct a simple sentence:
                    - simple objects eg. book, car, ramen, sushi
                    - simple verbs, to drink, to eat, to meet
                    - simple times eg. tomorrow, today, yesterday
                    Please provide the response in the below format without any additional explanation.
                    Japanese: [sentence in Japanese]
                    English: [sentence in English]
                    """
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar-reasoning-pro",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            logger.info("Sending request to Perplexity API")
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                sentence = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"Perplexity API returned: {sentence}")
                return sentence.strip()
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.exception(f"Failed to generate sentence: {str(e)}")
            return None        

    def grade_submission_test(self, image):
        """Grade the user's submission"""
        logger.info("Grading submission started")
        
        # Debug info
        logger.info(f"Image type: {type(image)}")
        
        # For testing, let's use a simplified grading without OCR
        # This will help identify if the OCR is the problem
        try:
            # Hard-coded result for testing
            logger.info("Creating test grading result")
            return GradingResult(
                transcription="こんにちは、私は先生です。",
                translation="Hello, I am a teacher.",
                score="S",
                feedback="Great job! Your writing matches the target sentence perfectly."
            )
        except Exception as e:
            logger.exception(f"Error in simplified grading: {str(e)}")
            return GradingResult(
                transcription="Error",
                translation="Error",
                score="C",
                feedback=f"Error in grading: {str(e)}"
            )


    def grade_submission(self, image):
        """
        Grade the user's submission using MangaOCR and Perplexity API
        
        Steps:
        1. Use MangaOCR to extract Japanese text from the uploaded image
        2. Call Perplexity API to translate the extracted text
        3. Call Perplexity API to grade the translation against the target sentence
        4. Return the grading result
        """
        logger.info("Grading submission")
        
        # Step 1: Extract text using MangaOCR
        try:
            from manga_ocr import MangaOcr
        
            # Initialize MangaOCR
            logger.info("Initializing MangaOCR")
            mocr = MangaOcr()
            
            # Save the image temporarily
            temp_path = "temp_image_correct.png"
            image.save(temp_path)
            
            # Extract text from image
            logger.info("Extracting text from image using MangaOCR")
            submission = mocr(temp_path)
            logger.info(f"Extracted text: {submission}")
            
            # Remove temp file
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
        except Exception as e:
            logger.exception(f"MangaOCR error: {str(e)}")
            return GradingResult(
                transcription="Error in OCR",
                translation="Could not process image",
                score="C",
            feedback="There was an error processing your image. Please try again with a clearer image."
        )
    
        # If no text was extracted
        if not submission or len(submission.strip()) == 0:
            logger.warning("No text extracted from image")
            return GradingResult(
                transcription="No text detected",
                translation="No text detected",
                score="C",
                feedback="No Japanese text was detected in your image. Please make sure your writing is clear and visible."
            )
        
        # Step 2: Translate the extracted text using Perplexity API
        try:
            logger.info("Translating extracted text using Perplexity API")
            translation = self.translate_text(submission)
            
            if not translation:
                logger.warning("Translation failed")
                return GradingResult(
                    transcription=submission,
                    translation="Translation failed",
                    score="C",
                    feedback="We couldn't translate your submission. Please try again."
            )
        except Exception as e:
            logger.exception(f"Translation error: {str(e)}")
            return GradingResult(
                transcription=submission,
                translation="Translation error",
                score="C",
                feedback="There was an error translating your submission."
            )
    
    # Step 3: Grade the translation against the target sentence
        try:
            logger.info("Grading translation using Perplexity API")
            content = st.session_state.generated_content
            target_sentence = content.english_sentence
            
            grading_result = self.grade_translation(target_sentence, submission, translation)
        
            if not grading_result:
                logger.warning("Grading failed")
                return GradingResult(
                    transcription=submission,
                    translation=translation,
                score="C",
                feedback="We couldn't grade your submission. Please try again."
            )
            
        # Parse the grading result
            grade_match = re.search(r'Grade:\s*([SABC])', grading_result, re.IGNORECASE)
            feedback_match = re.search(r'Feedback:\s*(.*?)$', grading_result, re.DOTALL)
        
            grade = grade_match.group(1) if grade_match else "C"
            feedback = feedback_match.group(1).strip() if feedback_match else "No specific feedback available."
        
            return GradingResult(
            transcription=submission,
            translation=translation,
            score=grade,
            feedback=feedback
        )
        
        except Exception as e:
            logger.exception(f"Grading error: {str(e)}")
            return GradingResult(
                transcription=submission,
                translation=translation,
                score="C",
                feedback="There was an error grading your submission."
            )
        
    def translate_text(self, text: str) -> Optional[str]:
        """Translate Japanese text to English using Perplexity API"""
        logger.info(f"Translating text: {text}")
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            logger.error("PERPLEXITY_API_KEY environment variable not set")
            return None
    
        system_prompt = "You are a Japanese language translator. Provide a literal, accurate translation of the Japanese text to English. Only respond with the translation, no explanations."
        user_prompt = f"Translate this Japanese text to English: {text}"
    
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
        data = {
            "model": "sonar-reasoning-pro",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
    
        try:
            logger.info("Sending translation request to Perplexity API")
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
        
            if response.status_code == 200:
                result = response.json()
                translation = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"Translation API returned: {translation}")
                # Remove thinking part if present
                translation = re.sub(r'<think>[\s\S]*?<\/think>', '', translation).strip()
                return translation
            else:
                logger.error(f"Translation API error: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.exception(f"Failed to translate text: {str(e)}")
            return None

    def grade_translation(self, target_sentence: str, submission: str, translation: str) -> Optional[str]:
        """Grade the translation against the target sentence using Perplexity API"""
        logger.info(f"Grading translation against target: {target_sentence}")
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            logger.error("PERPLEXITY_API_KEY environment variable not set")
            return None
        
        system_prompt = """You are a Japanese language teacher grading student writing.
                        Grade based on:
                        - Accuracy of translation compared to target sentence
                        - Grammar correctness
                        - Writing style and naturalness
                        Use S/A/B/C grading scale where:
                        S: Perfect or near-perfect
                        A: Very good with minor issues
                        B: Good but needs improvement
                        C: Significant issues to address"""

        user_prompt = f"""Grade this Japanese writing sample:
                        Target English sentence: {target_sentence}
                        Student's Japanese: {submission}
                        Literal translation: {translation}
                        Provide your assessment in this format:
                        Grade: [S/A/B/C]
                        Feedback: [Your detailed feedback]"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar-reasoning-pro",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        try:
            logger.info("Sending grading request to Perplexity API")
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                grading = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"Grading API returned: {grading}")
                
                # Remove thinking part if present
                grading = re.sub(r'<think>[\s\S]*?<\/think>', '', grading).strip()
                return grading
            else:
                logger.error(f"Grading API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.exception(f"Failed to grade translation: {str(e)}")
            return None

    def render_setup_state(self):
        """Render the setup state UI"""
        st.title("Japanese Writing Practice")
        st.write(f"Group ID: {self.group_id}")
        
        # Use on_click to set the flag instead of directly calling the function
        st.button("Generate Sentence", on_click=on_generate_click, key="gen_btn")

    def render_practice_state(self):
        """Render the practice state UI"""
        st.title("Japanese Writing Practice")
        
        content = st.session_state.generated_content
        if content:
            # Display the selected Japanese word
            st.subheader("Selected Japanese Word")
            st.write(content.japanese_word)
            
            # Display the Japanese sentence with a large font
            st.subheader("Generated Sentence")
            st.markdown(f"<h1 style='font-size: 40px;'>{content.japanese_sentence}</h1>", unsafe_allow_html=True)
            
            # Display the English sentence
            st.subheader("English Sentence")
            target_sentence = content.english_sentence
            st.write(target_sentence)
        
        # File uploader directly in the function
        uploaded_file = st.file_uploader(
            "Upload your written answer", 
            type=["png", "jpg", "jpeg"], 
            key="file_upload"
        )
        
        # Direct handling of submission
        if uploaded_file is not None:
            if st.button("Process Image"):
                # Process the image directly here, no session state needed
                with st.spinner("Processing your writing..."):
                    try:
                        image = Image.open(uploaded_file)
                        result = self.grade_submission(image)
                        st.session_state.grading_result = result
                        st.session_state.state = AppState.REVIEW.value
                        st.experimental_rerun()  # Force a rerun to show the review state
                    except Exception as e:
                        st.error(f"Error processing image: {str(e)}")
                        logger.exception(f"Error processing image: {str(e)}")

    def render_review_state(self):
        """Render the review state UI"""
        st.title("Japanese Writing Practice")
        
        content = st.session_state.generated_content
        if content:
            # Display the selected Japanese word
            st.subheader("Selected Japanese Word")
            st.write(content.japanese_word)
            
            # Display the Japanese sentence with a large font
            st.subheader("Generated Sentence")
            st.markdown(f"<h1 style='font-size: 32px;'>{content.japanese_sentence}</h1>", unsafe_allow_html=True)
            
            # Display the English sentence
            st.subheader("English Sentence")
            target_sentence = content.english_sentence
            st.write(target_sentence)
        
        result = st.session_state.grading_result
        st.subheader("Review")
        st.write(f"Transcription: {result.transcription}")
        st.write(f"Translation: {result.translation}")
        st.subheader(f"Score: {result.score}")
        st.subheader("Feedback")
        feedback = re.sub(r'\[\d+\]', '', result.feedback)
        st.write(feedback)
        
        # Use on_click to set the flag instead of directly calling the function
        st.button("Next Question", on_click=on_next_click, key="next_btn")

    def run(self):
        """Run the app based on current state"""
        # Get the current state string value
        current_state = st.session_state.state.value if hasattr(st.session_state.state, 'value') else st.session_state.state
        logger.info(f"Running app in state: {current_state}")
        
        # Show debug info
        st.sidebar.write(f"Current state: {current_state}")
        
        # Render the appropriate UI based on the current state
        if current_state == AppState.SETUP.value:
            self.render_setup_state()
        elif current_state == AppState.PRACTICE.value:
            self.render_practice_state()
        elif current_state == AppState.REVIEW.value:
            self.render_review_state()
        else:
            st.error(f"Unknown state: {current_state}")
            # Reset to setup state
            st.session_state.state = AppState.SETUP.value


if __name__ == "__main__":
    app = WritingPracticeApp()
    app.run()