# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. Server Disconnected
**Problem:** Ollama service is not running or has stopped
**Solution:** Restart Ollama service
```bash
ollama serve
```

### 2. JSON Parsing Errors
**Problem:** The AI model output cannot be parsed as valid JSON
**Solutions:**
- Try a different topic or text type
- Use simpler, more specific topics
- Check if the model is overloaded

### 3. Validation Failures
**Problem:** The LLM output doesn't meet B2 requirements
**Solutions:**
- Ensure topics are appropriate for B2 level
- Try different text types
- Use custom instructions to guide the AI

### 4. Connection Timeouts
**Problem:** Requests to Ollama are timing out
**Solutions:**
- Check your internet connection
- Restart Ollama service
- Try a smaller model if using a large one

### 5. Model Not Found
**Problem:** Selected model is not available
**Solutions:**
- Pull the model: `ollama pull llama3.1:8b`
- Check available models: `ollama list`
- Select a different model from the dropdown

## If Problems Persist

- Try using a different model (e.g., switch from llama3.1:8b to mistral:latest)
- Simplify the topic to something more straightforward
- Check the Ollama logs for detailed error messages
- Restart the Streamlit application

## Getting Help

If you continue to experience issues:
1. Check the failure logs in the `failure_logs/` directory
2. Review the batch summary files for patterns
3. Use the QA Review system to identify common problems
4. Consider adjusting generation parameters (temperature, max tokens) 