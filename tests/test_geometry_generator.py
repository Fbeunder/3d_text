"""
Unit tests for the Geometry Generator module.

Tests cover mesh generation, extrusion, beveling, optimization,
and validation functionality.
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geometry_generator import (
    GeometryGenerator, GeometryError, MeshValidationError,
    validate_outline, calculate_outline_area, is_outline_clockwise
)


class TestGeometryGenerator(unittest.TestCase):
    """Test cases for GeometryGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = GeometryGenerator()
        self.square_outline = [(0, 0), (10, 0), (10, 10), (0, 10)]
        self.triangle_outline = [(0, 0), (5, 0), (2.5, 5)]
        self.invalid_outline = [(0, 0), (1, 1)]  # Too few points
    
    def test_init(self):
        """Test GeometryGenerator initialization."""
        self.assertIsInstance(self.generator, GeometryGenerator)
        self.assertGreater(self.generator.default_depth, 0)
        self.assertGreaterEqual(self.generator.default_bevel_depth, 0)
    
    def test_extrude_outline_valid(self):
        """Test successful outline extrusion."""
        depth = 5.0
        mesh = self.generator.extrude_outline(self.square_outline, depth)
        
        self.assertIn('vertices', mesh)
        self.assertIn('faces', mesh)
        self.assertIn('normals', mesh)
        
        vertices = mesh['vertices']
        faces = mesh['faces']
        
        # Should have 8 vertices (4 bottom + 4 top)
        self.assertEqual(len(vertices), 8)
        
        # Check that top vertices are at correct depth
        top_vertices = vertices[4:8]
        for vertex in top_vertices:
            self.assertAlmostEqual(vertex[2], depth, places=5)
        
        # Check that bottom vertices are at z=0
        bottom_vertices = vertices[0:4]
        for vertex in bottom_vertices:
            self.assertAlmostEqual(vertex[2], 0.0, places=5)
        
        # Should have faces
        self.assertGreater(len(faces), 0)
    
    def test_extrude_outline_invalid_input(self):
        """Test extrusion with invalid input."""
        # Test with too few points
        with self.assertRaises(GeometryError):
            self.generator.extrude_outline(self.invalid_outline, 5.0)
        
        # Test with invalid depth
        with self.assertRaises(GeometryError):
            self.generator.extrude_outline(self.square_outline, -1.0)
        
        with self.assertRaises(GeometryError):
            self.generator.extrude_outline(self.square_outline, 0.0)
        
        # Test with empty outline
        with self.assertRaises(GeometryError):
            self.generator.extrude_outline([], 5.0)
    
    def test_generate_mesh_single_outline(self):
        """Test mesh generation with single outline."""
        outlines = [self.square_outline]
        depth = 5.0
        
        mesh = self.generator.generate_mesh(outlines, depth)
        
        self.assertIn('vertices', mesh)
        self.assertIn('faces', mesh)
        self.assertIn('normals', mesh)
        
        # Verify mesh is valid
        self.assertTrue(self.generator._validate_mesh(mesh))
    
    def test_generate_mesh_multiple_outlines(self):
        """Test mesh generation with multiple outlines."""
        outlines = [self.square_outline, self.triangle_outline]
        depth = 5.0
        
        mesh = self.generator.generate_mesh(outlines, depth)
        
        self.assertIn('vertices', mesh)
        self.assertIn('faces', mesh)
        self.assertIn('normals', mesh)
        
        # Should have more vertices than single outline
        single_mesh = self.generator.generate_mesh([self.square_outline], depth)
        self.assertGreater(len(mesh['vertices']), len(single_mesh['vertices']))
    
    def test_generate_mesh_with_bevel(self):
        """Test mesh generation with bevel effect."""
        outlines = [self.square_outline]
        depth = 5.0
        bevel_depth = 1.0
        
        mesh = self.generator.generate_mesh(outlines, depth, bevel_depth)
        
        self.assertIn('vertices', mesh)
        self.assertIn('faces', mesh)
        
        # Beveled mesh should have more vertices than simple extrusion
        simple_mesh = self.generator.generate_mesh(outlines, depth, 0.0)
        self.assertGreater(len(mesh['vertices']), len(simple_mesh['vertices']))
    
    def test_generate_mesh_invalid_input(self):
        """Test mesh generation with invalid input."""
        # Test with empty outlines
        with self.assertRaises(GeometryError):
            self.generator.generate_mesh([], 5.0)
        
        # Test with invalid depth
        with self.assertRaises(GeometryError):
            self.generator.generate_mesh([self.square_outline], -1.0)
        
        # Test with invalid bevel depth
        with self.assertRaises(GeometryError):
            self.generator.generate_mesh([self.square_outline], 5.0, -1.0)
    
    def test_calculate_normals(self):
        """Test normal vector calculation."""
        vertices = [
            (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)  # Square in XY plane
        ]
        faces = [[0, 1, 2], [0, 2, 3]]  # Two triangles
        
        normals = self.generator.calculate_normals(vertices, faces)
        
        self.assertEqual(len(normals), len(faces))
        
        # For a square in XY plane, normals should point in +Z direction
        for normal in normals:
            self.assertEqual(len(normal), 3)
            # Normal should be unit vector
            length = np.linalg.norm(normal)
            self.assertAlmostEqual(length, 1.0, places=5)
    
    def test_calculate_normals_empty_input(self):
        """Test normal calculation with empty input."""
        normals = self.generator.calculate_normals([], [])
        self.assertEqual(len(normals), 0)
        
        normals = self.generator.calculate_normals([(0, 0, 0)], [])
        self.assertEqual(len(normals), 0)
    
    def test_optimize_mesh(self):
        """Test mesh optimization."""
        # Create mesh with duplicate vertices
        vertices = [
            (0, 0, 0), (1, 0, 0), (1, 1, 0),  # Triangle 1
            (0, 0, 0), (1, 1, 0), (0, 1, 0)   # Triangle 2 (shares vertices)
        ]
        faces = [[0, 1, 2], [3, 4, 5]]
        normals = [(0, 0, 1), (0, 0, 1)]
        
        mesh = {
            'vertices': np.array(vertices),
            'faces': np.array(faces),
            'normals': np.array(normals)
        }
        
        optimized = self.generator.optimize_mesh(mesh)
        
        # Should have fewer vertices after removing duplicates
        self.assertLess(len(optimized['vertices']), len(vertices))
        self.assertIn('faces', optimized)
        self.assertIn('normals', optimized)
    
    def test_optimize_mesh_invalid(self):
        """Test mesh optimization with invalid input."""
        # Test with empty mesh
        empty_mesh = {'vertices': np.array([]), 'faces': np.array([])}
        with self.assertRaises(MeshValidationError):
            self.generator.optimize_mesh(empty_mesh)
    
    def test_validate_mesh_valid(self):
        """Test mesh validation with valid mesh."""
        mesh = self.generator.extrude_outline(self.square_outline, 5.0)
        self.assertTrue(self.generator._validate_mesh(mesh))
    
    def test_validate_mesh_invalid(self):
        """Test mesh validation with invalid meshes."""
        # Test with no vertices
        with self.assertRaises(MeshValidationError):
            self.generator._validate_mesh({'vertices': [], 'faces': []})
        
        # Test with no faces
        with self.assertRaises(MeshValidationError):
            self.generator._validate_mesh({
                'vertices': [(0, 0, 0), (1, 0, 0), (1, 1, 0)],
                'faces': []
            })
        
        # Test with invalid face indices
        with self.assertRaises(MeshValidationError):
            self.generator._validate_mesh({
                'vertices': np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0)]),
                'faces': [[0, 1, 5]]  # Index 5 doesn't exist
            })
    
    def test_get_mesh_info(self):
        """Test mesh information extraction."""
        mesh = self.generator.extrude_outline(self.square_outline, 5.0)
        info = self.generator.get_mesh_info(mesh)
        
        self.assertIn('vertex_count', info)
        self.assertIn('face_count', info)
        self.assertIn('triangle_count', info)
        self.assertIn('bounds_min', info)
        self.assertIn('bounds_max', info)
        self.assertIn('center', info)
        
        self.assertGreater(info['vertex_count'], 0)
        self.assertGreater(info['face_count'], 0)
    
    def test_remove_duplicate_vertices(self):
        """Test duplicate vertex removal."""
        vertices = np.array([
            (0, 0, 0), (1, 0, 0), (0, 0, 0),  # First and third are duplicates
            (1, 1, 0)
        ])
        
        unique_vertices, vertex_map = self.generator._remove_duplicate_vertices(vertices)
        
        # Should have 3 unique vertices
        self.assertEqual(len(unique_vertices), 3)
        
        # Check mapping
        self.assertEqual(vertex_map[0], vertex_map[2])  # Duplicates map to same index
        self.assertNotEqual(vertex_map[0], vertex_map[1])  # Different vertices have different indices
    
    def test_triangulate_polygon(self):
        """Test polygon triangulation."""
        # Test triangle (should return as-is)
        triangle_indices = [0, 1, 2]
        triangles = self.generator._triangulate_polygon(triangle_indices)
        self.assertEqual(len(triangles), 1)
        self.assertEqual(triangles[0], triangle_indices)
        
        # Test square (should return 2 triangles)
        square_indices = [0, 1, 2, 3]
        triangles = self.generator._triangulate_polygon(square_indices)
        self.assertEqual(len(triangles), 2)
        
        # Test invalid input
        triangles = self.generator._triangulate_polygon([0, 1])  # Too few vertices
        self.assertEqual(len(triangles), 0)
    
    @patch('geometry_generator.trimesh')
    def test_export_to_trimesh(self, mock_trimesh):
        """Test export to trimesh object."""
        mock_mesh_obj = MagicMock()
        mock_trimesh.Trimesh.return_value = mock_mesh_obj
        
        mesh = self.generator.extrude_outline(self.square_outline, 5.0)
        result = self.generator.export_to_trimesh(mesh)
        
        self.assertEqual(result, mock_mesh_obj)
        mock_trimesh.Trimesh.assert_called_once()
    
    def test_export_to_trimesh_no_trimesh(self):
        """Test export when trimesh is not available."""
        with patch('geometry_generator.trimesh', None):
            mesh = self.generator.extrude_outline(self.square_outline, 5.0)
            result = self.generator.export_to_trimesh(mesh)
            self.assertIsNone(result)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_validate_outline_valid(self):
        """Test outline validation with valid outlines."""
        valid_outlines = [
            [(0, 0), (1, 0), (1, 1), (0, 1)],  # Square
            [(0, 0), (5, 0), (2.5, 5)],        # Triangle
            [(0, 0), (1, 0), (2, 1), (1, 2), (0, 1)]  # Pentagon
        ]
        
        for outline in valid_outlines:
            self.assertTrue(validate_outline(outline))
    
    def test_validate_outline_invalid(self):
        """Test outline validation with invalid outlines."""
        invalid_outlines = [
            [],                           # Empty
            [(0, 0)],                    # Single point
            [(0, 0), (1, 1)],           # Two points
            [(0, 0), (1, 0), (1,)],     # Invalid point format
            [(0, 0), (1, 0), ('a', 1)], # Non-numeric coordinates
            [(0, 0), (1, 0), (float('inf'), 1)]  # Infinite coordinates
        ]
        
        for outline in invalid_outlines:
            self.assertFalse(validate_outline(outline))
    
    def test_calculate_outline_area(self):
        """Test outline area calculation."""
        # Unit square (counter-clockwise)
        square_ccw = [(0, 0), (1, 0), (1, 1), (0, 1)]
        area_ccw = calculate_outline_area(square_ccw)
        self.assertAlmostEqual(area_ccw, 1.0, places=5)
        
        # Unit square (clockwise)
        square_cw = [(0, 0), (0, 1), (1, 1), (1, 0)]
        area_cw = calculate_outline_area(square_cw)
        self.assertAlmostEqual(area_cw, -1.0, places=5)
        
        # Triangle
        triangle = [(0, 0), (2, 0), (1, 2)]
        area_triangle = calculate_outline_area(triangle)
        self.assertAlmostEqual(area_triangle, 2.0, places=5)
        
        # Invalid outline
        area_invalid = calculate_outline_area([(0, 0), (1, 1)])
        self.assertEqual(area_invalid, 0.0)
    
    def test_is_outline_clockwise(self):
        """Test clockwise orientation detection."""
        # Counter-clockwise square
        square_ccw = [(0, 0), (1, 0), (1, 1), (0, 1)]
        self.assertFalse(is_outline_clockwise(square_ccw))
        
        # Clockwise square
        square_cw = [(0, 0), (0, 1), (1, 1), (1, 0)]
        self.assertTrue(is_outline_clockwise(square_cw))


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = GeometryGenerator()
    
    def test_complete_workflow(self):
        """Test complete mesh generation workflow."""
        # Define character outlines (letter 'H' approximation)
        left_bar = [(0, 0), (2, 0), (2, 10), (0, 10)]
        right_bar = [(8, 0), (10, 0), (10, 10), (8, 10)]
        cross_bar = [(2, 4), (8, 4), (8, 6), (2, 6)]
        
        outlines = [left_bar, right_bar, cross_bar]
        
        # Generate mesh
        mesh = self.generator.generate_mesh(outlines, depth=5.0, bevel_depth=0.5)
        
        # Validate result
        self.assertIn('vertices', mesh)
        self.assertIn('faces', mesh)
        self.assertIn('normals', mesh)
        
        # Check mesh is valid
        self.assertTrue(self.generator._validate_mesh(mesh))
        
        # Get mesh info
        info = self.generator.get_mesh_info(mesh)
        self.assertGreater(info['vertex_count'], 0)
        self.assertGreater(info['face_count'], 0)
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with invalid outline
        with self.assertRaises(GeometryError):
            self.generator.generate_mesh([[(0, 0)]], 5.0)  # Too few points
        
        # Test with invalid parameters
        with self.assertRaises(GeometryError):
            self.generator.generate_mesh([[(0, 0), (1, 0), (1, 1)]], -1.0)  # Negative depth
    
    def test_performance_limits(self):
        """Test with large outlines to check performance."""
        # Create a large outline (circle approximation)
        import math
        num_points = 100
        circle_outline = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = 10 * math.cos(angle)
            y = 10 * math.sin(angle)
            circle_outline.append((x, y))
        
        # Should handle large outlines without error
        mesh = self.generator.generate_mesh([circle_outline], 5.0)
        self.assertIn('vertices', mesh)
        self.assertIn('faces', mesh)
        
        # Check mesh is still valid
        self.assertTrue(self.generator._validate_mesh(mesh))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)