#!/usr/bin/env python3
"""
Streamlit Cloud Deployment Version - B2 First Task Generator
This version disables LLM integration for cloud deployment while keeping UI visible
"""

import streamlit as st
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import time
from datetime import datetime
import random

# Add src to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"

# Method 1: Add src directory to path
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Method 2: Add project root to path as backup
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import services (these should work without Ollama)
try:
    from services.config_service import ConfigService
    from services.task_service import TaskService
    from services.ui_components import UIComponents
except ImportError:
    # Fallback import path
    import sys
    sys.path.append(str(Path(__file__).parent))
    from services.config_service import ConfigService
    from services.task_service import TaskService
    from services.ui_components import UIComponents

# Initialize services
config_service = ConfigService(project_root)
task_service = TaskService(project_root / "generated_tasks")
ui_components = UIComponents(task_service, config_service)

# Get configurations
B2_TEXT_TYPES = config_service.get_b2_text_types()
TOPIC_CATEGORIES = config_service.get_topic_categories()
TOPIC_SETS = config_service.get_topic_sets()

# Page configuration
st.set_page_config(
    page_title="B2 First Task Generator - Demo",
    page_icon="🤖",
    layout="wide"
)

def main():
    st.title("🤖 B2 First Task Generator - Demo Mode")
    st.markdown("**Demo Version** - LLM generation disabled for cloud deployment")
    
    # Demo mode notice
    st.warning("""
    🚧 **Demo Mode Active**
    
    This is a demonstration version of the B2 First Task Generator. 
    LLM integration and task generation features are disabled for cloud deployment.
    
    **Available Features:**
    - ✅ Browse existing tasks and batches
    - ✅ View task library with filtering
    - ✅ QA review interface
    - ✅ Task export and download
    - ❌ Task generation (requires local Ollama)
    - ❌ Batch generation (requires local Ollama)
    """)
    
    # Sidebar configuration (disabled)
    st.sidebar.header("🔧 Configuration")
    st.sidebar.info("**Demo Mode** - Configuration disabled")
    
    # Disabled model selection
    st.sidebar.selectbox(
        "Select Model",
        ["llama3.1:8b (Demo)"],
        disabled=True,
        help="Model selection disabled in demo mode"
    )
    
    # Disabled generation parameters
    st.sidebar.subheader("Generation Parameters")
    st.sidebar.slider("Temperature", 0.1, 1.0, 0.7, 0.1, disabled=True)
    st.sidebar.slider("Max Tokens", 1000, 4000, 2000, 100, disabled=True)
    
    # Auto-save option
    st.sidebar.subheader("💾 Save Settings")
    st.sidebar.info("Auto-save disabled in demo mode")
    
    # Main interface tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Generate Tasks", "🔧 Improve Tasks", "📊 Batch Generation", "📚 Task Library", "⚙️ Admin Panel", "📖 Docs"])
    
    with tab1:
        st.header("Generate Single Task")
        st.info("🚧 **Task Generation Disabled**")
        st.markdown("""
        Task generation requires a local Ollama installation and is not available in this demo version.
        
        **To enable task generation:**
        1. Install Ollama locally: https://ollama.ai/
        2. Start Ollama: `ollama serve`
        3. Pull a model: `ollama pull llama3.1:8b`
        4. Run the full version locally
        """)
        
        # Disabled form inputs
        topic = st.text_input(
            "Task Topic",
            placeholder="e.g., sustainable travel and eco-tourism",
            disabled=True,
            help="Disabled in demo mode"
        )
        
        text_type_options = config_service.get_text_type_options()
        selected_text_type = st.selectbox(
            "Text Type",
            text_type_options,
            index=0,
            disabled=True,
            help="Disabled in demo mode"
        )
        
        custom_instructions = st.text_area(
            "Custom Instructions (Optional)",
            placeholder="Any specific requirements or focus areas...",
            height=100,
            disabled=True,
            help="Disabled in demo mode"
        )
        
        # Disabled generate button
        if st.button("🚀 Generate Task", type="primary", disabled=True):
            st.info("Generation disabled in demo mode")
    
    with tab2:
        st.header("🔧 Improve Existing Tasks")
        st.info("🚧 **Task Improvement Disabled**")
        st.markdown("Task improvement requires LLM integration and is not available in demo mode.")
    
    with tab3:
        st.header("Batch Generation")
        st.info("🚧 **Batch Generation Disabled**")
        st.markdown("""
        Batch generation requires a local Ollama installation and is not available in this demo version.
        
        **Available in full version:**
        - Generate multiple tasks efficiently
        - Batch processing with progress tracking
        - Auto-save in organized folders
        - Comprehensive batch summaries
        """)
        
        # Show disabled batch interface
        st.subheader("📝 Text Types")
        st.markdown("Select which text types to include in batch generation:")
        
        cols = st.columns(3)
        for i, (text_type_name, text_type_info) in enumerate(B2_TEXT_TYPES.items()):
            col_idx = i % 3
            with cols[col_idx]:
                st.checkbox(
                    text_type_name, 
                    value=(i < 3),
                    disabled=True,
                    key=f"demo_batch_text_type_{text_type_info['key']}"
                )
        
        st.subheader("📚 Topics")
        st.selectbox("Choose Topic Set", list(config_service.get_topic_sets().keys()), disabled=True)
        
        st.slider("Tasks per Topic", 1, 3, 1, disabled=True)
        
        if st.button("🚀 Start Batch Generation", type="primary", disabled=True):
            st.info("Batch generation disabled in demo mode")
    
    with tab4:
        st.header("📚 Task Library")
        
        # Load and display all generated tasks and batches
        generated_tasks_dir = Path(__file__).parent.parent / "generated_tasks"
        if generated_tasks_dir.exists():
            # Get individual task files and batch directories
            task_files = list(generated_tasks_dir.glob("*.json"))
            batch_dirs = [d for d in generated_tasks_dir.iterdir() if d.is_dir() and d.name.startswith("batch_")]
            
            if not task_files and not batch_dirs:
                st.info("No tasks found. Generate some tasks first!")
                return
            
            # Quick Stats Dashboard
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📄 Individual Tasks", len(task_files))
            with col2:
                st.metric("📦 Batch Collections", len(batch_dirs))
            with col3:
                # Calculate total tasks in batches
                total_batch_tasks = sum(len(list(batch_dir.glob("*.json"))) for batch_dir in batch_dirs)
                st.metric("🎯 Total Tasks", len(task_files) + total_batch_tasks)
            with col4:
                # Calculate storage size
                total_size = sum(f.stat().st_size for f in task_files)
                for batch_dir in batch_dirs:
                    total_size += sum(f.stat().st_size for f in batch_dir.rglob("*.json"))
                size_mb = total_size / (1024 * 1024)
                st.metric("💾 Storage", f"{size_mb:.1f} MB")
            
            st.divider()
            
            # Main selection interface
            st.subheader("🎯 Select Content to View")
            
            # Create selection options
            col1, col2 = st.columns([2, 1])
            
            with col1:
                content_type = st.selectbox(
                    "Content Type",
                    ["📄 Individual Tasks", "📦 Batch Collections"],
                    index=0,
                    key="content_type_selector"
                )
            
            with col2:
                view_mode = st.selectbox(
                    "View Mode",
                    ["🎓 Learner View", "📋 Summary", "🔧 Full Details", "🔍 QA Review"],
                    index=0,
                    key="main_view_mode"
                )
            
            st.divider()
            
            # Individual Tasks Section
            if content_type == "📄 Individual Tasks":
                if not task_files:
                    st.info("No individual tasks found.")
                    return
                
                # Load all task data for filtering and sorting
                tasks_data = []
                for task_file in task_files:
                    try:
                        with open(task_file, 'r') as f:
                            task = json.load(f)
                            task['filename'] = task_file.name
                            task['file_path'] = str(task_file)
                            task['word_count'] = len(task.get('text', '').split())
                            tasks_data.append(task)
                    except Exception as e:
                        st.warning(f"Could not load {task_file.name}: {e}")
                
                if not tasks_data:
                    st.error("No valid tasks could be loaded.")
                    return
                
                # Filter and sort controls
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    # Topic filter
                    all_topics = sorted(set(task.get('topic_category', 'Unknown') for task in tasks_data))
                    topic_filter = st.selectbox(
                        "Filter by Topic",
                        ["All Topics"] + all_topics,
                        index=0,
                        key="individual_topic_filter"
                    )
                
                with col2:
                    # Text type filter
                    all_text_types = sorted(set(task.get('text_type', 'Unknown') for task in tasks_data))
                    text_type_filter = st.selectbox(
                        "Filter by Text Type",
                        ["All Types"] + all_text_types,
                        index=0,
                        key="individual_text_type_filter"
                    )
                
                with col3:
                    # QA Status filter
                    qa_status_filter = st.selectbox(
                        "Filter by QA Status",
                        ["All Status", "⏳ Pending", "✅ Approved", "❌ Rejected"],
                        index=0,
                        key="individual_qa_status_filter"
                    )
                
                with col4:
                    # Sort options
                    sort_option = st.selectbox(
                        "Sort by",
                        ["Task ID ↑", "Task ID ↓", "Title A-Z", "Title Z-A", "Word Count ↑", "Word Count ↓", "Recent First", "QA Status"],
                        index=0,
                        key="individual_sort_option"
                    )
                
                with col5:
                    # Search
                    search_term = st.text_input(
                        "Search",
                        placeholder="Search titles, topics...",
                        key="individual_search"
                    )
                
                # Apply filters
                filtered_tasks = tasks_data.copy()
                
                if topic_filter != "All Topics":
                    filtered_tasks = [task for task in filtered_tasks if task.get('topic_category') == topic_filter]
                
                if text_type_filter != "All Types":
                    filtered_tasks = [task for task in filtered_tasks if task.get('text_type') == text_type_filter]
                
                if qa_status_filter != "All Status":
                    status_map = {"⏳ Pending": "pending", "✅ Approved": "approved", "❌ Rejected": "rejected"}
                    target_status = status_map.get(qa_status_filter, "pending")
                    filtered_tasks = [task for task in filtered_tasks if task_service.get_task_qa_status(task) == target_status]
                
                if search_term:
                    search_lower = search_term.lower()
                    filtered_tasks = [task for task in filtered_tasks 
                                    if search_lower in task.get('title', '').lower() 
                                    or search_lower in task.get('topic', '').lower()]
                
                # Apply sorting
                if sort_option == "Task ID ↑":
                    filtered_tasks.sort(key=lambda x: x.get('task_id', ''))
                elif sort_option == "Task ID ↓":
                    filtered_tasks.sort(key=lambda x: x.get('task_id', ''), reverse=True)
                elif sort_option == "Title A-Z":
                    filtered_tasks.sort(key=lambda x: x.get('title', ''))
                elif sort_option == "Title Z-A":
                    filtered_tasks.sort(key=lambda x: x.get('title', ''), reverse=True)
                elif sort_option == "Word Count ↑":
                    filtered_tasks.sort(key=lambda x: x.get('word_count', 0))
                elif sort_option == "Word Count ↓":
                    filtered_tasks.sort(key=lambda x: x.get('word_count', 0), reverse=True)
                elif sort_option == "Recent First":
                    filtered_tasks.sort(key=lambda x: x.get('file_path', ''), reverse=True)
                elif sort_option == "QA Status":
                    filtered_tasks.sort(key=lambda x: task_service.get_task_qa_status(x))
                
                # Display filtered results
                st.subheader(f"📋 Filtered Results ({len(filtered_tasks)} tasks)")
                
                # Quick metrics
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                    st.metric("📄 Total", len(filtered_tasks))
                with col2:
                    approved_count = sum(1 for task in filtered_tasks if task_service.get_task_qa_status(task) == 'approved')
                    st.metric("✅ Approved", approved_count)
                with col3:
                    pending_count = sum(1 for task in filtered_tasks if task_service.get_task_qa_status(task) == 'pending')
                    st.metric("⏳ Pending", pending_count)
                with col4:
                    rejected_count = sum(1 for task in filtered_tasks if task_service.get_task_qa_status(task) == 'rejected')
                    st.metric("❌ Rejected", rejected_count)
                with col5:
                    if filtered_tasks:
                        avg_words = sum(task.get('word_count', 0) for task in filtered_tasks) / len(filtered_tasks)
                        st.metric("📊 Avg Words", f"{avg_words:.0f}")
                with col6:
                    if st.button("📥 Download Filtered", key="download_filtered_individual"):
                        if filtered_tasks:
                            import zipfile
                            import io
                            
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for task in filtered_tasks:
                                    zip_file.write(task['file_path'], task['filename'])
                            
                            st.download_button(
                                label="💾 Download ZIP",
                                data=zip_buffer.getvalue(),
                                file_name=f"b2_first_filtered_tasks_{len(filtered_tasks)}.zip",
                                mime="application/zip",
                                key="download_filtered_zip"
                            )
                
                if not filtered_tasks:
                    st.info("No tasks match the current filters.")
                    return
                
                st.divider()
                
                # Task selection dropdown
                task_options = []
                for task in filtered_tasks:
                    title = task.get('title', 'Untitled')
                    if len(title) > 35:
                        title = title[:32] + "..."
                    
                    # Add QA status to display
                    qa_status = task_service.get_task_qa_status(task)
                    qa_emoji = task_service.get_qa_status_emoji(qa_status)
                    
                    task_options.append(f"{qa_emoji} {task.get('task_id', 'Unknown')} - {title}")
                
                selected_task_index = st.selectbox(
                    f"Select Task ({len(filtered_tasks)} available)",
                    range(len(task_options)),
                    format_func=lambda x: task_options[x],
                    key="selected_task"
                )
                
                if selected_task_index is not None:
                    selected_task = filtered_tasks[selected_task_index]
                    
                    st.divider()
                    st.subheader(f"📖 {selected_task.get('title', 'Untitled Task')}")
                    
                    if view_mode == "🎓 Learner View":
                        display_task_learner_view(selected_task)
                    elif view_mode == "📋 Summary":
                        display_task_summary_view(selected_task)
                    elif view_mode == "🔧 Full Details":
                        display_task_json_view(selected_task)
                    elif view_mode == "🔍 QA Review":
                        display_task_qa_view(selected_task, selected_task.get('file_path'))
            
            # Batch Collections Section
            elif content_type == "📦 Batch Collections":
                if not batch_dirs:
                    st.info("No batch collections found.")
                    return
                
                # Sort batches by creation time (newest first)
                batch_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Load batch summaries
                batch_data = []
                for batch_dir in batch_dirs:
                    try:
                        summary_file = batch_dir / "BATCH_SUMMARY.txt"
                        batch_info = {
                            'name': batch_dir.name,
                            'path': batch_dir,
                            'task_count': len(list(batch_dir.glob("*.json"))),
                            'created': batch_dir.stat().st_mtime,
                            'summary_exists': summary_file.exists()
                        }
                        
                        if summary_file.exists():
                            with open(summary_file, 'r') as f:
                                summary_content = f.read()
                                # Extract key info from summary
                                lines = summary_content.split('\n')
                                for line in lines:
                                    if 'Topics:' in line:
                                        batch_info['topics'] = line.split('Topics:')[1].strip()
                                    elif 'Text Types:' in line:
                                        batch_info['text_types'] = line.split('Text Types:')[1].strip()
                                    elif 'Success Rate:' in line:
                                        batch_info['success_rate'] = line.split('Success Rate:')[1].strip()
                        
                        batch_data.append(batch_info)
                    except Exception as e:
                        st.warning(f"Could not load batch info for {batch_dir.name}: {e}")
                
                if not batch_data:
                    st.error("No valid batch collections could be loaded.")
                    return
                
                # Batch selection and info
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    batch_options = []
                    for batch in batch_data:
                        # Parse batch name for display
                        name_parts = batch['name'].split('_')
                        if len(name_parts) >= 4:
                            date_part = name_parts[1]  # YYYYMMDD
                            time_part = name_parts[2]  # HHMMSS
                            topics_part = name_parts[3] if len(name_parts) > 3 else "unknown"
                            types_part = name_parts[4] if len(name_parts) > 4 else "unknown"
                            
                            # Format date and time
                            try:
                                from datetime import datetime
                                date_obj = datetime.strptime(date_part, "%Y%m%d")
                                time_obj = datetime.strptime(time_part, "%H%M%S")
                                formatted_date = date_obj.strftime("%Y-%m-%d")
                                formatted_time = time_obj.strftime("%H:%M:%S")
                                display_name = f"{formatted_date} {formatted_time} ({topics_part}, {types_part}) - {batch['task_count']} tasks"
                            except:
                                display_name = f"{batch['name']} - {batch['task_count']} tasks"
                        else:
                            display_name = f"{batch['name']} - {batch['task_count']} tasks"
                        
                        batch_options.append(display_name)
                    
                    selected_batch_index = st.selectbox(
                        f"Select Batch Collection ({len(batch_data)} available)",
                        range(len(batch_options)),
                        format_func=lambda x: batch_options[x],
                        key="selected_batch"
                    )
                
                with col2:
                    st.metric("📦 Total Batches", len(batch_data))
                
                if selected_batch_index is not None:
                    selected_batch = batch_data[selected_batch_index]
                    
                    # Batch actions
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("📋 View Summary", key="view_batch_summary"):
                            st.session_state.show_batch_summary = True
                    
                    with col2:
                        if st.button("📄 View Tasks", key="view_batch_tasks"):
                            st.session_state.show_batch_tasks = True
                    
                    with col3:
                        # Download batch
                        if st.button("📥 Download Batch", key="download_selected_batch"):
                            import zipfile
                            import io
                            
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for file_path in selected_batch['path'].rglob("*"):
                                    if file_path.is_file():
                                        arcname = file_path.relative_to(selected_batch['path'])
                                        zip_file.write(file_path, arcname)
                            
                            st.download_button(
                                label="💾 Download ZIP",
                                data=zip_buffer.getvalue(),
                                file_name=f"{selected_batch['name']}.zip",
                                mime="application/zip",
                                key="download_batch_zip"
                            )
                    
                    with col4:
                        if st.button("🗑️ Delete Batch", key="delete_selected_batch"):
                            st.session_state.confirm_delete_batch = selected_batch_index
                    
                    # Batch info display with QA status summary
                    # Load batch tasks to get QA status
                    batch_task_files = list(selected_batch['path'].glob("*.json"))
                    batch_qa_summary = {"approved": 0, "pending": 0, "rejected": 0}
                    
                    for task_file in batch_task_files:
                        try:
                            with open(task_file, 'r') as f:
                                task = json.load(f)
                                qa_status = task_service.get_task_qa_status(task)
                                batch_qa_summary[qa_status] += 1
                        except:
                            batch_qa_summary["pending"] += 1  # Default to pending if can't read
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Total Tasks", selected_batch['task_count'])
                    with col2:
                        st.metric("✅ Approved", batch_qa_summary["approved"])
                    with col3:
                        st.metric("⏳ Pending", batch_qa_summary["pending"])
                    with col4:
                        st.metric("❌ Rejected", batch_qa_summary["rejected"])
                    
                    st.caption(f"🕒 Created: {datetime.fromtimestamp(selected_batch['created']).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Confirmation for batch deletion
                    if st.session_state.get('confirm_delete_batch') == selected_batch_index:
                        st.warning("⚠️ Are you sure you want to delete this entire batch collection?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Yes, Delete Batch", key="confirm_batch_delete_yes"):
                                try:
                                    import shutil
                                    shutil.rmtree(selected_batch['path'])
                                    st.success("Batch collection deleted successfully!")
                                    st.session_state.confirm_delete_batch = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting batch: {e}")
                        with col2:
                            if st.button("❌ Cancel", key="confirm_batch_delete_no"):
                                st.session_state.confirm_delete_batch = None
                                st.rerun()
                    
                    # Display batch content
                    if st.session_state.get('show_batch_summary', False):
                        st.divider()
                        st.subheader("📋 Batch Summary")
                        
                        summary_file = selected_batch['path'] / "BATCH_SUMMARY.txt"
                        if summary_file.exists():
                            with open(summary_file, 'r') as f:
                                summary_content = f.read()
                            st.text_area("Summary Content", summary_content, height=300, key="batch_summary_content")
                        else:
                            st.warning("No batch summary file found.")
                    
                    if st.session_state.get('show_batch_tasks', False):
                        st.divider()
                        st.subheader("📄 Batch Tasks")
                        
                        # Load all tasks in the batch
                        batch_task_files = list(selected_batch['path'].glob("*.json"))
                        if batch_task_files:
                            batch_tasks = []
                            for task_file in batch_task_files:
                                try:
                                    with open(task_file, 'r') as f:
                                        task = json.load(f)
                                        task['filename'] = task_file.name
                                        task['file_path'] = str(task_file)
                                        batch_tasks.append(task)
                                except Exception as e:
                                    st.warning(f"Could not load {task_file.name}: {e}")
                            
                            if batch_tasks:
                                # Sort by task ID
                                batch_tasks.sort(key=lambda x: x.get('task_id', ''))
                                
                                # Task selection within batch with QA status
                                task_options = []
                                for task in batch_tasks:
                                    title = task.get('title', 'Untitled')
                                    if len(title) > 35:
                                        title = title[:32] + "..."
                                    
                                    # Add QA status to display
                                    qa_status = task_service.get_task_qa_status(task)
                                    qa_emoji = task_service.get_qa_status_emoji(qa_status)
                                    
                                    task_options.append(f"{qa_emoji} {task.get('task_id', 'Unknown')} - {title}")
                                
                                selected_batch_task_index = st.selectbox(
                                    f"Select Task from Batch ({len(batch_tasks)} available)",
                                    range(len(task_options)),
                                    format_func=lambda x: task_options[x],
                                    key="selected_batch_task"
                                )
                                
                                if selected_batch_task_index is not None:
                                    selected_batch_task = batch_tasks[selected_batch_task_index]
                                    
                                    st.divider()
                                    st.subheader(f"📖 {selected_batch_task.get('title', 'Untitled Task')}")
                                    
                                    if view_mode == "🎓 Learner View":
                                        display_task_learner_view_simple(selected_batch_task, context="batch")
                                    elif view_mode == "📋 Summary":
                                        display_task_summary_view(selected_batch_task)
                                    elif view_mode == "🔧 Full Details":
                                        display_task_json_view(selected_batch_task)
                                    elif view_mode == "🔍 QA Review":
                                        display_task_qa_view(selected_batch_task, selected_batch_task.get('file_path'))
                        else:
                            st.warning("No task files found in this batch.")
        else:
            st.info("Generated tasks directory not found. Generate some tasks first!")
    
    with tab5:
        st.header("⚙️ Admin Panel")
        st.info("🚧 **Admin Panel Disabled**")
        st.markdown("Admin panel features require local installation and are not available in demo mode.")
    
    with tab6:
        st.header("📖 Documentation")
        
        # Load documentation files
        docs_dir = Path(__file__).parent.parent / "docs"
        
        if docs_dir.exists():
            doc_files = list(docs_dir.glob("*.md"))
            
            if doc_files:
                # Sort by filename
                doc_files.sort(key=lambda x: x.name)
                
                # Create tabs for each documentation file
                doc_tabs = st.tabs([f"📄 {doc.name.replace('.md', '').replace('_', ' ').title()}" for doc in doc_files])
                
                for i, (tab, doc_file) in enumerate(zip(doc_tabs, doc_files)):
                    with tab:
                        try:
                            with open(doc_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            st.markdown(content)
                        except Exception as e:
                            st.error(f"Error loading {doc_file.name}: {e}")
            else:
                st.info("No documentation files found.")
        else:
            st.info("Documentation directory not found.")
            
            # Fallback documentation
            st.markdown("""
            ## B2 First Task Generator
            
            This is a tool for generating Cambridge B2 First Reading Part 5 tasks using local LLM integration.
            
            ### Features
            - Generate authentic B2 First reading tasks
            - Batch generation capabilities
            - Task library with filtering and sorting
            - QA review interface
            - Export and download functionality
            
            ### Demo Mode
            This version is running in demo mode with LLM features disabled.
            To use full functionality, install locally with Ollama.
            """)

# Display functions (copied from main app)
def display_task_learner_view(task):
    """Display a task in a nicely formatted learner view"""
    # Initialize session state for showing answers
    if 'show_answers' not in st.session_state:
        st.session_state.show_answers = False

    # Display task header with metadata
    ui_components.display_task_header(task, show_qa_status=False)
    
    # Show custom instructions if available
    if task.get('custom_instructions'):
        st.markdown(f"**📝 Custom Instructions:** {task.get('custom_instructions')}")
    
    # Show generation parameters if available
    gen_params = task.get('generation_params', {})
    if gen_params:
        with st.expander("🤖 Generation Parameters"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Model", gen_params.get('model_full_name', 'N/A'))
            with col2:
                temp = gen_params.get('temperature', 'N/A')
                if isinstance(temp, (int, float)):
                    st.metric("Temperature", f"{temp:.2f}")
                else:
                    st.metric("Temperature", str(temp))
            with col3:
                st.metric("Max Tokens", str(gen_params.get('max_tokens', 'N/A')))
    
    st.divider()
    
    # Create two columns for text and questions
    col1, col2 = st.columns([1, 1])
    
    with col1:
        ui_components.display_reading_text(task, container_type="container")
    
    with col2:
        ui_components.display_questions(task, show_answers=st.session_state.show_answers, interactive=False)
    
    # Action buttons
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Filter out non-serializable fields for download
        task_data_clean = task_service.clean_task_for_json(task)
        
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(task_data_clean, indent=2),
            file_name=f"{task.get('task_id', 'task')}.json",
            mime="application/json",
            key=f"download_learner_{task.get('task_id', 'unknown')}"
        )

    with col2:
        if st.button("📋 Copy Text Only", key=f"copy_text_{task.get('task_id', 'unknown')}"):
            st.code(task.get('text', ''), language=None)
    
    with col3:
        if st.button("📊 View JSON", key=f"json_view_{task.get('task_id', 'unknown')}"):
            # Filter out non-serializable fields for JSON display
            task_data_clean = task_service.clean_task_for_json(task)
            st.json(task_data_clean)
    
    with col4:
        if st.button("👁️ Reveal Answers", key=f"reveal_{task.get('task_id', 'unknown')}"):
            st.session_state.show_answers = not st.session_state.show_answers
            st.rerun()

def display_task_summary_view(task):
    """Display a task in summary card format"""
    text_type_display = task.get('text_type', 'unknown').replace('_', ' ').title()
    
    with st.expander(f"📖 {task.get('title', 'Untitled')} ({text_type_display})"):
        # Display task summary card with preview
        ui_components.display_task_summary_card(task, show_preview=True)
        
        # Show generation parameters if available
        gen_params = task.get('generation_params', {})
        if gen_params:
            st.markdown("**🤖 Generation Parameters:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                model_name = gen_params.get('model_full_name', task.get('model', 'unknown'))
                st.metric("Model", model_name)
            with col2:
                temperature = gen_params.get('temperature', 'N/A')
                if isinstance(temperature, (int, float)):
                    st.metric("Temperature", f"{temperature:.2f}")
                else:
                    st.metric("Temperature", str(temperature))
            with col3:
                st.metric("Max Tokens", str(gen_params.get('max_tokens', 'N/A')))
        
        # Show custom instructions if available
        if task.get('custom_instructions'):
            st.markdown(f"**📝 Custom Instructions:** {task.get('custom_instructions')}")
        
        # Individual task actions
        col1, col2 = st.columns(2)
        with col1:
            # Filter out non-serializable fields for download
            task_data_clean = task_service.clean_task_for_json(task)
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(task_data_clean, indent=2),
                file_name=f"{task.get('task_id', 'task')}.json",
                mime="application/json",
                key=f"download_summary_{task.get('task_id', 'unknown')}"
            )
        
        with col2:
            if st.button("📋 Copy Text Only", key=f"copy_text_summary_{task.get('task_id', 'unknown')}"):
                st.code(task.get('text', ''), language=None)

def display_task_json_view(task):
    """Display a task in raw JSON format"""
    st.subheader("🔧 Raw Task Data")
    
    # Filter out non-serializable fields for JSON display
    task_data_clean = task_service.clean_task_for_json(task)
    st.json(task_data_clean)

def display_task_learner_view_simple(task, context="batch"):
    """Display a task in a simplified learner view without expanders (for batch view)"""
    # Initialize session state for showing answers
    if f"show_answers_{context}" not in st.session_state:
        st.session_state[f"show_answers_{context}"] = False

    # Display task header with metadata
    ui_components.display_task_header(task, show_qa_status=False)
    
    # Show custom instructions if available
    if task.get('custom_instructions'):
        st.markdown(f"**📝 Custom Instructions:** {task.get('custom_instructions')}")
    
    # Show generation parameters (without expander for simplified view)
    gen_params = task.get('generation_params', {})
    if gen_params:
        st.markdown("**🤖 Generation Parameters:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Model", gen_params.get('model_full_name', 'N/A'))
        with col2:
            temp = gen_params.get('temperature', 'N/A')
            if isinstance(temp, (int, float)):
                st.metric("Temperature", f"{temp:.2f}")
            else:
                st.metric("Temperature", str(temp))
        with col3:
            st.metric("Max Tokens", str(gen_params.get('max_tokens', 'N/A')))
    
    st.divider()
    
    # Create two columns for text and questions
    col1, col2 = st.columns([1, 1])
    
    with col1:
        ui_components.display_reading_text(task, container_type="container")
    
    with col2:
        ui_components.display_questions(task, show_answers=st.session_state[f"show_answers_{context}"], interactive=False)
    
    # Action buttons
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Filter out non-serializable fields for download
        task_data_clean = task_service.clean_task_for_json(task)
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(task_data_clean, indent=2),
            file_name=f"{task.get('task_id', 'task')}.json",
            mime="application/json",
            key=f"download_{context}_{task.get('task_id', 'unknown')}"
        )

    with col2:
        if st.button("📋 Copy Text Only", key=f"copy_text_{context}_{task.get('task_id', 'unknown')}"):
            st.code(task.get('text', ''), language=None)
    
    with col3:
        if st.button("📊 View JSON", key=f"json_view_{context}_{task.get('task_id', 'unknown')}"):
            # Filter out non-serializable fields for JSON display
            task_data_clean = task_service.clean_task_for_json(task)
            st.json(task_data_clean)

    with col4:
        if st.button("👁️ Reveal Answers", key=f"reveal_{context}_{task.get('task_id', 'unknown')}"):
            st.session_state[f"show_answers_{context}"] = not st.session_state[f"show_answers_{context}"]
            st.rerun()

def display_task_qa_view(task, task_file_path=None):
    """Display a task in a QA review format"""
    # Display task header with metadata
    ui_components.display_task_header(task, show_qa_status=True)
    
    # Show custom instructions if available
    if task.get('custom_instructions'):
        st.markdown(f"**📝 Custom Instructions:** {task.get('custom_instructions')}")
    
    # Show generation parameters if available
    gen_params = task.get('generation_params', {})
    if gen_params:
        with st.expander("🤖 Generation Parameters"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Model", gen_params.get('model_full_name', 'N/A'))
            with col2:
                temp = gen_params.get('temperature', 'N/A')
                if isinstance(temp, (int, float)):
                    st.metric("Temperature", f"{temp:.2f}")
                else:
                    st.metric("Temperature", str(temp))
            with col3:
                st.metric("Max Tokens", str(gen_params.get('max_tokens', 'N/A')))
    
    st.divider()
    
    # Create two columns for text and questions
    col1, col2 = st.columns([1, 1])
    
    with col1:
        ui_components.display_reading_text(task, container_type="container")
    
    with col2:
        ui_components.display_questions(task, show_answers=True, interactive=True)
    
    # Action buttons
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filter out non-serializable fields for download
        task_data_clean = task_service.clean_task_for_json(task)
        
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(task_data_clean, indent=2),
            file_name=f"{task.get('task_id', 'task')}.json",
            mime="application/json",
            key=f"download_qa_{task.get('task_id', 'unknown')}"
        )
    
    with col2:
        if st.button("📋 Copy Text Only", key=f"copy_text_qa_{task.get('task_id', 'unknown')}"):
            st.code(task.get('text', ''), language=None)
    
    with col3:
        if st.button("📊 View JSON", key=f"json_view_qa_{task.get('task_id', 'unknown')}"):
            # Filter out non-serializable fields for JSON display
            task_data_clean = task_service.clean_task_for_json(task)
            st.json(task_data_clean)

if __name__ == "__main__":
    main()
