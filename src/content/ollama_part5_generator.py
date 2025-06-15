#!/usr/bin/env python3
"""
Ollama-powered Reading Part 5 Task Generator
Generates authentic Cambridge B2 First Reading Part 5 tasks using local Ollama LLM
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from llm.ollama_client import OllamaClient, OllamaConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaTaskGenerator:
    """Generate Reading Part 5 tasks using Ollama LLM"""
    
    def __init__(self, model: str = "llama3.1:8b"):
        """Initialize with specified Ollama model"""
        config = OllamaConfig(model=model)
        self.client = OllamaClient(config)
        self.output_dir = Path(__file__).parent.parent.parent / "generated_tasks"
        self.output_dir.mkdir(exist_ok=True)
        
        # Load knowledge base for context
        self.knowledge_base_dir = Path(__file__).parent.parent.parent / "knowledge_base"
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load existing knowledge base for context"""
        try:
            # Load generation guidelines
            guidelines_path = self.knowledge_base_dir / "b2_first_reading_part5_generation_guidelines.json"
            if guidelines_path.exists():
                with open(guidelines_path, 'r', encoding='utf-8') as f:
                    self.guidelines = json.load(f)
                logger.info("Loaded generation guidelines")
            else:
                self.guidelines = {}
                logger.warning("Generation guidelines not found")
            
            # Load examples for reference
            examples_path = self.knowledge_base_dir / "reading_part5_examples.json"
            if examples_path.exists():
                with open(examples_path, 'r', encoding='utf-8') as f:
                    self.examples = json.load(f)
                logger.info("Loaded example tasks")
            else:
                self.examples = {}
                logger.warning("Example tasks not found")
                
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            self.guidelines = {}
            self.examples = {}
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and ready"""
        if not self.client.check_connection():
            logger.error("❌ Ollama is not running or not accessible")
            logger.info("To start Ollama:")
            logger.info("1. Install Ollama: https://ollama.ai/")
            logger.info("2. Run: ollama serve")
            logger.info("3. Pull a model: ollama pull llama3.1:8b")
            return False
        return True
    
    def get_next_task_number(self) -> int:
        """Get the next available task number to avoid overwriting existing files"""
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
            return 1
        
        existing_files = list(self.output_dir.glob("reading_part5_task_*.json"))
        if not existing_files:
            return 1
        
        # Extract numbers from existing files
        existing_numbers = []
        for file in existing_files:
            try:
                # Extract number from filename like "reading_part5_task_05.json"
                filename_parts = file.stem.split('_')
                if len(filename_parts) >= 4 and filename_parts[-2] == 'task':
                    # Handle format: reading_part5_task_05
                    number_part = filename_parts[-1]
                    existing_numbers.append(int(number_part))
                elif len(filename_parts) >= 3:
                    # Handle other formats, get last part
                    number_part = filename_parts[-1]
                    if number_part.isdigit():
                        existing_numbers.append(int(number_part))
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse task number from file {file.name}: {e}")
                continue
        
        if existing_numbers:
            next_number = max(existing_numbers) + 1
            logger.info(f"📋 Next available task number: {next_number} (found {len(existing_numbers)} existing tasks)")
            return next_number
        else:
            logger.info("📋 No existing tasks found, starting with task number 1")
            return 1

    def generate_single_task(self, topic: str, task_number: int = None, text_type: str = "magazine_article", custom_instructions: Optional[str] = None) -> Dict[str, Any]:
        """Generate a single Reading Part 5 task with specified text type"""
        
        # Auto-assign task number if not provided - do this FIRST to avoid None issues
        if task_number is None:
            task_number = self.get_next_task_number()
        
        logger.info(f"Generating task {task_number} for topic: {topic} (text type: {text_type})")
        
        try:
            logger.info(f"Attempting generation for task {task_number}")
            
            # Generate the task using Ollama with text type
            task_data = self.client.generate_reading_part5_task(
                topic, 
                text_type=text_type,
                custom_instructions=custom_instructions
            )
            
            # Update task ID to match our numbering
            task_data['task_id'] = f"reading_part5_task_{task_number:02d}"
            
            # Add comprehensive metadata including generation parameters
            task_data['generated_by'] = "ollama"
            task_data['model'] = self.client.config.model
            task_data['generation_params'] = {
                'temperature': self.client.config.temperature,
                'max_tokens': self.client.config.max_tokens,
                'model_full_name': self.client.config.model
            }
            task_data['topic_category'] = self.categorize_topic(topic)
            task_data['text_type'] = text_type
            
            # Validate task quality
            if self.validate_task(task_data):
                logger.info(f"✅ Task validation passed")
                logger.info(f"✅ Successfully generated task {task_number}")
                return task_data
            else:
                # Save validation failure details
                validation_error = f"Task validation failed for task {task_number}"
                self.save_failure_log(task_number, topic, text_type, custom_instructions, validation_error, "validation_failure")
                logger.error(f"Task {task_number} failed validation, details saved to failure log")
                raise RuntimeError(f"Generated task failed validation requirements")
            
        except Exception as e:
            # Save detailed failure information
            self.save_failure_log(task_number, topic, text_type, custom_instructions, str(e), type(e).__name__)
            logger.error(f"Generation failed for task {task_number}: {e}")
            logger.error(f"Failure details saved to log file")
            raise RuntimeError(f"Failed to generate task: {str(e)}")
    
    def categorize_topic(self, topic: str) -> str:
        """Categorize topic for organization"""
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['travel', 'journey', 'adventure', 'explore', 'tourism']):
            return 'travel_adventure'
        elif any(word in topic_lower for word in ['technology', 'digital', 'internet', 'ai', 'computer', 'tech']):
            return 'technology_modern'
        elif any(word in topic_lower for word in ['personal', 'growth', 'development', 'learning', 'skill', 'career']):
            return 'personal_growth'
        elif any(word in topic_lower for word in ['environment', 'climate', 'nature', 'sustainability', 'green']):
            return 'environment_sustainability'
        elif any(word in topic_lower for word in ['health', 'fitness', 'wellness', 'medical', 'exercise']):
            return 'health_wellness'
        elif any(word in topic_lower for word in ['culture', 'art', 'music', 'literature', 'creative']):
            return 'culture_arts'
        else:
            return 'general'
    
    def validate_task(self, task_data: Dict[str, Any]) -> bool:
        """Validate generated task meets B2 First Reading Part 5 requirements"""
        errors = []
        
        # Check required fields
        required_fields = ['task_id', 'title', 'text', 'questions']
        for field in required_fields:
            if field not in task_data:
                errors.append(f"Missing field: {field}")
        
        # Check text length - B2 First Reading Part 5 should be 550-750 words
        # Allow some flexibility: 400-800 words
        if 'text' in task_data:
            word_count = len(task_data['text'].split())
            if word_count < 400 or word_count > 800:
                errors.append(f"Text length {word_count} words (should be 400-800 for B2 First)")
        
        # Check questions - should have 6 questions numbered 1-6
        # Allow 5-6 questions for flexibility
        if 'questions' in task_data:
            question_count = len(task_data['questions'])
            if question_count < 5 or question_count > 6:
                errors.append(f"Expected 5-6 questions, got {question_count}")
            
            for i, question in enumerate(task_data['questions']):
                expected_q_num = i + 1  # Questions should be numbered 1-6
                
                if 'question_number' not in question:
                    errors.append(f"Question {i+1} missing question_number")
                elif question['question_number'] != expected_q_num:
                    # This is a warning, not an error - we can fix numbering
                    logger.warning(f"Question {i+1} numbered {question['question_number']}, expected {expected_q_num}")
                
                if 'options' not in question:
                    errors.append(f"Question {i+1} missing options")
                elif not isinstance(question['options'], dict):
                    errors.append(f"Question {i+1} options should be a dictionary")
                elif len(question['options']) != 4:
                    # Check if it has A, B, C, D keys or if it's a different format
                    option_keys = list(question['options'].keys())
                    if not all(key in ['A', 'B', 'C', 'D'] for key in option_keys):
                        errors.append(f"Question {i+1} should have options A, B, C, D")
                    elif len(option_keys) != 4:
                        errors.append(f"Question {i+1} should have exactly 4 options, got {len(option_keys)}")
                
                if 'correct_answer' not in question:
                    errors.append(f"Question {i+1} missing correct answer")
                elif question['correct_answer'] not in ['A', 'B', 'C', 'D']:
                    errors.append(f"Question {i+1} correct answer should be A, B, C, or D")
        
        if errors:
            logger.warning(f"Task validation issues: {'; '.join(errors)}")
            return False
        
        logger.info("✅ Task validation passed")
        return True
    
    def save_task(self, task_data: Dict[str, Any]) -> Path:
        """Save generated task to JSON file"""
        filename = f"{task_data['task_id']}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved task to: {filepath}")
        return filepath
    
    def generate_batch_tasks(self, topics: List[str], text_types: List[str] = None, tasks_per_topic: int = 1) -> List[Dict[str, Any]]:
        """Generate multiple tasks for given topics and text types"""
        if not self.check_ollama_status():
            raise RuntimeError("Ollama is not available")
        
        if text_types is None:
            text_types = ["magazine_article"]
        
        all_tasks = []
        task_counter = 1  # For display purposes only
        
        # Pre-calculate all task numbers to avoid conflicts
        total_tasks_needed = len(topics) * len(text_types) * tasks_per_topic
        starting_task_number = self.get_next_task_number()
        task_numbers = list(range(starting_task_number, starting_task_number + total_tasks_needed))
        task_number_index = 0
        
        logger.info(f"🚀 Starting batch generation: {len(topics)} topics, {len(text_types)} text types, {tasks_per_topic} tasks each")
        logger.info(f"📋 Pre-assigned task numbers: {starting_task_number} to {starting_task_number + total_tasks_needed - 1}")
        
        for topic in topics:
            for text_type in text_types:
                for i in range(tasks_per_topic):
                    # Use pre-assigned task number
                    assigned_task_number = task_numbers[task_number_index]
                    task_number_index += 1
                    
                    logger.info(f"📝 Working on task {task_counter}: {text_type} about '{topic}' (task #{assigned_task_number:02d})")
                    
                    try:
                        task = self.generate_single_task(topic, assigned_task_number, text_type)
                        filepath = self.save_task(task)
                        all_tasks.append(task)
                        
                        logger.info(f"✅ Task {task_counter} completed: {task['title']} (saved as {task['task_id']})")
                        task_counter += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to generate task {task_counter} for '{topic}' ({text_type}): {e}")
                        task_counter += 1  # Still increment for display purposes
                        continue
        
        logger.info(f"🎉 Batch generation complete! Generated {len(all_tasks)} tasks")
        return all_tasks
    
    def improve_existing_tasks(self, task_files: List[str]) -> List[Dict[str, Any]]:
        """Improve existing tasks using Ollama"""
        if not self.check_ollama_status():
            raise RuntimeError("Ollama is not available")
        
        improved_tasks = []
        
        for task_file in task_files:
            try:
                # Load existing task
                with open(task_file, 'r', encoding='utf-8') as f:
                    original_task = json.load(f)
                
                logger.info(f"🔧 Improving task: {original_task.get('title', 'Unknown')}")
                
                # Improve using Ollama
                improved_task = self.client.improve_existing_task(original_task)
                
                # Save improved version
                improved_task['improved_by'] = 'ollama'
                improved_task['original_generator'] = original_task.get('generated_by', 'unknown')
                
                filepath = self.save_task(improved_task)
                improved_tasks.append(improved_task)
                
                logger.info(f"✅ Improved and saved: {filepath}")
                
            except Exception as e:
                logger.error(f"❌ Failed to improve {task_file}: {e}")
                continue
        
        return improved_tasks
    
    def save_failure_log(self, task_number: int, topic: str, text_type: str, custom_instructions: Optional[str], error_message: str, error_type: str):
        """Save detailed failure information for analysis"""
        import datetime
        
        # Create failure logs directory if it doesn't exist
        failure_logs_dir = Path(__file__).parent.parent.parent / "failure_logs"
        failure_logs_dir.mkdir(exist_ok=True)
        
        # Generate timestamp and filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"task_{task_number:02d}_failure_{timestamp}.txt"
        filepath = failure_logs_dir / filename
        
        # Collect system information
        failure_details = f"""TASK GENERATION FAILURE LOG
