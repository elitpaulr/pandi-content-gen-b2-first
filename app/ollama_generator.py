#!/usr/bin/env python3
"""
Streamlit interface for Ollama-powered B2 First task generation
"""

import streamlit as st
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import time
from datetime import datetime

# Add src to path for imports - Multiple methods for robustness
project_root = Path(__file__).parent.parent
src_path = project_root / "src"

# Method 1: Add src directory to path
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Method 2: Add project root to path as backup
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    # Try importing from src directory structure
    from content.ollama_part5_generator import OllamaTaskGenerator
    from llm.ollama_client import OllamaClient, OllamaConfig
except ImportError:
    try:
        # Fallback: try importing with src prefix
        from src.content.ollama_part5_generator import OllamaTaskGenerator
        from src.llm.ollama_client import OllamaClient, OllamaConfig
    except ImportError as e:
        st.error(f"Import error: {e}")
        st.error("Make sure Ollama dependencies are installed")
        st.error(f"Project root: {project_root}")
        st.error(f"Src path: {src_path}")
        st.error(f"Src path exists: {src_path.exists()}")
        st.error(f"Python path: {sys.path}")
        
        # Show directory structure for debugging
        if src_path.exists():
            st.error("Contents of src directory:")
            for item in src_path.iterdir():
                st.error(f"  - {item.name}")
        st.stop()

# B2 First Reading Part 5 Text Types
B2_TEXT_TYPES = {
    "📰 Magazine Article": {
        "key": "magazine_article",
        "description": "Informative articles from lifestyle, science, or general interest magazines",
        "examples": ["Health and wellness trends", "Technology reviews", "Travel destinations"]
    },
    "📄 Newspaper Article": {
        "key": "newspaper_article", 
        "description": "News articles, feature stories, and opinion pieces",
        "examples": ["Environmental initiatives", "Social issues", "Cultural events"]
    },
    "📖 Novel Extract": {
        "key": "novel_extract",
        "description": "Excerpts from contemporary fiction showing character development",
        "examples": ["Coming-of-age stories", "Adventure narratives", "Relationship dynamics"]
    },
    "✍️ Personal Blog Post": {
        "key": "blog_post",
        "description": "First-person accounts of experiences and reflections",
        "examples": ["Travel experiences", "Career changes", "Personal challenges"]
    },
    "🔬 Popular Science Article": {
        "key": "science_article",
        "description": "Accessible explanations of scientific concepts and discoveries",
        "examples": ["Climate science", "Psychology research", "Technology innovations"]
    },
    "🎭 Cultural Review": {
        "key": "cultural_review",
        "description": "Reviews and commentary on books, films, art, or performances",
        "examples": ["Book reviews", "Film critiques", "Art exhibition reviews"]
    },
    "💼 Professional Feature": {
        "key": "professional_feature",
        "description": "Articles about careers, workplace trends, and professional development",
        "examples": ["Remote work trends", "Career advice", "Industry insights"]
    },
    "🏠 Lifestyle Feature": {
        "key": "lifestyle_feature",
        "description": "Articles about home, family, hobbies, and personal interests",
        "examples": ["Home improvement", "Cooking trends", "Hobby communities"]
    },
    "🌍 Travel Writing": {
        "key": "travel_writing",
        "description": "Descriptive accounts of places, cultures, and travel experiences",
        "examples": ["Destination guides", "Cultural observations", "Adventure stories"]
    },
    "📚 Educational Feature": {
        "key": "educational_feature",
        "description": "Informative articles about learning, education, and skill development",
        "examples": ["Language learning", "Study techniques", "Educational trends"]
    }
}

# Page configuration
st.set_page_config(
    page_title="Ollama Task Generator",
    page_icon="🤖",
    layout="wide"
)

def check_ollama_connection():
    """Check if Ollama is available"""
    try:
        client = OllamaClient()
        return client.check_connection(), client.list_models()
    except Exception as e:
        return False, []

