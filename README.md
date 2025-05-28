# 3D Text Generator

A powerful Python application that converts 2D text into high-quality 3D models with various customization options and export formats.

## 🌟 Features

- **Font Support**: TTF and OTF font files with automatic fallback to system fonts
- **3D Generation**: Advanced extrusion and beveling for realistic 3D text
- **Multiple Export Formats**: STL, OBJ, PLY, and GLTF/GLB support
- **Interactive Preview**: Real-time 3D visualization with camera controls
- **Batch Processing**: Process multiple texts or configurations
- **Customizable Parameters**: Font size, character spacing, extrusion depth, bevel effects
- **High Performance**: Optimized mesh generation with validation
- **Comprehensive CLI**: Full command-line interface with extensive options

## 📋 Requirements

- Python 3.7 or higher
- Operating System: Windows, macOS, or Linux

## 🚀 Quick Installation

```bash
# Clone the repository
git clone https://github.com/Fbeunder/3d_text.git
cd 3d_text

# Install dependencies
pip install -r requirements.txt
```

## ⚡ Quick Start

### Basic Usage

```bash
# Generate a simple 3D text model
python main.py "Hello World" -o hello.stl

# Use a custom font
python main.py "Custom Text" -f /path/to/font.ttf -o custom.stl

# Generate with custom parameters
python main.py "3D Text" -d 10 -b 2 --font-size 72 -o text3d.obj --format OBJ
```

### Preview Before Export

```bash
# Show interactive 3D preview
python main.py "Preview Text" --preview

# Save preview image
python main.py "Preview Text" --save-preview preview.png -o model.stl
```

### Advanced Usage

```bash
# Full customization example
python main.py "Advanced" \
  --font /path/to/font.ttf \
  --font-size 64 \
  --character-spacing 1.2 \
  --depth 15 \
  --bevel 3 \
  --format GLTF \
  --export-scale 2.0 \
  --output-dir ./models \
  --preview \
  --verbose \
  --stats
```

## 📖 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[User Guide](docs/user_guide.md)** - Comprehensive tutorials and examples
- **[API Documentation](docs/api.md)** - Complete API reference
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 💡 Examples

Check out the [examples/](examples/) directory for:

- **[Basic Usage](examples/basic_usage.py)** - Simple text generation examples
- **[Advanced Usage](examples/advanced_usage.py)** - Complex configurations and workflows
- **[Batch Processing](examples/batch_processing.py)** - Processing multiple texts
- **[Custom Fonts](examples/custom_fonts.py)** - Working with different font files

## 🛠️ Command Line Options

### Required Arguments
- `text` - Text to convert to 3D model

### Font Options
- `-f, --font` - Path to font file (TTF/OTF)
- `--font-size` - Font size in points (default: 48)
- `--character-spacing` - Character spacing (default: 0.0)

### 3D Geometry Options
- `-d, --depth` - Extrusion depth (default: 5.0)
- `-b, --bevel` - Bevel depth (default: 0.5)
- `--bevel-resolution` - Bevel resolution (default: 4)

### Export Options
- `-o, --output` - Output file path
- `--format` - Export format: STL, OBJ, PLY, GLTF (default: STL)
- `--export-scale` - Scale factor (default: 1.0)
- `--output-dir` - Output directory

### Preview Options
- `--preview` - Show interactive 3D preview
- `--save-preview` - Save preview image to file

### Output Options
- `-v, --verbose` - Enable verbose output
- `-q, --quiet` - Suppress non-error output
- `--log-file` - Log to file
- `--stats` - Show processing statistics

## 🏗️ Architecture

The application is built with a modular architecture:

```
3d_text/
├── main.py              # CLI interface and workflow orchestration
├── text_processor.py    # Font loading and text processing
├── geometry_generator.py # 3D mesh generation
├── renderer.py          # 3D visualization and rendering
├── exporter.py          # Multi-format export functionality
├── config.py            # Configuration management
├── utils.py             # Utility functions
├── tests/               # Comprehensive test suite
├── docs/                # Documentation
└── examples/            # Usage examples
```

### Core Components

- **Text Processor**: Handles font loading, text parsing, and character outline extraction
- **Geometry Generator**: Converts 2D outlines to 3D meshes with extrusion and beveling
- **Renderer**: Provides 3D visualization with camera controls and lighting
- **Exporter**: Supports multiple 3D file formats with validation
- **Main Application**: Orchestrates the complete workflow with CLI interface

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test modules
python -m pytest tests/test_text_processor.py -v
python -m pytest tests/test_integration.py -v
```

## 🔧 Development

### Setting up Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/Fbeunder/3d_text.git
cd 3d_text
pip install -e .

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking (if using mypy)
mypy .
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with tests
4. **Run the test suite**: `python -m pytest tests/`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Contribution Guidelines

- Write tests for new functionality
- Follow the existing code style
- Update documentation for new features
- Ensure all tests pass
- Add examples for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FreeType** for font rendering capabilities
- **Trimesh** for 3D mesh processing
- **Matplotlib** for 3D visualization
- **NumPy** and **SciPy** for numerical computations

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Fbeunder/3d_text/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Fbeunder/3d_text/discussions)
- **Documentation**: [Full Documentation](docs/)

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added GLTF export and improved rendering
- **v1.2.0** - Enhanced CLI interface and batch processing
- **v1.3.0** - Comprehensive testing and documentation

---

**Made with ❤️ by [Fbeunder](https://github.com/Fbeunder)**