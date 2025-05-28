"""
Unit tests for the 3D Renderer Module

Tests for Camera, Light, and Renderer classes with comprehensive
coverage of functionality, error handling, and edge cases.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from pathlib import Path
import tempfile
import os

# Import the modules to test
from renderer import (
    Camera, Light, Renderer, RenderingError, CameraError, LightingError,
    create_default_renderer, render_mesh_quick
)


class TestCamera(unittest.TestCase):
    """Test cases for Camera class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.camera = Camera()
    
    def test_camera_initialization(self):
        """Test camera initialization with default values."""
        self.assertTrue(np.allclose(self.camera.position, [50, 50, 50]))
        self.assertTrue(np.allclose(self.camera.target, [0, 0, 0]))
        self.assertTrue(np.allclose(self.camera.up_vector, [0, 0, 1]))
        self.assertEqual(self.camera.fov, 45.0)
    
    def test_camera_custom_initialization(self):
        """Test camera initialization with custom values."""
        position = (10, 20, 30)
        target = (5, 5, 5)
        up_vector = (0, 1, 0)
        
        camera = Camera(position, target, up_vector)
        
        self.assertTrue(np.allclose(camera.position, position))
        self.assertTrue(np.allclose(camera.target, target))
        self.assertTrue(np.allclose(camera.up_vector, up_vector))
    
    def test_camera_invalid_vectors(self):
        """Test camera with invalid vector inputs."""
        with self.assertRaises(CameraError):
            Camera(position=(np.inf, 0, 0))
        
        with self.assertRaises(CameraError):
            Camera(position=(1, 2))  # Wrong dimension
    
    def test_set_position(self):
        """Test setting camera position."""
        new_position = (100, 200, 300)
        self.camera.set_position(new_position)
        self.assertTrue(np.allclose(self.camera.position, new_position))
    
    def test_set_target(self):
        """Test setting camera target."""
        new_target = (10, 20, 30)
        self.camera.set_target(new_target)
        self.assertTrue(np.allclose(self.camera.target, new_target))
    
    def test_set_up_vector(self):
        """Test setting camera up vector."""
        new_up = (0, 1, 0)
        self.camera.set_up_vector(new_up)
        self.assertTrue(np.allclose(self.camera.up_vector, new_up))
    
    def test_get_view_matrix(self):
        """Test view matrix calculation."""
        view_matrix = self.camera.get_view_matrix()
        
        # Check matrix shape
        self.assertEqual(view_matrix.shape, (4, 4))
        
        # Check that it's a valid transformation matrix
        self.assertTrue(np.allclose(view_matrix[3, :3], [0, 0, 0]))
        self.assertAlmostEqual(view_matrix[3, 3], 1.0)
    
    def test_orbit(self):
        """Test camera orbit functionality."""
        original_position = self.camera.position.copy()
        
        # Orbit camera
        self.camera.orbit(45, 30)
        
        # Position should change
        self.assertFalse(np.allclose(self.camera.position, original_position))
        
        # Distance from target should remain approximately the same
        original_distance = np.linalg.norm(original_position - self.camera.target)
        new_distance = np.linalg.norm(self.camera.position - self.camera.target)
        self.assertAlmostEqual(original_distance, new_distance, places=5)
    
    def test_orbit_edge_cases(self):
        """Test camera orbit edge cases."""
        # Test with camera at target (zero distance)
        self.camera.set_position((0, 0, 0))
        self.camera.set_target((0, 0, 0))
        
        # Should not raise error
        self.camera.orbit(45, 30)
        self.assertTrue(np.allclose(self.camera.position, [0, 0, 0]))
    
    def test_zoom(self):
        """Test camera zoom functionality."""
        original_distance = np.linalg.norm(self.camera.position - self.camera.target)
        
        # Zoom in
        self.camera.zoom(2.0)
        new_distance = np.linalg.norm(self.camera.position - self.camera.target)
        self.assertAlmostEqual(new_distance, original_distance / 2.0, places=5)
        
        # Zoom out
        self.camera.zoom(0.5)
        final_distance = np.linalg.norm(self.camera.position - self.camera.target)
        self.assertAlmostEqual(final_distance, original_distance, places=5)
    
    def test_zoom_invalid_factor(self):
        """Test zoom with invalid factor."""
        with self.assertRaises(CameraError):
            self.camera.zoom(0)
        
        with self.assertRaises(CameraError):
            self.camera.zoom(-1)
    
    def test_zoom_zero_distance(self):
        """Test zoom when camera is at target."""
        self.camera.set_position((0, 0, 0))
        self.camera.set_target((0, 0, 0))
        
        # Should not raise error
        self.camera.zoom(2.0)
        self.assertTrue(np.allclose(self.camera.position, [0, 0, 0]))


