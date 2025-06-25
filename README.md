# Computer Use Assistant (CUA) for HPS Testing

An AI-powered testing agent that implements the **Azure Computer Use Assistant (CUA)** pattern to automate interaction with Honeywell Process Solutions (HPS) test applications. This solution follows the official Azure CUA sample architecture from: https://github.com/Azure-Samples/computer-use-model

## Overview

This system uses Azure's Computer Use model to observe HPS application UIs through screenshots, understand the current state using AI vision, make intelligent decisions about next actions, and execute keyboard/mouse inputs to drive tests forward automatically.

### Key Features

- **Azure CUA Pattern**: Implements the official Azure Computer Use Assistant architecture
- **Cross-Platform Computer Control**: Works on Windows, Mac, and Linux using pyautogui
- **AI Vision Understanding**: Uses Azure GPT-4 Vision to interpret application screens
- **Intelligent Action Planning**: AI determines appropriate actions based on current state
- **Safety and Consent**: Built-in safety checks and user consent mechanisms
- **Screen Scaling**: Automatic screen scaling for optimal AI processing
- **Comprehensive Logging**: Detailed logs and execution tracking

## Azure CUA Implementation

This solution now fully implements the **Azure Computer Use Assistant (CUA)** pattern as demonstrated in the official Azure sample: https://github.com/Azure-Samples/computer-use-model

### CUA Architecture

```
cua/                           # CUA package (matches Azure sample)
├── __init__.py               # Package exports
├── agent.py                  # Agent class - manages AI conversation loop
├── local_computer.py         # LocalComputer - cross-platform computer control
├── scaler.py                 # Scaler - screen scaling and coordinate translation
├── computer_use_assistant.py # High-level CUA wrapper
├── config.py                 # Configuration management
└── logger.py                 # Logging setup

main.py                       # Enhanced CLI with CUA integration
simple_cua.py                 # Direct Azure CUA sample pattern
```

### Core CUA Components

1. **Agent**: Manages the AI conversation loop, tool calls, and response handling
2. **LocalComputer**: Cross-platform computer control using pyautogui  
3. **Scaler**: Handles screen scaling and coordinate translation for optimal AI vision
4. **Computer Use Assistant**: High-level orchestrator with safety and consent features

## Quick Start

### Prerequisites

- Python 3.8 or later
- Azure OpenAI access with Computer Use model deployment
- Windows, Mac, or Linux environment  
- Required environment variables:
  - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
  - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd computer-use
   ```

2. **Install dependencies** (matches Azure CUA sample):
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   ```bash
   # Windows
   set AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
   set AZURE_OPENAI_API_KEY=your-api-key

   # Linux/Mac
   export AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
   export AZURE_OPENAI_API_KEY=your-api-key
   ```

### Usage Options

#### Option 1: Direct Azure CUA Pattern
Use `simple_cua.py` for the exact Azure CUA sample implementation:

```bash
python simple_cua.py --instructions "Open calculator and compute 2+2" --autoplay
```

#### Option 2: Enhanced CUA with Safety Features
Use `main.py` for the enhanced version with additional safety and configuration:

```bash
python main.py --instructions "Perform controller swap test on HPS application" --autoplay --max-actions 10
```

### Command Line Options

Both scripts support these key options:
- `--instructions`: Natural language instructions for the AI
- `--model`: AI model to use (default: computer-use-preview)
- `--endpoint`: Either 'azure' or 'openai' (default: azure)
- `--autoplay`: Automatically execute actions without confirmation
- `--environment`: Target OS environment (windows/mac/linux)

### Basic Usage

1. **Start the HPS test application** and navigate to the main menu.

2. **Run a simple test**:
   ```bash
   python src/main.py --scenario swap_test --count 5
   ```

3. **Run in dry-run mode** (simulates actions without executing):
   ```bash
   python src/main.py --scenario swap_test --count 3 --dry-run
   ```

4. **Check the results** in the `logs/` directory.

## Configuration

The system uses YAML configuration files located in the `config/` directory.

### Key Configuration Options

```yaml
# Test settings
scenario: swap_test              # Test scenario to run
iteration_count: 10             # Number of test iterations
target_controllers: "17 HPM 18" # Target controller pair
target_network: "UCN 07"        # Target network

# Azure AI settings
azure_endpoint: "https://your-endpoint.openai.azure.com/"
azure_api_key: "your-api-key"
azure_deployment_name: "gpt-4-vision"

# Timing settings
action_delay: 1.0               # Delay after each action (seconds)
swap_completion_timeout: 120.0  # Max time to wait for swap completion

