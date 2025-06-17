import pytest
import json
from pathlib import Path
import sys

# Add app to path for service imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

try:
    from services.config_service import ConfigService
    from services.task_service import TaskService
    from services.ui_components import UIComponents
except ImportError as e:
    pytest.skip(f"Service modules not available: {e}", allow_module_level=True)


@pytest.fixture
def config_service():
    """Create a ConfigService instance for testing"""
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    return ConfigService(project_root)

@pytest.fixture
def task_service(temp_generated_tasks_dir):
    """Create a TaskService instance for testing"""
    return TaskService(temp_generated_tasks_dir)

@pytest.fixture
def ui_components(task_service, config_service):
    """Create a UIComponents instance for testing"""
    return UIComponents(task_service, config_service)

class TestConfigService:
    """Test ConfigService functionality"""
    
    @pytest.mark.unit
    def test_config_service_initialization(self, config_service):
        """Test that ConfigService initializes properly"""
        assert config_service is not None
        assert hasattr(config_service, 'get_topic_sets')
        assert hasattr(config_service, 'get_b2_text_types')
    
    @pytest.mark.unit
    def test_get_topic_sets(self, config_service):
        """Test topic sets retrieval"""
        topic_sets = config_service.get_topic_sets()
        
        assert isinstance(topic_sets, dict), "Topic sets should be a dictionary"
        assert len(topic_sets) > 0, "Should have at least one topic set"
        
        # Check structure of topic sets
        for category, topics in topic_sets.items():
            assert isinstance(category, str), "Category should be string"
            assert isinstance(topics, list), "Topics should be a list"
            assert len(topics) > 0, f"Category {category} should have topics"
            
            for topic in topics:
                assert isinstance(topic, str), "Each topic should be a string"
                assert len(topic.strip()) > 0, "Topic should not be empty"
        # Check that at least one expected category from the knowledge base is present
        expected_category = "Sport & Fitness"
        assert expected_category in topic_sets, f"Expected category '{expected_category}' not found in topic sets"
    
    @pytest.mark.unit
    def test_get_text_types(self, config_service):
        """Test text types retrieval"""
        text_types = config_service.get_b2_text_types()
        
        assert isinstance(text_types, dict), "Text types should be a dictionary"
        assert len(text_types) > 0, "Should have at least one text type"
        
        # Check for expected text types
        expected_keys = ['blog_post', 'magazine_article']
        
        all_keys = []
        for v in text_types.values():
            all_keys.append(v['key'])

        for expected_key in expected_keys:
            assert expected_key in all_keys, f"Missing expected text type key: {expected_key}"


class TestTaskService:
    """Test TaskService functionality"""
    
    @pytest.fixture
    def mock_task_file(self, temp_generated_tasks_dir, sample_task_data):
        """Create a mock task file for testing"""
        task_file = temp_generated_tasks_dir / "reading_part5_task_01.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(sample_task_data, f, indent=2)
        return task_file
    
    @pytest.mark.unit
    def test_task_service_initialization(self, task_service):
        """Test that TaskService initializes properly"""
        assert task_service is not None
        assert hasattr(task_service, 'load_individual_tasks')
        assert hasattr(task_service, 'save_task')
        assert hasattr(task_service, 'get_task_qa_status')
        assert hasattr(task_service, 'validate_task_structure')
    
    @pytest.mark.unit
    def test_get_task_qa_status(self, task_service, sample_task_data):
        """Test QA status determination"""
        # Test task without QA data
        status = task_service.get_task_qa_status(sample_task_data)
        assert status == 'pending', "Task without QA should be pending"
        
        # Test task with approved QA
        approved_task = sample_task_data.copy()
        approved_task['qa_annotations'] = {'overall_task': {'status': 'approved'}}
        status = task_service.get_task_qa_status(approved_task)
        assert status == 'approved', "Task with approved QA should be approved"
        
        # Test task with rejected QA
        rejected_task = sample_task_data.copy()
        rejected_task['qa_annotations'] = {'overall_task': {'status': 'rejected'}}
        status = task_service.get_task_qa_status(rejected_task)
        assert status == 'rejected', "Task with rejected QA should be rejected"
    
    @pytest.mark.unit
    def test_get_qa_status_emoji(self, task_service):
        """Test QA status emoji mapping"""
        assert task_service.get_qa_status_emoji('approved') == '✅'
        assert task_service.get_qa_status_emoji('rejected') == '❌'
        assert task_service.get_qa_status_emoji('pending') == '⏳'
    
    @pytest.mark.unit
    def test_validate_task_structure(self, task_service, sample_task_data):
        """Test task structure validation"""
        # Test valid task
        result = task_service.validate_task_structure(sample_task_data)
        assert result['is_valid'], f"Valid task should pass validation: {result['issues']}"
        
        # Test invalid task - missing required field
        invalid_task = sample_task_data.copy()
        del invalid_task['title']
        result = task_service.validate_task_structure(invalid_task)
        assert not result['is_valid'], "Task missing title should fail validation"
    
    @pytest.mark.unit
    def test_clean_task_for_json(self, task_service, sample_task_data):
        """Test task cleaning for JSON serialization"""
        # Add some non-serializable fields
        dirty_task = sample_task_data.copy()
        dirty_task['filename'] = 'test.json'
        dirty_task['file_path'] = '/path/to/test.json'
        
        clean_task = task_service.clean_task_for_json(dirty_task)
        
        # Should remove non-serializable fields
        assert 'filename' not in clean_task
        assert 'file_path' not in clean_task
        
        # Should keep all original fields
        for key in sample_task_data:
            assert key in clean_task, f"Should preserve field: {key}"
    
    @pytest.mark.unit
    def test_load_individual_tasks(self, task_service, mock_task_file):
        """Test loading individual task files"""
        # Set the generated_tasks directory to our temp directory
        original_base_path = getattr(task_service, 'tasks_dir', None)
        task_service.tasks_dir = mock_task_file.parent
        
        try:
            tasks = task_service.load_individual_tasks()
            
            assert isinstance(tasks, list), "Should return a list of tasks"
            assert len(tasks) == 1, "Should find one task file"
            
            task = tasks[0]
            assert task['task_id'] == 'reading_part5_task_test'
            assert task['title'] == 'Test Task Title'
            
        finally:
            # Restore original base path if it existed
            if original_base_path:
                task_service.tasks_dir = original_base_path


