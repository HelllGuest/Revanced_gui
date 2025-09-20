# Changelog

All notable changes to the ReVanced GUI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2024-12-20

### Added
- Comprehensive codebase cleanup and optimization
- Professional project structure with proper packaging
- Development tools and configuration files
- Setup.py for proper package installation
- Makefile for common development tasks
- EditorConfig for consistent code formatting
- MANIFEST.in for package distribution
- Enhanced .gitignore with ReVanced-specific exclusions

### Changed
- Optimized import statements across all modules
- Improved code readability and maintainability
- Streamlined error handling and validation
- Enhanced configuration management
- Better separation of concerns in UI components
- Consolidated duplicate code patterns
- Improved documentation and comments

### Removed
- Obsolete gui_original.py file
- Duplicate Readme.md file (kept README.md)
- Python cache directories (__pycache__)
- Redundant code patterns and unused imports

### Fixed
- Inconsistent file naming conventions
- Import path issues
- Code formatting inconsistencies
- Potential memory leaks in system monitoring
- Window centering calculations in dialogs

### Technical Improvements
- Reduced code complexity and duplication
- Enhanced error handling with specific recovery suggestions
- Improved resource management and cleanup
- Better cross-platform compatibility
- Optimized file I/O operations
- Streamlined UI component creation

### Development Experience
- Added comprehensive development tooling
- Improved project structure for maintainability
- Enhanced debugging and logging capabilities
- Better dependency management
- Standardized code formatting rules

## [1.3.0] - Previous Release

### Added
- Modular architecture with separated concerns
- Core functionality modules (patcher, config, java_manager, system_monitor)
- UI component separation (main_window, dialogs)
- Comprehensive error handling and validation
- System monitoring and resource checking
- Configuration persistence
- Drag and drop file support
- Real-time progress monitoring

### Features
- Cross-platform compatibility (Windows, macOS, Linux)
- Java version detection and validation
- Disk space monitoring
- Configurable logging system
- Help and about dialogs
- Automatic output filename generation
- Session state persistence