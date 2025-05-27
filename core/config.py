"""
Core Configuration Management
"""

import os
import yaml
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from copy import deepcopy
import logging

from core.exceptions import ConfigurationError

@dataclass
class ModelConfig:
    """Model configuration dataclass"""
    name: str
    base_url: str
    api_key: str
    model: str
    details: str
    max_tokens: int = 128000
    temperature: float = 0.7
    timeout: int = 60
    retries: int = 3
    enabled: bool = True
    cost_per_token: float = 0.0
    capabilities: List[str] = field(default_factory=list)

@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    workspace_dir: str = "./sandbox_workspaces"
    max_workspaces: int = 10
    max_file_size_mb: int = 100
    max_execution_time: int = 300
    allowed_commands: List[str] = field(default_factory=lambda: [
        "python", "pip", "node", "npm", "git", "curl", "wget"
    ])
    blocked_commands: List[str] = field(default_factory=lambda: [
        "rm", "del", "format", "shutdown", "reboot", "net", "reg"
    ])
    resource_limits: Dict[str, Any] = field(default_factory=lambda: {
        "memory_mb": 2048,
        "cpu_percent": 80,
        "disk_mb": 1024
    })

@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str = "./data/database.sqlite"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backups: int = 7
    connection_pool_size: int = 5

@dataclass
class MemoryConfig:
    """Memory and ChromaDB configuration"""
    chromadb_path: str = "./data/embeddings"
    embedding_model: str = "all-MiniLM-L6-v2"
    max_memory_items: int = 1000
    summary_threshold: int = 10
    similarity_threshold: float = 0.7
    collection_name: str = "ai_assistant_memory"

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    log_dir: str = "./data/logs"
    max_file_size_mb: int = 10
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_console: bool = True
    enable_file: bool = True

@dataclass
class SecurityConfig:
    """Security settings"""
    api_key_encryption: bool = True
    sandbox_isolation: bool = True
    command_validation: bool = True
    file_access_restrictions: bool = True
    network_restrictions: bool = True
    max_request_size_mb: int = 50

@dataclass
class UIConfig:
    """UI and interaction settings"""
    interactive_mode: bool = True
    progress_bars: bool = True
    colored_output: bool = True
    confirm_dangerous_actions: bool = True
    auto_save_sessions: bool = True
    session_timeout_minutes: int = 60

