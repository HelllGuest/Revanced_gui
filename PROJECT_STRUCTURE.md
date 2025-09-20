# ReVanced GUI - Modular Project Structure

## 🏗️ Architecture Overview

The ReVanced GUI has been successfully refactored from a monolithic `gui.py` file into a clean, modular architecture following Python best practices.

## 📁 Directory Structure

```
revanced-gui/
├── main.py                    # 🚀 Main entry point (replaces gui.py)
├── gui_original.py           # 📦 Original monolithic file (backup)
├── requirements.txt          # 📋 Python dependencies
├── README.md                # 📖 Project documentation
├── LICENSE                  # ⚖️ MIT License
├── PROJECT_STRUCTURE.md     # 📊 This architecture guide
├── config.json              # ⚙️ Configuration file (auto-generated)
├── logs/                    # 📝 Log files (if enabled)
│   └── revanced_gui_*.log
└── src/                     # 📦 Source code package
    ├── __init__.py          # Package initialization
    ├── revanced_gui.py      # 🎯 Main application class
    ├── core/                # 🔧 Core functionality modules
    │   ├── __init__.py
    │   ├── config.py        # Configuration management
    │   ├── java_manager.py  # Java detection & validation
    │   ├── patcher.py       # APK patching operations
    │   └── system_monitor.py # System resource monitoring
    └── ui/                  # 🎨 User interface components
        ├── __init__.py
        ├── dialogs.py       # Help & About dialogs
        └── main_window.py   # Main window interface
```

## 🔧 Core Modules

### ConfigManager (`src/core/config.py`)
- **Purpose**: Configuration loading, saving, and management
- **Features**:
  - JSON-based configuration persistence
  - Atomic file operations for safety
  - Smart path restoration (JAR/RVP remembered, APK-based output)
  - Settings validation and error handling

### JavaManager (`src/core/java_manager.py`)
- **Purpose**: Java installation detection and version validation
- **Features**:
  - Cross-platform Java detection
  - Version parsing (old and new formats)
  - ReVanced CLI compatibility checking
  - Timeout handling for system calls

### SystemMonitor (`src/core/system_monitor.py`)
- **Purpose**: System resource monitoring and validation
- **Features**:
  - Cross-platform disk usage checking
  - Background CPU monitoring
  - Memory usage validation
  - Optional psutil integration

### APKPatcher (`src/core/patcher.py`)
- **Purpose**: APK patching operations and validation
- **Features**:
  - Input validation and error handling
  - Command building and execution
  - Real-time progress monitoring
  - Threaded patching operations

## 🎨 UI Components

### MainWindow (`src/ui/main_window.py`)
- **Purpose**: Main application window and interface
- **Features**:
  - Modular UI component creation
  - Drag & drop integration
  - Progress bar and status management
  - Window resize handling

### Dialogs (`src/ui/dialogs.py`)
- **Purpose**: Help and About dialog windows
- **Features**:
  - Tabbed help interface (Usage, Requirements, Troubleshooting)
  - Application information display
  - Centered modal dialogs
  - Rich text content with formatting

## 🎯 Main Application (`src/revanced_gui.py`)

The main application class that orchestrates all components:
- **Dependency injection**: Manages all core modules
- **Event coordination**: Handles UI events and core operations
- **State management**: Maintains application state and variables
- **Lifecycle management**: Handles startup, operation, and cleanup

## 🚀 Entry Point (`main.py`)

Clean entry point that:
- Sets up Python path for src imports
- Handles drag & drop initialization
- Manages application lifecycle
- Provides error handling and cleanup

## ✨ Benefits of Modular Architecture

### 🔧 Maintainability
- **Single Responsibility**: Each module has one clear purpose
- **Loose Coupling**: Modules interact through well-defined interfaces
- **Easy Updates**: Changes to one module don't affect others
- **Clear Dependencies**: Import structure shows relationships

### 🧪 Testability
- **Unit Testing**: Individual modules can be tested in isolation
- **Mock Integration**: Easy to mock dependencies for testing
- **Focused Testing**: Test specific functionality without UI overhead
- **Regression Prevention**: Modular tests catch breaking changes

### 📈 Scalability
- **Feature Addition**: New features can be added as separate modules
- **Performance Optimization**: Individual modules can be optimized
- **Memory Management**: Modules can be loaded/unloaded as needed
- **Parallel Development**: Multiple developers can work on different modules

### 🔄 Reusability
- **Component Reuse**: Core modules can be used in other projects
- **Interface Consistency**: Standard patterns across modules
- **Plugin Architecture**: Easy to add new functionality
- **Library Extraction**: Modules can become standalone libraries

## 📊 Code Metrics

### Before (Monolithic)
- **Single file**: `gui.py` (~630 lines)
- **Mixed concerns**: UI, logic, configuration all together
- **Hard to test**: Everything coupled together
- **Difficult maintenance**: Changes affect entire file

### After (Modular)
- **Multiple focused files**: 8 modules averaging ~100 lines each
- **Separated concerns**: Clear boundaries between functionality
- **Easy to test**: Individual modules can be tested
- **Simple maintenance**: Changes are localized to specific modules

## 🎯 Usage

### Running the Application
```bash
# Install dependencies (optional but recommended)
pip install -r requirements.txt

# Run the application
python main.py
```

### Development
```bash
# Import specific modules for testing
from src.core.java_manager import JavaManager
from src.core.system_monitor import SystemMonitor

# Test individual components
java_ok, info = JavaManager.check_java_installation()
disk_free, disk_total = SystemMonitor.get_disk_usage()
```

## 🔮 Future Enhancements

The modular architecture enables easy addition of:
- **Plugin system** for custom patches
- **Batch processing** for multiple APKs
- **Update checker** for ReVanced components
- **Theme system** for UI customization
- **Advanced logging** with different levels
- **Configuration profiles** for different setups

## 📝 Migration Notes

- **Original file preserved**: `gui_original.py` contains the original monolithic code
- **Full compatibility**: All original functionality is preserved
- **Same interface**: Users see no difference in functionality
- **Enhanced reliability**: Better error handling and resource management
- **Improved performance**: More efficient resource usage

The modular architecture provides a solid foundation for future development while maintaining all existing functionality and improving code quality significantly.