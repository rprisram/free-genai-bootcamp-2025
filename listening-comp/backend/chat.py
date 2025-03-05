# Create BedrockChat
# bedrock_chat.py
import boto3
import streamlit as st
from typing import Optional, Dict, Any


# Model ID
MODEL_ID = "amazon.nova-micro-v1:0"



class BedrockChat:
    def __init__(self, model_id: str = MODEL_ID):
        """Initialize Bedrock chat client"""
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
            self.model_id = model_id
            self.initialized = True
        except Exception as e:
            st.error(f"Failed to initialize Bedrock client: {str(e)}")
            self.initialized = False

    def generate_response(self, message: str, inference_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate a response using Amazon Bedrock"""
        if not self.initialized:
            return "Sorry, I couldn't connect to Amazon Bedrock. Please check your AWS credentials and configuration."
            
        if inference_config is None:
            inference_config = {"temperature": 0.7}

        messages = [{
            "role": "user",
            "content": [{"text": message}]
        }]

        try:
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig=inference_config
            )
            if 'output' in response and 'message' in response['output'] and 'content' in response['output']['message']:
                return response['output']['message']['content'][0]['text']
            else:
                st.warning("Received unexpected response format from Bedrock")
                return "I received an unexpected response format. Please try again."
            
        except Exception as e:
            error_message = str(e)
            st.error(f"Error generating response: {error_message}")
            
            if "AccessDeniedException" in error_message:
                return "Access denied. Please check your AWS credentials and permissions for Amazon Bedrock."
            elif "ResourceNotFoundException" in error_message:
                return f"Model '{self.model_id}' not found. Please check if the model ID is correct and available in your region."
            elif "ValidationException" in error_message:
                return "Invalid request. Please check your input and try again."
            elif "ThrottlingException" in error_message:
                return "Service is currently throttled. Please try again later."
            else:
                return f"Sorry, I encountered an error: {error_message}"


if __name__ == "__main__":
    chat = BedrockChat()
    while True:
        user_input = input("You: ")
        if user_input.lower() == '/exit':
            break
        response = chat.generate_response(user_input)
        print("Bot:", response)
