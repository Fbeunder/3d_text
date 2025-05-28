"""
3D Renderer Module for 3D Text Generator

This module provides functionality for 3D rendering and visualization
of generated meshes with configurable camera, lighting, and materials.
"""

import logging
from typing import List, Tuple, Dict, Optional, Union, Any
import numpy as np
from pathlib import Path
import warnings

# Suppress matplotlib warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import matplotlib.colors as mcolors
except ImportError:
    plt = None
    Axes3D = None
    Poly3DCollection = None
    mcolors = None
    logging.error("matplotlib not available. 3D rendering functionality will be disabled.")

try:
    import mayavi.mlab as mlab
    MAYAVI_AVAILABLE = True
except ImportError:
    mlab = None
    MAYAVI_AVAILABLE = False
    logging.info("mayavi not available. Advanced 3D rendering features will be limited.")

from config import Config
from utils import validate_numeric_input


class RenderingError(Exception):
    """Exception raised when rendering operations fail."""
    pass


class CameraError(Exception):
    """Exception raised when camera operations fail."""
    pass


class LightingError(Exception):
    """Exception raised when lighting operations fail."""
    pass


class Camera:
    """
    Camera class for managing 3D view parameters.
    """
    
    def __init__(self, position: Tuple[float, float, float] = (50, 50, 50),
                 target: Tuple[float, float, float] = (0, 0, 0),
                 up_vector: Tuple[float, float, float] = (0, 0, 1)):
        """
        Initialize camera with position, target, and up vector.
        
        Args:
            position: Camera position in 3D space
            target: Point the camera is looking at
            up_vector: Camera up direction vector
        """
        self.position = np.array(position, dtype=float)
        self.target = np.array(target, dtype=float)
        self.up_vector = np.array(up_vector, dtype=float)
        
        # Validate inputs
        self._validate_vectors()
        
        # Camera parameters
        self.fov = 45.0  # Field of view in degrees
        self.near_clip = 0.1
        self.far_clip = 1000.0
        
    def _validate_vectors(self):
        """Validate camera vectors."""
        for name, vector in [("position", self.position), ("target", self.target), ("up_vector", self.up_vector)]:
            if not np.all(np.isfinite(vector)):
                raise CameraError(f"Camera {name} contains invalid values")
            if len(vector) != 3:
                raise CameraError(f"Camera {name} must be a 3D vector")
    
    def set_position(self, position: Tuple[float, float, float]):
        """Set camera position."""
        self.position = np.array(position, dtype=float)
        self._validate_vectors()
    
    def set_target(self, target: Tuple[float, float, float]):
        """Set camera target."""
        self.target = np.array(target, dtype=float)
        self._validate_vectors()
    
    def set_up_vector(self, up_vector: Tuple[float, float, float]):
        """Set camera up vector."""
        self.up_vector = np.array(up_vector, dtype=float)
        self._validate_vectors()
    
    def get_view_matrix(self) -> np.ndarray:
        """
        Calculate view matrix for the camera.
        
        Returns:
            4x4 view matrix
        """
        try:
            # Calculate camera coordinate system
            forward = self.target - self.position
            forward = forward / np.linalg.norm(forward)
            
            right = np.cross(forward, self.up_vector)
            right = right / np.linalg.norm(right)
            
            up = np.cross(right, forward)
            
            # Create view matrix
            view_matrix = np.eye(4)
            view_matrix[0, :3] = right
            view_matrix[1, :3] = up
            view_matrix[2, :3] = -forward
            view_matrix[:3, 3] = -np.dot(np.array([right, up, -forward]), self.position)
            
            return view_matrix
            
        except Exception as e:
            raise CameraError(f"Failed to calculate view matrix: {str(e)}")
    
    def orbit(self, azimuth_delta: float, elevation_delta: float):
        """
        Orbit camera around target.
        
        Args:
            azimuth_delta: Change in azimuth angle (degrees)
            elevation_delta: Change in elevation angle (degrees)
        """
        try:
            # Convert to radians
            azimuth_rad = np.radians(azimuth_delta)
            elevation_rad = np.radians(elevation_delta)
            
            # Calculate current spherical coordinates
            direction = self.position - self.target
            distance = np.linalg.norm(direction)
            
            if distance == 0:
                return
            
            direction = direction / distance
            
            # Current spherical coordinates
            current_elevation = np.arcsin(direction[2])
            current_azimuth = np.arctan2(direction[1], direction[0])
            
            # Apply deltas
            new_azimuth = current_azimuth + azimuth_rad
            new_elevation = np.clip(current_elevation + elevation_rad, -np.pi/2 + 0.01, np.pi/2 - 0.01)
            
            # Convert back to Cartesian
            new_direction = np.array([
                np.cos(new_elevation) * np.cos(new_azimuth),
                np.cos(new_elevation) * np.sin(new_azimuth),
                np.sin(new_elevation)
            ])
            
            self.position = self.target + new_direction * distance
            
        except Exception as e:
            raise CameraError(f"Failed to orbit camera: {str(e)}")
    
    def zoom(self, factor: float):
        """
        Zoom camera by moving closer/farther from target.
        
        Args:
            factor: Zoom factor (>1 zoom in, <1 zoom out)
        """
        if factor <= 0:
            raise CameraError("Zoom factor must be positive")
        
        try:
            direction = self.position - self.target
            distance = np.linalg.norm(direction)
            
            if distance == 0:
                return
            
            new_distance = distance / factor
            direction_normalized = direction / distance
            self.position = self.target + direction_normalized * new_distance
            
        except Exception as e:
            raise CameraError(f"Failed to zoom camera: {str(e)}")


