"""
Integration tests for 3D Text Generator.

Comprehensive end-to-end testing of the complete 3D text generation workflow
to ensure all modules work correctly together.
"""

import unittest
import tempfile
import shutil
import time
import psutil
import os
import sys
from pathlib import Path
from unittest.mock import patch, Mock
import threading
import gc

# Import the main application and core modules
from main import Text3DGenerator, main as main_function
from text_processor import FontLoader, TextProcessor
from geometry_generator import GeometryGenerator
from renderer import Renderer
from exporter import Exporter
from config import Config

# Import exceptions
from text_processor import FontLoadError, TextProcessingError
from geometry_generator import GeometryError
from renderer import RenderingError
from exporter import ExportError
from main import WorkflowError


class IntegrationTestBase(unittest.TestCase):
    """Base class for integration tests with common setup."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_fonts_dir = self.temp_dir / "fonts"
        self.test_output_dir = self.temp_dir / "output"
        self.test_fonts_dir.mkdir(exist_ok=True)
        self.test_output_dir.mkdir(exist_ok=True)
        
        # Create a simple test font file (mock)
        self.test_font_path = self.test_fonts_dir / "test_font.ttf"
        self.test_font_path.write_bytes(b"MOCK_FONT_DATA")
        
        # Configuration overrides for testing
        self.config_overrides = {
            'DEFAULT_OUTPUT_DIR': self.test_output_dir
        }
        
        # Initialize generator
        self.generator = Text3DGenerator(self.config_overrides)
        
        # Test parameters
        self.test_text = "Test"
        self.simple_text = "A"
        self.complex_text = "Hello World!"
        self.unicode_text = "Héllo Wörld! 🌍"
        self.large_text = "A" * 100  # Large text for performance testing
        
        # Performance thresholds
        self.max_processing_time = 30.0  # seconds
        self.max_memory_usage = 1024 * 1024 * 1024  # 1GB in bytes
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        # Force garbage collection
        gc.collect()
    
    def get_memory_usage(self):
        """Get current memory usage in bytes."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss
    
    def measure_time_and_memory(self, func, *args, **kwargs):
        """Measure execution time and memory usage of a function."""
        gc.collect()  # Clean up before measurement
        start_memory = self.get_memory_usage()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = e
            success = False
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        return {
            'result': result,
            'success': success,
            'execution_time': end_time - start_time,
            'memory_delta': end_memory - start_memory,
            'peak_memory': end_memory
        }


