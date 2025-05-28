#!/usr/bin/env python3
"""
3D Text Generator - Main Application

Command-line interface and workflow orchestration for converting
2D text to 3D models with various export options.
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

# Import core modules
from text_processor import FontLoader, TextProcessor, FontLoadError, TextProcessingError
from geometry_generator import GeometryGenerator, GeometryError, MeshValidationError
from renderer import Renderer, Camera, Light, RenderingError
from exporter import Exporter, ExportError
from config import Config, get_text_config, get_3d_config, get_export_config
from utils import (
    setup_logging, ensure_directory_exists, validate_file_path,
    safe_filename, get_unique_filename, measure_time
)


class Text3DGeneratorError(Exception):
    """Base exception for 3D Text Generator application."""
    pass


class WorkflowError(Exception):
    """Exception raised when workflow execution fails."""
    pass


class Text3DGenerator:
    """
    Main application class that orchestrates the 3D text generation workflow.
    """
    
    def __init__(self, config_overrides: Optional[Dict[str, Any]] = None):
        """
        Initialize the 3D Text Generator.
        
        Args:
            config_overrides: Optional configuration overrides
        """
        self.config = Config()
        self.config_overrides = config_overrides or {}
        
        # Initialize core components
        self.font_loader = FontLoader()
        self.text_processor = TextProcessor(self.font_loader)
        self.geometry_generator = GeometryGenerator()
        self.renderer = Renderer()
        self.exporter = Exporter()
        
        # Workflow state
        self.current_text = None
        self.current_mesh = None
        self.current_layout = None
        self.processing_stats = {}
        
        # Apply configuration overrides
        self._apply_config_overrides()
    
    def _apply_config_overrides(self):
        """Apply configuration overrides from command line or other sources."""
        for key, value in self.config_overrides.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logging.debug(f"Applied config override: {key} = {value}")
    
    @measure_time
    def load_font(self, font_path: str, font_size: Optional[int] = None) -> bool:
        """
        Load a font file for text processing.
        
        Args:
            font_path: Path to the font file
            font_size: Optional font size override
            
        Returns:
            True if font loaded successfully
            
        Raises:
            FontLoadError: If font loading fails
        """
        try:
            if not validate_file_path(font_path):
                # Try to find default font if path is invalid
                default_font = self.config.get_default_font_path()
                if default_font:
                    logging.warning(f"Font {font_path} not found, using default: {default_font}")
                    font_path = str(default_font)
                else:
                    raise FontLoadError(f"Font file not found: {font_path}")
            
            size = font_size or self.config.DEFAULT_FONT_SIZE
            if not self.config.validate_font_size(size):
                raise FontLoadError(f"Invalid font size: {size}")
            
            success = self.font_loader.load_font(font_path, size)
            if success:
                logging.info(f"Font loaded successfully: {font_path} (size: {size})")
                self.processing_stats['font_path'] = font_path
                self.processing_stats['font_size'] = size
            
            return success
            
        except Exception as e:
            raise FontLoadError(f"Failed to load font: {str(e)}")
    
    @measure_time
    def process_text(self, text: str, spacing: Optional[float] = None) -> Dict:
        """
        Process input text and calculate layout.
        
        Args:
            text: Input text to process
            spacing: Optional character spacing override
            
        Returns:
            Dictionary with text processing results
            
        Raises:
            TextProcessingError: If text processing fails
        """
        try:
            if not text or not text.strip():
                raise TextProcessingError("Empty text provided")
            
            # Parse and validate text
            parsed_text = self.text_processor.parse_text(text)
            logging.info(f"Processing text: '{parsed_text}' ({len(parsed_text)} characters)")
            
            # Calculate layout
            char_spacing = spacing or self.config.DEFAULT_CHARACTER_SPACING
            layout = self.text_processor.calculate_layout(parsed_text, char_spacing)
            
            # Get character outlines
            outlines = self.text_processor.get_text_outlines(parsed_text)
            
            # Store results
            self.current_text = parsed_text
            self.current_layout = layout
            
            results = {
                'text': parsed_text,
                'layout': layout,
                'outlines': outlines,
                'character_count': len([c for c in layout if c['character'] != ' ']),
                'total_width': max([c['position'][0] + c.get('width', 0) for c in layout], default=0)
            }
            
            self.processing_stats.update({
                'character_count': results['character_count'],
                'total_width': results['total_width']
            })
            
            logging.info(f"Text processed: {results['character_count']} characters, "
                        f"width: {results['total_width']:.2f}")
            
            return results
            
        except Exception as e:
            raise TextProcessingError(f"Failed to process text: {str(e)}")
    
    @measure_time
    def generate_geometry(self, text_data: Dict, depth: Optional[float] = None,
                         bevel_depth: Optional[float] = None) -> Dict:
        """
        Generate 3D geometry from text data.
        
        Args:
            text_data: Text processing results
            depth: Optional extrusion depth override
            bevel_depth: Optional bevel depth override
            
        Returns:
            Dictionary with geometry generation results
            
        Raises:
            GeometryError: If geometry generation fails
        """
        try:
            outlines = text_data.get('outlines', {})
            layout = text_data.get('layout', [])
            
            if not outlines:
                raise GeometryError("No character outlines available")
            
            extrusion_depth = depth or self.config.DEFAULT_EXTRUSION_DEPTH
            if not self.config.validate_extrusion_depth(extrusion_depth):
                raise GeometryError(f"Invalid extrusion depth: {extrusion_depth}")
            
            bevel = bevel_depth or self.config.DEFAULT_BEVEL_DEPTH
            
            logging.info(f"Generating 3D geometry (depth: {extrusion_depth}, bevel: {bevel})")
            
            # Generate meshes for each character
            all_meshes = []
            total_vertices = 0
            total_faces = 0
            
            for char_info in layout:
                char = char_info['character']
                position = char_info['position']
                
                if char in outlines and outlines[char]:
                    # Translate outlines to character position
                    translated_outlines = []
                    for outline in outlines[char]:
                        translated_outline = [(x + position[0], y + position[1]) for x, y in outline]
                        translated_outlines.append(translated_outline)
                    
                    # Generate mesh for this character
                    char_mesh = self.geometry_generator.generate_mesh(
                        translated_outlines, extrusion_depth, bevel
                    )
                    
                    all_meshes.append(char_mesh)
                    total_vertices += len(char_mesh['vertices'])
                    total_faces += len(char_mesh['faces'])
            
            if not all_meshes:
                raise GeometryError("No valid geometry generated")
            
            # Combine all character meshes
            combined_mesh = self._combine_meshes(all_meshes)
            self.current_mesh = combined_mesh
            
            results = {
                'mesh': combined_mesh,
                'character_meshes': len(all_meshes),
                'total_vertices': total_vertices,
                'total_faces': total_faces,
                'bounds': self._calculate_mesh_bounds(combined_mesh)
            }
            
            self.processing_stats.update({
                'vertices': total_vertices,
                'faces': total_faces,
                'extrusion_depth': extrusion_depth,
                'bevel_depth': bevel
            })
            
            logging.info(f"Geometry generated: {total_vertices} vertices, {total_faces} faces")
            
            return results
            
        except Exception as e:
            raise GeometryError(f"Failed to generate geometry: {str(e)}")
    
    def _combine_meshes(self, meshes: List[Dict]) -> Dict:
        """Combine multiple meshes into a single mesh."""
        if not meshes:
            raise GeometryError("No meshes to combine")
        
        if len(meshes) == 1:
            return meshes[0]
        
        all_vertices = []
        all_faces = []
        vertex_offset = 0
        
        for mesh in meshes:
            vertices = mesh['vertices']
            faces = mesh['faces']
            
            # Add vertices
            all_vertices.extend(vertices)
            
            # Add faces with vertex offset
            offset_faces = []
            for face in faces:
                offset_face = [idx + vertex_offset for idx in face]
                offset_faces.append(offset_face)
            all_faces.extend(offset_faces)
            
            vertex_offset += len(vertices)
        
        # Calculate combined normals
        normals = self.geometry_generator.calculate_normals(all_vertices, all_faces)
        
        return {
            'vertices': all_vertices,
            'faces': all_faces,
            'normals': normals
        }
    
    def _calculate_mesh_bounds(self, mesh: Dict) -> Dict:
        """Calculate bounding box of a mesh."""
        vertices = mesh.get('vertices', [])
        if not vertices:
            return {'min': (0, 0, 0), 'max': (0, 0, 0), 'size': (0, 0, 0)}
        
        import numpy as np
        vertices = np.array(vertices)
        
        min_bounds = tuple(np.min(vertices, axis=0))
        max_bounds = tuple(np.max(vertices, axis=0))
        size = tuple(np.array(max_bounds) - np.array(min_bounds))
        
        return {
            'min': min_bounds,
            'max': max_bounds,
            'size': size
        }
    
    @measure_time
    def render_preview(self, geometry_data: Dict, output_path: Optional[str] = None,
                      show_preview: bool = False) -> Optional[str]:
        """
        Render a preview of the 3D geometry.
        
        Args:
            geometry_data: Geometry generation results
            output_path: Optional output path for preview image
            show_preview: Whether to show interactive preview
            
        Returns:
            Path to saved preview image or None
            
        Raises:
            RenderingError: If rendering fails
        """
        try:
            mesh = geometry_data.get('mesh')
            if not mesh:
                raise RenderingError("No mesh data available for rendering")
            
            logging.info("Rendering 3D preview...")
            
            # Setup camera
            bounds = geometry_data.get('bounds', {})
            if bounds:
                # Position camera based on mesh bounds
                size = bounds.get('size', (10, 10, 10))
                max_dimension = max(size)
                camera_distance = max_dimension * 2
                
                camera = Camera()
                camera.set_position(camera_distance, camera_distance, camera_distance)
                camera.look_at((0, 0, 0))
                self.renderer.set_camera(camera)
            
            # Setup lighting
            light = Light()
            light.set_position(10, 10, 10)
            self.renderer.add_light(light)
            
            # Render the mesh
            if show_preview:
                self.renderer.render_interactive(mesh)
            
            # Save preview image if requested
            if output_path:
                preview_path = self.renderer.render_to_image(mesh, output_path)
                logging.info(f"Preview saved to: {preview_path}")
                return preview_path
            
            return None
            
        except Exception as e:
            raise RenderingError(f"Failed to render preview: {str(e)}")
    
    @measure_time
    def export_model(self, geometry_data: Dict, output_path: str,
                    export_format: str = 'STL', **export_options) -> str:
        """
        Export the 3D model to a file.
        
        Args:
            geometry_data: Geometry generation results
            output_path: Output file path
            export_format: Export format (STL, OBJ, PLY, GLTF)
            **export_options: Additional export options
            
        Returns:
            Path to exported file
            
        Raises:
            ExportError: If export fails
        """
        try:
            mesh = geometry_data.get('mesh')
            if not mesh:
                raise ExportError("No mesh data available for export")
            
            # Validate export format
            format_upper = export_format.upper()
            if not self.config.validate_export_format(format_upper):
                raise ExportError(f"Unsupported export format: {export_format}")
            
            # Ensure output directory exists
            output_path = Path(output_path)
            ensure_directory_exists(output_path.parent)
            
            # Make filename safe
            safe_name = safe_filename(output_path.stem)
            output_path = output_path.parent / f"{safe_name}{output_path.suffix}"
            
            # Get unique filename if file exists
            if output_path.exists():
                output_path = get_unique_filename(
                    output_path.parent, 
                    output_path.stem, 
                    output_path.suffix
                )
            
            logging.info(f"Exporting to {format_upper}: {output_path}")
            
            # Export the mesh
            exported_path = self.exporter.export_mesh(
                mesh, str(output_path), format_upper, **export_options
            )
            
            self.processing_stats['export_path'] = exported_path
            self.processing_stats['export_format'] = format_upper
            
            logging.info(f"Model exported successfully: {exported_path}")
            
            return exported_path
            
        except Exception as e:
            raise ExportError(f"Failed to export model: {str(e)}")
    
    def run_workflow(self, text: str, font_path: Optional[str] = None,
                    output_path: Optional[str] = None, **options) -> Dict:
        """
        Run the complete 3D text generation workflow.
        
        Args:
            text: Input text to convert
            font_path: Optional font file path
            output_path: Optional output file path
            **options: Additional workflow options
            
        Returns:
            Dictionary with workflow results
            
        Raises:
            WorkflowError: If workflow execution fails
        """
        try:
            workflow_start = time.time()
            results = {}
            
            logging.info("Starting 3D text generation workflow...")
            
            # Step 1: Load font
            if font_path:
                self.load_font(font_path, options.get('font_size'))
            elif not self.font_loader.font and not self.font_loader._face:
                # Try to load default font
                default_font = self.config.get_default_font_path()
                if default_font:
                    self.load_font(str(default_font), options.get('font_size'))
                else:
                    logging.warning("No font specified and no default font found")
            
            # Step 2: Process text
            text_data = self.process_text(text, options.get('character_spacing'))
            results['text_processing'] = text_data
            
            # Step 3: Generate geometry
            geometry_data = self.generate_geometry(
                text_data,
                options.get('extrusion_depth'),
                options.get('bevel_depth')
            )
            results['geometry_generation'] = geometry_data
            
            # Step 4: Render preview (optional)
            if options.get('show_preview') or options.get('save_preview'):
                preview_path = self.render_preview(
                    geometry_data,
                    options.get('preview_path'),
                    options.get('show_preview', False)
                )
                if preview_path:
                    results['preview_path'] = preview_path
            
            # Step 5: Export model
            if output_path:
                exported_path = self.export_model(
                    geometry_data,
                    output_path,
                    options.get('export_format', 'STL'),
                    **{k: v for k, v in options.items() if k.startswith('export_')}
                )
                results['exported_path'] = exported_path
            
            # Calculate total workflow time
            workflow_time = time.time() - workflow_start
            self.processing_stats['total_time'] = workflow_time
            results['processing_stats'] = self.processing_stats.copy()
            
            logging.info(f"Workflow completed successfully in {workflow_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            raise WorkflowError(f"Workflow execution failed: {str(e)}")
    
    def get_processing_stats(self) -> Dict:
        """Get current processing statistics."""
        return self.processing_stats.copy()
    
    def reset(self):
        """Reset the generator state."""
        self.current_text = None
        self.current_mesh = None
        self.current_layout = None
        self.processing_stats.clear()
        logging.debug("Generator state reset")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="3D Text Generator - Convert 2D text to 3D models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Hello World" -o hello.stl
  %(prog)s "Text" -f arial.ttf -d 10 -b 2 -o text.obj --format OBJ
  %(prog)s "Sample" --preview --verbose
  %(prog)s "Test" -o test.gltf --format GLTF --export-scale 2.0
        """
    )
    
    # Required arguments
    parser.add_argument(
        'text',
        help='Text to convert to 3D model'
    )
    
    # Font options
    font_group = parser.add_argument_group('Font Options')
    font_group.add_argument(
        '-f', '--font',
        help='Path to font file (TTF/OTF)'
    )
    font_group.add_argument(
        '--font-size',
        type=int,
        default=Config.DEFAULT_FONT_SIZE,
        help=f'Font size in points (default: {Config.DEFAULT_FONT_SIZE})'
    )
    font_group.add_argument(
        '--character-spacing',
        type=float,
        default=Config.DEFAULT_CHARACTER_SPACING,
        help=f'Character spacing (default: {Config.DEFAULT_CHARACTER_SPACING})'
    )
    
    # 3D generation options
    geometry_group = parser.add_argument_group('3D Geometry Options')
    geometry_group.add_argument(
        '-d', '--depth', '--extrusion-depth',
        type=float,
        default=Config.DEFAULT_EXTRUSION_DEPTH,
        help=f'Extrusion depth (default: {Config.DEFAULT_EXTRUSION_DEPTH})'
    )
    geometry_group.add_argument(
        '-b', '--bevel', '--bevel-depth',
        type=float,
        default=Config.DEFAULT_BEVEL_DEPTH,
        help=f'Bevel depth (default: {Config.DEFAULT_BEVEL_DEPTH})'
    )
    geometry_group.add_argument(
        '--bevel-resolution',
        type=int,
        default=Config.DEFAULT_BEVEL_RESOLUTION,
        help=f'Bevel resolution (default: {Config.DEFAULT_BEVEL_RESOLUTION})'
    )
    
    # Export options
    export_group = parser.add_argument_group('Export Options')
    export_group.add_argument(
        '-o', '--output',
        help='Output file path'
    )
    export_group.add_argument(
        '--format',
        choices=['STL', 'OBJ', 'PLY', 'GLTF'],
        default=Config.DEFAULT_EXPORT_FORMAT,
        help=f'Export format (default: {Config.DEFAULT_EXPORT_FORMAT})'
    )
    export_group.add_argument(
        '--export-scale',
        type=float,
        default=Config.DEFAULT_EXPORT_SCALE,
        help=f'Export scale factor (default: {Config.DEFAULT_EXPORT_SCALE})'
    )
    export_group.add_argument(
        '--output-dir',
        help=f'Output directory (default: {Config.DEFAULT_OUTPUT_DIR})'
    )
    
    # Preview options
    preview_group = parser.add_argument_group('Preview Options')
    preview_group.add_argument(
        '--preview',
        action='store_true',
        help='Show interactive 3D preview'
    )
    preview_group.add_argument(
        '--save-preview',
        help='Save preview image to file'
    )
    
    # Logging and output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    output_group.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress non-error output'
    )
    output_group.add_argument(
        '--log-file',
        help='Log to file'
    )
    output_group.add_argument(
        '--stats',
        action='store_true',
        help='Show processing statistics'
    )
    
    return parser


