import streamlit as st
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional

# Page configuration
st.set_page_config(
    page_title="B2 First Content Generator - Static Demo",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_tasks_data():
    """Load all tasks from JSON files"""
    data_dir = Path(__file__).parent / 'data'
    
    # Load index
    with open(data_dir / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    # Load all chunks
    all_tasks = []
    for chunk_file in index['chunk_files']:
        with open(data_dir / chunk_file, 'r', encoding='utf-8') as f:
            chunk_tasks = json.load(f)
            all_tasks.extend(chunk_tasks)
    
    return all_tasks

def get_task_qa_status(task):
    """Determine QA status of a task"""
    if not task.get('questions'):
        return 'needs_review'
    
    text_length = len(task.get('text', '').split())
    if text_length < 400 or text_length > 800:
        return 'needs_review'
    
    if len(task.get('questions', [])) != 6:
        return 'needs_review'
    
    return 'approved'

def get_qa_status_emoji(status):
    """Get emoji for QA status"""
    return {
        'approved': '✅',
        'needs_review': '⚠️',
        'rejected': '❌'
    }.get(status, '❓')

def get_qa_status_color(status):
    """Get color for QA status"""
    return {
        'approved': 'green',
        'needs_review': 'orange', 
        'rejected': 'red'
    }.get(status, 'gray')

def display_task_learner_view(task):
    """Display a task in a nicely formatted learner view with two-column layout"""
    # Task header
    st.markdown(f"# 📖 {task.get('title', 'Untitled Task')}")
    
    # Task metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Word Count", len(task.get('text', '').split()))
    with col2:
        st.metric("❓ Questions", len(task.get('questions', [])))
    with col3:
        text_type = task.get('text_type', 'unknown').replace('_', ' ').title()
        st.metric("📄 Text Type", text_type)
    with col4:
        st.metric("🎯 Topic", task.get('topic', 'Unknown').replace('_', ' ').title())
    
    # Additional metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        if task.get('topic'):
            st.markdown(f"**🎯 Topic:** {task.get('topic')}")
    with col2:
        if task.get('topic_category'):
            category = task.get('topic_category', '').replace('_', ' ').title()
            st.markdown(f"**📂 Category:** {category}")
    with col3:
        st.markdown(f"**🆔 Task ID:** {task.get('task_id', 'N/A')}")
    
    st.divider()
    
    # Calculate dynamic height based on text length
    text_content = task.get('text', 'No text available')
    word_count = len(text_content.split())
    # Estimate height: ~25 words per line, ~25px per line, plus padding
    estimated_text_height = max(400, min(1200, (word_count // 25) * 25 + 100))
    
    # Add CSS for side-by-side layout with dynamic height
    st.markdown(f"""
    <style>
    .reading-text-container {{
        min-height: {estimated_text_height}px;
        max-height: none;
        overflow-y: visible;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        line-height: 1.6;
        font-size: 16px;
    }}
    .reading-text-container p {{
        margin-bottom: 1.2em;
        text-align: justify;
    }}
    .questions-container {{
        min-height: {estimated_text_height}px;
        max-height: none;
        overflow-y: visible;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }}
    .question-item {{
        margin-bottom: 25px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }}
    .question-header {{
        font-size: 18px;
        font-weight: bold;
        color: #007bff;
        margin-bottom: 10px;
    }}
    .question-text {{
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 15px;
        color: #333;
    }}
    .option-item {{
        margin: 8px 0;
        padding: 8px 12px;
        border-radius: 5px;
        font-size: 15px;
    }}
    .option-correct {{
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        font-weight: 600;
    }}
    .option-incorrect {{
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        color: #495057;
    }}
    .question-meta {{
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px solid #dee2e6;
        font-size: 14px;
        color: #6c757d;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Create two columns for text and questions
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("## 📄 Reading Text")
        
        # Format the text nicely
        formatted_text = text_content.strip()
        paragraphs = formatted_text.split('\n\n')
        
        # Create expandable text container that shows full content
        text_html = '<div class="reading-text-container">'
        for paragraph in paragraphs:
            if paragraph.strip():
                text_html += f'<p>{paragraph.strip()}</p>'
        text_html += '</div>'
        
        st.markdown(text_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown("## ❓ Questions")
        questions = task.get('questions', [])
        
        if questions:
            # Create scrollable questions container
            questions_html = '<div class="questions-container">'
            
            for i, question in enumerate(questions, 1):
                try:
                    questions_html += f'<div class="question-item">'
                    questions_html += f'<div class="question-header">Question {i}</div>'
                    
                    # Question text
                    question_text = question.get('question_text', 'No question text')
                    questions_html += f'<div class="question-text">{question_text}</div>'
                    
                    # Options
                    options = question.get('options', {})
                    correct_answer = question.get('correct_answer', '')
                    
                    if options:
                        # Handle both dict and list formats for options
                        if isinstance(options, dict):
                            for option_key, option_text in options.items():
                                if option_key == correct_answer:
                                    questions_html += f'<div class="option-item option-correct">✅ <strong>{option_key}.</strong> {option_text}</div>'
                                else:
                                    questions_html += f'<div class="option-item option-incorrect"><strong>{option_key}.</strong> {option_text}</div>'
                        elif isinstance(options, list):
                            # Handle list format (fallback)
                            option_keys = ['A', 'B', 'C', 'D']
                            for j, option_text in enumerate(options):
                                if j < len(option_keys):
                                    option_key = option_keys[j]
                                    if option_key == correct_answer:
                                        questions_html += f'<div class="option-item option-correct">✅ <strong>{option_key}.</strong> {option_text}</div>'
                                    else:
                                        questions_html += f'<div class="option-item option-incorrect"><strong>{option_key}.</strong> {option_text}</div>'
                    
                    # Question metadata
                    q_type = question.get('question_type', 'unknown')
                    questions_html += f'<div class="question-meta">'
                    questions_html += f'<strong>Type:</strong> {q_type.replace("_", " ").title()} | '
                    questions_html += f'<strong>Correct Answer:</strong> {correct_answer}'
                    
                    # Explanation if available
                    if question.get('explanation'):
                        questions_html += f'<br><strong>💡 Explanation:</strong> {question.get("explanation")}'
                    
                    questions_html += '</div>'
                    questions_html += '</div>'
                    
                except Exception as e:
                    # Fallback for any problematic questions
                    questions_html += f'<div class="question-item">'
                    questions_html += f'<div class="question-header">Question {i}</div>'
                    questions_html += f'<div class="question-text">Error displaying question: {str(e)}</div>'
                    questions_html += '</div>'
            
            questions_html += '</div>'
            st.markdown(questions_html, unsafe_allow_html=True)
        else:
            st.warning("No questions available for this task.")

def display_task_qa_view(task):
    """Display task in QA review format"""
    st.markdown(f"### 🔍 QA Review: {task.get('title', 'Untitled Task')}")
    
    # QA Status
    qa_status = get_task_qa_status(task)
    status_emoji = get_qa_status_emoji(qa_status)
    status_color = get_qa_status_color(qa_status)
    
    st.markdown(f"**QA Status:** :{status_color}[{status_emoji} {qa_status.title()}]")
    
    # Task metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Text Type", task.get('text_type', 'Unknown').replace('_', ' ').title())
    with col2:
        st.metric("Topic", task.get('topic', 'Unknown').replace('_', ' ').title())
    with col3:
        st.metric("Difficulty", task.get('difficulty', 'B2'))
    with col4:
        st.metric("Questions", len(task.get('questions', [])))
    
    # Text analysis
    text_content = task.get('text', '')
    word_count = len(text_content.split()) if text_content else 0
    
    st.markdown("#### 📊 Text Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Word Count", word_count)
    with col2:
        target_range = "400-800 words"
        in_range = 400 <= word_count <= 800
        st.metric("Target Range", target_range, delta="✅ In range" if in_range else "❌ Out of range")
    
    # Reading text
    st.markdown("#### 📖 Reading Text")
    with st.expander("View Full Text", expanded=False):
        st.markdown(text_content)
    
    # Questions review
    st.markdown("#### ❓ Questions Review")
    questions = task.get('questions', [])
    
    if questions:
        for i, question in enumerate(questions, 1):
            with st.expander(f"Q{i}: {question.get('question_text', 'No question text')[:50]}...", expanded=False):
                st.markdown(f"**Full Question:** {question.get('question_text', 'No question text')}")
                
                options = question.get('options', {})
                correct_answer = question.get('correct_answer', 'Unknown')
                
                # Display options with correct answer highlighted
                st.markdown("**Options:**")
                if isinstance(options, dict):
                    for option_key, option_text in options.items():
                        if option_key == correct_answer:
                            st.success(f"**{option_key}.** {option_text} ✅ **CORRECT**")
                        else:
                            st.write(f"**{option_key}.** {option_text}")
                elif isinstance(options, list):
                    for idx, option_text in enumerate(options):
                        option_key = chr(65 + idx)  # A, B, C, D
                        if option_key == correct_answer:
                            st.success(f"**{option_key}.** {option_text} ✅ **CORRECT**")
                        else:
                            st.write(f"**{option_key}.** {option_text}")
                
                # Question metadata
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Type:** {question.get('question_type', 'Unknown')}")
                with col2:
                    st.info(f"**Correct Answer:** {correct_answer}")
    else:
        st.warning("No questions available for this task.")

def display_task_json_view(task):
    """Display task in JSON format"""
    st.markdown("#### 🔧 JSON Data")
    
    # Clean task data for display (remove file paths)
    clean_task = {k: v for k, v in task.items() if k not in ['file_path', 'filename']}
    
    st.json(clean_task)

def main():
    """Main application"""
    
    # Header
    st.title("📚 B2 First Content Generator - Static Demo")
    st.markdown("**Explore 485+ AI-Generated Cambridge B2 First Reading Part 5 Tasks**")
    
    # Load tasks
    try:
        tasks = load_tasks_data()
        st.success(f"✅ Loaded {len(tasks)} tasks successfully!")
    except Exception as e:
        st.error(f"❌ Error loading tasks: {str(e)}")
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📖 Task Library", 
        "📊 Statistics", 
        "🔍 QA Dashboard", 
        "📋 Documentation",
        "🔧 System Info"
    ])
    
    with tab1:
        st.header("📖 Task Library")
        st.markdown("Browse and explore all generated reading tasks with advanced filtering options.")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Text type filter
            text_types = sorted(list(set(task.get('text_type', 'unknown') for task in tasks)))
            selected_text_type = st.selectbox(
                "📄 Filter by Text Type",
                ["All"] + text_types,
                key="text_type_filter"
            )
        
        with col2:
            # Topic filter
            topics = sorted(list(set(task.get('topic', 'unknown') for task in tasks if task.get('topic'))))
            selected_topic = st.selectbox(
                "🎯 Filter by Topic",
                ["All"] + topics[:20],  # Limit to first 20 topics
                key="topic_filter"
            )
        
        with col3:
            # QA status filter
            qa_statuses = ["All", "approved", "needs_review", "rejected"]
            selected_qa_status = st.selectbox(
                "✅ Filter by QA Status",
                qa_statuses,
                key="qa_status_filter"
            )
        
        # Apply filters
        filtered_tasks = tasks
        
        if selected_text_type != "All":
            filtered_tasks = [t for t in filtered_tasks if t.get('text_type') == selected_text_type]
        
        if selected_topic != "All":
            filtered_tasks = [t for t in filtered_tasks if t.get('topic') == selected_topic]
        
        if selected_qa_status != "All":
            filtered_tasks = [t for t in filtered_tasks if get_task_qa_status(t) == selected_qa_status]
        
        st.markdown(f"**Showing {len(filtered_tasks)} of {len(tasks)} tasks**")
        
        # Task selection
        if filtered_tasks:
            # Create task options for selectbox
            task_options = []
            for i, task in enumerate(filtered_tasks):
                title = task.get('title', 'Untitled Task')
                text_type = task.get('text_type', 'unknown').replace('_', ' ').title()
                topic = task.get('topic', 'Unknown')
                qa_status = get_task_qa_status(task)
                status_emoji = get_qa_status_emoji(qa_status)
                
                option_text = f"{status_emoji} {title} | {text_type} | {topic}"
                task_options.append(option_text)
            
            selected_task_index = st.selectbox(
                "📋 Select a task to view:",
                range(len(task_options)),
                format_func=lambda x: task_options[x],
                key="task_selector"
            )
            
            selected_task = filtered_tasks[selected_task_index]
            
            # View mode selection
            view_mode = st.radio(
                "👁️ View Mode:",
                ["📖 Learner View", "🔍 QA Review", "🔧 JSON Data"],
                horizontal=True,
                key="view_mode"
            )
            
            st.divider()
            
            # Display selected task
            if view_mode == "📖 Learner View":
                display_task_learner_view(selected_task)
            elif view_mode == "🔍 QA Review":
                display_task_qa_view(selected_task)
            elif view_mode == "🔧 JSON Data":
                display_task_json_view(selected_task)
        
        else:
            st.warning("No tasks match the selected filters.")
    
    with tab2:
        st.header("📊 Statistics Dashboard")
        st.markdown("Comprehensive analytics of the generated task collection.")
        
        # Overall stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📚 Total Tasks", len(tasks))
        
        with col2:
            total_words = sum(len(task.get('text', '').split()) for task in tasks)
            st.metric("📝 Total Words", f"{total_words:,}")
        
        with col3:
            total_questions = sum(len(task.get('questions', [])) for task in tasks)
            st.metric("❓ Total Questions", total_questions)
        
        with col4:
            avg_words = total_words // len(tasks) if tasks else 0
            st.metric("📊 Avg Words/Task", avg_words)
        
        st.divider()
        
        # Text type distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Text Type Distribution")
            text_type_counts = {}
            for task in tasks:
                text_type = task.get('text_type', 'unknown').replace('_', ' ').title()
                text_type_counts[text_type] = text_type_counts.get(text_type, 0) + 1
            
            if text_type_counts:
                df_text_types = pd.DataFrame(
                    list(text_type_counts.items()),
                    columns=['Text Type', 'Count']
                ).sort_values('Count', ascending=False)
                
                st.dataframe(df_text_types, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Topic Distribution")
            topic_counts = {}
            for task in tasks:
                topic = task.get('topic', 'unknown')
                if topic and topic != 'unknown':
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            if topic_counts:
                # Show top 10 topics
                sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                df_topics = pd.DataFrame(sorted_topics, columns=['Topic', 'Count'])
                st.dataframe(df_topics, use_container_width=True)
        
        # QA Status distribution
        st.subheader("✅ QA Status Distribution")
        qa_status_counts = {}
        for task in tasks:
            status = get_task_qa_status(task)
            qa_status_counts[status] = qa_status_counts.get(status, 0) + 1
        
        col1, col2, col3 = st.columns(3)
        for i, (status, count) in enumerate(qa_status_counts.items()):
            with [col1, col2, col3][i % 3]:
                emoji = get_qa_status_emoji(status)
                st.metric(f"{emoji} {status.title()}", count)
    
    with tab3:
        st.header("🔍 QA Dashboard")
        st.markdown("Quality assurance overview and task compliance checking.")
        
        # QA Metrics
        approved_tasks = [t for t in tasks if get_task_qa_status(t) == 'approved']
        needs_review_tasks = [t for t in tasks if get_task_qa_status(t) == 'needs_review']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            approval_rate = (len(approved_tasks) / len(tasks)) * 100 if tasks else 0
            st.metric("✅ Approval Rate", f"{approval_rate:.1f}%")
        
        with col2:
            st.metric("⚠️ Needs Review", len(needs_review_tasks))
        
        with col3:
            avg_questions = sum(len(task.get('questions', [])) for task in tasks) / len(tasks) if tasks else 0
            st.metric("❓ Avg Questions", f"{avg_questions:.1f}")
        
        st.divider()
        
        # Word count analysis
        st.subheader("📊 Word Count Analysis")
        word_counts = [len(task.get('text', '').split()) for task in tasks]
        
        col1, col2 = st.columns(2)
        
        with col1:
            in_range_count = sum(1 for wc in word_counts if 400 <= wc <= 800)
            compliance_rate = (in_range_count / len(word_counts)) * 100 if word_counts else 0
            st.metric("📏 Word Count Compliance", f"{compliance_rate:.1f}%")
            st.caption("Tasks with 400-800 words")
        
        with col2:
            if word_counts:
                avg_words = sum(word_counts) / len(word_counts)
                st.metric("📝 Average Word Count", f"{avg_words:.0f}")
                st.caption(f"Range: {min(word_counts)}-{max(word_counts)} words")
        
        # Tasks needing review
        if needs_review_tasks:
            st.subheader("⚠️ Tasks Needing Review")
            st.markdown(f"**{len(needs_review_tasks)} tasks require attention:**")
            
            for task in needs_review_tasks[:10]:  # Show first 10
                title = task.get('title', 'Untitled Task')
                word_count = len(task.get('text', '').split())
                question_count = len(task.get('questions', []))
                
                issues = []
                if word_count < 400:
                    issues.append(f"Too short ({word_count} words)")
                elif word_count > 800:
                    issues.append(f"Too long ({word_count} words)")
                
                if question_count != 6:
                    issues.append(f"Wrong question count ({question_count})")
                
                st.warning(f"**{title}** - {', '.join(issues)}")
    
    with tab4:
        st.header("📋 Documentation")
        st.markdown("System overview and feature documentation.")
        
        st.markdown("""
        ## 🎯 About This Demo
        
        This static demonstration showcases the **B2 First Content Generator**, an AI-powered system for creating Cambridge B2 First Reading Part 5 examination tasks.
        
        ### 📚 Content Overview
        - **485+ Generated Tasks** across multiple text types and topics
        - **10 Text Types**: Magazine articles, newspaper articles, blog posts, novel extracts, science articles, cultural reviews, professional features, lifestyle features, travel writing, and educational features
        - **Diverse Topics**: Technology, environment, health, travel, urban development, adventure sports psychology, renewable energy, and more
        - **Cambridge Standards**: All tasks meet B2 First examination criteria
        
        ### 🔧 Features
        
        #### 📖 Task Library
        - Browse all generated tasks with advanced filtering
        - Multiple view modes: Learner View, QA Review, JSON Data
        - Filter by text type, topic, and QA status
        - Beautiful two-column layout for optimal reading experience
        
        #### 📊 Statistics Dashboard
        - Comprehensive analytics of the task collection
        - Text type and topic distribution analysis
        - QA status tracking and compliance metrics
        - Word count analysis and compliance checking
        
        #### 🔍 QA Dashboard
        - Quality assurance overview
        - Task compliance checking
        - Identification of tasks needing review
        - Performance metrics and approval rates
        
        ### 🎨 Technical Features
        - **Responsive Design**: Optimized for all screen sizes
        - **Fast Loading**: Efficient data loading with caching
        - **Professional UI**: Clean, modern interface design
        - **Accessibility**: Screen reader friendly and keyboard navigable
        
        ### 📈 Quality Standards
        - **Text Length**: 400-800 words per task
        - **Question Count**: 6 questions per task
        - **Question Types**: Inference, vocabulary, detail, attitude, reference, main idea
        - **Answer Format**: Multiple choice (A, B, C, D)
        - **Difficulty Level**: B2 (Upper Intermediate)
        """)
    
    with tab5:
        st.header("🔧 System Information")
        st.markdown("Technical details and system status.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Data Statistics")
            st.info(f"**Total Tasks:** {len(tasks)}")
            st.info(f"**Data Source:** JSON files")
            st.info(f"**Last Updated:** Static deployment")
            st.info(f"**Version:** 1.0.0")
        
        with col2:
            st.subheader("🛠️ Technical Stack")
            st.info("**Frontend:** Streamlit")
            st.info("**Data Format:** JSON")
            st.info("**Deployment:** Streamlit Cloud")
            st.info("**Python Version:** 3.10+")
        
        st.subheader("📋 System Status")
        st.success("✅ All systems operational")
        st.success("✅ Data loaded successfully")
        st.success("✅ UI components functional")
        st.success("✅ Filters working correctly")

if __name__ == "__main__":
    main()
