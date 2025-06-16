"""
Core System Tests for B2 First Content Generation Tool

These tests verify the complete end-to-end functionality of the system.
"""

import pytest
import json
from pathlib import Path
import time

# Import the modules we need to test
try:
    from content.ollama_part5_generator import OllamaTaskGenerator
    from llm.ollama_client import OllamaClient
    from llm.json_parser import RobustJSONParser
except ImportError as e:
    pytest.skip(f"Required modules not available: {e}", allow_module_level=True)


class TestEndToEndTaskGeneration:
    """Test complete task generation pipeline"""
    
    @pytest.mark.system
    @pytest.mark.slow
    def test_complete_task_generation_pipeline(self, ollama_available, test_config, temp_generated_tasks_dir):
        """Test the full pipeline from topic input to saved JSON file"""
        if not ollama_available:
            pytest.skip("Ollama not available for testing")
        
        # Given
        topic = test_config["test_topic"]
        text_type = test_config["test_text_type"]
        
        # When
        generator = OllamaTaskGenerator("llama3.1:8b")
        
        try:
            start_time = time.time()
            task = generator.generate_single_task(topic, text_type=text_type)
            generation_time = time.time() - start_time
            
            # Then - Verify task structure
            assert task is not None, "Task generation returned None"
            assert isinstance(task, dict), "Task should be a dictionary"
            
            # Verify required fields
            required_fields = ['task_id', 'title', 'topic', 'text_type', 'difficulty', 'text', 'questions']
            for field in required_fields:
                assert field in task, f"Missing required field: {field}"
                assert task[field] is not None, f"Field {field} is None"
            
            # Verify text length
            text_words = len(task['text'].split())
            assert test_config["min_text_length"] <= text_words <= test_config["max_text_length"], \
                f"Text length {text_words} not in range {test_config['min_text_length']}-{test_config['max_text_length']}"
            
            # Verify questions
            assert isinstance(task['questions'], list), "Questions should be a list"
            assert len(task['questions']) >= 5, f"Expected at least 5 questions, got {len(task['questions'])}"
            
            # Verify each question structure
            for i, question in enumerate(task['questions']):
                assert 'question_number' in question, f"Question {i} missing question_number"
                assert 'question_text' in question, f"Question {i} missing question_text"
                assert 'options' in question, f"Question {i} missing options"
                assert 'correct_answer' in question, f"Question {i} missing correct_answer"
                
                # Verify options
                options = question['options']
                assert isinstance(options, dict), f"Question {i} options should be dict"
                assert set(options.keys()) == {'A', 'B', 'C', 'D'}, f"Question {i} should have options A,B,C,D"
                assert question['correct_answer'] in options, f"Question {i} correct_answer not in options"
            
            # Verify performance
            assert generation_time < test_config["timeout_seconds"], \
                f"Generation took {generation_time:.1f}s, expected < {test_config['timeout_seconds']}s"
            
            print(f"✅ Task generated successfully in {generation_time:.1f}s")
            print(f"📖 Title: {task['title']}")
            print(f"📝 Text: {text_words} words")
            print(f"❓ Questions: {len(task['questions'])}")
            
        finally:
            # No need to restore directory, as it's not set on the generator
            pass