class TestCompleteWorkflow(IntegrationTestBase):
    """Test complete workflow integration."""
    
    def test_complete_workflow(self):
        """Test the complete pipeline from text to export."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh, \
             patch('exporter.Exporter.export_mesh') as mock_export:
            
            # Setup mocks for successful workflow
            mock_load_font.return_value = True
            mock_parse.return_value = self.test_text
            mock_layout.return_value = [
                {'character': 'T', 'position': (0, 0), 'width': 10},
                {'character': 'e', 'position': (12, 0), 'width': 8},
                {'character': 's', 'position': (22, 0), 'width': 8},
                {'character': 't', 'position': (32, 0), 'width': 6}
            ]
            mock_outlines.return_value = {
                'T': [[(0, 0), (10, 0), (10, 20), (0, 20)]],
                'e': [[(0, 0), (8, 0), (8, 15), (0, 15)]],
                's': [[(0, 0), (8, 0), (8, 15), (0, 15)]],
                't': [[(0, 0), (6, 0), (6, 18), (0, 18)]]
            }
            
            # Mock mesh generation
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (10, 0, 0), (10, 20, 0), (0, 20, 0),
                           (0, 0, 5), (10, 0, 5), (10, 20, 5), (0, 20, 5)],
                'faces': [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2],
                         [2, 6, 7, 3], [3, 7, 4, 0]],
                'normals': [(0, 0, -1), (0, 0, 1), (0, -1, 0), (1, 0, 0), (0, 1, 0), (-1, 0, 0)]
            }
            
            output_path = self.test_output_dir / "test_complete.stl"
            mock_export.return_value = str(output_path)
            
            # Run complete workflow
            result = self.generator.run_workflow(
                text=self.test_text,
                font_path=str(self.test_font_path),
                output_path=str(output_path),
                export_format="STL"
            )
            
            # Verify workflow completion
            self.assertIn('text_processing', result)
            self.assertIn('geometry_generation', result)
            self.assertIn('exported_path', result)
            self.assertIn('processing_stats', result)
            
            # Verify text processing results
            text_data = result['text_processing']
            self.assertEqual(text_data['text'], self.test_text)
            self.assertEqual(text_data['character_count'], 4)
            self.assertGreater(text_data['total_width'], 0)
            
            # Verify geometry generation results
            geometry_data = result['geometry_generation']
            self.assertGreater(geometry_data['total_vertices'], 0)
            self.assertGreater(geometry_data['total_faces'], 0)
            self.assertEqual(geometry_data['character_meshes'], 4)
            
            # Verify export
            self.assertEqual(result['exported_path'], str(output_path))
            
            # Verify processing stats
            stats = result['processing_stats']
            self.assertIn('total_time', stats)
            self.assertIn('vertices', stats)
            self.assertIn('faces', stats)
    
    def test_workflow_with_preview(self):
        """Test workflow with preview generation."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh, \
             patch('renderer.Renderer.render_to_image') as mock_render:
            
            # Setup mocks
            mock_load_font.return_value = True
            mock_parse.return_value = self.simple_text
            mock_layout.return_value = [{'character': 'A', 'position': (0, 0), 'width': 10}]
            mock_outlines.return_value = {'A': [[(0, 0), (10, 0), (5, 20)]]}
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (10, 0, 0), (5, 20, 0)],
                'faces': [[0, 1, 2]],
                'normals': [(0, 0, 1)]
            }
            
            preview_path = self.test_output_dir / "preview.png"
            mock_render.return_value = str(preview_path)
            
            # Run workflow with preview
            result = self.generator.run_workflow(
                text=self.simple_text,
                save_preview=str(preview_path)
            )
            
            # Verify preview was generated
            self.assertIn('preview_path', result)
            self.assertEqual(result['preview_path'], str(preview_path))
            mock_render.assert_called_once()


