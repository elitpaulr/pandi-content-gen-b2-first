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

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from llm.ollama_client import OllamaClient, OllamaConfig
    from content.ollama_part5_generator import OllamaTaskGenerator
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Make sure Ollama dependencies are installed")
    st.stop()

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
                with st.spinner(f"Generating task about '{topic}'... This may take 30-60 seconds"):
                    try:
                        # Initialize generator
                        config = OllamaConfig(
                            model=selected_model,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        generator = OllamaTaskGenerator(selected_model)
                        
                        # Generate task
                        task_data = generator.generate_single_task(topic, 1)
                        
                        # Display results
                        st.success("✅ Task generated successfully!")
                        
                        # Task overview
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Word Count", len(task_data['text'].split()))
                        with col2:
                            st.metric("Questions", len(task_data['questions']))
                        with col3:
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
        
        # Predefined topic sets
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
        
        st.info(f"Will generate {len(topics_to_use)} × {tasks_per_topic} = {len(topics_to_use) * tasks_per_topic} tasks")
        
        if st.button("🚀 Start Batch Generation", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                generator = OllamaTaskGenerator(selected_model)
                total_tasks = len(topics_to_use) * tasks_per_topic
                completed_tasks = []
                
                for i, topic in enumerate(topics_to_use):
                    for j in range(tasks_per_topic):
                        task_num = i * tasks_per_topic + j + 1
                        
                        status_text.text(f"Generating task {task_num}/{total_tasks}: {topic}")
                        
                        try:
                            task = generator.generate_single_task(topic, task_num)
                            generator.save_task(task)
                            completed_tasks.append(task)
                            
                            progress_bar.progress(task_num / total_tasks)
                            
                        except Exception as e:
                            st.warning(f"Failed to generate task for '{topic}': {str(e)}")
                
                st.success(f"✅ Batch generation complete! Generated {len(completed_tasks)} tasks")
                
                # Summary
                categories = {}
                for task in completed_tasks:
                    cat = task.get('topic_category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                
                st.subheader("Generation Summary")
                for cat, count in categories.items():
                    st.metric(cat.replace('_', ' ').title(), count)
                
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
                col1, col2 = st.columns(2)
                with col1:
                    filter_by_generator = st.selectbox(
                        "Filter by Generator",
                        ["All", "ollama", "improved", "manual"],
                        index=0
                    )
                
                with col2:
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
                
                # Display tasks
                for task in tasks_data:
                    with st.expander(f"📖 {task.get('title', 'Untitled')} ({task.get('filename', 'unknown')})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Word Count", len(task.get('text', '').split()))
                        with col2:
                            st.metric("Questions", len(task.get('questions', [])))
                        with col3:
                            st.metric("Generator", task.get('generated_by', 'unknown'))
                        
                        if st.button(f"View Full Task", key=f"view_{task.get('task_id', 'unknown')}"):
                            st.json(task)
            else:
                st.info("No tasks found. Generate some tasks first!")
        else:
            st.info("Generated tasks directory not found.")

if __name__ == "__main__":
    main() 