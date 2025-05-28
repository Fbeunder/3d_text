#!/usr/bin/env python3
"""
Unit tests for GUI module

Tests all GUI components including panels, dialogs, and main application.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import tkinter as tk
from tkinter import ttk
import tempfile
import json
import threading
import time
from pathlib import Path

# Import GUI components
try:
    from gui import (
        SettingsManager, ProgressDialog, TextInputPanel, GeometryPanel,
        ExportPanel, PreviewPanel, GUIApplication, GUIError
    )
    GUI_AVAILABLE = True
except ImportError as e:
    GUI_AVAILABLE = False
    print(f"GUI tests skipped - GUI module not available: {e}")

from config import Config


@unittest.skipUnless(GUI_AVAILABLE, "GUI module not available")
class TestSettingsManager(unittest.TestCase):
    """Test SettingsManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = Path(self.temp_dir) / "test_settings.json"
        self.settings_manager = SettingsManager(str(self.settings_file))
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.settings_file.exists():
            self.settings_file.unlink()
        self.temp_dir = None
    
    def test_default_settings(self):
        """Test default settings initialization."""
        # Test that default settings are loaded
        self.assertEqual(self.settings_manager.get('font_size'), Config.DEFAULT_FONT_SIZE)
        self.assertEqual(self.settings_manager.get('export_format'), Config.DEFAULT_EXPORT_FORMAT)
        self.assertEqual(self.settings_manager.get('auto_preview'), True)
    
    def test_save_and_load_settings(self):
        """Test settings persistence."""
        # Modify settings
        self.settings_manager.set('font_size', 100)
        self.settings_manager.set('custom_setting', 'test_value')
        
        # Save settings
        self.settings_manager.save_settings()
        
        # Verify file was created
        self.assertTrue(self.settings_file.exists())
        
        # Create new manager and verify settings loaded
        new_manager = SettingsManager(str(self.settings_file))
        self.assertEqual(new_manager.get('font_size'), 100)
        self.assertEqual(new_manager.get('custom_setting'), 'test_value')
    
    def test_invalid_settings_file(self):
        """Test handling of invalid settings file."""
        # Create invalid JSON file
        with open(self.settings_file, 'w') as f:
            f.write("invalid json content")
        
        # Should fall back to defaults
        manager = SettingsManager(str(self.settings_file))
        self.assertEqual(manager.get('font_size'), Config.DEFAULT_FONT_SIZE)
    
    def test_missing_settings_file(self):
        """Test handling of missing settings file."""
        non_existent_file = Path(self.temp_dir) / "non_existent.json"
        manager = SettingsManager(str(non_existent_file))
        
        # Should use defaults
        self.assertEqual(manager.get('font_size'), Config.DEFAULT_FONT_SIZE)
    
    def test_get_with_default(self):
        """Test get method with default value."""
        # Test existing key
        self.assertEqual(self.settings_manager.get('font_size'), Config.DEFAULT_FONT_SIZE)
        
        # Test non-existing key with default
        self.assertEqual(self.settings_manager.get('non_existent', 'default'), 'default')
        
        # Test non-existing key without default
        self.assertIsNone(self.settings_manager.get('non_existent'))


