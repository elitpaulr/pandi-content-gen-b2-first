"""
UI Components Service for B2 First Task Generator
Centralizes all display functions and UI components to eliminate code duplication
"""

import streamlit as st
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import zipfile
import io

class UIComponents:
    """
    Centralized UI components service
    Handles all display functions and UI rendering logic
    """
    
    def __init__(self, task_service, config_service):
        """
        Initialize UI components with required services
        
        Args:
            task_service: TaskService instance
            config_service: ConfigService instance
        """
        self.task_service = task_service
        self.config_service = config_service
    
    def display_task_header(self, task: Dict[str, Any], show_qa_status: bool = True) -> None:
        """
        Display task header with title, metadata, and QA status
        
        Args:
            task: Task dictionary
            show_qa_status: Whether to show QA status indicator
        """
        # Main title
        st.header(task.get('title', 'Untitled Task'))
        
        # Metadata row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Task ID", task.get('task_id', 'N/A'))
        
        with col2:
            word_count = len(task.get('text', '').split())
            st.metric("📊 Word Count", f"{word_count:,}")
        
        with col3:
            question_count = len(task.get('questions', []))
            st.metric("❓ Questions", question_count)
        
        with col4:
            if show_qa_status:
                qa_status = self.task_service.get_task_qa_status(task)
                emoji = self.task_service.get_qa_status_emoji(qa_status)
                st.metric(f"{emoji} QA Status", qa_status.title())
        
        # Topic and difficulty
        col1, col2 = st.columns(2)
        with col1:
            if task.get('topic'):
                st.info(f"🎯 **Topic:** {task['topic']}")
        with col2:
            if task.get('difficulty'):
                st.info(f"🎓 **Level:** {task['difficulty']}")
    
    def display_reading_text(self, task: Dict[str, Any], container_type: str = "container") -> None:
        """
        Display the reading text in a formatted container
        
        Args:
            task: Task dictionary
            container_type: Type of container ('container', 'expander', 'columns')
        """
        text = task.get('text', '')
        if not text:
            st.warning("No reading text available")
            return
        
        if container_type == "expander":
            with st.expander("📖 Reading Text", expanded=True):
                st.markdown(text)
        elif container_type == "columns":
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("📖 Reading Text")
                st.markdown(text)
        else:  # default container
            st.subheader("📖 Reading Text")
            with st.container():
                st.markdown(text)
    
    def display_questions(self, task: Dict[str, Any], show_answers: bool = False, 
                         interactive: bool = False) -> Optional[Dict[int, str]]:
        """
        Display questions with options, optionally showing correct answers
        
        Args:
            task: Task dictionary
            show_answers: Whether to show correct answers
            interactive: Whether questions are interactive (for student mode)
            
        Returns:
            Dictionary of selected answers if interactive, None otherwise
        """
        questions = task.get('questions', [])
        if not questions:
            st.warning("No questions available")
            return None
        
        st.subheader("❓ Questions")
        
        selected_answers = {}
        
        for i, question in enumerate(questions, 1):
            with st.container():
                st.markdown(f"**Question {i}:** {question.get('question_text', 'Question text missing')}")
                
                options = question.get('options', {})
                correct_answer = question.get('correct_answer')
                
                if interactive:
                    # Interactive mode for students
                    option_keys = [''] + list(options.keys())
                    selected = st.radio(
                        f"Select your answer for Question {i}:",
                        option_keys,
                        format_func=lambda x: f"{x}: {options.get(x, 'Select an option')}" if x else "Select an option",
                        key=f"q_{i}"
                    )
                    if selected:
                        selected_answers[i] = selected
                else:
                    # Display mode
                    for opt_key, opt_text in options.items():
                        if show_answers and opt_key == correct_answer:
                            st.success(f"✅ **{opt_key}**: {opt_text}")
                        else:
                            st.markdown(f"**{opt_key}**: {opt_text}")
                
                if show_answers and correct_answer:
                    st.info(f"**Correct Answer:** {correct_answer}")
                
                if i < len(questions):  # Add separator except for last question
                    st.markdown("---")
        
        return selected_answers if interactive else None
    
    def display_task_summary_card(self, task: Dict[str, Any], show_preview: bool = True) -> None:
        """
        Display a compact task summary card
        
        Args:
            task: Task dictionary
            show_preview: Whether to show text preview
        """
        with st.container():
            # Header row
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{task.get('title', 'Untitled')}**")
                if task.get('topic'):
                    st.caption(f"🎯 {task['topic']}")
            
            with col2:
                word_count = len(task.get('text', '').split())
                st.metric("Words", f"{word_count:,}")
            
            with col3:
                qa_status = self.task_service.get_task_qa_status(task)
                emoji = self.task_service.get_qa_status_emoji(qa_status)
                st.markdown(f"{emoji} {qa_status.title()}")
            
            # Preview text if requested
            if show_preview:
                text = task.get('text', '')
                preview = text[:200] + "..." if len(text) > 200 else text
                st.caption(preview)
    
    def display_batch_statistics(self, tasks: List[Dict[str, Any]]) -> None:
        """
        Display comprehensive statistics for a batch of tasks
        
        Args:
            tasks: List of task dictionaries
        """
        if not tasks:
            st.info("No tasks to analyze")
            return
        
        stats = self.task_service.get_tasks_statistics(tasks)
        
        st.subheader("📊 Batch Statistics")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total Tasks", stats['total_tasks'])
        
        with col2:
            st.metric("📊 Total Words", f"{stats['total_words']:,}")
        
        with col3:
            st.metric("❓ Total Questions", stats['total_questions'])
        
        with col4:
            st.metric("📈 Avg Words/Task", f"{stats['avg_word_count']:.0f}")
        
        # QA Status breakdown
        st.subheader("🔍 QA Status Breakdown")
        qa_counts = stats['qa_status_counts']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Approved", qa_counts['approved'])
        with col2:
            st.metric("❌ Rejected", qa_counts['rejected'])
        with col3:
            st.metric("⏳ Pending", qa_counts['pending'])
    
    def display_task_validation_results(self, task: Dict[str, Any]) -> None:
        """
        Display task validation results with issues and warnings
        
        Args:
            task: Task dictionary to validate
        """
        validation = self.task_service.validate_task_structure(task)
        
        st.subheader("🔍 Task Validation")
        
        # Overall score
        score = validation['score']
        if score >= 90:
            st.success(f"✅ Validation Score: {score}/100 - Excellent!")
        elif score >= 70:
            st.warning(f"⚠️ Validation Score: {score}/100 - Good with minor issues")
        else:
            st.error(f"❌ Validation Score: {score}/100 - Needs attention")
        
        # Issues
        if validation['issues']:
            st.error("**Critical Issues:**")
            for issue in validation['issues']:
                st.error(f"• {issue}")
        
        # Warnings
        if validation['warnings']:
            st.warning("**Warnings:**")
            for warning in validation['warnings']:
                st.warning(f"• {warning}")
        
        if not validation['issues'] and not validation['warnings']:
            st.success("🎉 No issues found! Task is well-structured.")
    
    def display_progress_tracker(self, current: int, total: int, operation: str = "Processing") -> None:
        """
        Display a progress tracker with status
        
        Args:
            current: Current progress
            total: Total items
            operation: Operation description
        """
        if total > 0:
            progress = current / total
            st.progress(progress)
            st.caption(f"{operation}: {current}/{total} ({progress:.1%})")
        else:
            st.info(f"{operation}: No items to process")
    
    def display_task_filters(self) -> Dict[str, Any]:
        """
        Display task filtering controls
        
        Returns:
            Dictionary with filter settings
        """
        st.subheader("🔍 Filter & Sort Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            qa_filter = st.selectbox(
                "QA Status Filter:",
                ["all", "approved", "rejected", "pending"],
                format_func=lambda x: {
                    "all": "📋 All Tasks",
                    "approved": "✅ Approved Only", 
                    "rejected": "❌ Rejected Only",
                    "pending": "⏳ Pending Only"
                }[x]
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort By:",
                ["task_id", "word_count", "questions", "qa_status", "topic", "title"],
                format_func=lambda x: {
                    "task_id": "📝 Task ID",
                    "word_count": "📊 Word Count",
                    "questions": "❓ Question Count", 
                    "qa_status": "🔍 QA Status",
                    "topic": "🎯 Topic",
                    "title": "📖 Title"
                }[x]
            )
        
        with col3:
            sort_order = st.radio("Order:", ["Ascending", "Descending"])
        
        return {
            "qa_filter": qa_filter,
            "sort_by": sort_by,
            "reverse": sort_order == "Descending"
        }
    
    def display_export_options(self, tasks: List[Dict[str, Any]]) -> None:
        """
        Display export options and handle downloads
        
        Args:
            tasks: List of tasks to export
        """
        if not tasks:
            st.info("No tasks to export")
            return
        
        st.subheader("📥 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_name = st.text_input(
                "Export Name:",
                value=f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
        
        with col2:
            if st.button("📦 Generate ZIP Export", type="primary"):
                try:
                    zip_data = self.task_service.export_tasks_batch(tasks, export_name)
                    st.download_button(
                        label="⬇️ Download ZIP File",
                        data=zip_data,
                        file_name=f"{export_name}.zip",
                        mime="application/zip"
                    )
                    st.success(f"✅ Export ready! {len(tasks)} tasks included.")
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    def display_qa_annotation_interface(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Display QA annotation interface for task review
        
        Args:
            task: Task dictionary
            
        Returns:
            Updated QA annotations
        """
        st.subheader("🔍 QA Review Interface")
        
        # Get existing annotations
        qa_annotations = task.get('qa_annotations', {})
        overall_task = qa_annotations.get('overall_task', {})
        
        # Overall task annotation
        col1, col2 = st.columns(2)
        
        with col1:
            overall_status = st.selectbox(
                "Overall Task Status:",
                ["pending", "approved", "rejected"],
                index=["pending", "approved", "rejected"].index(overall_task.get('status', 'pending')),
                format_func=lambda x: f"{self.task_service.get_qa_status_emoji(x)} {x.title()}"
            )
        
        with col2:
            overall_score = st.slider(
                "Quality Score (1-10):",
                min_value=1, max_value=10,
                value=overall_task.get('score', 7)
            )
        
        # Comments
        overall_comments = st.text_area(
            "Review Comments:",
            value=overall_task.get('comments', ''),
            height=100
        )
        
        # Question-specific annotations
        st.subheader("📝 Question-Specific Reviews")
        question_annotations = qa_annotations.get('questions', {})
        
        questions = task.get('questions', [])
        for i, question in enumerate(questions, 1):
            with st.expander(f"Question {i} Review", expanded=False):
                q_key = str(i)
                q_annotation = question_annotations.get(q_key, {})
                
                col1, col2 = st.columns(2)
                with col1:
                    q_status = st.selectbox(
                        f"Q{i} Status:",
                        ["ok", "needs_revision", "problematic"],
                        index=["ok", "needs_revision", "problematic"].index(q_annotation.get('status', 'ok')),
                        key=f"q_status_{i}"
                    )
                
                with col2:
                    q_score = st.slider(
                        f"Q{i} Score:",
                        min_value=1, max_value=10,
                        value=q_annotation.get('score', 7),
                        key=f"q_score_{i}"
                    )
                
                q_comments = st.text_area(
                    f"Q{i} Comments:",
                    value=q_annotation.get('comments', ''),
                    key=f"q_comments_{i}",
                    height=60
                )
                
                question_annotations[q_key] = {
                    'status': q_status,
                    'score': q_score,
                    'comments': q_comments
                }
        
        # Return updated annotations
        return {
            'overall_task': {
                'status': overall_status,
                'score': overall_score,
                'comments': overall_comments,
                'reviewer': 'system',  # Could be made dynamic
                'review_date': datetime.now().isoformat()
            },
            'questions': question_annotations
        }
    
    def display_task_comparison(self, task1: Dict[str, Any], task2: Dict[str, Any]) -> None:
        """
        Display side-by-side comparison of two tasks
        
        Args:
            task1: First task dictionary
            task2: Second task dictionary
        """
        st.subheader("🔍 Task Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Task A")
            self.display_task_header(task1, show_qa_status=True)
            
        with col2:
            st.markdown("### Task B") 
            self.display_task_header(task2, show_qa_status=True)
        
        # Detailed comparison
        st.markdown("### Detailed Comparison")
        
        comparison_data = []
        fields = ['word_count', 'questions', 'topic', 'difficulty']
        
        for field in fields:
            val1 = len(task1.get('text', '').split()) if field == 'word_count' else task1.get(field, 'N/A')
            val1 = len(task1.get('questions', [])) if field == 'questions' else val1
            
            val2 = len(task2.get('text', '').split()) if field == 'word_count' else task2.get(field, 'N/A')
            val2 = len(task2.get('questions', [])) if field == 'questions' else val2
            
            comparison_data.append({
                'Field': field.replace('_', ' ').title(),
                'Task A': val1,
                'Task B': val2,
                'Match': '✅' if val1 == val2 else '❌'
            })
        
        st.table(comparison_data) 