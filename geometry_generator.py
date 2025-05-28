"""
Geometry Generator Module for 3D Text Generator

This module provides functionality for converting 2D character outlines
to 3D meshes through extrusion, beveling, and mesh optimization.
"""

import logging
from typing import List, Tuple, Dict, Optional, Union
import numpy as np
from pathlib import Path

try:
    import trimesh
except ImportError:
    trimesh = None
    logging.warning("trimesh not available. 3D mesh functionality will be limited.")

try:
    from scipy.spatial import Delaunay
    from scipy.spatial.distance import cdist
except ImportError:
    Delaunay = None
    cdist = None
    logging.warning("scipy not available. Advanced mesh operations will be limited.")

from config import Config
from utils import validate_numeric_input


class GeometryError(Exception):
    """Exception raised when geometry operations fail."""
    pass


class MeshValidationError(Exception):
    """Exception raised when mesh validation fails."""
    pass


class GeometryGenerator:
    """
    Handles conversion of 2D character outlines to 3D meshes.
    """
    
    def __init__(self):
        self.default_depth = Config.DEFAULT_EXTRUSION_DEPTH
        self.default_bevel_depth = Config.DEFAULT_BEVEL_DEPTH
        self.default_bevel_resolution = Config.DEFAULT_BEVEL_RESOLUTION
        self.mesh_resolution = Config.DEFAULT_MESH_RESOLUTION
        
    def extrude_outline(self, outline: List[Tuple[float, float]], depth: float) -> Dict:
        """
        Extrude a 2D outline to create a 3D mesh.
        
        Args:
            outline: List of (x, y) points defining the outline
            depth: Extrusion depth along Z-axis
            
        Returns:
            Dictionary containing vertices, faces, and normals
            
        Raises:
            GeometryError: If extrusion fails
        """
        if not outline or len(outline) < 3:
            raise GeometryError("Outline must contain at least 3 points")
        
        if not validate_numeric_input(depth) or depth <= 0:
            raise GeometryError("Depth must be a positive number")
        
        try:
            # Ensure outline is closed
            if outline[0] != outline[-1]:
                outline = outline + [outline[0]]
            
            # Create vertices for bottom and top faces
            bottom_vertices = [(x, y, 0.0) for x, y in outline[:-1]]  # Exclude duplicate last point
            top_vertices = [(x, y, depth) for x, y in outline[:-1]]
            
            vertices = bottom_vertices + top_vertices
            
            # Generate faces
            faces = self._generate_extrusion_faces(len(bottom_vertices))
            
            # Calculate normals
            normals = self.calculate_normals(vertices, faces)
            
            mesh_data = {
                'vertices': np.array(vertices),
                'faces': np.array(faces),
                'normals': np.array(normals)
            }
            
            return mesh_data
            
        except Exception as e:
            raise GeometryError(f"Failed to extrude outline: {str(e)}")
    
    def _generate_extrusion_faces(self, num_vertices: int) -> List[List[int]]:
        """Generate faces for extruded geometry."""
        faces = []
        
        # Bottom face (triangulated)
        if num_vertices >= 3:
            bottom_faces = self._triangulate_polygon(list(range(num_vertices)))
            faces.extend(bottom_faces)
        
        # Top face (triangulated, reversed for correct normal)
        if num_vertices >= 3:
            top_indices = list(range(num_vertices, 2 * num_vertices))
            top_faces = self._triangulate_polygon(top_indices)
            # Reverse face orientation for outward normals
            top_faces = [face[::-1] for face in top_faces]
            faces.extend(top_faces)
        
        # Side faces
        for i in range(num_vertices):
            next_i = (i + 1) % num_vertices
            
            # Two triangles per side face
            # Triangle 1: bottom_i, top_i, bottom_next
            faces.append([i, i + num_vertices, next_i])
            # Triangle 2: bottom_next, top_i, top_next
            faces.append([next_i, i + num_vertices, next_i + num_vertices])
        
        return faces
    
    def _triangulate_polygon(self, indices: List[int]) -> List[List[int]]:
        """Triangulate a polygon using simple fan triangulation."""
        if len(indices) < 3:
            return []
        
        if len(indices) == 3:
            return [indices]
        
        # Simple fan triangulation from first vertex
        triangles = []
        for i in range(1, len(indices) - 1):
            triangles.append([indices[0], indices[i], indices[i + 1]])
        
        return triangles
    
    def generate_mesh(self, outlines: List[List[Tuple[float, float]]], 
                     depth: float, bevel_depth: float = 0.0) -> Dict:
        """
        Generate a complete 3D mesh from multiple outlines with optional beveling.
        
        Args:
            outlines: List of outlines (contours) for the character
            depth: Extrusion depth
            bevel_depth: Depth of bevel effect (0 for no bevel)
            
        Returns:
            Dictionary containing combined mesh data
            
        Raises:
            GeometryError: If mesh generation fails
        """
        if not outlines:
            raise GeometryError("No outlines provided")
        
        if not validate_numeric_input(depth) or depth <= 0:
            raise GeometryError("Depth must be a positive number")
        
        if not validate_numeric_input(bevel_depth) or bevel_depth < 0:
            raise GeometryError("Bevel depth must be non-negative")
        
        try:
            all_vertices = []
            all_faces = []
            vertex_offset = 0
            
            for outline in outlines:
                if len(outline) < 3:
                    logging.warning(f"Skipping outline with {len(outline)} points")
                    continue
                
                # Generate mesh for this outline
                if bevel_depth > 0:
                    mesh_data = self._generate_beveled_mesh(outline, depth, bevel_depth)
                else:
                    mesh_data = self.extrude_outline(outline, depth)
                
                # Add vertices with offset
                all_vertices.extend(mesh_data['vertices'])
                
                # Add faces with vertex offset
                offset_faces = [[f[0] + vertex_offset, f[1] + vertex_offset, f[2] + vertex_offset] 
                               for f in mesh_data['faces']]
                all_faces.extend(offset_faces)
                
                vertex_offset += len(mesh_data['vertices'])
            
            if not all_vertices:
                raise GeometryError("No valid geometry generated")
            
            # Combine all mesh data
            combined_mesh = {
                'vertices': np.array(all_vertices),
                'faces': np.array(all_faces),
                'normals': self.calculate_normals(all_vertices, all_faces)
            }
            
            # Optimize the mesh
            optimized_mesh = self.optimize_mesh(combined_mesh)
            
            return optimized_mesh
            
        except Exception as e:
            raise GeometryError(f"Failed to generate mesh: {str(e)}")
    
    def _generate_beveled_mesh(self, outline: List[Tuple[float, float]], 
                              depth: float, bevel_depth: float) -> Dict:
        """
        Generate a mesh with bevel effects.
        
        Args:
            outline: 2D outline points
            depth: Total extrusion depth
            bevel_depth: Depth of bevel effect
            
        Returns:
            Mesh data with bevel geometry
        """
        if bevel_depth >= depth:
            logging.warning("Bevel depth >= extrusion depth, using simple extrusion")
            return self.extrude_outline(outline, depth)
        
        # Create multiple levels for bevel effect
        bevel_steps = max(2, self.default_bevel_resolution)
        step_height = bevel_depth / bevel_steps
        
        all_vertices = []
        all_faces = []
        
        # Generate vertices for each bevel level
        for step in range(bevel_steps + 1):
            z = step * step_height
            # Simple linear bevel (could be enhanced with curves)
            scale = 1.0 - (step * 0.1 / bevel_steps)  # Slight inward scaling
            
            level_vertices = []
            for x, y in outline:
                # Apply scaling for bevel effect
                scaled_x = x * scale
                scaled_y = y * scale
                level_vertices.append((scaled_x, scaled_y, z))
            
            all_vertices.extend(level_vertices)
        
        # Add top level vertices (no bevel)
        top_vertices = [(x, y, depth) for x, y in outline]
        all_vertices.extend(top_vertices)
        
        # Generate faces connecting the levels
        vertices_per_level = len(outline)
        total_levels = bevel_steps + 2  # Including bottom and top
        
        faces = []
        
        # Connect adjacent levels
        for level in range(total_levels - 1):
            for i in range(vertices_per_level):
                next_i = (i + 1) % vertices_per_level
                
                # Current level indices
                curr_base = level * vertices_per_level
                next_base = (level + 1) * vertices_per_level
                
                # Two triangles per quad
                faces.append([curr_base + i, next_base + i, curr_base + next_i])
                faces.append([curr_base + next_i, next_base + i, next_base + next_i])
        
        # Add bottom and top faces
        bottom_faces = self._triangulate_polygon(list(range(vertices_per_level)))
        faces.extend(bottom_faces)
        
        top_start = (total_levels - 1) * vertices_per_level
        top_indices = list(range(top_start, top_start + vertices_per_level))
        top_faces = self._triangulate_polygon(top_indices)
        top_faces = [face[::-1] for face in top_faces]  # Reverse for correct normals
        faces.extend(top_faces)
        
        return {
            'vertices': np.array(all_vertices),
            'faces': np.array(faces),
            'normals': self.calculate_normals(all_vertices, faces)
        }
    
    def optimize_mesh(self, mesh: Dict) -> Dict:
        """
        Optimize mesh by removing duplicate vertices and degenerate faces.
        
        Args:
            mesh: Mesh data dictionary
            
        Returns:
            Optimized mesh data
            
        Raises:
            MeshValidationError: If mesh optimization fails
        """
        try:
            vertices = mesh['vertices']
            faces = mesh['faces']
            
            if len(vertices) == 0 or len(faces) == 0:
                raise MeshValidationError("Empty mesh provided")
            
            # Remove duplicate vertices
            unique_vertices, vertex_map = self._remove_duplicate_vertices(vertices)
            
            # Update face indices
            updated_faces = []
            for face in faces:
                new_face = [vertex_map[idx] for idx in face]
                
                # Skip degenerate faces (where all vertices are the same)
                if len(set(new_face)) >= 3:
                    updated_faces.append(new_face)
            
            if not updated_faces:
                raise MeshValidationError("No valid faces after optimization")
            
            # Recalculate normals
            normals = self.calculate_normals(unique_vertices, updated_faces)
            
            optimized_mesh = {
                'vertices': np.array(unique_vertices),
                'faces': np.array(updated_faces),
                'normals': np.array(normals)
            }
            
            # Validate the optimized mesh
            self._validate_mesh(optimized_mesh)
            
            return optimized_mesh
            
        except Exception as e:
            raise MeshValidationError(f"Failed to optimize mesh: {str(e)}")
    
    def _remove_duplicate_vertices(self, vertices: np.ndarray, tolerance: float = 1e-6) -> Tuple[List, Dict]:
        """Remove duplicate vertices and return mapping."""
        unique_vertices = []
        vertex_map = {}
        
        for i, vertex in enumerate(vertices):
            # Find if this vertex already exists
            found_duplicate = False
            for j, unique_vertex in enumerate(unique_vertices):
                if np.allclose(vertex, unique_vertex, atol=tolerance):
                    vertex_map[i] = j
                    found_duplicate = True
                    break
            
            if not found_duplicate:
                vertex_map[i] = len(unique_vertices)
                unique_vertices.append(vertex)
        
        return unique_vertices, vertex_map
    
    def calculate_normals(self, vertices: List, faces: List) -> List[Tuple[float, float, float]]:
        """
        Calculate normal vectors for mesh faces.
        
        Args:
            vertices: List of vertex coordinates
            faces: List of face indices
            
        Returns:
            List of normal vectors for each face
        """
        if not vertices or not faces:
            return []
        
        vertices = np.array(vertices)
        normals = []
        
        for face in faces:
            if len(face) < 3:
                normals.append((0.0, 0.0, 1.0))  # Default normal
                continue
            
            try:
                # Get three vertices of the face
                v1 = vertices[face[0]]
                v2 = vertices[face[1]]
                v3 = vertices[face[2]]
                
                # Calculate two edge vectors
                edge1 = v2 - v1
                edge2 = v3 - v1
                
                # Calculate normal using cross product
                normal = np.cross(edge1, edge2)
                
                # Normalize the normal vector
                norm_length = np.linalg.norm(normal)
                if norm_length > 0:
                    normal = normal / norm_length
                else:
                    normal = np.array([0.0, 0.0, 1.0])  # Default normal
                
                normals.append(tuple(normal))
                
            except (IndexError, ValueError):
                normals.append((0.0, 0.0, 1.0))  # Default normal for invalid faces
        
        return normals
    
    def _validate_mesh(self, mesh: Dict) -> bool:
        """
        Validate mesh data for correctness.
        
        Args:
            mesh: Mesh data dictionary
            
        Returns:
            True if mesh is valid
            
        Raises:
            MeshValidationError: If mesh is invalid
        """
        vertices = mesh.get('vertices', [])
        faces = mesh.get('faces', [])
        
        if len(vertices) == 0:
            raise MeshValidationError("Mesh has no vertices")
        
        if len(faces) == 0:
            raise MeshValidationError("Mesh has no faces")
        
        # Check vertex dimensions
        if vertices.shape[1] != 3:
            raise MeshValidationError("Vertices must be 3D coordinates")
        
        # Check face indices
        max_vertex_index = len(vertices) - 1
        for i, face in enumerate(faces):
            if len(face) < 3:
                raise MeshValidationError(f"Face {i} has less than 3 vertices")
            
            for vertex_idx in face:
                if vertex_idx < 0 or vertex_idx > max_vertex_index:
                    raise MeshValidationError(f"Face {i} references invalid vertex index {vertex_idx}")
        
        # Check for NaN or infinite values
        if np.any(~np.isfinite(vertices)):
            raise MeshValidationError("Mesh contains NaN or infinite vertex coordinates")
        
        return True
    
    def get_mesh_info(self, mesh: Dict) -> Dict:
        """
        Get information about a mesh.
        
        Args:
            mesh: Mesh data dictionary
            
        Returns:
            Dictionary with mesh statistics
        """
        vertices = mesh.get('vertices', [])
        faces = mesh.get('faces', [])
        
        info = {
            'vertex_count': len(vertices),
            'face_count': len(faces),
            'triangle_count': len([f for f in faces if len(f) == 3]),
            'quad_count': len([f for f in faces if len(f) == 4])
        }
        
        if len(vertices) > 0:
            vertices = np.array(vertices)
            info.update({
                'bounds_min': tuple(np.min(vertices, axis=0)),
                'bounds_max': tuple(np.max(vertices, axis=0)),
                'center': tuple(np.mean(vertices, axis=0))
            })
        
        return info
    
    def export_to_trimesh(self, mesh: Dict) -> Optional[object]:
        """
        Convert mesh data to trimesh object for advanced operations.
        
        Args:
            mesh: Mesh data dictionary
            
        Returns:
            Trimesh object or None if trimesh not available
        """
        if not trimesh:
            logging.warning("Trimesh not available for export")
            return None
        
        try:
            vertices = mesh['vertices']
            faces = mesh['faces']
            
            # Convert faces to triangles only (trimesh requirement)
            triangle_faces = []
            for face in faces:
                if len(face) == 3:
                    triangle_faces.append(face)
                elif len(face) == 4:
                    # Split quad into two triangles
                    triangle_faces.append([face[0], face[1], face[2]])
                    triangle_faces.append([face[0], face[2], face[3]])
            
            mesh_obj = trimesh.Trimesh(vertices=vertices, faces=triangle_faces)
            return mesh_obj
            
        except Exception as e:
            logging.error(f"Failed to create trimesh object: {e}")
            return None


