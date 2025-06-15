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
    
    # Auto-save option
    st.sidebar.subheader("💾 Save Settings")
    auto_save = st.sidebar.checkbox(
        "Auto-save generated tasks",
        value=st.session_state.get('auto_save_enabled', False),
        help="Automatically save tasks to the generated_tasks folder after generation"
    )
    st.session_state['auto_save_enabled'] = auto_save
    
    if auto_save:
        st.sidebar.success("✅ Auto-save enabled")
    else:
        st.sidebar.info("💡 Manual save required")
    
    # Main interface tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Generate Tasks", "🔧 Improve Tasks", "📊 Batch Generation", "📚 Task Library", "⚙️ Admin Panel"])
    
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
        


        # Persistent Save Section - appears when there's a generated task
        if 'generated_task' in st.session_state and st.session_state.generated_task:
            st.markdown("---")
            st.subheader("💾 Save Generated Task")
            
            task_to_save = st.session_state.generated_task
            generator_to_use = st.session_state.get('task_generator')
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("💾 Save Task", type="primary", key="persistent_save_btn"):
                    if generator_to_use:
                        try:
                            with st.spinner("Saving task..."):
                                filepath = generator_to_use.save_task(task_to_save)
                                
                                if filepath.exists():
                                    file_size = filepath.stat().st_size
                                    st.success(f"✅ Task saved: `{filepath.name}` ({file_size} bytes)")
                                    
                                    # Clear session state after successful save
                                    del st.session_state.generated_task
                                    del st.session_state.task_generator
                                    st.rerun()
                                else:
                                    st.error("❌ Save failed - file not created")
                        except Exception as e:
                            st.error(f"❌ Save error: {str(e)}")
                    else:
                        st.error("❌ No generator available - please regenerate the task")
            
            with col2:
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(task_to_save, indent=2),
                    file_name=f"{task_to_save['task_id']}.json",
                    mime="application/json",
                    key="persistent_download_btn"
                )
            
            with col3:
                st.info(f"📋 **{task_to_save.get('title', 'Unknown Task')}**")
                if st.button("🗑️ Clear Task", key="clear_task_btn"):
                    del st.session_state.generated_task
                    del st.session_state.task_generator
                    st.rerun()
            
            st.markdown("---")

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
                    
                    # Store task in session state for saving
                    st.session_state.generated_task = task_data
                    st.session_state.task_generator = generator
                    
                    # Display results
                    st.success("✅ Task generated successfully!")
                    
                    # Auto-save option
                    if st.session_state.get('auto_save_enabled', False):
                        try:
                            with st.spinner("Auto-saving task..."):
                                filepath = generator.save_task(task_data)
                                st.success(f"✅ Task auto-saved to: {filepath.name}")
                        except Exception as e:
                            st.warning(f"⚠️ Auto-save failed: {str(e)}")
                            st.info("💡 You can still save manually using the Save Task button below")
                    
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
                    
                    # Store task in session state for persistent save functionality
                    st.session_state.generated_task = task_data
                    st.session_state.task_generator = generator
                    
                    # Show download option immediately
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(task_data, indent=2),
                        file_name=f"{task_data['task_id']}.json",
                        mime="application/json",
                        key="immediate_download_btn"
                    )
                    
                    st.markdown("---")
                    
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
        
        # Custom instructions for batch generation
        st.subheader("📝 Custom Instructions (Optional)")
        batch_custom_instructions = st.text_area(
            "Additional instructions for all tasks in this batch",
            placeholder="e.g., Focus on environmental benefits, include specific statistics, target young adults...",
            help="These instructions will be applied to all tasks in the batch generation"
        )
        
        # Determine topics to use
        if custom_topics.strip():
            topics_to_use = [topic.strip() for topic in custom_topics.split('\n') if topic.strip()]
        else:
            topics_to_use = topic_sets[selected_set]
        
        total_tasks = len(topics_to_use) * len(selected_text_types) * tasks_per_topic
        st.info(f"Will generate {len(topics_to_use)} topics × {len(selected_text_types)} text types × {tasks_per_topic} tasks = **{total_tasks} total tasks**")
        
        # Show batch folder info
        if total_tasks > 0:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_folder_name = f"batch_{timestamp}_{len(topics_to_use)}topics_{len(selected_text_types)}types"
            st.info(f"📁 Tasks will be saved in subfolder: `{batch_folder_name}`")
        
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
                
                import time
                batch_start_time = time.time()
                
                # Update initial status
                overall_progress.progress(0.1)
                status_text.text("📁 Creating batch folder and initializing...")
                current_task_text.text("🚀 Starting batch generation with auto-save...")
                
                # Use the new batch generation method with auto-save and subfolder creation
                completed_tasks = generator.generate_batch_tasks(
                    topics=topics_to_use,
                    text_types=selected_text_types,
                    tasks_per_topic=tasks_per_topic,
                    custom_instructions=batch_custom_instructions.strip() if batch_custom_instructions.strip() else None
                )
                
                # Simulate progress updates for UI feedback
                for i in range(total_tasks):
                    progress = (i + 1) / total_tasks
                    overall_progress.progress(progress)
                    current_task_progress.progress(progress)
                    
                    if i < len(completed_tasks):
                        task = completed_tasks[i]
                        status_text.text(f"📝 Completed task {i+1}/{total_tasks}")
                        current_task_text.text(f"✅ Generated: {task['title'][:50]}...")
                        
                        # Update metrics
                        col1.metric("✅ Successful", i + 1)
                        col3.metric("🤖 Ollama Generated", i + 1)  # All tasks use Ollama now
                        
                        # Update log
                        task_log.markdown(f"**Latest:** ✅ {task['task_id']} - {task['title']}")
                    
                    time.sleep(0.1)  # Brief delay for visual feedback
                
                # Final completion
                batch_time = time.time() - batch_start_time
                overall_progress.progress(1.0)
                current_task_progress.progress(1.0)
                status_text.text(f"🎉 Batch generation complete! ({batch_time:.1f}s total)")
                current_task_text.text(f"✅ Generated {len(completed_tasks)} tasks with auto-save")
                
                # Update final metrics
                success_count = len(completed_tasks)
                failed_count = total_tasks - success_count
                ollama_count = success_count  # All successful tasks use Ollama
                fallback_count = 0
                
                col1.metric("✅ Successful", success_count)
                col2.metric("❌ Failed", failed_count)
                col3.metric("🤖 Ollama Generated", ollama_count)
                col4.metric("🔄 Fallback Used", fallback_count)
                
                # Final status
                if success_count > 0:
                    success_rate = (success_count / total_tasks) * 100
                    parsing_info.success(f"**Final Status:** {success_rate:.1f}% success rate - All tasks auto-saved in batch subfolder")
                    
                    # Show batch folder info
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    batch_folder_name = f"batch_{timestamp}_{len(topics_to_use)}topics_{len(selected_text_types)}types"
                    current_attempts.success(f"**Batch Folder:** `generated_tasks/{batch_folder_name}/`")
                else:
                    parsing_info.error("**Final Status:** No tasks generated successfully")
                
                # Show task summary
                if completed_tasks:
                    task_summaries = []
                    for task in completed_tasks[-5:]:  # Show last 5 tasks
                        task_summaries.append(f"✅ {task['task_id']} - {task['title'][:40]}...")
                    task_log.markdown("**Recently Generated:**\n" + "\n".join(task_summaries))
                
                st.success(f"✅ Batch generation complete! Generated {len(completed_tasks)} tasks in {batch_time:.1f} seconds")
                st.info(f"📁 All tasks auto-saved in subfolder with batch summary file")
                
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
        
        # Load and display all generated tasks and batches
        generated_tasks_dir = Path(__file__).parent.parent / "generated_tasks"
        if generated_tasks_dir.exists():
            # Get individual task files and batch directories
            task_files = list(generated_tasks_dir.glob("*.json"))
            batch_dirs = [d for d in generated_tasks_dir.iterdir() if d.is_dir() and d.name.startswith("batch_")]
            
            # Create main tabs for Individual Tasks and Batches
            if task_files or batch_dirs:
                library_tab1, library_tab2 = st.tabs(["📄 Individual Tasks", "📦 Batch Collections"])
                
                # Individual Tasks Tab
                with library_tab1:
                    if task_files:
                        # Action buttons row
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Total Tasks", len(task_files))
                        
                        with col2:
                            if st.button("📥 Download All Tasks", key="download_individual"):
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
                                    file_name="b2_first_individual_tasks.zip",
                                    mime="application/zip",
                                    key="download_individual_zip"
                                )
                        
                        with col3:
                            view_mode = st.selectbox(
                                "View Mode",
                                ["🎓 Learner View", "📋 Summary View", "🔧 JSON View"],
                                index=0,
                                key="individual_view_mode"
                            )
                        
                        with col4:
                            if st.button("🗑️ Clear All Individual Tasks", key="clear_individual"):
                                if st.checkbox("⚠️ Confirm deletion of individual tasks", key="confirm_individual"):
                                    for task_file in task_files:
                                        task_file.unlink()
                                    st.success("All individual tasks deleted!")
                                    st.rerun()
                        
                        st.divider()
                        
                        # Filter options
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            filter_by_generator = st.selectbox(
                                "Filter by Generator",
                                ["All", "ollama", "improved", "fallback"],
                                index=0,
                                key="individual_generator_filter"
                            )
                        
                        with col2:
                            filter_by_text_type = st.selectbox(
                                "Filter by Text Type",
                                ["All"] + [info['key'] for info in B2_TEXT_TYPES.values()],
                                index=0,
                                key="individual_text_type_filter"
                            )
                        
                        with col3:
                            sort_by = st.selectbox(
                                "Sort by",
                                ["Task ID", "Title", "Topic Category", "Word Count"],
                                index=0,
                                key="individual_sort"
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
                            st.info("No individual tasks match the current filters.")
                        else:
                            st.info(f"Showing {len(tasks_data)} individual tasks")
                            
                            # Display tasks based on view mode
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
                        st.info("No individual tasks found. Generate some tasks first!")
                
                # Batch Collections Tab
                with library_tab2:
                    if batch_dirs:
                        # Sort batch directories by creation time (newest first)
                        batch_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                        
                        # Action buttons row
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📦 Total Batches", len(batch_dirs))
                        
                        with col2:
                            if st.button("📥 Download All Batches", key="download_batches"):
                                # Create a zip file with all batch folders
                                import zipfile
                                import io
                                
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                    for batch_dir in batch_dirs:
                                        for file_path in batch_dir.rglob("*"):
                                            if file_path.is_file():
                                                arcname = str(file_path.relative_to(generated_tasks_dir))
                                                zip_file.write(file_path, arcname)
                                
                                st.download_button(
                                    label="💾 Download All Batches ZIP",
                                    data=zip_buffer.getvalue(),
                                    file_name="b2_first_batch_collections.zip",
                                    mime="application/zip",
                                    key="download_batches_zip"
                                )
                        
                        with col3:
                            batch_view_mode = st.selectbox(
                                "Batch View Mode",
                                ["📋 Batch Summary", "🎓 Learner View", "📋 Summary View", "🔧 JSON View"],
                                index=0,
                                key="batch_view_mode"
                            )
                        
                        st.divider()
                        
                        # Display batch collections
                        for batch_dir in batch_dirs:
                            batch_name = batch_dir.name
                            
                            # Load batch summary if available
                            summary_file = batch_dir / "BATCH_SUMMARY.txt"
                            batch_summary = None
                            if summary_file.exists():
                                try:
                                    with open(summary_file, 'r') as f:
                                        batch_summary = f.read()
                                except Exception as e:
                                    st.warning(f"Could not load summary for {batch_name}: {e}")
                            
                            # Get batch task files
                            batch_task_files = list(batch_dir.glob("*.json"))
                            
                            # For Learner View, avoid nested expanders by using a different layout
                            if batch_view_mode == "🎓 Learner View":
                                # Load batch tasks data first
                                batch_tasks_data = []
                                for task_file in batch_task_files:
                                    try:
                                        with open(task_file, 'r') as f:
                                            task = json.load(f)
                                            task['filename'] = task_file.name
                                            batch_tasks_data.append(task)
                                    except Exception as e:
                                        st.warning(f"Could not load {task_file.name}: {e}")
                                
                                # Sort by task ID
                                batch_tasks_data.sort(key=lambda x: x.get('task_id', ''))
                                
                                if batch_tasks_data:
                                    st.markdown(f"### 📦 {batch_name} - Learner View ({len(batch_task_files)} tasks)")
                                    
                                    # Create tabs for individual task viewing (no expander wrapper)
                                    task_names = [f"{task.get('task_id', 'Unknown')} - {task.get('title', 'Untitled')[:25]}..." 
                                                 if len(task.get('title', '')) > 25 
                                                 else f"{task.get('task_id', 'Unknown')} - {task.get('title', 'Untitled')}" 
                                                 for task in batch_tasks_data]
                                    
                                    if len(batch_tasks_data) > 6:
                                        st.warning("⚠️ Too many tasks for tab view in batch. Showing first 6 tasks.")
                                        batch_tasks_data = batch_tasks_data[:6]
                                        task_names = task_names[:6]
                                    
                                    # Use unique keys for batch tabs
                                    batch_tabs = st.tabs(task_names)
                                    
                                    for i, (task, tab) in enumerate(zip(batch_tasks_data, batch_tabs)):
                                        with tab:
                                            # Create a simplified learner view without nested expanders
                                            display_task_learner_view_simple(task)
                                    
                                    # Add batch actions below tabs
                                    st.divider()
                                    st.markdown("### 🔧 Batch Actions")
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        # Download this batch
                                        if st.button(f"📥 Download {batch_name}", key=f"download_{batch_name}"):
                                            import zipfile
                                            import io
                                            
                                            zip_buffer = io.BytesIO()
                                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                                for file_path in batch_dir.rglob("*"):
                                                    if file_path.is_file():
                                                        arcname = str(file_path.relative_to(batch_dir))
                                                        zip_file.write(file_path, arcname)
                                            
                                            st.download_button(
                                                label=f"💾 Download {batch_name}.zip",
                                                data=zip_buffer.getvalue(),
                                                file_name=f"{batch_name}.zip",
                                                mime="application/zip",
                                                key=f"download_{batch_name}_zip"
                                            )
                                    
                                    with col2:
                                        # View batch folder info
                                        if st.button(f"📁 Folder Info", key=f"info_{batch_name}"):
                                            st.info(f"**Path:** {batch_dir}")
                                            st.info(f"**Created:** {datetime.fromtimestamp(batch_dir.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                                            st.info(f"**Size:** {sum(f.stat().st_size for f in batch_dir.rglob('*') if f.is_file())} bytes")
                                    
                                    with col3:
                                        # Delete batch
                                        if st.button(f"🗑️ Delete {batch_name}", key=f"delete_{batch_name}"):
                                            if st.checkbox(f"⚠️ Confirm deletion of {batch_name}", key=f"confirm_delete_{batch_name}"):
                                                import shutil
                                                shutil.rmtree(batch_dir)
                                                st.success(f"Batch {batch_name} deleted!")
                                                st.rerun()
                                else:
                                    st.info(f"No task files found in {batch_name}")
                            
                            else:
                                # For other view modes, use expandable sections
                                with st.expander(f"📦 {batch_name} ({len(batch_task_files)} tasks)", expanded=False):
                                    if batch_view_mode == "📋 Batch Summary":
                                        # Display batch summary
                                        if batch_summary:
                                            st.markdown("### 📊 Batch Summary")
                                            st.text(batch_summary)
                                        else:
                                            st.warning("No batch summary available")
                                        
                                        # Quick stats
                                        if batch_task_files:
                                            st.markdown("### 📈 Quick Stats")
                                            col1, col2, col3 = st.columns(3)
                                            
                                            total_words = 0
                                            total_questions = 0
                                            text_types = set()
                                            
                                            for task_file in batch_task_files:
                                                try:
                                                    with open(task_file, 'r') as f:
                                                        task = json.load(f)
                                                        total_words += len(task.get('text', '').split())
                                                        total_questions += len(task.get('questions', []))
                                                        text_types.add(task.get('text_type', 'unknown'))
                                                except:
                                                    pass
                                            
                                            with col1:
                                                st.metric("Total Words", f"{total_words:,}")
                                            with col2:
                                                st.metric("Total Questions", total_questions)
                                            with col3:
                                                st.metric("Text Types", len(text_types))
                                    
                                    else:
                                        # Display individual tasks in the batch for Summary and JSON view modes
                                        if batch_task_files:
                                            st.markdown(f"### 📄 Tasks in {batch_name}")
                                            
                                            batch_tasks_data = []
                                            for task_file in batch_task_files:
                                                try:
                                                    with open(task_file, 'r') as f:
                                                        task = json.load(f)
                                                        task['filename'] = task_file.name
                                                        batch_tasks_data.append(task)
                                                except Exception as e:
                                                    st.warning(f"Could not load {task_file.name}: {e}")
                                            
                                            # Sort by task ID
                                            batch_tasks_data.sort(key=lambda x: x.get('task_id', ''))
                                            
                                            # Display tasks based on selected view mode
                                            if batch_view_mode == "📋 Summary View":
                                                # Display tasks in summary cards
                                                for task in batch_tasks_data:
                                                    display_task_summary_view(task)
                                            
                                            elif batch_view_mode == "🔧 JSON View":
                                                # Display tasks in JSON format
                                                for task in batch_tasks_data:
                                                    display_task_json_view(task)
                                        else:
                                            st.info("No task files found in this batch")
                                    
                                    # Batch actions
                                    st.markdown("### 🔧 Batch Actions")
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        # Download this batch
                                        if st.button(f"📥 Download {batch_name}", key=f"download_{batch_name}"):
                                            import zipfile
                                            import io
                                            
                                            zip_buffer = io.BytesIO()
                                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                                for file_path in batch_dir.rglob("*"):
                                                    if file_path.is_file():
                                                        arcname = str(file_path.relative_to(batch_dir))
                                                        zip_file.write(file_path, arcname)
                                            
                                            st.download_button(
                                                label=f"💾 Download {batch_name}.zip",
                                                data=zip_buffer.getvalue(),
                                                file_name=f"{batch_name}.zip",
                                                mime="application/zip",
                                                key=f"download_{batch_name}_zip"
                                            )
                                    
                                    with col2:
                                        # View batch folder info
                                        if st.button(f"📁 Folder Info", key=f"info_{batch_name}"):
                                            st.info(f"**Path:** {batch_dir}")
                                            st.info(f"**Created:** {datetime.fromtimestamp(batch_dir.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                                            st.info(f"**Size:** {sum(f.stat().st_size for f in batch_dir.rglob('*') if f.is_file())} bytes")
                                    
                                    with col3:
                                        # Delete batch
                                        if st.button(f"🗑️ Delete {batch_name}", key=f"delete_{batch_name}"):
                                            if st.checkbox(f"⚠️ Confirm deletion of {batch_name}", key=f"confirm_delete_{batch_name}"):
                                                import shutil
                                                shutil.rmtree(batch_dir)
                                                st.success(f"Batch {batch_name} deleted!")
                                                st.rerun()
                    else:
                        st.info("No batch collections found. Use Batch Generation to create batch collections!")
            else:
                st.info("No tasks or batches found. Generate some content first!")
        else:
            st.info("Generated tasks directory not found.")

    with tab5:
        st.header("⚙️ Admin Panel")
        st.markdown("**Configure AI prompts and system parameters**")
        
        # Admin panel content (no authentication for simplicity)
        st.success("🔓 Admin access granted")
        
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
            
            # Save prompts button
            if st.button("💾 Save AI Prompts", type="primary"):
                prompts_to_save = {
                    'main_generation_prompt': edited_system_prompt,
                    'improvement_prompt': edited_improvement_prompt,
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
                "max_retries": 1
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
            
            if st.button("💾 Save Model Configuration", type="primary"):
                new_config = {
                    "default_model": new_model,
                    "temperature": new_temperature,
                    "max_tokens": new_max_tokens,
                    "timeout": new_timeout,
                    "max_retries": new_max_retries,
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
    
    # Custom instructions if available
    if task.get('custom_instructions'):
        st.markdown(f"**📝 Custom Instructions:** {task.get('custom_instructions')}")
    
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
        
        # Custom instructions if available
        if task.get('custom_instructions'):
            st.markdown(f"**📝 Custom Instructions:** {task.get('custom_instructions')}")
        
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

def display_task_learner_view_simple(task):
    """Display a task in a simplified learner view without expanders (for batch view)"""
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
    
    # Custom instructions if available
    if task.get('custom_instructions'):
        st.markdown(f"**📝 Custom Instructions:** {task.get('custom_instructions')}")
    
    # Generation parameters (without expander)
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
        
        # Create text container that shows full content
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
            # Create questions container
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
            key=f"download_simple_{task.get('task_id', 'unknown')}"
        )
    
    with col2:
        if st.button("📋 Copy Text Only", key=f"copy_text_simple_{task.get('task_id', 'unknown')}"):
            st.code(task.get('text', ''), language=None)
    
    with col3:
        if st.button("📊 View JSON", key=f"json_view_simple_{task.get('task_id', 'unknown')}"):
            st.json(task)

if __name__ == "__main__":
    main() 