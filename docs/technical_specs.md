# 🔧 Technical Specifications

## System Architecture

### Core Components

**LLM Integration:** Ollama with local models
- Primary models: Llama 3.1:8b, Mistral:latest
- Local processing for privacy and control
- Configurable parameters (temperature, max tokens)

**Content Generation:** Step-by-step task creation with validation
- Multi-stage generation process
- JSON-based output format
- Robust error handling and retry logic

**JSON Processing:** Robust parsing with error recovery
- Custom JSON parser with fallback strategies
- Control character handling
- Validation against B2 standards

**File Management:** Auto-save, batch processing, organized storage
- Automatic file naming and organization
- Batch collection management
- Export and download capabilities

**QA System:** Comprehensive review and annotation workflow
- Multi-level annotation system
- Status tracking and filtering
- Reviewer identification and timestamping

### Text Types Available

**Primary Text Types:**
- Magazine Article
- Blog Post
- News Report
- Professional Feature
- Educational Feature
- Cultural Review
- Travel Writing
- Lifestyle Feature
- Opinion Piece
- Novel Extract

Each text type has specific style guidelines and generation instructions.

## QA System Features

### Review Capabilities

**Multi-level Annotation:**
- Overall task assessment
- Title evaluation
- Text quality review
- Individual question analysis

**Status Tracking:**
- Pending (default status)
- Approved (meets standards)
- Rejected (needs improvement)

**Reviewer Features:**
- Reviewer identification
- Timestamp tracking
- Detailed notes and feedback
- Status change history

**Filtering and Sorting:**
- Filter by QA status
- Sort by creation date, topic, text type
- Search functionality
- Batch operations

### Data Management

**JSON-based Annotation Storage:**
- Embedded annotations in task files
- Structured data format
- Cross-session persistence

**Real-time Status Updates:**
- Immediate status changes
- Live filtering and sorting
- Dynamic statistics

**Export and Download:**
- Individual task download
- Batch collection export
- ZIP file generation for batches

## File Structure

### Directory Organization

```
project/
├── app/                    # Streamlit frontend
│   ├── ollama_generator.py # Main application
│   └── services/          # Service layer
├── src/                   # Core logic
│   ├── llm/              # LLM clients
│   └── content/          # Content generation
├── docs/                 # Documentation
├── generated_tasks/      # Output directory
├── failure_logs/         # Error logs
└── knowledge_base/       # Reference materials
```

### File Naming Conventions

**Task Files:** `reading_part5_task_XX.json`
**Batch Folders:** `batch_YYYYMMDD_HHMMSS_Ntopics_Mtypes`
**Failure Logs:** `task_XX_failure_YYYYMMDD_HHMMSS.txt`

## API Specifications

### Ollama Integration

**Connection Management:**
- Health check endpoint
- Model availability verification
- Error handling for disconnections

**Generation Parameters:**
- Temperature: 0.1-1.0 (default 0.7)
- Max tokens: 1000-4000 (default 2000)
- Model selection from available models

**Request/Response Format:**
- JSON-based communication
- Streaming support for long responses
- Timeout handling

## Performance Specifications

### Generation Times

**Single Task:** 2-5 minutes average
- Title generation: 10-30 seconds
- Text generation: 60-120 seconds
- Question generation: 60-180 seconds
- Validation: 5-10 seconds

**Batch Generation:** Scales linearly
- 6 tasks: 15-30 minutes
- 12 tasks: 30-60 minutes
- Progress tracking and status updates

### Resource Requirements

**Memory:** 4GB minimum, 8GB recommended
**Storage:** 1GB for application, additional for generated content
**CPU:** Multi-core recommended for concurrent processing
**Network:** Local network for Ollama communication

## Security Considerations

### Data Privacy
- All processing done locally
- No external API calls for content generation
- User data remains on local system

### File Security
- Organized directory structure
- Proper file permissions
- Backup recommendations

### Input Validation
- Topic and instruction sanitization
- File path validation
- JSON structure verification

## Best Practices

### Content Creation Guidelines
- Choose contemporary, relevant subjects
- Ensure cultural neutrality and age appropriateness
- Balance familiar and challenging concepts

### Quality Control
- Use QA Review mode for systematic evaluation
- Filter by status to prioritize pending tasks
- Provide specific, constructive feedback
- Track approval rates and common issues

### Performance Optimization
- Use appropriate model for task complexity
- Monitor generation times and adjust parameters
- Regular cleanup of failure logs
- Batch processing for efficiency

### Maintenance
- Regular model updates
- Log file rotation
- Backup of generated content
- System health monitoring 