def main():
    st.title("🤖 Ollama-Powered B2 First Task Generator")
    st.markdown("Generate authentic Cambridge B2 First Reading Part 5 tasks using local Ollama LLM")
    
    # Check Ollama status
    with st.spinner("Checking Ollama connection..."):
        is_connected, available_models = check_ollama_connection()
    
    if not is_connected:
        st.error("❌ **Ollama is not running or not accessible**")
        st.markdown("""
        **To get started:**
        1. Install Ollama: https://ollama.ai/
        2. Start Ollama: `ollama serve`
        3. Pull a model: `ollama pull llama3.1:8b`
        4. Refresh this page
        """)
        return
    
    st.success("✅ **Ollama is connected and ready!**")
    
    # Sidebar configuration
    st.sidebar.header("🔧 Configuration")
    
    # Model selection
    if available_models:
        selected_model = st.sidebar.selectbox(
            "Select Model",
            available_models,
            index=0 if "llama3.1:8b" not in available_models else available_models.index("llama3.1:8b")
        )
    else:
        st.sidebar.warning("No models found. Pull a model first: `ollama pull llama3.1:8b`")
        return
    
    # Generation parameters
    st.sidebar.subheader("Generation Parameters")
    temperature = st.sidebar.slider("Temperature", 0.1, 1.0, 0.7, 0.1)
    max_tokens = st.sidebar.slider("Max Tokens", 1000, 4000, 2000, 100)
    
    # Main interface tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Generate Tasks", "🔧 Improve Tasks", "📊 Batch Generation", "📋 Task Library", "⚙️ Admin Panel", "🧪 Test Save"])
    
    with tab1:
        st.header("Generate Single Task")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            topic = st.text_input(
                "Task Topic",
                placeholder="e.g., sustainable travel and eco-tourism",
                help="Enter a specific topic for the Reading Part 5 task"
            )
            
            # Text Type Selection
            text_type_options = list(B2_TEXT_TYPES.keys())
            selected_text_type = st.selectbox(
                "Text Type",
                text_type_options,
                index=0,
                help="Choose the style and format of the reading text"
            )
            
            # Show text type description
            text_type_key = B2_TEXT_TYPES[selected_text_type]["key"]
            text_type_desc = B2_TEXT_TYPES[selected_text_type]["description"]
            text_type_examples = B2_TEXT_TYPES[selected_text_type]["examples"]
            
            with st.expander("ℹ️ About this text type"):
                st.markdown(f"**{selected_text_type}**")
                st.write(text_type_desc)
                st.markdown("**Examples:**")
                for example in text_type_examples:
                    st.markdown(f"• {example}")
            
            custom_instructions = st.text_area(
                "Custom Instructions (Optional)",
                placeholder="Any specific requirements or focus areas...",
                height=100
            )
        
        with col2:
            st.markdown("**Suggested Topics:**")
            suggested_topics = [
                "sustainable travel and eco-tourism",
                "digital nomad lifestyle",
                "urban gardening projects",
                "AI in everyday life",
                "traditional crafts revival",
                "mindfulness and wellness",
                "renewable energy at home",
                "cultural food exchange",
                "adventure sports psychology",
                "social media relationships"
            ]
            
            for topic_suggestion in suggested_topics[:5]:
                if st.button(f"📝 {topic_suggestion}", key=f"suggest_{topic_suggestion}"):
                    st.session_state.topic_input = topic_suggestion
        
        if st.button("🚀 Generate Task", type="primary", disabled=not topic):
            if topic:
                # Create progress containers
                progress_container = st.container()
                status_container = st.container()
                
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    details_expander = st.expander("🔍 Generation Details", expanded=True)
                
                with details_expander:
                    step_status = st.empty()
                    attempt_status = st.empty()
                    parsing_status = st.empty()
                    validation_status = st.empty()
                
                try:
                    # Step 1: Initialize
                    status_text.text("🔧 Initializing generator...")
                    step_status.info("**Step 1/5:** Initializing Ollama generator and checking connection")
                    progress_bar.progress(0.1)
                    
                    config = OllamaConfig(
                        model=selected_model,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    generator = OllamaTaskGenerator(selected_model)
                    
                    # Step 2: Start generation
                    status_text.text(f"🎯 Generating {selected_text_type.lower()} about '{topic}'...")
                    step_status.info(f"**Step 2/5:** Generating task with {selected_model} model")
                    progress_bar.progress(0.2)
                    
                    # Custom generation with progress tracking
                    import time
                    start_time = time.time()
                    
                    # Show generation attempts in real-time
                    attempt_status.info("**Generation Attempts:** Starting...")
                    
                    # Step 3: LLM Generation
                    status_text.text("🤖 LLM generating content...")
                    step_status.info("**Step 3/5:** Large Language Model generating task content")
                    progress_bar.progress(0.4)
                    
                    # Generate the task (use auto-numbering)
                    # Handle empty custom instructions
                    processed_custom_instructions = custom_instructions.strip() if custom_instructions else None
                    if not processed_custom_instructions:
                        processed_custom_instructions = None
                    
                    task_data = generator.generate_single_task(
                        topic, 
                        None,  # Auto-assign task number to avoid overwriting
                        text_type=text_type_key,
                        custom_instructions=processed_custom_instructions
                    )
                    
                    # Step 4: Validation
                    status_text.text("✅ Validating task structure...")
                    step_status.info("**Step 4/5:** Validating task format and B2 First requirements")
                    progress_bar.progress(0.7)
                    
                    # Show validation results
                    validation_results = []
                    if task_data:
                        # Check word count
                        word_count = len(task_data['text'].split())
                        if 400 <= word_count <= 800:
                            validation_results.append("✅ Word count: " + str(word_count))
                        else:
                            validation_results.append(f"⚠️ Word count: {word_count} (should be 400-800)")
                        
                        # Check questions
                        question_count = len(task_data['questions'])
                        if 5 <= question_count <= 6:
                            validation_results.append("✅ Questions: " + str(question_count))
                        else:
                            validation_results.append(f"⚠️ Questions: {question_count} (should be 5-6)")
                        
                        # Check text type
                        if task_data.get('text_type') == text_type_key:
                            validation_results.append("✅ Text type: " + selected_text_type)
                        else:
                            validation_results.append("⚠️ Text type mismatch")
                        
                        # Check generation source
                        if task_data.get('generated_by') == 'ollama':
                            validation_results.append("✅ Generated by: Ollama LLM")
                        else:
                            validation_results.append("⚠️ Generated by: Fallback system")
                    
                    validation_status.markdown("**Validation Results:**\n" + "\n".join(validation_results))
                    
                    # Step 5: Complete
                    generation_time = time.time() - start_time
                    status_text.text(f"🎉 Task generated successfully in {generation_time:.1f}s!")
                    step_status.success(f"**Step 5/5:** Task generation complete! Generated by: {task_data.get('generated_by', 'unknown')}")
                    progress_bar.progress(1.0)
                    
                    # Show final generation summary
                    attempt_status.success(f"**Generation Summary:** Completed in {generation_time:.1f} seconds")
                    parsing_status.success(f"**JSON Parsing:** Successful (Text type: {selected_text_type})")
                    
                    # Display results
                    st.success("✅ Task generated successfully!")
                    
                    # Task overview with enhanced metrics
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Word Count", len(task_data['text'].split()))
                    with col2:
                        st.metric("Questions", len(task_data['questions']))
                    with col3:
                        st.metric("Text Type", selected_text_type.split()[1])
                    with col4:
                        st.metric("Generated By", task_data.get('generated_by', 'unknown').title())
                    with col5:
                        st.metric("Generation Time", f"{generation_time:.1f}s")
                    
                    # Display task
                    st.subheader(f"📖 {task_data['title']}")
                    
                    # Text and questions side by side
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        st.markdown("**Reading Text:**")
                        st.markdown(task_data['text'])
                    
                    with col2:
                        st.markdown("**Questions:**")
                        for i, question in enumerate(task_data['questions']):
                            with st.expander(f"Question {question['question_number']}", expanded=True):
                                st.markdown(f"**{question['question_text']}**")
                                
                                for option, text in question['options'].items():
                                    if option == question['correct_answer']:
                                        st.markdown(f"✅ **{option}**: {text}")
                                    else:
                                        st.markdown(f"   **{option}**: {text}")
                                
                                st.caption(f"Type: {question.get('question_type', 'unknown')}")
                                if 'explanation' in question:
                                    st.info(f"💡 {question['explanation']}")
                    
                    # Save option with enhanced feedback
                    if st.button("💾 Save Task"):
                        try:
                            with st.spinner("Saving task..."):
                                filepath = generator.save_task(task_data)
                                st.success(f"✅ Task saved successfully to: {filepath}")
                                st.info(f"📁 File location: `{filepath}`")
                        except Exception as e:
                            st.error(f"❌ Failed to save task: {str(e)}")
                            with st.expander("🔧 Save Troubleshooting"):
                                st.markdown(f"""
                                **Error Details:** {str(e)}
                                
                                **Common save issues:**
                                - Directory permissions (check if you can write to the generated_tasks folder)
                                - Disk space (ensure you have enough storage)
                                - File already exists and is locked
                                - Invalid characters in filename
                                
                                **Workaround:** Use the Download JSON button below as an alternative.
                                """)
                    
                    # Download JSON
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(task_data, indent=2),
                        file_name=f"{task_data['task_id']}.json",
                        mime="application/json"
                    )
                    
                except Exception as e:
                    # Enhanced error reporting
                    status_text.text("❌ Generation failed")
                    step_status.error(f"**Error:** {str(e)}")
                    
                    # Show detailed error information
                    if "Server disconnected" in str(e):
                        attempt_status.error("**Connection Issue:** Ollama server disconnected during generation")
                        parsing_status.warning("**Suggestion:** Check if Ollama is running and restart if needed")
                    elif "JSON" in str(e) or "parse" in str(e).lower():
                        attempt_status.error("**Parsing Issue:** Failed to parse LLM response as valid JSON")
                        parsing_status.error(f"**Details:** {str(e)}")
                    elif "validation" in str(e).lower():
                        attempt_status.error("**Validation Issue:** Generated task doesn't meet B2 First requirements")
                        validation_status.error(f"**Details:** {str(e)}")
                    else:
                        attempt_status.error(f"**Unknown Error:** {str(e)}")
                    
                    st.error(f"❌ Generation failed: {str(e)}")
                    
                    # Provide troubleshooting suggestions
                    with st.expander("🔧 Troubleshooting"):
                        st.markdown("""
                        **Common issues and solutions:**
                        
                        1. **Server disconnected:** Restart Ollama service
                        2. **JSON parsing errors:** Try a different topic or text type
                        3. **Validation failures:** The LLM output doesn't meet B2 requirements
                        4. **Connection timeouts:** Check your internet connection
                        
                        **If problems persist:** Try using a different model or simplifying the topic.
                        """)
                        
                        if st.button("🔄 Retry Generation"):
                            st.rerun()
    
    with tab2:
        st.header("Improve Existing Tasks")
        
        # Load existing tasks
        generated_tasks_dir = Path(__file__).parent.parent / "generated_tasks"
        if generated_tasks_dir.exists():
            task_files = list(generated_tasks_dir.glob("*.json"))
            
            if task_files:
                selected_file = st.selectbox(
                    "Select Task to Improve",
                    task_files,
                    format_func=lambda x: x.stem
                )
                
                if selected_file:
                    # Load and display current task
                    with open(selected_file, 'r') as f:
                        current_task = json.load(f)
                    
                    st.subheader("Current Task")
                    st.json(current_task, expanded=False)
                    
                    improvement_focus = st.multiselect(
                        "Focus Areas for Improvement",
                        ["Question specificity", "Distractor quality", "Text engagement", "Vocabulary level", "Question variety"],
                        default=["Question specificity", "Distractor quality"]
                    )
                    
                    if st.button("🔧 Improve Task"):
                        with st.spinner("Improving task... This may take 30-60 seconds"):
                            try:
                                config = OllamaConfig(model=selected_model)
                                client = OllamaClient(config)
                                
                                improved_task = client.improve_existing_task(current_task)
                                
                                st.success("✅ Task improved!")
                                st.subheader("Improved Task")
                                st.json(improved_task, expanded=False)
                                
                                # Save improved version
                                if st.button("💾 Save Improved Task"):
                                    improved_filename = f"{improved_task['task_id']}_improved.json"
                                    improved_path = generated_tasks_dir / improved_filename
                                    
                                    with open(improved_path, 'w') as f:
                                        json.dump(improved_task, f, indent=2)
                                    
                                    st.success(f"Improved task saved as: {improved_filename}")
                                
                            except Exception as e:
                                st.error(f"❌ Improvement failed: {str(e)}")
            else:
                st.info("No existing tasks found. Generate some tasks first!")
        else:
            st.info("Generated tasks directory not found.")
    
    with tab3:
        st.header("Batch Generation")
        
        st.markdown("Generate multiple tasks efficiently")
        
        # Text Type Selection for Batch Generation
        st.subheader("📝 Text Types")
        st.markdown("Select which text types to include in batch generation:")
        
        # Create columns for checkboxes
        cols = st.columns(3)
        selected_text_types = []
        
        for i, (text_type_name, text_type_info) in enumerate(B2_TEXT_TYPES.items()):
            col_idx = i % 3
            with cols[col_idx]:
                if st.checkbox(
                    text_type_name, 
                    value=(i < 3),  # Default first 3 selected
                    key=f"batch_text_type_{text_type_info['key']}"
                ):
                    selected_text_types.append(text_type_info['key'])
        
        if not selected_text_types:
            st.warning("⚠️ Please select at least one text type")
            return
        
        st.info(f"Selected {len(selected_text_types)} text types: {', '.join([t.replace('_', ' ').title() for t in selected_text_types])}")
        
        # Predefined topic sets
        st.subheader("📚 Topics")
        topic_sets = {
            "Travel & Adventure": [
                "sustainable travel and eco-tourism",
                "adventure sports and personal challenges",
                "cultural exchange through travel",
                "digital nomad lifestyle"
            ],
            "Technology & Modern Life": [
                "artificial intelligence in everyday life",
                "social media influence on relationships",
                "remote work and productivity",
                "digital wellness and screen time"
            ],
            "Environment & Sustainability": [
                "urban gardening and community spaces",
                "renewable energy solutions for homes",
                "climate change adaptation strategies",
                "sustainable fashion and consumption"
            ],
            "Personal Development": [
                "mindfulness and mental health awareness",
                "lifelong learning and skill development",
                "creative hobbies and self-expression",
                "work-life balance strategies"
            ]
        }
        
        selected_set = st.selectbox("Choose Topic Set", list(topic_sets.keys()))
        custom_topics = st.text_area(
            "Or Enter Custom Topics (one per line)",
            placeholder="sustainable travel\ndigital wellness\nurban gardening"
        )
        
        tasks_per_topic = st.slider("Tasks per Topic", 1, 3, 1)
        
        # Determine topics to use
        if custom_topics.strip():
            topics_to_use = [topic.strip() for topic in custom_topics.split('\n') if topic.strip()]
        else:
            topics_to_use = topic_sets[selected_set]
        
        total_tasks = len(topics_to_use) * len(selected_text_types) * tasks_per_topic
        st.info(f"Will generate {len(topics_to_use)} topics × {len(selected_text_types)} text types × {tasks_per_topic} tasks = **{total_tasks} total tasks**")
        
        if st.button("🚀 Start Batch Generation", type="primary"):
            # Create enhanced progress tracking
            progress_container = st.container()
            stats_container = st.container()
            details_container = st.container()
            
            with progress_container:
                overall_progress = st.progress(0)
                current_task_progress = st.progress(0)
                status_text = st.empty()
                current_task_text = st.empty()
            
            with stats_container:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    success_metric = st.metric("✅ Successful", 0)
                with col2:
                    failed_metric = st.metric("❌ Failed", 0)
                with col3:
                    ollama_metric = st.metric("🤖 Ollama Generated", 0)
                with col4:
                    fallback_metric = st.metric("🔄 Fallback Used", 0)
            
            with details_container:
                details_expander = st.expander("📊 Generation Details", expanded=True)
                with details_expander:
                    task_log = st.empty()
                    current_attempts = st.empty()
                    parsing_info = st.empty()
            
            try:
                generator = OllamaTaskGenerator(selected_model)
                completed_tasks = []
                failed_tasks = []
                task_counter = 0
                success_count = 0
                failed_count = 0
                ollama_count = 0
                fallback_count = 0
                
                # Create log entries list
                log_entries = []
                
                import time
                batch_start_time = time.time()
                
                for topic in topics_to_use:
                    for text_type_key in selected_text_types:
                        text_type_name = next(name for name, info in B2_TEXT_TYPES.items() if info['key'] == text_type_key)
                        
                        for j in range(tasks_per_topic):
                            task_counter += 1
                            task_start_time = time.time()
                            
                            # Update main progress
                            overall_progress.progress(task_counter / total_tasks)
                            status_text.text(f"📝 Processing task {task_counter}/{total_tasks}")
                            current_task_text.text(f"🎯 Generating: {text_type_name} about '{topic}' (attempt {j+1})")
                            
                            # Reset current task progress
                            current_task_progress.progress(0.1)
                            current_attempts.info(f"**Current Task:** {text_type_name} - '{topic[:50]}{'...' if len(topic) > 50 else ''}'")
                            
                            try:
                                # Step-by-step progress for current task
                                current_task_progress.progress(0.2)
                                parsing_info.info("**Status:** Initializing generation...")
                                
                                current_task_progress.progress(0.4)
                                parsing_info.info("**Status:** LLM generating content...")
                                
                                # Generate the task (use auto-numbering)
                                task = generator.generate_single_task(
                                    topic, 
                                    None,  # Auto-assign task number to avoid overwriting
                                    text_type=text_type_key
                                )
                                
                                current_task_progress.progress(0.7)
                                parsing_info.info("**Status:** Validating and saving...")
                                
                                # Save the task
                                generator.save_task(task)
                                completed_tasks.append(task)
                                
                                # Update counters
                                success_count += 1
                                if task.get('generated_by') == 'ollama':
                                    ollama_count += 1
                                else:
                                    fallback_count += 1
                                
                                # Complete current task
                                current_task_progress.progress(1.0)
                                task_time = time.time() - task_start_time
                                
                                # Add to log
                                generation_source = "🤖 Ollama" if task.get('generated_by') == 'ollama' else "🔄 Fallback"
                                log_entries.append(f"✅ Task {task_counter}: {text_type_name} - '{topic[:30]}...' ({generation_source}, {task_time:.1f}s)")
                                parsing_info.success(f"**Status:** ✅ Completed in {task_time:.1f}s ({generation_source})")
                                
                                # Update metrics
                                col1.metric("✅ Successful", success_count)
                                col3.metric("🤖 Ollama Generated", ollama_count)
                                col4.metric("🔄 Fallback Used", fallback_count)
                                
                            except Exception as e:
                                failed_count += 1
                                failed_tasks.append({
                                    'topic': topic,
                                    'text_type': text_type_name,
                                    'error': str(e)
                                })
                                
                                task_time = time.time() - task_start_time
                                
                                # Add to log
                                error_type = "Connection" if "disconnected" in str(e) else "Parsing" if "JSON" in str(e) else "Unknown"
                                log_entries.append(f"❌ Task {task_counter}: {text_type_name} - '{topic[:30]}...' ({error_type} error, {task_time:.1f}s)")
                                parsing_info.error(f"**Status:** ❌ Failed - {error_type} error ({task_time:.1f}s)")
                                
                                # Update metrics
                                col2.metric("❌ Failed", failed_count)
                                
                                # Brief pause before continuing
                                time.sleep(0.5)
                            
                            # Update the log display
                            if log_entries:
                                # Show last 10 entries
                                recent_logs = log_entries[-10:]
                                task_log.markdown("**Recent Tasks:**\n" + "\n".join(recent_logs))
                            
                            # Small delay to make progress visible
                            time.sleep(0.2)
                
                # Final completion
                batch_time = time.time() - batch_start_time
                overall_progress.progress(1.0)
                current_task_progress.progress(1.0)
                status_text.text(f"🎉 Batch generation complete! ({batch_time:.1f}s total)")
                current_task_text.text(f"✅ Generated {success_count} tasks, {failed_count} failed")
                
                # Final status
                if success_count > 0:
                    success_rate = (success_count / (success_count + failed_count)) * 100
                    parsing_info.success(f"**Final Status:** {success_rate:.1f}% success rate ({ollama_count} Ollama, {fallback_count} fallback)")
                else:
                    parsing_info.error("**Final Status:** No tasks generated successfully")
                
                # Show complete log
                if log_entries:
                    task_log.markdown("**Complete Generation Log:**\n" + "\n".join(log_entries))
                
                st.success(f"✅ Batch generation complete! Generated {len(completed_tasks)} tasks in {batch_time:.1f} seconds")
                
                # Enhanced summary with detailed statistics
                if completed_tasks:
                    st.subheader("📊 Generation Summary")
                    
                    # Success metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Tasks", len(completed_tasks))
                    with col2:
                        success_rate = (len(completed_tasks) / total_tasks) * 100
                        st.metric("Success Rate", f"{success_rate:.1f}%")
                    with col3:
                        avg_time = batch_time / total_tasks
                        st.metric("Avg Time/Task", f"{avg_time:.1f}s")
                    with col4:
                        ollama_rate = (ollama_count / len(completed_tasks)) * 100 if completed_tasks else 0
                        st.metric("Ollama Success", f"{ollama_rate:.1f}%")
                    
                    # Detailed breakdowns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📝 By Text Type:**")
                        text_type_counts = {}
                        for task in completed_tasks:
                            text_type = task.get('text_type', 'unknown')
                            text_type_counts[text_type] = text_type_counts.get(text_type, 0) + 1
                        
                        for text_type, count in text_type_counts.items():
                            display_name = text_type.replace('_', ' ').title()
                            st.metric(display_name, count)
                    
                    with col2:
                        st.markdown("**🎯 By Topic:**")
                        topic_counts = {}
                        for task in completed_tasks:
                            topic = task.get('topic', 'unknown')
                            topic_counts[topic] = topic_counts.get(topic, 0) + 1
                        
                        for topic, count in list(topic_counts.items())[:5]:  # Show top 5
                            display_topic = topic[:25] + "..." if len(topic) > 25 else topic
                            st.metric(display_topic, count)
                
                # Show failed tasks if any
                if failed_tasks:
                    st.subheader("⚠️ Failed Tasks")
                    with st.expander(f"View {len(failed_tasks)} failed tasks"):
                        for i, failed_task in enumerate(failed_tasks, 1):
                            st.markdown(f"**{i}.** {failed_task['text_type']} - '{failed_task['topic']}'")
                            st.caption(f"Error: {failed_task['error']}")
                
            except Exception as e:
                status_text.text("❌ Batch generation failed")
                current_task_text.text(f"Error: {str(e)}")
                parsing_info.error(f"**Critical Error:** {str(e)}")
                st.error(f"❌ Batch generation failed: {str(e)}")
                
                # Troubleshooting for batch generation
                with st.expander("🔧 Batch Generation Troubleshooting"):
                    st.markdown("""
                    **Common batch generation issues:**
                    
                    1. **Ollama connection lost:** Restart Ollama service
                    2. **Memory issues:** Reduce batch size or use smaller model
                    3. **Timeout errors:** Check network stability
                    4. **High failure rate:** Try simpler topics or different text types
                    
                    **Recommendations:**
                    - Start with smaller batches (3-5 tasks) to test
                    - Use stable topics that work well individually
                    - Monitor system resources during generation
                    """)
                    
                    if st.button("🔄 Retry Batch Generation"):
                        st.rerun()
    
    with tab4:
        st.header("📚 Task Library")
        
        # Load and display all generated tasks
        generated_tasks_dir = Path(__file__).parent.parent / "generated_tasks"
        if generated_tasks_dir.exists():
            task_files = list(generated_tasks_dir.glob("*.json"))
            
            if task_files:
                # Action buttons row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Total Tasks", len(task_files))
                
                with col2:
                    if st.button("📥 Download All Tasks"):
                        # Create a zip file with all tasks
                        import zipfile
                        import io
                        
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for task_file in task_files:
                                zip_file.write(task_file, task_file.name)
                        
                        st.download_button(
                            label="💾 Download ZIP",
                            data=zip_buffer.getvalue(),
                            file_name="b2_first_tasks.zip",
                            mime="application/zip"
                        )
                
                with col3:
                    view_mode = st.selectbox(
                        "View Mode",
                        ["🎓 Learner View", "📋 Summary View", "🔧 JSON View"],
                        index=0
                    )
                
                with col4:
                    if st.button("🗑️ Clear All Tasks"):
                        if st.checkbox("⚠️ Confirm deletion"):
                            for task_file in task_files:
                                task_file.unlink()
                            st.success("All tasks deleted!")
                            st.rerun()
                
                st.divider()
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_by_generator = st.selectbox(
                        "Filter by Generator",
                        ["All", "ollama", "improved", "fallback"],
                        index=0
                    )
                
                with col2:
                    filter_by_text_type = st.selectbox(
                        "Filter by Text Type",
                        ["All"] + [info['key'] for info in B2_TEXT_TYPES.values()],
                        index=0
                    )
                
                with col3:
                    sort_by = st.selectbox(
                        "Sort by",
                        ["Task ID", "Title", "Topic Category", "Word Count"],
                        index=0
                    )
                
                # Load and display tasks
                tasks_data = []
                for task_file in task_files:
                    try:
                        with open(task_file, 'r') as f:
                            task = json.load(f)
                            task['filename'] = task_file.name
                            tasks_data.append(task)
                    except Exception as e:
                        st.warning(f"Could not load {task_file.name}: {e}")
                
                # Apply filters
                if filter_by_generator != "All":
                    tasks_data = [t for t in tasks_data if t.get('generated_by') == filter_by_generator]
                
                if filter_by_text_type != "All":
                    tasks_data = [t for t in tasks_data if t.get('text_type') == filter_by_text_type]
                
                # Sort tasks
                if sort_by == "Task ID":
                    tasks_data.sort(key=lambda x: x.get('task_id', ''))
                elif sort_by == "Title":
                    tasks_data.sort(key=lambda x: x.get('title', ''))
                elif sort_by == "Topic Category":
                    tasks_data.sort(key=lambda x: x.get('topic_category', ''))
                elif sort_by == "Word Count":
                    tasks_data.sort(key=lambda x: len(x.get('text', '').split()), reverse=True)
                
                if not tasks_data:
                    st.info("No tasks match the current filters.")
                    return
                
                st.info(f"Showing {len(tasks_data)} tasks")
                
                # Create tabs for each task
                if view_mode == "🎓 Learner View":
                    # Create tabs for individual task viewing
                    task_names = [f"{task.get('task_id', 'Unknown')} - {task.get('title', 'Untitled')[:30]}..." 
                                 if len(task.get('title', '')) > 30 
                                 else f"{task.get('task_id', 'Unknown')} - {task.get('title', 'Untitled')}" 
                                 for task in tasks_data]
                    
                    if len(tasks_data) > 10:
                        st.warning("⚠️ Too many tasks for tab view. Showing first 10 tasks. Use filters to narrow down.")
                        tasks_data = tasks_data[:10]
                        task_names = task_names[:10]
                    
                    if tasks_data:
                        selected_tabs = st.tabs(task_names)
                        
                        for i, (task, tab) in enumerate(zip(tasks_data, selected_tabs)):
                            with tab:
                                display_task_learner_view(task)
                
                elif view_mode == "📋 Summary View":
                    # Display tasks in summary cards
                    for task in tasks_data:
                        display_task_summary_view(task)
                
                elif view_mode == "🔧 JSON View":
                    # Display tasks in JSON format
                    for task in tasks_data:
                        display_task_json_view(task)
                        
            else:
                st.info("No tasks found. Generate some tasks first!")
        else:
            st.info("Generated tasks directory not found.")