class TestLight(unittest.TestCase):
    """Test cases for Light class."""
    
    def test_light_initialization(self):
        """Test light initialization with default values."""
        light = Light()
        
        self.assertEqual(light.light_type, 'directional')
        self.assertTrue(np.allclose(light.position, [10, 10, 10]))
        self.assertEqual(light.intensity, 1.0)
        self.assertTrue(np.allclose(light.color, [1.0, 1.0, 1.0]))
    
    def test_light_custom_initialization(self):
        """Test light initialization with custom values."""
        light = Light('ambient', (0, 0, 0), 0.5, (0.8, 0.9, 1.0))
        
        self.assertEqual(light.light_type, 'ambient')
        self.assertTrue(np.allclose(light.position, [0, 0, 0]))
        self.assertEqual(light.intensity, 0.5)
        self.assertTrue(np.allclose(light.color, [0.8, 0.9, 1.0]))
    
    def test_light_invalid_type(self):
        """Test light with invalid type."""
        with self.assertRaises(LightingError):
            Light('invalid_type')
    
    def test_light_invalid_intensity(self):
        """Test light with invalid intensity."""
        with self.assertRaises(LightingError):
            Light(intensity=-1.0)
        
        with self.assertRaises(LightingError):
            Light(intensity='invalid')
    
    def test_light_invalid_color(self):
        """Test light with invalid color."""
        with self.assertRaises(LightingError):
            Light(color=(1.0, 1.0))  # Wrong dimension
        
        with self.assertRaises(LightingError):
            Light(color=(1.0, 1.0, 2.0))  # Out of range
        
        with self.assertRaises(LightingError):
            Light(color=(-0.1, 1.0, 1.0))  # Negative value
    
    def test_light_invalid_position(self):
        """Test light with invalid position."""
        with self.assertRaises(LightingError):
            Light(position=(np.inf, 0, 0))
    
    def test_set_intensity(self):
        """Test setting light intensity."""
        light = Light()
        light.set_intensity(0.7)
        self.assertEqual(light.intensity, 0.7)
        
        with self.assertRaises(LightingError):
            light.set_intensity(-1.0)
    
    def test_set_color(self):
        """Test setting light color."""
        light = Light()
        new_color = (0.8, 0.9, 1.0)
        light.set_color(new_color)
        self.assertTrue(np.allclose(light.color, new_color))
        
        with self.assertRaises(LightingError):
            light.set_color((1.0, 1.0, 2.0))
    
    def test_set_position(self):
        """Test setting light position."""
        light = Light()
        new_position = (5, 10, 15)
        light.set_position(new_position)
        self.assertTrue(np.allclose(light.position, new_position))
        
        with self.assertRaises(LightingError):
            light.set_position((np.nan, 0, 0))