# Utility functions

def validate_outline(outline: List[Tuple[float, float]]) -> bool:
    """
    Validate that an outline is suitable for 3D extrusion.
    
    Args:
        outline: List of (x, y) coordinate tuples
        
    Returns:
        True if outline is valid
    """
    if not outline or len(outline) < 3:
        return False
    
    # Check that all points are valid numbers
    for point in outline:
        if len(point) != 2:
            return False
        x, y = point
        if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
            return False
        if not (np.isfinite(x) and np.isfinite(y)):
            return False
    
    return True


def calculate_outline_area(outline: List[Tuple[float, float]]) -> float:
    """
    Calculate the area of a 2D outline using the shoelace formula.
    
    Args:
        outline: List of (x, y) coordinate tuples
        
    Returns:
        Area of the outline (positive for counter-clockwise, negative for clockwise)
    """
    if len(outline) < 3:
        return 0.0
    
    area = 0.0
    n = len(outline)
    
    for i in range(n):
        j = (i + 1) % n
        area += outline[i][0] * outline[j][1]
        area -= outline[j][0] * outline[i][1]
    
    return area / 2.0


def is_outline_clockwise(outline: List[Tuple[float, float]]) -> bool:
    """
    Determine if an outline is oriented clockwise.
    
    Args:
        outline: List of (x, y) coordinate tuples
        
    Returns:
        True if outline is clockwise
    """
    return calculate_outline_area(outline) < 0


# Example usage and testing
if __name__ == "__main__":
    # Basic testing
    try:
        generator = GeometryGenerator()
        
        # Test with a simple square outline
        square_outline = [(0, 0), (10, 0), (10, 10), (0, 10)]
        
        print(f"Testing with square outline: {square_outline}")
        print(f"Outline valid: {validate_outline(square_outline)}")
        print(f"Outline area: {calculate_outline_area(square_outline)}")
        print(f"Clockwise: {is_outline_clockwise(square_outline)}")
        
        # Test extrusion
        mesh = generator.extrude_outline(square_outline, 5.0)
        print(f"\nExtruded mesh info:")
        info = generator.get_mesh_info(mesh)
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Test mesh generation with multiple outlines
        outlines = [square_outline]
        combined_mesh = generator.generate_mesh(outlines, 5.0, 1.0)
        print(f"\nCombined mesh info:")
        combined_info = generator.get_mesh_info(combined_mesh)
        for key, value in combined_info.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error during testing: {e}")