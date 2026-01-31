# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-01

### Added
- Initial release of oc-collab (opencode-collaboration)
- Dual-agent collaboration framework
- Agent workflow management (requirements → design → development → testing → deployment)
- Agent daemon functionality with background mode and process supervision
- Git-based state management and communication between agents
- CLI commands for project management and agent control

### Features
- `oc-collab agent` - Agent daemon command with daemonization support
- `oc-collab project status` - Check current project phase and status
- `oc-collab advance` - Advance project to next phase
- `oc-collab signoff` - Sign off on phase completions
- Process supervision with auto-restart (max 5 restarts/hour)
- Configurable git timeout control

### Components
- `AgentDaemon` - Core daemon class for agent lifecycle management
- `ProcessSupervisor` - Process supervision with exponential backoff
- `GitMonitor` - Git timeout and status monitoring

### Documentation
- Requirements specifications for agent daemon
- Detailed design documentation
- Development task assignments
- Blackbox test results

### Tests
- Unit tests for daemon functionality (24 tests passing)
- Blackbox testing for all CLI commands

## [Unreleased]
- Additional agent features
- Enhanced collaboration workflows