class Light:
    """
    Light class for managing lighting in 3D scenes.
    """
    
    LIGHT_TYPES = ['ambient', 'directional', 'point']
    
    def __init__(self, light_type: str = 'directional',
                 position: Tuple[float, float, float] = (10, 10, 10),
                 intensity: float = 1.0,
                 color: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
        """
        Initialize light with type, position, intensity, and color.
        
        Args:
            light_type: Type of light ('ambient', 'directional', 'point')
            position: Light position (for directional: direction vector)
            intensity: Light intensity (0.0 to 1.0+)
            color: Light color as RGB tuple (0.0 to 1.0)
        """
        if light_type not in self.LIGHT_TYPES:
            raise LightingError(f"Invalid light type: {light_type}. Must be one of {self.LIGHT_TYPES}")
        
        self.light_type = light_type
        self.position = np.array(position, dtype=float)
        self.intensity = float(intensity)
        self.color = np.array(color, dtype=float)
        
        self._validate_parameters()
    
    def _validate_parameters(self):
        """Validate light parameters."""
        if not np.all(np.isfinite(self.position)):
            raise LightingError("Light position contains invalid values")
        
        if not validate_numeric_input(self.intensity) or self.intensity < 0:
            raise LightingError("Light intensity must be non-negative")
        
        if len(self.color) != 3 or not np.all((self.color >= 0) & (self.color <= 1)):
            raise LightingError("Light color must be RGB tuple with values 0.0-1.0")
    
    def set_intensity(self, intensity: float):
        """Set light intensity."""
        if not validate_numeric_input(intensity) or intensity < 0:
            raise LightingError("Light intensity must be non-negative")
        self.intensity = float(intensity)
    
    def set_color(self, color: Tuple[float, float, float]):
        """Set light color."""
        self.color = np.array(color, dtype=float)
        if len(self.color) != 3 or not np.all((self.color >= 0) & (self.color <= 1)):
            raise LightingError("Light color must be RGB tuple with values 0.0-1.0")
    
    def set_position(self, position: Tuple[float, float, float]):
        """Set light position."""
        self.position = np.array(position, dtype=float)
        if not np.all(np.isfinite(self.position)):
            raise LightingError("Light position contains invalid values")


class Renderer:
    """
    Main renderer class for 3D visualization of meshes.
    """
    
    BACKENDS = ['matplotlib', 'mayavi']
    RENDER_MODES = ['wireframe', 'solid', 'shaded']
    
    def __init__(self, backend: str = 'matplotlib'):
        """
        Initialize renderer with specified backend.
        
        Args:
            backend: Rendering backend ('matplotlib' or 'mayavi')
        """
        if backend not in self.BACKENDS:
            raise RenderingError(f"Invalid backend: {backend}. Must be one of {self.BACKENDS}")
        
        if backend == 'matplotlib' and plt is None:
            raise RenderingError("matplotlib backend not available")
        
        if backend == 'mayavi' and not MAYAVI_AVAILABLE:
            raise RenderingError("mayavi backend not available")
        
        self.backend = backend
        self.figure = None
        self.axes = None
        
        # Scene properties
        self.camera = Camera()
        self.lights = []
        self.background_color = (0.95, 0.95, 0.95)  # Light gray
        self.resolution = Config.DEFAULT_RESOLUTION
        
        # Rendering properties
        self.render_mode = 'shaded'
        self.show_wireframe = False
        self.wireframe_color = (0.2, 0.2, 0.2)
        self.wireframe_width = 0.5
        
        # Add default lighting
        self._setup_default_lighting()
    
    def _setup_default_lighting(self):
        """Setup default lighting configuration."""
        try:
            # Ambient light
            ambient = Light('ambient', (0, 0, 0), 0.3, (1.0, 1.0, 1.0))
            self.lights.append(ambient)
            
            # Main directional light
            main_light = Light('directional', (1, 1, 1), Config.DEFAULT_LIGHTING_INTENSITY, (1.0, 1.0, 1.0))
            self.lights.append(main_light)
            
            # Fill light
            fill_light = Light('directional', (-0.5, -0.5, 0.5), 0.4, (0.8, 0.9, 1.0))
            self.lights.append(fill_light)
            
        except Exception as e:
            logging.warning(f"Failed to setup default lighting: {e}")
    
    def setup_scene(self, resolution: Tuple[int, int] = None):
        """
        Setup 3D scene with specified resolution.
        
        Args:
            resolution: Scene resolution as (width, height)
        """
        if resolution is None:
            resolution = self.resolution
        else:
            self.resolution = resolution
        
        try:
            if self.backend == 'matplotlib':
                self._setup_matplotlib_scene()
            elif self.backend == 'mayavi':
                self._setup_mayavi_scene()
                
        except Exception as e:
            raise RenderingError(f"Failed to setup scene: {str(e)}")
    
    def _setup_matplotlib_scene(self):
        """Setup matplotlib 3D scene."""
        if plt is None:
            raise RenderingError("matplotlib not available")
        
        # Create figure and 3D axes
        self.figure = plt.figure(figsize=(self.resolution[0]/100, self.resolution[1]/100), dpi=100)
        self.axes = self.figure.add_subplot(111, projection='3d')
        
        # Set background color
        self.figure.patch.set_facecolor(self.background_color)
        self.axes.xaxis.pane.fill = False
        self.axes.yaxis.pane.fill = False
        self.axes.zaxis.pane.fill = False
        
        # Configure axes
        self.axes.set_xlabel('X')
        self.axes.set_ylabel('Y')
        self.axes.set_zlabel('Z')
        
        # Set camera position
        self._update_matplotlib_camera()
    
    def _setup_mayavi_scene(self):
        """Setup mayavi 3D scene."""
        if not MAYAVI_AVAILABLE:
            raise RenderingError("mayavi not available")
        
        # Create mayavi figure
        self.figure = mlab.figure(size=self.resolution, bgcolor=self.background_color)
        mlab.clf()
    
    def _update_matplotlib_camera(self):
        """Update matplotlib camera view."""
        if self.axes is None:
            return
        
        # Calculate view angles
        direction = self.camera.position - self.camera.target
        distance = np.linalg.norm(direction)
        
        if distance > 0:
            direction = direction / distance
            
            # Calculate elevation and azimuth
            elevation = np.degrees(np.arcsin(direction[2]))
            azimuth = np.degrees(np.arctan2(direction[1], direction[0]))
            
            # Set view
            self.axes.view_init(elev=elevation, azim=azimuth)
            
            # Set camera distance
            self.axes.dist = Config.DEFAULT_CAMERA_DISTANCE / distance if distance > 0 else Config.DEFAULT_CAMERA_DISTANCE
    
    def set_camera(self, position: Tuple[float, float, float],
                   target: Tuple[float, float, float] = (0, 0, 0),
                   up_vector: Tuple[float, float, float] = (0, 0, 1)):
        """
        Set camera position and orientation.
        
        Args:
            position: Camera position
            target: Camera target point
            up_vector: Camera up vector
        """
        try:
            self.camera.set_position(position)
            self.camera.set_target(target)
            self.camera.set_up_vector(up_vector)
            
            if self.backend == 'matplotlib' and self.axes is not None:
                self._update_matplotlib_camera()
                
        except Exception as e:
            raise CameraError(f"Failed to set camera: {str(e)}")
    
    def add_lighting(self, light_type: str, position: Tuple[float, float, float],
                    intensity: float, color: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
        """
        Add lighting to the scene.
        
        Args:
            light_type: Type of light ('ambient', 'directional', 'point')
            position: Light position or direction
            intensity: Light intensity
            color: Light color as RGB tuple
        """
        try:
            light = Light(light_type, position, intensity, color)
            self.lights.append(light)
            
        except Exception as e:
            raise LightingError(f"Failed to add lighting: {str(e)}")
    
    def render_mesh(self, mesh_data: Dict, material_properties: Dict = None):
        """
        Render a 3D mesh.
        
        Args:
            mesh_data: Dictionary containing vertices, faces, and normals
            material_properties: Optional material properties
        """
        if not self._validate_mesh_data(mesh_data):
            raise RenderingError("Invalid mesh data provided")
        
        try:
            if self.backend == 'matplotlib':
                self._render_mesh_matplotlib(mesh_data, material_properties)
            elif self.backend == 'mayavi':
                self._render_mesh_mayavi(mesh_data, material_properties)
                
        except Exception as e:
            raise RenderingError(f"Failed to render mesh: {str(e)}")
    
    def _validate_mesh_data(self, mesh_data: Dict) -> bool:
        """Validate mesh data structure."""
        required_keys = ['vertices', 'faces']
        
        for key in required_keys:
            if key not in mesh_data:
                logging.error(f"Missing required key in mesh data: {key}")
                return False
        
        vertices = mesh_data['vertices']
        faces = mesh_data['faces']
        
        if len(vertices) == 0 or len(faces) == 0:
            logging.error("Empty vertices or faces in mesh data")
            return False
        
        # Check for performance limits
        if len(vertices) > Config.MAX_VERTICES_PER_MESH:
            logging.warning(f"Mesh has {len(vertices)} vertices, which exceeds recommended limit of {Config.MAX_VERTICES_PER_MESH}")
        
        return True
    
    def _render_mesh_matplotlib(self, mesh_data: Dict, material_properties: Dict = None):
        """Render mesh using matplotlib."""
        if self.axes is None:
            self.setup_scene()
        
        vertices = mesh_data['vertices']
        faces = mesh_data['faces']
        normals = mesh_data.get('normals', None)
        
        # Default material properties
        if material_properties is None:
            material_properties = {
                'color': (0.7, 0.7, 0.9),
                'alpha': 1.0,
                'shininess': 0.5
            }
        
        # Create face collections
        face_vertices = []
        face_colors = []
        
        for i, face in enumerate(faces):
            if len(face) < 3:
                continue
            
            # Get vertices for this face
            face_verts = [vertices[idx] for idx in face]
            face_vertices.append(face_verts)
            
            # Calculate lighting if normals available
            if normals is not None and i < len(normals):
                color = self._calculate_face_color(normals[i], material_properties)
            else:
                color = material_properties['color']
            
            face_colors.append(color)
        
        if not face_vertices:
            logging.warning("No valid faces to render")
            return
        
        # Render based on mode
        if self.render_mode == 'wireframe':
            self._render_wireframe_matplotlib(face_vertices)
        elif self.render_mode == 'solid':
            self._render_solid_matplotlib(face_vertices, face_colors, material_properties)
        elif self.render_mode == 'shaded':
            self._render_shaded_matplotlib(face_vertices, face_colors, material_properties)
        
        # Add wireframe overlay if requested
        if self.show_wireframe and self.render_mode != 'wireframe':
            self._render_wireframe_matplotlib(face_vertices, overlay=True)
        
        # Set equal aspect ratio and fit view
        self._fit_view_matplotlib(vertices)
    
    def _render_wireframe_matplotlib(self, face_vertices: List, overlay: bool = False):
        """Render wireframe using matplotlib."""
        color = self.wireframe_color if overlay else (0.2, 0.2, 0.2)
        linewidth = self.wireframe_width if overlay else 1.0
        
        for face_verts in face_vertices:
            if len(face_verts) < 3:
                continue
            
            # Draw edges
            for i in range(len(face_verts)):
                start = face_verts[i]
                end = face_verts[(i + 1) % len(face_verts)]
                
                self.axes.plot3D([start[0], end[0]], [start[1], end[1]], [start[2], end[2]],
                               color=color, linewidth=linewidth, alpha=0.8)
    
    def _render_solid_matplotlib(self, face_vertices: List, face_colors: List, material_properties: Dict):
        """Render solid faces using matplotlib."""
        poly_collection = Poly3DCollection(face_vertices, alpha=material_properties.get('alpha', 1.0))
        poly_collection.set_facecolors(face_colors)
        poly_collection.set_edgecolors('none')
        self.axes.add_collection3d(poly_collection)
    
    def _render_shaded_matplotlib(self, face_vertices: List, face_colors: List, material_properties: Dict):
        """Render shaded faces using matplotlib."""
        poly_collection = Poly3DCollection(face_vertices, alpha=material_properties.get('alpha', 1.0))
        poly_collection.set_facecolors(face_colors)
        poly_collection.set_edgecolors((0.1, 0.1, 0.1))
        poly_collection.set_linewidths(0.1)
        self.axes.add_collection3d(poly_collection)
    
    def _render_mesh_mayavi(self, mesh_data: Dict, material_properties: Dict = None):
        """Render mesh using mayavi."""
        if not MAYAVI_AVAILABLE:
            raise RenderingError("mayavi not available")
        
        vertices = mesh_data['vertices']
        faces = mesh_data['faces']
        
        # Convert faces to triangles for mayavi
        triangular_faces = []
        for face in faces:
            if len(face) == 3:
                triangular_faces.append(face)
            elif len(face) == 4:
                # Split quad into two triangles
                triangular_faces.append([face[0], face[1], face[2]])
                triangular_faces.append([face[0], face[2], face[3]])
        
        if not triangular_faces:
            logging.warning("No triangular faces available for mayavi rendering")
            return
        
        # Create mesh
        x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
        triangular_faces = np.array(triangular_faces)
        
        # Default material properties
        if material_properties is None:
            material_properties = {'color': (0.7, 0.7, 0.9)}
        
        # Render mesh
        mesh = mlab.triangular_mesh(x, y, z, triangular_faces, 
                                   color=material_properties.get('color', (0.7, 0.7, 0.9)))
        
        return mesh
    
    def _calculate_face_color(self, normal: Tuple[float, float, float], 
                            material_properties: Dict) -> Tuple[float, float, float]:
        """Calculate face color based on lighting and normal."""
        base_color = np.array(material_properties.get('color', (0.7, 0.7, 0.9)))
        normal = np.array(normal)
        
        # Normalize normal
        normal_length = np.linalg.norm(normal)
        if normal_length > 0:
            normal = normal / normal_length
        else:
            return tuple(base_color)
        
        # Calculate lighting contribution
        total_light = np.zeros(3)
        
        for light in self.lights:
            if light.light_type == 'ambient':
                total_light += light.color * light.intensity
            elif light.light_type == 'directional':
                light_dir = light.position / np.linalg.norm(light.position)
                dot_product = max(0, np.dot(normal, light_dir))
                total_light += light.color * light.intensity * dot_product
            elif light.light_type == 'point':
                # Simplified point light calculation
                light_dir = light.position / np.linalg.norm(light.position)
                dot_product = max(0, np.dot(normal, light_dir))
                total_light += light.color * light.intensity * dot_product * 0.5
        
        # Apply lighting to base color
        final_color = base_color * total_light
        final_color = np.clip(final_color, 0, 1)
        
        return tuple(final_color)
    
    def _fit_view_matplotlib(self, vertices: np.ndarray):
        """Fit view to show all vertices."""
        if len(vertices) == 0:
            return
        
        # Calculate bounds
        min_coords = np.min(vertices, axis=0)
        max_coords = np.max(vertices, axis=0)
        
        # Add some padding
        padding = 0.1 * (max_coords - min_coords)
        min_coords -= padding
        max_coords += padding
        
        # Set axis limits
        self.axes.set_xlim(min_coords[0], max_coords[0])
        self.axes.set_ylim(min_coords[1], max_coords[1])
        self.axes.set_zlim(min_coords[2], max_coords[2])
        
        # Set equal aspect ratio
        max_range = np.max(max_coords - min_coords)
        center = (max_coords + min_coords) / 2
        
        self.axes.set_xlim(center[0] - max_range/2, center[0] + max_range/2)
        self.axes.set_ylim(center[1] - max_range/2, center[1] + max_range/2)
        self.axes.set_zlim(center[2] - max_range/2, center[2] + max_range/2)
    
    def show_preview(self, interactive: bool = True):
        """
        Show interactive preview of the rendered scene.
        
        Args:
            interactive: Enable interactive controls
        """
        try:
            if self.backend == 'matplotlib':
                if self.figure is None:
                    raise RenderingError("No scene to display. Call setup_scene() first.")
                
                if interactive:
                    plt.ion()  # Turn on interactive mode
                
                plt.show()
                
            elif self.backend == 'mayavi':
                if not MAYAVI_AVAILABLE:
                    raise RenderingError("mayavi not available")
                
                mlab.show()
                
        except Exception as e:
            raise RenderingError(f"Failed to show preview: {str(e)}")
    
    def save_image(self, filename: Union[str, Path], format: str = 'PNG', dpi: int = 300):
        """
        Save rendered image to file.
        
        Args:
            filename: Output filename
            format: Image format ('PNG', 'JPG', 'SVG', etc.)
            dpi: Image resolution in DPI
        """
        filename = Path(filename)
        
        # Ensure output directory exists
        filename.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if self.backend == 'matplotlib':
                if self.figure is None:
                    raise RenderingError("No scene to save. Call setup_scene() first.")
                
                self.figure.savefig(filename, format=format.lower(), dpi=dpi, 
                                  bbox_inches='tight', facecolor=self.background_color)
                
            elif self.backend == 'mayavi':
                if not MAYAVI_AVAILABLE:
                    raise RenderingError("mayavi not available")
                
                mlab.savefig(str(filename))
            
            logging.info(f"Image saved to {filename}")
            
        except Exception as e:
            raise RenderingError(f"Failed to save image: {str(e)}")
    
    def clear_scene(self):
        """Clear the current scene."""
        try:
            if self.backend == 'matplotlib':
                if self.axes is not None:
                    self.axes.clear()
                    self.axes.set_xlabel('X')
                    self.axes.set_ylabel('Y')
                    self.axes.set_zlabel('Z')
                    self._update_matplotlib_camera()
                    
            elif self.backend == 'mayavi':
                if MAYAVI_AVAILABLE:
                    mlab.clf()
                    
        except Exception as e:
            logging.warning(f"Failed to clear scene: {e}")
    
    def set_render_mode(self, mode: str):
        """
        Set rendering mode.
        
        Args:
            mode: Render mode ('wireframe', 'solid', 'shaded')
        """
        if mode not in self.RENDER_MODES:
            raise RenderingError(f"Invalid render mode: {mode}. Must be one of {self.RENDER_MODES}")
        
        self.render_mode = mode
    
    def set_background_color(self, color: Tuple[float, float, float]):
        """Set background color."""
        if len(color) != 3 or not all(0 <= c <= 1 for c in color):
            raise RenderingError("Background color must be RGB tuple with values 0.0-1.0")
        
        self.background_color = color
        
        if self.figure is not None:
            if self.backend == 'matplotlib':
                self.figure.patch.set_facecolor(color)
    
    def enable_wireframe_overlay(self, enable: bool = True, color: Tuple[float, float, float] = None, width: float = None):
        """
        Enable/disable wireframe overlay.
        
        Args:
            enable: Enable wireframe overlay
            color: Wireframe color
            width: Wireframe line width
        """
        self.show_wireframe = enable
        
        if color is not None:
            if len(color) != 3 or not all(0 <= c <= 1 for c in color):
                raise RenderingError("Wireframe color must be RGB tuple with values 0.0-1.0")
            self.wireframe_color = color
        
        if width is not None:
            if not validate_numeric_input(width) or width <= 0:
                raise RenderingError("Wireframe width must be positive")
            self.wireframe_width = width


# Utility functions

def create_default_renderer(backend: str = 'matplotlib') -> Renderer:
    """
    Create a renderer with default settings.
    
    Args:
        backend: Rendering backend to use
        
    Returns:
        Configured Renderer instance
    """
    try:
        renderer = Renderer(backend)
        renderer.setup_scene()
        return renderer
        
    except Exception as e:
        logging.error(f"Failed to create default renderer: {e}")
        raise


def render_mesh_quick(mesh_data: Dict, output_file: Optional[Union[str, Path]] = None,
                     backend: str = 'matplotlib', show_preview: bool = True) -> Optional[Renderer]:
    """
    Quick render function for simple mesh visualization.
    
    Args:
        mesh_data: Mesh data dictionary
        output_file: Optional output file path
        backend: Rendering backend
        show_preview: Show interactive preview
        
    Returns:
        Renderer instance or None if rendering failed
    """
    try:
        renderer = create_default_renderer(backend)
        renderer.render_mesh(mesh_data)
        
        if output_file:
            renderer.save_image(output_file)
        
        if show_preview:
            renderer.show_preview()
        
        return renderer
        
    except Exception as e:
        logging.error(f"Quick render failed: {e}")
        return None


# Example usage and testing
if __name__ == "__main__":
    # Basic testing
    try:
        print("Testing 3D Renderer...")
        
        # Create test mesh data (simple cube)
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # Bottom face
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # Top face
        ])
        
        faces = [
            [0, 1, 2], [0, 2, 3],  # Bottom
            [4, 7, 6], [4, 6, 5],  # Top
            [0, 4, 5], [0, 5, 1],  # Front
            [2, 6, 7], [2, 7, 3],  # Back
            [0, 3, 7], [0, 7, 4],  # Left
            [1, 5, 6], [1, 6, 2]   # Right
        ]
        
        test_mesh = {
            'vertices': vertices,
            'faces': faces,
            'normals': [(0, 0, -1)] * 2 + [(0, 0, 1)] * 2 + 
                      [(0, -1, 0)] * 2 + [(0, 1, 0)] * 2 + 
                      [(-1, 0, 0)] * 2 + [(1, 0, 0)] * 2
        }
        
        print("Creating renderer...")
        renderer = create_default_renderer('matplotlib')
        
        print("Rendering test mesh...")
        renderer.render_mesh(test_mesh)
        
        print("Testing camera controls...")
        renderer.camera.orbit(45, 30)
        renderer.camera.zoom(1.5)
        
        print("Testing render modes...")
        for mode in ['wireframe', 'solid', 'shaded']:
            print(f"  Testing {mode} mode...")
            renderer.set_render_mode(mode)
            renderer.clear_scene()
            renderer.render_mesh(test_mesh)
        
        print("Testing lighting...")
        renderer.add_lighting('point', (5, 5, 5), 0.8, (1.0, 0.8, 0.6))
        
        print("Renderer testing completed successfully!")
        
        # Uncomment to show preview
        # renderer.show_preview()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()