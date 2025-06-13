#!/usr/bin/env python3
"""
Debug script to see exactly what Ollama returns
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from llm.ollama_client import OllamaClient, OllamaConfig

def debug_ollama_response():
    """Debug what Ollama actually returns"""
    print("🔍 Debugging Ollama JSON response...")
    
    try:
        client = OllamaClient()
        
        # Simple test prompt
        system_prompt = """You must respond with ONLY valid JSON. No explanations, no markdown, no extra text.

Return this exact JSON structure:
{
    "test": "success",
    "message": "This is a test response"
}"""
        
        user_prompt = "Return the JSON structure as requested."
        
        print("📤 Sending test prompt...")
        print(f"System: {system_prompt[:100]}...")
        print(f"User: {user_prompt}")
        print("\n" + "="*50)
        
        response = client.generate_text(user_prompt, system_prompt)
        
        print("📥 Raw response received:")
        print(f"Length: {len(response)} characters")
        print(f"Type: {type(response)}")
        print("="*50)
        print(response)
        print("="*50)
        
        # Try to parse as JSON
        try:
            parsed = json.loads(response)
            print("✅ Successfully parsed as JSON:")
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            
            # Try to clean it up
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            print(f"\n🧹 After cleanup:")
            print(f"Length: {len(cleaned)} characters")
            print("="*30)
            print(cleaned)
            print("="*30)
            
            try:
                parsed = json.loads(cleaned)
                print("✅ Successfully parsed cleaned JSON:")
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError as e2:
                print(f"❌ Still failed after cleanup: {e2}")
                
                # Try to find JSON boundaries
                json_start = cleaned.find('{')
                json_end = cleaned.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_part = cleaned[json_start:json_end]
                    print(f"\n🎯 Extracted JSON part:")
                    print("="*30)
                    print(json_part)
                    print("="*30)
                    
                    try:
                        parsed = json.loads(json_part)
                        print("✅ Successfully parsed extracted JSON:")
                        print(json.dumps(parsed, indent=2))
                    except json.JSONDecodeError as e3:
                        print(f"❌ Even extracted part failed: {e3}")
                        
                        # Show character by character analysis
                        print("\n🔬 Character analysis of first 50 chars:")
                        for i, char in enumerate(json_part[:50]):
                            print(f"{i:2d}: '{char}' (ord: {ord(char)})")
                else:
                    print("❌ Could not find JSON boundaries")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_reading_task_generation():
    """Test actual reading task generation"""
    print("\n" + "="*60)
    print("🎯 Testing Reading Task Generation")
    print("="*60)
    
    try:
        client = OllamaClient()
        
        print("📤 Generating reading task...")
        task = client.generate_reading_part5_task("sustainable travel")
        
        print("✅ Task generation successful!")
        print(f"Title: {task.get('title', 'N/A')}")
        print(f"Text length: {len(task.get('text', '').split())} words")
        print(f"Questions: {len(task.get('questions', []))}")
        
    except Exception as e:
        print(f"❌ Task generation failed: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    debug_ollama_response()
    test_reading_task_generation() 