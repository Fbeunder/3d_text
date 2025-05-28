"""
Export Module for 3D Text Generator

This module provides functionality for exporting 3D meshes to various
popular 3D formats including STL, OBJ, PLY, and GLTF.
"""

import logging
import json
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import numpy as np

try:
    import trimesh
except ImportError:
    trimesh = None
    logging.warning("trimesh not available. Export functionality will be limited.")

try:
    from stl import mesh as stl_mesh
except ImportError:
    stl_mesh = None
    logging.warning("numpy-stl not available. STL export will be limited.")

from config import Config
from utils import validate_numeric_input


class ExportError(Exception):
    """Exception raised when export operations fail."""
    pass


class ValidationError(Exception):
    """Exception raised when export validation fails."""
    pass


class Exporter:
    """
    Handles export of 3D meshes to various formats.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the Exporter.
        
        Args:
            output_dir: Directory for output files (defaults to config setting)
        """
        self.output_dir = output_dir or Config.DEFAULT_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.export_scale = Config.DEFAULT_EXPORT_SCALE
        self.supported_formats = Config.SUPPORTED_EXPORT_FORMATS
        
        # Export settings
        self.stl_ascii = False  # Binary STL by default
        self.obj_include_materials = True
        self.ply_ascii = False  # Binary PLY by default
        self.gltf_embed_textures = True
        
        logging.info(f"Exporter initialized with output directory: {self.output_dir}")
    
    def export_mesh(self, mesh: Dict, filename: str, format_type: str, **kwargs) -> Path:
        """
        Export mesh to specified format.
        
        Args:
            mesh: Mesh data dictionary with vertices, faces, and normals
            filename: Output filename (without extension)
            format_type: Export format ('STL', 'OBJ', 'PLY', 'GLTF')
            **kwargs: Format-specific options
            
        Returns:
            Path to exported file
            
        Raises:
            ExportError: If export fails
            ValidationError: If mesh validation fails
        """
        format_type = format_type.upper()
        
        if format_type not in self.supported_formats:
            raise ExportError(f"Unsupported format: {format_type}")
        
        # Validate mesh before export
        self._validate_mesh_for_export(mesh)
        
        # Apply scaling if needed
        scaled_mesh = self._apply_scaling(mesh, kwargs.get('scale', self.export_scale))
        
        # Route to appropriate export method
        export_methods = {
            'STL': self.export_stl,
            'OBJ': self.export_obj,
            'PLY': self.export_ply,
            'GLTF': self.export_gltf
        }
        
        try:
            export_method = export_methods[format_type]
            output_path = export_method(scaled_mesh, filename, **kwargs)
            
            # Validate exported file
            self.validate_export(output_path, format_type)
            
            logging.info(f"Successfully exported {format_type} file: {output_path}")
            return output_path
            
        except Exception as e:
            raise ExportError(f"Failed to export {format_type}: {str(e)}")
    
    def export_stl(self, mesh: Dict, filename: str, **kwargs) -> Path:
        """
        Export mesh to STL format.
        
        Args:
            mesh: Mesh data dictionary
            filename: Output filename (without extension)
            **kwargs: STL-specific options (ascii=False)
            
        Returns:
            Path to exported STL file
        """
        ascii_mode = kwargs.get('ascii', self.stl_ascii)
        output_path = self.output_dir / f"{filename}.stl"
        
        vertices = mesh['vertices']
        faces = mesh['faces']
        
        try:
            if stl_mesh:
                # Use numpy-stl for STL export
                stl_data = self._create_stl_mesh(vertices, faces)
                stl_data.save(str(output_path), mode=stl_mesh.Mode.ASCII if ascii_mode else stl_mesh.Mode.BINARY)
            elif trimesh:
                # Fallback to trimesh
                mesh_obj = self._create_trimesh_object(vertices, faces)
                mesh_obj.export(str(output_path))
            else:
                # Manual STL export
                self._export_stl_manual(vertices, faces, output_path, ascii_mode)
            
            return output_path
            
        except Exception as e:
            raise ExportError(f"STL export failed: {str(e)}")
    
    def export_obj(self, mesh: Dict, filename: str, **kwargs) -> Path:
        """
        Export mesh to OBJ format with optional materials.
        
        Args:
            mesh: Mesh data dictionary
            filename: Output filename (without extension)
            **kwargs: OBJ-specific options (materials=True, material_name='default')
            
        Returns:
            Path to exported OBJ file
        """
        include_materials = kwargs.get('materials', self.obj_include_materials)
        material_name = kwargs.get('material_name', 'default_material')
        
        output_path = self.output_dir / f"{filename}.obj"
        
        vertices = mesh['vertices']
        faces = mesh['faces']
        normals = mesh.get('normals', [])
        
        try:
            if trimesh:
                # Use trimesh for OBJ export
                mesh_obj = self._create_trimesh_object(vertices, faces)
                mesh_obj.export(str(output_path))
                
                # Add materials if requested
                if include_materials:
                    self._create_mtl_file(filename, material_name)
            else:
                # Manual OBJ export
                self._export_obj_manual(vertices, faces, normals, output_path, 
                                      include_materials, material_name)
            
            return output_path
            
        except Exception as e:
            raise ExportError(f"OBJ export failed: {str(e)}")
    
    def export_ply(self, mesh: Dict, filename: str, **kwargs) -> Path:
        """
        Export mesh to PLY format.
        
        Args:
            mesh: Mesh data dictionary
            filename: Output filename (without extension)
            **kwargs: PLY-specific options (ascii=False, colors=None)
            
        Returns:
            Path to exported PLY file
        """
        ascii_mode = kwargs.get('ascii', self.ply_ascii)
        vertex_colors = kwargs.get('colors', None)
        
        output_path = self.output_dir / f"{filename}.ply"
        
        vertices = mesh['vertices']
        faces = mesh['faces']
        
        try:
            if trimesh:
                # Use trimesh for PLY export
                mesh_obj = self._create_trimesh_object(vertices, faces)
                if vertex_colors is not None:
                    mesh_obj.visual.vertex_colors = vertex_colors
                mesh_obj.export(str(output_path))
            else:
                # Manual PLY export
                self._export_ply_manual(vertices, faces, output_path, ascii_mode, vertex_colors)
            
            return output_path
            
        except Exception as e:
            raise ExportError(f"PLY export failed: {str(e)}")
    
    def export_gltf(self, mesh: Dict, filename: str, **kwargs) -> Path:
        """
        Export mesh to GLTF format.
        
        Args:
            mesh: Mesh data dictionary
            filename: Output filename (without extension)
            **kwargs: GLTF-specific options (embed_textures=True, binary=False)
            
        Returns:
            Path to exported GLTF file
        """
        embed_textures = kwargs.get('embed_textures', self.gltf_embed_textures)
        binary_format = kwargs.get('binary', False)
        
        extension = '.glb' if binary_format else '.gltf'
        output_path = self.output_dir / f"{filename}{extension}"
        
        vertices = mesh['vertices']
        faces = mesh['faces']
        normals = mesh.get('normals', [])
        
        try:
            if trimesh:
                # Use trimesh for GLTF export
                mesh_obj = self._create_trimesh_object(vertices, faces)
                mesh_obj.export(str(output_path))
            else:
                # Manual GLTF export
                self._export_gltf_manual(vertices, faces, normals, output_path, 
                                       embed_textures, binary_format)
            
            return output_path
            
        except Exception as e:
            raise ExportError(f"GLTF export failed: {str(e)}")
    
    def _validate_mesh_for_export(self, mesh: Dict) -> bool:
        """
        Validate mesh data for export.
        
        Args:
            mesh: Mesh data dictionary
            
        Returns:
            True if mesh is valid
            
        Raises:
            ValidationError: If mesh is invalid
        """
        if not isinstance(mesh, dict):
            raise ValidationError("Mesh must be a dictionary")
        
        if 'vertices' not in mesh:
            raise ValidationError("Mesh must contain 'vertices' key")
        
        if 'faces' not in mesh:
            raise ValidationError("Mesh must contain 'faces' key")
        
        vertices = mesh['vertices']
        faces = mesh['faces']
        
        if len(vertices) == 0:
            raise ValidationError("Mesh has no vertices")
        
        if len(faces) == 0:
            raise ValidationError("Mesh has no faces")
        
        # Check vertex format
        vertices = np.array(vertices)
        if vertices.shape[1] != 3:
            raise ValidationError("Vertices must be 3D coordinates")
        
        # Check for invalid values
        if np.any(~np.isfinite(vertices)):
            raise ValidationError("Mesh contains invalid vertex coordinates")
        
        # Check face indices
        max_vertex_index = len(vertices) - 1
        for i, face in enumerate(faces):
            if len(face) < 3:
                raise ValidationError(f"Face {i} has less than 3 vertices")
            
            for vertex_idx in face:
                if vertex_idx < 0 or vertex_idx > max_vertex_index:
                    raise ValidationError(f"Face {i} references invalid vertex index {vertex_idx}")
        
        return True
    
    def _apply_scaling(self, mesh: Dict, scale: float) -> Dict:
        """
        Apply scaling to mesh vertices.
        
        Args:
            mesh: Original mesh data
            scale: Scale factor
            
        Returns:
            Scaled mesh data
        """
        if not validate_numeric_input(scale) or scale <= 0:
            raise ExportError("Scale must be a positive number")
        
        if scale == 1.0:
            return mesh  # No scaling needed
        
        scaled_mesh = mesh.copy()
        scaled_mesh['vertices'] = np.array(mesh['vertices']) * scale
        
        return scaled_mesh
    
    def _create_trimesh_object(self, vertices: np.ndarray, faces: List) -> object:
        """Create trimesh object from vertices and faces."""
        if not trimesh:
            raise ExportError("Trimesh not available")
        
        # Convert faces to triangles only
        triangle_faces = []
        for face in faces:
            if len(face) == 3:
                triangle_faces.append(face)
            elif len(face) == 4:
                # Split quad into two triangles
                triangle_faces.append([face[0], face[1], face[2]])
                triangle_faces.append([face[0], face[2], face[3]])
        
        return trimesh.Trimesh(vertices=vertices, faces=triangle_faces)
    
    def _create_stl_mesh(self, vertices: np.ndarray, faces: List) -> object:
        """Create STL mesh object from vertices and faces."""
        if not stl_mesh:
            raise ExportError("numpy-stl not available")
        
        # Convert to triangles
        triangles = []
        for face in faces:
            if len(face) >= 3:
                # Take first three vertices for triangle
                triangle = [vertices[face[0]], vertices[face[1]], vertices[face[2]]]
                triangles.append(triangle)
        
        # Create STL mesh
        stl_data = stl_mesh.Mesh(np.zeros(len(triangles), dtype=stl_mesh.Mesh.dtype))
        for i, triangle in enumerate(triangles):
            stl_data.vectors[i] = triangle
        
        return stl_data
    
    def _export_stl_manual(self, vertices: np.ndarray, faces: List, 
                          output_path: Path, ascii_mode: bool = False):
        """Manual STL export implementation."""
        with open(output_path, 'w' if ascii_mode else 'wb') as f:
            if ascii_mode:
                f.write("solid exported_mesh\n")
                
                for face in faces:
                    if len(face) >= 3:
                        # Calculate normal
                        v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                        normal = np.cross(v2 - v1, v3 - v1)
                        normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else [0, 0, 1]
                        
                        f.write(f"  facet normal {normal[0]} {normal[1]} {normal[2]}\n")
                        f.write("    outer loop\n")
                        f.write(f"      vertex {v1[0]} {v1[1]} {v1[2]}\n")
                        f.write(f"      vertex {v2[0]} {v2[1]} {v2[2]}\n")
                        f.write(f"      vertex {v3[0]} {v3[1]} {v3[2]}\n")
                        f.write("    endloop\n")
                        f.write("  endfacet\n")
                
                f.write("endsolid exported_mesh\n")
            else:
                # Binary STL format
                header = b"Binary STL exported by 3D Text Generator" + b"\x00" * (80 - 42)
                f.write(header)
                
                # Count triangles
                triangle_count = sum(1 for face in faces if len(face) >= 3)
                f.write(triangle_count.to_bytes(4, byteorder='little'))
                
                for face in faces:
                    if len(face) >= 3:
                        v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                        normal = np.cross(v2 - v1, v3 - v1)
                        normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else [0, 0, 1]
                        
                        # Write normal (3 floats)
                        for component in normal:
                            f.write(np.float32(component).tobytes())
                        
                        # Write vertices (9 floats)
                        for vertex in [v1, v2, v3]:
                            for component in vertex:
                                f.write(np.float32(component).tobytes())
                        
                        # Write attribute byte count (2 bytes)
                        f.write(b"\x00\x00")
    
    def _export_obj_manual(self, vertices: np.ndarray, faces: List, normals: List,
                          output_path: Path, include_materials: bool, material_name: str):
        """Manual OBJ export implementation."""
        with open(output_path, 'w') as f:
            f.write("# OBJ file exported by 3D Text Generator\n")
            
            if include_materials:
                mtl_file = output_path.with_suffix('.mtl')
                f.write(f"mtllib {mtl_file.name}\n")
                f.write(f"usemtl {material_name}\n")
            
            # Write vertices
            for vertex in vertices:
                f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
            
            # Write vertex normals if available
            if normals:
                for normal in normals:
                    if isinstance(normal, (list, tuple)) and len(normal) >= 3:
                        f.write(f"vn {normal[0]} {normal[1]} {normal[2]}\n")
            
            # Write faces
            for face in faces:
                if len(face) >= 3:
                    face_str = "f"
                    for vertex_idx in face:
                        face_str += f" {vertex_idx + 1}"  # OBJ uses 1-based indexing
                    f.write(face_str + "\n")
        
        if include_materials:
            self._create_mtl_file(output_path.stem, material_name)
    
    def _create_mtl_file(self, filename: str, material_name: str):
        """Create MTL material file for OBJ export."""
        mtl_path = self.output_dir / f"{filename}.mtl"
        
        with open(mtl_path, 'w') as f:
            f.write("# MTL file exported by 3D Text Generator\n")
            f.write(f"newmtl {material_name}\n")
            f.write("Ka 0.2 0.2 0.2\n")  # Ambient color
            f.write("Kd 0.8 0.8 0.8\n")  # Diffuse color
            f.write("Ks 0.5 0.5 0.5\n")  # Specular color
            f.write("Ns 32.0\n")          # Specular exponent
            f.write("d 1.0\n")            # Transparency
    
    def _export_ply_manual(self, vertices: np.ndarray, faces: List, output_path: Path,
                          ascii_mode: bool = False, vertex_colors: Optional[np.ndarray] = None):
        """Manual PLY export implementation."""
        has_colors = vertex_colors is not None
        
        with open(output_path, 'w' if ascii_mode else 'wb') as f:
            if ascii_mode:
                # ASCII PLY header
                f.write("ply\n")
                f.write("format ascii 1.0\n")
                f.write(f"element vertex {len(vertices)}\n")
                f.write("property float x\n")
                f.write("property float y\n")
                f.write("property float z\n")
                
                if has_colors:
                    f.write("property uchar red\n")
                    f.write("property uchar green\n")
                    f.write("property uchar blue\n")
                
                f.write(f"element face {len(faces)}\n")
                f.write("property list uchar int vertex_indices\n")
                f.write("end_header\n")
                
                # Write vertices
                for i, vertex in enumerate(vertices):
                    line = f"{vertex[0]} {vertex[1]} {vertex[2]}"
                    if has_colors:
                        color = vertex_colors[i] if i < len(vertex_colors) else [128, 128, 128]
                        line += f" {int(color[0])} {int(color[1])} {int(color[2])}"
                    f.write(line + "\n")
                
                # Write faces
                for face in faces:
                    f.write(f"{len(face)}")
                    for vertex_idx in face:
                        f.write(f" {vertex_idx}")
                    f.write("\n")
            else:
                # Binary PLY format (simplified)
                header = "ply\nformat binary_little_endian 1.0\n"
                header += f"element vertex {len(vertices)}\n"
                header += "property float x\nproperty float y\nproperty float z\n"
                if has_colors:
                    header += "property uchar red\nproperty uchar green\nproperty uchar blue\n"
                header += f"element face {len(faces)}\n"
                header += "property list uchar int vertex_indices\n"
                header += "end_header\n"
                
                f.write(header.encode('ascii'))
                
                # Write binary vertex data
                for i, vertex in enumerate(vertices):
                    f.write(np.float32(vertex[0]).tobytes())
                    f.write(np.float32(vertex[1]).tobytes())
                    f.write(np.float32(vertex[2]).tobytes())
                    
                    if has_colors:
                        color = vertex_colors[i] if i < len(vertex_colors) else [128, 128, 128]
                        f.write(bytes([int(color[0]), int(color[1]), int(color[2])]))
                
                # Write binary face data
                for face in faces:
                    f.write(bytes([len(face)]))
                    for vertex_idx in face:
                        f.write(np.int32(vertex_idx).tobytes())
    
    def _export_gltf_manual(self, vertices: np.ndarray, faces: List, normals: List,
                           output_path: Path, embed_textures: bool, binary_format: bool):
        """Manual GLTF export implementation."""
        # Simplified GLTF export
        gltf_data = {
            "asset": {
                "version": "2.0",
                "generator": "3D Text Generator"
            },
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{
                "primitives": [{
                    "attributes": {"POSITION": 0},
                    "indices": 1
                }]
            }],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,  # FLOAT
                    "count": len(vertices),
                    "type": "VEC3",
                    "min": vertices.min(axis=0).tolist(),
                    "max": vertices.max(axis=0).tolist()
                },
                {
                    "bufferView": 1,
                    "componentType": 5125,  # UNSIGNED_INT
                    "count": len(faces) * 3,  # Assuming triangles
                    "type": "SCALAR"
                }
            ],
            "bufferViews": [
                {
                    "buffer": 0,
                    "byteOffset": 0,
                    "byteLength": len(vertices) * 12  # 3 floats * 4 bytes
                },
                {
                    "buffer": 0,
                    "byteOffset": len(vertices) * 12,
                    "byteLength": len(faces) * 12  # 3 ints * 4 bytes per triangle
                }
            ],
            "buffers": [{
                "byteLength": len(vertices) * 12 + len(faces) * 12
            }]
        }
        
        if binary_format:
            # GLB format (simplified)
            raise ExportError("Binary GLTF (GLB) export not implemented in manual mode")
        else:
            # JSON GLTF format
            with open(output_path, 'w') as f:
                json.dump(gltf_data, f, indent=2)
            
            # Create separate binary buffer file
            bin_path = output_path.with_suffix('.bin')
            with open(bin_path, 'wb') as f:
                # Write vertex data
                for vertex in vertices:
                    f.write(np.float32(vertex[0]).tobytes())
                    f.write(np.float32(vertex[1]).tobytes())
                    f.write(np.float32(vertex[2]).tobytes())
                
                # Write face indices (convert to triangles)
                for face in faces:
                    if len(face) >= 3:
                        f.write(np.uint32(face[0]).tobytes())
                        f.write(np.uint32(face[1]).tobytes())
                        f.write(np.uint32(face[2]).tobytes())
            
            gltf_data["buffers"][0]["uri"] = bin_path.name
            
            # Rewrite GLTF file with buffer URI
            with open(output_path, 'w') as f:
                json.dump(gltf_data, f, indent=2)
    
    def validate_export(self, file_path: Path, format_type: str) -> bool:
        """
        Validate exported file for correctness.
        
        Args:
            file_path: Path to exported file
            format_type: Export format type
            
        Returns:
            True if file is valid
            
        Raises:
            ValidationError: If file validation fails
        """
        if not file_path.exists():
            raise ValidationError(f"Exported file does not exist: {file_path}")
        
        if file_path.stat().st_size == 0:
            raise ValidationError(f"Exported file is empty: {file_path}")
        
        # Format-specific validation
        try:
            if format_type == 'STL':
                self._validate_stl_file(file_path)
            elif format_type == 'OBJ':
                self._validate_obj_file(file_path)
            elif format_type == 'PLY':
                self._validate_ply_file(file_path)
            elif format_type == 'GLTF':
                self._validate_gltf_file(file_path)
            
            return True
            
        except Exception as e:
            raise ValidationError(f"File validation failed: {str(e)}")
    
    def _validate_stl_file(self, file_path: Path):
        """Validate STL file format."""
        with open(file_path, 'rb') as f:
            header = f.read(80)
            if len(header) < 80:
                raise ValidationError("Invalid STL header")
            
            # Check if it's ASCII or binary
            f.seek(0)
            first_line = f.read(5)
            if first_line == b'solid':
                # ASCII STL
                f.seek(0)
                content = f.read().decode('utf-8', errors='ignore')
                if 'endsolid' not in content:
                    raise ValidationError("Invalid ASCII STL format")
            else:
                # Binary STL
                f.seek(80)
                triangle_count_bytes = f.read(4)
                if len(triangle_count_bytes) < 4:
                    raise ValidationError("Invalid binary STL format")
    
    def _validate_obj_file(self, file_path: Path):
        """Validate OBJ file format."""
        with open(file_path, 'r') as f:
            has_vertices = False
            has_faces = False
            
            for line in f:
                line = line.strip()
                if line.startswith('v '):
                    has_vertices = True
                elif line.startswith('f '):
                    has_faces = True
            
            if not has_vertices:
                raise ValidationError("OBJ file has no vertices")
            if not has_faces:
                raise ValidationError("OBJ file has no faces")
    
    def _validate_ply_file(self, file_path: Path):
        """Validate PLY file format."""
        with open(file_path, 'rb') as f:
            first_line = f.read(3)
            if first_line != b'ply':
                raise ValidationError("Invalid PLY file header")
    
    def _validate_gltf_file(self, file_path: Path):
        """Validate GLTF file format."""
        try:
            with open(file_path, 'r') as f:
                gltf_data = json.load(f)
            
            if 'asset' not in gltf_data:
                raise ValidationError("GLTF file missing asset information")
            
            if 'version' not in gltf_data['asset']:
                raise ValidationError("GLTF file missing version information")
                
        except json.JSONDecodeError:
            raise ValidationError("Invalid GLTF JSON format")
    
    def get_export_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get information about an exported file.
        
        Args:
            file_path: Path to exported file
            
        Returns:
            Dictionary with file information
        """
        if not file_path.exists():
            return {"error": "File does not exist"}
        
        stat = file_path.stat()
        
        info = {
            "file_path": str(file_path),
            "file_size": stat.st_size,
            "format": file_path.suffix.upper().lstrip('.'),
            "created": stat.st_ctime,
            "modified": stat.st_mtime
        }
        
        return info


# Utility functions

def get_supported_formats() -> List[str]:
    """Get list of supported export formats."""
    return list(Config.SUPPORTED_EXPORT_FORMATS)


def validate_export_format(format_name: str) -> bool:
    """Validate if export format is supported."""
    return format_name.upper() in Config.SUPPORTED_EXPORT_FORMATS


# Example usage and testing
if __name__ == "__main__":
    # Basic testing
    try:
        exporter = Exporter()
        
        # Test with a simple mesh
        test_mesh = {
            'vertices': np.array([
                [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # Bottom face
                [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # Top face
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
        
        print("Testing export functionality...")
        print(f"Supported formats: {get_supported_formats()}")
        
        # Test each format
        for format_type in ['STL', 'OBJ', 'PLY']:
            try:
                output_path = exporter.export_mesh(test_mesh, f"test_cube", format_type)
                info = exporter.get_export_info(output_path)
                print(f"{format_type} export successful: {info}")
            except Exception as e:
                print(f"{format_type} export failed: {e}")
        
        # Test GLTF (might fail without trimesh)
        try:
            output_path = exporter.export_mesh(test_mesh, "test_cube", "GLTF")
            info = exporter.get_export_info(output_path)
            print(f"GLTF export successful: {info}")
        except Exception as e:
            print(f"GLTF export failed: {e}")
            
    except Exception as e:
        print(f"Error during testing: {e}")