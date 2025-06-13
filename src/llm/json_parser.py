import json
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RobustJSONParser:
    """
    A robust JSON parser that can handle LLM-generated content with formatting characters.
    This parser properly escapes JSON strings while preserving the original formatting.
    """
    
    @staticmethod
    def escape_json_string(text: str) -> str:
        """
        Properly escape a string for JSON while preserving formatting.
        
        Args:
            text: The string to escape
            
        Returns:
            The escaped string safe for JSON
        """
        if not isinstance(text, str):
            return str(text)
            
        # Escape in the correct order to avoid double-escaping
        text = text.replace('\\', '\\\\')  # Escape backslashes first
        text = text.replace('"', '\\"')    # Escape quotes
        text = text.replace('\n', '\\n')   # Escape newlines
        text = text.replace('\r', '\\r')   # Escape carriage returns
        text = text.replace('\t', '\\t')   # Escape tabs
        text = text.replace('\b', '\\b')   # Escape backspace
        text = text.replace('\f', '\\f')   # Escape form feed
        
        # Escape other control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', lambda m: f'\\u{ord(m.group(0)):04x}', text)
        
        return text
    
    @staticmethod
    def fix_json_strings(json_text: str) -> str:
        """
        Fix JSON strings by properly escaping content within string values.
        This is a sophisticated approach that identifies string boundaries and escapes content.
        
        Args:
            json_text: The potentially malformed JSON text
            
        Returns:
            JSON text with properly escaped strings
        """
        try:
            # First, try to parse as-is
            json.loads(json_text)
            return json_text  # Already valid
        except json.JSONDecodeError:
            pass
        
        # If parsing failed, we need to fix the strings
        logger.info("JSON parsing failed, attempting to fix string escaping...")
        
        # Remove any markdown code blocks
        json_text = json_text.strip()
        if json_text.startswith('```json'):
            json_text = json_text[7:]
        elif json_text.startswith('```'):
            json_text = json_text[3:]
        if json_text.endswith('```'):
            json_text = json_text[:-3]
        json_text = json_text.strip()
        
        # Find JSON boundaries
        json_start = json_text.find('{')
        json_end = json_text.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            raise ValueError("Could not find JSON boundaries")
        
        json_content = json_text[json_start:json_end]
        
        # Use the improved character-by-character parser
        return RobustJSONParser._parse_and_fix_json(json_content)
    
    @staticmethod
    def _parse_and_fix_json(json_text: str) -> str:
        """
        Parse JSON character by character and fix string escaping issues.
        This version properly handles unescaped quotes within string values.
        """
        result = []
        i = 0
        in_string = False
        string_start_pos = -1
        brace_count = 0
        
        while i < len(json_text):
            char = json_text[i]
            
            if not in_string:
                # Outside of string
                if char == '{':
                    brace_count += 1
                    result.append(char)
                elif char == '}':
                    brace_count -= 1
                    result.append(char)
                    # If we've closed all braces, we might have a complete JSON object
                    if brace_count == 0:
                        # Check if there's more content after this that looks like JSON
                        remaining = json_text[i+1:].strip()
                        if not remaining or not remaining.startswith('{'):
                            # This seems to be the end of the JSON object
                            break
                elif char == '"':
                    # Start of a string
                    in_string = True
                    string_start_pos = len(result)
                    result.append(char)
                else:
                    # Regular JSON structure character
                    result.append(char)
            else:
                # Inside a string
                if char == '"':
                    # This could be the end of the string, or an unescaped quote
                    # We need to look ahead to see if this makes sense as an end quote
                    
                    # Look ahead to see what comes next (skip whitespace)
                    next_meaningful_char = None
                    j = i + 1
                    while j < len(json_text) and json_text[j].isspace():
                        j += 1
                    if j < len(json_text):
                        next_meaningful_char = json_text[j]
                    
                    # If the next meaningful character suggests this is the end of a string value
                    # (comma, closing brace, closing bracket, colon), then treat it as string end
                    if next_meaningful_char in [',', '}', ']', ':']:
                        # This is likely the end of the string
                        result.append(char)
                        in_string = False
                    else:
                        # This is likely an unescaped quote within the string
                        result.append('\\"')  # Escape it
                else:
                    # Regular character inside string - escape special characters
                    if char == '\\':
                        # Check if it's already a valid escape sequence
                        if i + 1 < len(json_text) and json_text[i + 1] in ['"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u']:
                            # Valid escape sequence, keep as-is
                            result.append(char)
                        else:
                            # Escape the backslash
                            result.append('\\\\')
                    elif char == '\n':
                        result.append('\\n')
                    elif char == '\r':
                        result.append('\\r')
                    elif char == '\t':
                        result.append('\\t')
                    elif char == '\b':
                        result.append('\\b')
                    elif char == '\f':
                        result.append('\\f')
                    elif ord(char) < 32 or ord(char) == 127:
                        # Other control characters
                        result.append(f'\\u{ord(char):04x}')
                    else:
                        result.append(char)
            
            i += 1
        
        # If we're still in a string at the end, close it
        if in_string:
            result.append('"')
        
        # If we have unmatched braces, try to close them
        while brace_count > 0:
            result.append('}')
            brace_count -= 1
        
        return ''.join(result)
    
    @staticmethod
    def parse_llm_json(json_text: str, max_attempts: int = 4) -> Dict[str, Any]:
        """
        Parse JSON from LLM output with multiple fallback strategies.
        
        Args:
            json_text: The JSON text from LLM
            max_attempts: Maximum number of parsing attempts
            
        Returns:
            Parsed JSON as dictionary
            
        Raises:
            ValueError: If JSON cannot be parsed after all attempts
        """
        original_text = json_text
        
        for attempt in range(max_attempts):
            try:
                logger.debug(f"JSON parsing attempt {attempt + 1}")
                
                if attempt == 0:
                    # First attempt: try as-is
                    return json.loads(json_text)
                elif attempt == 1:
                    # Second attempt: basic cleanup
                    json_text = RobustJSONParser._basic_cleanup(original_text)
                    return json.loads(json_text)
                elif attempt == 2:
                    # Third attempt: full string fixing
                    json_text = RobustJSONParser.fix_json_strings(original_text)
                    return json.loads(json_text)
                else:
                    # Final attempt: try to extract and fix partial JSON
                    json_text = RobustJSONParser._extract_partial_json(original_text)
                    return json.loads(json_text)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    # Last attempt failed
                    logger.error(f"All JSON parsing attempts failed")
                    logger.error(f"Original text (first 500 chars): {original_text[:500]}")
                    logger.error(f"Final processed text (first 500 chars): {json_text[:500]}")
                    raise ValueError(f"Could not parse JSON after {max_attempts} attempts: {str(e)}")
                continue
        
        # Should never reach here
        raise ValueError("Unexpected error in JSON parsing")
    
    @staticmethod
    def _basic_cleanup(json_text: str) -> str:
        """Basic cleanup of JSON text."""
        # Remove markdown code blocks
        json_text = json_text.strip()
        if json_text.startswith('```json'):
            json_text = json_text[7:]
        elif json_text.startswith('```'):
            json_text = json_text[3:]
        if json_text.endswith('```'):
            json_text = json_text[:-3]
        json_text = json_text.strip()
        
        # Find JSON boundaries
        json_start = json_text.find('{')
        json_end = json_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_text = json_text[json_start:json_end]
        
        return json_text
    
    @staticmethod
    def _extract_partial_json(json_text: str) -> str:
        """
        Extract and fix partial JSON that might be incomplete.
        This is a last-resort method for handling truncated responses.
        """
        # Basic cleanup first
        json_text = RobustJSONParser._basic_cleanup(json_text)
        
        # Try to find the main JSON structure
        start = json_text.find('{')
        if start == -1:
            raise ValueError("No JSON object found")
        
        # Count braces to find where the JSON might end
        brace_count = 0
        end = start
        
        for i in range(start, len(json_text)):
            if json_text[i] == '{':
                brace_count += 1
            elif json_text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        # Extract the JSON portion
        json_portion = json_text[start:end]
        
        # If it's incomplete, try to complete it
        if brace_count > 0:
            # We have unclosed braces, try to close them
            json_portion += '}' * brace_count
        
        # Apply string fixing
        return RobustJSONParser._parse_and_fix_json(json_portion) 