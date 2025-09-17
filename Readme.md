# ReVanced Patcher GUI

A cross-platform graphical user interface for the ReVanced CLI patching tool, making it easier to patch Android APK files with ReVanced patches.

![ReVanced Patcher GUI](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-success) ![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue) ![Version](https://img.shields.io/badge/Version-1.3.0-green)

## Features

- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux
- **User-Friendly Interface**: Intuitive GUI that simplifies the patching process
- **Drag & Drop Support**: Drop files directly onto the interface for quick selection
- **Automatic Naming**: Automatically adds "-patched" suffix to output files
- **Real-Time Logging**: View patching progress in real-time with detailed output
- **File Browsing**: Easy file selection with native dialogs
- **Dynamic Scaling**: Responsive UI that adapts to window size changes
- **System Monitoring**: Real-time system resource monitoring and validation
- **Profile Management**: Save and load different configuration profiles
- **Recent Files**: Quick access to recently used files
- **Error Handling**: Comprehensive validation and error reporting with auto-retry
- **APK Analysis**: Built-in APK and patches file analysis tools
- **Keyboard Shortcuts**: Full keyboard navigation support

## Prerequisites

Before using this application, ensure you have:

1. **Python 3.7 or higher** installed on your system
2. **Java Runtime Environment (JRE)** installed (required by ReVanced CLI)
3. **ReVanced CLI JAR** file (revanced-cli.jar)
4. **ReVanced Patches** file (patches.rvp)

### Installing Prerequisites

#### Python Installation
- **Windows**: Download from [python.org](https://python.org)
- **macOS**: Pre-installed on newer versions, or use Homebrew: `brew install python`
- **Linux**: Use your package manager:
  - Ubuntu/Debian: `sudo apt-get install python3 python3-tk`
  - Fedora: `sudo dnf install python3 python3-tkinter`

#### Java Installation
- **Windows**: Download from [java.com](https://java.com)
- **macOS**: `brew install openjdk`
- **Linux**:
  - Ubuntu/Debian: `sudo apt-get install openjdk-17-jre`
  - Fedora: `sudo dnf install java-17-openjdk`

#### ReVanced Files
Download the latest ReVanced files from:
- CLI: [ReVanced CLI Releases](https://github.com/revanced/revanced-cli/releases)
- Patches: [ReVanced Patches Releases](https://github.com/revanced/revanced-patches/releases)

## Quick Start

1. **Download and run**:
   ```bash
   git clone https://github.com/your-username/revanced-patcher-gui.git
   cd revanced-patcher-gui
   pip install -r requirements.txt
   python gui.py
   ```

2. **Drag & drop your files** or use the browse buttons to select:
   - ReVanced CLI JAR file
   - Patches RVP file  
   - APK file to patch

3. **Click "Patch APK"** and monitor the progress!

## Installation

1. **Download the script**:
   ```bash
   git clone https://github.com/your-username/revanced-patcher-gui.git
   cd revanced-patcher-gui
   ```

2. **Install optional dependencies** (recommended):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python gui.py
   ```

   Or if you have multiple Python versions:
   ```bash
   python3 gui.py
   ```

## Usage

### Step-by-Step Guide

1. **Launch the application** by running the Python script
2. **Select ReVanced CLI JAR**:
   - Click "Browse" next to "ReVanced CLI JAR" or drag & drop the file
   - Navigate to and select your `revanced-cli.jar` file

3. **Select Patches File**:
   - Click "Browse" next to "Patches RVP" or drag & drop the file
   - Navigate to and select your `patches.rvp` file

4. **Select APK File**:
   - Click "Browse" next to "APK File" or drag & drop the file
   - Select the APK you want to patch (e.g., `youtube.apk`)

5. **Choose Output Directory**:
   - Click "Browse" next to "Output Directory"
   - Select where you want to save the patched APK

6. **Review Output Filename**:
   - The application automatically suggests a filename with "-patched" suffix
   - You can modify this if desired

7. **Start Patching**:
   - Click "Patch APK" to begin the patching process
   - Monitor progress in the log area with real-time updates

8. **Completion**:
   - When finished, you'll see a success message
   - The patched APK will be saved in your chosen output directory

### Advanced Features

- **Drag & Drop**: Simply drag files from your file manager directly onto the input fields
- **Profiles**: Save your current settings as a profile for quick reuse (File → Profiles → Save Current Profile)
- **Recent Files**: Access recently used files from the File menu
- **System Validation**: Use "Validate Setup" to check system requirements
- **APK Analysis**: Analyze APK files before patching (View → Analyze APK)
- **Keyboard Shortcuts**: 
  - `Ctrl+O`: Open APK file
  - `Ctrl+P`: Start patching
  - `Ctrl+L`: Clear log
  - `Ctrl+S`: Export log
  - `F1`: System Information
  - `F5`: Validate system

### Menu Options

**File Menu:**
- **Clear Log**: Clear the progress log area
- **Recent Files**: Access recently used files
- **Profiles**: Save and load configuration profiles
- **Export Log**: Save the current log to a file
- **Exit**: Close the application

**View Menu:**
- **System Info**: Display detailed system information
- **Analyze APK**: Analyze APK file structure and contents
- **Analyze Patches**: Analyze patches file information

**Help Menu:**
- **Documentation**: Open ReVanced documentation in browser
- **Help Contents**: Show comprehensive help dialog
- **About**: View application information including:
  - Version number (v1.3.0)
  - Author information
  - License details (MIT)
  - GitHub repository link

## Command Line Equivalent

This GUI executes the following command behind the scenes:

```bash
java -jar revanced-cli.jar patch -p patches.rvp -o output.apk input.apk
```

## Troubleshooting

### Common Issues

1. **Java Not Found Error**:
   - Ensure Java is installed and available in your PATH
   - Verify installation with: `java -version`

2. **File Not Found Errors**:
   - Double-check that all file paths are correct
   - Ensure files exist at the specified locations

3. **Patching Failures**:
   - Make sure you're using compatible versions of CLI, patches, and APK
   - Check the ReVanced documentation for version requirements

4. **GUI Rendering Issues**:
   - On Linux, ensure python3-tk is installed
   - On macOS, if using a bundled Python, Tkinter should be included

### Logging

The application provides detailed logs in the progress area:
- Command being executed
- Real-time output from the patching process
- Success/error messages
- Output file location
- System resource monitoring
- Error reports with troubleshooting suggestions

### Recent Improvements (v1.3.0)

- **Code Quality**: Removed unused methods and variables for cleaner codebase
- **Import Optimization**: Fixed missing imports and dependency management
- **Enhanced UX**: Added drag & drop support for intuitive file selection
- **System Integration**: Real-time system monitoring and validation
- **Workflow Enhancement**: Profile management and recent files for better productivity
- **Error Recovery**: Auto-retry mechanism for failed operations
- **Analysis Tools**: Built-in APK and patches file analysis

## Project Structure

```
revanced-patcher-gui/
├── gui.py              # Main application script
├── README.md           # This documentation
└── requirements.txt    # Python dependencies (optional)
```

## Development

### Dependencies

**Core Dependencies (included with Python):**
- `tkinter` for the GUI
- `subprocess` for running commands
- `threading` for non-blocking operations
- `os` and `sys` for file operations

**Optional Dependencies (recommended):**
- `tkinterdnd2` for drag-and-drop file support
- `psutil` for system monitoring and resource usage

Install optional dependencies with:
```bash
pip install -r requirements.txt
```

### Modifying the Application

To customize the application:

1. **UI Changes**: Modify the `setup_ui()` method
2. **Functionality**: Edit the patching logic in `patch_apk()` and `run_patching()`
3. **Appearance**: Adjust colors, fonts, and layouts in the UI setup

### Building Executables

To create standalone executables:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Build for your platform**:
   ```bash
   pyinstaller --onefile --windowed gui.py
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Acknowledgments

- **ReVanced Team**: For creating the excellent patching tools
- **Python Community**: For the robust standard library
- **Tkinter Developers**: For the cross-platform GUI toolkit

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Search for similar issues in the GitHub repository
3. Create a new issue with:
   - Your operating system
   - Python version
   - Steps to reproduce the problem
   - Error messages from the log area

## Version History

- **v1.3.0** (Current)
  - Enhanced drag & drop support with tkinterdnd2
  - Added system monitoring with psutil integration
  - Profile management system for saving/loading configurations
  - Recent files functionality for quick access
  - APK and patches file analysis tools
  - Comprehensive keyboard shortcuts
  - Auto-retry mechanism for failed operations
  - Improved error handling and reporting
  - System validation and resource monitoring
  - Code optimization and dead code removal

- **v1.0.0** (Previous)
  - Initial release
  - Cross-platform GUI for ReVanced patching
  - Automatic output naming with "-patched" suffix
  - Real-time progress logging
  - Basic error handling

