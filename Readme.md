# ReVanced GUI

A comprehensive, user-friendly GUI wrapper for the ReVanced CLI tool that provides an easy-to-use interface for patching APK files with ReVanced patches.

![Version](https://img.shields.io/badge/version-1.3.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Features

- **Cross-platform compatibility** - Works on Windows, macOS, and Linux
- **Drag & drop support** - Simply drag files into the interface
- **Real-time progress monitoring** - Watch the patching process live
- **System validation** - Automatic Java and system requirements checking
- **Configuration persistence** - Remembers your settings between sessions
- **Resource monitoring** - Disk space and system resource checking
- **Professional UI** - Clean, intuitive interface with help dialogs
- **Comprehensive logging** - Detailed logs with export functionality
- **Error handling** - Specific error messages with recovery suggestions

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (with tkinter support)
- **Java 8+** (Java 11+ recommended)
- **ReVanced CLI JAR** file
- **ReVanced Patches RVP** file

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/revanced/revanced-gui.git
   cd revanced-gui
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using the Makefile:
   ```bash
   make install
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```
   
   Or using the Makefile:
   ```bash
   make run
   ```

### Optional Dependencies

For enhanced functionality, install these optional packages:

- **psutil** - System monitoring and resource usage
- **tkinterdnd2** - Drag-and-drop file support

```bash
pip install psutil tkinterdnd2
```

## 📖 Usage

1. **Select ReVanced CLI JAR** - Browse or drag the CLI JAR file
2. **Select Patches RVP** - Browse or drag the patches file
3. **Choose APK file** - Select the APK you want to patch
4. **Set output location** - Automatically set to APK's directory
5. **Click "Patch APK"** - Start the patching process
6. **Monitor progress** - Watch real-time output in the log area

### Interface Overview

- **Status Bar** - Shows system status, Java version, and quick actions
- **File Inputs** - Browse or drag-and-drop required files
- **Progress Section** - Real-time progress bar and status updates
- **Log Area** - Detailed output with export functionality
- **Settings** - Toggle logging and configuration persistence

## 🏗️ Project Structure

```
revanced-gui/
├── src/                    # Source code
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration management
│   │   ├── java_manager.py # Java detection and validation
│   │   ├── patcher.py     # APK patching logic
│   │   └── system_monitor.py # System monitoring
│   ├── ui/                # User interface
│   │   ├── dialogs.py     # Help and about dialogs
│   │   └── main_window.py # Main application window
│   └── revanced_gui.py    # Main application class
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup configuration
├── Makefile              # Development commands
└── README.md             # This file
```

## 🛠️ Development

### Development Setup

```bash
# Install development dependencies
make install-dev

# Check dependencies
make check-deps

# Run linting
make lint

# Format code
make format

# Clean build artifacts
make clean
```

### Code Quality

The project follows these standards:
- **PEP 8** compliance with 100-character line limit
- **Type hints** where applicable
- **Comprehensive documentation** with docstrings
- **Modular architecture** with separation of concerns
- **Error handling** with specific recovery suggestions

## 📋 System Requirements

### Minimum Requirements
- Python 3.8+ with tkinter
- Java 8+ (for ReVanced CLI)
- 2GB free disk space
- 4GB RAM

### Recommended Requirements
- Python 3.10+
- Java 11+
- 5GB free disk space
- 8GB RAM
- psutil and tkinterdnd2 packages

## 🔧 Configuration

The application automatically saves configuration in `config.json`:

```json
{
  "save_logs_enabled": false,
  "save_config_enabled": true,
  "last_cli_path": "/path/to/revanced-cli.jar",
  "last_patches_path": "/path/to/patches.rvp",
  "last_output_dir": "/path/to/output",
  "window_geometry": "1000x600+100+100"
}
```

## 📝 Logging

Logs are saved to the `logs/` directory when enabled:
- **Console output** - Always displayed in the interface
- **File logging** - Optional, with timestamps and detailed information
- **Export functionality** - Save current session log to file

## 🐛 Troubleshooting

### Common Issues

**Java not found:**
- Install Java 8+ and ensure it's in your PATH
- Verify with: `java -version`

**File not found errors:**
- Check file paths and permissions
- Ensure files are not corrupted

**Patching failed:**
- Verify APK version matches patches
- Check available disk space
- Review log output for specific errors

**Performance issues:**
- Close other applications
- Ensure sufficient RAM and disk space
- Use original APK files from trusted sources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ReVanced Team** - For the amazing ReVanced project
- **Community Contributors** - For feedback and improvements
- **Python Community** - For the excellent libraries and tools

## 📞 Support

- **Issues** - Report bugs and request features on GitHub Issues
- **Discussions** - Join community discussions on GitHub Discussions
- **Documentation** - Check the built-in help dialog for usage instructions

---

**Note:** This is an unofficial GUI wrapper. For official ReVanced tools and support, visit the [ReVanced GitHub organization](https://github.com/revanced).