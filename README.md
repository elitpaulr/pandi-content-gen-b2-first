# B2 First Exam Content Generation Tool

A Python-based language learning content generation tool for Cambridge B2 First exam preparation featuring both static content processing and dynamic AI-powered generation using local Ollama LLM with Streamlit frontend.

## 🎯 Project Overview

This tool transforms the official Cambridge B2 First handbook into an interactive learning system with multiple interfaces for exam preparation. It processes PDF content, extracts structured knowledge, and generates authentic practice tasks using advanced AI-powered generation with comprehensive batch processing and task management capabilities.

## ✨ Features

### 📚 Multiple Streamlit Interfaces
- **Main Handbook Navigator** - Browse complete handbook content
- **Reading Criteria Browser** - Focused Reading & Use of English criteria with search
- **Part 5 Examples Viewer** - Interactive practice with official examples
- **Generated Tasks Browser** - Browse and practice with AI-generated tasks
- **🤖 Ollama Task Generator** - Real-time AI-powered task generation using local LLM

### 🤖 Advanced Content Generation
- **Static Tasks**: 10 pre-generated Reading Part 5 tasks with authentic exam-style questions
- **Dynamic AI Generation**: Real-time task creation using local Ollama LLM with step-by-step generation
- **📝 Custom Instructions**: Add specific requirements and focus areas to generated tasks
- **📝 Text Type Selection**: Choose from 10 B2-appropriate text types for varied content
- **🚀 Batch Generation with Auto-Save**: Create multiple tasks efficiently with automatic subfolder organization
- **📁 Intelligent File Management**: Timestamped batch folders with comprehensive summaries
- **Contextual Multiple Choice Questions** - Specific, not generic placeholders
- **Multiple Topic Categories** - Travel/Adventure, Technology/Modern, Personal Growth, Environment, Health, Culture
- **Official Task Specifications** - Following Cambridge guidelines (400-800 words, 5-6 questions)
- **Task Improvement** - AI-powered enhancement of existing tasks
- **🔄 Step-by-Step Generation**: Advanced LLM approach for higher success rates

### 📊 Enhanced Task Library & Management
- **📦 Batch Collection Viewing**: Browse and manage batch-generated tasks with summaries
- **🎓 Multiple View Modes**: Learner View, Summary View, and JSON View for all tasks
- **📋 Comprehensive Batch Summaries**: Detailed generation metadata, statistics, and file listings
- **🔍 Advanced Filtering**: Filter by generator type, text type, and other criteria
- **📥 Bulk Download**: Download individual tasks, batches, or entire collections as ZIP files
- **📊 Task Statistics**: Word counts, question counts, success rates, and generation metrics

### 📊 Interactive Practice
- **Immediate Feedback** - Answer checking with explanations
- **Score Calculation** - Track your performance
- **Question Type Labeling** - Understand different question categories
- **Two-Column Layout** - Text on left, questions on right
- **📝 Custom Instructions Display** - View generation parameters and custom requirements

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

# 🤖 Ollama Task Generator (Port 8508)
streamlit run app/ollama_generator.py --server.port 8508
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
│       ├── ollama_client.py      # Ollama client and API
│       └── json_parser.py        # Robust JSON parsing
├── knowledge_base/               # Structured JSON files
│   ├── b2_first_knowledge_base.json
│   ├── reading_criteria.json
│   ├── reading_part5_examples.json
│   └── b2_first_reading_part5_generation_guidelines.json
├── generated_tasks/              # Task storage with batch organization
│   ├── reading_part5_task_01.json # Individual tasks
│   ├── ...
│   ├── reading_part5_task_15.json
│   ├── batch_20250615_093427_2topics_2types/ # Batch folders
│   │   ├── BATCH_SUMMARY.txt     # Comprehensive batch metadata
│   │   ├── reading_part5_task_*.json # Auto-saved tasks
│   │   └── ...
│   └── batch_*/                  # Additional batch collections
├── failure_logs/                 # Generation failure analysis
│   └── task_*_failure_*.txt      # Detailed error logs
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

### 🚀 Advanced AI Generation Features
- **Local LLM Integration** - Uses Ollama for privacy and control
- **Multiple Model Support** - Compatible with llama3.1, mistral, and other models
- **📝 Text Type Selection** - 10 B2-appropriate text types with specific styling
- **📝 Custom Instructions** - Add specific requirements, focus areas, and constraints
- **🔄 Step-by-Step Generation** - Advanced LLM approach generating title, text, and questions separately
- **Real-time Generation** - Create tasks on-demand with custom topics
- **Quality Validation** - Automatic checking of generated content (400-800 words, 5-6 questions)
- **🚀 Batch Processing** - Generate multiple tasks efficiently with text type combinations
- **📁 Auto-Save with Subfolders** - Automatic organization in timestamped batch directories
- **📋 Comprehensive Summaries** - Detailed batch metadata and generation statistics
- **Task Improvement** - AI-powered enhancement of existing content
- **🛡️ Robust JSON Parsing** - Handles complex LLM output with formatting characters and control sequences
- **🔍 Failure Analysis** - Detailed logging and analysis of generation failures