def setup_application_logging(args) -> None:
    """Setup logging based on command-line arguments."""
    if args.quiet:
        log_level = 'ERROR'
    elif args.verbose:
        log_level = 'DEBUG'
    else:
        log_level = 'INFO'
    
    log_file = None
    if args.log_file:
        log_file = Path(args.log_file)
    
    setup_logging(log_level, log_file)


def validate_arguments(args) -> None:
    """Validate command-line arguments."""
    # Validate font size
    if not Config.validate_font_size(args.font_size):
        raise ValueError(f"Font size must be between {Config.MIN_FONT_SIZE} and {Config.MAX_FONT_SIZE}")
    
    # Validate extrusion depth
    if not Config.validate_extrusion_depth(args.depth):
        raise ValueError(f"Extrusion depth must be between {Config.MIN_EXTRUSION_DEPTH} and {Config.MAX_EXTRUSION_DEPTH}")
    
    # Validate bevel depth
    if args.bevel < 0:
        raise ValueError("Bevel depth cannot be negative")
    
    if args.bevel >= args.depth:
        raise ValueError("Bevel depth must be less than extrusion depth")
    
    # Validate font file if specified
    if args.font and not validate_file_path(args.font):
        raise ValueError(f"Font file not found: {args.font}")
    
    # Validate text length
    if len(args.text) > Config.MAX_TEXT_LENGTH:
        raise ValueError(f"Text too long (max {Config.MAX_TEXT_LENGTH} characters)")


