# 🏠 Getting Started Guide

## Welcome to the B2 First Content Generation Tool

This tool helps you create high-quality Cambridge B2 First Reading Part 5 tasks using local AI models through Ollama.

## Prerequisites

### Required Software

**Ollama Installation:**
1. Visit https://ollama.ai/
2. Download and install Ollama for your operating system
3. Start Ollama service: `ollama serve`
4. Pull a recommended model: `ollama pull llama3.1:8b`

**Python Environment:**
- Python 3.10 or higher
- Virtual environment recommended
- Required packages (see requirements.txt)

### System Requirements

**Minimum:**
- 4GB RAM
- 2GB free disk space
- Internet connection for initial setup

**Recommended:**
- 8GB RAM
- 5GB free disk space
- Multi-core processor

## Quick Start

### 1. First Launch

1. Start Ollama: `ollama serve`
2. Launch the application: `streamlit run app/ollama_generator.py`
3. Check that Ollama connection shows ✅ green status
4. Select your preferred model from the sidebar

### 2. Generate Your First Task

1. Go to the **🎯 Generate Tasks** tab
2. Enter a topic (e.g., "sustainable travel and eco-tourism")
3. Select a text type (e.g., "Magazine Article")
4. Click **🚀 Generate Task**
5. Wait 2-5 minutes for generation to complete
6. Review and save your task

### 3. Explore Features

**📊 Batch Generation:** Create multiple tasks efficiently
**📚 Task Library:** Review and manage generated content
**🔍 QA Review:** Evaluate task quality systematically
**⚙️ Admin Panel:** Configure AI prompts and parameters

## Understanding the Interface

### Main Tabs

**🎯 Generate Tasks:** Single task creation with custom options
**🔧 Improve Tasks:** Future feature for task enhancement
**📊 Batch Generation:** Bulk task creation with topic sets
**📚 Task Library:** Browse, review, and manage tasks
**⚙️ Admin Panel:** System configuration and prompts
**📖 Docs:** Comprehensive documentation

### Sidebar Configuration

**Model Selection:** Choose from available Ollama models
**Generation Parameters:** Adjust temperature and max tokens
**Save Settings:** Enable auto-save for generated tasks

## Best Practices for New Users

### Topic Selection

**Good Topics:**
- Contemporary and relevant subjects
- Culturally neutral themes
- Age-appropriate for teenagers/young adults
- Specific enough to generate focused content

**Examples:**
- "sustainable travel and eco-tourism"
- "remote work productivity strategies"
- "digital wellness and screen time management"
- "urban gardening and community spaces"

### Text Type Selection

**For Beginners:**
- Start with "Magazine Article" or "Blog Post"
- These tend to generate more consistent results
- Gradually explore other text types

**Text Type Variety:**
- Magazine Article: Informative, engaging style
- Blog Post: Personal, conversational tone
- News Report: Factual, journalistic approach
- Educational Feature: Instructional content

### Quality Control

**Use QA Review:**
1. Generate several tasks initially
2. Review them in the Task Library
3. Use QA Review mode to evaluate quality
4. Note patterns in successful vs. problematic tasks
5. Adjust your approach based on findings

## Common First-Time Issues

### Ollama Not Connected
**Problem:** Red ❌ status in the interface
**Solution:** 
1. Ensure Ollama is running: `ollama serve`
2. Check available models: `ollama list`
3. Pull a model if needed: `ollama pull llama3.1:8b`

### Generation Failures
**Problem:** Tasks fail validation or generation
**Solutions:**
1. Try simpler, more specific topics
2. Use different text types
3. Check failure logs for details
4. Adjust generation parameters

### Poor Quality Output
**Problem:** Generated tasks don't meet B2 standards
**Solutions:**
1. Use custom instructions to guide the AI
2. Try different models (llama3.1:8b vs mistral:latest)
3. Review B2 standards documentation
4. Use QA Review to identify specific issues

## Next Steps

### After Your First Success

1. **Generate a small batch** (3-6 tasks) to understand consistency
2. **Use QA Review extensively** to learn quality indicators
3. **Experiment with different text types** and topics
4. **Read the B2 Standards documentation** for quality guidelines
5. **Explore batch generation** for efficient content creation

### Building Your Workflow

1. **Develop topic lists** for different themes
2. **Create custom instructions** for consistent quality
3. **Establish QA review processes** for quality control
4. **Organize generated content** using the Task Library
5. **Monitor and adjust** based on success patterns

## Getting Help

### Built-in Resources
- **📖 Docs tab:** Comprehensive guides and standards
- **🔧 Troubleshooting:** Common issues and solutions
- **Failure logs:** Detailed error information in `failure_logs/`

### Self-Help Tips
1. Check the troubleshooting guide first
2. Review failure logs for specific errors
3. Try different topics or text types
4. Adjust generation parameters
5. Restart Ollama if connection issues persist

### Quality Improvement
1. Use QA Review to identify patterns
2. Study successful vs. failed tasks
3. Refine your topic selection approach
4. Develop effective custom instructions
5. Build a library of high-quality examples 