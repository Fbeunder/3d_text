# Troubleshooting Guide

Solutions for common issues with the 3D Text Generator.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Font Issues](#font-issues)
- [Text Processing Issues](#text-processing-issues)
- [3D Generation Issues](#3d-generation-issues)
- [Preview and Rendering Issues](#preview-and-rendering-issues)
- [Export Issues](#export-issues)
- [Performance Issues](#performance-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Error Messages](#error-messages)
- [Getting Help](#getting-help)

---

## Installation Issues

### Python Version Issues

**Problem:** "Python version not supported" or compatibility errors

**Solutions:**
```bash
# Check Python version
python --version

# Install supported version (3.7+)
# Windows: Download from python.org
# macOS: brew install python@3.9
# Linux: sudo apt install python3.9
```

### Dependency Installation Failures

**Problem:** "Failed building wheel" or "Microsoft Visual C++ required"

**Solutions:**
```bash
# Update pip and build tools
pip install --upgrade pip setuptools wheel

# Windows: Install Visual C++ Build Tools
# Download from Microsoft Visual Studio website

# Install dependencies one by one
pip install numpy
pip install scipy
pip install freetype-py
pip install -r requirements.txt
```

### Permission Errors

**Problem:** "Permission denied" during installation

**Solutions:**
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate    # Windows
pip install -r requirements.txt

# Or install for user only
pip install --user -r requirements.txt
```

### Import Errors After Installation

**Problem:** "ModuleNotFoundError" when running the application

**Solutions:**
```bash
# Verify installation
pip list | grep -E "(numpy|scipy|freetype|trimesh|matplotlib)"

# Reinstall missing packages
pip install --force-reinstall [package-name]

# Check Python path
python -c "import sys; print(sys.path)"
```

---

## Font Issues

### Font Not Found

**Problem:** "Font file not found" or "FontLoadError"

**Solutions:**
```bash
# Use absolute path
python main.py "Text" -f /full/path/to/font.ttf -o output.stl

# Check if file exists
ls -la /path/to/font.ttf  # Linux/macOS
dir "C:\\path\\to\\font.ttf"  # Windows

# Use system fonts
# Windows: C:\\Windows\\Fonts\\arial.ttf
# macOS: /System/Library/Fonts/Arial.ttf
# Linux: /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf

# Let application find default font
python main.py "Text" -o output.stl  # No -f flag
```

### Font Loading Errors

**Problem:** "Failed to load font" with valid font file

**Solutions:**
```bash
# Check font file integrity
file /path/to/font.ttf  # Should show "TrueType font data"

# Try different font
python main.py "Text" -f /path/to/different/font.ttf -o output.stl

# Use verbose mode for debugging
python main.py "Text" -f /path/to/font.ttf -v -o output.stl

# Check font permissions
chmod 644 /path/to/font.ttf  # Linux/macOS
```

### Unsupported Font Format

**Problem:** Font format not recognized

**Solutions:**
- **Supported formats:** TTF, OTF
- **Not supported:** WOFF, EOT, SVG fonts
- **Convert fonts:** Use online converters or FontForge

```bash
# Check font format
file font.ttf  # Should show TrueType or OpenType
```

### Missing Characters

**Problem:** Some characters don't appear in 3D output

**Solutions:**
```bash
# Check if font supports the characters
python -c "
from text_processor import FontLoader
loader = FontLoader()
loader.load_font('font.ttf', 48)
print('Character supported:', loader.get_character_outline('ñ') is not None)
"

# Use font with better Unicode support
# Good options: Arial, Roboto, Noto Sans

# Check character encoding
python main.py "Test: ñáéíóú" -f arial.ttf --preview
```

---

## Text Processing Issues

### Empty Output

**Problem:** No 3D geometry generated from text

**Solutions:**
```bash
# Check text content
python main.py "Hello World" --preview  # Use simple ASCII text first

# Verify font loading
python main.py "Test" -f /path/to/font.ttf -v --preview

# Check for invisible characters
python -c "print(repr('your text here'))"

# Use different font
python main.py "Test" -f arial.ttf --preview
```

### Text Layout Issues

**Problem:** Characters overlapping or incorrectly positioned

**Solutions:**
```bash
# Adjust character spacing
python main.py "Overlapping" --character-spacing 1.0 --preview

# Try different font size
python main.py "Text" --font-size 64 --preview

# Use monospace font for consistent spacing
python main.py "Text" -f courier.ttf --preview
```

### Special Characters

**Problem:** Accented characters or symbols not working

**Solutions:**
```bash
# Use UTF-8 encoding
export PYTHONIOENCODING=utf-8  # Linux/macOS
set PYTHONIOENCODING=utf-8     # Windows

# Test with simple characters first
python main.py "ABC123" --preview

# Use Unicode escape sequences
python main.py "Caf\\u00e9" --preview  # For "Café"

# Choose font with good Unicode support
python main.py "Café" -f "Noto Sans.ttf" --preview
```

---

## 3D Generation Issues

### Geometry Generation Failures

**Problem:** "GeometryError" or "Failed to generate geometry"

**Solutions:**
```bash
# Use simpler parameters
python main.py "Text" -d 5 -b 0 --preview

# Check text complexity
python main.py "A" --preview  # Test with single character

# Reduce bevel depth
python main.py "Text" -d 10 -b 1 --preview

# Use verbose mode for debugging
python main.py "Text" -v --preview
```

### Mesh Validation Errors

**Problem:** "MeshValidationError" or invalid mesh warnings

**Solutions:**
```bash
# Simplify geometry
python main.py "Text" -d 5 -b 0 --bevel-resolution 2 --preview

# Use different font
python main.py "Text" -f arial.ttf --preview

# Check mesh statistics
python main.py "Text" --stats -o output.stl
```

### Memory Issues with Complex Text

**Problem:** Out of memory errors with long text or complex fonts

**Solutions:**
```bash
# Reduce text length
python main.py "Short" --preview

# Use smaller font size
python main.py "Long Text" --font-size 32 --preview

# Reduce bevel resolution
python main.py "Text" --bevel-resolution 2 --preview

# Process in parts
python main.py "Part 1" -o part1.stl
python main.py "Part 2" -o part2.stl
```

---

## Preview and Rendering Issues

### Preview Window Not Appearing

**Problem:** `--preview` flag doesn't show window

**Solutions:**
```bash
# Check display environment (Linux)
echo $DISPLAY

# Use X11 forwarding (SSH)
ssh -X user@server

# Try different backend
export MPLBACKEND=Qt5Agg  # Linux/macOS
set MPLBACKEND=Qt5Agg     # Windows

# Install GUI backend
pip install PyQt5

# Use image preview instead
python main.py "Text" --save-preview preview.png
```

### Preview Window Empty or Black

**Problem:** Preview window opens but shows nothing

**Solutions:**
```bash
# Check OpenGL support
python -c "
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot([0,1], [0,1], [0,1])
plt.show()
"

# Update graphics drivers
# Install mesa-utils (Linux)
sudo apt install mesa-utils
glxinfo | grep OpenGL

# Try software rendering
export LIBGL_ALWAYS_SOFTWARE=1  # Linux
```

### Slow Preview Performance

**Problem:** Preview is very slow or unresponsive

**Solutions:**
```bash
# Reduce geometry complexity
python main.py "Text" -d 5 -b 0 --bevel-resolution 2 --preview

# Use smaller font size
python main.py "Text" --font-size 32 --preview

# Close other applications
# Upgrade graphics drivers
# Use dedicated GPU if available
```

---

## Export Issues

### Export Failures

**Problem:** "ExportError" or failed to save file

**Solutions:**
```bash
# Check output directory permissions
mkdir -p output_dir
chmod 755 output_dir

# Use absolute path
python main.py "Text" -o /full/path/to/output.stl

# Try different format
python main.py "Text" -o output.obj --format OBJ

# Check disk space
df -h .  # Linux/macOS
dir      # Windows
```

### Large File Sizes

**Problem:** Exported files are unexpectedly large

**Solutions:**
```bash
# Check mesh statistics
python main.py "Text" --stats -o output.stl

# Reduce complexity
python main.py "Text" -d 5 -b 0 --font-size 32 -o output.stl

# Use binary format
python main.py "Text" -o output.stl  # STL binary by default

# Optimize mesh (future feature)
# Use mesh decimation tools
```

### Format-Specific Issues

**Problem:** Exported file won't open in target software

**Solutions:**
```bash
# Verify export format
python main.py "Text" -o model.stl --format STL  # Explicit format

# Try different format
python main.py "Text" -o model.obj --format OBJ  # More compatible

# Check file integrity
file output.stl  # Should show "data" or format info

# Validate with mesh viewer
# Use MeshLab, Blender, or online viewers
```

---

## Performance Issues

### Slow Processing

**Problem:** Text generation takes very long time

**Solutions:**
```bash
# Profile with timing
python main.py "Text" --stats -v -o output.stl

# Reduce complexity
python main.py "Text" --font-size 32 -d 5 -b 0 -o output.stl

# Use simpler font
python main.py "Text" -f arial.ttf -o output.stl

# Process shorter text
python main.py "Short" -o output.stl
```

### High Memory Usage

**Problem:** Application uses too much RAM

**Solutions:**
```bash
# Monitor memory usage
python -c "
import psutil
import subprocess
import sys

proc = subprocess.Popen([sys.executable, 'main.py', 'Text', '-o', 'test.stl'])
process = psutil.Process(proc.pid)
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
proc.wait()
"

# Reduce parameters
python main.py "Text" --font-size 24 -d 3 -b 0 -o output.stl

# Process in batches
# Close other applications
# Add more RAM if needed
```

---

## Platform-Specific Issues

### Windows Issues

**Problem:** Various Windows-specific errors

**Solutions:**
```cmd
REM Use PowerShell for better Unicode support
powershell

REM Set UTF-8 encoding
chcp 65001

REM Use short paths
cd C:\\3d_text

REM Install Visual C++ redistributables
REM Download from Microsoft website
```

### macOS Issues

**Problem:** macOS-specific errors

**Solutions:**
```bash
# Install Xcode command line tools
xcode-select --install

# Update certificates
/Applications/Python\\ 3.x/Install\\ Certificates.command

# Use Homebrew Python
brew install python
brew install freetype

# Set PYTHONPATH if needed
export PYTHONPATH=/usr/local/lib/python3.x/site-packages
```

### Linux Issues

**Problem:** Linux-specific errors

**Solutions:**
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-dev python3-tk libgl1-mesa-glx

# Fix display issues
export DISPLAY=:0

# Use virtual display for headless servers
sudo apt install xvfb
xvfb-run -a python main.py "Text" --save-preview preview.png

# Check font paths
fc-list | grep -i arial
```

---

## Error Messages

### Common Error Messages and Solutions

#### "FontLoadError: Failed to load font"
```bash
# Check font file exists and is readable
ls -la /path/to/font.ttf
python main.py "Text" -f /absolute/path/to/font.ttf -o output.stl
```

#### "TextProcessingError: Empty text provided"
```bash
# Ensure text is not empty
python main.py "Non-empty text" -o output.stl
```

#### "GeometryError: No character outlines available"
```bash
# Check font supports the characters
python main.py "ABC" -f arial.ttf --preview
```

#### "RenderingError: Failed to render preview"
```bash
# Install GUI backend
pip install PyQt5
# Or use image preview
python main.py "Text" --save-preview preview.png
```

#### "ExportError: Unsupported export format"
```bash
# Use supported format
python main.py "Text" -o output.stl --format STL
python main.py "Text" -o output.obj --format OBJ
```

#### "WorkflowError: Workflow execution failed"
```bash
# Use verbose mode to see detailed error
python main.py "Text" -v -o output.stl
```

### Debug Mode

Enable detailed debugging:

```bash
# Maximum verbosity
python main.py "Debug Text" -v --stats --log-file debug.log -o debug.stl

# Check log file
cat debug.log  # Linux/macOS
type debug.log # Windows
```

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Try with simple text and default settings**
3. **Update to the latest version**
4. **Check system requirements**

### Information to Include

When reporting issues, include:

```bash
# System information
python --version
pip list | grep -E "(numpy|scipy|freetype|trimesh|matplotlib)"
uname -a  # Linux/macOS
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"  # Windows

# Error reproduction
python main.py "Problem Text" -v --stats -o problem.stl 2>&1 | tee error.log
```

### Where to Get Help

1. **GitHub Issues**: [Report bugs and request features](https://github.com/Fbeunder/3d_text/issues)
2. **GitHub Discussions**: [Ask questions and share ideas](https://github.com/Fbeunder/3d_text/discussions)
3. **Documentation**: [Read the full documentation](../README.md)

### Creating a Good Issue Report

```markdown
## Problem Description
Brief description of the issue

## Steps to Reproduce
1. Run command: `python main.py "Text" -o output.stl`
2. Error occurs at step X

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [Windows 10/macOS 12/Ubuntu 20.04]
- Python version: [3.9.7]
- Package versions: [paste pip list output]

## Error Message
```
[paste complete error message]
```

## Additional Context
Any other relevant information
```

---

## Quick Fixes Checklist

When something doesn't work, try these in order:

1. ✅ **Use simple text**: `python main.py "Test" -o test.stl`
2. ✅ **Check Python version**: `python --version` (should be 3.7+)
3. ✅ **Update packages**: `pip install --upgrade -r requirements.txt`
4. ✅ **Use absolute paths**: Full paths for fonts and output files
5. ✅ **Try different font**: Use system fonts like Arial
6. ✅ **Reduce complexity**: Smaller font size, less depth, no bevel
7. ✅ **Check permissions**: Write access to output directory
8. ✅ **Use verbose mode**: Add `-v` flag for detailed output
9. ✅ **Try different format**: STL, OBJ, PLY instead of GLTF
10. ✅ **Restart terminal**: Fresh environment

**Still having issues? Don't hesitate to ask for help! 🤝**