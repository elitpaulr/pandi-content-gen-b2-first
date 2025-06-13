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
    def _preprocess_llm_json(json_text: str) -> str:
        """
        Preprocess LLM-generated JSON to fix common formatting issues.
        This handles patterns that commonly appear in LLM output.
        """
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
        
        if json_start == -1 or json_end <= json_start:
            raise ValueError("Could not find JSON boundaries")
        
        json_content = json_text[json_start:json_end]
        
        # FIRST: Handle the specific control character issue - unescaped newlines
        # This is the most common cause of "Invalid control character" errors
        
        # The core issue: LLM generates literal newlines in JSON strings like:
        # "text": "Line 1
        # Line 2"
        # But JSON requires: "text": "Line 1\nLine 2"
        
        # Quick fix for the most common case: escape literal newlines in string values
        import re
        
        # Step 1: Find and fix unescaped newlines within string values
        # We need to be careful not to break the JSON structure
        
        def escape_newlines_in_strings(text):
            """Escape literal newlines within JSON string values"""
            result = []
            i = 0
            in_string = False
            
            while i < len(text):
                char = text[i]
                
                if char == '"' and (i == 0 or text[i-1] != '\\'):
                    # Toggle string state
                    in_string = not in_string
                    result.append(char)
                elif in_string and char == '\n':
                    # We're inside a string and found a literal newline - escape it
                    result.append('\\n')
                elif in_string and char == '\r':
                    # Also handle carriage returns
                    result.append('\\r')
                elif in_string and char == '\t':
                    # And tabs
                    result.append('\\t')
                elif in_string and ord(char) < 32 or ord(char) == 127:
                    # Other control characters
                    result.append(f'\\u{ord(char):04x}')
                else:
                    result.append(char)
                
                i += 1
            
            return ''.join(result)
        
        try:
            # Apply the newline escaping
            fixed_content = escape_newlines_in_strings(json_content)
            
            # Test if this creates valid JSON
            json.loads(fixed_content)
            logger.debug("Successfully fixed JSON by escaping control characters")
            return fixed_content
            
        except Exception as e:
            logger.debug(f"Control character escaping failed: {e}, trying regex approach")
        
        # FALLBACK: Try the regex approach for more complex cases
        def fix_text_field(match):
            """Fix a complete text field including quotes"""
            field_name = match.group(1)  # "text" or other field name
            field_value = match.group(2)  # The content between quotes
            
            # Fix control characters and escaping in the field value
            fixed_value = RobustJSONParser.escape_json_string(field_value)
            
            return f'"{field_name}": "{fixed_value}"'
        
        # Pattern to match any string field (not just "text")
        # This catches: "fieldname": "content with potential issues"
        string_field_pattern = r'"([^"]+)"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'
        
        try:
            # Apply the fix to all string fields
            fixed_content = re.sub(string_field_pattern, fix_text_field, json_content, flags=re.DOTALL)
            
            # Test if this creates valid JSON
            json.loads(fixed_content)
            logger.debug("Successfully fixed JSON using regex approach")
            return fixed_content
            
        except Exception as e:
            logger.debug(f"Regex-based fixing failed: {e}, trying manual approach")
        
        # FALLBACK: Use more sophisticated state machine approach for complex cases
        # This handles cases where the regex approach fails due to complex nesting
        
        result = []
        i = 0
        in_string = False
        in_field_name = False
        current_field = ""
        
        while i < len(json_content):
            char = json_content[i]
            
            if char == '"' and (i == 0 or json_content[i-1] != '\\'):
                if not in_string:
                    # Starting a string
                    in_string = True
                    # Check if this is a field name by looking ahead
                    next_colon = json_content.find(':', i)
                    next_quote = json_content.find('"', i + 1)
                    if next_colon != -1 and next_quote != -1 and next_colon < next_quote:
                        in_field_name = True
                        current_field = ""
                    else:
                        in_field_name = False
                    result.append(char)
                else:
                    # Ending a string
                    in_string = False
                    if in_field_name:
                        in_field_name = False
                    result.append(char)
            elif in_string:
                if in_field_name:
                    # Collecting field name
                    current_field += char
                    result.append(char)
                else:
                    # We're in a field value - apply escaping
                    if char == '\n':
                        result.append('\\n')
                    elif char == '\r':
                        result.append('\\r')
                    elif char == '\t':
                        result.append('\\t')
                    elif char == '\b':
                        result.append('\\b')
                    elif char == '\f':
                        result.append('\\f')
                    elif char == '\\':
                        # Check if it's already a valid escape
                        if i + 1 < len(json_content) and json_content[i + 1] in ['"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u']:
                            result.append(char)
                        else:
                            result.append('\\\\')
                    elif ord(char) < 32 or ord(char) == 127:
                        # Control characters
                        result.append(f'\\u{ord(char):04x}')
                    else:
                        result.append(char)
            else:
                # Outside of strings
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    @staticmethod
    def _extract_and_fix_text_content(json_content: str, start_pos: int) -> tuple:
        """
        Extract and fix text content from a text field, handling complex cases.
        Returns (fixed_content, end_position) or (None, start_pos) if failed.
        """
        # State machine to track JSON structure
        pos = start_pos
        content_chars = []
        
        while pos < len(json_content):
            char = json_content[pos]
            
            if char == '"':
                # Check if this quote is escaped
                escaped = False
                backslash_count = 0
                check_pos = pos - 1
                
                # Count consecutive backslashes before this quote
                while check_pos >= 0 and json_content[check_pos] == '\\':
                    backslash_count += 1
                    check_pos -= 1
                
                escaped = (backslash_count % 2 == 1)
                
                if not escaped:
                    # This might be the end of the text field
                    # Look ahead to confirm
                    next_pos = pos + 1
                    while next_pos < len(json_content) and json_content[next_pos].isspace():
                        next_pos += 1
                    
                    if next_pos < len(json_content) and json_content[next_pos] in [',', '}', ']']:
                        # This is the end of the text field
                        full_content = ''.join(content_chars)
                        escaped_content = RobustJSONParser.escape_json_string(full_content)
                        return escaped_content + '"', pos + 1  # Add closing quote
                    else:
                        # This is a quote within the text, add it to content
                        content_chars.append(char)
                else:
                    # This is an escaped quote, add it to content
                    content_chars.append(char)
            else:
                # Regular character in text content
                content_chars.append(char)
            
            pos += 1
        
        # If we reach here, we didn't find a proper end
        # Return the content we have so far, properly escaped and closed
        if content_chars:
            full_content = ''.join(content_chars)
            escaped_content = RobustJSONParser.escape_json_string(full_content)
            return escaped_content + '"', pos  # Add closing quote
        
        return None, start_pos
    
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
        
        # Apply preprocessing first
        try:
            json_text = RobustJSONParser._preprocess_llm_json(json_text)
        except Exception as e:
            logger.warning(f"Preprocessing failed: {e}, continuing with original text")
        
        # Use the improved character-by-character parser
        return RobustJSONParser._parse_and_fix_json(json_text)
    
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
        bracket_count = 0
        current_key = None
        
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
                elif char == '[':
                    bracket_count += 1
                    result.append(char)
                elif char == ']':
                    bracket_count -= 1
                    result.append(char)
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
                    
                    # Special handling for text fields which often contain dialogue
                    # Look back to see if we're in a "text" field
                    recent_content = ''.join(result[-50:]).lower() if len(result) >= 50 else ''.join(result).lower()
                    in_text_field = '"text"' in recent_content and recent_content.rfind('"text"') > recent_content.rfind('}')
                    
                    # If we're in a text field and this quote is followed by dialogue patterns,
                    # it's likely an unescaped quote
                    if in_text_field and next_meaningful_char and next_meaningful_char not in [',', '}', ']', ':']:
                        # Look for dialogue patterns
                        remaining_text = json_text[i+1:i+20]  # Look ahead 20 chars
                        dialogue_indicators = [' said', ' asked', ' replied', ' thought', ' whispered', ' shouted']
                        is_dialogue = any(indicator in remaining_text.lower() for indicator in dialogue_indicators)
                        
                        # Also check if this looks like the start of dialogue
                        prev_chars = json_text[max(0, i-10):i]
                        starts_dialogue = any(pattern in prev_chars for pattern in ['. ', '.\n', '? ', '!\n', '! '])
                        
                        if is_dialogue or starts_dialogue:
                            # This is likely dialogue, escape the quote
                            result.append('\\"')
                        else:
                            # Check normal end-of-string patterns
                            if next_meaningful_char in [',', '}', ']', ':']:
                                result.append(char)
                                in_string = False
                            else:
                                result.append('\\"')
                    else:
                        # Normal end-of-string detection
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
            
        # If we have unmatched brackets, try to close them
        while bracket_count > 0:
            result.append(']')
            bracket_count -= 1
        
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
                    # Second attempt: use preprocessing to fix common LLM issues (control characters, etc.)
                    logger.debug("Applying preprocessing to fix control characters and escaping")
                    json_text = RobustJSONParser._preprocess_llm_json(original_text)
                    return json.loads(json_text)
                elif attempt == 2:
                    # Third attempt: more aggressive string fixing with dialogue detection
                    logger.info("JSON parsing failed, attempting to fix string escaping...")
                    json_text = RobustJSONParser.fix_json_strings(original_text)
                    return json.loads(json_text)
                else:
                    # Final attempt: try to extract and fix partial JSON
                    logger.debug("Attempting to extract and fix partial JSON")
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
        try:
            return RobustJSONParser._preprocess_llm_json(json_text)
        except Exception as e:
            logger.warning(f"Preprocessing failed in basic cleanup: {e}")
            # Fallback to original simple cleanup
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