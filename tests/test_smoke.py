"""
Smoke Tests for B2 First Content Generation Tool

Quick tests to verify basic functionality is working.
These should run fast and catch major issues.
"""

import pytest
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


class TestBasicImports:
    """Test that all critical modules can be imported"""
    
    @pytest.mark.unit
    def test_import_ollama_client(self):
        """Test importing OllamaClient"""
        try:
            from llm.ollama_client import OllamaClient
            assert OllamaClient is not None
        except ImportError as e:
            pytest.fail(f"Failed to import OllamaClient: {e}")
    
    @pytest.mark.unit
    def test_import_task_generator(self):
        """Test importing OllamaTaskGenerator"""
        try:
            from content.ollama_part5_generator import OllamaTaskGenerator
            assert OllamaTaskGenerator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import OllamaTaskGenerator: {e}")
    
    @pytest.mark.unit
    def test_import_json_parser(self):
        """Test importing RobustJSONParser"""
        try:
            from llm.json_parser import RobustJSONParser
            assert RobustJSONParser is not None
        except ImportError as e:
            pytest.fail(f"Failed to import RobustJSONParser: {e}")
    
    @pytest.mark.unit
    def test_import_services(self):
        """Test importing service modules"""
        try:
            from services.config_service import ConfigService
            from services.task_service import TaskService
            from services.ui_components import UIComponents
            
            assert ConfigService is not None
            assert TaskService is not None
            assert UIComponents is not None
        except ImportError as e:
            pytest.fail(f"Failed to import services: {e}")


class TestBasicInstantiation:
    """Test that classes can be instantiated without errors"""
    
    @pytest.mark.unit
    def test_create_ollama_client(self):
        """Test creating OllamaClient instance"""
        try:
            from llm.ollama_client import OllamaClient
            client = OllamaClient()
            assert client is not None
        except Exception as e:
            pytest.fail(f"Failed to create OllamaClient: {e}")
    
    @pytest.mark.unit
    def test_create_json_parser(self):
        """Test creating RobustJSONParser instance"""
        try:
            from llm.json_parser import RobustJSONParser
            parser = RobustJSONParser()
            assert parser is not None
        except Exception as e:
            pytest.fail(f"Failed to create RobustJSONParser: {e}")
    
    @pytest.mark.unit
    def test_create_services(self):
        """Test creating service instances"""
        try:
            from services.config_service import ConfigService
            from services.task_service import TaskService
            from services.ui_components import UIComponents
            from pathlib import Path
            
            # Create services with required arguments
            project_root = Path(__file__).parent.parent
            tasks_dir = project_root / "generated_tasks"
            tasks_dir.mkdir(exist_ok=True)
            
            config_service = ConfigService(project_root)
            task_service = TaskService(tasks_dir)
            ui_components = UIComponents(task_service, config_service)
            
            assert config_service is not None
            assert task_service is not None
            assert ui_components is not None
        except Exception as e:
            pytest.fail(f"Failed to create services: {e}")


class TestConfigFiles:
    """Test that required configuration files exist"""
    
    @pytest.mark.unit
    def test_knowledge_base_files_exist(self):
        """Test that knowledge base files exist"""
        knowledge_base_dir = Path(__file__).parent.parent / "knowledge_base"
        
        expected_files = [
            "b2_first_reading_part5_generation_guidelines.json"
        ]
        
        for filename in expected_files:
            file_path = knowledge_base_dir / filename
            assert file_path.exists(), f"Missing knowledge base file: {filename}"
            assert file_path.stat().st_size > 0, f"Knowledge base file is empty: {filename}"
    
    @pytest.mark.unit
    def test_config_files_exist(self):
        """Test that configuration files exist"""
        config_dir = Path(__file__).parent.parent / "config"
        
        if config_dir.exists():
            # Check for any JSON files in config directory
            json_files = list(config_dir.glob("*.json"))
            if json_files:
                for json_file in json_files:
                    assert json_file.stat().st_size > 0, f"Config file is empty: {json_file.name}"


