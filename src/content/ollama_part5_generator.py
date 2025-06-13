#!/usr/bin/env python3
"""
Ollama-powered Reading Part 5 Task Generator
Generates authentic Cambridge B2 First Reading Part 5 tasks using local Ollama LLM
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
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
    
    def generate_single_task(self, topic: str, task_number: int) -> Dict[str, Any]:
        """Generate a single Reading Part 5 task"""
        logger.info(f"Generating task {task_number} for topic: {topic}")
        
        try:
            # Generate the task using Ollama
            task_data = self.client.generate_reading_part5_task(topic)
            
            # Update task ID to match our numbering
            task_data['task_id'] = f"reading_part5_task_{task_number:02d}"
            
            # Add metadata
            task_data['generated_by'] = "ollama"
            task_data['model'] = self.client.config.model
            task_data['topic_category'] = self.categorize_topic(topic)
            
            # Validate task quality
            self.validate_task(task_data)
            
            return task_data
            
        except Exception as e:
            logger.error(f"Failed to generate task {task_number}: {e}")
            raise
    
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
        """Validate generated task meets requirements"""
        errors = []
        
        # Check required fields
        required_fields = ['task_id', 'title', 'text', 'questions']
        for field in required_fields:
            if field not in task_data:
                errors.append(f"Missing field: {field}")
        
        # Check text length
        if 'text' in task_data:
            word_count = len(task_data['text'].split())
            if word_count < 550 or word_count > 750:
                errors.append(f"Text length {word_count} words (should be 550-750)")
        
        # Check questions
        if 'questions' in task_data:
            if len(task_data['questions']) != 6:
                errors.append(f"Expected 6 questions, got {len(task_data['questions'])}")
            
            for i, question in enumerate(task_data['questions']):
                q_num = i + 31  # Questions should be numbered 31-36
                
                if 'question_number' not in question or question['question_number'] != q_num:
                    errors.append(f"Question {i+1} should be numbered {q_num}")
                
                if 'options' not in question or len(question['options']) != 4:
                    errors.append(f"Question {i+1} should have exactly 4 options")
                
                if 'correct_answer' not in question:
                    errors.append(f"Question {i+1} missing correct answer")
        
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
    
    def generate_batch_tasks(self, topics: List[str], tasks_per_topic: int = 2) -> List[Dict[str, Any]]:
        """Generate multiple tasks for given topics"""
        if not self.check_ollama_status():
            raise RuntimeError("Ollama is not available")
        
        all_tasks = []
        task_counter = 1
        
        logger.info(f"🚀 Starting batch generation: {len(topics)} topics, {tasks_per_topic} tasks each")
        
        for topic in topics:
            logger.info(f"📝 Working on topic: {topic}")
            
            for i in range(tasks_per_topic):
                try:
                    task = self.generate_single_task(topic, task_counter)
                    filepath = self.save_task(task)
                    all_tasks.append(task)
                    
                    logger.info(f"✅ Task {task_counter} completed: {task['title']}")
                    task_counter += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to generate task {task_counter} for '{topic}': {e}")
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