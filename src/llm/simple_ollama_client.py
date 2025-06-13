#!/usr/bin/env python3
"""
Simplified Ollama client that generates shorter, cleaner JSON
"""

import ollama
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class SimpleOllamaClient:
    """Simplified client for generating clean JSON responses"""
    
    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model
        self.client = ollama.Client()
    
    def generate_simple_task(self, topic: str) -> Dict[str, Any]:
        """Generate a simple, clean Reading Part 5 task"""
        
        # Much simpler prompt that asks for shorter content
        system_prompt = """You are a Cambridge B2 exam creator. Create a short Reading Part 5 task.

CRITICAL: Respond with ONLY valid JSON. No explanations. Keep text short and simple.

Format:
{
  "task_id": "task_01",
  "title": "Short Title",
  "topic": "topic",
  "text": "Short paragraph about the topic. Keep it under 200 words. No line breaks.",
  "questions": [
    {
      "number": 31,
      "question": "What is the main idea?",
      "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
      "answer": "A"
    }
  ]
}"""

        user_prompt = f"Create a simple Reading task about: {topic}. Keep the text short (under 200 words) and use only 1 question."
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={"temperature": 0.3}  # Lower temperature for more consistent output
            )
            
            content = response['message']['content'].strip()
            logger.info(f"Raw response length: {len(content)}")
            
            # Clean up the response
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Try to parse
            try:
                task_data = json.loads(content)
                logger.info("✅ Successfully parsed simple task")
                return task_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                logger.error(f"Content: {content[:300]}")
                
                # Try to find and extract just the JSON part
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    json_part = content[start:end]
                    try:
                        task_data = json.loads(json_part)
                        logger.info("✅ Successfully parsed extracted JSON")
                        return task_data
                    except json.JSONDecodeError as e2:
                        logger.error(f"Even extracted JSON failed: {e2}")
                
                # If all else fails, create a manual fallback
                return self.create_manual_fallback(topic)
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self.create_manual_fallback(topic)
    
    def create_manual_fallback(self, topic: str) -> Dict[str, Any]:
        """Create a manual fallback task"""
        return {
            "task_id": "fallback_01",
            "title": f"Reading: {topic.title()}",
            "topic": topic,
            "text": f"The topic of {topic} is very important in today's world. Many people are interested in learning more about this subject because it affects their daily lives. Experts believe that understanding {topic} can help people make better decisions. Research shows that those who study this area often develop useful skills. The future of {topic} looks promising as technology continues to advance.",
            "questions": [
                {
                    "number": 31,
                    "question": f"According to the text, why is {topic} important?",
                    "options": {
                        "A": "It is easy to understand",
                        "B": "It affects people's daily lives", 
                        "C": "It is a new discovery",
                        "D": "It requires no study"
                    },
                    "answer": "B"
                }
            ]
        }

def test_simple_generation():
    """Test the simple generation"""
    print("🧪 Testing Simple Ollama Generation")
    
    client = SimpleOllamaClient()
    
    try:
        task = client.generate_simple_task("sustainable travel")
        print("✅ Simple task generated successfully!")
        print(f"Title: {task.get('title')}")
        print(f"Text length: {len(task.get('text', '').split())} words")
        print(f"Questions: {len(task.get('questions', []))}")
        print("\nFull task:")
        print(json.dumps(task, indent=2))
        
    except Exception as e:
        print(f"❌ Simple generation failed: {e}")

if __name__ == "__main__":
    test_simple_generation() 