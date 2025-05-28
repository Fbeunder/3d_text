# Installation Guide

Complete installation instructions for the 3D Text Generator.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Development Installation](#development-installation)
- [Dependency Details](#dependency-details)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **Python**: 3.7 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 500MB free space
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

### Recommended Requirements

- **Python**: 3.9 or higher
- **RAM**: 8GB or more
- **Storage**: 2GB free space
- **Graphics**: Dedicated GPU for better preview performance
- **Operating System**: Latest stable versions

### Python Version Compatibility

| Python Version | Support Status | Notes |
|----------------|----------------|-------|
| 3.7 | ✅ Supported | Minimum version |
| 3.8 | ✅ Supported | Recommended |
| 3.9 | ✅ Supported | Recommended |
| 3.10 | ✅ Supported | Recommended |
| 3.11 | ✅ Supported | Latest tested |
| 3.12+ | ⚠️ Experimental | May work but not tested |

---

## Quick Installation

### Option 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/Fbeunder/3d_text.git
cd 3d_text

# Install dependencies
pip install -r requirements.txt

# Verify installation
python main.py "Test" --preview
```

### Option 2: Download ZIP

1. Download the ZIP file from [GitHub](https://github.com/Fbeunder/3d_text)
2. Extract to your desired location
3. Open terminal/command prompt in the extracted folder
4. Run: `pip install -r requirements.txt`

---

## Platform-Specific Instructions

### Windows

#### Prerequisites

1. **Install Python:**
   - Download from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation
   - ✅ Check "Install pip"

2. **Install Git (optional but recommended):**
   - Download from [git-scm.com](https://git-scm.com/download/win)

#### Installation Steps

```cmd
# Open Command Prompt or PowerShell

# Clone repository
git clone https://github.com/Fbeunder/3d_text.git
cd 3d_text

# Create virtual environment (recommended)
python -m venv venv
venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Test installation
python main.py "Hello Windows" --preview
```

#### Windows-Specific Notes

- **Visual C++ Build Tools**: Some dependencies may require Microsoft Visual C++ 14.0. Download from [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- **Font Paths**: Windows fonts are typically in `C:\\Windows\\Fonts\\`
- **PowerShell**: Use PowerShell for better Unicode support

### macOS

#### Prerequisites

1. **Install Python:**
   ```bash
   # Using Homebrew (recommended)
   brew install python
   
   # Or download from python.org
   ```

2. **Install Xcode Command Line Tools:**
   ```bash
   xcode-select --install
   ```

#### Installation Steps

```bash
# Open Terminal

# Clone repository
git clone https://github.com/Fbeunder/3d_text.git
cd 3d_text

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test installation
python main.py "Hello macOS" --preview
```

#### macOS-Specific Notes

- **Font Paths**: System fonts are in `/System/Library/Fonts/` and `/Library/Fonts/`
- **Matplotlib Backend**: May need to install additional backends for GUI preview
- **M1/M2 Macs**: All dependencies are compatible with Apple Silicon

### Linux (Ubuntu/Debian)

#### Prerequisites

```bash
# Update package list
sudo apt update

# Install Python and development tools
sudo apt install python3 python3-pip python3-venv python3-dev

# Install system dependencies for graphics
sudo apt install libgl1-mesa-glx libglib2.0-0 libxrender1 libxext6

# Install Git
sudo apt install git
```

#### Installation Steps

```bash
# Clone repository
git clone https://github.com/Fbeunder/3d_text.git
cd 3d_text

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test installation
python main.py "Hello Linux" --preview
```

#### Linux-Specific Notes

- **Font Paths**: System fonts are typically in `/usr/share/fonts/` and `~/.fonts/`
- **Display Issues**: For headless servers, use `--save-preview` instead of `--preview`
- **Package Managers**: Instructions above are for Ubuntu/Debian. Adjust for other distributions.

### Linux (CentOS/RHEL/Fedora)

#### Prerequisites

```bash
# CentOS/RHEL
sudo yum install python3 python3-pip python3-devel gcc git
sudo yum install mesa-libGL-devel

# Fedora
sudo dnf install python3 python3-pip python3-devel gcc git
sudo dnf install mesa-libGL-devel
```

### Linux (Arch)

#### Prerequisites

```bash
sudo pacman -S python python-pip git gcc mesa
```

---

## Development Installation

For contributing to the project or advanced usage:

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Fbeunder/3d_text.git
cd 3d_text

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt

# Install additional development tools
pip install black flake8 mypy pytest-xdist
```

### Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test files
python -m pytest tests/test_text_processor.py -v

# Run integration tests
python -m pytest tests/test_integration.py -v
```

---

## Dependency Details

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | >=1.21.0 | Numerical computations |
| scipy | >=1.7.0 | Scientific computing |
| freetype-py | >=2.3.0 | Font processing |
| Pillow | >=9.0.0 | Image processing |
| trimesh | >=3.15.0 | 3D mesh operations |
| numpy-stl | >=2.16.0 | STL file handling |
| matplotlib | >=3.5.0 | 3D visualization |

### Optional Dependencies

| Package | Purpose | Installation |
|---------|---------|--------------|
| mayavi | Advanced 3D visualization | `pip install mayavi` |
| PyQt5 | GUI interface | `pip install PyQt5` |
| sphinx | Documentation generation | `pip install sphinx` |

### Development Dependencies

| Package | Purpose |
|---------|---------|
| pytest | Testing framework |
| pytest-cov | Coverage reporting |
| black | Code formatting |
| flake8 | Code linting |
| psutil | Performance monitoring |

### Installing Optional Dependencies

```bash
# For advanced 3D visualization
pip install mayavi

# For GUI interface (future feature)
pip install PyQt5

# For documentation building
pip install sphinx sphinx-rtd-theme

# All optional dependencies
pip install mayavi PyQt5 sphinx sphinx-rtd-theme
```

---

## Verification

### Basic Verification

```bash
# Test basic functionality
python main.py "Test" -o test.stl

# Test with preview
python main.py "Preview Test" --preview

# Test different formats
python main.py "Format Test" -o test.obj --format OBJ
```

### Comprehensive Verification

```bash
# Run test suite
python -m pytest tests/ -v

# Test with statistics
python main.py "Stats Test" --stats -o stats_test.stl

# Test with custom font (if available)
python main.py "Font Test" -f /path/to/font.ttf -o font_test.stl
```

### Performance Verification

```bash
# Test with verbose output
python main.py "Performance Test" -v --stats -o perf_test.stl

# Test memory usage
python -c "
import psutil
import subprocess
import sys

process = subprocess.Popen([
    sys.executable, 'main.py', 'Memory Test', '-o', 'memory_test.stl'
])
process.wait()
print(f'Peak memory usage: {psutil.Process(process.pid).memory_info().rss / 1024 / 1024:.1f} MB')
"
```

---

## Troubleshooting

### Common Installation Issues

#### Issue: "pip: command not found"

**Solution:**
```bash
# Windows
python -m ensurepip --upgrade

# macOS/Linux
sudo apt install python3-pip  # Ubuntu/Debian
brew install python           # macOS with Homebrew
```

#### Issue: "Microsoft Visual C++ 14.0 is required" (Windows)

**Solution:**
1. Download Microsoft Visual C++ Build Tools
2. Install with C++ build tools workload
3. Restart command prompt
4. Retry installation

#### Issue: "No module named '_tkinter'" (Linux)

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Fedora
sudo dnf install python3-tkinter
```

#### Issue: "ImportError: libGL.so.1" (Linux)

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install libgl1-mesa-glx

# CentOS/RHEL
sudo yum install mesa-libGL

# Fedora
sudo dnf install mesa-libGL
```

#### Issue: "Permission denied" errors

**Solution:**
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate    # Windows

# Or install with --user flag
pip install --user -r requirements.txt
```

### Dependency Issues

#### Issue: "Failed building wheel for [package]"

**Solution:**
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install build dependencies
pip install Cython numpy

# Retry installation
pip install -r requirements.txt
```

#### Issue: Matplotlib backend issues

**Solution:**
```bash
# Install GUI backend
pip install PyQt5

# Or use non-interactive backend
export MPLBACKEND=Agg  # Linux/macOS
set MPLBACKEND=Agg     # Windows
```

### Platform-Specific Issues

#### Windows: Long path issues

**Solution:**
- Enable long path support in Windows 10+
- Use shorter installation paths
- Use virtual environments

#### macOS: SSL certificate issues

**Solution:**
```bash
# Update certificates
/Applications/Python\\ 3.x/Install\\ Certificates.command

# Or install certificates manually
pip install --upgrade certifi
```

#### Linux: Display issues on headless servers

**Solution:**
```bash
# Use virtual display
sudo apt install xvfb
xvfb-run -a python main.py "Test" --save-preview test.png

# Or use non-GUI mode
python main.py "Test" -o test.stl  # Skip --preview
```

### Getting Help

If you encounter issues not covered here:

1. **Check the [Troubleshooting Guide](troubleshooting.md)**
2. **Search existing [GitHub Issues](https://github.com/Fbeunder/3d_text/issues)**
3. **Create a new issue** with:
   - Your operating system and version
   - Python version (`python --version`)
   - Complete error message
   - Steps to reproduce

---

## Next Steps

After successful installation:

1. **Read the [User Guide](user_guide.md)** for usage instructions
2. **Check out [Examples](../examples/)** for practical use cases
3. **Review the [API Documentation](api.md)** for advanced usage
4. **Join the community** on GitHub Discussions

**Congratulations! You're ready to create amazing 3D text! 🎉**