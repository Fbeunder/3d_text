#!/usr/bin/env python3
"""
Batch Processing Examples for 3D Text Generator

This file demonstrates how to process multiple texts efficiently
using the 3D Text Generator application.
"""

import os
import sys
import csv
import json
import time
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import Text3DGenerator


def example_1_simple_batch():
    """
    Example 1: Simple batch processing of multiple texts
    """
    print("Example 1: Simple batch processing")
    print("-" * 40)
    
    try:
        # List of texts to process
        texts = [
            "Hello",
            "World", 
            "Batch",
            "Processing",
            "Example"
        ]
        
        generator = Text3DGenerator()
        results = []
        
        for i, text in enumerate(texts):
            print(f"   Processing {i+1}/{len(texts)}: {text}")
            
            result = generator.run_workflow(
                text=text,
                output_path=f"examples/output/batch_simple/text_{i+1:02d}_{text.lower()}.stl",
                font_size=48,
                extrusion_depth=8.0,
                bevel_depth=1.5
            )
            
            results.append({
                'text': text,
                'file': result['exported_path'],
                'vertices': result['processing_stats']['vertices'],
                'time': result['processing_stats']['total_time']
            })
        
        # Summary
        total_time = sum(r['time'] for r in results)
        total_vertices = sum(r['vertices'] for r in results)
        
        print(f"\n✅ Batch processing completed!")
        print(f"   Processed: {len(results)} texts")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Total vertices: {total_vertices:,}")
        print(f"   Average time per text: {total_time/len(results):.2f} seconds")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_2_batch_with_different_parameters():
    """
    Example 2: Batch processing with different parameters for each text
    """
    print("Example 2: Batch with different parameters")
    print("-" * 40)
    
    try:
        # Define texts with individual parameters
        batch_configs = [
            {
                "text": "TITLE",
                "font_size": 72,
                "extrusion_depth": 15.0,
                "bevel_depth": 3.0,
                "format": "STL"
            },
            {
                "text": "Subtitle",
                "font_size": 56,
                "extrusion_depth": 10.0,
                "bevel_depth": 2.0,
                "format": "OBJ"
            },
            {
                "text": "body text",
                "font_size": 40,
                "extrusion_depth": 6.0,
                "bevel_depth": 1.0,
                "format": "PLY"
            },
            {
                "text": "footnote",
                "font_size": 32,
                "extrusion_depth": 4.0,
                "bevel_depth": 0.5,
                "format": "GLTF"
            }
        ]
        
        generator = Text3DGenerator()
        
        for i, config in enumerate(batch_configs):
            print(f"   Processing {i+1}/{len(batch_configs)}: {config['text']}")
            
            extension = config['format'].lower()
            if extension == 'gltf':
                extension = 'glb'
            
            result = generator.run_workflow(
                text=config["text"],
                output_path=f"examples/output/batch_params/{config['text'].replace(' ', '_').lower()}.{extension}",
                font_size=config["font_size"],
                extrusion_depth=config["extrusion_depth"],
                bevel_depth=config["bevel_depth"],
                export_format=config["format"]
            )
            
            print(f"     ✅ {config['format']}: {result['exported_path']}")
        
        print(f"\n✅ Parametric batch processing completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_3_batch_from_csv():
    """
    Example 3: Batch processing from CSV file
    """
    print("Example 3: Batch processing from CSV")
    print("-" * 40)
    
    try:
        # Create sample CSV file
        csv_file = "examples/output/batch_csv/batch_input.csv"
        Path(csv_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Sample data
        csv_data = [
            ["text", "font_size", "depth", "bevel", "format", "output_name"],
            ["Logo Text", "64", "12", "2.5", "STL", "logo"],
            ["Sign Text", "72", "15", "3.0", "OBJ", "sign"],
            ["Label", "48", "8", "1.5", "PLY", "label"],
            ["Badge", "56", "10", "2.0", "GLTF", "badge"]
        ]
        
        # Write CSV file
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
        
        print(f"   Created CSV file: {csv_file}")
        
        # Read and process CSV
        generator = Text3DGenerator()
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader):
                print(f"   Processing row {i+1}: {row['text']}")
                
                extension = row['format'].lower()
                if extension == 'gltf':
                    extension = 'glb'
                
                result = generator.run_workflow(
                    text=row["text"],
                    output_path=f"examples/output/batch_csv/{row['output_name']}.{extension}",
                    font_size=int(row["font_size"]),
                    extrusion_depth=float(row["depth"]),
                    bevel_depth=float(row["bevel"]),
                    export_format=row["format"]
                )
                
                print(f"     ✅ Exported: {result['exported_path']}")
        
        print(f"\n✅ CSV batch processing completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_4_parallel_processing():
    """
    Example 4: Parallel batch processing for better performance
    """
    print("Example 4: Parallel batch processing")
    print("-" * 40)
    
    def process_single_text(args: Tuple[str, Dict]) -> Dict:
        """Process a single text with given parameters"""
        text, params = args
        
        try:
            generator = Text3DGenerator()
            
            result = generator.run_workflow(
                text=text,
                output_path=params["output_path"],
                font_size=params.get("font_size", 48),
                extrusion_depth=params.get("extrusion_depth", 8.0),
                bevel_depth=params.get("bevel_depth", 1.5),
                export_format=params.get("export_format", "STL")
            )
            
            return {
                'text': text,
                'success': True,
                'file': result['exported_path'],
                'vertices': result['processing_stats']['vertices'],
                'time': result['processing_stats']['total_time']
            }
            
        except Exception as e:
            return {
                'text': text,
                'success': False,
                'error': str(e),
                'file': None,
                'vertices': 0,
                'time': 0
            }
    
    try:
        # Define batch job
        batch_jobs = [
            ("Parallel 1", {"output_path": "examples/output/batch_parallel/parallel_1.stl"}),
            ("Parallel 2", {"output_path": "examples/output/batch_parallel/parallel_2.stl"}),
            ("Parallel 3", {"output_path": "examples/output/batch_parallel/parallel_3.stl"}),
            ("Parallel 4", {"output_path": "examples/output/batch_parallel/parallel_4.stl"}),
            ("Parallel 5", {"output_path": "examples/output/batch_parallel/parallel_5.stl"}),
        ]
        
        # Create output directory
        Path("examples/output/batch_parallel").mkdir(parents=True, exist_ok=True)
        
        # Process in parallel
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            print(f"   Starting parallel processing with {executor._max_workers} workers...")
            
            # Submit all jobs
            future_to_text = {
                executor.submit(process_single_text, job): job[0] 
                for job in batch_jobs
            }
            
            results = []
            for future in concurrent.futures.as_completed(future_to_text):
                text = future_to_text[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        print(f"   ✅ Completed: {result['text']} ({result['vertices']} vertices)")
                    else:
                        print(f"   ❌ Failed: {result['text']} - {result['error']}")
                        
                except Exception as exc:
                    print(f"   ❌ Exception for {text}: {exc}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Summary
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n✅ Parallel processing completed!")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")
        
        if successful:
            avg_time = sum(r['time'] for r in successful) / len(successful)
            total_vertices = sum(r['vertices'] for r in successful)
            print(f"   Average processing time: {avg_time:.2f} seconds")
            print(f"   Total vertices: {total_vertices:,}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_5_batch_with_error_handling():
    """
    Example 5: Robust batch processing with comprehensive error handling
    """
    print("Example 5: Batch with error handling")
    print("-" * 40)
    
    try:
        # Mix of valid and problematic inputs
        batch_items = [
            {"text": "Good Text 1", "font_size": 48, "valid": True},
            {"text": "", "font_size": 48, "valid": False},  # Empty text
            {"text": "Good Text 2", "font_size": 56, "valid": True},
            {"text": "Bad Size", "font_size": -10, "valid": False},  # Invalid size
            {"text": "Good Text 3", "font_size": 64, "valid": True},
            {"text": "Bad Depth", "font_size": 48, "extrusion_depth": -5, "valid": False},  # Invalid depth
            {"text": "Good Text 4", "font_size": 40, "valid": True},
        ]
        
        generator = Text3DGenerator()
        successful_exports = []
        failed_exports = []
        
        for i, item in enumerate(batch_items):
            print(f"   Processing {i+1}/{len(batch_items)}: {item['text'] or 'Empty'}")
            
            try:
                result = generator.run_workflow(
                    text=item["text"],
                    output_path=f"examples/output/batch_errors/item_{i+1:02d}.stl",
                    font_size=item.get("font_size", 48),
                    extrusion_depth=item.get("extrusion_depth", 8.0),
                    bevel_depth=1.5
                )
                
                successful_exports.append({
                    'index': i+1,
                    'text': item["text"],
                    'file': result['exported_path'],
                    'expected': item["valid"]
                })
                
                print(f"     ✅ Success: {result['exported_path']}")
                
            except Exception as item_error:
                failed_exports.append({
                    'index': i+1,
                    'text': item["text"],
                    'error': str(item_error),
                    'expected': not item["valid"]
                })
                
                if item["valid"]:
                    print(f"     ❌ Unexpected failure: {item_error}")
                else:
                    print(f"     ⚠️  Expected failure: {item_error}")
        
        # Generate error report
        report = {
            'total_items': len(batch_items),
            'successful': len(successful_exports),
            'failed': len(failed_exports),
            'expected_failures': len([f for f in failed_exports if f['expected']]),
            'unexpected_failures': len([f for f in failed_exports if not f['expected']]),
            'successful_exports': successful_exports,
            'failed_exports': failed_exports
        }
        
        # Save report
        report_file = "examples/output/batch_errors/error_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Error handling batch completed!")
        print(f"   Total items: {report['total_items']}")
        print(f"   Successful: {report['successful']}")
        print(f"   Failed: {report['failed']}")
        print(f"   Expected failures: {report['expected_failures']}")
        print(f"   Unexpected failures: {report['unexpected_failures']}")
        print(f"   Report saved: {report_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_6_batch_with_progress_tracking():
    """
    Example 6: Batch processing with detailed progress tracking
    """
    print("Example 6: Batch with progress tracking")
    print("-" * 40)
    
    try:
        # Large batch for progress demonstration
        texts = [f"Item {i:03d}" for i in range(1, 21)]  # 20 items
        
        generator = Text3DGenerator()
        progress_data = []
        
        print(f"   Processing {len(texts)} items...")
        print("   Progress: [", end="", flush=True)
        
        for i, text in enumerate(texts):
            start_time = time.time()
            
            try:
                result = generator.run_workflow(
                    text=text,
                    output_path=f"examples/output/batch_progress/item_{i+1:03d}.stl",
                    font_size=32,  # Smaller for faster processing
                    extrusion_depth=5.0,
                    bevel_depth=0.5
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                progress_data.append({
                    'item': i+1,
                    'text': text,
                    'success': True,
                    'time': processing_time,
                    'vertices': result['processing_stats']['vertices'],
                    'file': result['exported_path']
                })
                
                # Update progress bar
                if (i + 1) % (len(texts) // 20) == 0 or i == len(texts) - 1:
                    print("█", end="", flush=True)
                
            except Exception as item_error:
                progress_data.append({
                    'item': i+1,
                    'text': text,
                    'success': False,
                    'error': str(item_error),
                    'time': 0,
                    'vertices': 0,
                    'file': None
                })
                print("X", end="", flush=True)
        
        print("] Done!")
        
        # Calculate statistics
        successful = [p for p in progress_data if p['success']]
        total_time = sum(p['time'] for p in successful)
        total_vertices = sum(p['vertices'] for p in successful)
        avg_time = total_time / len(successful) if successful else 0
        
        # Save progress report
        progress_report = {
            'summary': {
                'total_items': len(texts),
                'successful': len(successful),
                'failed': len(progress_data) - len(successful),
                'total_time': total_time,
                'average_time': avg_time,
                'total_vertices': total_vertices
            },
            'details': progress_data
        }
        
        report_file = "examples/output/batch_progress/progress_report.json"
        with open(report_file, 'w') as f:
            json.dump(progress_report, f, indent=2)
        
        print(f"\n✅ Progress tracking batch completed!")
        print(f"   Items processed: {len(successful)}/{len(texts)}")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Average time per item: {avg_time:.2f} seconds")
        print(f"   Total vertices: {total_vertices:,}")
        print(f"   Progress report: {report_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def example_7_batch_optimization():
    """
    Example 7: Optimized batch processing with resource management
    """
    print("Example 7: Optimized batch processing")
    print("-" * 40)
    
    try:
        # Test different batch sizes for optimization
        batch_sizes = [1, 3, 5]
        test_texts = [f"Opt {i}" for i in range(1, 16)]  # 15 items
        
        for batch_size in batch_sizes:
            print(f"   Testing batch size: {batch_size}")
            
            start_time = time.time()
            processed = 0
            
            # Process in batches
            for i in range(0, len(test_texts), batch_size):
                batch = test_texts[i:i+batch_size]
                
                # Use single generator instance for the batch
                generator = Text3DGenerator()
                
                for j, text in enumerate(batch):
                    try:
                        result = generator.run_workflow(
                            text=text,
                            output_path=f"examples/output/batch_opt/batch_{batch_size}/item_{i+j+1:02d}.stl",
                            font_size=32,
                            extrusion_depth=4.0,
                            bevel_depth=0.0  # No bevel for speed
                        )
                        processed += 1
                        
                    except Exception as item_error:
                        print(f"     ⚠️  Failed: {text} - {item_error}")
                
                # Reset generator to free memory
                generator.reset()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"     Processed: {processed}/{len(test_texts)} items")
            print(f"     Time: {total_time:.2f} seconds")
            print(f"     Rate: {processed/total_time:.1f} items/second")
        
        print(f"\n✅ Batch optimization testing completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def main():
    """
    Run all batch processing examples
    """
    print("3D Text Generator - Batch Processing Examples")
    print("=" * 60)
    print()
    
    # Create output directories
    output_dirs = [
        "examples/output/batch_simple",
        "examples/output/batch_params",
        "examples/output/batch_csv",
        "examples/output/batch_parallel",
        "examples/output/batch_errors",
        "examples/output/batch_progress",
        "examples/output/batch_opt/batch_1",
        "examples/output/batch_opt/batch_3",
        "examples/output/batch_opt/batch_5"
    ]
    
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Run all examples
    example_1_simple_batch()
    example_2_batch_with_different_parameters()
    example_3_batch_from_csv()
    example_4_parallel_processing()
    example_5_batch_with_error_handling()
    example_6_batch_with_progress_tracking()
    example_7_batch_optimization()
    
    print("=" * 60)
    print("All batch processing examples completed!")
    print("Check the examples/output/batch_* directories for generated files.")
    print()
    print("Batch processing techniques demonstrated:")
    print("- Simple sequential batch processing")
    print("- Parameter variation across batches")
    print("- CSV-driven batch processing")
    print("- Parallel processing for performance")
    print("- Comprehensive error handling")
    print("- Progress tracking and reporting")
    print("- Resource optimization strategies")
    print()
    print("Use these patterns for:")
    print("- Processing large text datasets")
    print("- Automated 3D text generation")
    print("- Production workflows")
    print("- Performance optimization")


if __name__ == "__main__":
    main()