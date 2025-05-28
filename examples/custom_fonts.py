#!/usr/bin/env python3
"""
Custom Font Usage Examples for 3D Text Generator

This file demonstrates how to work with different fonts and font-related
features in the 3D Text Generator application.
"""

import os
import sys
import platform
from pathlib import Path
from typing import List, Dict, Optional

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import Text3DGenerator
from text_processor import FontLoader


def get_system_fonts() -> List[Path]:
    """
    Get list of common system fonts based on the operating system
    """
    system = platform.system().lower()
    font_paths = []
    
    if system == "windows":
        font_dir = Path("C:/Windows/Fonts")
        if font_dir.exists():
            common_fonts = [
                "arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf",
                "times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf",
                "calibri.ttf", "calibrib.ttf", "calibrii.ttf", "calibriz.ttf",
                "verdana.ttf", "verdanab.ttf", "verdanai.ttf", "verdanaz.ttf",
                "tahoma.ttf", "tahomabd.ttf",
                "comic.ttf", "comicbd.ttf",
                "impact.ttf",
                "georgia.ttf", "georgiab.ttf", "georgiai.ttf", "georgiaz.ttf"
            ]
            font_paths = [font_dir / font for font in common_fonts if (font_dir / font).exists()]
    
    elif system == "darwin":  # macOS
        font_dirs = [
            Path("/System/Library/Fonts"),
            Path("/Library/Fonts"),
            Path.home() / "Library/Fonts"
        ]
        common_fonts = [
            "Arial.ttf", "Arial Bold.ttf", "Arial Italic.ttf", "Arial Bold Italic.ttf",
            "Times New Roman.ttf", "Times New Roman Bold.ttf", "Times New Roman Italic.ttf",
            "Helvetica.ttc", "Helvetica Neue.ttc",
            "Georgia.ttf", "Georgia Bold.ttf", "Georgia Italic.ttf",
            "Verdana.ttf", "Verdana Bold.ttf", "Verdana Italic.ttf",
            "Impact.ttf",
            "Comic Sans MS.ttf", "Comic Sans MS Bold.ttf"
        ]
        for font_dir in font_dirs:
            if font_dir.exists():
                for font in common_fonts:
                    font_path = font_dir / font
                    if font_path.exists():
                        font_paths.append(font_path)
    
    else:  # Linux
        font_dirs = [
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path.home() / ".local/share/fonts"
        ]
        common_fonts = [
            "truetype/dejavu/DejaVuSans.ttf",
            "truetype/dejavu/DejaVuSans-Bold.ttf",
            "truetype/dejavu/DejaVuSans-Oblique.ttf",
            "truetype/dejavu/DejaVuSerif.ttf",
            "truetype/dejavu/DejaVuSerif-Bold.ttf",
            "truetype/liberation/LiberationSans-Regular.ttf",
            "truetype/liberation/LiberationSans-Bold.ttf",
            "truetype/liberation/LiberationSerif-Regular.ttf",
            "truetype/liberation/LiberationMono-Regular.ttf",
            "truetype/ubuntu/Ubuntu-R.ttf",
            "truetype/ubuntu/Ubuntu-B.ttf"
        ]
        for font_dir in font_dirs:
            if font_dir.exists():
                for font in common_fonts:
                    font_path = font_dir / font
                    if font_path.exists():
                        font_paths.append(font_path)
    
    return font_paths