def generate_output_path(text: str, output_dir: str, format_name: str) -> str:
    """Generate output file path from text and format."""
    safe_text = safe_filename(text[:20])  # Limit filename length
    if not safe_text:
        safe_text = "text_3d"
    
    extension = format_name.lower()
    if extension == 'gltf':
        extension = 'glb'  # Use binary GLTF format
    
    output_dir = Path(output_dir)
    ensure_directory_exists(output_dir)
    
    return str(get_unique_filename(output_dir, safe_text, extension))


def print_processing_stats(stats: Dict) -> None:
    """Print processing statistics in a formatted way."""
    print("\n" + "="*50)
    print("PROCESSING STATISTICS")
    print("="*50)
    
    if 'font_path' in stats:
        print(f"Font: {stats['font_path']} (size: {stats.get('font_size', 'N/A')})")
    
    if 'character_count' in stats:
        print(f"Characters: {stats['character_count']}")
    
    if 'total_width' in stats:
        print(f"Text width: {stats['total_width']:.2f}")
    
    if 'vertices' in stats and 'faces' in stats:
        print(f"Geometry: {stats['vertices']} vertices, {stats['faces']} faces")
    
    if 'extrusion_depth' in stats:
        print(f"Extrusion depth: {stats['extrusion_depth']}")
    
    if 'bevel_depth' in stats:
        print(f"Bevel depth: {stats['bevel_depth']}")
    
    if 'export_format' in stats and 'export_path' in stats:
        print(f"Export: {stats['export_format']} -> {stats['export_path']}")
    
    if 'total_time' in stats:
        print(f"Total time: {stats['total_time']:.2f} seconds")
    
    print("="*50)


