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
import random

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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Generate Tasks", "🔧 Improve Tasks", "📊 Batch Generation", "📚 Task Library", "⚙️ Admin Panel", "📖 Docs"])
    
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
            
            # Comprehensive B2 First Topic Categories
            topic_categories = {
                "🏃‍♂️ Sport & Fitness": [
                    "extreme sports and risk-taking",
                    "fitness trends for busy professionals",
                    "team sports vs individual activities",
                    "mental health benefits of exercise",
                    "sports nutrition for amateur athletes"
                ],
                "🌍 Environment & Sustainability": [
                    "sustainable travel and eco-tourism",
                    "urban gardening and community spaces",
                    "renewable energy solutions for homes",
                    "plastic-free lifestyle challenges",
                    "climate change adaptation strategies"
                ],
                "💰 Money & Economics": [
                    "financial literacy for young adults",
                    "sustainable shopping and ethical consumption",
                    "side hustles and passive income",
                    "cryptocurrency for beginners",
                    "budgeting for digital nomads"
                ],
                "💼 Work & Business": [
                    "remote work productivity strategies",
                    "career change in your thirties",
                    "entrepreneurship vs traditional employment",
                    "workplace diversity and inclusion",
                    "artificial intelligence in the workplace"
                ],
                "🎓 Education & Learning": [
                    "lifelong learning and skill development",
                    "online education vs traditional classrooms",
                    "language learning through immersion",
                    "creative thinking in problem-solving",
                    "study abroad experiences"
                ],
                "🏠 Family & Relationships": [
                    "work-life balance strategies",
                    "multi-generational living arrangements",
                    "long-distance relationships in digital age",
                    "parenting in the social media era",
                    "friendship maintenance as adults"
                ],
                "🎨 Arts & Culture": [
                    "traditional crafts revival in modern times",
                    "street art as cultural expression",
                    "music festivals and community building",
                    "cultural food exchange and fusion cuisine",
                    "digital art and NFT revolution"
                ],
                "🏥 Health & Medicine": [
                    "mindfulness and mental health awareness",
                    "alternative medicine vs conventional treatment",
                    "nutrition myths and scientific evidence",
                    "sleep optimization for better performance",
                    "preventive healthcare for young adults"
                ],
                "🌐 Technology & Digital Life": [
                    "AI in everyday life applications",
                    "social media influence on relationships",
                    "digital wellness and screen time management",
                    "cybersecurity for personal data protection",
                    "virtual reality in education and training"
                ],
                "✈️ Travel & Adventure": [
                    "digital nomad lifestyle challenges",
                    "adventure sports psychology and motivation",
                    "cultural immersion vs tourist experiences",
                    "solo travel safety and empowerment",
                    "sustainable tourism practices"
                ]
            }
            
            # Category selector for topics
            selected_category = st.selectbox(
                "Choose Topic Category",
                list(topic_categories.keys()),
                key="topic_category_selector"
            )
            
            # Display topics from selected category
            category_topics = topic_categories[selected_category]
            
            st.markdown(f"**{selected_category} Topics:**")
            for i, topic_suggestion in enumerate(category_topics):
                if st.button(f"📝 {topic_suggestion}", key=f"suggest_{selected_category}_{i}"):
                    st.session_state.topic_input = topic_suggestion
                    st.rerun()
            
            # Quick random topic button
            if st.button("🎲 Random Topic", key="random_topic_btn"):
                all_topics = [topic for topics in topic_categories.values() for topic in topics]
                random_topic = random.choice(all_topics)
                st.session_state.topic_input = random_topic
                st.rerun()


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
            "🏃‍♂️ Sport & Fitness Focus": [
                "extreme sports and risk-taking",
                "fitness trends for busy professionals", 
                "team sports vs individual activities",
                "mental health benefits of exercise",
                "sports nutrition for amateur athletes",
                "adventure sports psychology and motivation"
            ],
            "🌍 Environment & Sustainability": [
                "sustainable travel and eco-tourism",
                "urban gardening and community spaces",
                "renewable energy solutions for homes",
                "plastic-free lifestyle challenges",
                "climate change adaptation strategies",
                "sustainable fashion and consumption"
            ],
            "💰 Money & Economics": [
                "financial literacy for young adults",
                "sustainable shopping and ethical consumption",
                "side hustles and passive income",
                "cryptocurrency for beginners",
                "budgeting for digital nomads",
                "economic impact of remote work"
            ],
            "💼 Work & Business": [
                "remote work productivity strategies",
                "career change in your thirties",
                "entrepreneurship vs traditional employment",
                "workplace diversity and inclusion",
                "artificial intelligence in the workplace",
                "work-life balance strategies"
            ],
            "🎓 Education & Learning": [
                "lifelong learning and skill development",
                "online education vs traditional classrooms",
                "language learning through immersion",
                "creative thinking in problem-solving",
                "study abroad experiences",
                "digital literacy for modern students"
            ],
            "🏠 Family & Relationships": [
                "multi-generational living arrangements",
                "long-distance relationships in digital age",
                "parenting in the social media era",
                "friendship maintenance as adults",
                "cultural differences in family structures",
                "community building in urban environments"
            ],
            "🎨 Arts & Culture": [
                "traditional crafts revival in modern times",
                "street art as cultural expression",
                "music festivals and community building",
                "cultural food exchange and fusion cuisine",
                "digital art and NFT revolution",
                "preserving cultural heritage through technology"
            ],
            "🏥 Health & Medicine": [
                "mindfulness and mental health awareness",
                "alternative medicine vs conventional treatment",
                "nutrition myths and scientific evidence",
                "sleep optimization for better performance",
                "preventive healthcare for young adults",
                "mental health stigma in different cultures"
            ],
            "🌐 Technology & Digital Life": [
                "AI in everyday life applications",
                "social media influence on relationships",
                "digital wellness and screen time management",
                "cybersecurity for personal data protection",
                "virtual reality in education and training",
                "ethical implications of artificial intelligence"
            ],
            "✈️ Travel & Adventure": [
                "digital nomad lifestyle challenges",
                "cultural immersion vs tourist experiences",
                "solo travel safety and empowerment",
                "sustainable tourism practices",
                "travel photography and storytelling",
                "adventure travel for personal growth"
            ],
            "🎯 Mixed Contemporary Issues": [
                "social media influence on relationships",
                "climate change adaptation strategies",
                "remote work productivity strategies",
                "mindfulness and mental health awareness",
                "sustainable fashion and consumption",
                "artificial intelligence in the workplace"
            ],
            "🌟 Personal Development": [
                "lifelong learning and skill development",
                "creative thinking in problem-solving",
                "work-life balance strategies",
                "mindfulness and mental health awareness",
                "friendship maintenance as adults",
                "sleep optimization for better performance"
            ],
            "🏙️ Modern Urban Life": [
                "urban gardening and community spaces",
                "multi-generational living arrangements",
                "sustainable shopping and ethical consumption",
                "digital wellness and screen time management",
                "community building in urban environments",
                "street art as cultural expression"
            ],
            "🎓 Student Life & Career": [
                "study abroad experiences",
                "language learning through immersion",
                "career change in your thirties",
                "financial literacy for young adults",
                "online education vs traditional classrooms",
                "workplace diversity and inclusion"
            ],
            "🌱 Wellness & Lifestyle": [
                "nutrition myths and scientific evidence",
                "alternative medicine vs conventional treatment",
                "fitness trends for busy professionals",
                "preventive healthcare for young adults",
                "mental health benefits of exercise",
                "plastic-free lifestyle challenges"
            ],
            "🚀 Innovation & Future": [
                "virtual reality in education and training",
                "cryptocurrency for beginners",
                "digital art and NFT revolution",
                "ethical implications of artificial intelligence",
                "cybersecurity for personal data protection",
                "preserving cultural heritage through technology"
            ]
        }
        
        selected_set = st.selectbox("Choose Topic Set", list(topic_sets.keys()))
        
        # Custom topic set management
        st.markdown("---")
        st.subheader("🎨 Custom Topic Sets")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            custom_topics = st.text_area(
                "Enter Custom Topics (one per line)",
                placeholder="sustainable travel\ndigital wellness\nurban gardening\nAI in education\nremote work challenges",
                height=120,
                help="Enter your own topics, one per line. These will be used instead of the selected topic set above."
            )
        
        with col2:
            st.markdown("**Quick Topic Builders:**")
            
            # Quick topic builders based on common B2 themes
            if st.button("🌍 Environmental Topics", key="env_topics"):
                env_topics = [
                    "sustainable travel and eco-tourism",
                    "renewable energy solutions for homes", 
                    "plastic-free lifestyle challenges",
                    "urban gardening and community spaces",
                    "climate change adaptation strategies"
                ]
                st.session_state.custom_topics_input = "\n".join(env_topics)
                st.rerun()
            
            if st.button("💼 Career & Work Topics", key="work_topics"):
                work_topics = [
                    "remote work productivity strategies",
                    "career change in your thirties",
                    "workplace diversity and inclusion",
                    "artificial intelligence in the workplace",
                    "work-life balance strategies"
                ]
                st.session_state.custom_topics_input = "\n".join(work_topics)
                st.rerun()
            
            if st.button("🎓 Education Topics", key="edu_topics"):
                edu_topics = [
                    "online education vs traditional classrooms",
                    "language learning through immersion",
                    "study abroad experiences",
                    "lifelong learning and skill development",
                    "digital literacy for modern students"
                ]
                st.session_state.custom_topics_input = "\n".join(edu_topics)
                st.rerun()
            
            if st.button("🏥 Health & Wellness", key="health_topics"):
                health_topics = [
                    "mindfulness and mental health awareness",
                    "nutrition myths and scientific evidence",
                    "fitness trends for busy professionals",
                    "sleep optimization for better performance",
                    "preventive healthcare for young adults"
                ]
                st.session_state.custom_topics_input = "\n".join(health_topics)
                st.rerun()
            
            if st.button("🎲 Random Mix", key="random_mix"):
                all_topics = [topic for topics in topic_sets.values() for topic in topics]
                random_topics = random.sample(all_topics, min(6, len(all_topics)))
                st.session_state.custom_topics_input = "\n".join(random_topics)
                st.rerun()
        
        # Apply session state to text area if set
        if 'custom_topics_input' in st.session_state:
            custom_topics = st.session_state.custom_topics_input
            del st.session_state.custom_topics_input
        
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
            topic_source = "Custom Topics"
        else:
            topics_to_use = topic_sets[selected_set]
            topic_source = selected_set
        
        # Topic Preview and Statistics
        st.markdown("---")
        st.subheader("📊 Batch Generation Preview")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Topic Source:** {topic_source}")
            st.markdown(f"**Topics to Generate ({len(topics_to_use)}):**")
            
            # Show topics in a nice format
            for i, topic in enumerate(topics_to_use, 1):
                st.markdown(f"{i}. {topic}")
        
        with col2:
            st.metric("📝 Topics", len(topics_to_use))
            st.metric("📄 Text Types", len(selected_text_types))
            st.metric("🔢 Tasks per Topic", tasks_per_topic)
        
        with col3:
            total_tasks = len(topics_to_use) * len(selected_text_types) * tasks_per_topic
            st.metric("🎯 Total Tasks", total_tasks)
            
            # Estimated time (based on ~30 seconds per task with step-by-step generation)
            estimated_minutes = (total_tasks * 30) / 60
            if estimated_minutes < 60:
                time_estimate = f"{estimated_minutes:.0f} min"
            else:
                hours = estimated_minutes / 60
                time_estimate = f"{hours:.1f} hrs"
            
            st.metric("⏱️ Est. Time", time_estimate)
            
            # Show generation approach
            st.info("🚀 Using step-by-step LLM generation for high quality")
        
        # Show detailed breakdown if more than 6 total tasks
        if total_tasks > 6:
            with st.expander("📋 Detailed Generation Plan", expanded=False):
                st.markdown("**Task Distribution:**")
                
                for topic in topics_to_use:
                    st.markdown(f"**{topic}:**")
                    for text_type in selected_text_types:
                        text_type_display = text_type.replace('_', ' ').title()
                        task_count = tasks_per_topic
                        st.markdown(f"  • {text_type_display}: {task_count} task{'s' if task_count > 1 else ''}")
                
                st.markdown("---")
                st.markdown("**Quality Assurance:**")
                st.markdown("• ✅ Each task validated for B2 First standards")
                st.markdown("• ✅ 400-800 word texts with 5-6 questions")
                st.markdown("• ✅ Auto-save in timestamped batch folder")
                st.markdown("• ✅ Comprehensive batch summary generated")
        
        total_tasks = len(topics_to_use) * len(selected_text_types) * tasks_per_topic
        
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
                    ["🎓 Learner View", "📋 Summary", "🔧 Full Details"],
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
                            task['file_path'] = task_file
                            task['word_count'] = len(task.get('text', '').split())
                            tasks_data.append(task)
                    except Exception as e:
                        st.warning(f"Could not load {task_file.name}: {e}")
                
                if not tasks_data:
                    st.error("No valid tasks could be loaded.")
                    return
                
                # Filter and sort controls
                col1, col2, col3, col4 = st.columns(4)
                
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
                    # Sort options
                    sort_option = st.selectbox(
                        "Sort by",
                        ["Task ID ↑", "Task ID ↓", "Title A-Z", "Title Z-A", "Word Count ↑", "Word Count ↓", "Recent First"],
                        index=0,
                        key="individual_sort_option"
                    )
                
                with col4:
                    # Search
                    search_term = st.text_input(
                        "Search",
                        placeholder="Search titles, topics...",
                        key="individual_search"
                    )
                
                # Apply filters
                filtered_tasks = tasks_data.copy()
                
                if topic_filter != "All Topics":
                    filtered_tasks = [t for t in filtered_tasks if t.get('topic_category') == topic_filter]
                
                if text_type_filter != "All Types":
                    filtered_tasks = [t for t in filtered_tasks if t.get('text_type') == text_type_filter]
                
                if search_term:
                    search_lower = search_term.lower()
                    filtered_tasks = [t for t in filtered_tasks if 
                                    search_lower in t.get('title', '').lower() or 
                                    search_lower in t.get('topic_category', '').lower() or
                                    search_lower in t.get('text_type', '').lower()]
                
                # Apply sorting
                if sort_option == "Task ID ↑":
                    filtered_tasks.sort(key=lambda x: x.get('task_id', ''))
                elif sort_option == "Task ID ↓":
                    filtered_tasks.sort(key=lambda x: x.get('task_id', ''), reverse=True)
                elif sort_option == "Title A-Z":
                    filtered_tasks.sort(key=lambda x: x.get('title', '').lower())
                elif sort_option == "Title Z-A":
                    filtered_tasks.sort(key=lambda x: x.get('title', '').lower(), reverse=True)
                elif sort_option == "Word Count ↑":
                    filtered_tasks.sort(key=lambda x: x.get('word_count', 0))
                elif sort_option == "Word Count ↓":
                    filtered_tasks.sort(key=lambda x: x.get('word_count', 0), reverse=True)
                elif sort_option == "Recent First":
                    filtered_tasks.sort(key=lambda x: x.get('file_path').stat().st_mtime, reverse=True)
                
                # Display results summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Tasks", len(tasks_data))
                with col2:
                    st.metric("🔍 Filtered Results", len(filtered_tasks))
                with col3:
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
                for i, task in enumerate(filtered_tasks):
                    title = task.get('title', 'Untitled')
                    if len(title) > 50:
                        title = title[:47] + "..."
                    
                    option = f"{task.get('task_id', f'Task {i+1}')} - {title}"
                    task_options.append(option)
                
                selected_task_index = st.selectbox(
                    f"Select Task to View ({len(filtered_tasks)} available)",
                    range(len(task_options)),
                    format_func=lambda x: task_options[x],
                    key="selected_individual_task"
                )
                
                if selected_task_index is not None:
                    selected_task = filtered_tasks[selected_task_index]
                    
                    # Quick actions for selected task
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("📄 View Task", key="view_selected_task"):
                            st.session_state.show_selected_task = True
                    
                    with col2:
                        # Download individual task (exclude non-serializable fields)
                        task_data_for_download = {k: v for k, v in selected_task.items() 
                                                if k not in ['file_path', 'filename']}
                        task_json = json.dumps(task_data_for_download, indent=2)
                        st.download_button(
                            label="💾 Download JSON",
                            data=task_json,
                            file_name=selected_task.get('filename', 'task.json'),
                            mime="application/json",
                            key="download_selected_task"
                        )
                    
                    with col3:
                        if st.button("🗑️ Delete Task", key="delete_selected_task"):
                            st.session_state.confirm_delete_task = selected_task_index
                    
                    with col4:
                        # Task info
                        st.caption(f"📝 {selected_task.get('word_count', 0)} words | 🎯 {selected_task.get('text_type', 'Unknown')}")
                    
                    # Confirmation for deletion
                    if st.session_state.get('confirm_delete_task') == selected_task_index:
                        st.warning("⚠️ Are you sure you want to delete this task?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Yes, Delete", key="confirm_delete_yes"):
                                try:
                                    selected_task['file_path'].unlink()
                                    st.success("Task deleted successfully!")
                                    st.session_state.confirm_delete_task = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting task: {e}")
                        with col2:
                            if st.button("❌ Cancel", key="confirm_delete_no"):
                                st.session_state.confirm_delete_task = None
                                st.rerun()
                    
                    # Display selected task
                    if st.session_state.get('show_selected_task', False):
                        st.divider()
                        st.subheader(f"📖 {selected_task.get('title', 'Untitled Task')}")
                        
                        if view_mode == "🎓 Learner View":
                            display_task_learner_view(selected_task)
                        elif view_mode == "📋 Summary":
                            display_task_summary_view(selected_task)
                        elif view_mode == "🔧 Full Details":
                            display_task_json_view(selected_task)
            
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
                    
                    # Batch info display
                    st.info(f"📊 **{selected_batch['task_count']} tasks** | 🕒 Created: {datetime.fromtimestamp(selected_batch['created']).strftime('%Y-%m-%d %H:%M:%S')}")
                    
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
                                        batch_tasks.append(task)
                                except Exception as e:
                                    st.warning(f"Could not load {task_file.name}: {e}")
                            
                            if batch_tasks:
                                # Sort by task ID
                                batch_tasks.sort(key=lambda x: x.get('task_id', ''))
                                
                                # Task selection within batch
                                task_options = []
                                for task in batch_tasks:
                                    title = task.get('title', 'Untitled')
                                    if len(title) > 40:
                                        title = title[:37] + "..."
                                    task_options.append(f"{task.get('task_id', 'Unknown')} - {title}")
                                
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
                        else:
                            st.warning("No task files found in this batch.")
        else:
            st.info("Generated tasks directory not found. Generate some tasks first!")

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

    # Documentation Tab
    with tab6:
        st.header("📖 Documentation")
        
        # Simple approach - load and display the topic selection guide directly
        st.subheader("📋 B2 First Topic Selection Guide")
        
        try:
            docs_path = Path("docs/topic_selection_guide.md")
            if docs_path.exists():
                with open(docs_path, 'r', encoding='utf-8') as f:
                    guide_content = f.read()
                st.markdown(guide_content)
                st.success(f"✅ Documentation loaded successfully")
            else:
                st.error("📄 Topic Selection Guide not found")
                st.info(f"🔍 Looking for: {docs_path.resolve()}")
                st.info(f"📍 Current directory: {Path.cwd()}")
                
        except Exception as e:
            st.error(f"❌ Error loading documentation: {str(e)}")
            st.info("Please check that the docs/topic_selection_guide.md file exists and is readable.")
        
        # Add additional documentation sections directly
        st.markdown("---")
        st.subheader("🎯 B2 First Standards")
        st.markdown("""
        ### Cambridge B2 First Reading Part 5 Requirements
        
        **Text Specifications:**
        - **Length**: 400-800 words (flexible range for quality content)
        - **Level**: Intermediate to Upper-Intermediate (B2)
        - **Topics**: Age-appropriate, culturally neutral, contemporary relevance
        
        **Question Requirements:**
        - **Number**: 5-6 questions per task
        - **Types**: Inference, vocabulary, detail, attitude, reference, main idea
        - **Format**: Multiple choice with 4 options (A, B, C, D)
        - **Answer Key**: One correct answer per question
        """)
        
        st.markdown("---")
        st.subheader("🔧 Technical Specifications")
        st.markdown("""
        ### System Architecture
        
        **Core Components:**
        - **LLM Integration**: Ollama with local models (Llama 3.1, Mistral)
        - **Content Generation**: Step-by-step task creation with validation
        - **JSON Processing**: Robust parsing with error recovery
        - **File Management**: Auto-save, batch processing, organized storage
        
        **Text Types Available:**
        - Magazine Article, Blog Post, News Report, Professional Feature
        - Educational Feature, Cultural Review, Travel Writing, Lifestyle Feature
        - Opinion Piece, Novel Extract
        """)
        
        st.markdown("---")
        st.subheader("💡 Best Practices")
        st.markdown("""
        ### Content Creation Guidelines
        
        **Topic Selection:**
        - Choose contemporary, relevant subjects
        - Ensure cultural neutrality and age appropriateness
        - Balance familiar and challenging concepts
        
        **Quality Control:**
        - Review generated content for accuracy
        - Check cultural sensitivity
        - Verify language level appropriateness
        - Test questions with target learners
        """)

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
        # Filter out non-serializable fields for download
        task_data_clean = {k: v for k, v in task.items() 
                          if k not in ['file_path', 'filename']}
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
            task_data_clean = {k: v for k, v in task.items() 
                              if k not in ['file_path', 'filename']}
            st.json(task_data_clean)

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
            # Filter out non-serializable fields for download
            task_data_clean = {k: v for k, v in task.items() 
                              if k not in ['file_path', 'filename']}
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(task_data_clean, indent=2),
                file_name=f"{task.get('task_id', 'task')}.json",
                mime="application/json",
                key=f"download_summary_{task.get('task_id', 'unknown')}"
            )
        with col2:
            if st.button(f"📖 View Full Task", key=f"view_summary_{task.get('task_id', 'unknown')}"):
                # Filter out non-serializable fields for JSON display
                task_data_clean = {k: v for k, v in task.items() 
                                  if k not in ['file_path', 'filename']}
                st.json(task_data_clean)

def display_task_json_view(task):
    """Display a task in JSON format"""
    text_type_display = task.get('text_type', 'unknown').replace('_', ' ').title()
    
    # Filter out non-serializable fields for display and download
    task_data_clean = {k: v for k, v in task.items() 
                      if k not in ['file_path', 'filename']}
    
    with st.expander(f"🔧 {task.get('title', 'Untitled')} - JSON Data"):
        st.json(task_data_clean)
        
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(task_data_clean, indent=2),
            file_name=f"{task.get('task_id', 'task')}.json",
            mime="application/json",
            key=f"download_json_{task.get('task_id', 'unknown')}"
        )

def display_task_learner_view_simple(task, context="batch"):
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
        # Filter out non-serializable fields for download
        task_data_clean = {k: v for k, v in task.items() 
                          if k not in ['file_path', 'filename']}
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
            task_data_clean = {k: v for k, v in task.items() 
                              if k not in ['file_path', 'filename']}
            st.json(task_data_clean)

if __name__ == "__main__":
    main() 