class TestWorkflowWithDifferentFonts(IntegrationTestBase):
    """Test workflow with different font types."""
    
    def test_workflow_with_default_font(self):
        """Test workflow using default font when no font specified."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh, \
             patch('config.Config.get_default_font_path') as mock_default_font:
            
            # Setup mocks
            mock_default_font.return_value = Path("/system/default.ttf")
            mock_load_font.return_value = True
            mock_parse.return_value = self.simple_text
            mock_layout.return_value = [{'character': 'A', 'position': (0, 0), 'width': 10}]
            mock_outlines.return_value = {'A': [[(0, 0), (10, 0), (5, 20)]]}
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (10, 0, 0), (5, 20, 0)],
                'faces': [[0, 1, 2]],
                'normals': [(0, 0, 1)]
            }
            
            # Run workflow without specifying font
            result = self.generator.run_workflow(text=self.simple_text)
            
            # Verify workflow completed successfully
            self.assertIn('text_processing', result)
            self.assertIn('geometry_generation', result)
    
    def test_workflow_with_different_font_sizes(self):
        """Test workflow with various font sizes."""
        font_sizes = [12, 24, 48, 72, 144]
        
        for font_size in font_sizes:
            with self.subTest(font_size=font_size):
                with patch('text_processor.FontLoader.load_font') as mock_load_font, \
                     patch('text_processor.TextProcessor.parse_text') as mock_parse, \
                     patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
                     patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
                     patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh:
                    
                    # Setup mocks
                    mock_load_font.return_value = True
                    mock_parse.return_value = self.simple_text
                    mock_layout.return_value = [{'character': 'A', 'position': (0, 0), 'width': font_size/2}]
                    mock_outlines.return_value = {'A': [[(0, 0), (font_size/2, 0), (font_size/4, font_size)]]}
                    mock_mesh.return_value = {
                        'vertices': [(0, 0, 0), (font_size/2, 0, 0), (font_size/4, font_size, 0)],
                        'faces': [[0, 1, 2]],
                        'normals': [(0, 0, 1)]
                    }
                    
                    # Run workflow with specific font size
                    result = self.generator.run_workflow(
                        text=self.simple_text,
                        font_size=font_size
                    )
                    
                    # Verify font size was applied
                    self.assertIn('processing_stats', result)
                    stats = result['processing_stats']
                    self.assertEqual(stats.get('font_size'), font_size)


class TestWorkflowWithDifferentExportFormats(IntegrationTestBase):
    """Test workflow with different export formats."""
    
    def test_workflow_with_all_export_formats(self):
        """Test workflow with all supported export formats."""
        export_formats = ['STL', 'OBJ', 'PLY', 'GLTF']
        
        for export_format in export_formats:
            with self.subTest(format=export_format):
                with patch('text_processor.FontLoader.load_font') as mock_load_font, \
                     patch('text_processor.TextProcessor.parse_text') as mock_parse, \
                     patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
                     patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
                     patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh, \
                     patch('exporter.Exporter.export_mesh') as mock_export:
                    
                    # Setup mocks
                    mock_load_font.return_value = True
                    mock_parse.return_value = self.simple_text
                    mock_layout.return_value = [{'character': 'A', 'position': (0, 0), 'width': 10}]
                    mock_outlines.return_value = {'A': [[(0, 0), (10, 0), (5, 20)]]}
                    mock_mesh.return_value = {
                        'vertices': [(0, 0, 0), (10, 0, 0), (5, 20, 0)],
                        'faces': [[0, 1, 2]],
                        'normals': [(0, 0, 1)]
                    }
                    
                    extension = export_format.lower()
                    if extension == 'gltf':
                        extension = 'glb'
                    
                    output_path = self.test_output_dir / f"test.{extension}"
                    mock_export.return_value = str(output_path)
                    
                    # Run workflow with specific export format
                    result = self.generator.run_workflow(
                        text=self.simple_text,
                        output_path=str(output_path),
                        export_format=export_format
                    )
                    
                    # Verify export format was used
                    self.assertIn('exported_path', result)
                    self.assertEqual(result['exported_path'], str(output_path))
                    
                    # Verify export was called with correct format
                    mock_export.assert_called_once()
                    call_args = mock_export.call_args
                    self.assertEqual(call_args[0][2], export_format)  # Format argument


class TestWorkflowPerformance(IntegrationTestBase):
    """Test workflow performance and resource usage."""
    
    def test_workflow_performance(self):
        """Test that workflow completes within acceptable time limits."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh:
            
            # Setup mocks for normal text
            mock_load_font.return_value = True
            mock_parse.return_value = self.complex_text
            mock_layout.return_value = [
                {'character': c, 'position': (i * 10, 0), 'width': 8}
                for i, c in enumerate(self.complex_text) if c != ' '
            ]
            mock_outlines.return_value = {
                c: [[(0, 0), (8, 0), (8, 15), (0, 15)]]
                for c in self.complex_text if c != ' '
            }
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (8, 0, 0), (8, 15, 0), (0, 15, 0)],
                'faces': [[0, 1, 2, 3]],
                'normals': [(0, 0, 1)]
            }
            
            # Measure performance
            metrics = self.measure_time_and_memory(
                self.generator.run_workflow,
                text=self.complex_text
            )
            
            # Verify performance requirements
            self.assertTrue(metrics['success'], f"Workflow failed: {metrics['result']}")
            self.assertLess(
                metrics['execution_time'], 
                self.max_processing_time,
                f"Workflow took {metrics['execution_time']:.2f}s, exceeding limit of {self.max_processing_time}s"
            )
    
    def test_workflow_memory_usage(self):
        """Test that workflow memory usage stays within acceptable limits."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh:
            
            # Setup mocks
            mock_load_font.return_value = True
            mock_parse.return_value = self.complex_text
            mock_layout.return_value = [
                {'character': c, 'position': (i * 10, 0), 'width': 8}
                for i, c in enumerate(self.complex_text) if c != ' '
            ]
            mock_outlines.return_value = {
                c: [[(0, 0), (8, 0), (8, 15), (0, 15)]]
                for c in self.complex_text if c != ' '
            }
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (8, 0, 0), (8, 15, 0), (0, 15, 0)],
                'faces': [[0, 1, 2, 3]],
                'normals': [(0, 0, 1)]
            }
            
            # Measure memory usage
            metrics = self.measure_time_and_memory(
                self.generator.run_workflow,
                text=self.complex_text
            )
            
            # Verify memory requirements
            self.assertTrue(metrics['success'], f"Workflow failed: {metrics['result']}")
            self.assertLess(
                metrics['peak_memory'],
                self.max_memory_usage,
                f"Peak memory usage {metrics['peak_memory']} bytes exceeds limit of {self.max_memory_usage} bytes"
            )
    
    def test_large_text_processing(self):
        """Test workflow with large text input."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh:
            
            # Setup mocks for large text
            mock_load_font.return_value = True
            mock_parse.return_value = self.large_text
            mock_layout.return_value = [
                {'character': 'A', 'position': (i * 10, 0), 'width': 8}
                for i in range(len(self.large_text))
            ]
            mock_outlines.return_value = {
                'A': [[(0, 0), (8, 0), (8, 15), (0, 15)]]
            }
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (8, 0, 0), (8, 15, 0), (0, 15, 0)],
                'faces': [[0, 1, 2, 3]],
                'normals': [(0, 0, 1)]
            }
            
            # Test large text processing
            result = self.generator.run_workflow(text=self.large_text)
            
            # Verify processing completed
            self.assertIn('text_processing', result)
            self.assertIn('geometry_generation', result)
            
            # Verify character count
            text_data = result['text_processing']
            self.assertEqual(text_data['character_count'], len(self.large_text))