def display_task_learner_view(task):
    """Display a task in a nicely formatted learner view"""
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
        st.metric("🤖 Generator", task.get('generated_by', 'unknown').title())
    
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
    
    # Generation parameters
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
        
        # Format the text nicely (text_content already retrieved above)
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
                    
                    questions_html += f'</div>'
                    questions_html += f'</div>'
                    
                except Exception as e:
                    questions_html += f'<div class="question-item"><div style="color: red;">Error displaying question {i}: {str(e)}</div></div>'
            
            questions_html += '</div>'
            st.markdown(questions_html, unsafe_allow_html=True)
        else:
            st.warning("No questions found for this task.")
    
    # Action buttons
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(task, indent=2),
            file_name=f"{task.get('task_id', 'task')}.json",
            mime="application/json",
            key=f"download_learner_{task.get('task_id', 'unknown')}"
        )
    
    with col2:
        if st.button("📋 Copy Text Only", key=f"copy_text_{task.get('task_id', 'unknown')}"):
            st.code(task.get('text', ''), language=None)
    
    with col3:
        if st.button("📊 View JSON", key=f"json_view_{task.get('task_id', 'unknown')}"):
            st.json(task)

def display_task_summary_view(task):
    """Display a task in summary card format"""
    text_type_display = task.get('text_type', 'unknown').replace('_', ' ').title()
    
    # Get generation parameters if available
    gen_params = task.get('generation_params', {})
    model_name = gen_params.get('model_full_name', task.get('model', 'unknown'))
    
    with st.expander(f"📖 {task.get('title', 'Untitled')} ({text_type_display})"):
        # Basic metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Word Count", len(task.get('text', '').split()))
        with col2:
            st.metric("Questions", len(task.get('questions', [])))
        with col3:
            st.metric("Text Type", text_type_display)
        with col4:
            st.metric("Generator", task.get('generated_by', 'unknown'))
        
        # Generation parameters row
        if gen_params:
            st.markdown("**🤖 Generation Parameters:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Model", model_name)
            with col2:
                temperature = gen_params.get('temperature', 'N/A')
                if isinstance(temperature, (int, float)):
                    st.metric("Temperature", f"{temperature:.2f}")
                else:
                    st.metric("Temperature", str(temperature))
            with col3:
                st.metric("Max Tokens", str(gen_params.get('max_tokens', 'N/A')))
        
        # Additional metadata
        if task.get('topic_category'):
            st.markdown(f"**📂 Category:** {task.get('topic_category', 'unknown').replace('_', ' ').title()}")
        
        if task.get('topic'):
            st.markdown(f"**🎯 Topic:** {task.get('topic', 'N/A')}")
        
        # Text preview
        text_preview = task.get('text', '')[:200] + "..." if len(task.get('text', '')) > 200 else task.get('text', '')
        st.markdown(f"**📄 Text Preview:** {text_preview}")
        
        # Individual task actions
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(task, indent=2),
                file_name=f"{task.get('task_id', 'task')}.json",
                mime="application/json",
                key=f"download_summary_{task.get('task_id', 'unknown')}"
            )
        with col2:
            if st.button(f"📖 View Full Task", key=f"view_summary_{task.get('task_id', 'unknown')}"):
                st.json(task)

