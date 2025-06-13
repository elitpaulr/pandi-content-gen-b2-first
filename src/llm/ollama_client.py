import ollama
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

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
            models = self.client.list()
            logger.info(f"Connected to Ollama. Available models: {[m['name'] for m in models['models']]}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
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
    
    def generate_reading_part5_task(self, topic: str, difficulty: str = "B2") -> Dict[str, Any]:
        """Generate a complete Reading Part 5 task using Ollama"""
        
        system_prompt = """You are an expert Cambridge B2 First exam content creator. 
        Generate authentic Reading Part 5 tasks that match the official exam format exactly.
        
        Reading Part 5 Requirements:
        - Text length: 550-750 words
        - 6 multiple choice questions (31-36)
        - Each question has 4 options (A, B, C, D)
        - Question types: inference, vocabulary in context, attitude/opinion, detail, reference, main idea
        - Text should be engaging and at B2 level
        - Questions must be specific and contextual, not generic
        
        Return ONLY valid JSON in this exact format:
        {
            "task_id": "reading_part5_task_XX",
            "title": "Task Title",
            "topic": "topic_category",
            "difficulty": "B2",
            "text": "The complete text here...",
            "questions": [
                {
                    "question_number": 31,
                    "question_text": "Specific question about the text",
                    "options": {
                        "A": "Option A text",
                        "B": "Option B text", 
                        "C": "Option C text",
                        "D": "Option D text"
                    },
                    "correct_answer": "A",
                    "question_type": "inference",
                    "explanation": "Why this answer is correct"
                }
            ]
        }"""
        
        user_prompt = f"""Create a Reading Part 5 task about: {topic}
        
        Make sure:
        1. The text is exactly 550-750 words
        2. The topic is engaging and suitable for B2 level students
        3. All 6 questions (31-36) are specific to the text content
        4. Questions test different skills: inference, vocabulary, attitude, details, references, main ideas
        5. Each question has exactly 4 realistic options
        6. Only one option is clearly correct
        7. Include explanations for correct answers
        
        Topic: {topic}
        Difficulty: {difficulty}"""
        
        try:
            response = self.generate_text(user_prompt, system_prompt)
            
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            task_data = json.loads(response)
            
            # Validate the structure
            required_fields = ['task_id', 'title', 'topic', 'text', 'questions']
            for field in required_fields:
                if field not in task_data:
                    raise ValueError(f"Missing required field: {field}")
            
            if len(task_data['questions']) != 6:
                raise ValueError(f"Expected 6 questions, got {len(task_data['questions'])}")
            
            logger.info(f"Successfully generated task: {task_data['title']}")
            return task_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response}")
            raise
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
        
        Return the improved task in the same JSON format."""
        
        user_prompt = f"""Improve this Reading Part 5 task by making the questions more specific and contextual:

        {json.dumps(task_data, indent=2)}
        
        Make sure each question:
        - References specific parts of the text
        - Has realistic distractors that could seem correct
        - Tests a different skill (inference, vocabulary, attitude, etc.)
        - Has only one clearly correct answer"""
        
        try:
            response = self.generate_text(user_prompt, system_prompt)
            
            # Clean up response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            improved_task = json.loads(response)
            logger.info(f"Successfully improved task: {improved_task.get('title', 'Unknown')}")
            return improved_task
            
        except Exception as e:
            logger.error(f"Failed to improve task: {e}")
            return task_data  # Return original if improvement fails

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