def example_1_system_font_discovery():
    """
    Example 1: Discover and test system fonts
    """
    print("Example 1: System font discovery")
    print("-" * 40)
    
    try:
        system_fonts = get_system_fonts()
        
        if not system_fonts:
            print("   No common system fonts found")
            return
        
        print(f"   Found {len(system_fonts)} system fonts:")
        
        generator = Text3DGenerator()
        successful_fonts = []
        
        for i, font_path in enumerate(system_fonts[:5]):  # Test first 5 fonts
            try:
                print(f"   Testing font {i+1}: {font_path.name}")
                
                result = generator.run_workflow(
                    text="Font Test",
                    font_path=str(font_path),
                    output_path=f"examples/output/fonts_system/font_{i+1:02d}_{font_path.stem}.stl",
                    font_size=48,
                    extrusion_depth=6.0,
                    bevel_depth=1.0
                )
                
                successful_fonts.append({
                    'name': font_path.name,
                    'path': str(font_path),
                    'file': result['exported_path']
                })
                
                print(f"     ✅ Success: {result['exported_path']}")
                
            except Exception as font_error:
                print(f"     ❌ Failed: {font_error}")
        
        print(f"\n✅ System font discovery completed!")
        print(f"   Tested: {min(5, len(system_fonts))} fonts")
        print(f"   Successful: {len(successful_fonts)} fonts")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_2_font_comparison():
    """
    Example 2: Compare different font styles with the same text
    """
    print("Example 2: Font style comparison")
    print("-" * 40)
    
    try:
        # Find available fonts for comparison
        system_fonts = get_system_fonts()
        
        # Try to find different font styles
        font_categories = {
            "serif": ["times", "georgia", "dejavu", "liberation"],
            "sans_serif": ["arial", "helvetica", "verdana", "ubuntu"],
            "monospace": ["courier", "mono", "liberation"],
            "display": ["impact", "comic", "tahoma"]
        }
        
        selected_fonts = {}
        
        for category, keywords in font_categories.items():
            for font_path in system_fonts:
                font_name_lower = font_path.name.lower()
                if any(keyword in font_name_lower for keyword in keywords):
                    if category not in selected_fonts:
                        selected_fonts[category] = font_path
                    break
        
        if not selected_fonts:
            print("   No suitable fonts found for comparison")
            return
        
        generator = Text3DGenerator()
        comparison_text = "Typography"
        
        print(f"   Comparing fonts with text: '{comparison_text}'")
        
        for category, font_path in selected_fonts.items():
            try:
                print(f"   Processing {category}: {font_path.name}")
                
                result = generator.run_workflow(
                    text=comparison_text,
                    font_path=str(font_path),
                    output_path=f"examples/output/fonts_comparison/{category}_{font_path.stem}.stl",
                    font_size=56,
                    extrusion_depth=8.0,
                    bevel_depth=1.5,
                    save_preview=f"examples/output/fonts_comparison/{category}_{font_path.stem}_preview.png"
                )
                
                print(f"     ✅ {category.replace('_', ' ').title()}: {result['exported_path']}")
                
            except Exception as font_error:
                print(f"     ❌ Failed for {category}: {font_error}")
        
        print(f"\n✅ Font comparison completed!")
        print(f"   Compared {len(selected_fonts)} font categories")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_3_font_size_variations():
    """
    Example 3: Test different font sizes with the same font
    """
    print("Example 3: Font size variations")
    print("-" * 40)
    
    try:
        # Find a good font for testing
        system_fonts = get_system_fonts()
        test_font = None
        
        for font_path in system_fonts:
            if "arial" in font_path.name.lower() or "dejavu" in font_path.name.lower():
                test_font = font_path
                break
        
        if not test_font:
            test_font = system_fonts[0] if system_fonts else None
        
        if not test_font:
            print("   No suitable font found for size testing")
            return
        
        print(f"   Testing font sizes with: {test_font.name}")
        
        # Test different font sizes
        font_sizes = [24, 36, 48, 64, 80, 96]
        generator = Text3DGenerator()
        
        for size in font_sizes:
            try:
                print(f"   Processing size {size}pt")
                
                result = generator.run_workflow(
                    text=f"Size {size}",
                    font_path=str(test_font),
                    output_path=f"examples/output/fonts_sizes/size_{size:02d}pt.stl",
                    font_size=size,
                    extrusion_depth=6.0,
                    bevel_depth=1.0
                )
                
                stats = result['processing_stats']
                print(f"     ✅ {size}pt: {stats['vertices']} vertices, {stats['total_time']:.2f}s")
                
            except Exception as size_error:
                print(f"     ❌ Failed for size {size}: {size_error}")
        
        print(f"\n✅ Font size variation testing completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_4_unicode_and_special_characters():
    """
    Example 4: Test Unicode and special characters with different fonts
    """
    print("Example 4: Unicode and special characters")
    print("-" * 40)
    
    try:
        # Test texts with different character sets
        test_cases = [
            ("Basic ASCII", "Hello World 123"),
            ("Accented", "Café Naïve Résumé"),
            ("Symbols", "©®™€£¥$¢"),
            ("Math", "α²+β²=γ² ∑∞∆"),
            ("Arrows", "←↑→↓↔↕⇄⇅"),
            ("Mixed", "Test™ Café → 100€")
        ]
        
        # Find fonts with good Unicode support
        system_fonts = get_system_fonts()
        unicode_fonts = []
        
        for font_path in system_fonts:
            font_name_lower = font_path.name.lower()
            # Fonts known for good Unicode support
            if any(name in font_name_lower for name in ["dejavu", "liberation", "arial", "noto"]):
                unicode_fonts.append(font_path)
        
        if not unicode_fonts:
            unicode_fonts = system_fonts[:2] if system_fonts else []
        
        if not unicode_fonts:
            print("   No suitable Unicode fonts found")
            return
        
        generator = Text3DGenerator()
        
        for font_path in unicode_fonts[:2]:  # Test with first 2 Unicode fonts
            print(f"   Testing with font: {font_path.name}")
            
            for case_name, test_text in test_cases:
                try:
                    print(f"     Processing {case_name}: {test_text}")
                    
                    safe_name = case_name.lower().replace(" ", "_")
                    font_name = font_path.stem.lower().replace(" ", "_")
                    
                    result = generator.run_workflow(
                        text=test_text,
                        font_path=str(font_path),
                        output_path=f"examples/output/fonts_unicode/{font_name}_{safe_name}.stl",
                        font_size=48,
                        extrusion_depth=6.0,
                        bevel_depth=1.0
                    )
                    
                    print(f"       ✅ Success: {result['processing_stats']['character_count']} chars")
                    
                except Exception as char_error:
                    print(f"       ⚠️  Failed: {char_error}")
        
        print(f"\n✅ Unicode character testing completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_5_font_metrics_analysis():
    """
    Example 5: Analyze font metrics and characteristics
    """
    print("Example 5: Font metrics analysis")
    print("-" * 40)
    
    try:
        system_fonts = get_system_fonts()
        
        if not system_fonts:
            print("   No fonts available for analysis")
            return
        
        font_loader = FontLoader()
        font_analysis = []
        
        for font_path in system_fonts[:5]:  # Analyze first 5 fonts
            try:
                print(f"   Analyzing: {font_path.name}")
                
                # Load font
                success = font_loader.load_font(str(font_path), 48)
                if not success:
                    print(f"     ⚠️  Could not load font")
                    continue
                
                # Get font metrics
                metrics = font_loader.get_font_metrics()
                
                # Test character availability
                test_chars = "ABCabc123!@#"
                available_chars = 0
                for char in test_chars:
                    outline = font_loader.get_character_outline(char)
                    if outline:
                        available_chars += 1
                
                analysis = {
                    'name': font_path.name,
                    'path': str(font_path),
                    'metrics': metrics,
                    'character_coverage': f"{available_chars}/{len(test_chars)}",
                    'coverage_percent': (available_chars / len(test_chars)) * 100
                }
                
                font_analysis.append(analysis)
                
                print(f"     ✅ Metrics: height={metrics.get('height', 'N/A')}, "
                      f"ascender={metrics.get('ascender', 'N/A')}, "
                      f"coverage={analysis['coverage_percent']:.1f}%")
                
            except Exception as analysis_error:
                print(f"     ❌ Analysis failed: {analysis_error}")
        
        # Generate comparison models with best fonts
        if font_analysis:
            # Sort by character coverage
            font_analysis.sort(key=lambda x: x['coverage_percent'], reverse=True)
            
            print(f"\n   Generating models with top fonts:")
            generator = Text3DGenerator()
            
            for i, analysis in enumerate(font_analysis[:3]):  # Top 3 fonts
                try:
                    result = generator.run_workflow(
                        text="Font Analysis",
                        font_path=analysis['path'],
                        output_path=f"examples/output/fonts_analysis/analysis_{i+1:02d}_{Path(analysis['path']).stem}.stl",
                        font_size=52,
                        extrusion_depth=8.0,
                        bevel_depth=1.5
                    )
                    
                    print(f"     ✅ Model {i+1}: {analysis['name']} ({analysis['coverage_percent']:.1f}% coverage)")
                    
                except Exception as model_error:
                    print(f"     ❌ Model failed: {model_error}")
        
        print(f"\n✅ Font metrics analysis completed!")
        print(f"   Analyzed {len(font_analysis)} fonts")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_6_custom_font_workflow():
    """
    Example 6: Complete workflow for using custom fonts
    """
    print("Example 6: Custom font workflow")
    print("-" * 40)
    
    try:
        # Simulate custom font workflow
        print("   Custom Font Workflow Steps:")
        print("   1. Font Discovery")
        print("   2. Font Validation")
        print("   3. Character Set Testing")
        print("   4. Parameter Optimization")
        print("   5. Final Model Generation")
        
        system_fonts = get_system_fonts()
        if not system_fonts:
            print("   No fonts available for workflow demonstration")
            return
        
        # Step 1: Font Discovery
        print(f"\n   Step 1: Found {len(system_fonts)} system fonts")
        
        # Step 2: Font Validation
        print("   Step 2: Validating fonts...")
        valid_fonts = []
        font_loader = FontLoader()
        
        for font_path in system_fonts[:3]:  # Test first 3
            try:
                if font_loader.load_font(str(font_path), 48):
                    valid_fonts.append(font_path)
                    print(f"     ✅ Valid: {font_path.name}")
                else:
                    print(f"     ❌ Invalid: {font_path.name}")
            except:
                print(f"     ❌ Error: {font_path.name}")
        
        if not valid_fonts:
            print("   No valid fonts found")
            return
        
        # Step 3: Character Set Testing
        print("   Step 3: Testing character sets...")
        best_font = None
        best_coverage = 0
        
        test_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()"
        
        for font_path in valid_fonts:
            try:
                font_loader.load_font(str(font_path), 48)
                coverage = 0
                
                for char in test_text:
                    outline = font_loader.get_character_outline(char)
                    if outline:
                        coverage += 1
                
                coverage_percent = (coverage / len(test_text)) * 100
                print(f"     {font_path.name}: {coverage_percent:.1f}% coverage")
                
                if coverage_percent > best_coverage:
                    best_coverage = coverage_percent
                    best_font = font_path
                    
            except Exception as test_error:
                print(f"     ❌ Test failed for {font_path.name}: {test_error}")
        
        if not best_font:
            print("   No suitable font found")
            return
        
        print(f"   Best font: {best_font.name} ({best_coverage:.1f}% coverage)")
        
        # Step 4: Parameter Optimization
        print("   Step 4: Optimizing parameters...")
        generator = Text3DGenerator()
        
        # Test different parameter combinations
        param_tests = [
            {"size": 48, "depth": 6.0, "bevel": 1.0, "name": "balanced"},
            {"size": 64, "depth": 10.0, "bevel": 2.0, "name": "high_quality"},
            {"size": 32, "depth": 4.0, "bevel": 0.5, "name": "fast"}
        ]
        
        best_params = None
        best_time = float('inf')
        
        for params in param_tests:
            try:
                import time
                start_time = time.time()
                
                result = generator.run_workflow(
                    text="Param Test",
                    font_path=str(best_font),
                    output_path=f"examples/output/fonts_workflow/param_test_{params['name']}.stl",
                    font_size=params["size"],
                    extrusion_depth=params["depth"],
                    bevel_depth=params["bevel"]
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                print(f"     {params['name']}: {processing_time:.2f}s, {result['processing_stats']['vertices']} vertices")
                
                if processing_time < best_time:
                    best_time = processing_time
                    best_params = params
                    
            except Exception as param_error:
                print(f"     ❌ {params['name']} failed: {param_error}")
        
        # Step 5: Final Model Generation
        print("   Step 5: Generating final model...")
        
        if best_params:
            try:
                final_result = generator.run_workflow(
                    text="Custom Font Workflow",
                    font_path=str(best_font),
                    output_path="examples/output/fonts_workflow/final_model.stl",
                    font_size=best_params["size"],
                    extrusion_depth=best_params["depth"],
                    bevel_depth=best_params["bevel"],
                    save_preview="examples/output/fonts_workflow/final_preview.png"
                )
                
                print(f"     ✅ Final model: {final_result['exported_path']}")
                print(f"     ✅ Preview: {final_result.get('preview_path', 'N/A')}")
                
            except Exception as final_error:
                print(f"     ❌ Final generation failed: {final_error}")
        
        print(f"\n✅ Custom font workflow completed!")
        print(f"   Selected font: {best_font.name}")
        print(f"   Character coverage: {best_coverage:.1f}%")
        if best_params:
            print(f"   Optimal parameters: {best_params['name']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def main():
    """
    Run all custom font examples
    """
    print("3D Text Generator - Custom Font Examples")
    print("=" * 60)
    print()
    
    # Create output directories
    output_dirs = [
        "examples/output/fonts_system",
        "examples/output/fonts_comparison",
        "examples/output/fonts_sizes",
        "examples/output/fonts_unicode",
        "examples/output/fonts_analysis",
        "examples/output/fonts_workflow"
    ]
    
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Run all examples
    example_1_system_font_discovery()
    example_2_font_comparison()
    example_3_font_size_variations()
    example_4_unicode_and_special_characters()
    example_5_font_metrics_analysis()
    example_6_custom_font_workflow()
    
    print("=" * 60)
    print("All custom font examples completed!")
    print("Check the examples/output/fonts_* directories for generated files.")
    print()
    print("Font techniques demonstrated:")
    print("- System font discovery and testing")
    print("- Font style comparison and analysis")
    print("- Font size optimization")
    print("- Unicode and special character support")
    print("- Font metrics analysis")
    print("- Complete custom font workflow")
    print()
    print("Font selection tips:")
    print("- Use fonts with good character coverage")
    print("- Test fonts with your specific text content")
    print("- Consider font style for your use case")
    print("- Optimize font size for performance vs quality")
    print("- Validate fonts before batch processing")


if __name__ == "__main__":
    main()