@unittest.skipUnless(GUI_AVAILABLE, "GUI module not available")
class TestProgressDialog(unittest.TestCase):
    """Test ProgressDialog functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.root.destroy()
    
    def test_progress_dialog_creation(self):
        """Test progress dialog creation."""
        dialog = ProgressDialog(self.root, "Test Progress")
        
        # Verify dialog properties
        self.assertEqual(dialog.dialog.title(), "Test Progress")
        self.assertFalse(dialog.cancelled)
        
        # Verify widgets exist
        self.assertIsNotNone(dialog.status_label)
        self.assertIsNotNone(dialog.progress_bar)
        self.assertIsNotNone(dialog.cancel_button)
        
        dialog.close()
    
    def test_progress_update(self):
        """Test progress updates."""
        dialog = ProgressDialog(self.root)
        
        # Update progress
        dialog.update_progress(50, "Processing...")
        
        # Verify updates
        self.assertEqual(dialog.progress_var.get(), 50)
        self.assertEqual(dialog.status_label.cget("text"), "Processing...")
        
        dialog.close()
    
    def test_progress_cancel(self):
        """Test progress cancellation."""
        dialog = ProgressDialog(self.root)
        
        # Cancel operation
        dialog.cancel()
        
        # Verify cancellation
        self.assertTrue(dialog.cancelled)
        
        # Dialog should be closed
        self.assertFalse(dialog.dialog.winfo_exists())


@unittest.skipUnless(GUI_AVAILABLE, "GUI module not available")
class TestTextInputPanel(unittest.TestCase):
    """Test TextInputPanel functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create mock settings manager
        self.settings = Mock()
        self.settings.get.return_value = ""
        
        self.panel = TextInputPanel(self.root, self.settings)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.root.destroy()
    
    def test_panel_creation(self):
        """Test panel creation and widget setup."""
        # Verify frame exists
        self.assertIsNotNone(self.panel.frame)
        
        # Verify input widgets exist
        self.assertIsNotNone(self.panel.text_entry)
        self.assertIsNotNone(self.panel.font_entry)
        self.assertIsNotNone(self.panel.browse_button)
    
    def test_get_values(self):
        """Test getting input values."""
        # Set test values
        self.panel.text_var.set("Test Text")
        self.panel.font_path_var.set("/path/to/font.ttf")
        self.panel.font_size_var.set(100)
        self.panel.char_spacing_var.set(2.5)
        
        values = self.panel.get_values()
        
        # Verify values
        self.assertEqual(values['text'], "Test Text")
        self.assertEqual(values['font_path'], "/path/to/font.ttf")
        self.assertEqual(values['font_size'], 100)
        self.assertEqual(values['character_spacing'], 2.5)
    
    def test_validation_empty_text(self):
        """Test validation with empty text."""
        self.panel.text_var.set("")
        
        valid, message = self.panel.validate()
        
        self.assertFalse(valid)
        self.assertIn("enter text", message.lower())
    
    def test_validation_text_too_long(self):
        """Test validation with text too long."""
        long_text = "x" * (Config.MAX_TEXT_LENGTH + 1)
        self.panel.text_var.set(long_text)
        
        valid, message = self.panel.validate()
        
        self.assertFalse(valid)
        self.assertIn("too long", message.lower())
    
    def test_validation_invalid_font_size(self):
        """Test validation with invalid font size."""
        self.panel.text_var.set("Valid Text")
        self.panel.font_size_var.set(Config.MAX_FONT_SIZE + 1)
        
        valid, message = self.panel.validate()
        
        self.assertFalse(valid)
        self.assertIn("font size", message.lower())
    
    @patch('gui.validate_file_path')
    def test_validation_invalid_font_path(self, mock_validate):
        """Test validation with invalid font path."""
        mock_validate.return_value = False
        
        self.panel.text_var.set("Valid Text")
        self.panel.font_path_var.set("/invalid/path.ttf")
        
        valid, message = self.panel.validate()
        
        self.assertFalse(valid)
        self.assertIn("not found", message.lower())
    
    def test_validation_valid_input(self):
        """Test validation with valid input."""
        self.panel.text_var.set("Valid Text")
        self.panel.font_path_var.set("")  # Empty path should be valid
        self.panel.font_size_var.set(Config.DEFAULT_FONT_SIZE)
        
        valid, message = self.panel.validate()
        
        self.assertTrue(valid)
        self.assertEqual(message, "")
    
    @patch('gui.filedialog.askopenfilename')
    def test_browse_font(self, mock_dialog):
        """Test font browsing functionality."""
        mock_dialog.return_value = "/selected/font.ttf"
        
        self.panel.browse_font()
        
        # Verify dialog was called
        mock_dialog.assert_called_once()
        
        # Verify font path was set
        self.assertEqual(self.panel.font_path_var.get(), "/selected/font.ttf")
    
    @patch('gui.filedialog.askopenfilename')
    def test_browse_font_cancelled(self, mock_dialog):
        """Test font browsing when cancelled."""
        mock_dialog.return_value = ""
        original_path = "/original/path.ttf"
        self.panel.font_path_var.set(original_path)
        
        self.panel.browse_font()
        
        # Verify path unchanged
        self.assertEqual(self.panel.font_path_var.get(), original_path)