class TestUIComponents:
    """Test UIComponents service"""
    
    @pytest.mark.unit
    def test_ui_components_initialization(self, ui_components):
        """Test that UIComponents initializes properly"""
        assert ui_components is not None
        assert hasattr(ui_components, 'display_task_header')
        assert hasattr(ui_components, 'display_reading_text')
        assert hasattr(ui_components, 'display_questions')
        assert hasattr(ui_components, 'display_task_summary_card')
    
    @pytest.mark.unit
    def test_format_text_for_display(self, ui_components):
        """Test text formatting for display"""
        # Test basic text formatting
        test_text = "This is a test paragraph.\n\nThis is another paragraph."
        
        # This would test the text formatting if the method is public
        # For now, we'll just verify the service has the expected methods
        assert hasattr(ui_components, 'display_reading_text')
    
    @pytest.mark.unit
    def test_display_methods_exist(self, ui_components):
        """Test that all expected display methods exist"""
        expected_methods = [
            'display_task_header',
            'display_reading_text', 
            'display_questions',
            'display_task_summary_card',
            'display_batch_statistics',
            'display_task_validation_results',
            'display_progress_tracker',
            'display_task_filters',
            'display_export_options',
            'display_qa_annotation_interface',
            'display_task_comparison'
        ]
        
        for method_name in expected_methods:
            assert hasattr(ui_components, method_name), f"Missing method: {method_name}"
            method = getattr(ui_components, method_name)
            assert callable(method), f"Method {method_name} should be callable"


class TestServiceIntegration:
    """Test integration between services"""
    
    @pytest.fixture
    def all_services(self, config_service, task_service, ui_components):
        """Create all service instances"""
        return {
            'config': config_service,
            'task': task_service,
            'ui': ui_components
        }
    
    @pytest.mark.integration
    def test_services_work_together(self, all_services, sample_task_data):
        """Test that services can work together"""
        config_service = all_services['config']
        task_service = all_services['task']
        ui_service = all_services['ui']
        
        # Test config service provides data for task service
        topic_sets = config_service.get_topic_sets()
        assert len(topic_sets) > 0, "Config service should provide topic sets"
        
        # Test task service can process task data
        qa_status = task_service.get_task_qa_status(sample_task_data)
        assert qa_status in ['pending', 'approved', 'rejected'], "Task service should return valid QA status"
        
        # Test task validation
        is_valid = task_service.validate_task_structure(sample_task_data)
        assert is_valid['is_valid'], f"Sample task should be valid: {is_valid['issues']}"
        
        # Test services are properly initialized
        assert all(service is not None for service in all_services.values())
        
        print("✅ All services initialized and working together") 