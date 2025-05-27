"""
CLI Handler for AI Assistant
"""

import argparse
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging

from core.config import ConfigManager
from core.exceptions import AIAssistantError, ConfigurationError
from ui.formatter import ColorFormatter
from ui.progress_display import ProgressDisplay
from utils.file_utils import FileValidator

class CLIHandler:
    """Command-line interface handler"""
    
    def __init__(self, assistant=None, config_manager: ConfigManager = None, logger=None):
        self.assistant = assistant
        self.config_manager = config_manager
        self.logger = logger or logging.getLogger(__name__)
        self.formatter = ColorFormatter()
        self.progress = ProgressDisplay()
        self.file_validator = FileValidator()
        self.parser = None
        self._setup_parser()
    
    def _setup_parser(self):
        """Setup argument parser with all commands and options"""
        try:
            self.parser = argparse.ArgumentParser(
                prog='ai-assistant',
                description='🤖 AI Assistant CLI - Intelligent task automation and code generation',
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog="""
Examples:
  # Interactive mode
  ai-assistant

  # Process files with prompt
  ai-assistant -f project.zip -p "Analyze this code and suggest improvements"
  
  # Batch processing with specific model
  ai-assistant -f *.py -p "Add docstrings" -m phi_4_reasoning -o ./output
  
  # Configuration check
  ai-assistant --config-check
  
  # List available models
  ai-assistant --list-models
                """
            )
            
            # Input options
            input_group = self.parser.add_argument_group('Input Options')
            input_group.add_argument(
                '-f', '--files', '--input-files',
                nargs='+',
                dest='input_files',
                help='Input files (zip, text, code files)',
                metavar='FILE'
            )
            input_group.add_argument(
                '-p', '--prompt',
                type=str,
                help='Task prompt or instruction',
                metavar='TEXT'
            )
            input_group.add_argument(
                '--stdin',
                action='store_true',
                help='Read prompt from stdin'
            )
            
            # Model options
            model_group = self.parser.add_argument_group('Model Options')
            model_group.add_argument(
                '-m', '--model',
                type=str,
                default='auto',
                help='Model to use (auto, devstral_small, llama_3_3_8b, phi_4_reasoning, deepseek_v3, qwen3_30b)',
                metavar='MODEL'
            )
            model_group.add_argument(
                '--temperature',
                type=float,
                help='Model temperature (0.0-2.0)',
                metavar='FLOAT'
            )
            model_group.add_argument(
                '--max-tokens',
                type=int,
                help='Maximum tokens to generate',
                metavar='INT'
            )
            
            # Output options
            output_group = self.parser.add_argument_group('Output Options')
            output_group.add_argument(
                '-o', '--output',
                type=str,
                default='./output',
                help='Output directory',
                metavar='DIR'
            )
            output_group.add_argument(
                '--format',
                choices=['text', 'json', 'markdown'],
                default='text',
                help='Output format'
            )
            output_group.add_argument(
                '--save-session',
                action='store_true',
                help='Save session for later resume'
            )
            
            # Task options
            task_group = self.parser.add_argument_group('Task Options')
            task_group.add_argument(
                '--task-type',
                choices=['coding', 'analysis', 'review', 'generation', 'research', 'auto'],
                default='auto',
                help='Task type for optimal model selection'
            )
            task_group.add_argument(
                '--parallel',
                action='store_true',
                help='Enable parallel task execution'
            )
            task_group.add_argument(
                '--memory',
                action='store_true',
                help='Enable memory and context retention'
            )
            task_group.add_argument(
                '--search',
                action='store_true',
                help='Enable semantic search in input files'
            )
            
            # Sandbox options
            sandbox_group = self.parser.add_argument_group('Sandbox Options')
            sandbox_group.add_argument(
                '--sandbox',
                action='store_true',
                default=True,
                help='Enable sandbox execution (default: True)'
            )
            sandbox_group.add_argument(
                '--no-sandbox',
                action='store_false',
                dest='sandbox',
                help='Disable sandbox execution (dangerous)'
            )
            sandbox_group.add_argument(
                '--timeout',
                type=int,
                help='Task timeout in seconds',
                metavar='SECONDS'
            )
            
            # Code quality options
            quality_group = self.parser.add_argument_group('Code Quality Options')
            quality_group.add_argument(
                '--lint',
                action='store_true',
                help='Enable code linting'
            )
            quality_group.add_argument(
                '--format-code',
                action='store_true',
                help='Auto-format generated code'
            )
            quality_group.add_argument(
                '--test',
                action='store_true',
                help='Generate and run tests'
            )
            
            # Browser options
            browser_group = self.parser.add_argument_group('Browser Options')
            browser_group.add_argument(
                '--browser',
                action='store_true',
                help='Enable browser automation for research'
            )
            browser_group.add_argument(
                '--headless',
                action='store_true',
                default=True,
                help='Run browser in headless mode'
            )
            
            # Interactive mode
            interactive_group = self.parser.add_argument_group('Interactive Mode')
            interactive_group.add_argument(
                '-i', '--interactive',
                action='store_true',
                help='Start in interactive mode'
            )
            interactive_group.add_argument(
                '--no-color',
                action='store_true',
                help='Disable colored output'
            )
            interactive_group.add_argument(
                '--quiet',
                action='store_true',
                help='Quiet mode - minimal output'
            )
            
            # Configuration and info
            config_group = self.parser.add_argument_group('Configuration')
            config_group.add_argument(
                '--config-check',
                action='store_true',
                help='Check configuration and model connectivity'
            )
            config_group.add_argument(
                '--list-models',
                action='store_true',
                help='List available models and their capabilities'
            )
            config_group.add_argument(
                '--config-file',
                type=str,
                help='Custom configuration file path',
                metavar='FILE'
            )
            config_group.add_argument(
                '--reset-config',
                action='store_true',
                help='Reset configuration to defaults'
            )
            
            # Debugging and logging
            debug_group = self.parser.add_argument_group('Debugging')
            debug_group.add_argument(
                '--debug',
                action='store_true',
                help='Enable debug logging'
            )
            debug_group.add_argument(
                '--log-file',
                type=str,
                help='Custom log file path',
                metavar='FILE'
            )
            debug_group.add_argument(
                '--dry-run',
                action='store_true',
                help='Show what would be done without executing'
            )
            
            # Version and help
            self.parser.add_argument(
                '--version',
                action='version',
                version='AI Assistant CLI v1.0.0'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to setup argument parser: {e}")
            raise AIAssistantError(f"CLI setup failed: {e}")
    
    def parse_arguments(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Parse command line arguments"""
        try:
            if args is None:
                args = sys.argv[1:]
            
            # Handle special cases
            if not args:
                return {'interactive': True}
            
            parsed_args = self.parser.parse_args(args)
            
            # Convert to dictionary
            args_dict = vars(parsed_args)
            
            # Handle stdin input
            if args_dict.get('stdin'):
                try:
                    stdin_content = sys.stdin.read().strip()
                    if stdin_content:
                        args_dict['prompt'] = stdin_content
                except Exception as e:
                    self.logger.warning(f"Could not read from stdin: {e}")
            
            # Validate arguments
            self._validate_arguments(args_dict)
            
            # Process file paths
            if args_dict.get('input_files'):
                args_dict['input_files'] = self._process_file_paths(args_dict['input_files'])
            
            return args_dict
            
        except SystemExit as e:
            # Handle --help and --version
            if e.code == 0:
                sys.exit(0)
            else:
                raise AIAssistantError("Invalid command line arguments")
                
        except Exception as e:
            self.logger.error(f"Argument parsing failed: {e}")
            raise AIAssistantError(f"Failed to parse arguments: {e}")
    
    def _validate_arguments(self, args: Dict[str, Any]):
        """Validate parsed arguments"""
        try:
            # Check for conflicting options
            if args.get('interactive') and (args.get('input_files') or args.get('prompt')):
                raise AIAssistantError("Interactive mode cannot be used with input files or prompts")
            
            # Validate model name
            if args.get('model') and args['model'] != 'auto':
                if self.config_manager:
                    available_models = list(self.config_manager.models.keys())
                    if args['model'] not in available_models:
                        raise AIAssistantError(f"Invalid model: {args['model']}. Available: {available_models}")
            
            # Validate temperature
            if args.get('temperature') is not None:
                temp = args['temperature']
                if not (0.0 <= temp <= 2.0):
                    raise AIAssistantError("Temperature must be between 0.0 and 2.0")
            
            # Validate max_tokens
            if args.get('max_tokens') is not None:
                max_tokens = args['max_tokens']
                if max_tokens <= 0:
                    raise AIAssistantError("Max tokens must be positive")
            
            # Validate timeout
            if args.get('timeout') is not None:
                timeout = args['timeout']
                if timeout <= 0:
                    raise AIAssistantError("Timeout must be positive")
            
            # Check output directory
            if args.get('output'):
                output_path = Path(args['output'])
                try:
                    output_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    raise AIAssistantError(f"Cannot create output directory: {e}")
            
        except Exception as e:
            raise AIAssistantError(f"Argument validation failed: {e}")
    
    def _process_file_paths(self, file_paths: List[str]) -> List[str]:
        """Process and validate file paths with glob support"""
        processed_files = []
        
        try:
            for file_path in file_paths:
                path = Path(file_path)
                
                # Handle glob patterns
                if '*' in file_path or '?' in file_path:
                    matches = list(Path('.').glob(file_path))
                    for match in matches:
                        if match.is_file():
                            if self.file_validator.validate_file(match):
                                processed_files.append(str(match.absolute()))
                            else:
                                self.logger.warning(f"File validation failed: {match}")
                else:
                    # Regular file path
                    if path.exists() and path.is_file():
                        if self.file_validator.validate_file(path):
                            processed_files.append(str(path.absolute()))
                        else:
                            self.logger.warning(f"File validation failed: {path}")
                    else:
                        self.logger.warning(f"File not found: {path}")
            
            if not processed_files and file_paths:
                raise AIAssistantError("No valid input files found")
            
            return processed_files
            
        except Exception as e:
            raise AIAssistantError(f"File processing failed: {e}")
    
    async def show_help(self):
        """Show interactive help"""
        try:
            help_text = """
🤖 AI Assistant CLI - Interactive Commands

📝 Basic Commands:
  help, ?           - Show this help message
  exit, quit, q     - Exit the application
  clear             - Clear screen
  status            - Show current status

🔧 Configuration Commands:
  config            - Show current configuration  
  models            - List available models
  set model <name>  - Switch to different model
  set temp <value>  - Set temperature (0.0-2.0)
  
📁 File Commands:
  load <file>       - Load file for processing
  files             - List loaded files
  clear files       - Clear loaded files
  
🎯 Task Commands:
  task <prompt>     - Execute task with prompt  
  batch <dir>       - Process directory in batch
  search <query>    - Semantic search in loaded files
  
🔍 Memory Commands:
  memory            - Show current memory/context
  summarize         - Summarize current session
  save session      - Save current session
  load session      - Load previous session
  
⚙️ Sandbox Commands:
  sandbox status    - Check sandbox status
  sandbox reset     - Reset sandbox environment
  sandbox ls        - List sandbox contents
  
🌐 Browser Commands:
  browser open <url> - Open URL in browser
  browser search <q> - Search the web
  browser close      - Close browser
  
📊 Statistics:
  stats             - Show usage statistics
  feedback <rating> - Provide feedback (1-5)
  
Examples:
  task "Analyze this code and suggest improvements"
  load project.zip
  search "authentication logic"
  set model phi_4_reasoning
            """
            
            print(self.formatter.format_info(help_text))
            
        except Exception as e:
            self.logger.error(f"Failed to show help: {e}")
    
    async def check_configuration(self) -> bool:
        """Check configuration and connectivity"""
        try:
            if not self.config_manager:
                print(self.formatter.format_error("❌ Configuration manager not available"))
                return False
            
            print(self.formatter.format_header("🔧 Configuration Check"))
            
            # Check basic configuration
            print(self.formatter.format_info("📋 Basic Configuration:"))
            print(f"  Models configured: {len(self.config_manager.models)}")
            print(f"  Sandbox enabled: {self.config_manager.sandbox}")
            print(f"  Memory enabled: {self.config_manager.memory}")
            print(f"  Security enabled: {self.config_manager.security}")
            
            # Check model connectivity
            print(self.formatter.format_info("\n🌐 Model Connectivity:"))
            connectivity_results = await self.config_manager.check_model_connectivity()
            
            all_connected = True
            for model_name, connected in connectivity_results.items():
                status = "✅ Connected" if connected else "❌ Failed"
                print(f"  {model_name}: {status}")
                if not connected:
                    all_connected = False
            
            # Check directories
            print(self.formatter.format_info("\n📁 Directory Check:"))
            directories = [
                ("Sandbox", self.config_manager.sandbox.workspace_dir),
                ("Database", Path(self.config_manager.database.path).parent),
                ("Memory", self.config_manager.memory.chromadb_path),
                ("Logs", self.config_manager.logging.log_dir)
            ]
            
            for name, path in directories:
                path_obj = Path(path)
                if path_obj.exists():
                    print(f"  {name}: ✅ {path}")
                else:
                    try:
                        path_obj.mkdir(parents=True, exist_ok=True)
                        print(f"  {name}: ✅ Created {path}")
                    except Exception as e:
                        print(f"  {name}: ❌ Failed to create {path} - {e}")
                        all_connected = False
            
            # Overall status
            if all_connected:
                print(self.formatter.format_success("\n✅ Configuration check passed"))
            else:
                print(self.formatter.format_error("\n❌ Configuration check failed"))
                
            return all_connected
            
        except Exception as e:
            self.logger.error(f"Configuration check failed: {e}")
            print(self.formatter.format_error(f"❌ Configuration check error: {e}"))
            return False
    
    async def list_models(self):
        """List available models and their capabilities"""
        try:
            if not self.config_manager:
                print(self.formatter.format_error("❌ Configuration manager not available"))
                return
            
            print(self.formatter.format_header("🤖 Available Models"))
            
            for model_name, model_config in self.config_manager.models.items():
                status = "✅ Enabled" if model_config.enabled else "❌ Disabled"
                print(f"\n📍 {model_name}")
                print(f"  Status: {status}")
                print(f"  Model: {model_config.model}")
                print(f"  Max Tokens: {model_config.max_tokens:,}")
                print(f"  Temperature: {model_config.temperature}")
                print(f"  Capabilities: {', '.join(model_config.capabilities)}")
                print(f"  Details: {model_config.details[:100]}...")
            
            # Show recommended usage
            print(self.formatter.format_info("\n💡 Recommended Usage:"))
            recommendations = [
                ("Coding Tasks", "devstral_small, phi_4_reasoning"),
                ("Math/Reasoning", "phi_4_reasoning, qwen3_30b"),
                ("General Chat", "deepseek_v3, llama_3_3_8b"),
                ("Fast Response", "llama_3_3_8b"),
                ("Agent Tasks", "devstral_small, qwen3_30b"),
                ("Multilingual", "qwen3_30b, deepseek_v3")
            ]
            
            for task_type, models in recommendations:
                print(f"  {task_type}: {models}")
                
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            print(self.formatter.format_error(f"❌ Error listing models: {e}"))
    
    async def handle_interactive_command(self, command: str) -> Dict[str, Any]:
        """Handle interactive mode commands"""
        try:
            parts = command.strip().split()
            if not parts:
                return {'success': False, 'error': 'Empty command'}
            
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Basic commands
            if cmd in ['help', '?']:
                await self.show_help()
                return {'success': True}
            
            elif cmd == 'clear':
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                return {'success': True}
            
            elif cmd == 'config':
                await self.check_configuration()
                return {'success': True}
            
            elif cmd == 'models':
                await self.list_models()
                return {'success': True}
            
            elif cmd == 'status':
                if self.assistant:
                    status = await self.assistant.get_status()
                    print(json.dumps(status, indent=2))
                return {'success': True}
            
            # Configuration commands
            elif cmd == 'set' and len(args) >= 2:
                setting = args[0].lower()
                value = ' '.join(args[1:])
                
                if setting == 'model':
                    if self.config_manager and value in self.config_manager.models:
                        # This would be handled by the assistant
                        return {'success': True, 'action': 'set_model', 'value': value}
                    else:
                        return {'success': False, 'error': f'Invalid model: {value}'}
                
                elif setting in ['temperature', 'temp']:
                    try:
                        temp_value = float(value)
                        if 0.0 <= temp_value <= 2.0:
                            return {'success': True, 'action': 'set_temperature', 'value': temp_value}
                        else:
                            return {'success': False, 'error': 'Temperature must be between 0.0 and 2.0'}
                    except ValueError:
                        return {'success': False, 'error': 'Invalid temperature value'}
            
            # File commands
            elif cmd == 'load' and args:
                file_path = ' '.join(args)
                if Path(file_path).exists():
                    return {'success': True, 'action': 'load_file', 'value': file_path}
                else:
                    return {'success': False, 'error': f'File not found: {file_path}'}
            
            elif cmd == 'files':
                return {'success': True, 'action': 'list_files'}
            
            # Task commands
            elif cmd == 'task' and args:
                task_prompt = ' '.join(args)
                return {'success': True, 'action': 'execute_task', 'value': task_prompt}
            
            elif cmd == 'search' and args:
                search_query = ' '.join(args)
                return {'success': True, 'action': 'semantic_search', 'value': search_query}
            
            # Unknown command
            else:
                return {'success': False, 'error': f'Unknown command: {cmd}. Type "help" for available commands.'}
            
        except Exception as e:
            self.logger.error(f"Interactive command handling failed: {e}")
            return {'success': False, 'error': f'Command error: {e}'}
    
    def get_parser(self) -> argparse.ArgumentParser:
        """Get the argument parser"""
        return self.parser