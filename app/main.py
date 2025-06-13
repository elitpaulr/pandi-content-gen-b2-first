import streamlit as st
import json
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="B2 First Handbook Navigator",
    page_icon="📚",
    layout="wide"
)

# Load the knowledge base
def load_knowledge_base():
    knowledge_base_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "knowledge_base",
        "b2_first_knowledge_base.json"
    )
    try:
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Knowledge base file not found. Please run the PDF processor first.")
        return None
    except json.JSONDecodeError:
        st.error("Error reading knowledge base file. The file might be corrupted.")
        return None

def main():
    st.title("📚 B2 First Handbook Navigator")
    
    # Load knowledge base
    knowledge_base = load_knowledge_base()
    if not knowledge_base:
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Main sections
    sections = {
        "Paper Sections": knowledge_base.get("paper_sections", {}),
        "Assessment Criteria": knowledge_base.get("assessment_criteria", {}),
        "Sample Materials": knowledge_base.get("sample_materials", {}),
        "Teaching Resources": knowledge_base.get("teaching_resources", {})
    }
    
    # Navigation in sidebar
    selected_section = st.sidebar.selectbox(
        "Select Section",
        list(sections.keys())
    )
    
    # Display selected section
    st.header(selected_section)
    
    if selected_section == "Paper Sections":
        # Display paper sections
        for paper_name, paper_content in sections[selected_section].items():
            with st.expander(f"📄 {paper_name.replace('_', ' ').title()}"):
                if isinstance(paper_content, dict):
                    # Display tasks
                    if "tasks" in paper_content:
                        st.subheader("Tasks")
                        for task in paper_content["tasks"]:
                            st.write(f"- {task}")
                    
                    # Display timing
                    if "timing" in paper_content:
                        st.subheader("Timing")
                        for timing_key, timing_value in paper_content["timing"].items():
                            st.write(f"- {timing_key}: {timing_value}")
                    
                    # Display marks
                    if "marks" in paper_content:
                        st.subheader("Marks")
                        for marks_key, marks_value in paper_content["marks"].items():
                            st.write(f"- {marks_key}: {marks_value}")
                    
                    # Display full content
                    if "content" in paper_content:
                        st.subheader("Full Content")
                        st.text(paper_content["content"])
    
    elif selected_section == "Assessment Criteria":
        criteria = sections[selected_section]
        if isinstance(criteria, dict):
            if "criteria" in criteria:
                for criterion in criteria["criteria"]:
                    st.write(f"- {criterion}")
            if "content" in criteria:
                st.text(criteria["content"])
    
    elif selected_section == "Sample Materials":
        samples = sections[selected_section]
        if isinstance(samples, dict):
            if "examples" in samples:
                for example in samples["examples"]:
                    st.write(f"- {example}")
            if "content" in samples:
                st.text(samples["content"])
    
    elif selected_section == "Teaching Resources":
        resources = sections[selected_section]
        if isinstance(resources, dict):
            for key, value in resources.items():
                st.subheader(key.replace("_", " ").title())
                st.write(value)

if __name__ == "__main__":
    main() 