class TestErrorScenarios(IntegrationTestBase):
    """Test error handling in complete workflow."""
    
    def test_font_loading_error_handling(self):
        """Test workflow behavior when font loading fails."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font:
            mock_load_font.side_effect = FontLoadError("Font not found")
            
            with self.assertRaises(FontLoadError):
                self.generator.load_font("/nonexistent/font.ttf")
    
    def test_text_processing_error_handling(self):
        """Test workflow behavior when text processing fails."""
        with patch('text_processor.TextProcessor.parse_text') as mock_parse:
            mock_parse.side_effect = TextProcessingError("Invalid text")
            
            with self.assertRaises(TextProcessingError):
                self.generator.process_text("invalid_text")
    
    def test_geometry_generation_error_handling(self):
        """Test workflow behavior when geometry generation fails."""
        with patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh:
            mock_mesh.side_effect = GeometryError("Mesh generation failed")
            
            text_data = {
                'outlines': {'A': [[(0, 0), (10, 0), (5, 20)]]},
                'layout': [{'character': 'A', 'position': (0, 0)}]
            }
            
            with self.assertRaises(GeometryError):
                self.generator.generate_geometry(text_data)
    
    def test_export_error_handling(self):
        """Test workflow behavior when export fails."""
        with patch('exporter.Exporter.export_mesh') as mock_export:
            mock_export.side_effect = ExportError("Export failed")
            
            geometry_data = {
                'mesh': {'vertices': [], 'faces': []}
            }
            
            with self.assertRaises(ExportError):
                self.generator.export_model(geometry_data, "/invalid/path.stl")
    
    def test_workflow_error_propagation(self):
        """Test that errors in workflow are properly propagated."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font:
            mock_load_font.side_effect = FontLoadError("Font error")
            
            with self.assertRaises(WorkflowError):
                self.generator.run_workflow(
                    text=self.test_text,
                    font_path="/invalid/font.ttf"
                )


