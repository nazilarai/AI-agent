#!/usr/bin/env python3
"""
AI Assistant CLI Tool - Main Entry Point
"""

import sys
import os
import asyncio
import signal
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from core.cli import CLIHandler
    from core.assistant import AIAssistant
    from core.config import ConfigManager
    from core.exceptions import (
        AIAssistantError, 
        ConfigurationError, 
        ModelError,
        TaskPlanningError,
        SandboxError
    )
    from ui.logger import setup_logger
    from ui.formatter import ColorFormatter
    from database.database import DatabaseManager
    from utils.system_utils import SystemChecker
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

class AIAssistantMain:
    """Main application class for AI Assistant CLI"""
    
    def __init__(self):
        self.config_manager: Optional[ConfigManager] = None
        self.assistant: Optional[AIAssistant] = None
        self.cli_handler: Optional[CLIHandler] = None
        self.db_manager: Optional[DatabaseManager] = None
        self.logger = None
        self.shutdown_requested = False
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_requested = True
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def initialize(self) -> bool:
        """Initialize all components with error handling"""
        try:
            # Setup logging first
            self.logger = setup_logger("ai_assistant", PROJECT_ROOT / "data" / "logs")
            self.logger.info("🚀 Initializing AI Assistant CLI...")
            
            # Check system requirements
            system_checker = SystemChecker()
            if not system_checker.check_system_compatibility():
                self.logger.error("❌ System compatibility check failed")
                return False
                
            # Initialize configuration
            self.config_manager = ConfigManager(PROJECT_ROOT / "config")
            await self.config_manager.load_config()
            self.logger.info("✅ Configuration loaded successfully")
            
            # Initialize database
            self.db_manager = DatabaseManager(PROJECT_ROOT / "data" / "database.sqlite")
            await self.db_manager.initialize()
            self.logger.info("✅ Database initialized successfully")
            
            # Initialize core assistant
            self.assistant = AIAssistant(
                config_manager=self.config_manager,
                db_manager=self.db_manager,
                logger=self.logger
            )
            await self.assistant.initialize()
            self.logger.info("✅ AI Assistant core initialized successfully")
            
            # Initialize CLI handler
            self.cli_handler = CLIHandler(
                assistant=self.assistant,
                config_manager=self.config_manager,
                logger=self.logger
            )
            self.logger.info("✅ CLI Handler initialized successfully")
            
            return True
            
        except ConfigurationError as e:
            self.logger.error(f"❌ Configuration Error: {e}")
            print(f"Configuration Error: {e}")
            return False
            
        except ModelError as e:
            self.logger.error(f"❌ Model Error: {e}")
            print(f"Model Error: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Initialization Error: {e}")
            self.logger.error(traceback.format_exc())
            print(f"Initialization Error: {e}")
            return False
    
    async def run_interactive_mode(self):
        """Run assistant in interactive mode"""
        try:
            self.logger.info("🎯 Starting interactive mode...")
            formatter = ColorFormatter()
            
            print(formatter.format_header("🤖 AI Assistant CLI - Interactive Mode"))
            print(formatter.format_info("Type 'help' for commands, 'exit' to quit"))
            print("-" * 60)
            
            while not self.shutdown_requested:
                try:
                    user_input = input("\n💬 Enter your request: ").strip()
                    
                    if not user_input:
                        continue
                        
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        break
                        
                    if user_input.lower() in ['help', '?']:
                        await self.cli_handler.show_help()
                        continue
                    
                    # Process user request
                    result = await self.assistant.process_request(user_input)
                    
                    if result.get('success'):
                        print(formatter.format_success("✅ Task completed successfully"))
                        if result.get('output'):
                            print(formatter.format_output(result['output']))
                    else:
                        print(formatter.format_error(f"❌ Task failed: {result.get('error', 'Unknown error')}"))
                        
                except KeyboardInterrupt:
                    print("\n\nShutdown requested by user...")
                    break
                    
                except Exception as e:
                    self.logger.error(f"Error in interactive mode: {e}")
                    print(formatter.format_error(f"❌ Error: {e}"))
                    
        except Exception as e:
            self.logger.error(f"❌ Interactive mode error: {e}")
            raise
    
    async def run_batch_mode(self, args: Dict[str, Any]):
        """Run assistant in batch mode with provided arguments"""
        try:
            self.logger.info("📋 Starting batch mode...")
            
            # Extract arguments
            input_files = args.get('input_files', [])
            prompt = args.get('prompt', '')
            output_dir = args.get('output_dir', './output')
            model = args.get('model', 'auto')
            
            if not prompt and not input_files:
                raise AIAssistantError("Either prompt or input files must be provided")
            
            # Process batch request
            result = await self.assistant.process_batch_request(
                input_files=input_files,
                prompt=prompt,
                output_dir=output_dir,
                model=model
            )
            
            if result.get('success'):
                self.logger.info("✅ Batch processing completed successfully")
                print("✅ Batch processing completed successfully")
                if result.get('output_path'):
                    print(f"📁 Output saved to: {result['output_path']}")
            else:
                self.logger.error(f"❌ Batch processing failed: {result.get('error')}")
                print(f"❌ Batch processing failed: {result.get('error')}")
                return 1
                
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Batch mode error: {e}")
            print(f"❌ Batch mode error: {e}")
            return 1
    
    async def cleanup(self):
        """Cleanup resources gracefully"""
        try:
            self.logger.info("🧹 Starting cleanup...")
            
            if self.assistant:
                await self.assistant.cleanup()
                
            if self.db_manager:
                await self.db_manager.close()
                
            self.logger.info("✅ Cleanup completed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")

async def main():
    """Main entry point"""
    app = None
    exit_code = 0
    
    try:
        # Create main application instance
        app = AIAssistantMain()
        
        # Setup signal handlers for graceful shutdown
        app.setup_signal_handlers()
        
        # Initialize application
        if not await app.initialize():
            print("❌ Failed to initialize AI Assistant")
            return 1
        
        # Parse command line arguments
        args = app.cli_handler.parse_arguments()
        
        # Determine execution mode
        if args.get('interactive', False) or not any([
            args.get('prompt'),
            args.get('input_files'),
            args.get('config_check')
        ]):
            # Interactive mode
            await app.run_interactive_mode()
        elif args.get('config_check'):
            # Configuration check mode
            success = await app.cli_handler.check_configuration()
            exit_code = 0 if success else 1
        else:
            # Batch mode
            exit_code = await app.run_batch_mode(args)
            
    except AIAssistantError as e:
        print(f"❌ AI Assistant Error: {e}")
        exit_code = 1
        
    except TaskPlanningError as e:
        print(f"❌ Task Planning Error: {e}")
        exit_code = 1
        
    except SandboxError as e:
        print(f"❌ Sandbox Error: {e}")
        exit_code = 1
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        exit_code = 0
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        if app and app.logger:
            app.logger.error(f"Unexpected error: {e}")
            app.logger.error(traceback.format_exc())
        exit_code = 1
        
    finally:
        # Cleanup resources
        if app:
            await app.cleanup()
    
    return exit_code

def run():
    """Synchronous entry point for setup.py"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            sys.exit(1)
            
        # Create data directories if they don't exist
        data_dirs = [
            PROJECT_ROOT / "data" / "logs",
            PROJECT_ROOT / "data" / "cache",
            PROJECT_ROOT / "data" / "embeddings",
            PROJECT_ROOT / "sandbox_workspaces"
        ]
        
        for dir_path in data_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Run main async function
        if sys.platform == "win32":
            # Windows specific event loop policy
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()
