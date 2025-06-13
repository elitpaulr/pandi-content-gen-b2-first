import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Any

# Set page config
st.set_page_config(
    page_title="B2 First - Generated Tasks Browser",
    page_icon="📚",
    layout="wide"
)

def load_generated_tasks() -> List[Dict[str, Any]]:
    """Load all generated tasks from the generated_tasks directory."""
    tasks_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "generated_tasks"
    )
    
    tasks = []
    if os.path.exists(tasks_dir):
        for filename in sorted(os.listdir(tasks_dir)):
            if filename.endswith('.json'):
                filepath = os.path.join(tasks_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        task = json.load(f)
                        tasks.append(task)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    st.error(f"Error loading {filename}: {str(e)}")
    
    return tasks

def display_task_overview(tasks: List[Dict[str, Any]]):
    """Display an overview of all tasks."""
    st.subheader("📊 Tasks Overview")
    
    if not tasks:
        st.warning("No tasks found. Please generate some tasks first.")
        return
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tasks", len(tasks))
    
    with col2:
        topics = [task.get("topic", "unknown") for task in tasks]
        unique_topics = len(set(topics))
        st.metric("Unique Topics", unique_topics)
    
    with col3:
        avg_word_count = sum(task.get("metadata", {}).get("word_count", 0) for task in tasks) / len(tasks)
        st.metric("Avg Word Count", f"{avg_word_count:.0f}")
    
    with col4:
        total_questions = sum(len(task.get("questions", [])) for task in tasks)
        st.metric("Total Questions", total_questions)
    
    # Topic distribution
    st.subheader("📈 Topic Distribution")
    topic_counts = {}
    for task in tasks:
        topic = task.get("topic", "unknown")
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    for topic, count in topic_counts.items():
        st.write(f"**{topic.replace('_', ' ').title()}**: {count} tasks")

def display_task_details(task: Dict[str, Any], show_answers: bool = False):
    """Display detailed view of a single task."""
    st.header(f"📖 {task.get('title', 'Untitled Task')}")
    
    # Task metadata
    with st.expander("ℹ️ Task Information"):
        metadata = task.get("metadata", {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write(f"**Task ID:** {task.get('task_id', 'N/A')}")
        with col2:
            st.write(f"**Topic:** {task.get('topic', 'N/A').replace('_', ' ').title()}")
        with col3:
            st.write(f"**Word Count:** {metadata.get('word_count', 'N/A')}")
        with col4:
            st.write(f"**Estimated Time:** {metadata.get('estimated_time', 'N/A')}")
        
        if "question_types_used" in metadata:
            st.write("**Question Types:**")
            for q_type in metadata["question_types_used"]:
                st.write(f"- {q_type.replace('_', ' ').title()}")
    
    # Main content area
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Display the text
        st.subheader("📄 Reading Text")
        st.markdown(task.get("text", "No text available"))
    
    with col2:
        # Display questions
        st.subheader("❓ Questions")
        questions = task.get("questions", [])
        
        if not questions:
            st.warning("No questions available for this task.")
            return
        
        # Track user answers
        user_answers = {}
        
        for i, question in enumerate(questions):
            st.markdown(f"**{question.get('id', i+1)}. {question.get('question', 'No question text')}**")
            
            options = question.get("options", [])
            if options:
                # Create radio buttons for options
                selected_option = st.radio(
                    f"Select answer for question {question.get('id', i+1)}",
                    options,
                    key=f"q{question.get('id', i+1)}_{task.get('task_id', '')}"
                )
                
                user_answers[question.get('id', i+1)] = selected_option
                
                # Show correct answer if requested
                if show_answers:
                    correct_idx = question.get("correct_answer", 0)
                    correct_answer = options[correct_idx] if correct_idx < len(options) else "Unknown"
                    
                    if selected_option == correct_answer:
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. The correct answer is: {correct_answer}")
                    
                    # Show question type
                    q_type = question.get("question_type", "unknown")
                    st.caption(f"Question type: {q_type.replace('_', ' ').title()}")
            else:
                st.warning("No options available for this question.")
            
            st.markdown("---")
        
        # Score calculation when showing answers
        if show_answers and questions:
            correct_count = 0
            for question in questions:
                q_id = question.get('id')
                if q_id in user_answers:
                    correct_idx = question.get("correct_answer", 0)
                    options = question.get("options", [])
                    if correct_idx < len(options):
                        correct_answer = options[correct_idx]
                        if user_answers[q_id] == correct_answer:
                            correct_count += 1
            
            score_percentage = (correct_count / len(questions)) * 100
            st.subheader("📊 Your Score")
            st.metric("Score", f"{correct_count}/{len(questions)} ({score_percentage:.1f}%)")

def main():
    st.title("📚 B2 First - Generated Tasks Browser")
    
    # Load all tasks
    tasks = load_generated_tasks()
    
    if not tasks:
        st.error("No generated tasks found. Please run the task generator first.")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # View mode selection
    view_mode = st.sidebar.selectbox(
        "Select View Mode",
        ["Overview", "Task Details"]
    )
    
    if view_mode == "Overview":
        display_task_overview(tasks)
        
        # Show task list
        st.subheader("📋 All Tasks")
        for task in tasks:
            with st.expander(f"{task.get('title', 'Untitled')} - {task.get('topic', 'unknown').replace('_', ' ').title()}"):
                metadata = task.get("metadata", {})
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Word Count:** {metadata.get('word_count', 'N/A')}")
                    st.write(f"**Questions:** {len(task.get('questions', []))}")
                with col2:
                    st.write(f"**Task ID:** {task.get('task_id', 'N/A')}")
                    st.write(f"**Time:** {metadata.get('estimated_time', 'N/A')}")
    
    elif view_mode == "Task Details":
        # Task selection
        task_options = [f"{task.get('task_id', f'task_{i}')} - {task.get('topic', 'unknown').replace('_', ' ').title()}" 
                       for i, task in enumerate(tasks)]
        
        selected_task_idx = st.sidebar.selectbox(
            "Select a Task",
            range(len(tasks)),
            format_func=lambda x: task_options[x]
        )
        
        # Show/hide answers toggle
        show_answers = st.sidebar.checkbox("Show Answers")
        
        # Display selected task
        if 0 <= selected_task_idx < len(tasks):
            display_task_details(tasks[selected_task_idx], show_answers)
    
    # Footer with statistics
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Quick Stats")
    st.sidebar.write(f"Total Tasks: {len(tasks)}")
    if tasks:
        topics = set(task.get("topic", "unknown") for task in tasks)
        st.sidebar.write(f"Topics: {len(topics)}")
        total_questions = sum(len(task.get("questions", [])) for task in tasks)
        st.sidebar.write(f"Total Questions: {total_questions}")

if __name__ == "__main__":
    main() 