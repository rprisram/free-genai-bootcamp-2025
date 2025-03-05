from typing import List, Dict, Optional, Union, Any
import re
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

class JLPTTranscriptStructurer:
    """
    Class to structure JLPT listening practice test transcripts into a standardized format
    with Introduction, Conversation, and Question components for each test item.
    """
    
    def __init__(self, perplexity_api_key: Optional[str] = None):
        """
        Initialize the JLPTTranscriptStructurer
        
        Args:
            perplexity_api_key (Optional[str]): API key for Perplexity Pro
        """
        # First try to use the provided API key, then check environment variables
        self.perplexity_api_key = perplexity_api_key or os.environ.get('PERPLEXITY_API_KEY')
        
        if self.perplexity_api_key:
            print(f"Perplexity API key found: {self.perplexity_api_key[:5]}...{self.perplexity_api_key[-5:]}")
        else:
            print("Warning: No Perplexity API key provided. Structured extraction may not work.")
    
    def read_transcript(self, transcript_path: str) -> str:
        """
        Read transcript file content
        
        Args:
            transcript_path (str): Path to transcript file
            
        Returns:
            str: Transcript content
        """
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading transcript file: {str(e)}")
            return ""
    
    def extract_questions_with_perplexity(self, transcript_text: str) -> List[Dict[str, str]]:
        """Extract structured questions from transcript using Perplexity Pro's Sonar-reasoning-pro model
        
        Args:
            transcript_text (str): Raw transcript text
            
        Returns:
            List[Dict[str, str]]: List of structured questions with Introduction, Conversation, and Question
        """
        if not self.perplexity_api_key:
            raise ValueError("Perplexity API key is required for this operation")
        
        # Create a prompt for Perplexity API
        prompt = f"""
        I need you to extract all questions from this Japanese Language Proficiency Test (JLPT) listening transcript.
        
        IMPORTANT INSTRUCTIONS:
        1. The transcript contains at least 40 questions total, divided into multiple sections.
        2. Each question has an introduction, conversation, and the actual question.
        3. You MUST extract ALL questions from ALL sections. Do not stop after a few questions.
        4. Format each question as a JSON object with the following fields:
           - question_number: Include both section number and question number (e.g., "Section 1 Question 2")
           - introduction: The context or setup for the question
           - conversation: The dialogue or content being discussed
           - question: The actual question being asked
        
        5. Return your answer as a JSON array of these question objects. The format should be exactly:
        ```json
        [
          {{
            "question_number": "Section X Question Y",
            "introduction": "...",
            "conversation": "...",
            "question": "..."
          }},
          ... (all other questions)
        ]
        ```
        
        6. DO NOT include any explanations, markdown, or additional text outside of the JSON array.
        7. Make sure to process the ENTIRE transcript and extract ALL questions.
        8. If a section is unclear, make your best guess at the structure.
        
        Here is the transcript:
        {transcript_text}
        """
        
        # Make API request to Perplexity with retry mechanism
        max_retries = 3
        retry_delay = 5  # seconds
        
        for retry_count in range(max_retries):
            try:
                print(f"Making Perplexity API request (attempt {retry_count + 1}/{max_retries})...")
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar-reasoning-pro",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.0,
                        "max_tokens": 8000
                    }
                )
                
                if response.status_code != 200:
                    print(f"Error from Perplexity API: {response.status_code} - {response.text}")
                    if retry_count < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print("Maximum retries reached. Falling back to manual extraction.")
                        return []
                
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Print the first part of the response for debugging
                print(f"Received response from Perplexity API ({len(content)} characters)")
                print(f"Response preview: {content[:200]}..." if len(content) > 200 else content)
                
                # Try multiple approaches to extract JSON
                structured_data = []
                
                # Approach 1: Try to parse the entire content as JSON
                try:
                    structured_data = json.loads(content)
                    if isinstance(structured_data, list):
                        return structured_data
                except json.JSONDecodeError:
                    pass
                
                # Approach 2: Extract JSON array with regex
                try:
                    json_match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        structured_data = json.loads(json_str)
                        if isinstance(structured_data, list):
                            return structured_data
                except (json.JSONDecodeError, AttributeError):
                    pass
                
                # Approach 3: Try to find JSON without the brackets
                try:
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        json_str = f"[{json_match.group(0)}]"
                        structured_data = json.loads(json_str)
                        if isinstance(structured_data, list):
                            return structured_data
                except (json.JSONDecodeError, AttributeError):
                    pass
                
                # Approach 4: Look for code blocks that might contain JSON
                try:
                    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
                    if code_block_match:
                        code_content = code_block_match.group(1).strip()
                        structured_data = json.loads(code_content)
                        if isinstance(structured_data, list):
                            print(f"Successfully extracted {len(structured_data)} questions from code block")
                            return structured_data
                except (json.JSONDecodeError, AttributeError):
                    pass
                
                # Approach 5: Try to extract multiple JSON objects and combine them
                try:
                    json_objects = re.findall(r'\{[^{}]*\}', content)
                    if json_objects:
                        combined_data = []
                        for json_obj in json_objects:
                            try:
                                obj_data = json.loads(json_obj)
                                if isinstance(obj_data, dict) and any(k in obj_data for k in ['question_number', 'question']):
                                    combined_data.append(obj_data)
                            except json.JSONDecodeError:
                                continue
                        if combined_data:
                            print(f"Successfully extracted {len(combined_data)} questions from multiple JSON objects")
                            return combined_data
                except Exception as e:
                    print(f"Error in approach 5: {str(e)}")
                    pass
                
                # If all approaches fail, print the content for debugging
                print("Could not extract JSON from Perplexity response. Response content:")
                print(content[:500] + "..." if len(content) > 500 else content)
                
                # Try to analyze the response to see if it contains any questions
                question_markers = ['question_number', 'introduction', 'conversation', 'question']
                has_markers = all(marker in content for marker in question_markers)
                if has_markers:
                    print("The response contains question markers but could not be parsed as JSON.")
                    print("Attempting to clean up the response and extract JSON...")
                    
                    # Try to find JSON-like structures and fix common issues
                    # 1. Fix single quotes to double quotes
                    fixed_content = content.replace("'", '"')
                    
                    # 2. Fix unquoted keys
                    for marker in question_markers:
                        fixed_content = re.sub(f'([{{,])\s*{marker}\s*:', f'\\1"{marker}":', fixed_content)
                    
                    # 3. Try to extract the JSON array again
                    try:
                        json_match = re.search(r'\[\s*\{.*\}\s*\]', fixed_content, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(0)
                            structured_data = json.loads(json_str)
                            if isinstance(structured_data, list):
                                print(f"Successfully extracted {len(structured_data)} questions after fixing JSON format")
                                return structured_data
                    except (json.JSONDecodeError, AttributeError) as e:
                        print(f"Still failed to parse JSON after cleanup: {str(e)}")
                
                # Count the number of questions in the transcript
                question_count = len(re.findall(r'[\u4e00-\u9fa5\s]*\d+', transcript_text))
                print(f"Detected approximately {question_count} questions in the transcript")
                
                return []
                
            except Exception as e:
                print(f"Error calling Perplexity API: {str(e)}")
                return []
    
    def extract_questions_manually(self, transcript_text: str) -> List[Dict[str, str]]:
        """
        Manually extract structured questions from transcript using pattern matching
        (fallback method if Perplexity API is not available)
        
        Args:
            transcript_text (str): Raw transcript text
            
        Returns:
            List[Dict[str, str]]: List of structured questions with Introduction, Conversation, and Question
        """
        # For JLPT listening transcripts, a more specialized approach
        questions = []
        question_number = 1
        
        # First, try to find the main problem sections (問題1, 問題2, etc.)
        problem_sections = re.split(r'問題(\d+)', transcript_text)
        
        if len(problem_sections) > 1:
            # We found problem sections
            for i in range(1, len(problem_sections), 2):
                if i < len(problem_sections):
                    section_num = problem_sections[i]
                    section_content = problem_sections[i+1] if i+1 < len(problem_sections) else ""
                    
                    # For each section, find individual questions (1番, 2番, etc.)
                    question_parts = re.split(r'(\d+番)', section_content)
                    
                    if len(question_parts) > 1:
                        for j in range(1, len(question_parts), 2):
                            if j+1 < len(question_parts):
                                q_num = question_parts[j].strip('番')
                                q_content = question_parts[j+1]
                                
                                # Try to extract the three parts
                                # For JLPT, typically the question is at the end, repeated
                                q_lines = q_content.split('\n')
                                
                                # The introduction is usually at the beginning
                                introduction = q_lines[0] if q_lines else ""
                                
                                # The question is usually repeated at the end
                                question = q_lines[-1] if len(q_lines) > 1 else ""
                                
                                # The conversation is everything in between
                                conversation = '\n'.join(q_lines[1:-1]) if len(q_lines) > 2 else ""
                                
                                # If any part is empty, use a more general approach
                                if not introduction or not conversation or not question:
                                    # Split into thirds as a fallback
                                    third = len(q_content) // 3
                                    introduction = q_content[:third]
                                    conversation = q_content[third:2*third]
                                    question = q_content[2*third:]
                                
                                questions.append({
                                    'question_number': f"{section_num}-{q_num}",
                                    'introduction': introduction.strip(),
                                    'conversation': conversation.strip(),
                                    'question': question.strip()
                                })
                    else:
                        # If we couldn't find numbered questions, try to split by patterns
                        # Try to find where conversations start and end
                        lines = section_content.split('\n')
                        current_question = {'introduction': '', 'conversation': '', 'question': ''}
                        current_part = 'introduction'
                        
                        for line in lines:
                            if not line.strip():
                                continue
                                
                            # Look for conversation markers
                            if current_part == 'introduction' and any(marker in line for marker in ['：', '「', 'A：', 'B：', '男：', '女：']):
                                current_part = 'conversation'
                                
                            # Look for question markers
                            elif current_part == 'conversation' and any(marker in line for marker in ['ですか', '何', 'どこ', 'いつ', 'どの', 'どう']):
                                current_part = 'question'
                                
                            # Add the line to the current part
                            current_question[current_part] += line + '\n'
                            
                            # If we've completed a question, add it to the list
                            if current_part == 'question' and line.endswith('か。'):
                                questions.append({
                                    'question_number': f"{section_num}-{question_number}",
                                    'introduction': current_question['introduction'].strip(),
                                    'conversation': current_question['conversation'].strip(),
                                    'question': current_question['question'].strip()
                                })
                                question_number += 1
                                current_question = {'introduction': '', 'conversation': '', 'question': ''}
                                current_part = 'introduction'
                        
                        # If we have a partial question at the end, add it
                        if current_question['introduction'] or current_question['conversation'] or current_question['question']:
                            questions.append({
                                'question_number': f"{section_num}-{question_number}",
                                'introduction': current_question['introduction'].strip(),
                                'conversation': current_question['conversation'].strip(),
                                'question': current_question['question'].strip()
                            })
            # If we still couldn't extract any questions, use a simple approach
            if not questions:
                # Try to split by blank lines
                sections = section_content.split('\n\n')
                for i, section in enumerate(sections):
                    if len(section.strip()) > 50:  # Only process substantial sections
                        lines = section.split('\n')
                        third = len(lines) // 3
                        
                        questions.append({
                            'question_number': f"{section_num}-{i+1}",
                            'introduction': '\n'.join(lines[:third]).strip(),
                            'conversation': '\n'.join(lines[third:2*third]).strip(),
                            'question': '\n'.join(lines[2*third:]).strip()
                        })
        else:
            # If we couldn't find problem sections, try to split by patterns
            # Try a different approach - look for conversation patterns
            conversations = re.split(r'(\n\s*[A-Z]：|\n\s*男：|\n\s*女：)', transcript_text)
            
            if len(conversations) > 1:
                for i in range(1, len(conversations), 2):
                    if i+1 < len(conversations):
                        marker = conversations[i].strip()
                        content = conversations[i+1]
                        
                        # Try to find the question at the end
                        question_match = re.search(r'([^。]+(?:か|ですか)[。]?)$', content)
                        if question_match:
                            question = question_match.group(0)
                            remaining = content[:content.rfind(question)]
                            
                            # Split the remaining content into introduction and conversation
                            lines = remaining.split('\n')
                            introduction = lines[0] if lines else ""
                            conversation = marker + '\n'.join(lines[1:]) if len(lines) > 1 else ""
                            
                            questions.append({
                                'question_number': str(question_number),
                                'introduction': introduction.strip(),
                                'conversation': conversation.strip(),
                                'question': question.strip()
                            })
                            question_number += 1
            else:
                # If all else fails, just divide the text into sections
                # This is a very basic fallback
                sections = transcript_text.split('\n\n')
                for i, section in enumerate(sections):
                    if len(section.strip()) > 50:  # Only process substantial sections
                        lines = section.split('\n')
                        third = len(lines) // 3
                        
                        questions.append({
                            'question_number': str(i+1),
                            'introduction': '\n'.join(lines[:third]).strip(),
                            'conversation': '\n'.join(lines[third:2*third]).strip(),
                            'question': '\n'.join(lines[2*third:]).strip()
                        })
        
        # If we still couldn't extract any questions, use a simple approach
        if not questions:
            # Simple fallback: split the text into roughly equal thirds
            lines = transcript_text.split('\n')
            third = len(lines) // 3
            
            questions.append({
                'question_number': '1',
                'introduction': '\n'.join(lines[:third]),
                'conversation': '\n'.join(lines[third:2*third]),
                'question': '\n'.join(lines[2*third:])
            })
        
        return questions
    
    def structure_transcript(self, transcript_path: str, output_path: str = None, add_to_vector: bool = True) -> List[Dict[str, str]]:
        """Structure a transcript file into questions and save to output file if provided."""
        print(f"Processing transcript: {transcript_path}")
        
        # Read transcript file
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        
        # Try to extract questions using Perplexity API first
        print("Attempting to extract questions using Perplexity API...")
        structured_data = self.extract_questions_with_perplexity(transcript_text)
        
        # Verify we got a reasonable number of questions
        if structured_data and len(structured_data) > 0:
            print(f"Successfully extracted {len(structured_data)} questions using Perplexity API")
            
            # If we got significantly fewer questions than expected, try manual extraction as well
            expected_min_questions = 20  # We expect at least 20 questions for a typical JLPT transcript
            if len(structured_data) < expected_min_questions:
                print(f"Warning: Extracted only {len(structured_data)} questions, which is fewer than expected (at least {expected_min_questions})")
                print("Attempting manual extraction as a backup...")
                manual_data = self.extract_questions_manually(transcript_text)
                
                # If manual extraction got more questions, use that instead
                if len(manual_data) > len(structured_data):
                    print(f"Manual extraction found {len(manual_data)} questions, which is better than Perplexity's {len(structured_data)}")
                    structured_data = manual_data
                else:
                    print(f"Manual extraction found {len(manual_data)} questions, which is not better than Perplexity's {len(structured_data)}")
                    # Keep the Perplexity results
        else:
            print("Failed to extract questions using Perplexity API, falling back to manual extraction")
            structured_data = self.extract_questions_manually(transcript_text)
            print(f"Manually extracted {len(structured_data)} questions")
        
        # Save structured data to output file if provided
        if output_path and structured_data:
            print(f"Saving structured data to {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in structured_data:
                    f.write(f"Question: {item.get('question_number', 'Unknown')}\n")
                    f.write(f"Introduction: {item.get('introduction', '')}\n")
                    f.write(f"Conversation: {item.get('conversation', '')}\n")
                    f.write(f"Question: {item.get('question', '')}\n")
                    f.write("\n")
            print(f"Successfully saved {len(structured_data)} questions to {output_path}")
        
        # Add to vector store if requested
        if add_to_vector and structured_data:
            source_file = os.path.basename(transcript_path)
            self.add_to_vector_store(structured_data, source_file)
        
        return structured_data
    
    def add_to_vector_store(self, structured_data: List[Dict[str, str]], source_file: str) -> bool:
        """Add structured data to vector store
        
        Args:
            structured_data (List[Dict[str, str]]): List of structured questions
            source_file (str): Source file name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if Perplexity API key is available
            if not self.perplexity_api_key:
                print("Error: Perplexity API key is required for vector store operations")
                return False
                
            # Import vector store module
            from vector_store import JLPTQuestionVectorStore
            
            # Initialize vector store with Perplexity API key
            vector_store = JLPTQuestionVectorStore(perplexity_api_key=self.perplexity_api_key)
            
            # Add questions to vector store
            count = vector_store.add_questions(structured_data, source_file)
            print(f"Added {count} questions to vector store using Perplexity embeddings")
            
            return True
        except Exception as e:
            print(f"Error adding to vector store: {str(e)}")
            return False
    
    def save_structured_data(self, structured_data: List[Dict[str, str]], output_path: str) -> bool:
        """
        Save structured data to a text file
        
        Args:
            structured_data (List[Dict[str, str]]): Structured data to save
            output_path (str): Path to save the text file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in structured_data:
                    # Check if all required keys are present
                    question_number = item.get('question_number', 'Unknown')
                    introduction = item.get('introduction', '')
                    conversation = item.get('conversation', '')
                    question = item.get('question', '')
                    
                    f.write(f"Question {question_number}\n")
                    f.write(f"Introduction:\n{introduction}\n\n")
                    f.write(f"Conversation:\n{conversation}\n\n")
                    f.write(f"Question:\n{question}\n\n")
                    f.write("-" * 50 + "\n\n")
            print(f"Structured data saved successfully to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving structured data: {str(e)}")
            return False

    @staticmethod
    def process_directory(directory_path: str, use_perplexity: bool = True, add_to_vector: bool = True):
        """Process all transcript files in a directory"""
        print(f"Processing all transcript files in {directory_path}")
        
        # Get API key
        perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        if not perplexity_api_key:
            print("Error: Perplexity API key is required. Please set PERPLEXITY_API_KEY in your .env file.")
            if add_to_vector:
                print("Disabling vector store integration due to missing API key.")
                add_to_vector = False
            if use_perplexity:
                print("Falling back to manual extraction due to missing API key.")
                use_perplexity = False
        
        # Create structurer
        structurer = JLPTTranscriptStructurer(perplexity_api_key=perplexity_api_key)
        
        # Get all transcript files
        transcript_files = [f for f in Path(directory_path).glob("*.txt") 
                          if not f.name.endswith(".structured.txt")]
        
        print(f"Found {len(transcript_files)} transcript files")
        
        # Process each file
        for transcript_file in transcript_files:
            try:
                # Generate output path
                output_path = transcript_file.with_name(f"{transcript_file.stem}.structured.txt")
                
                # Skip if output file already exists
                if output_path.exists():
                    print(f"Skipping {transcript_file.name} as structured file already exists")
                    continue
                
                # Process transcript
                print(f"Processing {transcript_file.name}...")
                structured_data = structurer.structure_transcript(
                    str(transcript_file), 
                    str(output_path),
                    add_to_vector=add_to_vector
                )
                
                # Print summary
                if structured_data:
                    print(f"Successfully processed {transcript_file.name} and extracted {len(structured_data)} questions")
                else:
                    print(f"Failed to extract questions from {transcript_file.name}")
                    
            except Exception as e:
                print(f"Error processing {transcript_file.name}: {str(e)}")

def main(transcript_path: str, output_path: Optional[str] = None, use_perplexity: bool = True, add_to_vector: bool = True):
    """
    Main function to structure a transcript
    
    Args:
        transcript_path (str): Path to transcript file or directory
        output_path (Optional[str]): Path to output file (only used if transcript_path is a file)
        use_perplexity (bool): Whether to use Perplexity API
        add_to_vector (bool): Whether to add questions to vector store
    """
    # Check if transcript_path is a directory
    if os.path.isdir(transcript_path):
        JLPTTranscriptStructurer.process_directory(transcript_path, use_perplexity, add_to_vector)
        return
    
    # Process single file
    print(f"Processing transcript: {transcript_path}")
    
    # Get API key if using Perplexity
    perplexity_api_key = None
    if use_perplexity or add_to_vector:
        perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        if perplexity_api_key:
            # Print first and last 5 characters of API key for verification
            masked_key = perplexity_api_key[:5] + "*" * (len(perplexity_api_key) - 10) + perplexity_api_key[-5:]
            print(f"Using Perplexity API with key: {masked_key}")
        else:
            print("Error: Perplexity API key not found in environment variables.")
            if add_to_vector:
                print("Disabling vector store integration due to missing API key.")
                add_to_vector = False
            if use_perplexity:
                print("Falling back to manual extraction due to missing API key.")
                use_perplexity = False
    
    # Create structurer
    structurer = JLPTTranscriptStructurer(perplexity_api_key=perplexity_api_key)
    
    # Structure transcript
    structured_data = structurer.structure_transcript(
        transcript_path, 
        output_path,
        add_to_vector=add_to_vector
    )
    
    # Print summary
    if structured_data:
        print(f"Successfully extracted {len(structured_data)} questions")
    else:
        print("Failed to extract questions from transcript")

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Structure JLPT transcript files")
    parser.add_argument("transcript_path", help="Path to transcript file or directory")
    parser.add_argument("--output", "-o", help="Output file path (only used if transcript_path is a file)")
    parser.add_argument("--manual", "-m", action="store_true", help="Use manual extraction instead of Perplexity API")
    parser.add_argument("--no-vector", action="store_true", help="Don't add questions to vector store")
    
    args = parser.parse_args()
    
    # Process transcript
    main(
        transcript_path=args.transcript_path,
        output_path=args.output,
        use_perplexity=not args.manual,
        add_to_vector=not args.no_vector
    )