class ConfigManager:
    """Main configuration manager"""
    
    def __init__(self, config_dir: Union[str, Path]):
        self.config_dir = Path(config_dir)
        self.models: Dict[str, ModelConfig] = {}
        self.sandbox: SandboxConfig = SandboxConfig()
        self.database: DatabaseConfig = DatabaseConfig()
        self.memory: MemoryConfig = MemoryConfig()
        self.logging: LoggingConfig = LoggingConfig()
        self.security: SecurityConfig = SecurityConfig()
        self.ui: UIConfig = UIConfig()
        self.custom_settings: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    async def load_config(self):
        """Load configuration from files"""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load main settings
            await self._load_main_settings()
            
            # Load model configurations
            await self._load_model_configs()
            
            # Load tool configurations
            await self._load_tool_configs()
            
            # Load security policies
            await self._load_security_policies()
            
            # Validate configuration
            await self._validate_config()
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    async def _load_main_settings(self):
        """Load main settings from settings.yaml"""
        settings_file = self.config_dir / "settings.yaml"
        
        if not settings_file.exists():
            await self._create_default_settings()
            
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = yaml.safe_load(f) or {}
            
            # Update configurations
            if 'sandbox' in settings:
                self.sandbox = SandboxConfig(**settings['sandbox'])
                
            if 'database' in settings:
                self.database = DatabaseConfig(**settings['database'])
                
            if 'memory' in settings:
                self.memory = MemoryConfig(**settings['memory'])
                
            if 'logging' in settings:
                self.logging = LoggingConfig(**settings['logging'])
                
            if 'security' in settings:
                self.security = SecurityConfig(**settings['security'])
                
            if 'ui' in settings:
                self.ui = UIConfig(**settings['ui'])
                
            if 'custom' in settings:
                self.custom_settings = settings['custom']
                
        except Exception as e:
            raise ConfigurationError(f"Error loading settings.yaml: {e}")
    
    async def _load_model_configs(self):
        """Load model configurations"""
        models_file = self.config_dir / "models.yaml"
        
        if not models_file.exists():
            await self._create_default_models()
        
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                models_data = yaml.safe_load(f) or {}
            
            self.models = {}
            for model_name, model_data in models_data.get('models', {}).items():
                self.models[model_name] = ModelConfig(
                    name=model_name,
                    **model_data
                )
                
        except Exception as e:
            raise ConfigurationError(f"Error loading models.yaml: {e}")
    
    async def _load_tool_configs(self):
        """Load tool configurations"""
        tools_file = self.config_dir / "tools.yaml"
        
        if tools_file.exists():
            try:
                with open(tools_file, 'r', encoding='utf-8') as f:
                    tools_data = yaml.safe_load(f) or {}
                    
                # Update tool-specific settings
                if 'code_quality' in tools_data:
                    self.custom_settings['code_quality'] = tools_data['code_quality']
                    
                if 'browser' in tools_data:
                    self.custom_settings['browser'] = tools_data['browser']
                    
            except Exception as e:
                self.logger.warning(f"Could not load tools.yaml: {e}")
    
    async def _load_security_policies(self):
        """Load security policies"""
        security_file = self.config_dir / "security_policies.yaml"
        
        if security_file.exists():
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    security_data = yaml.safe_load(f) or {}
                
                # Update security settings
                if 'policies' in security_data:
                    for key, value in security_data['policies'].items():
                        if hasattr(self.security, key):
                            setattr(self.security, key, value)
                            
                # Update sandbox security
                if 'sandbox_policies' in security_data:
                    policies = security_data['sandbox_policies']
                    if 'allowed_commands' in policies:
                        self.sandbox.allowed_commands = policies['allowed_commands']
                    if 'blocked_commands' in policies:
                        self.sandbox.blocked_commands = policies['blocked_commands']
                        
            except Exception as e:
                self.logger.warning(f"Could not load security_policies.yaml: {e}")
    
    async def _create_default_settings(self):
        """Create default settings.yaml"""
        default_settings = {
            'sandbox': asdict(SandboxConfig()),
            'database': asdict(DatabaseConfig()),
            'memory': asdict(MemoryConfig()),
            'logging': asdict(LoggingConfig()),
            'security': asdict(SecurityConfig()),
            'ui': asdict(UIConfig()),
            'custom': {}
        }
        
        settings_file = self.config_dir / "settings.yaml"
        with open(settings_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_settings, f, default_flow_style=False)
    
    async def _create_default_models(self):
        """Create default models.yaml with provided model configurations"""
        default_models = {
            'models': {
                'devstral_small': {
                    'base_url': 'https://openrouter.ai/api/v1',
                    'api_key': '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',
                    'model': 'mistralai/devstral-small:free',
                    'details': 'Devstral-Small-2505 is a 24B parameter agentic LLM fine-tuned from Mistral-Small-3.1, jointly developed by Mistral AI and All Hands AI for advanced software engineering tasks.',
                    'max_tokens': 128000,
                    'temperature': 0.7,
                    'capabilities': ['coding', 'agents', 'file_editing']
                },
                'llama_3_3_8b': {
                    'base_url': 'https://openrouter.ai/api/v1',
                    'api_key': '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',
                    'model': 'meta-llama/llama-3.3-8b-instruct:free',
                    'details': 'A lightweight and ultra-fast variant of Llama 3.3 70B, for use when quick response times are needed most.',
                    'max_tokens': 128000,
                    'temperature': 0.7,
                    'capabilities': ['general', 'fast_response']
                },
                'phi_4_reasoning': {
                    'base_url': 'https://openrouter.ai/api/v1',
                    'api_key': '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',
                    'model': 'microsoft/phi-4-reasoning-plus:free',
                    'details': 'Phi-4-reasoning-plus is an enhanced 14B parameter model from Microsoft, fine-tuned with additional reinforcement learning to boost accuracy on math, science, and code reasoning tasks.',
                    'max_tokens': 128000,
                    'temperature': 0.3,
                    'capabilities': ['reasoning', 'math', 'science', 'coding']
                },
                'deepseek_v3': {
                    'base_url': 'https://openrouter.ai/api/v1',
                    'api_key': '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',
                    'model': 'deepseek/deepseek-chat-v3-0324:free',
                    'details': 'DeepSeek V3, a 685B-parameter, mixture-of-experts model, is the latest iteration of the flagship chat model family.',
                    'max_tokens': 163840,
                    'temperature': 0.7,
                    'capabilities': ['general', 'conversation', 'large_context']
                },
                'qwen3_30b': {
                    'base_url': 'https://openrouter.ai/api/v1',
                    'api_key': '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',
                    'model': 'qwen/qwen3-30b-a3b:free',
                    'details': 'Qwen3 features both dense and mixture-of-experts (MoE) architectures to excel in reasoning, multilingual support, and advanced agent tasks.',
                    'max_tokens': 131072,
                    'temperature': 0.7,
                    'capabilities': ['reasoning', 'multilingual', 'agents', 'creative_writing']
                }
            }
        }
        
        models_file = self.config_dir / "models.yaml"
        with open(models_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_models, f, default_flow_style=False)
    
    async def _validate_config(self):
        """Validate configuration settings"""
        try:
            # Validate models
            if not self.models:
                raise ConfigurationError("No models configured")
            
            for model_name, model_config in self.models.items():
                if not model_config.api_key:
                    raise ConfigurationError(f"No API key for model: {model_name}")
                if not model_config.base_url:
                    raise ConfigurationError(f"No base URL for model: {model_name}")
            
            # Validate directories
            for dir_path in [self.sandbox.workspace_dir, self.database.path, 
                           self.memory.chromadb_path, self.logging.log_dir]:
                try:
                    Path(dir_path).parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    raise ConfigurationError(f"Cannot create directory {dir_path}: {e}")
            
            # Validate resource limits
            if self.sandbox.max_file_size_mb <= 0:
                raise ConfigurationError("Invalid sandbox file size limit")
            
            if self.sandbox.max_execution_time <= 0:
                raise ConfigurationError("Invalid sandbox execution time limit")
            
            self.logger.info("Configuration validation successful")
            
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get specific model configuration"""
        return self.models.get(model_name)
    
    def get_enabled_models(self) -> Dict[str, ModelConfig]:
        """Get all enabled models"""
        return {name: config for name, config in self.models.items() if config.enabled}
    
    def get_best_model_for_task(self, task_type: str) -> Optional[ModelConfig]:
        """Get best model for specific task type"""
        task_model_mapping = {
            'coding': ['devstral_small', 'phi_4_reasoning'],
            'reasoning': ['phi_4_reasoning', 'qwen3_30b'],
            'general': ['deepseek_v3', 'llama_3_3_8b'],
            'fast': ['llama_3_3_8b'],
            'agents': ['devstral_small', 'qwen3_30b'],
            'multilingual': ['qwen3_30b', 'deepseek_v3']
        }
        
        preferred_models = task_model_mapping.get(task_type, list(self.models.keys()))
        
        for model_name in preferred_models:
            if model_name in self.models and self.models[model_name].enabled:
                return self.models[model_name]
        
        # Fallback to first enabled model
        enabled_models = self.get_enabled_models()
        return next(iter(enabled_models.values())) if enabled_models else None
    
    async def save_config(self):
        """Save current configuration to files"""
        try:
            # Save main settings
            settings_data = {
                'sandbox': asdict(self.sandbox),
                'database': asdict(self.database),
                'memory': asdict(self.memory),
                'logging': asdict(self.logging),
                'security': asdict(self.security),
                'ui': asdict(self.ui),
                'custom': self.custom_settings
            }
            
            settings_file = self.config_dir / "settings.yaml"
            with open(settings_file, 'w', encoding='utf-8') as f:
                yaml.dump(settings_data, f, default_flow_style=False)
            
            # Save models
            models_data = {
                'models': {name: asdict(config) for name, config in self.models.items()}
            }
            
            models_file = self.config_dir / "models.yaml"
            with open(models_file, 'w', encoding='utf-8') as f:
                yaml.dump(models_data, f, default_flow_style=False)
            
            self.logger.info("Configuration saved successfully")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def update_model_config(self, model_name: str, **kwargs):
        """Update model configuration"""
        if model_name not in self.models:
            raise ConfigurationError(f"Model {model_name} not found")
        
        model_config = self.models[model_name]
        for key, value in kwargs.items():
            if hasattr(model_config, key):
                setattr(model_config, key, value)
            else:
                raise ConfigurationError(f"Invalid model config key: {key}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get custom setting value"""
        return self.custom_settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set custom setting value"""
        self.custom_settings[key] = value
    
    def export_config(self) -> Dict[str, Any]:
        """Export complete configuration as dictionary"""
        return {
            'models': {name: asdict(config) for name, config in self.models.items()},
            'sandbox': asdict(self.sandbox),
            'database': asdict(self.database),
            'memory': asdict(self.memory),
            'logging': asdict(self.logging),
            'security': asdict(self.security),
            'ui': asdict(self.ui),
            'custom': deepcopy(self.custom_settings)
        }
    
    async def check_model_connectivity(self) -> Dict[str, bool]:
        """Check connectivity to all configured models"""
        results = {}
        
        for model_name, model_config in self.models.items():
            if not model_config.enabled:
                results[model_name] = False
                continue
                
            try:
                # Simple connectivity check - could be expanded
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    headers = {'Authorization': f'Bearer {model_config.api_key}'}
                    async with session.get(
                        f"{model_config.base_url}/models", 
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        results[model_name] = response.status == 200
                        
            except Exception as e:
                self.logger.warning(f"Connectivity check failed for {model_name}: {e}")
                results[model_name] = False
        
        return results