class TestSpecialCharacters(IntegrationTestBase):
    """Test workflow with special characters and unicode."""
    
    def test_unicode_text_processing(self):
        """Test workflow with unicode characters."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh:
            
            # Setup mocks for unicode text
            mock_load_font.return_value = True
            mock_parse.return_value = self.unicode_text
            mock_layout.return_value = [
                {'character': c, 'position': (i * 10, 0), 'width': 8}
                for i, c in enumerate(self.unicode_text) if c != ' '
            ]
            mock_outlines.return_value = {
                c: [[(0, 0), (8, 0), (8, 15), (0, 15)]]
                for c in self.unicode_text if c != ' '
            }
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (8, 0, 0), (8, 15, 0), (0, 15, 0)],
                'faces': [[0, 1, 2, 3]],
                'normals': [(0, 0, 1)]
            }
            
            # Test unicode processing
            result = self.generator.run_workflow(text=self.unicode_text)
            
            # Verify processing completed
            self.assertIn('text_processing', result)
            self.assertIn('geometry_generation', result)
            
            # Verify text was processed correctly
            text_data = result['text_processing']
            self.assertEqual(text_data['text'], self.unicode_text)
    
    def test_special_characters_handling(self):
        """Test workflow with various special characters."""
        special_texts = [
            "!@#$%^&*()",
            "123456789",
            "áéíóú",
            "ÀÈÌÒÙ",
            "çñü",
            "αβγδε"
        ]
        
        for special_text in special_texts:
            with self.subTest(text=special_text):
                with patch('text_processor.FontLoader.load_font') as mock_load_font, \
                     patch('text_processor.TextProcessor.parse_text') as mock_parse, \
                     patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
                     patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
                     patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh:
                    
                    # Setup mocks
                    mock_load_font.return_value = True
                    mock_parse.return_value = special_text
                    mock_layout.return_value = [
                        {'character': c, 'position': (i * 10, 0), 'width': 8}
                        for i, c in enumerate(special_text)
                    ]
                    mock_outlines.return_value = {
                        c: [[(0, 0), (8, 0), (8, 15), (0, 15)]]
                        for c in special_text
                    }
                    mock_mesh.return_value = {
                        'vertices': [(0, 0, 0), (8, 0, 0), (8, 15, 0), (0, 15, 0)],
                        'faces': [[0, 1, 2, 3]],
                        'normals': [(0, 0, 1)]
                    }
                    
                    # Test special character processing
                    result = self.generator.run_workflow(text=special_text)
                    
                    # Verify processing completed
                    self.assertIn('text_processing', result)
                    self.assertIn('geometry_generation', result)


class TestConfigurationOverrides(IntegrationTestBase):
    """Test CLI parameter overrides and configuration."""
    
    def test_configuration_overrides(self):
        """Test that CLI parameters override default configuration."""
        custom_config = {
            'DEFAULT_FONT_SIZE': 48,
            'DEFAULT_EXTRUSION_DEPTH': 10.0,
            'DEFAULT_BEVEL_DEPTH': 2.0,
            'DEFAULT_EXPORT_FORMAT': 'OBJ'
        }
        
        generator = Text3DGenerator(custom_config)
        
        # Verify configuration overrides were applied
        for key, value in custom_config.items():
            if hasattr(generator.config, key):
                self.assertEqual(getattr(generator.config, key), value)
    
    def test_workflow_parameter_overrides(self):
        """Test workflow with parameter overrides."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh, \
             patch('exporter.Exporter.export_mesh') as mock_export:
            
            # Setup mocks
            mock_load_font.return_value = True
            mock_parse.return_value = self.simple_text
            mock_layout.return_value = [{'character': 'A', 'position': (0, 0), 'width': 10}]
            mock_outlines.return_value = {'A': [[(0, 0), (10, 0), (5, 20)]]}
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (10, 0, 0), (5, 20, 0)],
                'faces': [[0, 1, 2]],
                'normals': [(0, 0, 1)]
            }
            mock_export.return_value = "/output/test.obj"
            
            # Test with custom parameters
            result = self.generator.run_workflow(
                text=self.simple_text,
                font_size=48,
                character_spacing=2.0,
                extrusion_depth=10.0,
                bevel_depth=2.0,
                export_format="OBJ",
                export_scale=2.0
            )
            
            # Verify parameters were used
            stats = result['processing_stats']
            self.assertEqual(stats.get('font_size'), 48)
            self.assertEqual(stats.get('extrusion_depth'), 10.0)
            self.assertEqual(stats.get('bevel_depth'), 2.0)


