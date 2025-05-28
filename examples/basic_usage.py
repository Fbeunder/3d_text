#!/usr/bin/env python3
"""
Basic Usage Examples for 3D Text Generator

This file demonstrates basic usage patterns for the 3D Text Generator.
Run these examples to learn how to use the application effectively.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import Text3DGenerator


def example_1_simple_text():
    """
    Example 1: Generate simple 3D text with default settings
    """
    print("Example 1: Simple 3D text generation")
    print("-" * 40)
    
    try:
        # Initialize the generator
        generator = Text3DGenerator()
        
        # Generate 3D text with default settings
        result = generator.run_workflow(
            text="Hello World",
            output_path="examples/output/hello_world.stl"
        )
        
        print(f"✅ Success! Model exported to: {result['exported_path']}")
        print(f"   Vertices: {result['processing_stats']['vertices']}")
        print(f"   Faces: {result['processing_stats']['faces']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_2_custom_font():
    """
    Example 2: Use a custom font file
    """
    print("Example 2: Custom font usage")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # Try to find a system font (adjust path for your system)
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "C:\\Windows\\Fonts\\arial.ttf",     # Windows
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break
        
        if font_path:
            result = generator.run_workflow(
                text="Custom Font",
                font_path=font_path,
                output_path="examples/output/custom_font.stl",
                font_size=64
            )
            print(f"✅ Success! Used font: {font_path}")
            print(f"   Model exported to: {result['exported_path']}")
        else:
            # Use default font
            result = generator.run_workflow(
                text="Default Font",
                output_path="examples/output/default_font.stl",
                font_size=64
            )
            print("✅ Success! Used default font")
            print(f"   Model exported to: {result['exported_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_3_3d_parameters():
    """
    Example 3: Customize 3D generation parameters
    """
    print("Example 3: Custom 3D parameters")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # Generate with custom extrusion depth and bevel
        result = generator.run_workflow(
            text="3D Custom",
            output_path="examples/output/custom_3d.stl",
            extrusion_depth=12.0,
            bevel_depth=2.5,
            font_size=72
        )
        
        print(f"✅ Success! Custom 3D parameters applied")
        print(f"   Extrusion depth: {result['processing_stats']['extrusion_depth']}")
        print(f"   Bevel depth: {result['processing_stats']['bevel_depth']}")
        print(f"   Model exported to: {result['exported_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_4_different_formats():
    """
    Example 4: Export to different file formats
    """
    print("Example 4: Different export formats")
    print("-" * 40)
    
    formats = [
        ("STL", "stl"),
        ("OBJ", "obj"),
        ("PLY", "ply"),
        ("GLTF", "glb")
    ]
    
    try:
        generator = Text3DGenerator()
        
        for format_name, extension in formats:
            result = generator.run_workflow(
                text="Format Test",
                output_path=f"examples/output/format_test.{extension}",
                export_format=format_name,
                font_size=48,
                extrusion_depth=8.0
            )
            print(f"✅ {format_name} export: {result['exported_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_5_character_spacing():
    """
    Example 5: Adjust character spacing
    """
    print("Example 5: Character spacing adjustment")
    print("-" * 40)
    
    spacing_values = [
        ("tight", -0.5),
        ("normal", 0.0),
        ("wide", 1.5)
    ]
    
    try:
        generator = Text3DGenerator()
        
        for name, spacing in spacing_values:
            result = generator.run_workflow(
                text="SPACING",
                output_path=f"examples/output/spacing_{name}.stl",
                character_spacing=spacing,
                font_size=56
            )
            print(f"✅ {name.capitalize()} spacing ({spacing}): {result['exported_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_6_with_preview():
    """
    Example 6: Generate with preview (save preview image)
    """
    print("Example 6: Generate with preview")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # Generate with saved preview image
        result = generator.run_workflow(
            text="Preview Me",
            output_path="examples/output/with_preview.stl",
            save_preview="examples/output/preview.png",
            font_size=60,
            extrusion_depth=10.0,
            bevel_depth=2.0
        )
        
        print(f"✅ Success! Model and preview generated")
        print(f"   Model: {result['exported_path']}")
        if 'preview_path' in result:
            print(f"   Preview: {result['preview_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_7_scaling():
    """
    Example 7: Export with different scales
    """
    print("Example 7: Export scaling")
    print("-" * 40)
    
    scales = [
        ("small", 0.5),
        ("normal", 1.0),
        ("large", 2.0)
    ]
    
    try:
        generator = Text3DGenerator()
        
        for name, scale in scales:
            result = generator.run_workflow(
                text="Scale Test",
                output_path=f"examples/output/scale_{name}.stl",
                export_scale=scale,
                font_size=48
            )
            print(f"✅ {name.capitalize()} scale ({scale}x): {result['exported_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_8_error_handling():
    """
    Example 8: Proper error handling
    """
    print("Example 8: Error handling")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # This should work
        result = generator.run_workflow(
            text="Good Text",
            output_path="examples/output/good_text.stl"
        )
        print(f"✅ Success: {result['exported_path']}")
        
        # This might fail with invalid font path
        try:
            result = generator.run_workflow(
                text="Bad Font",
                font_path="/nonexistent/font.ttf",
                output_path="examples/output/bad_font.stl"
            )
        except Exception as font_error:
            print(f"⚠️  Expected font error handled: {font_error}")
        
        # This might fail with empty text
        try:
            result = generator.run_workflow(
                text="",
                output_path="examples/output/empty_text.stl"
            )
        except Exception as text_error:
            print(f"⚠️  Expected text error handled: {text_error}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print()


def example_9_step_by_step():
    """
    Example 9: Step-by-step workflow (manual control)
    """
    print("Example 9: Step-by-step workflow")
    print("-" * 40)
    
    try:
        # Initialize generator
        generator = Text3DGenerator()
        
        # Step 1: Load font (optional)
        print("Step 1: Loading font...")
        # Using default font for this example
        
        # Step 2: Process text
        print("Step 2: Processing text...")
        text_data = generator.process_text("Step by Step", spacing=0.5)
        print(f"   Processed {text_data['character_count']} characters")
        
        # Step 3: Generate geometry
        print("Step 3: Generating 3D geometry...")
        geometry_data = generator.generate_geometry(
            text_data, 
            depth=8.0, 
            bevel_depth=1.5
        )
        print(f"   Generated {geometry_data['total_vertices']} vertices")
        
        # Step 4: Export
        print("Step 4: Exporting model...")
        exported_path = generator.export_model(
            geometry_data,
            "examples/output/step_by_step.stl",
            "STL"
        )
        print(f"   Exported to: {exported_path}")
        
        print("✅ Step-by-step workflow completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_10_statistics():
    """
    Example 10: Getting processing statistics
    """
    print("Example 10: Processing statistics")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        result = generator.run_workflow(
            text="Statistics",
            output_path="examples/output/statistics.stl",
            font_size=64,
            extrusion_depth=10.0,
            bevel_depth=2.0
        )
        
        # Get detailed statistics
        stats = result['processing_stats']
        
        print("✅ Processing completed! Statistics:")
        print(f"   Font size: {stats.get('font_size', 'default')}")
        print(f"   Characters: {stats.get('character_count', 0)}")
        print(f"   Text width: {stats.get('total_width', 0):.2f}")
        print(f"   Vertices: {stats.get('vertices', 0)}")
        print(f"   Faces: {stats.get('faces', 0)}")
        print(f"   Extrusion depth: {stats.get('extrusion_depth', 0)}")
        print(f"   Bevel depth: {stats.get('bevel_depth', 0)}")
        print(f"   Export format: {stats.get('export_format', 'N/A')}")
        print(f"   Total time: {stats.get('total_time', 0):.2f} seconds")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def main():
    """
    Run all basic usage examples
    """
    print("3D Text Generator - Basic Usage Examples")
    print("=" * 50)
    print()
    
    # Create output directory
    output_dir = Path("examples/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run all examples
    example_1_simple_text()
    example_2_custom_font()
    example_3_3d_parameters()
    example_4_different_formats()
    example_5_character_spacing()
    example_6_with_preview()
    example_7_scaling()
    example_8_error_handling()
    example_9_step_by_step()
    example_10_statistics()
    
    print("=" * 50)
    print("All basic examples completed!")
    print(f"Check the output directory: {output_dir.absolute()}")
    print()
    print("Next steps:")
    print("- Try advanced_usage.py for more complex examples")
    print("- Check batch_processing.py for processing multiple texts")
    print("- See custom_fonts.py for font-specific examples")


if __name__ == "__main__":
    main()