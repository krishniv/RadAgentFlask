import logging
import os
import json
import re
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        # Hugging Face configuration
        self.hf_token = os.getenv("HF_TOKEN")
        self.model_id = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")
        
        # Casual phrases that should get brief responses
        self.casual_phrases = [
            "hey", "hi", "hello", "thanks", "thank you", "ok", "okay", 
            "bye", "goodbye", "see you", "later", "good morning", 
            "good afternoon", "good evening", "good night", "how are you"
        ]
        
        # Validate required settings
        if not self.hf_token:
            logger.warning("Missing HF_TOKEN. Chat service may not function properly.")
            
        logger.info(f"Initialized ChatService with Hugging Face model: {self.model_id}")

    def generate_response(self, user_question, history=None):
        """Generate a response to a medical query using Hugging Face models."""
        try:
            # Check if this is a casual message or substantive question
            is_casual = self._is_casual_message(user_question)
            
            # Format the prompt with medical context and user question
            prompt = self._create_medical_prompt(user_question, history, is_casual)
            
            # Call the Hugging Face model with appropriate params based on message type
            return self._call_huggingface_model(prompt, is_casual)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble responding right now. Please try again."
    
    def _is_casual_message(self, message):
        """Determine if a message is casual or a substantive question"""
        # Convert to lowercase and remove punctuation
        cleaned = re.sub(r'[^\w\s]', '', message.lower())
        words = cleaned.split()
        
        # Check if it's just a single word or short phrase
        if len(words) <= 3:
            # See if any of the words match our casual phrases list
            for phrase in self.casual_phrases:
                if phrase in cleaned or cleaned in phrase:
                    return True
        
        # Check if it ends with a question mark (likely a real question)
        if message.strip().endswith("?"):
            return False
            
        # If the message is very short (less than 10 chars), consider it casual
        if len(message.strip()) < 10:
            return True
            
        return False
    
    def _create_medical_prompt(self, user_question, history=None, is_casual=False):
        """Create a prompt based on whether it's a casual message or real question"""
        if is_casual:
            # Brief, friendly instructions for casual messages
            system_prompt = (
                "You are a friendly medical assistant. For brief greetings or simple acknowledgments, "
                "respond concisely in 1-2 sentences. Be warm but efficient."
            )
        else:
            # Detailed instructions for medical questions
            system_prompt = (
                "You are an expert medical assistant with extensive knowledge of medicine, diseases, "
                "treatments, and healthcare practices. Provide accurate, clear, and helpful information "
                "to medical questions. Include relevant details about symptoms, treatments, and preventative "
                "measures when appropriate. Always present information in a well-structured format that's "
                "easy to understand."
            )
        
        # Add conversation history if available
        full_prompt = system_prompt + "\n\n"
        if history:
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    full_prompt += f"User: {content}\n"
                elif role == "assistant":
                    full_prompt += f"Assistant: {content}\n"
        
        # Add the current question
        full_prompt += f"User: {user_question}\nAssistant: "
        
        return full_prompt

    def _call_huggingface_model(self, prompt, is_casual=False):
        """Call the Hugging Face model with the given prompt"""
        try:
            # Initialize the HF inference client
            llm_client = InferenceClient(
                model=self.model_id,
                token=self.hf_token,
                timeout=30,
            )
            
            # Format the prompt properly for instruction-tuned models
            chat_formatted_prompt = f"""<s>[INST] {prompt} [/INST]"""
            
            logger.info(f"Sending request to Hugging Face model: {self.model_id} (casual: {is_casual})")
            
            # Set parameters based on message type
            parameters = {
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True,
                "return_full_text": False
            }
            
            # Adjust token limit based on message type
            if is_casual:
                parameters["max_new_tokens"] = 100  # Brief response for casual messages
            else:
                parameters["max_new_tokens"] = 500  # Detailed response for medical questions
            
            # Call the model
            response = llm_client.post(
                json={
                    "inputs": chat_formatted_prompt,
                    "parameters": parameters,
                },
            )
            
            # Process the response
            if isinstance(response, bytes):
                response_text = json.loads(response.decode())[0]["generated_text"]
            else:
                response_text = response[0]["generated_text"]
                
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Error calling Hugging Face model: {e}")
            return f"I apologize, but I'm having trouble accessing my knowledge source at the moment. Please try again later." 