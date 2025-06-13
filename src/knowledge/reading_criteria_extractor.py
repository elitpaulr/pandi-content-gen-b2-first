import json
import os
import re
from pathlib import Path

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove multiple newlines
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def extract_section(content: str, start_marker: str, end_markers: list) -> str:
    """Extract content between start_marker and the first occurrence of any end_marker."""
    try:
        start_idx = content.index(start_marker)
        end_indices = [content.index(end_marker) for end_marker in end_markers if end_marker in content[start_idx:]]
        if end_indices:
            end_idx = min(end_indices)
            return clean_text(content[start_idx:end_idx])
    except ValueError:
        return ""
    return ""

def extract_reading_criteria():
    # Load the full knowledge base
    knowledge_base_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "knowledge_base",
        "b2_first_knowledge_base.json"
    )
    
    try:
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            full_knowledge_base = json.load(f)
    except FileNotFoundError:
        print("Error: Knowledge base file not found")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in knowledge base file")
        return
    
    # Get the Reading and Use of English content
    reading_section = full_knowledge_base.get("paper_sections", {}).get("reading_use_of_english", {})
    if not reading_section or "content" not in reading_section:
        print("Error: Reading section content not found")
        return
    
    content = reading_section["content"]
    
    # Create focused knowledge base structure
    reading_knowledge_base = {
        "paper_name": "Reading and Use of English",
        "sections": {
            "overview": {
                "description": extract_section(
                    content,
                    "Reading and Use of English",
                    ["Tasks", "Assessment", "Sample paper"]
                )
            },
            "assessment_criteria": {
                "content": extract_section(
                    content,
                    "Assessment",
                    ["Sample paper", "Marking scheme"]
                ),
                "criteria": [
                    "Understanding of main ideas and specific information",
                    "Recognition of opinion, attitude, mood, purpose, feeling",
                    "Understanding of text organization and cohesion",
                    "Understanding of vocabulary and grammar in context"
                ]
            },
            "task_types": {
                "tasks": [
                    {
                        "name": "Part 1: Multiple-choice cloze",
                        "description": "Focus on vocabulary, e.g. idioms, collocations, fixed phrases, complementation, phrasal verbs, semantic precision."
                    },
                    {
                        "name": "Part 2: Open cloze",
                        "description": "Focus on grammar and vocabulary, e.g. articles, auxiliaries, prepositions, pronouns, verb forms, word formation."
                    },
                    {
                        "name": "Part 3: Word formation",
                        "description": "Focus on vocabulary, specifically word formation using prefixes, suffixes, internal changes."
                    },
                    {
                        "name": "Part 4: Key word transformation",
                        "description": "Focus on grammar and vocabulary, testing ability to express a message in different ways."
                    },
                    {
                        "name": "Part 5: Multiple choice",
                        "description": "Focus on understanding of detail, opinion, attitude, tone, purpose, main idea, implication, text organization."
                    },
                    {
                        "name": "Part 6: Cross-text multiple matching",
                        "description": "Focus on understanding of detail, opinion, attitude, specific information across texts."
                    },
                    {
                        "name": "Part 7: Multiple matching",
                        "description": "Focus on understanding of detail, opinion, specific information, implication."
                    }
                ]
            },
            "marking_scheme": {
                "timing": {
                    "total_time": "1 hour 15 minutes",
                    "recommended_timing": {
                        "Parts 1-4": "30 minutes",
                        "Parts 5-7": "45 minutes"
                    }
                },
                "marks": {
                    "total_marks": 52,
                    "part_distribution": {
                        "Part 1": "8 marks",
                        "Part 2": "8 marks",
                        "Part 3": "8 marks",
                        "Part 4": "8 marks",
                        "Part 5": "6 marks",
                        "Part 6": "6 marks",
                        "Part 7": "8 marks"
                    }
                }
            }
        }
    }
    
    # Save the focused knowledge base
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "knowledge_base"
    )
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "reading_criteria.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(reading_knowledge_base, f, indent=2, ensure_ascii=False)
    
    print(f"Reading and Use of English criteria saved to: {output_path}")

if __name__ == "__main__":
    extract_reading_criteria() 