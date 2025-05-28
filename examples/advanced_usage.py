#!/usr/bin/env python3
"""
Advanced Usage Examples for 3D Text Generator

This file demonstrates advanced usage patterns and complex configurations
for the 3D Text Generator application.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import Text3DGenerator
from config import Config


def example_1_configuration_overrides():
    """
    Example 1: Using configuration overrides
    """
    print("Example 1: Configuration overrides")
    print("-" * 40)
    
    try:
        # Custom configuration overrides
        config_overrides = {
            'DEFAULT_OUTPUT_DIR': Path('examples/output/custom_config'),
            'DEFAULT_FONT_SIZE': 80,
            'DEFAULT_EXTRUSION_DEPTH': 15.0,
            'DEFAULT_BEVEL_DEPTH': 3.0
        }
        
        # Initialize generator with custom config
        generator = Text3DGenerator(config_overrides)
        
        result = generator.run_workflow(
            text="Custom Config",
            output_path="custom_config.stl"
        )
        
        print(f"✅ Success with custom configuration!")
        print(f"   Model: {result['exported_path']}")
        print(f"   Used custom defaults for all parameters")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_2_complex_text_layout():
    """
    Example 2: Complex text with special characters and layout
    """
    print("Example 2: Complex text layout")
    print("-" * 40)
    
    complex_texts = [
        ("Unicode: Café Naïve", "unicode_text.stl"),
        ("Numbers: 123-456-789", "numbers_text.stl"),
        ("Symbols: @#$%&*()", "symbols_text.stl"),
        ("Mixed: Hello123!", "mixed_text.stl")
    ]
    
    try:
        generator = Text3DGenerator()
        
        for text, filename in complex_texts:
            try:
                result = generator.run_workflow(
                    text=text,
                    output_path=f"examples/output/complex/{filename}",
                    font_size=56,
                    character_spacing=0.8,
                    extrusion_depth=8.0,
                    bevel_depth=1.5
                )
                print(f"✅ {text}: {result['exported_path']}")
                
            except Exception as text_error:
                print(f"⚠️  Failed for '{text}': {text_error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_3_performance_optimization():
    """
    Example 3: Performance optimization techniques
    """
    print("Example 3: Performance optimization")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # Test different performance settings
        performance_configs = [
            {
                "name": "High Quality",
                "font_size": 72,
                "extrusion_depth": 15.0,
                "bevel_depth": 3.0,
                "bevel_resolution": 8
            },
            {
                "name": "Balanced",
                "font_size": 48,
                "extrusion_depth": 10.0,
                "bevel_depth": 2.0,
                "bevel_resolution": 4
            },
            {
                "name": "Fast",
                "font_size": 32,
                "extrusion_depth": 5.0,
                "bevel_depth": 0.0,  # No bevel for speed
                "bevel_resolution": 2
            }
        ]
        
        for config in performance_configs:
            start_time = time.time()
            
            result = generator.run_workflow(
                text="Performance",
                output_path=f"examples/output/performance/{config['name'].lower().replace(' ', '_')}.stl",
                font_size=config["font_size"],
                extrusion_depth=config["extrusion_depth"],
                bevel_depth=config["bevel_depth"]
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"✅ {config['name']} mode:")
            print(f"   Time: {processing_time:.2f}s")
            print(f"   Vertices: {result['processing_stats']['vertices']}")
            print(f"   File: {result['exported_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_4_multi_format_export():
    """
    Example 4: Export the same model to multiple formats with different settings
    """
    print("Example 4: Multi-format export")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # Generate the geometry once
        text_data = generator.process_text("Multi Format", spacing=1.0)
        geometry_data = generator.generate_geometry(
            text_data, 
            depth=12.0, 
            bevel_depth=2.5
        )
        
        # Export to different formats with format-specific options
        export_configs = [
            {
                "format": "STL",
                "extension": "stl",
                "options": {"export_scale": 1.0}
            },
            {
                "format": "OBJ", 
                "extension": "obj",
                "options": {"export_scale": 1.0}
            },
            {
                "format": "PLY",
                "extension": "ply", 
                "options": {"export_scale": 1.0}
            },
            {
                "format": "GLTF",
                "extension": "glb",
                "options": {"export_scale": 1.0}
            }
        ]
        
        for config in export_configs:
            exported_path = generator.export_model(
                geometry_data,
                f"examples/output/multi_format/multi_format.{config['extension']}",
                config["format"],
                **config["options"]
            )
            print(f"✅ {config['format']}: {exported_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_5_custom_workflow():
    """
    Example 5: Custom workflow with intermediate processing
    """
    print("Example 5: Custom workflow with intermediate steps")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # Step 1: Process multiple text variants
        text_variants = ["BOLD", "italic", "Normal"]
        all_geometry = []
        
        for i, text in enumerate(text_variants):
            print(f"   Processing variant {i+1}: {text}")
            
            # Process text with different parameters
            text_data = generator.process_text(text, spacing=0.5)
            
            # Generate geometry with variant-specific settings
            if text == "BOLD":
                geometry = generator.generate_geometry(text_data, depth=15.0, bevel_depth=3.0)
            elif text == "italic":
                geometry = generator.generate_geometry(text_data, depth=8.0, bevel_depth=1.0)
            else:
                geometry = generator.generate_geometry(text_data, depth=10.0, bevel_depth=2.0)
            
            all_geometry.append((text, geometry))
        
        # Step 2: Export each variant
        for text, geometry in all_geometry:
            exported_path = generator.export_model(
                geometry,
                f"examples/output/custom_workflow/{text.lower()}.stl",
                "STL"
            )
            print(f"✅ Exported {text}: {exported_path}")
        
        # Step 3: Generate preview for the last one
        preview_path = generator.render_preview(
            all_geometry[-1][1],
            "examples/output/custom_workflow/preview.png"
        )
        if preview_path:
            print(f"✅ Preview saved: {preview_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_6_batch_with_variations():
    """
    Example 6: Batch processing with parameter variations
    """
    print("Example 6: Batch processing with variations")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # Define parameter variations
        variations = [
            {"depth": 5.0, "bevel": 0.5, "size": 32},
            {"depth": 10.0, "bevel": 2.0, "size": 48},
            {"depth": 15.0, "bevel": 3.0, "size": 64},
        ]
        
        base_text = "Variation"
        
        for i, params in enumerate(variations):
            result = generator.run_workflow(
                text=f"{base_text} {i+1}",
                output_path=f"examples/output/variations/variation_{i+1}.stl",
                font_size=params["size"],
                extrusion_depth=params["depth"],
                bevel_depth=params["bevel"]
            )
            
            print(f"✅ Variation {i+1}:")
            print(f"   Size: {params['size']}, Depth: {params['depth']}, Bevel: {params['bevel']}")
            print(f"   File: {result['exported_path']}")
            print(f"   Vertices: {result['processing_stats']['vertices']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_7_error_recovery():
    """
    Example 7: Advanced error handling and recovery
    """
    print("Example 7: Error handling and recovery")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # List of potentially problematic inputs
        test_cases = [
            {"text": "Good Text", "font_size": 48, "should_work": True},
            {"text": "", "font_size": 48, "should_work": False},  # Empty text
            {"text": "Too Big", "font_size": 1000, "should_work": False},  # Invalid size
            {"text": "Negative", "font_size": 48, "extrusion_depth": -5, "should_work": False},  # Invalid depth
            {"text": "Recovery", "font_size": 48, "should_work": True},  # Should work after errors
        ]
        
        successful_exports = []
        
        for i, case in enumerate(test_cases):
            try:
                print(f"   Testing case {i+1}: {case['text']}")
                
                result = generator.run_workflow(
                    text=case["text"],
                    output_path=f"examples/output/error_recovery/case_{i+1}.stl",
                    font_size=case.get("font_size", 48),
                    extrusion_depth=case.get("extrusion_depth", 10.0)
                )
                
                successful_exports.append(result['exported_path'])
                print(f"   ✅ Success: {result['exported_path']}")
                
            except Exception as case_error:
                if case["should_work"]:
                    print(f"   ❌ Unexpected failure: {case_error}")
                else:
                    print(f"   ⚠️  Expected failure handled: {case_error}")
        
        print(f"\n✅ Error recovery test completed!")
        print(f"   Successful exports: {len(successful_exports)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_8_memory_management():
    """
    Example 8: Memory management for large texts
    """
    print("Example 8: Memory management")
    print("-" * 40)
    
    try:
        # Test with progressively larger texts
        text_sizes = [
            ("Small", "ABC", 64),
            ("Medium", "Hello World 123", 48),
            ("Large", "This is a much longer text string for testing", 32),
        ]
        
        for name, text, font_size in text_sizes:
            try:
                generator = Text3DGenerator()
                
                start_time = time.time()
                result = generator.run_workflow(
                    text=text,
                    output_path=f"examples/output/memory/{name.lower()}.stl",
                    font_size=font_size,
                    extrusion_depth=8.0,
                    bevel_depth=1.0
                )
                end_time = time.time()
                
                stats = result['processing_stats']
                print(f"✅ {name} text ({len(text)} chars):")
                print(f"   Time: {end_time - start_time:.2f}s")
                print(f"   Vertices: {stats['vertices']}")
                print(f"   Memory efficient processing completed")
                
                # Reset generator to free memory
                generator.reset()
                
            except Exception as size_error:
                print(f"⚠️  {name} text failed: {size_error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_9_configuration_profiles():
    """
    Example 9: Using configuration profiles for different use cases
    """
    print("Example 9: Configuration profiles")
    print("-" * 40)
    
    try:
        # Define profiles for different use cases
        profiles = {
            "3d_printing": {
                "font_size": 48,
                "extrusion_depth": 3.0,
                "bevel_depth": 0.5,
                "export_format": "STL",
                "export_scale": 1.0
            },
            "visualization": {
                "font_size": 72,
                "extrusion_depth": 15.0,
                "bevel_depth": 3.0,
                "export_format": "OBJ",
                "export_scale": 1.0
            },
            "web_display": {
                "font_size": 56,
                "extrusion_depth": 8.0,
                "bevel_depth": 2.0,
                "export_format": "GLTF",
                "export_scale": 0.1
            }
        }
        
        for profile_name, settings in profiles.items():
            generator = Text3DGenerator()
            
            result = generator.run_workflow(
                text=f"Profile {profile_name.replace('_', ' ').title()}",
                output_path=f"examples/output/profiles/{profile_name}.{settings['export_format'].lower()}",
                **settings
            )
            
            print(f"✅ {profile_name.replace('_', ' ').title()} profile:")
            print(f"   Format: {settings['export_format']}")
            print(f"   Scale: {settings['export_scale']}")
            print(f"   File: {result['exported_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_10_workflow_statistics():
    """
    Example 10: Comprehensive workflow statistics and analysis
    """
    print("Example 10: Workflow statistics and analysis")
    print("-" * 40)
    
    try:
        generator = Text3DGenerator()
        
        # Generate a complex model with full statistics
        result = generator.run_workflow(
            text="Statistics Analysis",
            output_path="examples/output/statistics/analysis.stl",
            font_size=64,
            character_spacing=1.2,
            extrusion_depth=12.0,
            bevel_depth=2.5,
            export_scale=1.5,
            save_preview="examples/output/statistics/analysis_preview.png"
        )
        
        # Analyze and display comprehensive statistics
        stats = result['processing_stats']
        
        print("✅ Comprehensive Statistics:")
        print(f"   Text Analysis:")
        print(f"     - Characters: {stats.get('character_count', 0)}")
        print(f"     - Text width: {stats.get('total_width', 0):.2f}")
        print(f"     - Font size: {stats.get('font_size', 'default')}")
        
        print(f"   Geometry Analysis:")
        print(f"     - Vertices: {stats.get('vertices', 0):,}")
        print(f"     - Faces: {stats.get('faces', 0):,}")
        print(f"     - Extrusion depth: {stats.get('extrusion_depth', 0)}")
        print(f"     - Bevel depth: {stats.get('bevel_depth', 0)}")
        
        print(f"   Export Analysis:")
        print(f"     - Format: {stats.get('export_format', 'N/A')}")
        print(f"     - File: {stats.get('export_path', 'N/A')}")
        
        print(f"   Performance Analysis:")
        print(f"     - Total time: {stats.get('total_time', 0):.2f} seconds")
        
        # Calculate complexity metrics
        if stats.get('vertices', 0) > 0 and stats.get('total_time', 0) > 0:
            vertices_per_second = stats['vertices'] / stats['total_time']
            print(f"     - Processing rate: {vertices_per_second:.0f} vertices/second")
        
        # Save statistics to JSON file
        stats_file = "examples/output/statistics/analysis_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        print(f"   Statistics saved to: {stats_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def main():
    """
    Run all advanced usage examples
    """
    print("3D Text Generator - Advanced Usage Examples")
    print("=" * 60)
    print()
    
    # Create output directories
    output_dirs = [
        "examples/output/custom_config",
        "examples/output/complex",
        "examples/output/performance", 
        "examples/output/multi_format",
        "examples/output/custom_workflow",
        "examples/output/variations",
        "examples/output/error_recovery",
        "examples/output/memory",
        "examples/output/profiles",
        "examples/output/statistics"
    ]
    
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Run all examples
    example_1_configuration_overrides()
    example_2_complex_text_layout()
    example_3_performance_optimization()
    example_4_multi_format_export()
    example_5_custom_workflow()
    example_6_batch_with_variations()
    example_7_error_recovery()
    example_8_memory_management()
    example_9_configuration_profiles()
    example_10_workflow_statistics()
    
    print("=" * 60)
    print("All advanced examples completed!")
    print("Check the examples/output/ directory for generated files.")
    print()
    print("Advanced techniques demonstrated:")
    print("- Configuration overrides and profiles")
    print("- Complex text and Unicode handling")
    print("- Performance optimization strategies")
    print("- Multi-format export workflows")
    print("- Custom processing pipelines")
    print("- Error handling and recovery")
    print("- Memory management for large texts")
    print("- Comprehensive statistics and analysis")


if __name__ == "__main__":
    main()