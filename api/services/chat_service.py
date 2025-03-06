import requests
import logging
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        # API endpoint - get the correct URL from env or use default with v1/completions
        self.api_url = os.getenv("FRIENDLI_API_URL", "https://api.friendli.ai/dedicated/v1/completions")
        
        # Get token from environment variable
        self.auth_token = os.getenv("FRIENDLI_TOKEN")
        
        # Model ID
        self.model_id = os.getenv("ENDPOINT_ID")
        
        # Validate required settings
        if not self.auth_token or not self.model_id:
            logger.warning("Missing FRIENDLI_TOKEN or ENDPOINT_ID. Chat service may not function properly.")
            
        logger.info(f"Initialized ChatService with endpoint URL: {self.api_url}")

    def generate_response(self, user_question, history=None):
        """Generate a response to a medical query."""
        try:
            # Format the prompt with medical context and user question
            prompt = self._create_medical_prompt(user_question, history)
            
            # Call the API
            return self._call_friendli_api(prompt)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble responding right now. Please try again."
    
    def _create_medical_prompt(self, user_question, history=None):
        """Create a medical-focused prompt"""
        # Enhanced medical assistant prompt
        medical_prompt = (
            "You are an expert medical assistant with extensive knowledge of medicine, diseases, "
            "treatments, and healthcare practices. Provide accurate, clear, and helpful information "
            "to medical questions. Include relevant details about symptoms, treatments, and preventative "
            "measures when appropriate.\n\n"
        )
        
        # Add conversation history if available
        if history:
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    medical_prompt += f"User: {content}\n"
                elif role == "assistant":
                    medical_prompt += f"Assistant: {content}\n"
        
        # Add the current question
        medical_prompt += f"User: {user_question}\nAssistant: "
        
        return medical_prompt

    def _call_friendli_api(self, prompt):
        """Call the Friendli API with the given prompt"""
        # Prepare the request payload
        payload = {
            "model": self.model_id,
            "max_tokens": 500,
            "top_k": 1,
            "prompt": prompt
        }
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        logger.info(f"Sending request to API: {self.api_url}")
        
        try:
            # Make the API call
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Process the response
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"API response keys: {list(result.keys())}")
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['text']
                    elif 'response' in result:
                        return result['response']
                    else:
                        logger.warning(f"Unexpected response structure: {result}")
                        return "I received a response I couldn't understand."
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON: {response.text[:100]}...")
                    return "I received an invalid response from my knowledge source."
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return f"I'm unable to access my knowledge source. (Error: {response.status_code})"
        
        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return "The request to my knowledge source timed out. Please try again later."
        
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return "I couldn't connect to my knowledge source. Please check your internet connection."
        
        except Exception as e:
            logger.error(f"Unexpected error during API call: {str(e)}")
            return "An unexpected error occurred while processing your request." 