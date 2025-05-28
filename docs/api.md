# API Documentation

Complete API reference for the 3D Text Generator application.

## Table of Contents

- [Main Application](#main-application)
- [Text Processing](#text-processing)
- [Geometry Generation](#geometry-generation)
- [Rendering](#rendering)
- [Export](#export)
- [Configuration](#configuration)
- [Utilities](#utilities)

---

## Main Application

### Text3DGenerator

Main application class that orchestrates the 3D text generation workflow.

```python
from main import Text3DGenerator

generator = Text3DGenerator(config_overrides=None)
```

#### Constructor

**`Text3DGenerator(config_overrides=None)`**

- **Parameters:**
  - `config_overrides` (dict, optional): Configuration overrides
- **Returns:** Text3DGenerator instance

#### Methods

**`load_font(font_path, font_size=None)`**

Load a font file for text processing.

- **Parameters:**
  - `font_path` (str): Path to the font file
  - `font_size` (int, optional): Font size override
- **Returns:** bool - True if font loaded successfully
- **Raises:** FontLoadError

**`process_text(text, spacing=None)`**

Process input text and calculate layout.

- **Parameters:**
  - `text` (str): Input text to process
  - `spacing` (float, optional): Character spacing override
- **Returns:** dict - Text processing results
- **Raises:** TextProcessingError

**`generate_geometry(text_data, depth=None, bevel_depth=None)`**

Generate 3D geometry from text data.

- **Parameters:**
  - `text_data` (dict): Text processing results
  - `depth` (float, optional): Extrusion depth override
  - `bevel_depth` (float, optional): Bevel depth override
- **Returns:** dict - Geometry generation results
- **Raises:** GeometryError

**`render_preview(geometry_data, output_path=None, show_preview=False)`**

Render a preview of the 3D geometry.

- **Parameters:**
  - `geometry_data` (dict): Geometry generation results
  - `output_path` (str, optional): Output path for preview image
  - `show_preview` (bool): Whether to show interactive preview
- **Returns:** str or None - Path to saved preview image
- **Raises:** RenderingError

**`export_model(geometry_data, output_path, export_format='STL', **export_options)`**

Export the 3D model to a file.

- **Parameters:**
  - `geometry_data` (dict): Geometry generation results
  - `output_path` (str): Output file path
  - `export_format` (str): Export format (STL, OBJ, PLY, GLTF)
  - `**export_options`: Additional export options
- **Returns:** str - Path to exported file
- **Raises:** ExportError

**`run_workflow(text, font_path=None, output_path=None, **options)`**

Run the complete 3D text generation workflow.

- **Parameters:**
  - `text` (str): Input text to convert
  - `font_path` (str, optional): Font file path
  - `output_path` (str, optional): Output file path
  - `**options`: Additional workflow options
- **Returns:** dict - Workflow results
- **Raises:** WorkflowError

---

## Text Processing

### FontLoader

Handles loading and management of font files.

```python
from text_processor import FontLoader

font_loader = FontLoader()
```

#### Methods

**`load_font(font_path, font_size)`**

Load a font file.

- **Parameters:**
  - `font_path` (str): Path to font file
  - `font_size` (int): Font size in points
- **Returns:** bool - Success status
- **Raises:** FontLoadError

**`get_character_outline(character)`**

Get outline data for a character.

- **Parameters:**
  - `character` (str): Single character
- **Returns:** list - List of outline contours
- **Raises:** FontLoadError

**`get_font_metrics()`**

Get font metrics information.

- **Returns:** dict - Font metrics (ascender, descender, height, etc.)

### TextProcessor

Processes text and calculates layout for 3D generation.

```python
from text_processor import TextProcessor

text_processor = TextProcessor(font_loader)
```

#### Constructor

**`TextProcessor(font_loader)`**

- **Parameters:**
  - `font_loader` (FontLoader): FontLoader instance

#### Methods

**`parse_text(text)`**

Parse and validate input text.

- **Parameters:**
  - `text` (str): Input text
- **Returns:** str - Parsed text
- **Raises:** TextProcessingError

**`calculate_layout(text, character_spacing=0.0)`**

Calculate character positions and layout.

- **Parameters:**
  - `text` (str): Text to layout
  - `character_spacing` (float): Additional spacing between characters
- **Returns:** list - List of character layout information

**`get_text_outlines(text)`**

Get outline data for all characters in text.

- **Parameters:**
  - `text` (str): Input text
- **Returns:** dict - Character outlines mapping

---

## Geometry Generation

### GeometryGenerator

Generates 3D meshes from 2D text outlines.

```python
from geometry_generator import GeometryGenerator

geometry_generator = GeometryGenerator()
```

#### Methods

**`generate_mesh(outlines, extrusion_depth, bevel_depth=0.0)`**

Generate 3D mesh from 2D outlines.

- **Parameters:**
  - `outlines` (list): List of 2D outline contours
  - `extrusion_depth` (float): Depth of extrusion
  - `bevel_depth` (float): Depth of bevel effect
- **Returns:** dict - Mesh data (vertices, faces, normals)
- **Raises:** GeometryError

**`extrude_outline(outline, depth)`**

Extrude a 2D outline to create 3D geometry.

- **Parameters:**
  - `outline` (list): 2D outline points
  - `depth` (float): Extrusion depth
- **Returns:** dict - Extruded mesh data

**`apply_bevel(mesh, bevel_depth, resolution=4)`**

Apply bevel effect to mesh edges.

- **Parameters:**
  - `mesh` (dict): Input mesh data
  - `bevel_depth` (float): Bevel depth
  - `resolution` (int): Bevel resolution
- **Returns:** dict - Beveled mesh data

**`calculate_normals(vertices, faces)`**

Calculate vertex normals for a mesh.

- **Parameters:**
  - `vertices` (list): Vertex coordinates
  - `faces` (list): Face indices
- **Returns:** list - Vertex normals

**`validate_mesh(mesh)`**

Validate mesh data integrity.

- **Parameters:**
  - `mesh` (dict): Mesh data to validate
- **Returns:** bool - Validation result
- **Raises:** MeshValidationError

---

## Rendering

### Renderer

Handles 3D visualization and rendering.

```python
from renderer import Renderer

renderer = Renderer(backend='matplotlib')
```

#### Constructor

**`Renderer(backend='matplotlib')`**

- **Parameters:**
  - `backend` (str): Rendering backend ('matplotlib' or 'mayavi')

#### Methods

**`render_interactive(mesh)`**

Show interactive 3D preview.

- **Parameters:**
  - `mesh` (dict): Mesh data to render
- **Raises:** RenderingError

**`render_to_image(mesh, output_path, width=800, height=600)`**

Render mesh to image file.

- **Parameters:**
  - `mesh` (dict): Mesh data to render
  - `output_path` (str): Output image path
  - `width` (int): Image width
  - `height` (int): Image height
- **Returns:** str - Path to saved image
- **Raises:** RenderingError

**`set_camera(camera)`**

Set camera for rendering.

- **Parameters:**
  - `camera` (Camera): Camera instance

**`add_light(light)`**

Add light source to scene.

- **Parameters:**
  - `light` (Light): Light instance

### Camera

Camera control for 3D rendering.

```python
from renderer import Camera

camera = Camera()
```

#### Methods

**`set_position(x, y, z)`**

Set camera position.

- **Parameters:**
  - `x, y, z` (float): Camera coordinates

**`look_at(target)`**

Point camera at target.

- **Parameters:**
  - `target` (tuple): Target coordinates (x, y, z)

**`set_fov(fov)`**

Set field of view.

- **Parameters:**
  - `fov` (float): Field of view in degrees

### Light

Light source for 3D rendering.

```python
from renderer import Light

light = Light(light_type='directional')
```

#### Constructor

**`Light(light_type='directional')`**

- **Parameters:**
  - `light_type` (str): Light type ('directional', 'point', 'ambient')

#### Methods

**`set_position(x, y, z)`**

Set light position.

- **Parameters:**
  - `x, y, z` (float): Light coordinates

**`set_intensity(intensity)`**

Set light intensity.

- **Parameters:**
  - `intensity` (float): Light intensity (0.0-1.0)

**`set_color(r, g, b)`**

Set light color.

- **Parameters:**
  - `r, g, b` (float): RGB color values (0.0-1.0)

---

## Export

### Exporter

Handles export to various 3D file formats.

```python
from exporter import Exporter

exporter = Exporter()
```

#### Methods

**`export_mesh(mesh, output_path, format_type, **options)`**

Export mesh to file.

- **Parameters:**
  - `mesh` (dict): Mesh data to export
  - `output_path` (str): Output file path
  - `format_type` (str): Export format ('STL', 'OBJ', 'PLY', 'GLTF')
  - `**options`: Format-specific options
- **Returns:** str - Path to exported file
- **Raises:** ExportError

**`export_stl(mesh, output_path, binary=True)`**

Export to STL format.

- **Parameters:**
  - `mesh` (dict): Mesh data
  - `output_path` (str): Output path
  - `binary` (bool): Use binary format
- **Returns:** str - Export path

**`export_obj(mesh, output_path, include_materials=False)`**

Export to OBJ format.

- **Parameters:**
  - `mesh` (dict): Mesh data
  - `output_path` (str): Output path
  - `include_materials` (bool): Include material file
- **Returns:** str - Export path

**`export_ply(mesh, output_path, binary=True)`**

Export to PLY format.

- **Parameters:**
  - `mesh` (dict): Mesh data
  - `output_path` (str): Output path
  - `binary` (bool): Use binary format
- **Returns:** str - Export path

**`export_gltf(mesh, output_path, binary=True)`**

Export to GLTF/GLB format.

- **Parameters:**
  - `mesh` (dict): Mesh data
  - `output_path` (str): Output path
  - `binary` (bool): Use binary GLB format
- **Returns:** str - Export path

**`validate_export(file_path, format_type)`**

Validate exported file.

- **Parameters:**
  - `file_path` (str): Path to exported file
  - `format_type` (str): Expected format
- **Returns:** bool - Validation result

---

## Configuration

### Config

Configuration management for the application.

```python
from config import Config

config = Config()
```

#### Class Attributes

**Font Configuration:**
- `DEFAULT_FONT_SIZE` (int): Default font size (48)
- `MIN_FONT_SIZE` (int): Minimum font size (8)
- `MAX_FONT_SIZE` (int): Maximum font size (500)
- `DEFAULT_CHARACTER_SPACING` (float): Default character spacing (0.0)

**3D Configuration:**
- `DEFAULT_EXTRUSION_DEPTH` (float): Default extrusion depth (5.0)
- `MIN_EXTRUSION_DEPTH` (float): Minimum extrusion depth (0.1)
- `MAX_EXTRUSION_DEPTH` (float): Maximum extrusion depth (100.0)
- `DEFAULT_BEVEL_DEPTH` (float): Default bevel depth (0.5)
- `DEFAULT_BEVEL_RESOLUTION` (int): Default bevel resolution (4)

**Export Configuration:**
- `DEFAULT_EXPORT_FORMAT` (str): Default export format ('STL')
- `SUPPORTED_EXPORT_FORMATS` (list): Supported formats
- `DEFAULT_EXPORT_SCALE` (float): Default export scale (1.0)
- `DEFAULT_OUTPUT_DIR` (Path): Default output directory

#### Methods

**`validate_font_size(size)`**

Validate font size.

- **Parameters:**
  - `size` (int): Font size to validate
- **Returns:** bool - Validation result

**`validate_extrusion_depth(depth)`**

Validate extrusion depth.

- **Parameters:**
  - `depth` (float): Depth to validate
- **Returns:** bool - Validation result

**`validate_export_format(format_name)`**

Validate export format.

- **Parameters:**
  - `format_name` (str): Format to validate
- **Returns:** bool - Validation result

**`get_default_font_path()`**

Get path to default system font.

- **Returns:** Path or None - Default font path

---

## Utilities

### Utility Functions

Collection of helper functions.

```python
from utils import setup_logging, ensure_directory_exists, validate_file_path
```

#### File Operations

**`ensure_directory_exists(directory_path)`**

Ensure directory exists, create if necessary.

- **Parameters:**
  - `directory_path` (Path): Directory path
- **Raises:** OSError

**`validate_file_path(file_path)`**

Validate if file path exists and is readable.

- **Parameters:**
  - `file_path` (str): File path to validate
- **Returns:** bool - Validation result

**`safe_filename(filename)`**

Create safe filename by removing invalid characters.

- **Parameters:**
  - `filename` (str): Original filename
- **Returns:** str - Safe filename

**`get_unique_filename(directory, base_name, extension)`**

Generate unique filename in directory.

- **Parameters:**
  - `directory` (Path): Target directory
  - `base_name` (str): Base filename
  - `extension` (str): File extension
- **Returns:** Path - Unique file path

#### Logging

**`setup_logging(level='INFO', log_file=None)`**

Setup application logging.

- **Parameters:**
  - `level` (str): Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
  - `log_file` (Path, optional): Log file path

#### Decorators

**`@measure_time`**

Decorator to measure function execution time.

```python
@measure_time
def my_function():
    # Function implementation
    pass
```

#### JSON Operations

**`load_json_file(file_path)`**

Load JSON data from file.

- **Parameters:**
  - `file_path` (str): JSON file path
- **Returns:** dict - JSON data
- **Raises:** JSONDecodeError

**`save_json_file(data, file_path)`**

Save data to JSON file.

- **Parameters:**
  - `data` (dict): Data to save
  - `file_path` (str): Output file path
- **Raises:** IOError

---

## Error Handling

### Exception Classes

**Base Exceptions:**
- `Text3DGeneratorError`: Base application exception
- `WorkflowError`: Workflow execution failure

**Module-Specific Exceptions:**
- `FontLoadError`: Font loading issues
- `TextProcessingError`: Text processing issues
- `GeometryError`: Geometry generation issues
- `MeshValidationError`: Mesh validation issues
- `RenderingError`: Rendering issues
- `ExportError`: Export issues

### Error Handling Best Practices

```python
try:
    generator = Text3DGenerator()
    result = generator.run_workflow("Hello World", output_path="hello.stl")
except FontLoadError as e:
    print(f"Font loading failed: {e}")
except GeometryError as e:
    print(f"Geometry generation failed: {e}")
except ExportError as e:
    print(f"Export failed: {e}")
except WorkflowError as e:
    print(f"Workflow failed: {e}")
```

---

## Examples

### Basic API Usage

```python
from main import Text3DGenerator

# Initialize generator
generator = Text3DGenerator()

# Load font
generator.load_font("arial.ttf", 48)

# Process text
text_data = generator.process_text("Hello API")

# Generate geometry
geometry_data = generator.generate_geometry(text_data, depth=10.0, bevel_depth=2.0)

# Export model
exported_path = generator.export_model(geometry_data, "hello_api.stl", "STL")

print(f"Model exported to: {exported_path}")
```

### Advanced Workflow

```python
from main import Text3DGenerator

# Configuration overrides
config_overrides = {
    'DEFAULT_OUTPUT_DIR': Path('./custom_output')
}

# Initialize with custom config
generator = Text3DGenerator(config_overrides)

# Run complete workflow
options = {
    'font_size': 64,
    'character_spacing': 1.5,
    'extrusion_depth': 15.0,
    'bevel_depth': 3.0,
    'export_format': 'GLTF',
    'export_scale': 2.0,
    'show_preview': True,
    'save_preview': 'preview.png'
}

result = generator.run_workflow(
    "Advanced Text",
    font_path="custom_font.ttf",
    output_path="advanced.glb",
    **options
)

# Get processing statistics
stats = generator.get_processing_stats()
print(f"Processing completed in {stats['total_time']:.2f} seconds")
```