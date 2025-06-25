# AI-Assisted UI Automation for HPS Testing

## Project Metadata

**Project Name**: AI-Assisted UI Automation for HPS Testing  
**Version**: 1.0.0  
**Author**: Microsoft AI Testing Team  
**Created**: June 2025  
**Platform**: Windows, Linux  
**Python Version**: 3.8+  

## Quick Links

- [Installation Guide](README.md#installation)
- [Configuration](README.md#configuration)
- [Usage Examples](README.md#basic-usage)
- [Troubleshooting](README.md#troubleshooting)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Testing Agent                         │
├─────────────────────────────────────────────────────────────┤
│  AgentOrchestrator (Main Controller)                        │
│  ├── ScreenCaptureModule (UI Screenshots)                   │
│  ├── AzureAIClient (Computer Vision Analysis)               │
│  ├── ActionExecutor (Keyboard/Mouse Input)                  │
│  ├── TestReporter (Logging & Reports)                       │
│  └── ContextManager (State & History)                       │
├─────────────────────────────────────────────────────────────┤
│                  External Dependencies                       │
│  ├── Azure OpenAI (GPT-4 Vision)                           │
│  ├── HPS Test Application (Target)                          │
│  └── Operating System (Windows/Linux)                       │
└─────────────────────────────────────────────────────────────┘
```

## Key Technologies

- **Azure OpenAI**: GPT-4 Vision for intelligent screen analysis
- **Python asyncio**: Asynchronous programming for responsive operation
- **PyYAML**: Configuration management
- **Pillow**: Image processing and manipulation
- **pynput**: Cross-platform input simulation
- **aiohttp**: Async HTTP client for Azure API communication

## Security Considerations

- All Azure credentials stored in configuration files (not in code)
- Local execution only (no remote control capabilities)
- Comprehensive audit logging of all actions
- Minimal network communication (Azure AI endpoints only)
- User-controlled abort mechanisms

## Performance Characteristics

- **Latency**: 1-3 seconds per AI decision (network dependent)
- **Accuracy**: >95% UI recognition in controlled environments
- **Throughput**: 10-20 actions per minute (depending on application response)
- **Resource Usage**: Low CPU/memory footprint on test machines

## Supported Test Scenarios

1. **Controller Swap Test**: Automated redundant controller failover testing
2. **Status Check**: Systematic verification of system status displays
3. **Startup Test**: Automated application initialization verification
4. **Custom Scenarios**: Extensible framework for additional test types

## Development Status

- ✅ Core architecture implemented
- ✅ Screen capture and AI integration
- ✅ Action execution framework
- ✅ Comprehensive logging and reporting
- ✅ Configuration management
- ⏳ Platform-specific optimizations
- ⏳ Advanced error recovery
- ⏳ Additional test scenarios

## Future Enhancements

- **Advanced Anomaly Detection**: Log analysis and predictive failure detection
- **Multi-Application Support**: Testing across multiple connected applications
- **Distributed Testing**: Coordinated testing across multiple test stations
- **Real-time Monitoring Dashboard**: Live status monitoring for multiple agents
- **Machine Learning Optimization**: Adaptive timing and decision making