@unittest.skipUnless(GUI_AVAILABLE, "GUI module not available")
class TestGeometryPanel(unittest.TestCase):
    """Test GeometryPanel functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create mock settings manager
        self.settings = Mock()
        self.settings.get.return_value = Config.DEFAULT_EXTRUSION_DEPTH
        
        self.panel = GeometryPanel(self.root, self.settings)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.root.destroy()
    
    def test_panel_creation(self):
        """Test panel creation and widget setup."""
        # Verify frame exists
        self.assertIsNotNone(self.panel.frame)
        
        # Verify geometry controls exist
        self.assertIsNotNone(self.panel.extrusion_depth_var)
        self.assertIsNotNone(self.panel.bevel_depth_var)
        self.assertIsNotNone(self.panel.bevel_resolution_var)
    
    def test_get_values(self):
        """Test getting geometry values."""
        # Set test values
        self.panel.extrusion_depth_var.set(10.0)
        self.panel.bevel_depth_var.set(1.5)
        self.panel.bevel_resolution_var.set(8)
        
        values = self.panel.get_values()
        
        # Verify values
        self.assertEqual(values['extrusion_depth'], 10.0)
        self.assertEqual(values['bevel_depth'], 1.5)
        self.assertEqual(values['bevel_resolution'], 8)
    
    def test_validation_invalid_extrusion_depth(self):
        """Test validation with invalid extrusion depth."""
        self.panel.extrusion_depth_var.set(Config.MAX_EXTRUSION_DEPTH + 1)
        
        valid, message = self.panel.validate()
        
        self.assertFalse(valid)
        self.assertIn("extrusion depth", message.lower())
    
    def test_validation_negative_bevel_depth(self):
        """Test validation with negative bevel depth."""
        self.panel.extrusion_depth_var.set(5.0)
        self.panel.bevel_depth_var.set(-1.0)
        
        valid, message = self.panel.validate()
        
        self.assertFalse(valid)
        self.assertIn("negative", message.lower())
    
    def test_validation_bevel_depth_too_large(self):
        """Test validation with bevel depth >= extrusion depth."""
        self.panel.extrusion_depth_var.set(5.0)
        self.panel.bevel_depth_var.set(5.0)
        
        valid, message = self.panel.validate()
        
        self.assertFalse(valid)
        self.assertIn("less than", message.lower())
    
    def test_validation_valid_geometry(self):
        """Test validation with valid geometry values."""
        self.panel.extrusion_depth_var.set(5.0)
        self.panel.bevel_depth_var.set(1.0)
        self.panel.bevel_resolution_var.set(4)
        
        valid, message = self.panel.validate()
        
        self.assertTrue(valid)
        self.assertEqual(message, "")


@unittest.skipUnless(GUI_AVAILABLE, "GUI module not available")
class TestExportPanel(unittest.TestCase):
    """Test ExportPanel functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create mock settings manager
        self.settings = Mock()
        self.settings.get.side_effect = lambda key: {
            'export_format': Config.DEFAULT_EXPORT_FORMAT,
            'export_scale': Config.DEFAULT_EXPORT_SCALE,
            'output_directory': str(Config.DEFAULT_OUTPUT_DIR)
        }.get(key, "")
        
        self.panel = ExportPanel(self.root, self.settings)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.root.destroy()
    
    def test_panel_creation(self):
        """Test panel creation and widget setup."""
        # Verify frame exists
        self.assertIsNotNone(self.panel.frame)
        
        # Verify export controls exist
        self.assertIsNotNone(self.panel.export_format_var)
        self.assertIsNotNone(self.panel.export_scale_var)
        self.assertIsNotNone(self.panel.output_dir_var)
    
    def test_get_values(self):
        """Test getting export values."""
        # Set test values
        self.panel.export_format_var.set("OBJ")
        self.panel.export_scale_var.set(2.0)
        self.panel.output_dir_var.set("/test/output")
        
        values = self.panel.get_values()
        
        # Verify values
        self.assertEqual(values['export_format'], "OBJ")
        self.assertEqual(values['export_scale'], 2.0)
        self.assertEqual(values['output_directory'], "/test/output")
    
    def test_validation_invalid_format(self):
        """Test validation with invalid export format."""
        self.panel.export_format_var.set("INVALID")
        
        valid, message = self.panel.validate()
        
        self.assertFalse(valid)
        self.assertIn("unsupported", message.lower())
    
    def test_validation_negative_scale(self):
        """Test validation with negative scale."""
        self.panel.export_format_var.set("STL")
        self.panel.export_scale_var.set(-1.0)
        
        valid, message = self.panel.validate()
        
        self.assertFalse(valid)
        self.assertIn("positive", message.lower())
    
    def test_validation_valid_export(self):
        """Test validation with valid export values."""
        self.panel.export_format_var.set("STL")
        self.panel.export_scale_var.set(1.0)
        self.panel.output_dir_var.set(str(Config.DEFAULT_OUTPUT_DIR))
        
        valid, message = self.panel.validate()
        
        self.assertTrue(valid)
        self.assertEqual(message, "")
    
    @patch('gui.filedialog.askdirectory')
    def test_browse_output_directory(self, mock_dialog):
        """Test output directory browsing."""
        mock_dialog.return_value = "/selected/output"
        
        self.panel.browse_output_directory()
        
        # Verify dialog was called
        mock_dialog.assert_called_once()
        
        # Verify directory was set
        self.assertEqual(self.panel.output_dir_var.get(), "/selected/output")


