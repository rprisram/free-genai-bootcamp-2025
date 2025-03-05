#!/usr/bin/env python3

import os
import json
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

class QuestionGenerator:
    """Generate JLPT listening practice questions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the question generator
        
        Args:
            api_key (Optional[str], optional): Perplexity API key. Defaults to None.
        """
        load_dotenv()
        self.perplexity_api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.perplexity_api_key:
            raise ValueError("Perplexity API key is required. Please set PERPLEXITY_API_KEY in your .env file.")
    
    def generate_questions(self, context: str, count: int = 2, level: str = "N3", topic: str = "conversation") -> List[Dict[str, str]]:
        """Generate JLPT listening practice questions
        
        Args:
            context (str): Context for the questions
            count (int, optional): Number of questions to generate. Defaults to 2.
            level (str, optional): JLPT level. Defaults to "N3".
            topic (str, optional): Topic for the questions. Defaults to "conversation".
            
        Returns:
            List[Dict[str, str]]: List of generated questions
        """
        prompt = f"""
        Generate {count} JLPT {level} listening practice questions based on the following context:
        
        {context}
        
        The questions should be about {topic}.
        
        For each question, provide:
        1. A question number (e.g., "Section 1 Question 1")
        2. An introduction (e.g., "レストランで男の人と店の人が話しています")
        3. A conversation (the actual dialogue)
        4. A question (e.g., "男の人は何を注文しましたか？")
        
        Format your response as a JSON object with a 'questions' array. Each question should have 'number', 'introduction', 'conversation', and 'question' fields.
        """
        
        return self._generate_with_perplexity(prompt)
    
    def _generate_with_perplexity(self, prompt: str) -> List[Dict[str, str]]:
        """Generate questions using Perplexity API
        
        Args:
            prompt (str): Prompt for Perplexity API
            
        Returns:
            List[Dict[str, str]]: List of generated questions
        """
        try:
            # Add explicit instructions to format the response as JSON
            json_prompt = f"""{prompt}

IMPORTANT: Format your response as a valid JSON object with a 'questions' array. Each question should have 'number', 'introduction', 'conversation', and 'question' fields. Do not include any explanations or additional text outside the JSON object."""
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-reasoning-pro",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that generates JLPT listening practice questions in JSON format. Always respond with valid JSON only. Your response must be a JSON object with a 'questions' array containing question objects."},
                        {"role": "user", "content": json_prompt}
                    ],
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                print(f"Error from Perplexity API: {response.status_code} - {response.text}")
                return []
            
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Parse JSON from response
            try:
                # Try to extract JSON from code blocks first
                import re
                code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
                if code_block_match:
                    json_str = code_block_match.group(1).strip()
                    try:
                        data = json.loads(json_str)
                        if 'questions' in data:
                            return data['questions']
                        elif isinstance(data, list):
                            return data
                        else:
                            return [data]
                    except json.JSONDecodeError:
                        pass  # Continue to next method if this fails
                
                # Try to find JSON object in the response
                json_match = re.search(r'(\{[\s\S]*?\})', content)
                if json_match:
                    json_str = json_match.group(1)
                    try:
                        data = json.loads(json_str)
                        if 'questions' in data:
                            return data['questions']
                        elif isinstance(data, list):
                            return data
                        else:
                            return [data]
                    except json.JSONDecodeError:
                        pass  # Continue to next method if this fails
                
                # If no JSON found, create a manual question from the content
                print(f"No valid JSON found in response. Creating a manual question from content.")
                print(f"Response content: {content[:200]}...")
                
                # Create a structured question from the unstructured response
                manual_question = {
                    "number": "Generated Question 1",
                    "introduction": "Restaurant conversation",
                    "conversation": content[:200] if len(content) > 200 else content,
                    "question": "What was discussed in the conversation?"
                }
                return [manual_question]
                
            except Exception as e:
                print(f"Error processing Perplexity response: {str(e)}")
                print(f"Response content: {content[:200]}...")
                return []
            
        except Exception as e:
            print(f"Error calling Perplexity API: {str(e)}")
            return []


def main():
    """Main function to demonstrate question generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JLPT Question Generator")
    parser.add_argument("--context", required=True, help="Context for generating questions")
    parser.add_argument("--count", type=int, default=2, help="Number of questions to generate")
    parser.add_argument("--level", default="N3", help="JLPT level (N1, N2, N3, N4, N5)")
    parser.add_argument("--topic", default="conversation", help="Topic for the questions")
    parser.add_argument("--output", help="Output file to save generated questions")
    
    args = parser.parse_args()
    
    # Initialize question generator
    generator = QuestionGenerator()
    
    # Generate questions
    questions = generator.generate_questions(
        context=args.context,
        count=args.count,
        level=args.level,
        topic=args.topic
    )
    
    # Print or save questions
    if questions:
        print(f"Generated {len(questions)} questions:")
        
        if args.output:
            # Save to file
            with open(args.output, 'w', encoding='utf-8') as f:
                for q in questions:
                    f.write(f"Question: {q.get('number', 'Unknown')}\n")
                    f.write(f"Introduction: {q.get('introduction', '')}\n")
                    f.write(f"Conversation: {q.get('conversation', '')}\n")
                    f.write(f"Question: {q.get('question', '')}\n")
                    f.write("\n")
            print(f"Saved questions to {args.output}")
        else:
            # Print to console
            for i, q in enumerate(questions):
                print(f"\nQuestion {i+1}:")
                print(f"Number: {q.get('number', 'Unknown')}")
                print(f"Introduction: {q.get('introduction', '')}")
                print(f"Conversation: {q.get('conversation', '')}")
                print(f"Question: {q.get('question', '')}")
    else:
        print("Failed to generate questions")


if __name__ == "__main__":
    main()
