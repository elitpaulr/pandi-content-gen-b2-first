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
    
    def generate_single_task(self, topic: str, task_number: int, text_type: str = "magazine_article", custom_instructions: Optional[str] = None) -> Dict[str, Any]:
        """Generate a single Reading Part 5 task with specified text type"""
        logger.info(f"Generating task {task_number} for topic: {topic} (text type: {text_type})")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries} for task {task_number}")
                
                # Generate the task using Ollama with text type
                task_data = self.client.generate_reading_part5_task(
                    topic, 
                    text_type=text_type,
                    custom_instructions=custom_instructions
                )
                
                # Update task ID to match our numbering
                task_data['task_id'] = f"reading_part5_task_{task_number:02d}"
                
                # Add metadata
                task_data['generated_by'] = "ollama"
                task_data['model'] = self.client.config.model
                task_data['topic_category'] = self.categorize_topic(topic)
                task_data['text_type'] = text_type
                
                # Validate task quality
                if self.validate_task(task_data):
                    logger.info(f"✅ Successfully generated task {task_number} on attempt {attempt + 1}")
                    return task_data
                else:
                    logger.warning(f"Task {task_number} failed validation on attempt {attempt + 1}")
                    if attempt == max_retries - 1:
                        # On last attempt, return even if validation fails
                        logger.warning(f"Returning task {task_number} despite validation issues")
                        return task_data
                    continue
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for task {task_number}: {e}")
                if attempt == max_retries - 1:
                    # On final attempt, create a fallback task
                    logger.error(f"All attempts failed for task {task_number}, creating fallback")
                    return self.create_fallback_task(topic, task_number, text_type)
                continue
        
        # This should never be reached, but just in case
        return self.create_fallback_task(topic, task_number, text_type)
    
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
        
        # Check questions - B2 First Reading Part 5 has 6 questions (31-36)
        # Allow 5-6 questions for flexibility
        if 'questions' in task_data:
            question_count = len(task_data['questions'])
            if question_count < 5 or question_count > 6:
                errors.append(f"Expected 5-6 questions for B2 First, got {question_count}")
            
            for i, question in enumerate(task_data['questions']):
                expected_q_num = i + 31  # Questions should be numbered 31-36
                
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
        task_counter = 1
        
        logger.info(f"🚀 Starting batch generation: {len(topics)} topics, {len(text_types)} text types, {tasks_per_topic} tasks each")
        
        for topic in topics:
            for text_type in text_types:
                for i in range(tasks_per_topic):
                    logger.info(f"📝 Working on task {task_counter}: {text_type} about '{topic}'")
                    
                    try:
                        task = self.generate_single_task(topic, task_counter, text_type)
                        filepath = self.save_task(task)
                        all_tasks.append(task)
                        
                        logger.info(f"✅ Task {task_counter} completed: {task['title']}")
                        task_counter += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to generate task {task_counter} for '{topic}' ({text_type}): {e}")
                        task_counter += 1  # Still increment to maintain numbering
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
    
    def create_fallback_task(self, topic: str, task_number: int, text_type: str) -> Dict[str, Any]:
        """Create a fallback task when AI generation fails"""
        logger.info(f"Creating fallback task for topic: {topic} (text type: {text_type})")
        
        fallback_task = {
            "task_id": f"reading_part5_task_{task_number:02d}",
            "title": f"Reading Task: {topic.title()}",
            "topic": topic,
            "topic_category": self.categorize_topic(topic),
            "difficulty": "B2",
            "generated_by": "fallback",
            "model": "fallback",
            "text": f"""This is a fallback task generated when AI generation failed for the topic '{topic}'. 
            
In today's rapidly changing world, the topic of {topic} has become increasingly important for people of all ages. Many experts believe that understanding this subject is crucial for personal and professional development.

The concept of {topic} involves various aspects that affect our daily lives. From technological advances to social changes, the impact can be seen everywhere. People are constantly adapting to new situations and finding innovative ways to approach challenges.

Research has shown that those who engage with {topic} tend to develop better problem-solving skills and a more comprehensive understanding of the world around them. This knowledge can be applied in numerous situations, making it a valuable asset in both personal and professional contexts.

Furthermore, the study of {topic} often reveals interesting connections between different fields of knowledge. These interdisciplinary links help create a more holistic view of complex issues and can lead to breakthrough discoveries.

As we move forward, it's clear that {topic} will continue to play a significant role in shaping our future. The ability to understand and work with these concepts will become increasingly important for success in the modern world.

Educational institutions are recognizing this trend and incorporating more {topic}-related content into their curricula. This ensures that students are well-prepared for the challenges they will face in their careers and personal lives.""",
            "questions": [
                {
                    "question_number": 31,
                    "question_text": f"What does the text suggest about the importance of {topic}?",
                    "options": {
                        "A": "It is only relevant for certain professions",
                        "B": "It is crucial for personal and professional development", 
                        "C": "It is a temporary trend that will fade",
                        "D": "It is too complex for most people to understand"
                    },
                    "correct_answer": "B",
                    "question_type": "detail",
                    "explanation": "The text explicitly states that understanding this subject is crucial for personal and professional development."
                },
                {
                    "question_number": 32,
                    "question_text": "According to the text, people who engage with this topic tend to:",
                    "options": {
                        "A": "become confused by complex information",
                        "B": "avoid challenging situations",
                        "C": "develop better problem-solving skills",
                        "D": "focus only on theoretical knowledge"
                    },
                    "correct_answer": "C",
                    "question_type": "detail",
                    "explanation": "The text states that research shows these people develop better problem-solving skills."
                },
                {
                    "question_number": 33,
                    "question_text": "The word 'holistic' in paragraph 4 most likely means:",
                    "options": {
                        "A": "partial and incomplete",
                        "B": "comprehensive and complete",
                        "C": "simple and basic",
                        "D": "theoretical and abstract"
                    },
                    "correct_answer": "B",
                    "question_type": "vocabulary",
                    "explanation": "Holistic refers to a comprehensive, complete view that considers all aspects."
                },
                {
                    "question_number": 34,
                    "question_text": "What does the text imply about the future relevance of this topic?",
                    "options": {
                        "A": "It will become less important over time",
                        "B": "It will only matter in academic settings",
                        "C": "It will continue to be significant",
                        "D": "It will be replaced by newer concepts"
                    },
                    "correct_answer": "C",
                    "question_type": "inference",
                    "explanation": "The text states it will continue to play a significant role in shaping our future."
                },
                {
                    "question_number": 35,
                    "question_text": "The text mentions that educational institutions are:",
                    "options": {
                        "A": "ignoring current trends",
                        "B": "reducing related content",
                        "C": "incorporating more related content",
                        "D": "focusing only on traditional subjects"
                    },
                    "correct_answer": "C",
                    "question_type": "detail",
                    "explanation": "The text explicitly states that institutions are incorporating more related content into curricula."
                },
                {
                    "question_number": 36,
                    "question_text": "The overall tone of the text can be described as:",
                    "options": {
                        "A": "pessimistic and worried",
                        "B": "neutral and informative",
                        "C": "critical and disapproving",
                        "D": "enthusiastic and promotional"
                    },
                    "correct_answer": "B",
                    "question_type": "tone",
                    "explanation": "The text presents information in a balanced, informative way without strong emotional language."
                }
            ],
            "text_type": text_type
        }
        
        return fallback_task

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