========================================

Timestamp: {datetime.datetime.now().isoformat()}
Task Number: {task_number:02d}
Error Type: {error_type}

GENERATION PARAMETERS:
---------------------
Topic: {topic}
Text Type: {text_type}
Custom Instructions: {custom_instructions or 'None'}

MODEL CONFIGURATION:
-------------------
Model: {self.client.config.model}
Temperature: {self.client.config.temperature}
Max Tokens: {self.client.config.max_tokens}

ERROR DETAILS:
-------------
{error_message}

SYSTEM INFO:
-----------
Ollama Status: {'Connected' if self.check_ollama_status() else 'Disconnected'}
Available Models: {getattr(self.client, '_available_models', 'Unknown')}

NEXT STEPS FOR ANALYSIS:
-----------------------
1. Check if this is a recurring pattern with similar topics/text types
2. Verify Ollama connection stability
3. Consider adjusting model parameters if validation failures
4. Review topic complexity and custom instructions

Generated by: OllamaTaskGenerator v1.0
"""
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(failure_details)
        
        logger.info(f"💾 Failure log saved to: {filepath}")
        return filepath


def main():
    """Main function for command-line usage"""
    generator = OllamaTaskGenerator()
    
    # Check if Ollama is available
    if not generator.check_ollama_status():
        return
    
    # Define topics for generation
    topics = [
        "sustainable travel and eco-tourism",
        "digital nomad lifestyle and remote work",
        "urban gardening and community spaces",
        "artificial intelligence in everyday life",
        "traditional crafts in the modern world",
        "mindfulness and mental health awareness",
        "renewable energy solutions for homes",
        "cultural exchange through food",
        "adventure sports and personal challenges",
        "social media influence on relationships"
    ]
    
    try:
        # Generate new tasks
        logger.info("🎯 Starting Ollama-powered task generation")
        tasks = generator.generate_batch_tasks(topics, tasks_per_topic=1)
        
        # Summary
        logger.info(f"📊 Generation Summary:")
        logger.info(f"   • Total tasks generated: {len(tasks)}")
        logger.info(f"   • Topics covered: {len(topics)}")
        logger.info(f"   • Output directory: {generator.output_dir}")
        
        # Show task categories
        categories = {}
        for task in tasks:
            cat = task.get('topic_category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        logger.info("   • Task categories:")
        for cat, count in categories.items():
            logger.info(f"     - {cat}: {count} tasks")
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 