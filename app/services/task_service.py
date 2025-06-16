"""
Task Service for B2 First Task Generator
Handles task loading, saving, processing, and management operations
"""

import json
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class TaskService:
    """
    Centralized task management service
    Handles all task-related operations including loading, saving, and processing
    """
    
    def __init__(self, tasks_dir: Path):
        """
        Initialize the task service
        
        Args:
            tasks_dir: Path to the generated tasks directory
        """
        self.tasks_dir = tasks_dir
        self.tasks_dir.mkdir(exist_ok=True)  # Ensure directory exists
    
    def load_individual_tasks(self) -> List[Dict[str, Any]]:
        """
        Load all individual task files from the tasks directory
        
        Returns:
            List of task dictionaries with metadata
        """
        task_files = list(self.tasks_dir.glob("*.json"))
        tasks = []
        
        for task_file in task_files:
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    task = json.load(f)
                    # Add file metadata
                    task['filename'] = task_file.name
                    task['file_path'] = str(task_file)
                    task['word_count'] = len(task.get('text', '').split())
                    tasks.append(task)
            except Exception as e:
                st.warning(f"Could not load {task_file.name}: {e}")
        
        return tasks
    
    def load_batch_collections(self) -> List[Dict[str, Any]]:
        """
        Load all batch directories and their metadata
        
        Returns:
            List of batch collection dictionaries
        """
        batch_dirs = [d for d in self.tasks_dir.iterdir() 
                     if d.is_dir() and d.name.startswith("batch_")]
        
        batch_data = []
        for batch_dir in batch_dirs:
            try:
                task_files = list(batch_dir.glob("*.json"))
                batch_info = {
                    'name': batch_dir.name,
                    'path': batch_dir,
                    'task_count': len(task_files),
                    'created': batch_dir.stat().st_ctime,
                    'size_mb': sum(f.stat().st_size for f in task_files) / (1024 * 1024)
                }
                batch_data.append(batch_info)
            except Exception as e:
                st.warning(f"Could not load batch {batch_dir.name}: {e}")
        
        return batch_data
    
    def clean_task_for_json(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove non-serializable fields from task for JSON export
        
        Args:
            task: Task dictionary to clean
            
        Returns:
            Cleaned task dictionary safe for JSON serialization
        """
        def clean_value(value):
            """Recursively clean a value for JSON serialization"""
            if hasattr(value, '__fspath__'):  # Path-like object
                return str(value)
            elif isinstance(value, dict):
                return {k: clean_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [clean_value(item) for item in value]
            else:
                return value
        
        task_clean = {}
        for k, v in task.items():
            if k not in ['file_path', 'filename']:  # Exclude non-serializable fields
                task_clean[k] = clean_value(v)
        return task_clean
    
    def save_task(self, task: Dict[str, Any], custom_filename: Optional[str] = None) -> Path:
        """
        Save a task to the tasks directory
        
        Args:
            task: Task dictionary to save
            custom_filename: Optional custom filename (otherwise uses task_id)
            
        Returns:
            Path to the saved file
        """
        # Clean task for JSON serialization
        task_clean = self.clean_task_for_json(task)
        
        # Determine filename
        if custom_filename:
            filename = custom_filename
        else:
            task_id = task.get('task_id', f'task_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            filename = f"{task_id}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Save file
        file_path = self.tasks_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(task_clean, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def delete_task(self, task_file_path: str) -> bool:
        """
        Delete a task file
        
        Args:
            task_file_path: Path to the task file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            file_path = Path(task_file_path)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting task: {e}")
            return False
    
    def get_task_qa_status(self, task: Dict[str, Any]) -> str:
        """
        Get the overall QA status of a task
        
        Args:
            task: Task dictionary
            
        Returns:
            QA status: 'approved', 'rejected', or 'pending'
        """
        qa_annotations = task.get('qa_annotations', {})
        overall_task_annotation = qa_annotations.get('overall_task', {})
        return overall_task_annotation.get('status', 'pending')
    
    def get_qa_status_emoji(self, status: str) -> str:
        """
        Get emoji representation for QA status
        
        Args:
            status: QA status string
            
        Returns:
            Corresponding emoji
        """
        status_emojis = {
            'approved': '✅',
            'rejected': '❌', 
            'pending': '⏳'
        }
        return status_emojis.get(status, '⏳')
    
    def get_qa_status_color(self, status: str) -> str:
        """
        Get color for QA status display
        
        Args:
            status: QA status string
            
        Returns:
            Color name for Streamlit
        """
        status_colors = {
            'approved': 'green',
            'rejected': 'red',
            'pending': 'orange'
        }
        return status_colors.get(status, 'gray')
    
    def filter_tasks_by_qa_status(self, tasks: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
        """
        Filter tasks by QA status
        
        Args:
            tasks: List of task dictionaries
            status: QA status to filter by
            
        Returns:
            Filtered list of tasks
        """
        return [task for task in tasks if self.get_task_qa_status(task) == status]
    
    def get_tasks_statistics(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics for a list of tasks
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Dictionary with various statistics
        """
        if not tasks:
            return {
                'total_tasks': 0,
                'total_words': 0,
                'total_questions': 0,
                'avg_word_count': 0,
                'qa_status_counts': {'approved': 0, 'rejected': 0, 'pending': 0}
            }
        
        total_words = sum(task.get('word_count', 0) for task in tasks)
        total_questions = sum(len(task.get('questions', [])) for task in tasks)
        
        # QA status counts
        qa_status_counts = {'approved': 0, 'rejected': 0, 'pending': 0}
        for task in tasks:
            status = self.get_task_qa_status(task)
            qa_status_counts[status] = qa_status_counts.get(status, 0) + 1
        
        return {
            'total_tasks': len(tasks),
            'total_words': total_words,
            'total_questions': total_questions,
            'avg_word_count': total_words / len(tasks) if tasks else 0,
            'qa_status_counts': qa_status_counts
        }
    
    def sort_tasks(self, tasks: List[Dict[str, Any]], sort_by: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Sort tasks by specified criteria
        
        Args:
            tasks: List of task dictionaries
            sort_by: Field to sort by ('task_id', 'word_count', 'created', etc.)
            reverse: Whether to sort in descending order
            
        Returns:
            Sorted list of tasks
        """
        try:
            if sort_by == 'word_count':
                return sorted(tasks, key=lambda x: x.get('word_count', 0), reverse=reverse)
            elif sort_by == 'questions':
                return sorted(tasks, key=lambda x: len(x.get('questions', [])), reverse=reverse)
            elif sort_by == 'qa_status':
                return sorted(tasks, key=lambda x: self.get_task_qa_status(x), reverse=reverse)
            elif sort_by == 'topic':
                return sorted(tasks, key=lambda x: x.get('topic', ''), reverse=reverse)
            elif sort_by == 'title':
                return sorted(tasks, key=lambda x: x.get('title', ''), reverse=reverse)
            else:  # Default to task_id
                return sorted(tasks, key=lambda x: x.get('task_id', ''), reverse=reverse)
        except Exception as e:
            st.warning(f"Error sorting tasks: {e}")
            return tasks
    
    def export_tasks_batch(self, tasks: List[Dict[str, Any]], export_name: str) -> bytes:
        """
        Export multiple tasks as a ZIP file
        
        Args:
            tasks: List of task dictionaries to export
            export_name: Name for the export batch
            
        Returns:
            ZIP file content as bytes
        """
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, task in enumerate(tasks):
                task_clean = self.clean_task_for_json(task)
                task_json = json.dumps(task_clean, indent=2, ensure_ascii=False)
                
                # Create filename
                task_id = task.get('task_id', f'task_{i+1}')
                filename = f"{task_id}.json"
                
                zip_file.writestr(filename, task_json)
            
            # Add batch summary
            batch_summary = {
                'export_name': export_name,
                'export_date': datetime.now().isoformat(),
                'task_count': len(tasks),
                'statistics': self.get_tasks_statistics(tasks)
            }
            
            zip_file.writestr('batch_summary.json', 
                            json.dumps(batch_summary, indent=2, ensure_ascii=False))
        
        return zip_buffer.getvalue()
    
    def validate_task_structure(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate task structure and return validation results
        
        Args:
            task: Task dictionary to validate
            
        Returns:
            Dictionary with validation results and issues
        """
        issues = []
        warnings = []
        
        # Required fields
        required_fields = ['task_id', 'title', 'text', 'questions']
        for field in required_fields:
            if field not in task or not task[field]:
                issues.append(f"Missing required field: {field}")
        
        # Text validation
        if 'text' in task:
            word_count = len(task['text'].split())
            if word_count < 400:
                warnings.append(f"Text too short: {word_count} words (recommended: 400-800)")
            elif word_count > 800:
                warnings.append(f"Text too long: {word_count} words (recommended: 400-800)")
        
        # Questions validation
        if 'questions' in task:
            questions = task['questions']
            if len(questions) < 5:
                issues.append(f"Too few questions: {len(questions)} (required: 5-6)")
            elif len(questions) > 6:
                warnings.append(f"Too many questions: {len(questions)} (recommended: 5-6)")
            
            # Validate individual questions
            for i, question in enumerate(questions, 1):
                if 'question_text' not in question:
                    issues.append(f"Question {i}: Missing question text")
                if 'options' not in question:
                    issues.append(f"Question {i}: Missing options")
                elif len(question.get('options', {})) != 4:
                    issues.append(f"Question {i}: Must have exactly 4 options")
                if 'correct_answer' not in question:
                    issues.append(f"Question {i}: Missing correct answer")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'score': max(0, 100 - len(issues) * 20 - len(warnings) * 5)
        } 