def display_task_json_view(task):
    """Display a task in JSON format"""
    text_type_display = task.get('text_type', 'unknown').replace('_', ' ').title()
    
    with st.expander(f"🔧 {task.get('title', 'Untitled')} - JSON Data"):
        st.json(task)
        
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(task, indent=2),
            file_name=f"{task.get('task_id', 'task')}.json",
            mime="application/json",
            key=f"download_json_{task.get('task_id', 'unknown')}"
        )

    with tab5:
        st.header("⚙️ Admin Panel")
        st.markdown("**Configure AI prompts and system parameters**")
        
        # Password protection for admin panel
        if 'admin_authenticated' not in st.session_state:
            st.session_state.admin_authenticated = False
        
        if not st.session_state.admin_authenticated:
            st.warning("🔒 Admin access required")
            admin_password = st.text_input("Enter admin password:", type="password")
            if st.button("Authenticate"):
                # Simple password check (in production, use proper authentication)
                if admin_password == "admin123":  # Change this to a secure password
                    st.session_state.admin_authenticated = True
                    st.success("✅ Authenticated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
            st.info("💡 Default password: admin123")
            return
        
        # Admin panel content
        st.success("🔓 Admin access granted")
        
        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.admin_authenticated = False
            st.rerun()
        
        # Create tabs for different admin sections
        admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
            "🤖 AI Prompts", 
            "📝 Text Type Instructions", 
            "⚙️ Model Parameters", 
            "📚 Knowledge Base"
        ])
        
        with admin_tab1:
            st.subheader("🤖 AI System Prompts")
            
            # Main generation system prompt
            st.markdown("### Main Task Generation Prompt")
            
            # Get current system prompt from the code
            current_system_prompt = """You are an expert Cambridge B2 First exam content creator. 
Generate authentic Reading Part 5 tasks that match the official exam format exactly.

CRITICAL: You must respond with ONLY valid JSON. No explanations, no markdown, no extra text.

Reading Part 5 Requirements:
- Text length: 550-750 words (engaging, authentic content)
- 6 multiple choice questions (31-36)
- Each question has 4 options (A, B, C, D)
- Question types: inference, vocabulary in context, attitude/opinion, detail, reference, main idea
- Text should be engaging and at B2 level
- Questions must be specific and contextual, not generic

TEXT TYPE INSTRUCTION: {text_style_instruction}

You can use natural formatting in your text including:
- Paragraphs with line breaks
- Quotation marks for dialogue or emphasis
- Natural punctuation and formatting

The JSON parser will handle the formatting correctly.

RESPOND WITH ONLY THIS JSON FORMAT:
{
    "task_id": "reading_part5_task_01",
    "title": "Engaging Task Title",
    "topic": "topic_category",
    "text_type": "{text_type}",
    "difficulty": "B2",
    "text": "Your engaging text here following the {text_type} style...",
    "questions": [
        {
            "question_number": 1,
            "question_text": "What does the author suggest about...?",
            "options": {
                "A": "First realistic option",
                "B": "Second realistic option", 
                "C": "Third realistic option",
                "D": "Fourth realistic option"
            },
            "correct_answer": "A",
            "question_type": "inference"
        }
    ]
}"""
            
            # Load saved prompt if exists
            prompt_file = Path(__file__).parent.parent / "config" / "system_prompts.json"
            prompt_file.parent.mkdir(exist_ok=True)
            
            if prompt_file.exists():
                try:
                    with open(prompt_file, 'r') as f:
                        saved_prompts = json.load(f)
                    current_system_prompt = saved_prompts.get('main_generation_prompt', current_system_prompt)
                except:
                    pass
            
            edited_system_prompt = st.text_area(
                "System Prompt for Task Generation:",
                value=current_system_prompt,
                height=400,
                help="This prompt controls how the AI generates reading tasks"
            )
            
            # Task improvement prompt
            st.markdown("### Task Improvement Prompt")
            
            current_improvement_prompt = """You are an expert Cambridge B2 First exam content creator.
Improve the given Reading Part 5 task by making the questions more specific and contextual.

Focus on:
1. Making questions refer to specific parts of the text
2. Creating realistic, plausible distractors
3. Ensuring questions test different skills
4. Making sure only one answer is clearly correct

You can use natural formatting in your improvements including quotes, line breaks, etc.
The JSON parser will handle the formatting correctly.

Return the improved task in the same JSON format."""
            
            # Load saved improvement prompt if exists
            if prompt_file.exists():
                try:
                    with open(prompt_file, 'r') as f:
                        saved_prompts = json.load(f)
                    current_improvement_prompt = saved_prompts.get('improvement_prompt', current_improvement_prompt)
                except:
                    pass
            
            edited_improvement_prompt = st.text_area(
                "System Prompt for Task Improvement:",
                value=current_improvement_prompt,
                height=200,
                help="This prompt controls how the AI improves existing tasks"
            )
            
            # User prompt template
            st.markdown("### User Prompt Template")
            
            current_user_prompt = """Create a Reading Part 5 task about: {topic}

Text Type: {text_type}
Style Instructions: {text_style_instruction}

Make sure:
1. The text is 550-750 words and follows the {text_type} style
2. Use natural formatting including paragraphs, quotes, and proper punctuation
3. The topic is engaging and suitable for B2 level students
4. Create 6 questions (numbered 1-6) that are specific to the text content
5. Questions test different skills: inference, vocabulary, attitude, details, reference, main idea
6. Each question has exactly 4 realistic options
7. Only one option is clearly correct for each question
8. Make the content authentic and interesting

Topic: {topic}
Text Type: {text_type}
Difficulty: {difficulty}"""
            
            # Load saved user prompt if exists
            if prompt_file.exists():
                try:
                    with open(prompt_file, 'r') as f:
                        saved_prompts = json.load(f)
                    current_user_prompt = saved_prompts.get('user_prompt_template', current_user_prompt)
                except:
                    pass
            
            edited_user_prompt = st.text_area(
                "User Prompt Template:",
                value=current_user_prompt,
                height=300,
                help="Template for the user prompt sent to the AI. Use {topic}, {text_type}, etc. as placeholders"
            )
            
            # Save prompts button
            if st.button("💾 Save AI Prompts", type="primary"):
                prompts_to_save = {
                    'main_generation_prompt': edited_system_prompt,
                    'improvement_prompt': edited_improvement_prompt,
                    'user_prompt_template': edited_user_prompt,
                    'last_updated': str(datetime.now())
                }
                
                try:
                    with open(prompt_file, 'w') as f:
                        json.dump(prompts_to_save, f, indent=2)
                    st.success("✅ AI prompts saved successfully!")
                    st.info("🔄 Restart the application to apply changes")
                except Exception as e:
                    st.error(f"❌ Failed to save prompts: {e}")
        
        with admin_tab2:
            st.subheader("📝 Text Type Instructions")
            
            # Load current text type instructions
            text_type_instructions = {
                "magazine_article": "Write as an engaging magazine article with a clear structure, subheadings if appropriate, and an informative yet accessible tone. Include expert quotes or statistics where relevant.",
                "newspaper_article": "Write as a newspaper feature article with journalistic style, factual reporting, and balanced perspective. Include relevant context and background information.",
                "novel_extract": "Write as an excerpt from a contemporary novel with character development, dialogue, and narrative description. Focus on showing rather than telling.",
                "blog_post": "Write as a personal blog post with first-person perspective, conversational tone, and personal reflections or experiences.",
                "science_article": "Write as a popular science article that explains complex concepts in accessible language, with examples and analogies to help understanding.",
                "cultural_review": "Write as a cultural review or commentary with analytical perspective, critical evaluation, and informed opinion.",
                "professional_feature": "Write as a professional feature article about workplace trends, career advice, or industry insights with practical information.",
                "lifestyle_feature": "Write as a lifestyle feature about personal interests, home, family, or hobbies with practical tips and relatable content.",
                "travel_writing": "Write as travel writing with vivid descriptions of places, cultural observations, and personal travel experiences.",
                "educational_feature": "Write as an educational feature about learning, study techniques, or educational trends with informative and helpful content."
            }
            
            # Load saved instructions if exists
            instructions_file = Path(__file__).parent.parent / "config" / "text_type_instructions.json"
            if instructions_file.exists():
                try:
                    with open(instructions_file, 'r') as f:
                        saved_instructions = json.load(f)
                    text_type_instructions.update(saved_instructions)
                except:
                    pass
            
            st.markdown("Edit the style instructions for each text type:")
            
            edited_instructions = {}
            for text_type, instruction in text_type_instructions.items():
                display_name = text_type.replace('_', ' ').title()
                edited_instructions[text_type] = st.text_area(
                    f"**{display_name}**",
                    value=instruction,
                    height=100,
                    key=f"instruction_{text_type}"
                )
            
            if st.button("💾 Save Text Type Instructions", type="primary"):
                try:
                    instructions_file.parent.mkdir(exist_ok=True)
                    with open(instructions_file, 'w') as f:
                        json.dump(edited_instructions, f, indent=2)
                    st.success("✅ Text type instructions saved successfully!")
                    st.info("🔄 Restart the application to apply changes")
                except Exception as e:
                    st.error(f"❌ Failed to save instructions: {e}")
        
        with admin_tab3:
            st.subheader("⚙️ Model Parameters")
            
            # Load current model config
            config_file = Path(__file__).parent.parent / "config" / "model_config.json"
            
            default_config = {
                "default_model": "llama3.1:8b",
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 120,
                "max_retries": 3
            }
            
            current_config = default_config.copy()
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        saved_config = json.load(f)
                    current_config.update(saved_config)
                except:
                    pass
            
            st.markdown("### Default Model Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_model = st.text_input(
                    "Default Model:",
                    value=current_config['default_model'],
                    help="Default Ollama model to use"
                )
                
                new_temperature = st.slider(
                    "Temperature:",
                    min_value=0.0,
                    max_value=2.0,
                    value=float(current_config['temperature']),
                    step=0.1,
                    help="Controls randomness in generation (0.0 = deterministic, 2.0 = very random)"
                )
                
                new_max_tokens = st.number_input(
                    "Max Tokens:",
                    min_value=500,
                    max_value=8000,
                    value=int(current_config['max_tokens']),
                    step=100,
                    help="Maximum number of tokens to generate"
                )
            
            with col2:
                new_timeout = st.number_input(
                    "Timeout (seconds):",
                    min_value=30,
                    max_value=300,
                    value=int(current_config['timeout']),
                    step=10,
                    help="Request timeout in seconds"
                )
                
                new_max_retries = st.number_input(
                    "Max Retries:",
                    min_value=1,
                    max_value=10,
                    value=int(current_config['max_retries']),
                    step=1,
                    help="Maximum number of retry attempts"
                )
            
            # Validation settings
            st.markdown("### Task Validation Settings")
            
            validation_config = current_config.get('validation', {
                'min_word_count': 400,
                'max_word_count': 800,
                'min_questions': 5,
                'max_questions': 6,
                'required_question_types': ['inference', 'vocabulary', 'detail']
            })
            
            col1, col2 = st.columns(2)
            
            with col1:
                min_words = st.number_input(
                    "Min Word Count:",
                    min_value=200,
                    max_value=1000,
                    value=validation_config['min_word_count'],
                    help="Minimum words in generated text"
                )
                
                max_words = st.number_input(
                    "Max Word Count:",
                    min_value=500,
                    max_value=1500,
                    value=validation_config['max_word_count'],
                    help="Maximum words in generated text"
                )
            
            with col2:
                min_questions = st.number_input(
                    "Min Questions:",
                    min_value=3,
                    max_value=8,
                    value=validation_config['min_questions'],
                    help="Minimum number of questions"
                )
                
                max_questions = st.number_input(
                    "Max Questions:",
                    min_value=5,
                    max_value=10,
                    value=validation_config['max_questions'],
                    help="Maximum number of questions"
                )
            
            if st.button("💾 Save Model Configuration", type="primary"):
                new_config = {
                    "default_model": new_model,
                    "temperature": new_temperature,
                    "max_tokens": new_max_tokens,
                    "timeout": new_timeout,
                    "max_retries": new_max_retries,
                    "validation": {
                        "min_word_count": min_words,
                        "max_word_count": max_words,
                        "min_questions": min_questions,
                        "max_questions": max_questions,
                        "required_question_types": validation_config['required_question_types']
                    },
                    "last_updated": str(datetime.now())
                }
                
                try:
                    config_file.parent.mkdir(exist_ok=True)
                    with open(config_file, 'w') as f:
                        json.dump(new_config, f, indent=2)
                    st.success("✅ Model configuration saved successfully!")
                    st.info("🔄 Restart the application to apply changes")
                except Exception as e:
                    st.error(f"❌ Failed to save configuration: {e}")
        
        with admin_tab4:
            st.subheader("📚 Knowledge Base Management")
            
            # Display current knowledge base files
            knowledge_base_dir = Path(__file__).parent.parent / "knowledge_base"
            
            if knowledge_base_dir.exists():
                kb_files = list(knowledge_base_dir.glob("*.json"))
                
                st.markdown("### Current Knowledge Base Files")
                for kb_file in kb_files:
                    with st.expander(f"📄 {kb_file.name}"):
                        try:
                            with open(kb_file, 'r') as f:
                                kb_content = json.load(f)
                            
                            st.json(kb_content, expanded=False)
                            
                            # Edit button for each file
                            if st.button(f"✏️ Edit {kb_file.name}", key=f"edit_{kb_file.name}"):
                                st.session_state[f"editing_{kb_file.name}"] = True
                            
                            # Edit mode
                            if st.session_state.get(f"editing_{kb_file.name}", False):
                                edited_content = st.text_area(
                                    f"Edit {kb_file.name}:",
                                    value=json.dumps(kb_content, indent=2),
                                    height=300,
                                    key=f"content_{kb_file.name}"
                                )
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"💾 Save {kb_file.name}", key=f"save_{kb_file.name}"):
                                        try:
                                            new_content = json.loads(edited_content)
                                            with open(kb_file, 'w') as f:
                                                json.dump(new_content, f, indent=2)
                                            st.success(f"✅ {kb_file.name} saved successfully!")
                                            st.session_state[f"editing_{kb_file.name}"] = False
                                            st.rerun()
                                        except json.JSONDecodeError as e:
                                            st.error(f"❌ Invalid JSON: {e}")
                                        except Exception as e:
                                            st.error(f"❌ Failed to save: {e}")
                                
                                with col2:
                                    if st.button(f"❌ Cancel", key=f"cancel_{kb_file.name}"):
                                        st.session_state[f"editing_{kb_file.name}"] = False
                                        st.rerun()
                        
                        except Exception as e:
                            st.error(f"Error loading {kb_file.name}: {e}")
            
            # Topic sets management
            st.markdown("### Topic Sets Management")
            
            # Load current topic sets
            topic_sets_file = Path(__file__).parent.parent / "config" / "topic_sets.json"
            
            default_topic_sets = {
                "Travel & Adventure": [
                    "sustainable travel and eco-tourism",
                    "adventure sports and personal challenges",
                    "cultural exchange through travel",
                    "digital nomad lifestyle"
                ],
                "Technology & Modern Life": [
                    "artificial intelligence in everyday life",
                    "social media influence on relationships",
                    "remote work and productivity",
                    "digital wellness and screen time"
                ],
                "Environment & Sustainability": [
                    "urban gardening and community spaces",
                    "renewable energy solutions for homes",
                    "climate change adaptation strategies",
                    "sustainable fashion and consumption"
                ],
                "Personal Development": [
                    "mindfulness and mental health awareness",
                    "lifelong learning and skill development",
                    "creative hobbies and self-expression",
                    "work-life balance strategies"
                ]
            }
            
            current_topic_sets = default_topic_sets.copy()
            if topic_sets_file.exists():
                try:
                    with open(topic_sets_file, 'r') as f:
                        saved_topic_sets = json.load(f)
                    current_topic_sets.update(saved_topic_sets)
                except:
                    pass
            
            # Edit topic sets
            edited_topic_sets = {}
            for category, topics in current_topic_sets.items():
                st.markdown(f"**{category}**")
                topics_text = '\n'.join(topics)
                edited_topics_text = st.text_area(
                    f"Topics for {category} (one per line):",
                    value=topics_text,
                    height=100,
                    key=f"topics_{category}"
                )
                edited_topic_sets[category] = [topic.strip() for topic in edited_topics_text.split('\n') if topic.strip()]
            
            if st.button("💾 Save Topic Sets", type="primary"):
                try:
                    topic_sets_file.parent.mkdir(exist_ok=True)
                    with open(topic_sets_file, 'w') as f:
                        json.dump(edited_topic_sets, f, indent=2)
                    st.success("✅ Topic sets saved successfully!")
                    st.info("🔄 Restart the application to apply changes")
                except Exception as e:
                    st.error(f"❌ Failed to save topic sets: {e}")

    with tab6:
        st.header("🧪 Test Save Functionality")
        st.markdown("Test the task saving system without generating new tasks")
        
        # Create a sample task for testing
        st.subheader("📝 Sample Task for Testing")
        
        sample_task = {
            "task_id": "test_save_task_01",
            "title": "Test Task: Sustainable Living in Urban Areas",
            "topic": "sustainable living",
            "topic_category": "environment_sustainability",
            "difficulty": "B2",
            "generated_by": "test_system",
            "model": "test_model",
            "generation_params": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "model_full_name": "test_model"
            },
            "text_type": "magazine_article",
            "text": """Living sustainably in a city might seem challenging, but it's becoming increasingly achievable thanks to innovative solutions and changing attitudes. Urban dwellers are discovering that small changes in their daily routines can make a significant environmental impact.

One of the most effective approaches is reducing energy consumption at home. Simple modifications like switching to LED lighting, using programmable thermostats, and choosing energy-efficient appliances can cut electricity bills by up to 30%. Many city residents are also embracing renewable energy options, with rooftop solar panels becoming more affordable and accessible.

Transportation represents another area where urban sustainability shines. Cities worldwide are expanding public transport networks and creating bike-sharing programs. Electric scooters and bicycles offer convenient alternatives for short trips, while car-sharing services reduce the need for private vehicle ownership.

The concept of urban farming is revolutionizing how city dwellers think about food production. Vertical gardens, rooftop farms, and community gardens are transforming unused spaces into productive areas. These initiatives not only provide fresh, local produce but also strengthen community bonds and improve air quality.

Waste reduction has become a priority for environmentally conscious urbanites. Zero-waste stores are appearing in neighborhoods, offering package-free shopping experiences. Composting programs, both individual and community-based, are diverting organic waste from landfills and creating valuable soil amendments.

Technology plays a crucial role in supporting sustainable urban living. Smart home systems optimize energy usage, while apps help residents find recycling centers, track their carbon footprint, and connect with local sustainability initiatives. These digital tools make eco-friendly choices more convenient and measurable.

The future of sustainable urban living looks promising as cities implement green building standards, expand renewable energy infrastructure, and prioritize environmental considerations in urban planning. Individual actions, when multiplied across millions of city residents, create substantial positive environmental change.""",
            "questions": [
                {
                    "question_number": 1,
                    "question_text": "According to the text, what is one of the most effective approaches to sustainable urban living?",
                    "options": {
                        "A": "Moving to the countryside",
                        "B": "Reducing energy consumption at home",
                        "C": "Buying more efficient cars",
                        "D": "Installing expensive technology"
                    },
                    "correct_answer": "B",
                    "question_type": "detail"
                },
                {
                    "question_number": 2,
                    "question_text": "The word 'embracing' in paragraph 2 is closest in meaning to:",
                    "options": {
                        "A": "rejecting",
                        "B": "questioning",
                        "C": "accepting enthusiastically",
                        "D": "considering carefully"
                    },
                    "correct_answer": "C",
                    "question_type": "vocabulary"
                },
                {
                    "question_number": 3,
                    "question_text": "What does the text suggest about urban farming?",
                    "options": {
                        "A": "It only provides food for individual families",
                        "B": "It requires expensive equipment to be successful",
                        "C": "It transforms unused spaces and strengthens communities",
                        "D": "It is only possible in certain types of buildings"
                    },
                    "correct_answer": "C",
                    "question_type": "inference"
                },
                {
                    "question_number": 4,
                    "question_text": "According to the text, zero-waste stores:",
                    "options": {
                        "A": "are only found in wealthy neighborhoods",
                        "B": "offer package-free shopping experiences",
                        "C": "are more expensive than regular stores",
                        "D": "only sell organic products"
                    },
                    "correct_answer": "B",
                    "question_type": "detail"
                },
                {
                    "question_number": 5,
                    "question_text": "What role does technology play in sustainable urban living?",
                    "options": {
                        "A": "It replaces the need for individual action",
                        "B": "It makes eco-friendly choices more convenient and measurable",
                        "C": "It is too expensive for most city residents",
                        "D": "It only works in new buildings"
                    },
                    "correct_answer": "B",
                    "question_type": "detail"
                },
                {
                    "question_number": 6,
                    "question_text": "The overall tone of the text towards sustainable urban living is:",
                    "options": {
                        "A": "pessimistic and doubtful",
                        "B": "neutral and factual",
                        "C": "optimistic and encouraging",
                        "D": "critical and disapproving"
                    },
                    "correct_answer": "C",
                    "question_type": "attitude"
                }
            ]
        }
        
        # Display the sample task
        with st.expander("👀 Preview Sample Task", expanded=False):
            st.json(sample_task, expanded=False)
        
        # Test save functionality
        st.subheader("💾 Test Save Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Test 1: Basic Save**")
            if st.button("🧪 Test Basic Save", type="primary"):
                try:
                    # Initialize generator for testing
                    generator = OllamaTaskGenerator()
                    
                    with st.spinner("Testing save functionality..."):
                        filepath = generator.save_task(sample_task)
                        st.success(f"✅ Save test successful!")
                        st.info(f"📁 File saved to: `{filepath}`")
                        
                        # Verify the file was actually created
                        if filepath.exists():
                            file_size = filepath.stat().st_size
                            st.success(f"✅ File verification passed (Size: {file_size} bytes)")
                        else:
                            st.error("❌ File verification failed - file not found")
                            
                except Exception as e:
                    st.error(f"❌ Save test failed: {str(e)}")
                    with st.expander("🔧 Error Details"):
                        st.code(str(e))
                        st.markdown("""
                        **Possible causes:**
                        - Directory permissions issue
                        - Disk space full
                        - Invalid file path
                        - File system error
                        """)
        
        with col2:
            st.markdown("**Test 2: Custom Task ID**")
            custom_task_id = st.text_input("Custom Task ID:", value="test_custom_save_01")
            
            if st.button("🧪 Test Custom ID Save"):
                try:
                    # Modify sample task with custom ID
                    test_task = sample_task.copy()
                    test_task['task_id'] = custom_task_id
                    
                    generator = OllamaTaskGenerator()
                    
                    with st.spinner("Testing custom ID save..."):
                        filepath = generator.save_task(test_task)
                        st.success(f"✅ Custom ID save successful!")
                        st.info(f"📁 File saved to: `{filepath}`")
                        
                except Exception as e:
                    st.error(f"❌ Custom ID save failed: {str(e)}")
        
        # Directory and permissions test
        st.subheader("📁 Directory & Permissions Test")
        
        if st.button("🔍 Check Save Directory"):
            try:
                generator = OllamaTaskGenerator()
                output_dir = generator.output_dir
                
                st.info(f"📂 Output directory: `{output_dir}`")
                
                # Check if directory exists
                if output_dir.exists():
                    st.success("✅ Directory exists")
                    
                    # Check if writable
                    test_file = output_dir / "write_test.tmp"
                    try:
                        test_file.write_text("test")
                        test_file.unlink()  # Delete test file
                        st.success("✅ Directory is writable")
                    except Exception as e:
                        st.error(f"❌ Directory not writable: {e}")
                    
                    # List existing files
                    existing_files = list(output_dir.glob("*.json"))
                    st.info(f"📄 Existing task files: {len(existing_files)}")
                    
                    if existing_files:
                        with st.expander("📋 Existing Files"):
                            for file in existing_files[-10:]:  # Show last 10 files
                                st.text(f"• {file.name}")
                else:
                    st.warning("⚠️ Directory does not exist")
                    
                    # Try to create it
                    if st.button("🔨 Create Directory"):
                        try:
                            output_dir.mkdir(parents=True, exist_ok=True)
                            st.success("✅ Directory created successfully")
                        except Exception as e:
                            st.error(f"❌ Failed to create directory: {e}")
                            
            except Exception as e:
                st.error(f"❌ Directory check failed: {e}")
        
        # Cleanup test files
        st.subheader("🧹 Cleanup Test Files")
        
        if st.button("🗑️ Remove Test Files"):
            try:
                generator = OllamaTaskGenerator()
                output_dir = generator.output_dir
                
                # Find test files
                test_files = list(output_dir.glob("test_*.json"))
                
                if test_files:
                    for test_file in test_files:
                        test_file.unlink()
                    st.success(f"✅ Removed {len(test_files)} test files")
                else:
                    st.info("ℹ️ No test files found to remove")
                    
            except Exception as e:
                st.error(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    main() 