# Behavior
dry_run: false                  # Set to true to simulate without executing
stop_on_error: true            # Stop test on first error
save_screenshots: true         # Save screenshots for debugging
```

## Test Scenarios

### Controller Swap Test

The primary test scenario automates the process of swapping redundant controllers:

1. Navigate to System Status screen
2. Select target network (UCN 07)
3. Initiate controller swap operation
4. Monitor swap progress and completion
5. Verify successful swap
6. Repeat for specified number of iterations

**Usage**:
```bash
python src/main.py --scenario swap_test --count 10
```

### Custom Scenarios

Additional scenarios can be implemented by extending the `AgentOrchestrator` class. The system is designed to be flexible and adaptable to different test procedures.

## Architecture

The system consists of several key modules:

- **AgentOrchestrator**: Main controller that coordinates all operations
- **ScreenCaptureModule**: Captures screenshots of the target application
- **AzureAIClient**: Communicates with Azure OpenAI for intelligent analysis
- **ActionExecutor**: Executes keyboard and mouse actions
- **TestReporter**: Generates comprehensive test reports
- **ContextManager**: Maintains conversation history and context

### Data Flow

1. **Screen Capture** → Take screenshot of HPS application
2. **AI Analysis** → Send image to Azure AI with context
3. **Decision Making** → AI recommends next action
4. **Action Execution** → Execute recommended action
5. **State Monitoring** → Wait for expected changes
6. **Logging** → Record all actions and results
7. **Repeat** → Continue until test completion

## Error Handling

The system includes robust error handling:

- **Vision Errors**: Retry with different prompts or request human intervention
- **Network Issues**: Retry with exponential backoff
- **Application Hangs**: Timeout and attempt recovery
- **Unexpected States**: Log error and optionally attempt recovery

## Logging and Reporting

### Log Files

All operations are logged with timestamps and details:
- `logs/ai_agent_YYYYMMDD_HHMMSS.log` - Detailed execution log
- `logs/test_report.txt` - Human-readable test summary
- `logs/test_report.json` - Machine-readable test data
- `logs/test_results.csv` - Data for analysis

### Screenshots

When enabled, screenshots are saved to `screenshots/` with timestamps for debugging and audit purposes.

## Security Considerations

- **API Keys**: Store Azure credentials securely, never commit to version control
- **Network Access**: System only communicates with Azure OpenAI endpoints
- **Local Execution**: All UI automation happens locally on the test machine
- **Audit Trail**: Complete log of all actions for security review

## Development

### Project Structure

```
src/
├── main.py                 # Entry point
├── core/                   # Core modules
│   ├── agent_orchestrator.py
│   ├── screen_capture.py
│   ├── azure_ai_client.py
│   ├── action_executor.py
│   ├── test_reporter.py
│   ├── context_manager.py
│   ├── config_manager.py
│   └── logger.py
├── utils/                  # Utilities
│   └── exceptions.py
config/                     # Configuration files
logs/                       # Log output directory
screenshots/               # Screenshot directory
tests/                      # Unit tests
```

### Adding New Test Scenarios

1. Extend the `AgentOrchestrator` class with new scenario methods
2. Define scenario-specific prompts and logic
3. Add configuration options for the new scenario
4. Update the command-line interface

### Testing

Run the test suite:
```bash
pytest tests/
```

## Troubleshooting

### Common Issues

**"Could not find window"**:
- Ensure the HPS application is running
- Check the `app_window_title` configuration
- Verify the application window is visible

**"Azure AI connection failed"**:
- Verify Azure credentials in configuration
- Check network connectivity
- Ensure the deployment name is correct

**"Action execution failed"**:
- Check if the application is responsive
- Verify the application has focus
- Try running with `--dry-run` to test logic

**"Test timeout"**:
- Increase timeout values in configuration
- Check if the system is under heavy load
- Verify the application is responding normally

### Debug Mode

Enable detailed logging:
```bash
python src/main.py --log-level DEBUG --scenario swap_test
```

### Dry Run Mode

Test logic without executing actions:
```bash
python src/main.py --dry-run --scenario swap_test
```

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the log files for detailed error information
3. Contact the development team with log files and configuration

## Contributing

1. Follow the existing code style and structure
2. Add unit tests for new functionality
3. Update documentation for any changes
4. Ensure all tests pass before submitting changes

## License

Microsoft Internal Use Only - See license agreement for details.

---

*Built with Azure AI technologies for intelligent test automation.*
