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
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Generate Tasks", "🔧 Improve Tasks", "📊 Batch Generation", "📋 Task Library"])
    
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
                with st.spinner(f"Generating {selected_text_type.lower()} about '{topic}'... This may take 30-60 seconds"):
                    try:
                        # Initialize generator
                        config = OllamaConfig(
                            model=selected_model,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        generator = OllamaTaskGenerator(selected_model)
                        
                        # Generate task with text type
                        task_data = generator.generate_single_task(
                            topic, 
                            1, 
                            text_type=text_type_key,
                            custom_instructions=custom_instructions
                        )
                        
                        # Display results
                        st.success("✅ Task generated successfully!")
                        
                        # Task overview
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Word Count", len(task_data['text'].split()))
                        with col2:
                            st.metric("Questions", len(task_data['questions']))
                        with col3:
                            st.metric("Text Type", selected_text_type.split()[1])
                        with col4:
                            st.metric("Topic Category", task_data.get('topic_category', 'general'))
                        
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
                        
                        # Save option
                        if st.button("💾 Save Task"):
                            filepath = generator.save_task(task_data)
                            st.success(f"Task saved to: {filepath}")
                        
                        # Download JSON
                        st.download_button(
                            label="📥 Download JSON",
                            data=json.dumps(task_data, indent=2),
                            file_name=f"{task_data['task_id']}.json",
                            mime="application/json"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Generation failed: {str(e)}")
    
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
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                generator = OllamaTaskGenerator(selected_model)
                completed_tasks = []
                task_counter = 0
                
                for topic in topics_to_use:
                    for text_type_key in selected_text_types:
                        text_type_name = next(name for name, info in B2_TEXT_TYPES.items() if info['key'] == text_type_key)
                        
                        for j in range(tasks_per_topic):
                            task_counter += 1
                            
                            status_text.text(f"Generating task {task_counter}/{total_tasks}: {text_type_name} about '{topic}'")
                            
                            try:
                                task = generator.generate_single_task(
                                    topic, 
                                    task_counter,
                                    text_type=text_type_key
                                )
                                generator.save_task(task)
                                completed_tasks.append(task)
                                
                                progress_bar.progress(task_counter / total_tasks)
                                
                            except Exception as e:
                                st.warning(f"Failed to generate {text_type_name} for '{topic}': {str(e)}")
                
                st.success(f"✅ Batch generation complete! Generated {len(completed_tasks)} tasks")
                
                # Summary
                text_type_counts = {}
                topic_counts = {}
                for task in completed_tasks:
                    # Count by text type
                    text_type = task.get('text_type', 'unknown')
                    text_type_counts[text_type] = text_type_counts.get(text_type, 0) + 1
                    
                    # Count by topic
                    topic = task.get('topic', 'unknown')
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
                
                st.subheader("Generation Summary")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**By Text Type:**")
                    for text_type, count in text_type_counts.items():
                        st.metric(text_type.replace('_', ' ').title(), count)
                
                with col2:
                    st.markdown("**By Topic:**")
                    for topic, count in list(topic_counts.items())[:5]:  # Show top 5
                        st.metric(topic[:30] + "..." if len(topic) > 30 else topic, count)
                
            except Exception as e:
                st.error(f"❌ Batch generation failed: {str(e)}")
    
    with tab4:
        st.header("Task Library")
        
        # Load and display all generated tasks
        generated_tasks_dir = Path(__file__).parent.parent / "generated_tasks"
        if generated_tasks_dir.exists():
            task_files = list(generated_tasks_dir.glob("*.json"))
            
            if task_files:
                st.info(f"Found {len(task_files)} generated tasks")
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_by_generator = st.selectbox(
                        "Filter by Generator",
                        ["All", "ollama", "improved", "manual"],
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
                        ["Task ID", "Title", "Topic Category"],
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
                
                # Display tasks
                for task in tasks_data:
                    text_type_display = task.get('text_type', 'unknown').replace('_', ' ').title()
                    
                    with st.expander(f"📖 {task.get('title', 'Untitled')} ({text_type_display})"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Word Count", len(task.get('text', '').split()))
                        with col2:
                            st.metric("Questions", len(task.get('questions', [])))
                        with col3:
                            st.metric("Text Type", text_type_display)
                        with col4:
                            st.metric("Generator", task.get('generated_by', 'unknown'))
                        
                        if st.button(f"View Full Task", key=f"view_{task.get('task_id', 'unknown')}"):
                            st.json(task)
            else:
                st.info("No tasks found. Generate some tasks first!")
        else:
            st.info("Generated tasks directory not found.")

if __name__ == "__main__":
    main() 