class TestPreviewFunctionality(IntegrationTestBase):
    """Test preview generation functionality."""
    
    def test_preview_image_generation(self):
        """Test preview image generation."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh, \
             patch('renderer.Renderer.render_to_image') as mock_render:
            
            # Setup mocks
            mock_load_font.return_value = True
            mock_parse.return_value = self.simple_text
            mock_layout.return_value = [{'character': 'A', 'position': (0, 0), 'width': 10}]
            mock_outlines.return_value = {'A': [[(0, 0), (10, 0), (5, 20)]]}
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (10, 0, 0), (5, 20, 0)],
                'faces': [[0, 1, 2]],
                'normals': [(0, 0, 1)]
            }
            
            preview_path = self.test_output_dir / "test_preview.png"
            mock_render.return_value = str(preview_path)
            
            # Test preview generation
            geometry_data = {
                'mesh': mock_mesh.return_value,
                'bounds': {'size': (10, 20, 5)}
            }
            
            result = self.generator.render_preview(
                geometry_data,
                str(preview_path)
            )
            
            # Verify preview was generated
            self.assertEqual(result, str(preview_path))
            mock_render.assert_called_once()
    
    def test_interactive_preview(self):
        """Test interactive preview functionality."""
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh, \
             patch('renderer.Renderer.render_interactive') as mock_interactive:
            
            # Setup mocks
            mock_load_font.return_value = True
            mock_parse.return_value = self.simple_text
            mock_layout.return_value = [{'character': 'A', 'position': (0, 0), 'width': 10}]
            mock_outlines.return_value = {'A': [[(0, 0), (10, 0), (5, 20)]]}
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (10, 0, 0), (5, 20, 0)],
                'faces': [[0, 1, 2]],
                'normals': [(0, 0, 1)]
            }
            
            # Test interactive preview
            geometry_data = {
                'mesh': mock_mesh.return_value,
                'bounds': {'size': (10, 20, 5)}
            }
            
            result = self.generator.render_preview(
                geometry_data,
                show_preview=True
            )
            
            # Verify interactive preview was called
            mock_interactive.assert_called_once()


class TestMainApplicationIntegration(IntegrationTestBase):
    """Test main application CLI integration."""
    
    @patch('sys.argv')
    def test_main_function_integration(self, mock_argv):
        """Test main function with command line arguments."""
        # Mock command line arguments
        mock_argv.__getitem__.side_effect = lambda x: [
            'main.py', 'Test', '-o', str(self.test_output_dir / 'test.stl')
        ][x]
        mock_argv.__len__.return_value = 4
        
        with patch('text_processor.FontLoader.load_font') as mock_load_font, \
             patch('text_processor.TextProcessor.parse_text') as mock_parse, \
             patch('text_processor.TextProcessor.calculate_layout') as mock_layout, \
             patch('text_processor.TextProcessor.get_text_outlines') as mock_outlines, \
             patch('geometry_generator.GeometryGenerator.generate_mesh') as mock_mesh, \
             patch('exporter.Exporter.export_mesh') as mock_export:
            
            # Setup mocks
            mock_load_font.return_value = True
            mock_parse.return_value = "Test"
            mock_layout.return_value = [{'character': 'T', 'position': (0, 0), 'width': 10}]
            mock_outlines.return_value = {'T': [[(0, 0), (10, 0), (10, 20), (0, 20)]]}
            mock_mesh.return_value = {
                'vertices': [(0, 0, 0), (10, 0, 0), (10, 20, 0), (0, 20, 0)],
                'faces': [[0, 1, 2, 3]],
                'normals': [(0, 0, 1)]
            }
            mock_export.return_value = str(self.test_output_dir / 'test.stl')
            
            # Test main function
            with patch('builtins.print'):  # Suppress output
                result = main_function()
            
            # Verify successful execution
            self.assertEqual(result, 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)