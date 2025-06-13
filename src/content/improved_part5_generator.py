import json
import os
import random
from typing import Dict, List, Any

class ImprovedReadingPart5Generator:
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
    
    def get_text_and_questions(self, topic: str) -> Dict[str, Any]:
        """Get text and specific questions for each topic."""
        
        if topic == "travel_adventure":
            return {
                "text": """The morning mist clung to the mountain peaks as Sarah adjusted her backpack straps for the third time. She had been planning this solo hiking trip for months, but now that she was actually here, doubt crept into her mind like the cold mountain air through her jacket. The trail ahead disappeared into a dense forest of pine trees, their branches heavy with yesterday's rain.

Her guidebook had warned about the challenging terrain, but nothing could have prepared her for the reality of the steep, rocky path that lay before her. Each step required careful consideration, and she found herself moving much slower than anticipated. The silence was both peaceful and unnerving – broken only by the occasional bird call or the distant sound of water rushing over rocks.

As she climbed higher, the trees began to thin out, revealing breathtaking views of the valley below. The small village where she had started her journey now looked like a collection of toy houses scattered across a green carpet. For the first time since beginning her trek, Sarah felt a surge of confidence. Perhaps she was stronger than she had given herself credit for.

The path leveled out temporarily, giving her a chance to catch her breath and consult her map. According to her calculations, she was making good progress, though the most difficult section still lay ahead. She pulled out her water bottle and took a long drink, savoring the cool liquid and the moment of rest.

Suddenly, she heard voices approaching from behind. Two experienced hikers, their gear suggesting they were seasoned mountaineers, caught up with her at a steady pace. They greeted her warmly and, after a brief conversation, offered to share their knowledge of the trail ahead. Sarah hesitated – part of her wanted to prove she could complete this challenge alone, but their friendly demeanor and obvious expertise made the offer tempting.

As they continued together, Sarah realized that accepting help didn't diminish her achievement. The mountain was teaching her lessons she hadn't expected to learn, and sometimes the greatest strength came from knowing when to rely on others.""",
                
                "questions": [
                    {
                        "id": 31,
                        "question": "In the first paragraph, what does Sarah's repeated adjustment of her backpack straps suggest?",
                        "options": [
                            "She is inexperienced with hiking equipment",
                            "She is feeling nervous about the journey ahead",
                            "The backpack is too heavy for the trip",
                            "She wants to make sure everything is secure"
                        ],
                        "correct_answer": 1,
                        "question_type": "inference"
                    },
                    {
                        "id": 32,
                        "question": "What does the writer mean by 'nothing could have prepared her for the reality'?",
                        "options": [
                            "The guidebook information was completely wrong",
                            "Reading about something is different from experiencing it",
                            "She had not read the guidebook carefully enough",
                            "The weather conditions were unexpectedly bad"
                        ],
                        "correct_answer": 1,
                        "question_type": "word_phrase_meaning"
                    },
                    {
                        "id": 33,
                        "question": "How does Sarah's attitude change as she climbs higher?",
                        "options": [
                            "She becomes more worried about the difficult terrain",
                            "She starts to regret beginning the hike alone",
                            "She gains confidence in her abilities",
                            "She decides to turn back to the village"
                        ],
                        "correct_answer": 2,
                        "question_type": "attitudes_opinions"
                    },
                    {
                        "id": 34,
                        "question": "Why does Sarah hesitate when the other hikers offer help?",
                        "options": [
                            "She doesn't trust their expertise",
                            "She wants to prove her independence",
                            "She prefers to hike in silence",
                            "She thinks they might slow her down"
                        ],
                        "correct_answer": 1,
                        "question_type": "details"
                    },
                    {
                        "id": 35,
                        "question": "What does 'their friendly demeanor and obvious expertise' refer to?",
                        "options": [
                            "The mountain guides she had hired",
                            "The people from the village",
                            "The two experienced hikers",
                            "Her hiking companions from the start"
                        ],
                        "correct_answer": 2,
                        "question_type": "references"
                    },
                    {
                        "id": 36,
                        "question": "What is the main message of the text?",
                        "options": [
                            "Solo hiking can be dangerous without proper preparation",
                            "Mountain hiking requires expensive professional equipment",
                            "Personal growth can come from accepting help from others",
                            "Guidebooks are essential for successful hiking trips"
                        ],
                        "correct_answer": 2,
                        "question_type": "main_ideas"
                    }
                ]
            }
        
        elif topic == "technology_modern":
            return {
                "text": """The notification sound had become as familiar to Marcus as his own heartbeat, yet today it filled him with an unusual sense of dread. His smartphone lay face-down on the desk, its screen dark, but he knew that dozens of messages, emails, and updates were accumulating behind that black surface like water behind a dam.

For the past five years, Marcus had prided himself on being constantly connected, always available, perpetually in the loop. His colleagues admired his quick response times, his clients appreciated his immediate availability, and his friends had come to expect instant replies to their messages. But somewhere along the way, this digital efficiency had transformed from a useful tool into an overwhelming burden.

The breaking point had come the previous evening during his daughter's school play. As she performed her solo piece on stage, Marcus found himself automatically reaching for his phone to check a work email. The look of disappointment in her eyes when she spotted him in the audience, head down, fingers tapping, had hit him like a physical blow.

Now, sitting in his home office on a Saturday morning, Marcus was conducting an experiment. He had turned off all notifications, closed his laptop, and placed his phone out of reach. The silence felt strange, almost oppressive. Without the constant stream of digital input, his mind seemed to wander aimlessly, unsure of how to occupy itself.

But gradually, something interesting began to happen. The anxiety that had been his constant companion for months started to ease. He became aware of sounds he hadn't noticed in years – birds singing outside his window, the gentle hum of the refrigerator, his own breathing. It was as if he had been living underwater and had finally surfaced.

The irony wasn't lost on him that technology, which had promised to make life easier and more connected, had actually created a barrier between him and the world around him. As he sat there in the unfamiliar quiet, Marcus began to wonder if there might be a different way to live – one that used technology as a tool rather than allowing it to become a master.""",
                
                "questions": [
                    {
                        "id": 31,
                        "question": "What does the comparison 'like water behind a dam' suggest about Marcus's messages?",
                        "options": [
                            "They are flowing smoothly and naturally",
                            "They are building up pressure and could overflow",
                            "They are being filtered and organized automatically",
                            "They are clean and refreshing to receive"
                        ],
                        "correct_answer": 1,
                        "question_type": "word_phrase_meaning"
                    },
                    {
                        "id": 32,
                        "question": "According to the text, how had Marcus's relationship with technology changed?",
                        "options": [
                            "From being useful to becoming burdensome",
                            "From being expensive to becoming affordable",
                            "From being simple to becoming complicated",
                            "From being optional to becoming necessary"
                        ],
                        "correct_answer": 0,
                        "question_type": "details"
                    },
                    {
                        "id": 33,
                        "question": "What was significant about Marcus's daughter's school play?",
                        "options": [
                            "It was the first time she had performed solo",
                            "It made Marcus realize his phone addiction was affecting his family",
                            "It was when Marcus received an important work email",
                            "It showed Marcus how talented his daughter was"
                        ],
                        "correct_answer": 1,
                        "question_type": "main_ideas"
                    },
                    {
                        "id": 34,
                        "question": "How does Marcus feel when he first turns off his devices?",
                        "options": [
                            "Relieved and immediately peaceful",
                            "Excited about the new experience",
                            "Uncomfortable and unsure",
                            "Angry about missing messages"
                        ],
                        "correct_answer": 2,
                        "question_type": "attitudes_opinions"
                    },
                    {
                        "id": 35,
                        "question": "What does 'it' refer to in the phrase 'as if he had been living underwater and had finally surfaced'?",
                        "options": [
                            "His constant anxiety",
                            "His digital disconnection",
                            "His awareness of natural sounds",
                            "His breathing pattern"
                        ],
                        "correct_answer": 2,
                        "question_type": "references"
                    },
                    {
                        "id": 36,
                        "question": "What is the writer's overall message about technology?",
                        "options": [
                            "Technology should be completely avoided in modern life",
                            "Technology is always harmful to family relationships",
                            "Technology should serve us rather than control us",
                            "Technology is too complicated for most people to use properly"
                        ],
                        "correct_answer": 2,
                        "question_type": "tone_purpose"
                    }
                ]
            }
        
        else:  # personal_growth
            return {
                "text": """The letter arrived on a Tuesday, unremarkable in every way except for the return address that made Elena's hands tremble as she held it. Twenty-five years had passed since she had last seen that handwriting, yet she recognized it immediately. Her sister Maria, from whom she had been estranged since their mother's funeral, was reaching out across the chasm of silence that had divided their family.

Elena set the letter on her kitchen table and stared at it for nearly an hour before finding the courage to open it. The contents were brief but profound – Maria was getting married and wanted Elena to be there. More importantly, she wanted to heal the wounds that had kept them apart for so long. The letter contained no accusations, no demands for apologies, just a simple invitation to reconnect.

The sisters had once been inseparable, sharing secrets, dreams, and an unbreakable bond that everyone assumed would last forever. But their mother's death had revealed fundamental differences in how they processed grief and handled responsibility. What should have brought them closer together had instead driven them apart, each convinced that the other had failed in their duty as a daughter.

Elena had spent years justifying her position, building walls of righteousness around her wounded heart. She had convinced herself that she was the victim, that Maria had been selfish and uncaring during their mother's final months. But holding the letter now, she began to question the narrative she had constructed so carefully.

The truth, she realized, was probably more complex than either of them had been willing to acknowledge at the time. Grief had made them both act in ways that were unlike their true selves, and pride had prevented them from reaching out when the initial hurt was still fresh and potentially healable.

As Elena read the letter for the third time, she felt something shift inside her chest – a loosening of the tight knot of anger and resentment she had carried for so long. Perhaps it was time to choose love over pride, connection over being right. Perhaps some bridges, no matter how badly damaged, were worth rebuilding.""",
                
                "questions": [
                    {
                        "id": 31,
                        "question": "What made the letter remarkable to Elena?",
                        "options": [
                            "It arrived on an unusual day of the week",
                            "It was from her estranged sister Maria",
                            "It contained unexpected news about money",
                            "It was written in a foreign language"
                        ],
                        "correct_answer": 1,
                        "question_type": "details"
                    },
                    {
                        "id": 32,
                        "question": "What does 'the chasm of silence' refer to?",
                        "options": [
                            "The physical distance between the sisters",
                            "The period of no communication between them",
                            "The quiet atmosphere in Elena's house",
                            "The difference in their personalities"
                        ],
                        "correct_answer": 1,
                        "question_type": "word_phrase_meaning"
                    },
                    {
                        "id": 33,
                        "question": "According to the text, what caused the sisters' estrangement?",
                        "options": [
                            "A disagreement about Maria's wedding plans",
                            "Different ways of dealing with their mother's death",
                            "A fight over their mother's inheritance",
                            "Elena's move to a different city"
                        ],
                        "correct_answer": 1,
                        "question_type": "main_ideas"
                    },
                    {
                        "id": 34,
                        "question": "How has Elena's perspective changed while reading the letter?",
                        "options": [
                            "She becomes more angry with Maria",
                            "She starts to question her own version of events",
                            "She decides Maria was definitely wrong",
                            "She feels more justified in her position"
                        ],
                        "correct_answer": 1,
                        "question_type": "attitudes_opinions"
                    },
                    {
                        "id": 35,
                        "question": "What does 'them' refer to in 'either of them had been willing to acknowledge'?",
                        "options": [
                            "Elena and her mother",
                            "Maria and her mother",
                            "Elena and Maria",
                            "The wedding guests"
                        ],
                        "correct_answer": 2,
                        "question_type": "references"
                    },
                    {
                        "id": 36,
                        "question": "What is the main theme of the passage?",
                        "options": [
                            "The importance of family traditions",
                            "The difficulty of planning weddings",
                            "The power of forgiveness and reconciliation",
                            "The challenges of long-distance relationships"
                        ],
                        "correct_answer": 2,
                        "question_type": "tone_purpose"
                    }
                ]
            }
    
    def generate_single_task(self, task_id: int) -> Dict[str, Any]:
        """Generate a single Reading Part 5 task with specific questions."""
        topics = ["travel_adventure", "technology_modern", "personal_growth"]
        topic = topics[(task_id - 1) % len(topics)]  # Cycle through topics
        
        content = self.get_text_and_questions(topic)
        
        return {
            "task_id": f"part5_task_{task_id:02d}",
            "title": f"Reading Part 5 - Task {task_id}",
            "topic": topic,
            "text": content["text"],
            "questions": content["questions"],
            "metadata": {
                "word_count": len(content["text"].split()),
                "question_types_used": [q["question_type"] for q in content["questions"]],
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
            
            print(f"Generated: {filename} - {task['topic']}")
        
        print(f"\nAll {count} tasks generated successfully in {output_dir}")

def main():
    generator = ImprovedReadingPart5Generator()
    generator.generate_all_tasks(10)

if __name__ == "__main__":
    main() 