### 📦 Batch Generation & Organization
- **Unique Timestamped Folders**: Format `batch_YYYYMMDD_HHMMSS_XtopicsYtypes`
- **Auto-Save Functionality**: Each task saved immediately after generation
- **Comprehensive Batch Summaries**: Include generation parameters, success metrics, file listings
- **Isolated Operations**: Batch generation doesn't interfere with individual task numbering
- **Error Handling**: Failed generations logged with detailed analysis
- **Progress Tracking**: Real-time progress updates and status reporting

### 📚 Enhanced Task Library Features
- **Dual Interface**: Separate views for Individual Tasks and Batch Collections
- **Multiple View Modes**:
  - **🎓 Learner View**: Interactive task experience with tabs
  - **📋 Summary View**: Compact cards with key information
  - **🔧 JSON View**: Raw data for technical inspection
- **Batch Management**:
  - **📋 Batch Summary**: Generation metadata and quick statistics
  - **🎓 Learner View**: Tabbed interface for batch tasks (up to 6 tasks)
  - **📥 Download Options**: Individual files, batch ZIP, or bulk downloads
  - **🗑️ Batch Actions**: Delete, info, and management functions
- **Advanced Filtering**: By generator type, text type, custom instructions
- **📊 Statistics Dashboard**: Success rates, word counts, question distributions

### Generated Content Quality
- **400-800 word texts** per task (B2 First standard)
- **5-6 specific questions** per task with contextual options (questions 31-36)
- **📝 Custom Instructions Integration**: Tasks reflect specific requirements and focus areas
- **10 Text Types Available:**
  - 📰 Magazine Article - Informative lifestyle and science content
  - 📄 Newspaper Article - News features and opinion pieces
  - 📖 Novel Extract - Contemporary fiction excerpts
  - ✍️ Personal Blog Post - First-person experiences
  - 🔬 Popular Science Article - Accessible scientific explanations
  - 🎭 Cultural Review - Commentary on books, films, art
  - 💼 Professional Feature - Career and workplace content
  - 🏠 Lifestyle Feature - Home, family, and personal interests
  - 🌍 Travel Writing - Destination guides and cultural observations
  - 📚 Educational Feature - Learning and skill development
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

### 🤖 AI-Powered Task Generation
1. Launch the Ollama Task Generator (port 8508)
2. Ensure Ollama is running with a model loaded
3. **Select Text Type** - Choose from 10 B2-appropriate text types
4. Enter a custom topic or select from suggestions
5. **Add Custom Instructions** - Specify requirements like "Focus on practical tips and include specific examples"
6. Generate tasks in real-time with immediate preview
7. **Save or Download** - Tasks can be saved locally or downloaded as JSON

### 🚀 Batch Generation Workflow
1. Navigate to the **Batch Generation** tab
2. **Select Topics** - Choose from predefined topics or add custom ones
3. **Choose Text Types** - Select multiple text types for variety
4. **Set Parameters** - Configure tasks per topic and custom instructions
5. **Preview Batch Folder** - See the auto-generated folder name before starting
6. **Generate** - Watch real-time progress with auto-save to batch subfolder
7. **Review Results** - Access comprehensive batch summary and individual tasks

### 📚 Enhanced Task Library Usage
1. Launch the Task Library tab
2. **Individual Tasks**:
   - Browse all standalone generated tasks
   - Filter by generator type, text type, or custom instructions
   - Use Learner View for interactive practice
   - Download individual tasks or bulk collections
3. **Batch Collections**:
   - View all batch folders with generation metadata
   - Access batch summaries with detailed statistics
   - Browse tasks within batches using tabbed interface
   - Download entire batches as organized ZIP files

### Browsing Generated Tasks
1. Launch the Generated Tasks Browser
2. Select "Overview Mode" to see all tasks
3. Switch to "Practice Mode" for interactive testing
4. Get immediate feedback and scoring

### Studying Reading Criteria
1. Open the Reading Criteria Browser
2. Use the search function to find specific topics
3. Explore assessment criteria and marking schemes
4. Review task types and requirements

#### Text Type Selection Features
- **Individual Tasks**: Dropdown selection with text type descriptions and examples
- **Batch Generation**: Checkbox selection for multiple text types
- **Style-Specific Prompts**: Each text type uses tailored generation instructions
- **Authentic Content**: Text types follow B2 First exam standards

## 🛠️ Development