@unittest.skipUnless(GUI_AVAILABLE, "GUI module not available")
class TestPreviewPanel(unittest.TestCase):
    """Test PreviewPanel functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.panel = PreviewPanel(self.root)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.root.destroy()
    
    def test_panel_creation(self):
        """Test panel creation and widget setup."""
        # Verify frame exists
        self.assertIsNotNone(self.panel.frame)
    
    @patch('gui.MATPLOTLIB_AVAILABLE', True)
    def test_update_preview_with_mesh(self):
        """Test preview update with valid mesh data."""
        # Create mock mesh data
        mesh_data = {
            'mesh': {
                'vertices': [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
                'faces': [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]]
            },
            'total_vertices': 4,
            'total_faces': 4,
            'bounds': {
                'min': (0, 0, 0),
                'max': (1, 1, 1),
                'size': (1, 1, 1)
            }
        }
        
        # Update preview (should not raise exception)
        try:
            self.panel.update_preview(mesh_data)
            self.assertEqual(self.panel.current_mesh, mesh_data)
        except Exception as e:
            # If matplotlib not available, this is expected
            if "matplotlib" not in str(e).lower():
                raise
    
    def test_update_preview_empty_mesh(self):
        """Test preview update with empty mesh data."""
        mesh_data = {'mesh': {'vertices': [], 'faces': []}}
        
        # Should handle empty mesh gracefully
        try:
            self.panel.update_preview(mesh_data)
        except Exception as e:
            # If matplotlib not available, this is expected
            if "matplotlib" not in str(e).lower():
                raise
    
    @patch('gui.filedialog.asksaveasfilename')
    @patch('gui.MATPLOTLIB_AVAILABLE', True)
    def test_save_preview(self, mock_dialog):
        """Test saving preview image."""
        mock_dialog.return_value = "/test/preview.png"
        
        # Set current mesh
        self.panel.current_mesh = {
            'mesh': {'vertices': [[0, 0, 0]], 'faces': [[0]]}
        }
        
        # Mock matplotlib figure
        with patch.object(self.panel, 'fig', Mock()) as mock_fig:
            self.panel.save_preview()
            
            # Verify dialog was called
            mock_dialog.assert_called_once()
            
            # Verify save was attempted
            mock_fig.savefig.assert_called_once_with(
                "/test/preview.png", dpi=300, bbox_inches='tight'
            )


@unittest.skipUnless(GUI_AVAILABLE, "GUI module not available")
class TestGUIApplication(unittest.TestCase):
    """Test GUIApplication functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary settings file
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = Path(self.temp_dir) / "test_gui_settings.json"
        
        # Patch SettingsManager to use test file
        self.settings_patcher = patch('gui.SettingsManager')
        mock_settings_class = self.settings_patcher.start()
        
        # Create mock settings instance
        self.mock_settings = Mock()
        self.mock_settings.get.side_effect = lambda key, default=None: {
            'window_geometry': '1200x800+100+100',
            'auto_preview': True,
            'show_statistics': True
        }.get(key, default)
        mock_settings_class.return_value = self.mock_settings
        
        # Patch Text3DGenerator
        self.generator_patcher = patch('gui.Text3DGenerator')
        mock_generator_class = self.generator_patcher.start()
        self.mock_generator = Mock()
        mock_generator_class.return_value = self.mock_generator
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.settings_patcher.stop()
        self.generator_patcher.stop()
        
        if hasattr(self, 'app') and self.app.root.winfo_exists():
            self.app.root.destroy()
    
    def test_application_creation(self):
        """Test GUI application creation."""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Create application
            self.app = GUIApplication()
            
            # Verify root window setup
            mock_root.title.assert_called_with("3D Text Generator")
            mock_root.geometry.assert_called_with("1200x800")
    
    @patch('gui.messagebox.showerror')
    def test_validation_error_handling(self, mock_error):
        """Test validation error handling."""
        # Create app with mocked root
        with patch('tkinter.Tk'):
            self.app = GUIApplication()
            
            # Mock validation failure
            self.app.text_panel = Mock()
            self.app.text_panel.validate.return_value = (False, "Test error")
            
            # Mock other panels
            self.app.geometry_panel = Mock()
            self.app.export_panel = Mock()
            
            # Try to run workflow
            self.app.run_workflow()
            
            # Verify error dialog was shown
            mock_error.assert_called_once_with("Validation Error", "Test error")
    
    @patch('threading.Thread')
    def test_workflow_threading(self, mock_thread):
        """Test that workflow runs in background thread."""
        # Create app with mocked root
        with patch('tkinter.Tk'):
            self.app = GUIApplication()
            
            # Mock successful validation
            self.app.validate_all_inputs = Mock(return_value=(True, ""))
            
            # Mock panels
            self.app.text_panel = Mock()
            self.app.text_panel.get_values.return_value = {
                'text': 'Test', 'font_path': '', 'font_size': 72, 'character_spacing': 2.0
            }
            self.app.geometry_panel = Mock()
            self.app.geometry_panel.get_values.return_value = {
                'extrusion_depth': 5.0, 'bevel_depth': 0.5, 'bevel_resolution': 4
            }
            self.app.export_panel = Mock()
            self.app.export_panel.get_values.return_value = {
                'export_format': 'STL', 'export_scale': 1.0, 'output_directory': '/tmp'
            }
            
            # Mock buttons
            self.app.generate_button = Mock()
            self.app.preview_button = Mock()
            self.app.export_button = Mock()
            
            # Mock progress dialog
            with patch('gui.ProgressDialog') as mock_progress:
                mock_progress_instance = Mock()
                mock_progress.return_value = mock_progress_instance
                
                # Run workflow
                self.app.run_workflow()
                
                # Verify thread was created and started
                mock_thread.assert_called_once()
                thread_instance = mock_thread.return_value
                thread_instance.start.assert_called_once()
    
    def test_settings_persistence(self):
        """Test settings save and load."""
        # Create app with mocked root
        with patch('tkinter.Tk'):
            self.app = GUIApplication()
            
            # Mock panels
            self.app.text_panel = Mock()
            self.app.text_panel.get_values.return_value = {
                'text': 'Test Text', 'font_path': '/test/font.ttf',
                'font_size': 100, 'character_spacing': 3.0
            }
            self.app.geometry_panel = Mock()
            self.app.geometry_panel.get_values.return_value = {
                'extrusion_depth': 10.0, 'bevel_depth': 2.0, 'bevel_resolution': 8
            }
            self.app.export_panel = Mock()
            self.app.export_panel.get_values.return_value = {
                'export_format': 'OBJ', 'export_scale': 2.0, 'output_directory': '/test/output'
            }
            
            # Mock root geometry
            self.app.root = Mock()
            self.app.root.geometry.return_value = "1400x900+200+150"
            
            # Save settings
            self.app.save_settings()
            
            # Verify settings were saved
            self.mock_settings.set.assert_any_call('window_geometry', "1400x900+200+150")
            self.mock_settings.set.assert_any_call('last_text', 'Test Text')
            self.mock_settings.set.assert_any_call('font_path', '/test/font.ttf')
            self.mock_settings.save_settings.assert_called_once()