class TestRenderer(unittest.TestCase):
    """Test cases for Renderer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test mesh data
        self.test_mesh = {
            'vertices': np.array([
                [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
            ]),
            'faces': [
                [0, 1, 2], [0, 2, 3],  # Bottom
                [4, 7, 6], [4, 6, 5],  # Top
                [0, 4, 5], [0, 5, 1],  # Front
                [2, 6, 7], [2, 7, 3],  # Back
                [0, 3, 7], [0, 7, 4],  # Left
                [1, 5, 6], [1, 6, 2]   # Right
            ],
            'normals': [(0, 0, -1)] * 2 + [(0, 0, 1)] * 2 + 
                      [(0, -1, 0)] * 2 + [(0, 1, 0)] * 2 + 
                      [(-1, 0, 0)] * 2 + [(1, 0, 0)] * 2
        }
    
    @patch('renderer.plt')
    def test_renderer_initialization_matplotlib(self, mock_plt):
        """Test renderer initialization with matplotlib backend."""
        renderer = Renderer('matplotlib')
        
        self.assertEqual(renderer.backend, 'matplotlib')
        self.assertIsInstance(renderer.camera, Camera)
        self.assertEqual(len(renderer.lights), 3)  # Default lighting
        self.assertEqual(renderer.render_mode, 'shaded')
    
    def test_renderer_invalid_backend(self):
        """Test renderer with invalid backend."""
        with self.assertRaises(RenderingError):
            Renderer('invalid_backend')
    
    @patch('renderer.plt', None)
    def test_renderer_matplotlib_unavailable(self):
        """Test renderer when matplotlib is unavailable."""
        with self.assertRaises(RenderingError):
            Renderer('matplotlib')
    
    @patch('renderer.MAYAVI_AVAILABLE', False)
    def test_renderer_mayavi_unavailable(self):
        """Test renderer when mayavi is unavailable."""
        with self.assertRaises(RenderingError):
            Renderer('mayavi')
    
    @patch('renderer.plt')
    def test_setup_scene_matplotlib(self, mock_plt):
        """Test scene setup with matplotlib."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        renderer.setup_scene((1024, 768))
        
        self.assertEqual(renderer.resolution, (1024, 768))
        mock_plt.figure.assert_called()
        mock_figure.add_subplot.assert_called_with(111, projection='3d')
    
    @patch('renderer.plt')
    def test_set_camera(self, mock_plt):
        """Test setting camera parameters."""
        renderer = Renderer('matplotlib')
        
        position = (100, 200, 300)
        target = (10, 20, 30)
        up_vector = (0, 1, 0)
        
        renderer.set_camera(position, target, up_vector)
        
        self.assertTrue(np.allclose(renderer.camera.position, position))
        self.assertTrue(np.allclose(renderer.camera.target, target))
        self.assertTrue(np.allclose(renderer.camera.up_vector, up_vector))
    
    @patch('renderer.plt')
    def test_add_lighting(self, mock_plt):
        """Test adding lighting to scene."""
        renderer = Renderer('matplotlib')
        initial_light_count = len(renderer.lights)
        
        renderer.add_lighting('point', (5, 5, 5), 0.8, (1.0, 0.8, 0.6))
        
        self.assertEqual(len(renderer.lights), initial_light_count + 1)
        new_light = renderer.lights[-1]
        self.assertEqual(new_light.light_type, 'point')
        self.assertEqual(new_light.intensity, 0.8)
    
    def test_validate_mesh_data(self):
        """Test mesh data validation."""
        with patch('renderer.plt'):
            renderer = Renderer('matplotlib')
        
        # Valid mesh
        self.assertTrue(renderer._validate_mesh_data(self.test_mesh))
        
        # Missing vertices
        invalid_mesh = {'faces': [[0, 1, 2]]}
        self.assertFalse(renderer._validate_mesh_data(invalid_mesh))
        
        # Missing faces
        invalid_mesh = {'vertices': [[0, 0, 0]]}
        self.assertFalse(renderer._validate_mesh_data(invalid_mesh))
        
        # Empty vertices
        invalid_mesh = {'vertices': [], 'faces': []}
        self.assertFalse(renderer._validate_mesh_data(invalid_mesh))
    
    @patch('renderer.plt')
    def test_render_mesh_invalid_data(self, mock_plt):
        """Test rendering with invalid mesh data."""
        renderer = Renderer('matplotlib')
        
        invalid_mesh = {'vertices': [], 'faces': []}
        
        with self.assertRaises(RenderingError):
            renderer.render_mesh(invalid_mesh)
    
    @patch('renderer.plt')
    def test_render_modes(self, mock_plt):
        """Test different rendering modes."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        renderer.setup_scene()
        
        # Test all render modes
        for mode in ['wireframe', 'solid', 'shaded']:
            renderer.set_render_mode(mode)
            self.assertEqual(renderer.render_mode, mode)
            
            # Should not raise error
            renderer.render_mesh(self.test_mesh)
    
    @patch('renderer.plt')
    def test_set_render_mode_invalid(self, mock_plt):
        """Test setting invalid render mode."""
        renderer = Renderer('matplotlib')
        
        with self.assertRaises(RenderingError):
            renderer.set_render_mode('invalid_mode')
    
    @patch('renderer.plt')
    def test_set_background_color(self, mock_plt):
        """Test setting background color."""
        renderer = Renderer('matplotlib')
        
        new_color = (0.2, 0.3, 0.4)
        renderer.set_background_color(new_color)
        self.assertEqual(renderer.background_color, new_color)
        
        # Invalid color
        with self.assertRaises(RenderingError):
            renderer.set_background_color((1.0, 1.0))  # Wrong dimension
        
        with self.assertRaises(RenderingError):
            renderer.set_background_color((1.0, 1.0, 2.0))  # Out of range
    
    @patch('renderer.plt')
    def test_enable_wireframe_overlay(self, mock_plt):
        """Test wireframe overlay functionality."""
        renderer = Renderer('matplotlib')
        
        # Enable wireframe
        renderer.enable_wireframe_overlay(True, (0.5, 0.5, 0.5), 2.0)
        self.assertTrue(renderer.show_wireframe)
        self.assertEqual(renderer.wireframe_color, (0.5, 0.5, 0.5))
        self.assertEqual(renderer.wireframe_width, 2.0)
        
        # Disable wireframe
        renderer.enable_wireframe_overlay(False)
        self.assertFalse(renderer.show_wireframe)
        
        # Invalid color
        with self.assertRaises(RenderingError):
            renderer.enable_wireframe_overlay(True, (1.0, 1.0, 2.0))
        
        # Invalid width
        with self.assertRaises(RenderingError):
            renderer.enable_wireframe_overlay(True, width=-1.0)
    
    @patch('renderer.plt')
    def test_clear_scene(self, mock_plt):
        """Test clearing scene."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        renderer.setup_scene()
        
        # Should not raise error
        renderer.clear_scene()
        mock_axes.clear.assert_called()
    
    @patch('renderer.plt')
    def test_save_image(self, mock_plt):
        """Test saving rendered image."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        renderer.setup_scene()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output.png"
            
            # Should not raise error
            renderer.save_image(output_path, 'PNG', 150)
            mock_figure.savefig.assert_called()
    
    @patch('renderer.plt')
    def test_save_image_no_scene(self, mock_plt):
        """Test saving image without scene."""
        renderer = Renderer('matplotlib')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output.png"
            
            with self.assertRaises(RenderingError):
                renderer.save_image(output_path)
    
    @patch('renderer.plt')
    def test_show_preview(self, mock_plt):
        """Test showing preview."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        renderer.setup_scene()
        
        # Should not raise error
        renderer.show_preview(interactive=True)
        mock_plt.ion.assert_called()
        mock_plt.show.assert_called()
    
    @patch('renderer.plt')
    def test_show_preview_no_scene(self, mock_plt):
        """Test showing preview without scene."""
        renderer = Renderer('matplotlib')
        
        with self.assertRaises(RenderingError):
            renderer.show_preview()
    
    @patch('renderer.plt')
    def test_calculate_face_color(self, mock_plt):
        """Test face color calculation with lighting."""
        renderer = Renderer('matplotlib')
        
        normal = (0, 0, 1)  # Pointing up
        material = {'color': (0.8, 0.8, 0.8)}
        
        color = renderer._calculate_face_color(normal, material)
        
        # Should return a valid RGB tuple
        self.assertEqual(len(color), 3)
        self.assertTrue(all(0 <= c <= 1 for c in color))
    
    @patch('renderer.plt')
    def test_fit_view_matplotlib(self, mock_plt):
        """Test fitting view to vertices."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        renderer.setup_scene()
        
        vertices = self.test_mesh['vertices']
        
        # Should not raise error
        renderer._fit_view_matplotlib(vertices)
        
        # Check that axis limits were set
        mock_axes.set_xlim.assert_called()
        mock_axes.set_ylim.assert_called()
        mock_axes.set_zlim.assert_called()
    
    @patch('renderer.plt')
    def test_fit_view_empty_vertices(self, mock_plt):
        """Test fitting view with empty vertices."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        renderer.setup_scene()
        
        # Should not raise error with empty vertices
        renderer._fit_view_matplotlib(np.array([]))


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    @patch('renderer.plt')
    def test_create_default_renderer(self, mock_plt):
        """Test creating default renderer."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = create_default_renderer('matplotlib')
        
        self.assertIsInstance(renderer, Renderer)
        self.assertEqual(renderer.backend, 'matplotlib')
    
    @patch('renderer.plt', None)
    def test_create_default_renderer_failure(self):
        """Test creating default renderer with unavailable backend."""
        with self.assertRaises(RenderingError):
            create_default_renderer('matplotlib')
    
    @patch('renderer.plt')
    def test_render_mesh_quick(self, mock_plt):
        """Test quick render function."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        test_mesh = {
            'vertices': np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]),
            'faces': [[0, 1, 2]]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "quick_render.png"
            
            renderer = render_mesh_quick(
                test_mesh, 
                output_file=output_path,
                backend='matplotlib',
                show_preview=False
            )
            
            self.assertIsInstance(renderer, Renderer)
    
    @patch('renderer.plt', None)
    def test_render_mesh_quick_failure(self):
        """Test quick render function failure."""
        test_mesh = {
            'vertices': np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]),
            'faces': [[0, 1, 2]]
        }
        
        result = render_mesh_quick(test_mesh, backend='matplotlib', show_preview=False)
        self.assertIsNone(result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    @patch('renderer.plt')
    def test_mesh_with_no_normals(self, mock_plt):
        """Test rendering mesh without normals."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        renderer.setup_scene()
        
        mesh_without_normals = {
            'vertices': np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]),
            'faces': [[0, 1, 2]]
        }
        
        # Should not raise error
        renderer.render_mesh(mesh_without_normals)
    
    @patch('renderer.plt')
    def test_mesh_with_invalid_faces(self, mock_plt):
        """Test rendering mesh with invalid faces."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        renderer.setup_scene()
        
        mesh_with_invalid_faces = {
            'vertices': np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]),
            'faces': [[0, 1], [0]]  # Invalid faces with < 3 vertices
        }
        
        # Should handle gracefully
        renderer.render_mesh(mesh_with_invalid_faces)
    
    @patch('renderer.plt')
    def test_large_mesh_warning(self, mock_plt):
        """Test warning for large meshes."""
        mock_figure = Mock()
        mock_axes = Mock()
        mock_plt.figure.return_value = mock_figure
        mock_figure.add_subplot.return_value = mock_axes
        
        renderer = Renderer('matplotlib')
        
        # Create large mesh (exceeding MAX_VERTICES_PER_MESH)
        large_vertices = np.random.rand(200000, 3)  # Exceeds typical limit
        large_faces = [[i, i+1, i+2] for i in range(0, len(large_vertices)-2, 3)]
        
        large_mesh = {
            'vertices': large_vertices,
            'faces': large_faces
        }
        
        with self.assertLogs(level='WARNING'):
            renderer._validate_mesh_data(large_mesh)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)