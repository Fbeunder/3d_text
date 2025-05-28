"""
Configuration module for 3D Text Generator

Contains default settings, constants, and configuration parameters
for the 3D text generation application.
"""

import os
from pathlib import Path


class Config:
    """Configuration class containing all application settings."""
    
    # Font settings
    DEFAULT_FONT_SIZE = 72  # Points
    DEFAULT_CHARACTER_SPACING = 2.0  # Units
    DEFAULT_CHARACTER_WIDTH = 10.0  # Fallback character width
    DEFAULT_LINE_SPACING = 1.2  # Multiplier for line height
    
    # 3D Generation settings
    DEFAULT_EXTRUSION_DEPTH = 5.0  # Units
    DEFAULT_BEVEL_DEPTH = 0.5  # Units
    DEFAULT_BEVEL_RESOLUTION = 4  # Number of bevel segments
    
    # Rendering settings
    DEFAULT_RESOLUTION = (800, 600)  # Width, Height
    DEFAULT_CAMERA_DISTANCE = 50.0  # Units from origin
    DEFAULT_LIGHTING_INTENSITY = 1.0  # Light intensity
    
    # Export settings
    DEFAULT_EXPORT_FORMAT = 'STL'  # Default export format
    DEFAULT_MESH_RESOLUTION = 0.1  # Mesh resolution for curved surfaces
    DEFAULT_EXPORT_SCALE = 1.0  # Scale factor for exports
    
    # File paths
    PROJECT_ROOT = Path(__file__).parent
    DEFAULT_FONT_DIR = PROJECT_ROOT / "fonts"
    DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"
    DEFAULT_TEMP_DIR = PROJECT_ROOT / "temp"
    
    # Supported formats
    SUPPORTED_FONT_FORMATS = {'.ttf', '.otf', '.woff', '.woff2'}
    SUPPORTED_EXPORT_FORMATS = {'STL', 'OBJ', 'PLY', 'GLTF'}
    
    # Validation limits
    MAX_TEXT_LENGTH = 1000  # Maximum characters in input text
    MIN_FONT_SIZE = 8  # Minimum font size in points
    MAX_FONT_SIZE = 500  # Maximum font size in points
    MIN_EXTRUSION_DEPTH = 0.1  # Minimum extrusion depth
    MAX_EXTRUSION_DEPTH = 100.0  # Maximum extrusion depth
    
    # Performance settings
    MAX_VERTICES_PER_MESH = 100000  # Maximum vertices before mesh splitting
    DEFAULT_SIMPLIFICATION_RATIO = 0.1  # Mesh simplification ratio
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = PROJECT_ROOT / "logs" / "3d_text.log"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        directories = [
            cls.DEFAULT_FONT_DIR,
            cls.DEFAULT_OUTPUT_DIR,
            cls.DEFAULT_TEMP_DIR,
            cls.LOG_FILE.parent
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_font_size(cls, size: float) -> bool:
        """Validate font size is within acceptable range."""
        return cls.MIN_FONT_SIZE <= size <= cls.MAX_FONT_SIZE
    
    @classmethod
    def validate_extrusion_depth(cls, depth: float) -> bool:
        """Validate extrusion depth is within acceptable range."""
        return cls.MIN_EXTRUSION_DEPTH <= depth <= cls.MAX_EXTRUSION_DEPTH
    
    @classmethod
    def validate_export_format(cls, format_name: str) -> bool:
        """Validate export format is supported."""
        return format_name.upper() in cls.SUPPORTED_EXPORT_FORMATS
    
    @classmethod
    def get_default_font_path(cls) -> Path:
        """Get path to default system font if available."""
        # Try to find a default system font
        system_font_paths = [
            # Windows
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/calibri.ttf"),
            # macOS
            Path("/System/Library/Fonts/Arial.ttf"),
            Path("/System/Library/Fonts/Helvetica.ttc"),
            # Linux
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        ]
        
        for font_path in system_font_paths:
            if font_path.exists():
                return font_path
        
        return None


# Global configuration instance
config = Config()

# Ensure directories exist on import
config.ensure_directories()


# Environment-specific overrides
def load_environment_config():
    """Load configuration overrides from environment variables."""
    
    # Font settings
    if 'TEXT3D_FONT_SIZE' in os.environ:
        try:
            Config.DEFAULT_FONT_SIZE = float(os.environ['TEXT3D_FONT_SIZE'])
        except ValueError:
            pass
    
    if 'TEXT3D_CHAR_SPACING' in os.environ:
        try:
            Config.DEFAULT_CHARACTER_SPACING = float(os.environ['TEXT3D_CHAR_SPACING'])
        except ValueError:
            pass
    
    # 3D settings
    if 'TEXT3D_EXTRUSION_DEPTH' in os.environ:
        try:
            Config.DEFAULT_EXTRUSION_DEPTH = float(os.environ['TEXT3D_EXTRUSION_DEPTH'])
        except ValueError:
            pass
    
    # Output directory
    if 'TEXT3D_OUTPUT_DIR' in os.environ:
        Config.DEFAULT_OUTPUT_DIR = Path(os.environ['TEXT3D_OUTPUT_DIR'])
    
    # Log level
    if 'TEXT3D_LOG_LEVEL' in os.environ:
        Config.LOG_LEVEL = os.environ['TEXT3D_LOG_LEVEL'].upper()


# Load environment overrides
load_environment_config()


# Convenience functions for common configurations
def get_text_config():
    """Get text processing configuration."""
    return {
        'font_size': Config.DEFAULT_FONT_SIZE,
        'character_spacing': Config.DEFAULT_CHARACTER_SPACING,
        'line_spacing': Config.DEFAULT_LINE_SPACING,
        'max_length': Config.MAX_TEXT_LENGTH
    }


def get_3d_config():
    """Get 3D generation configuration."""
    return {
        'extrusion_depth': Config.DEFAULT_EXTRUSION_DEPTH,
        'bevel_depth': Config.DEFAULT_BEVEL_DEPTH,
        'bevel_resolution': Config.DEFAULT_BEVEL_RESOLUTION,
        'mesh_resolution': Config.DEFAULT_MESH_RESOLUTION
    }


def get_export_config():
    """Get export configuration."""
    return {
        'format': Config.DEFAULT_EXPORT_FORMAT,
        'scale': Config.DEFAULT_EXPORT_SCALE,
        'output_dir': Config.DEFAULT_OUTPUT_DIR,
        'supported_formats': Config.SUPPORTED_EXPORT_FORMATS
    }


if __name__ == "__main__":
    # Print current configuration for debugging
    print("3D Text Generator Configuration:")
    print(f"  Font size: {Config.DEFAULT_FONT_SIZE}")
    print(f"  Character spacing: {Config.DEFAULT_CHARACTER_SPACING}")
    print(f"  Extrusion depth: {Config.DEFAULT_EXTRUSION_DEPTH}")
    print(f"  Output directory: {Config.DEFAULT_OUTPUT_DIR}")
    print(f"  Supported formats: {Config.SUPPORTED_EXPORT_FORMATS}")
    
    default_font = Config.get_default_font_path()
    if default_font:
        print(f"  Default font: {default_font}")
    else:
        print("  No default font found")