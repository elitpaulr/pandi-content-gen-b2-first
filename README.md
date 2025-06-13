# B2 First Exam Content Generation Tool

A Python-based language learning content generation tool for Cambridge B2 First exam preparation using Ollama (local LLM) and Streamlit frontend.

## 🎯 Project Overview

This tool transforms the official Cambridge B2 First handbook into an interactive learning system with multiple interfaces for exam preparation. It processes PDF content, extracts structured knowledge, and generates authentic practice tasks.

## ✨ Features

### 📚 Multiple Streamlit Interfaces
- **Main Handbook Navigator** - Browse complete handbook content
- **Reading Criteria Browser** - Focused Reading & Use of English criteria with search
- **Part 5 Examples Viewer** - Interactive practice with official examples
- **Generated Tasks Browser** - Browse and practice with AI-generated tasks

### 🤖 Content Generation
- **10 Complete Reading Part 5 Tasks** - Authentic exam-style questions
- **Contextual Multiple Choice Questions** - Specific, not generic placeholders
- **Three Topic Categories** - Travel/Adventure, Technology/Modern, Personal Growth
- **Official Task Specifications** - Following Cambridge guidelines

### 📊 Interactive Practice
- **Immediate Feedback** - Answer checking with explanations
- **Score Calculation** - Track your performance
- **Question Type Labeling** - Understand different question categories
- **Two-Column Layout** - Text on left, questions on right

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/elitpaulr/pandi-content-gen-b2-first.git
   cd pandi-content-gen-b2-first
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Applications

Each Streamlit app runs on a different port:

```bash
# Main Handbook Navigator (Port 8501)
streamlit run app/main.py

# Reading Criteria Browser (Port 8502)
streamlit run app/reading_criteria.py --server.port 8502

# Part 5 Examples Viewer (Port 8504)
streamlit run app/reading_part5.py --server.port 8504

# Generated Tasks Browser (Port 8505/8506)
streamlit run app/generated_tasks_browser.py --server.port 8505
```

## 📁 Project Structure

```
pandi-content-gen-b2-first/
├── app/                          # Streamlit applications
│   ├── main.py                   # Main handbook navigator
│   ├── reading_criteria.py       # Reading criteria browser
│   ├── reading_part5.py          # Part 5 examples viewer
│   └── generated_tasks_browser.py # Generated tasks browser
├── src/
│   ├── knowledge/                # PDF processing and extractors
│   │   ├── pdf_processor.py      # PDF content extraction
│   │   ├── reading_criteria_extractor.py
│   │   └── reading_part5_extractor.py
│   └── content/                  # Task generators
│       ├── part5_generator.py    # Initial generator
│       └── improved_part5_generator.py # Enhanced generator
├── knowledge_base/               # Structured JSON files
│   ├── b2_first_knowledge_base.json
│   ├── reading_criteria.json
│   ├── reading_part5_examples.json
│   └── b2_first_reading_part5_generation_guidelines.json
├── generated_tasks/              # 10 complete Part 5 tasks
│   ├── reading_part5_task_01.json
│   ├── ...
│   └── reading_part5_task_10.json
├── source-docs/                  # Original PDF (not in repo)
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔧 Technical Implementation

### Knowledge Processing Pipeline
1. **PDF Extraction** - PyPDF2 processes the official handbook
2. **Content Structuring** - Extracts specific sections and criteria
3. **JSON Storage** - Structured data for easy access
4. **Task Generation** - AI-powered content creation

### Generated Content Quality
- **550-750 word texts** per task
- **6 specific questions** per task with contextual options
- **Question types include:**
  - Inference and implication
  - Word/phrase meaning in context
  - Attitudes and opinions
  - Specific details
  - References and pronouns
  - Main ideas and purpose
  - Tone and style

### Example Question Quality
Instead of generic placeholders like "Option A for question 1", the system generates specific questions like:
- "What does the comparison 'like water behind a dam' suggest about Marcus's messages?"
- "The phrase 'digital detox' in paragraph 3 refers to..."

## 📊 Usage Examples

### Browsing Generated Tasks
1. Launch the Generated Tasks Browser
2. Select "Overview Mode" to see all 10 tasks
3. Switch to "Practice Mode" for interactive testing
4. Get immediate feedback and scoring

### Studying Reading Criteria
1. Open the Reading Criteria Browser
2. Use the search function to find specific topics
3. Explore assessment criteria and marking schemes
4. Review task types and requirements

## 🛠️ Development

### Adding New Tasks
1. Use `src/content/improved_part5_generator.py`
2. Modify topics or question types as needed
3. Generate new tasks with contextual questions

### Extending Knowledge Base
1. Add new PDF content to `source-docs/`
2. Create new extractors in `src/knowledge/`
3. Process and structure data into JSON format

## 📋 Dependencies

- **streamlit>=1.32.0** - Web interface framework
- **PyPDF2>=3.0.0** - PDF processing
- **pandas>=2.0.0** - Data manipulation
- **nltk>=3.8.1** - Natural language processing
- **python-dotenv>=1.0.0** - Environment management

## 🚀 Deployment Options

### Streamlit Cloud (Recommended)
1. Connect your GitHub repository
2. Select `app/main.py` as the main file
3. Deploy with automatic updates

### Local Development
- All apps can run simultaneously on different ports
- Use the provided port configurations for testing

### Alternative Platforms
- **Heroku** - Add `Procfile` for web deployment
- **Railway/Render** - Direct GitHub integration
- **Docker** - Containerized deployment (add Dockerfile)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is for educational purposes. The Cambridge B2 First content is used under fair use for educational content generation.

## 🙏 Acknowledgments

- Cambridge Assessment English for the B2 First handbook
- Streamlit team for the excellent web framework
- OpenAI/Ollama communities for LLM integration guidance

## 📞 Support

For questions or issues:
1. Check the existing GitHub issues
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

---

**Built with ❤️ for Cambridge B2 First exam preparation** 