class TestBasicFunctionality:
    """Test basic functionality without external dependencies"""
    
    @pytest.mark.unit
    def test_json_parser_basic_functionality(self):
        """Test basic JSON parsing functionality"""
        try:
            from llm.json_parser import RobustJSONParser
            
            parser = RobustJSONParser()
            
            # Test valid JSON
            valid_json = '{"test": "value", "number": 42}'
            result = parser.parse_llm_json(valid_json)
            
            assert result is not None, "Should parse valid JSON"
            assert result["test"] == "value", "Should preserve string values"
            assert result["number"] == 42, "Should preserve numeric values"
            
        except Exception as e:
            pytest.fail(f"JSON parser basic functionality failed: {e}")
    
    @pytest.mark.unit
    def test_config_service_basic_functionality(self):
        """Test basic ConfigService functionality"""
        try:
            from services.config_service import ConfigService
            from pathlib import Path
            
            project_root = Path(__file__).parent.parent
            config_service = ConfigService(project_root)
            
            # Test that methods exist and return something
            topic_sets = config_service.get_topic_sets()
            text_types = config_service.get_b2_text_types()
            
            assert isinstance(topic_sets, dict), "Topic sets should be a dictionary"
            assert isinstance(text_types, dict), "Text types should be a dictionary"
            assert len(topic_sets) > 0, "Should have some topic sets"
            assert len(text_types) > 0, "Should have some text types"
            # Check that at least one expected category from the knowledge base is present
            expected_category = "Sport & Fitness"
            assert expected_category in topic_sets, f"Expected category '{expected_category}' not found in topic sets"
        except Exception as e:
            pytest.fail(f"ConfigService basic functionality failed: {e}")
    
    @pytest.mark.unit
    def test_task_service_basic_functionality(self):
        """Test basic TaskService functionality"""
        try:
            from services.task_service import TaskService
            from pathlib import Path
            
            project_root = Path(__file__).parent.parent
            tasks_dir = project_root / "generated_tasks"
            tasks_dir.mkdir(exist_ok=True)
            
            task_service = TaskService(tasks_dir)
            
            # Test basic methods exist and work
            sample_task = {
                "task_id": "test",
                "title": "Test Task",
                "topic": "test",
                "text_type": "magazine_article",
                "difficulty": "B2",
                "text": "Test text",
                "questions": []
            }
            
            # Test QA status
            status = task_service.get_task_qa_status(sample_task)
            assert status in ['pending', 'approved', 'rejected'], "Should return valid QA status"
            
            # Test emoji mapping
            emoji = task_service.get_qa_status_emoji(status)
            assert isinstance(emoji, str), "Should return emoji string"
            assert len(emoji) > 0, "Emoji should not be empty"
            
        except Exception as e:
            pytest.fail(f"TaskService basic functionality failed: {e}")


class TestDirectoryStructure:
    """Test that required directories exist"""
    
    @pytest.mark.unit
    def test_required_directories_exist(self):
        """Test that all required directories exist"""
        base_dir = Path(__file__).parent.parent
        
        required_dirs = [
            "src",
            "src/llm",
            "src/content", 
            "app",
            "app/services",
            "knowledge_base",
            "docs"
        ]
        
        for dir_name in required_dirs:
            dir_path = base_dir / dir_name
            assert dir_path.exists(), f"Missing required directory: {dir_name}"
            assert dir_path.is_dir(), f"Path exists but is not a directory: {dir_name}"
    
    @pytest.mark.unit
    def test_generated_tasks_directory(self):
        """Test that generated_tasks directory exists or can be created"""
        base_dir = Path(__file__).parent.parent
        generated_tasks_dir = base_dir / "generated_tasks"
        
        # Should exist or be creatable
        if not generated_tasks_dir.exists():
            try:
                generated_tasks_dir.mkdir(exist_ok=True)
                assert generated_tasks_dir.exists(), "Should be able to create generated_tasks directory"
            except Exception as e:
                pytest.fail(f"Cannot create generated_tasks directory: {e}")
        else:
            assert generated_tasks_dir.is_dir(), "generated_tasks should be a directory"


if __name__ == "__main__":
    # Run smoke tests when executed directly
    pytest.main([__file__, "-v"]) 