# AI Assistant CLI Tool - Project Structure

```
ai_assistant_cli/
│
├── 📁 core/
│   ├── __init__.py
│   ├── config.py                    # Configuration management & model settings
│   ├── cli.py                      # Main CLI interface and argument parsing
│   ├── assistant.py                # Core assistant orchestrator
│   └── exceptions.py               # Custom exception classes
│
├── 📁 models/
│   ├── __init__.py
│   ├── model_manager.py            # LLM model selection and switching
│   ├── openrouter_client.py        # OpenRouter API client
│   └── response_parser.py          # Parse LLM responses and extract JSON
│
├── 📁 task_planning/
│   ├── __init__.py
│   ├── planner.py                  # High-level task decomposition
│   ├── task_queue.py               # Task queue management
│   ├── executor.py                 # Task execution engine
│   └── tracker.py                  # Live task status tracking
│
├── 📁 tools/
│   ├── __init__.py
│   ├── base_tool.py                # Abstract base class for tools
│   ├── file_operations.py          # File creation, reading, writing
│   ├── code_quality.py             # Linting tools (pylint, black, eslint)
│   ├── terminal_executor.py        # Safe terminal command execution
│   ├── browser_controller.py       # Firefox automation
│   └── tool_registry.py            # Tool registration and discovery
│
├── 📁 sandbox/
│   ├── __init__.py
│   ├── sandbox_manager.py          # Isolated environment management
│   ├── security.py                 # Security policies and validation
│   └── resource_monitor.py         # Resource usage monitoring
│
├── 📁 memory/
│   ├── __init__.py
│   ├── memory_manager.py           # Task memory and context management
│   ├── summarizer.py               # Memory summarization
│   ├── embeddings.py               # Text embeddings for ChromaDB
│   └── chromadb_client.py          # ChromaDB integration
│
├── 📁 search/
│   ├── __init__.py
│   ├── semantic_search.py          # Semantic search in project files
│   ├── indexer.py                  # File indexing and preprocessing
│   └── retriever.py                # Document retrieval and ranking
│
├── 📁 input_processing/
│   ├── __init__.py
│   ├── file_processor.py           # Handle zip, text, code files
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── zip_parser.py           # Extract and process zip files
│   │   ├── text_parser.py          # Process text files
│   │   └── code_parser.py          # Parse code files with AST
│   └── validators.py               # Input validation
│
├── 📁 database/
│   ├── __init__.py
│   ├── models.py                   # SQLAlchemy models
│   ├── database.py                 # Database connection and operations
│   ├── usage_tracker.py            # Track model usage and stats
│   └── feedback_manager.py         # Handle user feedback and RL data
│
├── 📁 ui/
│   ├── __init__.py
│   ├── interactive_mode.py         # Interactive CLI interface
│   ├── progress_display.py         # Task progress visualization
│   ├── logger.py                   # Structured logging
│   └── formatter.py                # Output formatting and colors
│
├── 📁 learning/
│   ├── __init__.py
│   ├── feedback_processor.py       # Process manual and LLM feedback
│   ├── reinforcement_learning.py   # RL algorithm implementation
│   └── model_optimizer.py          # Model selection optimization
│
├── 📁 utils/
│   ├── __init__.py
│   ├── file_utils.py               # File system utilities
│   ├── json_utils.py               # JSON parsing and validation
│   ├── crypto_utils.py             # Security and hashing utilities
│   └── system_utils.py             # System information and compatibility
│
├── 📁 config/
│   ├── settings.yaml               # Default configuration
│   ├── models.yaml                 # Model configurations
│   ├── tools.yaml                  # Tool configurations
│   └── security_policies.yaml     # Security and sandbox policies
│
├── 📁 templates/
│   ├── task_templates/             # Predefined task templates
│   │   ├── code_generation.yaml
│   │   ├── data_analysis.yaml
│   │   └── web_scraping.yaml
│   └── prompt_templates/           # LLM prompt templates
│       ├── task_planning.txt
│       ├── code_review.txt
│       └── tool_calling.txt
│
├── 📁 sandbox_workspaces/          # Isolated task workspaces
│   └── .gitkeep
│
├── 📁 data/
│   ├── embeddings/                 # ChromaDB storage
│   ├── logs/                       # Application logs
│   ├── cache/                      # Temporary cache files
│   └── database.sqlite             # SQLite database
│
├── 📁 tests/
│   ├── __init__.py
│   ├── test_core/
│   ├── test_tools/
│   ├── test_task_planning/
│   ├── test_memory/
│   ├── test_search/
│   ├── test_sandbox/
│   └── test_integration/
│
├── 📁 scripts/
│   ├── setup.py                    # Initial setup script
│   ├── install_dependencies.py    # Dependency installation
│   └── cleanup.py                  # Cleanup temporary files
│
├── 📁 docs/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── USAGE_EXAMPLES.md
│   └── SECURITY.md
│
├── requirements.txt                # Python dependencies
├── requirements-dev.txt            # Development dependencies
├── pyproject.toml                  # Project metadata and build config
├── setup.py                        # Package installation
├── .env.example                    # Environment variables template
├── .gitignore
└── main.py                         # Entry point
```