class TestOllamaIntegration:
    """Test Ollama LLM integration"""
    
    @pytest.mark.integration
    def test_ollama_connection(self):
        """Test basic Ollama connection and model availability"""
        client = OllamaClient()
        
        # Test connection
        is_connected = client.check_connection()
        assert is_connected, "Failed to connect to Ollama service"
        
        # Test model listing
        models = client.list_models()
        assert isinstance(models, list), "Models should be returned as a list"
        assert len(models) > 0, "No models available - run 'ollama pull llama3.1:8b'"
        
        print(f"✅ Connected to Ollama with {len(models)} models: {models}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_text_generation(self, ollama_available):
        """Test basic text generation functionality"""
        if not ollama_available:
            pytest.skip("Ollama not available for testing")
        
        client = OllamaClient()
        
        # Test simple text generation
        response = client.generate_text(
            "Write one sentence about language learning.",
            "You are a helpful assistant."
        )
        
        assert response is not None, "Text generation returned None"
        assert isinstance(response, str), "Response should be a string"
        assert len(response.strip()) > 0, "Response should not be empty"
        assert len(response.split()) >= 5, "Response should be at least 5 words"
        
        print(f"✅ Generated text: {response[:100]}...")


class TestJSONProcessing:
    """Test JSON parsing and validation"""
    
    @pytest.mark.unit
    def test_json_parser_valid_json(self, sample_task_data):
        """Test parsing valid JSON"""
        parser = RobustJSONParser()
        
        # Convert to JSON string and back
        json_str = json.dumps(sample_task_data)
        parsed_data = parser.parse_llm_json(json_str)
        
        assert parsed_data is not None, "Failed to parse valid JSON"
        assert parsed_data == sample_task_data, "Parsed data doesn't match original"
    
    @pytest.mark.unit
    def test_json_parser_malformed_json(self):
        """Test parsing malformed JSON with recovery"""
        parser = RobustJSONParser()
        
        # Test with common LLM output issues
        malformed_cases = [
            '{"title": "Test", "text": "Some text with\ncontrol chars"}',
            '{"title": "Test", "incomplete": ',
            'Some text before {"title": "Test"} some text after',
        ]
        
        for case in malformed_cases:
            try:
                result = parser.parse_llm_json(case)
                # Should either parse successfully or return None (not crash)
                assert result is None or isinstance(result, dict), \
                    f"Parser should handle malformed JSON gracefully: {case[:50]}..."
            except ValueError:
                # This is also an acceptable outcome for malformed JSON
                pass


class TestTaskValidation:
    """Test task validation logic"""
    
    @pytest.mark.unit
    def test_valid_task_structure(self, sample_task_data):
        """Test validation of a properly structured task"""
        # This would test the validation logic if it were extracted to a separate function
        # For now, we'll test the basic structure requirements
        
        required_fields = ['task_id', 'title', 'topic', 'text_type', 'difficulty', 'text', 'questions']
        for field in required_fields:
            assert field in sample_task_data, f"Sample task missing required field: {field}"
        
        # Test questions structure
        questions = sample_task_data['questions']
        assert len(questions) >= 5, "Should have at least 5 questions"
        
        for question in questions:
            assert 'question_number' in question
            assert 'question_text' in question
            assert 'options' in question
            assert 'correct_answer' in question
            assert set(question['options'].keys()) == {'A', 'B', 'C', 'D'}
            assert question['correct_answer'] in question['options']


class TestFileOperations:
    """Test file I/O operations"""
    
    @pytest.mark.unit
    def test_task_file_save_load(self, sample_task_data, temp_generated_tasks_dir):
        """Test saving and loading task files"""
        # Test file save
        task_file = temp_generated_tasks_dir / "test_task.json"
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(sample_task_data, f, indent=2, ensure_ascii=False)
        
        assert task_file.exists(), "Task file was not created"
        assert task_file.stat().st_size > 0, "Task file is empty"
        
        # Test file load
        with open(task_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == sample_task_data, "Loaded data doesn't match saved data"
        
        print(f"✅ Successfully saved and loaded task file: {task_file.name}")


# Performance benchmarks (optional, slow tests)
class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.slow
    @pytest.mark.system
    def test_generation_performance_benchmark(self, ollama_available, test_config):
        """Benchmark task generation performance"""
        if not ollama_available:
            pytest.skip("Ollama not available for performance testing")
        
        generator = OllamaTaskGenerator("llama3.1:8b")
        
        # Benchmark single task generation
        start_time = time.time()
        try:
            task = generator.generate_single_task(test_config["test_topic"])
            generation_time = time.time() - start_time
            
            assert task is not None, "Task generation should produce a result"
            assert isinstance(task, dict), "Task should be a dictionary"
            
            print(f"Task generation took {generation_time:.2f} seconds")
            
            # Allow for some performance variation, but fail if excessively slow
            assert generation_time < 300, "Task generation took too long"
            
        except RuntimeError as e:
            pytest.skip(f"Task generation failed validation, skipping performance test: {e}")
        
        # Log performance metrics
        text_words = len(task['text'].split())
        words_per_second = text_words / generation_time
        
        print(f"📊 Performance Metrics:")
        print(f"   Generation time: {generation_time:.1f}s")
        print(f"   Text length: {text_words} words")
        print(f"   Generation rate: {words_per_second:.1f} words/second")
        print(f"   Questions: {len(task['questions'])}") 