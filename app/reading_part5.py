import streamlit as st
import json
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="B2 First - Reading Part 5 Examples",
    page_icon="📖",
    layout="wide"
)

def load_part5_examples():
    """Load the Reading Part 5 examples from the JSON file."""
    examples_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "knowledge_base",
        "reading_part5_examples.json"
    )
    try:
        with open(examples_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Examples file not found. Please run the Part 5 extractor first.")
        return None
    except json.JSONDecodeError:
        st.error("Error reading examples file. The file might be corrupted.")
        return None

def display_example(example, show_answers=False):
    """Display a single example with its text and questions."""
    st.subheader(example["title"])
    
    # Create two columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Display the text
        st.markdown("### Text")
        st.markdown(example["text"])
    
    with col2:
        # Display questions
        st.markdown("### Questions")
        for question in example["questions"]:
            st.markdown(f"**{question['id']}. {question['question']}**")
            
            # Create radio buttons for options
            selected_option = st.radio(
                f"Select answer for question {question['id']}",
                question["options"],
                key=f"q{question['id']}"
            )
            
            # Show correct answer if requested
            if show_answers:
                correct_answer = question["options"][question["correct_answer"]]
                if selected_option == correct_answer:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {correct_answer}")
            
            st.markdown("---")

def main():
    st.title("📖 B2 First - Reading Part 5 Examples")
    
    # Load examples
    data = load_part5_examples()
    if not data:
        return
    
    # Display format information
    with st.expander("📝 Format Information"):
        st.markdown("### Reading Part 5 Format")
        format_info = data["format"]
        cols = st.columns(4)
        cols[0].metric("Questions", format_info["question_count"])
        cols[1].metric("Marks per Question", format_info["marks_per_question"])
        cols[2].metric("Total Marks", format_info["total_marks"])
        cols[3].metric("Time", format_info["recommended_time"])
    
    # Display tips
    with st.expander("💡 Tips"):
        st.markdown("### Tips for Reading Part 5")
        for tip in data["tips"]:
            st.markdown(f"- {tip}")
    
    # Example selection
    st.markdown("### Practice Examples")
    example_index = st.selectbox(
        "Select an example",
        range(len(data["examples"])),
        format_func=lambda x: data["examples"][x]["title"]
    )
    
    # Show/hide answers toggle
    show_answers = st.checkbox("Show answers")
    
    # Display selected example
    display_example(data["examples"][example_index], show_answers)

if __name__ == "__main__":
    main() 