## 🏗️ Core Architecture Components

### 1. **Core Module**
- **cli.py**: Main CLI interface using `argparse` or `click`
- **assistant.py**: Central orchestrator that coordinates all components
- **config.py**: Configuration management with support for multiple LLM models

### 2. **Model Management**
- **model_manager.py**: Handles switching between the 5 LLM models
- **openrouter_client.py**: API client for OpenRouter integration
- **response_parser.py**: Extracts JSON tool calls from LLM responses

### 3. **Task Planning Engine**
- **planner.py**: Breaks down high-level prompts into executable sub-tasks
- **task_queue.py**: Manages task prioritization and scheduling
- **executor.py**: Executes tasks with proper error handling
- **tracker.py**: Real-time task status monitoring

### 4. **Tool System**
- **base_tool.py**: Abstract base class for all tools
- **file_operations.py**: File CRUD operations
- **code_quality.py**: Integration with pylint, black, eslint
- **terminal_executor.py**: Secure command execution in sandbox
- **browser_controller.py**: Firefox automation using Selenium

### 5. **Sandbox Environment**
- **sandbox_manager.py**: Creates isolated workspaces for each task
- **security.py**: Enforces security policies and command validation
- **resource_monitor.py**: Monitor CPU/memory usage

### 6. **Memory & Knowledge**
- **memory_manager.py**: Per-task memory management
- **chromadb_client.py**: Vector database for semantic search
- **embeddings.py**: Text embedding generation

### 7. **Input Processing**
- **file_processor.py**: Main file processing coordinator
- **zip_parser.py**: Extract and analyze zip files
- **code_parser.py**: AST-based code analysis

### 8. **Database Layer**
- **models.py**: SQLAlchemy models for usage tracking
- **usage_tracker.py**: Track model performance and costs
- **feedback_manager.py**: Store and process user feedback

### 9. **Learning System**
- **reinforcement_learning.py**: RL for model selection optimization
- **feedback_processor.py**: Process manual and automated feedback

## 🔧 Key Features Implementation

### **JSON Tool Calling Format**
```json
{
  "tool": "create_file",
  "parameters": {
    "path": "example.py",
    "content": "print('Hello World')"
  }
}
```

### **Terminal Command Execution**
```json
{
  "tool": "run_command",
  "parameters": {
    "command": "python -m pytest tests/",
    "working_directory": "./sandbox_workspace_123",
    "timeout": 30
  }
}
```

### **Task Progress Tracking**
- Real-time status updates in CLI
- Structured logging with timestamps
- Progress bars for long-running tasks

### **Security Features**
- Sandboxed execution environment
- Command whitelist/blacklist
- Resource usage limits
- File access restrictions

This architecture provides a solid foundation for building your AI assistant CLI tool with all the required features while maintaining modularity and security.
