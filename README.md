# B2 First Exam Content Generation Tool

A Python-based language learning content generation tool for Cambridge B2 First exam preparation featuring both static content processing and dynamic AI-powered generation using local Ollama LLM with Streamlit frontend.

## 🎯 Project Overview

This tool transforms the official Cambridge B2 First handbook into an interactive learning system with multiple interfaces for exam preparation. It processes PDF content, extracts structured knowledge, and generates authentic practice tasks.

## ✨ Features

### 📚 Multiple Streamlit Interfaces
- **Main Handbook Navigator** - Browse complete handbook content
- **Reading Criteria Browser** - Focused Reading & Use of English criteria with search
- **Part 5 Examples Viewer** - Interactive practice with official examples
- **Generated Tasks Browser** - Browse and practice with AI-generated tasks
- **🤖 Ollama Task Generator** - Real-time AI-powered task generation using local LLM

### 🤖 Content Generation
- **Static Tasks**: 10 pre-generated Reading Part 5 tasks with authentic exam-style questions
- **Dynamic AI Generation**: Real-time task creation using local Ollama LLM
- **Contextual Multiple Choice Questions** - Specific, not generic placeholders
- **Multiple Topic Categories** - Travel/Adventure, Technology/Modern, Personal Growth, Environment, Health, Culture
- **Official Task Specifications** - Following Cambridge guidelines
- **Task Improvement** - AI-powered enhancement of existing tasks
- **Batch Generation** - Create multiple tasks efficiently

### 📊 Interactive Practice
- **Immediate Feedback** - Answer checking with explanations
- **Score Calculation** - Track your performance
- **Question Type Labeling** - Understand different question categories
- **Two-Column Layout** - Text on left, questions on right

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- **Ollama** (for AI-powered generation) - https://ollama.ai/

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

4. **Set up Ollama (for AI generation)**
   ```bash
   # Install Ollama from https://ollama.ai/
   # Start Ollama service
   ollama serve
   
   # Pull a recommended model
   ollama pull llama3.1:8b
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

# 🤖 Ollama Task Generator (Port 8507)
streamlit run app/ollama_generator.py --server.port 8507
```

## 📁 Project Structure

```
pandi-content-gen-b2-first/
├── app/                          # Streamlit applications
│   ├── main.py                   # Main handbook navigator
│   ├── reading_criteria.py       # Reading criteria browser
│   ├── reading_part5.py          # Part 5 examples viewer
│   ├── generated_tasks_browser.py # Generated tasks browser
│   └── ollama_generator.py       # 🤖 AI-powered task generator
├── src/
│   ├── knowledge/                # PDF processing and extractors
│   │   ├── pdf_processor.py      # PDF content extraction
│   │   ├── reading_criteria_extractor.py
│   │   └── reading_part5_extractor.py
│   ├── content/                  # Task generators
│   │   ├── part5_generator.py    # Initial generator
│   │   ├── improved_part5_generator.py # Enhanced generator
│   │   └── ollama_part5_generator.py # 🤖 AI-powered generator
│   └── llm/                      # LLM integration
│       └── ollama_client.py      # Ollama client and API
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
├── test_ollama.py                # Ollama integration test suite
└── README.md
```

## 🔧 Technical Implementation

### Knowledge Processing Pipeline
1. **PDF Extraction** - PyPDF2 processes the official handbook
2. **Content Structuring** - Extracts specific sections and criteria
3. **JSON Storage** - Structured data for easy access
4. **Static Task Generation** - Pre-generated content with improved algorithms
5. **🤖 AI-Powered Generation** - Real-time task creation using local Ollama LLM

### AI Generation Features
- **Local LLM Integration** - Uses Ollama for privacy and control
- **Multiple Model Support** - Compatible with llama3.1, mistral, and other models
- **Real-time Generation** - Create tasks on-demand with custom topics
- **Quality Validation** - Automatic checking of generated content
- **Batch Processing** - Generate multiple tasks efficiently
- **Task Improvement** - AI-powered enhancement of existing content

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

