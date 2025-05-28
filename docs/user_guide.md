# User Guide

Complete guide for using the 3D Text Generator application.

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Tutorials](#tutorials)
- [Best Practices](#best-practices)
- [Performance Tips](#performance-tips)
- [FAQ](#faq)

---

## Getting Started

### First Steps

After installation, you can immediately start generating 3D text:

```bash
# Your first 3D text
python main.py "Hello World" -o hello.stl
```

This creates a basic 3D model of "Hello World" and saves it as `hello.stl`.

### Understanding the Workflow

The 3D Text Generator follows a simple workflow:

1. **Font Loading** - Load a font file (TTF/OTF)
2. **Text Processing** - Parse text and extract character outlines
3. **Geometry Generation** - Convert 2D outlines to 3D meshes
4. **Preview** (optional) - Visualize the 3D model
5. **Export** - Save to your preferred 3D format

---

## Basic Usage

### Simple Text Generation

```bash
# Basic usage with default settings
python main.py "My Text" -o output.stl

# Specify output format
python main.py "My Text" -o output.obj --format OBJ
```

### Using Custom Fonts

```bash
# Use a specific font file
python main.py "Custom Font" -f /path/to/font.ttf -o custom.stl

# Adjust font size
python main.py "Big Text" -f arial.ttf --font-size 72 -o big.stl
```

### Adjusting 3D Parameters

```bash
# Change extrusion depth
python main.py "Deep Text" -d 15 -o deep.stl

# Add bevel effect
python main.py "Beveled" -d 10 -b 3 -o beveled.stl

# Combine parameters
python main.py "Custom 3D" -d 12 -b 2 --font-size 64 -o custom3d.stl
```

---

## Advanced Features

### Preview Functionality

Preview your 3D text before exporting:

```bash
# Interactive 3D preview
python main.py "Preview Me" --preview

# Save preview image
python main.py "Preview Me" --save-preview preview.png -o model.stl

# Both interactive and saved preview
python main.py "Preview Me" --preview --save-preview preview.png -o model.stl
```

### Character Spacing

Control spacing between characters:

```bash
# Tight spacing
python main.py "Tight" --character-spacing -0.5 -o tight.stl

# Wide spacing
python main.py "Wide" --character-spacing 2.0 -o wide.stl
```

### Export Options

#### Multiple Formats

```bash
# STL (default) - good for 3D printing
python main.py "For Printing" -o print.stl

# OBJ - good for 3D modeling software
python main.py "For Modeling" -o model.obj --format OBJ

# PLY - good for research and analysis
python main.py "For Research" -o research.ply --format PLY

# GLTF - good for web and games
python main.py "For Web" -o web.glb --format GLTF
```

#### Scaling

```bash
# Scale up for large prints
python main.py "Large" --export-scale 5.0 -o large.stl

# Scale down for miniatures
python main.py "Mini" --export-scale 0.1 -o mini.stl
```

### Output Management

```bash
# Specify output directory
python main.py "Organized" --output-dir ./models -o text.stl

# Verbose output for debugging
python main.py "Debug" -v -o debug.stl

# Quiet mode for scripts
python main.py "Script" -q -o script.stl

# Show processing statistics
python main.py "Stats" --stats -o stats.stl
```

---

## Tutorials

### Tutorial 1: Creating Your First 3D Text

**Goal:** Create a simple 3D text model for 3D printing.

**Steps:**

1. **Choose your text:**
   ```bash
   python main.py "Hello 3D" -o hello3d.stl
   ```

2. **Preview the result:**
   ```bash
   python main.py "Hello 3D" --preview
   ```

3. **Adjust if needed:**
   ```bash
   python main.py "Hello 3D" -d 8 -b 1 --preview
   ```

4. **Export final version:**
   ```bash
   python main.py "Hello 3D" -d 8 -b 1 -o hello3d_final.stl
   ```

### Tutorial 2: Using Custom Fonts

**Goal:** Create 3D text with a specific font style.

**Steps:**

1. **Find a font file** (TTF or OTF format)

2. **Test with preview:**
   ```bash
   python main.py "Custom Style" -f /path/to/font.ttf --preview
   ```

3. **Adjust font size:**
   ```bash
   python main.py "Custom Style" -f /path/to/font.ttf --font-size 80 --preview
   ```

4. **Fine-tune and export:**
   ```bash
   python main.py "Custom Style" -f /path/to/font.ttf --font-size 80 -d 10 -b 2 -o custom_style.stl
   ```

### Tutorial 3: Creating Logo Text

**Goal:** Create 3D text suitable for a logo or sign.

**Steps:**

1. **Start with bold text:**
   ```bash
   python main.py "LOGO" -f bold_font.ttf --font-size 100 --preview
   ```

2. **Adjust for visibility:**
   ```bash
   python main.py "LOGO" -f bold_font.ttf --font-size 100 -d 15 -b 3 --preview
   ```

3. **Add spacing for clarity:**
   ```bash
   python main.py "LOGO" -f bold_font.ttf --font-size 100 --character-spacing 1.5 -d 15 -b 3 --preview
   ```

4. **Export in multiple formats:**
   ```bash
   # For 3D printing
   python main.py "LOGO" -f bold_font.ttf --font-size 100 --character-spacing 1.5 -d 15 -b 3 -o logo.stl
   
   # For 3D software
   python main.py "LOGO" -f bold_font.ttf --font-size 100 --character-spacing 1.5 -d 15 -b 3 -o logo.obj --format OBJ
   ```

### Tutorial 4: Batch Processing

**Goal:** Create multiple 3D text models with consistent settings.

**Create a batch script:**

```bash
#!/bin/bash

# Common settings
FONT="arial.ttf"
DEPTH=10
BEVEL=2
SIZE=64

# Generate multiple texts
python main.py "Text 1" -f $FONT --font-size $SIZE -d $DEPTH -b $BEVEL -o text1.stl
python main.py "Text 2" -f $FONT --font-size $SIZE -d $DEPTH -b $BEVEL -o text2.stl
python main.py "Text 3" -f $FONT --font-size $SIZE -d $DEPTH -b $BEVEL -o text3.stl

echo "Batch processing complete!"
```

### Tutorial 5: Optimizing for 3D Printing

**Goal:** Create 3D text optimized for 3D printing.

**Considerations:**
- Minimum feature size
- Overhang angles
- Support requirements

**Steps:**

1. **Start with appropriate depth:**
   ```bash
   python main.py "PRINT ME" -d 3 --preview
   ```

2. **Add minimal bevel for strength:**
   ```bash
   python main.py "PRINT ME" -d 3 -b 0.5 --preview
   ```

3. **Scale for your printer:**
   ```bash
   python main.py "PRINT ME" -d 3 -b 0.5 --export-scale 2.0 -o printable.stl
   ```

4. **Verify with statistics:**
   ```bash
   python main.py "PRINT ME" -d 3 -b 0.5 --export-scale 2.0 --stats -o printable.stl
   ```

---

## Best Practices

### Font Selection

**Good Fonts for 3D Text:**
- Sans-serif fonts (Arial, Helvetica, Roboto)
- Bold or medium weight fonts
- Fonts with clear, distinct characters

**Avoid:**
- Very thin fonts (may break in 3D printing)
- Fonts with very small details
- Script fonts with overlapping characters

### Parameter Guidelines

**Extrusion Depth:**
- For 3D printing: 2-10mm typically
- For display models: 5-20mm
- For miniatures: 0.5-2mm

**Bevel Depth:**
- Generally 10-30% of extrusion depth
- For sharp edges: 0 (no bevel)
- For rounded edges: 1-5mm

**Font Size:**
- For readability: 48-72 points
- For large displays: 100+ points
- For small details: 24-36 points

### File Organization

```
project/
├── fonts/           # Store font files
├── models/          # Generated 3D models
├── previews/        # Preview images
└── scripts/         # Batch processing scripts
```

### Naming Conventions

```bash
# Include key parameters in filename
python main.py "Logo" -f arial.ttf -d 10 -b 2 -o logo_arial_d10_b2.stl

# Use descriptive names
python main.py "Company Name" -o company_name_sign.stl
```

---

## Performance Tips

### Optimizing Generation Speed

1. **Use appropriate font sizes:**
   - Larger fonts = more detail = slower processing
   - Choose the minimum size that meets your needs

2. **Limit text length:**
   - Shorter text processes faster
   - Break long text into multiple models if needed

3. **Adjust bevel settings:**
   - Lower bevel resolution = faster processing
   - Skip bevel for simple models (`-b 0`)

4. **Use efficient workflows:**
   ```bash
   # Preview first, then export
   python main.py "Test" --preview
   python main.py "Test" -o final.stl  # Only after confirming settings
   ```

### Memory Management

For large or complex text:

```bash
# Monitor memory usage
python main.py "Complex Text" --stats -v -o complex.stl

# Use simpler settings for large text
python main.py "Very Long Text String" -d 5 -b 0 --font-size 48 -o long_text.stl
```

### Batch Processing Optimization

```bash
# Process multiple files efficiently
for text in "Text1" "Text2" "Text3"; do
    python main.py "$text" -f arial.ttf -d 10 -b 2 -o "${text,,}.stl" -q
done
```

---

## FAQ

### General Questions

**Q: What font formats are supported?**
A: TTF (TrueType) and OTF (OpenType) fonts are supported.

**Q: Can I use system fonts?**
A: Yes, the application will try to find system fonts if a specific path isn't provided.

**Q: What's the maximum text length?**
A: The default limit is 1000 characters, but this can be adjusted in the configuration.

**Q: Can I use Unicode characters?**
A: Yes, Unicode characters are supported if the font contains the necessary glyphs.

### Technical Questions

**Q: Why is my text not appearing in 3D?**
A: Check that:
- The font file is valid and readable
- The text contains supported characters
- The extrusion depth is greater than 0

**Q: The preview window is empty. What's wrong?**
A: This usually indicates:
- Missing or invalid font
- Text processing error
- Graphics driver issues

**Q: How do I fix "Font not found" errors?**
A: Try:
- Providing the full path to the font file
- Using a different font
- Letting the application use the default font

**Q: The exported file is too large. How can I reduce it?**
A: Options include:
- Reducing font size
- Decreasing extrusion depth
- Lowering bevel resolution
- Using a simpler font

### 3D Printing Questions

**Q: My 3D printed text is breaking. What should I do?**
A: Try:
- Increasing extrusion depth
- Adding a small bevel for strength
- Using a bolder font
- Scaling up the model

**Q: How do I orient text for 3D printing?**
A: Generally:
- Print with text face down for best surface quality
- Use supports for overhangs if needed
- Consider splitting very long text

**Q: What scale should I use for 3D printing?**
A: Depends on your printer and needs:
- Desktop printers: 1.0-5.0 scale typically
- Large format: 0.1-1.0 scale
- Miniatures: 0.05-0.2 scale

### Export Questions

**Q: Which format should I use?**
A: 
- **STL**: 3D printing, simple models
- **OBJ**: 3D modeling software, texturing
- **PLY**: Research, point cloud processing
- **GLTF**: Web applications, games

**Q: Can I edit the exported models?**
A: Yes, all exported formats can be imported into 3D modeling software like Blender, Maya, or 3ds Max.

**Q: How do I add materials or colors?**
A: Use OBJ format and import into 3D software to add materials, or use GLTF for basic material support.

### Troubleshooting

**Q: The application crashes with large text. What should I do?**
A: Try:
- Reducing text length
- Using smaller font size
- Decreasing bevel resolution
- Adding more RAM to your system

**Q: Preview is very slow. How can I speed it up?**
A: Options:
- Use lower resolution settings
- Skip preview for final exports
- Close other applications
- Use a simpler font

**Q: Exported file won't open in my 3D software. Why?**
A: Check:
- File format compatibility
- File size (very large files may fail)
- Try a different export format
- Validate the export with `--stats`

---

## Getting Help

If you need additional help:

1. **Check the [Troubleshooting Guide](troubleshooting.md)**
2. **Review the [API Documentation](api.md)**
3. **Look at the [Examples](../examples/)**
4. **Open an issue on [GitHub](https://github.com/Fbeunder/3d_text/issues)**

---

**Happy 3D Text Generation! 🎉**