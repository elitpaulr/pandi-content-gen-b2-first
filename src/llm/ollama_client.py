import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import ollama

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
    """Client for interacting with local Ollama LLM using step-by-step generation"""
    
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
        """Generate a complete Reading Part 5 task using step-by-step LLM calls"""
        
        # Ensure parameters are not None
        topic = topic or "general topic"
        difficulty = difficulty or "B2"
        text_type = text_type or "magazine_article"
        
        try:
            logger.info(f"🚀 Generating task components step by step for topic: {topic}")
            
            # Step 1: Generate the title
            title = self._generate_title(topic, text_type)
            logger.info(f"✅ Generated title: {title}")
            
            # Step 2: Generate the main text
            text_content = self._generate_text_content(topic, text_type, custom_instructions)
            logger.info(f"✅ Generated text content: {len(text_content.split())} words")
            
            # Step 3: Generate questions based on the text
            questions = self._generate_questions(text_content, topic)
            logger.info(f"✅ Generated {len(questions)} questions")
            
            # Step 4: Assemble the complete task
            task_data = {
                "task_id": "reading_part5_task_01",  # Will be updated by the generator
                "title": title,
                "topic": self.categorize_topic(topic),
                "text_type": text_type,
                "difficulty": difficulty,
                "text": text_content,
                "questions": questions
            }
            
            logger.info(f"🎉 Successfully generated complete task: {title}")
            return self.normalize_question_numbers(task_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate task: {e}")
            raise
    
    def _generate_title(self, topic: str, text_type: str) -> str:
        """Generate an engaging title for the reading task"""
        
        system_prompt = f"""You are an expert content creator. Generate an engaging, clickable title for a {text_type} about {topic}.
        
        The title should be:
        - Engaging and attention-grabbing
        - Appropriate for B2 level English learners
        - Suitable for the {text_type} format
        - Between 5-12 words long
        - Natural and authentic
        
        Respond with ONLY the title, no quotes, no explanations, no extra text."""
        
        user_prompt = f"Create an engaging title for a {text_type} about: {topic}"
        
        title = self.generate_text(user_prompt, system_prompt).strip()
        # Clean up any quotes or extra formatting
        title = title.strip('"').strip("'").strip()
        
        return title
    
    def _generate_text_content(self, topic: str, text_type: str, custom_instructions: Optional[str] = None) -> str:
        """Generate the main reading text content"""
        
        # Text type specific instructions
        text_type_instructions = {
            "magazine_article": "Write as an engaging magazine article with a clear structure, subheadings if appropriate, and an informative yet accessible tone. Include expert quotes or statistics where relevant.",
            "newspaper_article": "Write as a newspaper feature article with journalistic style, factual reporting, and balanced perspective.",
            "novel_extract": "Write as an excerpt from a contemporary novel with character development, dialogue, and narrative description.",
            "blog_post": "Write as a personal blog post with first-person perspective, conversational tone, and personal reflections.",
            "science_article": "Write as a popular science article that explains complex concepts in accessible language.",
            "cultural_review": "Write as a cultural review or commentary with analytical perspective and informed opinion.",
            "professional_feature": "Write as a professional feature article about workplace trends or industry insights.",
            "lifestyle_feature": "Write as a lifestyle feature about personal interests, home, family, or hobbies with practical tips.",
            "travel_writing": "Write as travel writing with vivid descriptions of places and cultural observations.",
            "educational_feature": "Write as an educational feature about learning, study techniques, or educational trends."
        }
        
        style_instruction = text_type_instructions.get(text_type, text_type_instructions["magazine_article"])
        
        system_prompt = f"""You are an expert content writer. Write a {text_type} about {topic} that is exactly 550-750 words long.
        
        Style requirements: {style_instruction}
        
        Content requirements:
        - Write at B2 English level (intermediate)
        - Make it engaging and informative
        - Use clear paragraphs
        - Include specific details and examples
        - Write naturally - avoid overly complex sentences
        - Make sure it's exactly 550-750 words
        - Use simple formatting that won't break JSON parsing
        
        Respond with ONLY the text content, no titles, no explanations."""
        
        user_prompt = f"Write a {text_type} about: {topic}\n\nMake it engaging, informative, and exactly 550-750 words."
        
        if custom_instructions and custom_instructions.strip():
            user_prompt += f"\n\nAdditional requirements: {custom_instructions}"
        
        text_content = self.generate_text(user_prompt, system_prompt).strip()
        
        return text_content
    
    def _generate_questions(self, text_content: str, topic: str) -> List[Dict[str, Any]]:
        """Generate 6 multiple choice questions based on the text content"""
        
        questions = []
        question_types = ["inference", "vocabulary", "detail", "attitude", "reference", "main_idea"]
        
        for i, question_type in enumerate(question_types, 1):
            try:
                question = self._generate_single_question(text_content, i, question_type, topic)
                questions.append(question)
                logger.debug(f"✅ Generated question {i} ({question_type})")
            except Exception as e:
                logger.warning(f"⚠️ Failed to generate question {i} ({question_type}): {e}")
                # Continue with other questions
                continue
        
        return questions
    
    def _generate_single_question(self, text_content: str, question_number: int, question_type: str, topic: str) -> Dict[str, Any]:
        """Generate a single multiple choice question"""
        
        type_instructions = {
            "inference": "Create a question that requires the reader to infer or deduce information that is implied but not directly stated in the text.",
            "vocabulary": "Create a question about the meaning of a specific word or phrase from the text in context.",
            "detail": "Create a question about specific factual information that is directly stated in the text.",
            "attitude": "Create a question about the author's opinion, attitude, or tone towards the topic.",
            "reference": "Create a question about what a pronoun or phrase refers to in the text.",
            "main_idea": "Create a question about the overall main idea or purpose of the text."
        }
        
        system_prompt = f"""You are an expert Cambridge B2 First exam question writer. 

Create ONE multiple choice question based on the provided text.

Question type: {question_type}
Instructions: {type_instructions[question_type]}

Requirements:
- Question must be specific to the provided text
- Create exactly 4 options: A, B, C, D
- Only ONE option should be clearly correct
- Other options should be plausible but incorrect
- Use B2 level English
- Make the question clear and unambiguous

Format your response EXACTLY like this:
QUESTION: [Your question here]
A: [Option A]
B: [Option B] 
C: [Option C]
D: [Option D]
CORRECT: [A, B, C, or D]

Respond with ONLY this format, no explanations."""
        
        user_prompt = f"""Based on this text about {topic}, create a {question_type} question:

{text_content}

Create the question in the exact format specified."""
        
        response = self.generate_text(user_prompt, system_prompt).strip()
        
        # Parse the response
        question_data = self._parse_question_response(response, question_number, question_type)
        
        return question_data
    
    def _parse_question_response(self, response: str, question_number: int, question_type: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured question"""
        
        lines = response.strip().split('\n')
        
        question_text = ""
        options = {}
        correct_answer = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("QUESTION:"):
                question_text = line.replace("QUESTION:", "").strip()
            elif line.startswith("A:"):
                options["A"] = line.replace("A:", "").strip()
            elif line.startswith("B:"):
                options["B"] = line.replace("B:", "").strip()
            elif line.startswith("C:"):
                options["C"] = line.replace("C:", "").strip()
            elif line.startswith("D:"):
                options["D"] = line.replace("D:", "").strip()
            elif line.startswith("CORRECT:"):
                correct_answer = line.replace("CORRECT:", "").strip()
        
        # Validate we have all required components
        if not question_text:
            raise ValueError("No question text found")
        if len(options) != 4:
            raise ValueError(f"Expected 4 options, got {len(options)}: {list(options.keys())}")
        if correct_answer not in ["A", "B", "C", "D"]:
            raise ValueError(f"Invalid correct answer: {correct_answer}")
        
        return {
            "question_number": question_number,
            "question_text": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "question_type": question_type
        }
    
    def categorize_topic(self, topic: str) -> str:
        """Categorize the topic into a general category"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['health', 'fitness', 'diet', 'exercise', 'medical', 'nutrition']):
            return "health_and_fitness"
        elif any(word in topic_lower for word in ['technology', 'digital', 'computer', 'internet', 'ai', 'tech']):
            return "technology"
        elif any(word in topic_lower for word in ['travel', 'tourism', 'culture', 'country', 'city', 'place']):
            return "travel_and_culture"
        elif any(word in topic_lower for word in ['environment', 'climate', 'nature', 'green', 'sustainable']):
            return "environment"
        elif any(word in topic_lower for word in ['education', 'learning', 'school', 'university', 'study']):
            return "education"
        elif any(word in topic_lower for word in ['business', 'work', 'career', 'job', 'professional']):
            return "business_and_work"
        else:
            return "general"
    
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
        
        try:
            # For improvement, we'll use the step-by-step approach too
            # Generate improved questions one by one
            improved_questions = []
            for i, original_question in enumerate(task_data.get('questions', []), 1):
                try:
                    improved_question = self._improve_single_question(
                        task_data['text'], 
                        original_question, 
                        i, 
                        original_question.get('question_type', 'detail')
                    )
                    improved_questions.append(improved_question)
                except Exception as e:
                    logger.warning(f"Failed to improve question {i}, keeping original: {e}")
                    improved_questions.append(original_question)
            
            # Create improved task
            improved_task = task_data.copy()
            improved_task['questions'] = improved_questions
            
            logger.info(f"Successfully improved task: {improved_task.get('title', 'Unknown')}")
            return self.normalize_question_numbers(improved_task)
            
        except Exception as e:
            logger.error(f"Failed to improve task: {e}")
            raise
    
    def _improve_single_question(self, text_content: str, original_question: Dict[str, Any], question_number: int, question_type: str) -> Dict[str, Any]:
        """Improve a single question"""
        
        system_prompt = f"""You are an expert Cambridge B2 First exam question writer. 

Improve the given multiple choice question to make it more specific and contextual to the text.

Requirements:
- Make the question more specific to the provided text
- Create exactly 4 options: A, B, C, D
- Only ONE option should be clearly correct
- Other options should be plausible but incorrect
- Use B2 level English
- Make the question clear and unambiguous

Format your response EXACTLY like this:
QUESTION: [Your improved question here]
A: [Option A]
B: [Option B] 
C: [Option C]
D: [Option D]
CORRECT: [A, B, C, or D]

Respond with ONLY this format, no explanations."""
        
        user_prompt = f"""Based on this text, improve this {question_type} question:

TEXT:
{text_content}

ORIGINAL QUESTION:
{original_question.get('question_text', '')}
A: {original_question.get('options', {}).get('A', '')}
B: {original_question.get('options', {}).get('B', '')}
C: {original_question.get('options', {}).get('C', '')}
D: {original_question.get('options', {}).get('D', '')}
Correct: {original_question.get('correct_answer', '')}

Improve this question to be more specific to the text content."""
        
        response = self.generate_text(user_prompt, system_prompt).strip()
        
        # Parse the response
        question_data = self._parse_question_response(response, question_number, question_type)
        
        return question_data

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