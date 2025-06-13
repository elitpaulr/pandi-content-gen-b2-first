import json
import os
import random
from typing import Dict, List, Any

class ReadingPart5Generator:
    def __init__(self):
        self.guidelines = self.load_guidelines()
        self.examples = self.load_examples()
        
    def load_guidelines(self) -> Dict[str, Any]:
        """Load the generation guidelines."""
        guidelines_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "knowledge_base",
            "b2_first_reading_part5_generation_guidelines.json"
        )
        with open(guidelines_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_examples(self) -> Dict[str, Any]:
        """Load the existing examples."""
        examples_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "knowledge_base",
            "reading_part5_examples.json"
        )
        with open(examples_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_text(self, topic: str, style: str) -> str:
        """Generate a text based on topic and style."""
        # This is a simplified version - in a real implementation, 
        # you would use an LLM to generate the text
        texts = {
            "travel_adventure": """The morning mist clung to the mountain peaks as Sarah adjusted her backpack straps for the third time. She had been planning this solo hiking trip for months, but now that she was actually here, doubt crept into her mind like the cold mountain air through her jacket. The trail ahead disappeared into a dense forest of pine trees, their branches heavy with yesterday's rain.

Her guidebook had warned about the challenging terrain, but nothing could have prepared her for the reality of the steep, rocky path that lay before her. Each step required careful consideration, and she found herself moving much slower than anticipated. The silence was both peaceful and unnerving – broken only by the occasional bird call or the distant sound of water rushing over rocks.

As she climbed higher, the trees began to thin out, revealing breathtaking views of the valley below. The small village where she had started her journey now looked like a collection of toy houses scattered across a green carpet. For the first time since beginning her trek, Sarah felt a surge of confidence. Perhaps she was stronger than she had given herself credit for.

The path leveled out temporarily, giving her a chance to catch her breath and consult her map. According to her calculations, she was making good progress, though the most difficult section still lay ahead. She pulled out her water bottle and took a long drink, savoring the cool liquid and the moment of rest.

Suddenly, she heard voices approaching from behind. Two experienced hikers, their gear suggesting they were seasoned mountaineers, caught up with her at a steady pace. They greeted her warmly and, after a brief conversation, offered to share their knowledge of the trail ahead. Sarah hesitated – part of her wanted to prove she could complete this challenge alone, but their friendly demeanor and obvious expertise made the offer tempting.

As they continued together, Sarah realized that accepting help didn't diminish her achievement. The mountain was teaching her lessons she hadn't expected to learn, and sometimes the greatest strength came from knowing when to rely on others.""",
            
            "technology_modern": """The notification sound had become as familiar to Marcus as his own heartbeat, yet today it filled him with an unusual sense of dread. His smartphone lay face-down on the desk, its screen dark, but he knew that dozens of messages, emails, and updates were accumulating behind that black surface like water behind a dam.

For the past five years, Marcus had prided himself on being constantly connected, always available, perpetually in the loop. His colleagues admired his quick response times, his clients appreciated his immediate availability, and his friends had come to expect instant replies to their messages. But somewhere along the way, this digital efficiency had transformed from a useful tool into an overwhelming burden.

The breaking point had come the previous evening during his daughter's school play. As she performed her solo piece on stage, Marcus found himself automatically reaching for his phone to check a work email. The look of disappointment in her eyes when she spotted him in the audience, head down, fingers tapping, had hit him like a physical blow.

Now, sitting in his home office on a Saturday morning, Marcus was conducting an experiment. He had turned off all notifications, closed his laptop, and placed his phone out of reach. The silence felt strange, almost oppressive. Without the constant stream of digital input, his mind seemed to wander aimlessly, unsure of how to occupy itself.

But gradually, something interesting began to happen. The anxiety that had been his constant companion for months started to ease. He became aware of sounds he hadn't noticed in years – birds singing outside his window, the gentle hum of the refrigerator, his own breathing. It was as if he had been living underwater and had finally surfaced.

The irony wasn't lost on him that technology, which had promised to make life easier and more connected, had actually created a barrier between him and the world around him. As he sat there in the unfamiliar quiet, Marcus began to wonder if there might be a different way to live – one that used technology as a tool rather than allowing it to become a master.""",
            
            "personal_growth": """The letter arrived on a Tuesday, unremarkable in every way except for the return address that made Elena's hands tremble as she held it. Twenty-five years had passed since she had last seen that handwriting, yet she recognized it immediately. Her sister Maria, from whom she had been estranged since their mother's funeral, was reaching out across the chasm of silence that had divided their family.

Elena set the letter on her kitchen table and stared at it for nearly an hour before finding the courage to open it. The contents were brief but profound – Maria was getting married and wanted Elena to be there. More importantly, she wanted to heal the wounds that had kept them apart for so long. The letter contained no accusations, no demands for apologies, just a simple invitation to reconnect.

The sisters had once been inseparable, sharing secrets, dreams, and an unbreakable bond that everyone assumed would last forever. But their mother's death had revealed fundamental differences in how they processed grief and handled responsibility. What should have brought them closer together had instead driven them apart, each convinced that the other had failed in their duty as a daughter.

Elena had spent years justifying her position, building walls of righteousness around her wounded heart. She had convinced herself that she was the victim, that Maria had been selfish and uncaring during their mother's final months. But holding the letter now, she began to question the narrative she had constructed so carefully.

The truth, she realized, was probably more complex than either of them had been willing to acknowledge at the time. Grief had made them both act in ways that were unlike their true selves, and pride had prevented them from reaching out when the initial hurt was still fresh and potentially healable.

As Elena read the letter for the third time, she felt something shift inside her chest – a loosening of the tight knot of anger and resentment she had carried for so long. Perhaps it was time to choose love over pride, connection over being right. Perhaps some bridges, no matter how badly damaged, were worth rebuilding."""
        }
        
        return texts.get(topic, texts["personal_growth"])
    
    def generate_questions(self, text: str, question_types: List[str]) -> List[Dict[str, Any]]:
        """Generate questions based on the text and question types."""
        # This is a simplified version - in a real implementation,
        # you would use an LLM to generate contextually appropriate questions
        
        question_templates = {
            "main_ideas": [
                "What is the main theme of the text?",
                "What is the writer's primary purpose?",
                "What is the central message of the passage?"
            ],
            "details": [
                "According to the text, what happened when...?",
                "The writer mentions that...",
                "What specific detail does the author provide about...?"
            ],
            "attitudes_opinions": [
                "How does the writer feel about...?",
                "What is the author's attitude towards...?",
                "The writer's opinion of... is that it..."
            ],
            "word_phrase_meaning": [
                "What does the phrase '...' mean in this context?",
                "The word '...' in line X refers to...",
                "In the context of the passage, '...' suggests..."
            ],
            "references": [
                "What does 'it' refer to in line...?",
                "The pronoun 'they' in paragraph X refers to...",
                "What is meant by 'this' in the final paragraph?"
            ],
            "tone_purpose": [
                "What is the tone of the passage?",
                "Why does the writer include the example of...?",
                "The author's purpose in describing... is to..."
            ]
        }
        
        questions = []
        for i, q_type in enumerate(question_types[:6]):  # Ensure only 6 questions
            template = random.choice(question_templates.get(q_type, question_templates["main_ideas"]))
            
            # Generate sample options (in real implementation, these would be contextually relevant)
            options = [
                f"Option A for question {i+1}",
                f"Option B for question {i+1}",
                f"Option C for question {i+1}",
                f"Option D for question {i+1}"
            ]
            
            questions.append({
                "id": 31 + i,
                "question": template,
                "options": options,
                "correct_answer": random.randint(0, 3),
                "question_type": q_type
            })
        
        return questions
    
    def generate_single_task(self, task_id: int) -> Dict[str, Any]:
        """Generate a single Reading Part 5 task."""
        topics = ["travel_adventure", "technology_modern", "personal_growth"]
        topic = random.choice(topics)
        
        # Select question types based on guidelines
        available_types = [qt["type"].lower().replace("/", "_").replace(" ", "_") 
                          for qt in self.guidelines["question_types"]]
        selected_types = random.sample(available_types, 6)
        
        text = self.generate_text(topic, "article")
        questions = self.generate_questions(text, selected_types)
        
        return {
            "task_id": f"part5_task_{task_id:02d}",
            "title": f"Reading Part 5 - Task {task_id}",
            "topic": topic,
            "text": text,
            "questions": questions,
            "metadata": {
                "word_count": len(text.split()),
                "question_types_used": selected_types,
                "difficulty_level": "B2",
                "estimated_time": "15 minutes"
            }
        }
    
    def generate_all_tasks(self, count: int = 10) -> None:
        """Generate all tasks and save them as separate JSON files."""
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "generated_tasks"
        )
        os.makedirs(output_dir, exist_ok=True)
        
        for i in range(1, count + 1):
            task = self.generate_single_task(i)
            
            filename = f"reading_part5_task_{i:02d}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(task, f, indent=2, ensure_ascii=False)
            
            print(f"Generated: {filename}")
        
        print(f"\nAll {count} tasks generated successfully in {output_dir}")

def main():
    generator = ReadingPart5Generator()
    generator.generate_all_tasks(10)

if __name__ == "__main__":
    main() 