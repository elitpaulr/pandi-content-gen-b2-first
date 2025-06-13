import streamlit as st
import json
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="B2 First - Reading & Use of English Criteria",
    page_icon="📖",
    layout="wide"
)

def load_reading_criteria():
    """Load the Reading and Use of English criteria from the JSON file."""
    criteria_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "knowledge_base",
        "reading_criteria.json"
    )
    try:
        with open(criteria_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Reading criteria file not found. Please run the criteria extractor first.")
        return None
    except json.JSONDecodeError:
        st.error("Error reading criteria file. The file might be corrupted.")
        return None

def main():
    st.title("📖 B2 First - Reading & Use of English Criteria")
    
    # Load criteria
    criteria_data = load_reading_criteria()
    if not criteria_data:
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Get sections from the criteria data
    sections = criteria_data.get("sections", {})
    
    # Navigation in sidebar
    selected_section = st.sidebar.selectbox(
        "Select Section",
        list(sections.keys())
    )
    
    # Display selected section
    st.header(selected_section.replace("_", " ").title())
    
    # Display section content based on type
    section_content = sections[selected_section]
    
    if selected_section == "overview":
        if "description" in section_content:
            st.markdown(section_content["description"])
    
    elif selected_section == "assessment_criteria":
        if "criteria" in section_content:
            st.subheader("Assessment Criteria")
            for criterion in section_content["criteria"]:
                st.write(f"- {criterion}")
        
        if "content" in section_content:
            st.subheader("Detailed Information")
            st.markdown(section_content["content"])
    
    elif selected_section == "task_types":
        if "tasks" in section_content:
            st.subheader("Task Types")
            for task in section_content["tasks"]:
                with st.expander(f"📝 {task}"):
                    st.write(task)
    
    elif selected_section == "marking_scheme":
        if "timing" in section_content:
            st.subheader("Timing")
            for timing_key, timing_value in section_content["timing"].items():
                st.write(f"- {timing_key}: {timing_value}")
        
        if "marks" in section_content:
            st.subheader("Marks")
            for marks_key, marks_value in section_content["marks"].items():
                st.write(f"- {marks_key}: {marks_value}")
    
    # Add a search functionality
    st.sidebar.markdown("---")
    st.sidebar.subheader("Search")
    search_term = st.sidebar.text_input("Search in criteria")
    
    if search_term:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Search Results")
        
        # Search through all sections
        for section_name, section_data in sections.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if isinstance(value, str) and search_term.lower() in value.lower():
                        st.sidebar.write(f"Found in {section_name}:")
                        st.sidebar.write(f"- {value[:100]}...")
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and search_term.lower() in item.lower():
                                st.sidebar.write(f"Found in {section_name}:")
                                st.sidebar.write(f"- {item[:100]}...")

if __name__ == "__main__":
    main() 