def main():
    """Main application entry point."""
    try:
        # Parse command-line arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Setup logging
        setup_application_logging(args)
        
        # Validate arguments
        validate_arguments(args)
        
        # Create configuration overrides
        config_overrides = {}
        if args.output_dir:
            config_overrides['DEFAULT_OUTPUT_DIR'] = Path(args.output_dir)
        
        # Initialize the generator
        generator = Text3DGenerator(config_overrides)
        
        # Prepare workflow options
        workflow_options = {
            'font_size': args.font_size,
            'character_spacing': args.character_spacing,
            'extrusion_depth': args.depth,
            'bevel_depth': args.bevel,
            'export_format': args.format,
            'export_scale': args.export_scale,
            'show_preview': args.preview,
            'save_preview': args.save_preview
        }
        
        # Generate output path if not specified
        output_path = args.output
        if not output_path and not args.preview:
            output_dir = args.output_dir or Config.DEFAULT_OUTPUT_DIR
            output_path = generate_output_path(args.text, output_dir, args.format)
        
        # Run the workflow
        logging.info(f"Starting 3D text generation for: '{args.text}'")
        
        results = generator.run_workflow(
            args.text,
            args.font,
            output_path,
            **workflow_options
        )
        
        # Print results
        if not args.quiet:
            print(f"\n✓ 3D text generation completed successfully!")
            
            if 'exported_path' in results:
                print(f"✓ Model exported to: {results['exported_path']}")
            
            if 'preview_path' in results:
                print(f"✓ Preview saved to: {results['preview_path']}")
        
        # Print statistics if requested
        if args.stats:
            print_processing_stats(results.get('processing_stats', {}))
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1
        
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())