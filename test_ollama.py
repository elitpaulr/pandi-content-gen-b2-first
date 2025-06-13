#!/usr/bin/env python3
"""
Test script for Ollama integration
Run this to verify that Ollama is working correctly with the project
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_ollama_connection():
    """Test basic Ollama connection"""
    print("🔍 Testing Ollama connection...")
    
    try:
        from llm.ollama_client import OllamaClient
        
        client = OllamaClient()
        
        if client.check_connection():
            print("✅ Ollama connection successful!")
            
            models = client.list_models()
            print(f"📋 Available models: {models}")
            
            if models:
                print("🎯 Testing text generation...")
                response = client.generate_text(
                    "Write a short sentence about language learning.",
                    "You are a helpful assistant."
                )
                print(f"💬 Generated text: {response[:100]}...")
                print("✅ Text generation working!")
                return True
            else:
                print("⚠️  No models found. Pull a model first: ollama pull llama3.1:8b")
                return False
                
        else:
            print("❌ Failed to connect to Ollama")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to install requirements: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_task_generation():
    """Test Reading Part 5 task generation"""
    print("\n🎯 Testing task generation...")
    
    try:
        from content.ollama_part5_generator import OllamaTaskGenerator
        
        generator = OllamaTaskGenerator()
        
        if not generator.check_ollama_status():
            print("❌ Ollama not ready for task generation")
            return False
        
        print("🚀 Generating a test task...")
        task = generator.generate_single_task("sustainable travel", 999)
        
        print("✅ Task generation successful!")
        print(f"📖 Title: {task['title']}")
        print(f"📝 Text length: {len(task['text'].split())} words")
        print(f"❓ Questions: {len(task['questions'])}")
        print(f"🏷️  Category: {task.get('topic_category', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Task generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Ollama Integration Test Suite")
    print("=" * 40)
    
    # Test 1: Basic connection
    connection_ok = test_ollama_connection()
    
    if not connection_ok:
        print("\n❌ Basic connection failed. Please check:")
        print("1. Ollama is installed: https://ollama.ai/")
        print("2. Ollama is running: ollama serve")
        print("3. A model is available: ollama pull llama3.1:8b")
        return 1
    
    # Test 2: Task generation
    generation_ok = test_task_generation()
    
    print("\n" + "=" * 40)
    if connection_ok and generation_ok:
        print("🎉 All tests passed! Ollama integration is working correctly.")
        print("\nNext steps:")
        print("1. Run the Ollama generator: streamlit run app/ollama_generator.py --server.port 8507")
        print("2. Or use command line: python src/content/ollama_part5_generator.py")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main()) 