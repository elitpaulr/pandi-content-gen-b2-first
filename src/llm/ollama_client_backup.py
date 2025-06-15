import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import ollama
from src.llm.json_parser import RobustJSONParser

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OllamaConfig:
    """Configuration for Ollama client"""
    model: str = "llama3.1:8b"  # Default model
    host: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 120

class OllamaClient:
    """Client for interacting with local Ollama LLM"""
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.client = ollama.Client(host=self.config.host)
        
    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            models_response = self.client.list()
            
            # Extract model names from the response
            model_names = []
            if hasattr(models_response, 'models'):
                # If it's an object with models attribute
                for model in models_response.models:
                    if hasattr(model, 'model'):
                        model_names.append(model.model)
                    elif hasattr(model, 'name'):
                        model_names.append(model.name)
                    else:
                        model_names.append(str(model))
            elif isinstance(models_response, dict) and 'models' in models_response:
                # If it's a dictionary
                for model in models_response['models']:
                    if isinstance(model, dict):
                        name = model.get('name') or model.get('model', 'unknown')
                        model_names.append(name)
                    else:
                        model_names.append(str(model))
            
            logger.info(f"Connected to Ollama. Available models: {model_names}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            models_response = self.client.list()
            
            # Extract model names from the response
            model_names = []
            if hasattr(models_response, 'models'):
                # If it's an object with models attribute
                for model in models_response.models:
                    if hasattr(model, 'model'):
                        model_names.append(model.model)
                    elif hasattr(model, 'name'):
                        model_names.append(model.name)
                    else:
                        model_names.append(str(model))
            elif isinstance(models_response, dict) and 'models' in models_response:
                # If it's a dictionary
                for model in models_response['models']:
                    if isinstance(model, dict):
                        name = model.get('name') or model.get('model', 'unknown')
                        model_names.append(name)
                    else:
                        model_names.append(str(model))
            
            return model_names
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Ollama"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            response = self.client.chat(
                model=self.config.model,
                messages=messages,
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise
    
    def normalize_question_numbers(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize question numbers to start from 1"""
        if 'questions' in task_data and isinstance(task_data['questions'], list):
            for i, question in enumerate(task_data['questions']):
                if isinstance(question, dict) and 'question_number' in question:
                    question['question_number'] = i + 1
        return task_data
    
    def generate_reading_part5_task(self, topic: str, difficulty: str = "B2", text_type: str = "magazine_article", custom_instructions: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete Reading Part 5 task using Ollama with specified text type"""
        
        # Ensure parameters are not None to prevent f-string errors
        topic = topic or "general topic"
        difficulty = difficulty or "B2"
        text_type = text_type or "magazine_article"
        
        # Text type specific instructions
        text_type_instructions = {
            "magazine_article": "Write as an engaging magazine article with a clear structure, subheadings if appropriate, and an informative yet accessible tone. Include expert quotes or statistics where relevant.",
            "newspaper_article": "Write as a newspaper feature article with journalistic style, factual reporting, and balanced perspective. Include relevant context and background information.",
            "novel_extract": "Write as an excerpt from a contemporary novel with character development, dialogue, and narrative description. Focus on showing rather than telling.",
            "blog_post": "Write as a personal blog post with first-person perspective, conversational tone, and personal reflections or experiences.",
            "science_article": "Write as a popular science article that explains complex concepts in accessible language, with examples and analogies to help understanding.",
            "cultural_review": "Write as a cultural review or commentary with analytical perspective, critical evaluation, and informed opinion.",
            "professional_feature": "Write as a professional feature article about workplace trends, career advice, or industry insights with practical information.",
            "lifestyle_feature": "Write as a lifestyle feature about personal interests, home, family, or hobbies with practical tips and relatable content.",
            "travel_writing": "Write as travel writing with vivid descriptions of places, cultural observations, and personal travel experiences.",
            "educational_feature": "Write as an educational feature about learning, study techniques, or educational trends with informative and helpful content."
        }
        
        text_style_instruction = text_type_instructions.get(text_type, text_type_instructions["magazine_article"])
        
        system_prompt = f"""You are an expert Cambridge B2 First exam content creator. 

CRITICAL INSTRUCTIONS:
1. You MUST respond with ONLY valid JSON format
2. Do NOT include any explanations, markdown, or extra text
3. Do NOT use ```json code blocks
4. Start your response with {{ and end with }}
5. Follow the exact JSON structure provided

Generate authentic Reading Part 5 tasks that match the official exam format exactly.

Reading Part 5 Requirements:
- Text length: 550-750 words (engaging, authentic content)
- 6 multiple choice questions (numbered 1-6)
- Each question has 4 options (A, B, C, D)
- Question types: inference, vocabulary in context, attitude/opinion, detail, reference, main idea
- Text should be engaging and at B2 level
- Questions must be specific and contextual, not generic

TEXT TYPE INSTRUCTION: {text_style_instruction}

You can use natural formatting in your text including paragraphs and quotes, but keep it simple for JSON parsing.

RESPOND WITH ONLY THIS EXACT JSON FORMAT (no other text):"""
        
        user_prompt = f"""{{
    "task_id": "reading_part5_task_01",
    "title": "Create an engaging title about {topic}",
    "topic": "health_and_fitness",
    "text_type": "{text_type}",
    "difficulty": "B2",
    "text": "Write your {text_type} text here about {topic}. Make it 550-750 words, engaging and suitable for B2 level. Use simple formatting - avoid complex punctuation that might break JSON parsing. Focus on creating authentic, interesting content that follows the {text_type} style.",
    "questions": [
        {{
            "question_number": 1,
            "question_text": "Create a specific question about the text content",
            "options": {{
                "A": "First realistic option based on the text",
                "B": "Second realistic option", 
                "C": "Third realistic option",
                "D": "Fourth realistic option"
            }},
            "correct_answer": "A",
            "question_type": "inference"
        }},
        {{
            "question_number": 2,
            "question_text": "Create a vocabulary question about a word from the text",
            "options": {{
                "A": "Option A",
                "B": "Option B", 
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "B",
            "question_type": "vocabulary"
        }},
        {{
            "question_number": 3,
            "question_text": "Create a detail question about specific information",
            "options": {{
                "A": "Option A",
                "B": "Option B", 
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "C",
            "question_type": "detail"
        }},
        {{
            "question_number": 4,
            "question_text": "Create an attitude question about the author's opinion",
            "options": {{
                "A": "Option A",
                "B": "Option B", 
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "D",
            "question_type": "attitude"
        }},
        {{
            "question_number": 5,
            "question_text": "Create a reference question about what something refers to",
            "options": {{
                "A": "Option A",
                "B": "Option B", 
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "question_type": "reference"
        }},
        {{
            "question_number": 6,
            "question_text": "Create a main idea question about the overall message",
            "options": {{
                "A": "Option A",
                "B": "Option B", 
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "B",
            "question_type": "main_idea"
        }}
    ]
}}

Topic: {topic}
Text Type: {text_type}
Difficulty: {difficulty}"""
        
        if custom_instructions and custom_instructions.strip():
            user_prompt += f"\nAdditional Instructions: {custom_instructions}"
        
        user_prompt += f"\n\nRemember: Respond with ONLY the JSON format above, no explanations or extra text."
        
        try:
            response = self.generate_text(user_prompt, system_prompt)
            
            # Log the raw response for debugging
            logger.info(f"Raw LLM response length: {len(response)} characters")
            logger.debug(f"Raw response preview: {response[:200]}...")
            
            # Use the robust JSON parser to handle formatting characters
            task_data = RobustJSONParser.parse_llm_json(response)
            
            # Validate the structure
            required_fields = ['task_id', 'title', 'topic', 'text', 'questions']
            for field in required_fields:
                if field not in task_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure text_type is set
            task_data['text_type'] = text_type
            
            if 'questions' in task_data and len(task_data['questions']) != 6:
                logger.warning(f"Expected 6 questions, got {len(task_data['questions'])}")
                # Don't fail, just warn - some models might generate different amounts
            
            logger.info(f"Successfully generated task: {task_data.get('title', 'Unknown')}")
            return self.normalize_question_numbers(task_data)
            
        except Exception as e:
            logger.error(f"Failed to generate task: {e}")
            raise
    
    def generate_multiple_tasks(self, topics: List[str], count_per_topic: int = 2) -> List[Dict[str, Any]]:
        """Generate multiple Reading Part 5 tasks"""
        tasks = []
        task_counter = 1
        
        for topic in topics:
            for i in range(count_per_topic):
                try:
                    logger.info(f"Generating task {task_counter} for topic: {topic}")
                    task = self.generate_reading_part5_task(topic)
                    task['task_id'] = f"reading_part5_task_{task_counter:02d}"
                    tasks.append(task)
                    task_counter += 1
                except Exception as e:
                    logger.error(f"Failed to generate task for topic {topic}: {e}")
                    continue
        
        return tasks
    
    def improve_existing_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Improve an existing task by making questions more specific"""
        
        system_prompt = """You are an expert Cambridge B2 First exam content creator.
        Improve the given Reading Part 5 task by making the questions more specific and contextual.
        
        Focus on:
        1. Making questions refer to specific parts of the text
        2. Creating realistic, plausible distractors
        3. Ensuring questions test different skills
        4. Making sure only one answer is clearly correct
        
        You can use natural formatting in your improvements including quotes, line breaks, etc.
        The JSON parser will handle the formatting correctly.
        
        Return the improved task in the same JSON format."""
        
        user_prompt = f"""Please improve this Reading Part 5 task:

        Current task: {json.dumps(task_data, indent=2)}
        
        Make the questions more specific to the text content and ensure the distractors are realistic but clearly incorrect."""
        
        try:
            response = self.generate_text(user_prompt, system_prompt)
            
            # Use the robust JSON parser
            improved_task = RobustJSONParser.parse_llm_json(response)
            
            logger.info(f"Successfully improved task: {improved_task.get('title', 'Unknown')}")
            return self.normalize_question_numbers(improved_task)
            
        except Exception as e:
            logger.error(f"Failed to improve task: {e}")
            raise

# Example usage and testing
if __name__ == "__main__":
    # Test the Ollama client
    client = OllamaClient()
    
    if client.check_connection():
        print("✅ Ollama connection successful!")
        print(f"Available models: {client.list_models()}")
        
        # Test task generation
        try:
            task = client.generate_reading_part5_task("sustainable travel and eco-tourism")
            print(f"✅ Generated task: {task['title']}")
            print(f"Text length: {len(task['text'].split())} words")
            print(f"Number of questions: {len(task['questions'])}")
        except Exception as e:
            print(f"❌ Task generation failed: {e}")
    else:
        print("❌ Failed to connect to Ollama. Make sure it's running!")
        print("Start Ollama with: ollama serve") 