### 🤖 AI-Powered Task Generation
1. Launch the Ollama Task Generator (port 8507)
2. Ensure Ollama is running with a model loaded
3. Enter a custom topic or select from suggestions
4. Generate tasks in real-time with immediate preview
5. Use batch generation for multiple tasks
6. Improve existing tasks with AI enhancement

## 🛠️ Development

### Adding New Tasks
1. Use `src/content/improved_part5_generator.py`
2. Modify topics or question types as needed
3. Generate new tasks with contextual questions

### Extending Knowledge Base
1. Add new PDF content to `source-docs/`
2. Create new extractors in `src/knowledge/`
3. Process and structure data into JSON format

### Testing Ollama Integration
```bash
# Test Ollama connection and task generation
python test_ollama.py

# Generate tasks via command line
python src/content/ollama_part5_generator.py
```

## 📋 Dependencies

- **streamlit>=1.32.0** - Web interface framework
- **ollama>=0.1.6** - 🤖 Local LLM integration
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

## 🔧 Troubleshooting

### Ollama Issues
- **Connection Failed**: Ensure Ollama is running (`ollama serve`)
- **No Models Found**: Pull a model first (`ollama pull llama3.1:8b`)
- **Generation Slow**: Try a smaller model or adjust parameters
- **Import Errors**: Install requirements (`pip install -r requirements.txt`)

### Streamlit Issues
- **Port Conflicts**: Use different ports for each app
- **Module Not Found**: Ensure virtual environment is activated
- **Performance**: Install watchdog (`pip install watchdog`)

## 📞 Support

For questions or issues:
1. Run the test suite: `python test_ollama.py`
2. Check the existing GitHub issues
3. Create a new issue with detailed description
4. Include error messages and steps to reproduce

---

**Built with ❤️ for Cambridge B2 First exam preparation** 

# 🚀 **Ollama Integration Complete!**

### **🤖 What's New:**

#### **1. Ollama Client (`src/llm/ollama_client.py`)**
- Direct communication with local Ollama LLM
- Configurable models, temperature, and token limits
- Connection testing and model listing
- Specialized B2 First task generation methods

#### **2. Enhanced Task Generator (`src/content/ollama_part5_generator.py`)**
- Generates authentic Reading Part 5 tasks using Ollama
- Batch generation capabilities
- Task validation and quality checks
- Automatic categorization by topic
- Command-line interface

#### **3. Streamlit Interface (`app/ollama_generator.py`)**
- **4 tabs**: Generate Tasks, Improve Tasks, Batch Generation, Task Library
- Real-time Ollama status checking
- Model selection and parameter tuning
- Interactive task generation and improvement
- Progress tracking for batch operations

#### **4. Test Suite (`test_ollama.py`)**
- Verify Ollama connection
- Test task generation
- Comprehensive diagnostics

### **🎯 How to Use:**

#### **Setup Ollama:**
```bash
# 1. Install Ollama
# Visit: https://ollama.ai/

# 2. Start Ollama
ollama serve

# 3. Pull a model
ollama pull llama3.1:8b
```

#### **Test Integration:**
```bash
python test_ollama.py
```

#### **Run Streamlit Interface:**
```bash
streamlit run app/ollama_generator.py --server.port 8507
```

#### **Command Line Generation:**
```bash
python src/content/ollama_part5_generator.py
```

### **🔧 Features:**

- **Local LLM Power**: No API keys needed, runs entirely on your machine
- **Multiple Models**: Support for any Ollama model (llama3.1, mistral, etc.)
- **Quality Control**: Automatic validation of generated tasks
- **Batch Processing**: Generate multiple tasks efficiently
- **Task Improvement**: Enhance existing tasks with better questions
- **Interactive UI**: User-friendly Streamlit interface

### **📊 Generated Content Quality:**
- **550-750 word texts** per task
- **6 contextual questions** (not generic placeholders)
- **Authentic B2 level** language and topics
- **Proper Cambridge format** (questions 31-36)
- **Multiple question types**: inference, vocabulary, attitude, details, references, main ideas

Your project now has both the original static generation AND powerful local LLM capabilities! 🚀 