"""
Configuration Service for B2 First Task Generator
Handles all JSON configuration loading with robust error handling and fallbacks
"""

import json
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigService:
    """
    Centralized configuration management service
    Loads and manages all JSON configuration files with fallback support
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize the configuration service
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.config_dir = project_root / "config"
        
        # Load all configurations
        self._load_configurations()
    
    def _load_configurations(self):
        """Load all configuration files"""
        # Load B2 text types
        self.b2_text_types = self._load_json_config(
            'b2_text_types.json', 
            self._get_fallback_b2_text_types()
        )
        
        # Load unified topics knowledge base
        kb_path = self.project_root / "knowledge_base" / "b2_first_recommended_topics.json"
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)["b2_first_recommended_topics"]
        except Exception as e:
            st.error(f"❌ Error loading knowledge base: {e}")
            kb_data = {}
        self.topic_knowledge_base = kb_data
        self.topic_categories = kb_data.get("categories", {})
        self.usage_guidelines = kb_data.get("usage_guidelines", {})
        # Build topic sets (category name -> topic list)
        self.topic_sets = {cat_info["name"]: cat_info["topics"] for cat_info in self.topic_categories.values()} if self.topic_categories else {}
    
    def _load_json_config(self, filename: str, fallback_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Load JSON configuration with fallback to default data
        
        Args:
            filename: Name of the JSON file to load
            fallback_data: Default data to use if file doesn't exist or fails to load
            
        Returns:
            Dictionary containing the configuration data
        """
        file_path = self.config_dir / filename
        
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            else:
                st.warning(f"⚠️ Configuration file not found: {filename}")
                return fallback_data if fallback_data else {}
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON in {filename}: {e}")
            return fallback_data if fallback_data else {}
        except Exception as e:
            st.error(f"❌ Error loading {filename}: {e}")
            return fallback_data if fallback_data else {}
    
    def _get_fallback_b2_text_types(self) -> Dict[str, Any]:
        """Fallback data for B2 text types"""
        return {
            "📰 Magazine Article": {
                "key": "magazine_article",
                "description": "Informative articles from lifestyle, science, or general interest magazines",
                "examples": ["Health and wellness trends", "Technology reviews", "Travel destinations"]
            },
            "✍️ Personal Blog Post": {
                "key": "blog_post",
                "description": "First-person accounts of experiences and reflections",
                "examples": ["Travel experiences", "Career changes", "Personal challenges"]
            }
        }
    
    def get_topic_knowledge_base(self) -> Dict[str, Any]:
        """Get the full topic knowledge base (all metadata, categories, guidelines)"""
        return self.topic_knowledge_base
    
    def get_usage_guidelines(self) -> Dict[str, Any]:
        """Get topic usage guidelines"""
        return self.usage_guidelines
    
    # Public getter methods
    def get_b2_text_types(self) -> Dict[str, Any]:
        """Get B2 text types configuration"""
        return self.b2_text_types
    
    def get_topic_categories(self) -> Dict[str, Any]:
        """Get topic categories configuration"""
        return self.topic_categories
    
    def get_topic_sets(self) -> Dict[str, Any]:
        """Get topic sets configuration"""
        return self.topic_sets
    
    def get_text_type_options(self) -> list:
        """Get list of text type options for UI"""
        return list(self.b2_text_types.keys())
    
    def get_text_type_info(self, text_type_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific text type"""
        return self.b2_text_types.get(text_type_name, {})
    
    def get_category_topics(self, category_name: str) -> list:
        """Get topics for a specific category"""
        return self.topic_categories.get(category_name, [])
    
    def get_topic_set(self, set_name: str) -> list:
        """Get topics for a specific topic set"""
        return self.topic_sets.get(set_name, [])
    
    def reload_configurations(self):
        """Reload all configurations (useful for admin panel)"""
        self._load_configurations()
        st.success("🔄 All configurations reloaded successfully!")
    
    def validate_configurations(self) -> Dict[str, bool]:
        """Validate all configurations and return status"""
        validation_results = {
            'b2_text_types': bool(self.b2_text_types),
            'topic_categories': bool(self.topic_categories),
            'topic_sets': bool(self.topic_sets)
        }
        
        # Additional validation checks
        for text_type_name, text_type_info in self.b2_text_types.items():
            if not isinstance(text_type_info, dict) or 'key' not in text_type_info:
                validation_results['b2_text_types'] = False
                break
        
        return validation_results
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary information about loaded configurations"""
        return {
            'b2_text_types_count': len(self.b2_text_types),
            'topic_categories_count': len(self.topic_categories),
            'topic_sets_count': len(self.topic_sets),
            'config_directory': str(self.config_dir),
            'validation': self.validate_configurations()
        } 