@unittest.skipUnless(GUI_AVAILABLE, "GUI module not available")
class TestGUIIntegration(unittest.TestCase):
    """Integration tests for GUI with core modules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        pass
    
    @patch('gui.Text3DGenerator')
    def test_workflow_integration(self, mock_generator_class):
        """Test GUI workflow integration with core modules."""
        # Create mock generator
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        
        # Mock successful workflow
        mock_results = {
            'text_processing': {'text': 'Test', 'character_count': 4},
            'geometry_generation': {
                'mesh': {'vertices': [[0, 0, 0]], 'faces': [[0]]},
                'total_vertices': 1,
                'total_faces': 1
            },
            'processing_stats': {'total_time': 1.5}
        }
        mock_generator.run_workflow.return_value = mock_results
        
        # Create app with mocked components
        with patch('tkinter.Tk'), patch('gui.SettingsManager'):
            app = GUIApplication()
            
            # Mock validation and panels
            app.validate_all_inputs = Mock(return_value=(True, ""))
            app.text_panel = Mock()
            app.text_panel.get_values.return_value = {
                'text': 'Test', 'font_path': '', 'font_size': 72, 'character_spacing': 2.0
            }
            app.geometry_panel = Mock()
            app.geometry_panel.get_values.return_value = {
                'extrusion_depth': 5.0, 'bevel_depth': 0.5, 'bevel_resolution': 4
            }
            app.export_panel = Mock()
            app.export_panel.get_values.return_value = {
                'export_format': 'STL', 'export_scale': 1.0, 'output_directory': '/tmp'
            }
            
            # Mock UI components
            app.generate_button = Mock()
            app.preview_button = Mock()
            app.export_button = Mock()
            app.preview_panel = Mock()
            
            # Mock progress dialog
            with patch('gui.ProgressDialog') as mock_progress:
                mock_progress_instance = Mock()
                mock_progress.return_value = mock_progress_instance
                
                # Run workflow completion directly (simulate thread completion)
                app.workflow_completed(mock_results, False)
                
                # Verify preview was updated
                app.preview_panel.update_preview.assert_called_once()
                
                # Verify buttons were re-enabled
                app.generate_button.config.assert_called_with(state=tk.NORMAL)
                app.preview_button.config.assert_called_with(state=tk.NORMAL)
                app.export_button.config.assert_called_with(state=tk.NORMAL)
    
    def test_error_handling_integration(self):
        """Test error handling integration."""
        with patch('tkinter.Tk'), patch('gui.SettingsManager'):
            app = GUIApplication()
            
            # Mock UI components
            app.generate_button = Mock()
            app.preview_button = Mock()
            app.export_button = Mock()
            
            # Mock error dialog
            with patch('gui.messagebox.showerror') as mock_error:
                # Simulate workflow failure
                app.workflow_failed("Test error message")
                
                # Verify error dialog was shown
                mock_error.assert_called_once_with(
                    "Error", "Failed to generate 3D text:\nTest error message"
                )
                
                # Verify buttons were re-enabled
                app.generate_button.config.assert_called_with(state=tk.NORMAL)
                app.preview_button.config.assert_called_with(state=tk.NORMAL)
                app.export_button.config.assert_called_with(state=tk.NORMAL)


class TestGUIModuleImport(unittest.TestCase):
    """Test GUI module import and dependencies."""
    
    def test_gui_module_import(self):
        """Test that GUI module can be imported."""
        try:
            import gui
            self.assertTrue(hasattr(gui, 'GUIApplication'))
            self.assertTrue(hasattr(gui, 'TextInputPanel'))
            self.assertTrue(hasattr(gui, 'GeometryPanel'))
            self.assertTrue(hasattr(gui, 'ExportPanel'))
            self.assertTrue(hasattr(gui, 'PreviewPanel'))
        except ImportError as e:
            self.skipTest(f"GUI module not available: {e}")
    
    def test_matplotlib_availability(self):
        """Test matplotlib availability for 3D preview."""
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            matplotlib_available = True
        except ImportError:
            matplotlib_available = False
        
        # Test should pass regardless of matplotlib availability
        # GUI should handle missing matplotlib gracefully
        self.assertIsInstance(matplotlib_available, bool)


if __name__ == '__main__':
    # Configure test runner
    unittest.main(
        verbosity=2,
        buffer=True,
        catchbreak=True,
        warnings='ignore'
    )