### Recent Major Updates (v3.0 - Ollama Integration Branch)
- **📝 Custom Instructions System** - Add specific requirements and focus areas to generated tasks
- **🚀 Batch Generation with Auto-Save** - Create multiple tasks with automatic subfolder organization
- **📁 Intelligent File Management** - Timestamped batch folders with comprehensive summaries
- **📚 Enhanced Task Library** - Dual interface for individual tasks and batch collections
- **🔄 Step-by-Step LLM Generation** - Advanced approach for higher success rates
- **🛡️ Robust Error Handling** - Comprehensive failure logging and analysis
- **📊 Advanced Statistics** - Detailed metrics and success rate tracking
- **🎓 Multiple View Modes** - Learner, Summary, and JSON views for all content
- **📥 Bulk Download System** - ZIP downloads for batches and collections
- **🔍 Advanced Filtering** - Enhanced search and filter capabilities

### Previous Improvements (v2.0)
- **📝 Text Type Selection System** - 10 B2-appropriate text types with specific styling
- **Enhanced Validation** - Proper B2 First criteria (400-800 words, 5-6 questions)
- **Robust JSON Parser** - Handles complex LLM output with formatting characters
- **Improved Error Handling** - Better debugging and fallback mechanisms
- **Streamlit UI Enhancements** - Text type dropdowns, checkboxes, and information panels
- **Import Path Fixes** - Robust fallback import methods for better reliability

### Adding New Tasks
1. Use `src/content/ollama_part5_generator.py` for AI-powered generation
2. Add custom instructions for specific requirements
3. Generate individual tasks or use batch generation for multiple tasks

### Adding New Text Types
1. Update `B2_TEXT_TYPES` dictionary in `app/ollama_generator.py`
2. Add corresponding prompts in `src/llm/ollama_client.py`
3. Test generation with the new text type

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
- **pathlib** - File system operations (built-in)
- **json** - JSON processing (built-in)
- **datetime** - Timestamp generation (built-in)

## 🚀 Deployment Options

### ⚠️ Cloud Deployment Considerations

**Important**: When deploying to cloud platforms like Streamlit Cloud, generated tasks will **NOT persist** between app restarts due to ephemeral file systems.

#### Recommended Cloud Solutions:
1. **Download-Only Mode**: Users download generated tasks as JSON files
2. **Database Integration**: Add SQLite or cloud database for persistent storage
3. **Session Storage**: Tasks persist only during the current session

#### Local Development (Full Features)
- All features work including file saving and batch generation
- Tasks persist in `generated_tasks/` directory
- Batch folders and summaries are maintained

### Streamlit Cloud (Limited Persistence)
1. Connect your GitHub repository
2. Select `app/ollama_generator.py` as the main file
3. Note: Generated tasks available for download only
4. Deploy with automatic updates

### Local Development (Recommended for Full Features)
- All apps can run simultaneously on different ports
- Use the provided port configurations for testing
- Full file persistence and batch management

### Alternative Platforms
- **Heroku** - Add `Procfile` for web deployment (ephemeral storage)
- **Railway/Render** - Direct GitHub integration (ephemeral storage)
- **Docker** - Containerized deployment (add volume mounts for persistence)

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
- Ollama team for local LLM integration
- OpenAI/Ollama communities for LLM integration guidance

## 🔧 Troubleshooting

### Ollama Issues
- **Connection Failed**: Ensure Ollama is running (`ollama serve`)
- **No Models Found**: Pull a model first (`ollama pull llama3.1:8b`)
- **Generation Slow**: Try a smaller model or adjust parameters
- **Import Errors**: Install requirements (`pip install -r requirements.txt`)
- **JSON Parsing Errors**: The robust parser handles most issues automatically
- **Generation Failures**: Check `failure_logs/` directory for detailed analysis

### Streamlit Issues
- **Port Conflicts**: Use different ports for each app
- **Module Not Found**: Ensure virtual environment is activated
- **Performance**: Install watchdog (`pip install watchdog`)
- **Nested Expander Errors**: Fixed in latest version with simplified UI components
- **Duplicate Key Errors**: Resolved with unique key generation system

### Batch Generation Issues
- **Folder Creation Failed**: Check write permissions in `generated_tasks/` directory
- **Auto-Save Errors**: Ensure sufficient disk space for batch operations
- **Summary Generation Failed**: Check batch folder permissions and content

### Task Library Issues
- **Batch Not Displaying**: Ensure batch folders contain `BATCH_SUMMARY.txt`
- **View Mode Errors**: Try refreshing the page or switching view modes
- **Download Failures**: Check file permissions and browser download settings

## 📞 Support

For questions or issues:
1. Run the test suite: `python test_ollama.py`
2. Check the existing GitHub issues
3. Review `failure_logs/` for generation-specific issues
4. Create a new issue with detailed description
5. Include error messages and steps to reproduce

## 🔄 Version History

- **v3.0** (Current - Ollama Integration Branch): Custom instructions, batch generation, enhanced Task Library
- **v2.0**: Text type selection, robust JSON parsing, improved validation
- **v1.0**: Initial release with static task generation and basic Streamlit interface

---

**Built with ❤️ for Cambridge B2 First exam preparation** 