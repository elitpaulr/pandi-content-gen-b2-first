import json
import os
from pathlib import Path

def extract_reading_part5_examples():
    """Extract Part 5 examples and structure them for easy access."""
    # Example structure based on the screenshot
    reading_part5_examples = {
        "title": "Reading and Use of English Part 5",
        "description": "Multiple choice reading comprehension questions based on a single text.",
        "format": {
            "question_count": 6,
            "marks_per_question": 1,
            "total_marks": 6,
            "recommended_time": "15 minutes"
        },
        "examples": [
            {
                "id": "example_1",
                "title": "Island Visit",
                "text": """We live on the island of Islay. It's about four kilometres long and two kilometres wide at its broadest point, and it's joined to the mainland by a causeway called the Strand - a narrow road with sea on the south of the line which appears as from the rest of the mainland. Most of the time you wouldn't know we're on an island because the few inches between us and the mainland is just a vast stretch of tall grasses and brown mud. But when there's a high tide she the water rises a half a metre or so above the road and nothing can pass until the tide goes out again a few hours later. Then you know it's an island.

We were on our way back from the mainland. My older brother, Dominic, had just finished his first year at university in a town 150 km away. Dominic's train was due in at five and he'd asked for a lift back from the station. Now, Dad normally takes being disturbed when he's telling which is just about all the time - very badly. Having to go anywhere, but despite the typical signs and moans - 'Why can't he get a taxi?' - he'd agreed to collect Dominic. I went along too, though I can't remember why. I must have been about fourteen at the time.

So, anyway, Dad and I had driven to the mainland and picked up Dominic from the station. He had been talking non-stop from the moment I had seen him except for the occasional pause to draw his next breath. Dad was being unusually patient, though, making encouraging noises. When I had finally managed to get a word in, I had found him strangely distant. It wasn't like him to be so uncommunicative. I mean talking is an absorbing force in our family. I don't like it - the way he spoke and waved his hands around as if he was some kind of intellectual or something. It was embarrassing. It made me feel uncomfortable - that kind of discomfort you feel when someone you like, someone close to you, suddenly starts acting like a complete idiot. And I didn't like the way he was grinning like either. I'm all for smirking (I was getting) I might as well not have been there. I felt a bit angry at my own rat.

As we approached the island on that Friday afternoon, the tide was high and the island welcomed us with stretched out arms as clear and dry. Beautifully hazy in the heat - a dead heat of a summer bound by white sunshine and a blue horizon. We had might decided to take the scenic route home, along the coastal path. The car windows were down and a gentle breeze was getting into the car. The sun light as a smile on a girl and in the afternoon which fades through to the early evening.

We were about halfway along when Dad pulled up. He did so very suddenly and Dad's not like that. Dad's very smooth. There's nothing but small cottages, farmland, heathland and the road. So strangers don't walk because of that. If they're going to Malvern they tend to take the bus. So the only pedestrians you're likely to see around here are walkers or bird-watchers. But even from a distance I could tell that the figure ahead didn't fit into either of these categories. I wasn't sure how I knew. I just did.

As we drew closer, he became clearer. He was actually a young man rather than a boy. Although he was on the land side, he wasn't as slight as I'd first thought. He wasn't exactly muscular, but he wasn't exactly looking after the hard to explain. There was a sense of strength about him, a peculiar strength that showed in his features, the way he held himself, the way he walked.""",
                "questions": [
                    {
                        "id": 31,
                        "question": "In the first paragraph, what is Caitlin's main point about the island?",
                        "options": [
                            "It can be dangerous to try to cross from the mainland",
                            "It is much smaller than it looks from the mainland",
                            "It is only completely cut off at certain times",
                            "It can be a difficult place for people to live in"
                        ],
                        "correct_answer": 2  # 0-based index
                    },
                    {
                        "id": 32,
                        "question": "What does Caitlin suggest about her father?",
                        "options": [
                            "His surfing prevents him from doing things he wants to with his family",
                            "His initial reaction to his son's request is different from usual",
                            "His true feelings are often hidden from his family",
                            "His short temper is one event he will take time off for"
                        ],
                        "correct_answer": 1
                    },
                    {
                        "id": 33,
                        "question": "Caitlin emphasises her feelings of discomfort because she",
                        "options": [
                            "is embarrassed that she doesn't understand what her brother is talking about",
                            "feels confused about why she can't relate to her brother any more",
                            "is upset by the unexpected change in her brother's behaviour",
                            "feels foolish that her brother's attention is so important to her"
                        ],
                        "correct_answer": 2
                    },
                    {
                        "id": 34,
                        "question": "In the fourth paragraph, what is Caitlin's purpose in describing the island?",
                        "options": [
                            "to emphasise how peaceful everything seemed",
                            "to suggest that something unusual was about to happen",
                            "to show how familiar she was with the surroundings",
                            "to indicate how much she was enjoying the journey"
                        ],
                        "correct_answer": 0
                    }
                ]
            }
        ],
        "tips": [
            "Read the text carefully before looking at the questions",
            "Look for evidence in the text to support your answer",
            "Eliminate obviously wrong options",
            "Pay attention to the writer's tone and purpose"
        ]
    }
    
    # Save the examples
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "knowledge_base"
    )
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "reading_part5_examples.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(reading_part5_examples, f, indent=2, ensure_ascii=False)
    
    print(f"Reading Part 5 examples saved to: {output_path}")

if __name__ == "__main__":
    extract_reading_part5_examples() 