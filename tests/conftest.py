"""
Pytest configuration and fixtures for B2 First Content Generation Tool tests
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def temp_generated_tasks_dir():
    """Provide a temporary directory for test task generation"""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_tasks_"))
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

@pytest.fixture
def sample_task_data():
    """Provide sample task data for testing"""
    return {
        "task_id": "reading_part5_task_test",
        "title": "Test Task Title",
        "topic": "test_topic",
        "text_type": "magazine_article",
        "difficulty": "B2",
        "text": "This is a test reading text. " * 50,  # ~400 words
        "questions": [
            {
                "question_number": 1,
                "question_text": "What is the main idea?",
                "options": {
                    "A": "Option A",
                    "B": "Option B", 
                    "C": "Option C",
                    "D": "Option D"
                },
                "correct_answer": "A",
                "question_type": "main_idea"
            }
        ] * 5  # 5 questions
    }

@pytest.fixture
def ollama_available():
    """Check if Ollama is available for testing"""
    try:
        from llm.ollama_client import OllamaClient
        client = OllamaClient()
        return client.check_connection()
    except:
        return False

@pytest.fixture
def test_config():
    """Provide test configuration"""
    return {
        "test_topic": "sustainable travel",
        "test_text_type": "magazine_article",
        "timeout_seconds": 300,
        "min_text_length": 400,
        "max_text_length": 800,
        "expected_questions": 5
    } 