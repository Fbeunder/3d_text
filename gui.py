#!/usr/bin/env python3
"""
3D Text Generator - GUI Interface

Graphical user interface for the 3D Text Generator application using tkinter.
Provides a user-friendly interface for all CLI functionality with embedded 3D preview.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import queue
import time

# Import matplotlib for 3D preview
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("Matplotlib not available - 3D preview will be disabled")

# Import core modules
from main import Text3DGenerator, WorkflowError
from config import Config
from utils import safe_filename, validate_file_path


class GUIError(Exception):
    """Base exception for GUI-related errors."""
    pass


class SettingsManager:
    """Manages GUI settings persistence."""
    
    def __init__(self, settings_file: str = "gui_settings.json"):
        self.settings_file = Path(settings_file)
        self.default_settings = {
            'window_geometry': '1200x800+100+100',
            'font_path': '',
            'font_size': Config.DEFAULT_FONT_SIZE,
            'character_spacing': Config.DEFAULT_CHARACTER_SPACING,
            'extrusion_depth': Config.DEFAULT_EXTRUSION_DEPTH,
            'bevel_depth': Config.DEFAULT_BEVEL_DEPTH,
            'bevel_resolution': Config.DEFAULT_BEVEL_RESOLUTION,
            'export_format': Config.DEFAULT_EXPORT_FORMAT,
            'export_scale': Config.DEFAULT_EXPORT_SCALE,
            'output_directory': str(Config.DEFAULT_OUTPUT_DIR),
            'last_text': '',
            'auto_preview': True,
            'show_statistics': True
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                # Merge with defaults to handle new settings
                settings = self.default_settings.copy()
                settings.update(loaded)
                return settings
        except Exception as e:
            logging.warning(f"Failed to load settings: {e}")
        
        return self.default_settings.copy()
    
    def save_settings(self) -> None:
        """Save current settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")
    
    def get(self, key: str, default=None):
        """Get setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set setting value."""
        self.settings[key] = value


class ProgressDialog:
    """Dialog for showing progress during background operations."""
    
    def __init__(self, parent, title: str = "Processing..."):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (150 // 2)
        self.dialog.geometry(f"400x150+{x}+{y}")
        
        # Progress widgets
        self.setup_widgets()
        
        # Progress tracking
        self.cancelled = False
    
    def setup_widgets(self):
        """Setup progress dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Initializing...")
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Cancel button
        self.cancel_button = ttk.Button(
            main_frame,
            text="Cancel",
            command=self.cancel
        )
        self.cancel_button.pack()
    
    def update_progress(self, progress: float, status: str = None):
        """Update progress bar and status."""
        if self.dialog.winfo_exists():
            self.progress_var.set(progress)
            if status:
                self.status_label.config(text=status)
            self.dialog.update()
    
    def cancel(self):
        """Cancel the operation."""
        self.cancelled = True
        self.close()
    
    def close(self):
        """Close the progress dialog."""
        if self.dialog.winfo_exists():
            self.dialog.destroy()


class TextInputPanel:
    """Panel for text input and font configuration."""
    
    def __init__(self, parent, settings_manager: SettingsManager):
        self.parent = parent
        self.settings = settings_manager
        self.setup_widgets()
    
    def setup_widgets(self):
        """Setup text input panel widgets."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Text Input", padding="10")
        
        # Text input
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(text_frame, text="Text:").pack(anchor=tk.W)
        self.text_var = tk.StringVar(value=self.settings.get('last_text', ''))
        self.text_entry = ttk.Entry(text_frame, textvariable=self.text_var, font=('Arial', 12))
        self.text_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Font selection
        font_frame = ttk.Frame(self.frame)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_frame, text="Font:").pack(anchor=tk.W)
        
        font_select_frame = ttk.Frame(font_frame)
        font_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.font_path_var = tk.StringVar(value=self.settings.get('font_path', ''))
        self.font_entry = ttk.Entry(font_select_frame, textvariable=self.font_path_var)
        self.font_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(
            font_select_frame,
            text="Browse...",
            command=self.browse_font
        )
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Font settings
        settings_frame = ttk.Frame(self.frame)
        settings_frame.pack(fill=tk.X)
        
        # Font size
        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Label(size_frame, text="Font Size:").pack(anchor=tk.W)
        self.font_size_var = tk.IntVar(value=self.settings.get('font_size'))
        size_spinbox = ttk.Spinbox(
            size_frame,
            from_=Config.MIN_FONT_SIZE,
            to=Config.MAX_FONT_SIZE,
            textvariable=self.font_size_var,
            width=10
        )
        size_spinbox.pack(anchor=tk.W, pady=(2, 0))
        
        # Character spacing
        spacing_frame = ttk.Frame(settings_frame)
        spacing_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        ttk.Label(spacing_frame, text="Character Spacing:").pack(anchor=tk.W)
        self.char_spacing_var = tk.DoubleVar(value=self.settings.get('character_spacing'))
        spacing_spinbox = ttk.Spinbox(
            spacing_frame,
            from_=0.0,
            to=10.0,
            increment=0.1,
            textvariable=self.char_spacing_var,
            width=10,
            format="%.1f"
        )
        spacing_spinbox.pack(anchor=tk.W, pady=(2, 0))
    
    def browse_font(self):
        """Open font file browser dialog."""
        filetypes = [
            ("Font files", "*.ttf *.otf *.woff *.woff2"),
            ("TrueType fonts", "*.ttf"),
            ("OpenType fonts", "*.otf"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Font File",
            filetypes=filetypes
        )
        
        if filename:
            self.font_path_var.set(filename)
    
    def get_values(self) -> Dict[str, Any]:
        """Get current input values."""
        return {
            'text': self.text_var.get().strip(),
            'font_path': self.font_path_var.get().strip(),
            'font_size': self.font_size_var.get(),
            'character_spacing': self.char_spacing_var.get()
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate current input values."""
        values = self.get_values()
        
        if not values['text']:
            return False, "Please enter text to convert"
        
        if len(values['text']) > Config.MAX_TEXT_LENGTH:
            return False, f"Text too long (max {Config.MAX_TEXT_LENGTH} characters)"
        
        if values['font_path'] and not validate_file_path(values['font_path']):
            return False, f"Font file not found: {values['font_path']}"
        
        if not Config.validate_font_size(values['font_size']):
            return False, f"Font size must be between {Config.MIN_FONT_SIZE} and {Config.MAX_FONT_SIZE}"
        
        return True, ""


class GeometryPanel:
    """Panel for 3D geometry configuration."""
    
    def __init__(self, parent, settings_manager: SettingsManager):
        self.parent = parent
        self.settings = settings_manager
        self.setup_widgets()
    
    def setup_widgets(self):
        """Setup geometry panel widgets."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="3D Geometry", padding="10")
        
        # Extrusion depth
        depth_frame = ttk.Frame(self.frame)
        depth_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(depth_frame, text="Extrusion Depth:").pack(anchor=tk.W)
        self.extrusion_depth_var = tk.DoubleVar(value=self.settings.get('extrusion_depth'))
        depth_spinbox = ttk.Spinbox(
            depth_frame,
            from_=Config.MIN_EXTRUSION_DEPTH,
            to=Config.MAX_EXTRUSION_DEPTH,
            increment=0.5,
            textvariable=self.extrusion_depth_var,
            width=15,
            format="%.1f"
        )
        depth_spinbox.pack(anchor=tk.W, pady=(2, 0))
        
        # Bevel settings
        bevel_frame = ttk.Frame(self.frame)
        bevel_frame.pack(fill=tk.X)
        
        # Bevel depth
        bevel_depth_frame = ttk.Frame(bevel_frame)
        bevel_depth_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Label(bevel_depth_frame, text="Bevel Depth:").pack(anchor=tk.W)
        self.bevel_depth_var = tk.DoubleVar(value=self.settings.get('bevel_depth'))
        bevel_depth_spinbox = ttk.Spinbox(
            bevel_depth_frame,
            from_=0.0,
            to=10.0,
            increment=0.1,
            textvariable=self.bevel_depth_var,
            width=10,
            format="%.1f"
        )
        bevel_depth_spinbox.pack(anchor=tk.W, pady=(2, 0))
        
        # Bevel resolution
        bevel_res_frame = ttk.Frame(bevel_frame)
        bevel_res_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        ttk.Label(bevel_res_frame, text="Bevel Resolution:").pack(anchor=tk.W)
        self.bevel_resolution_var = tk.IntVar(value=self.settings.get('bevel_resolution'))
        bevel_res_spinbox = ttk.Spinbox(
            bevel_res_frame,
            from_=1,
            to=16,
            textvariable=self.bevel_resolution_var,
            width=10
        )
        bevel_res_spinbox.pack(anchor=tk.W, pady=(2, 0))
    
    def get_values(self) -> Dict[str, Any]:
        """Get current geometry values."""
        return {
            'extrusion_depth': self.extrusion_depth_var.get(),
            'bevel_depth': self.bevel_depth_var.get(),
            'bevel_resolution': self.bevel_resolution_var.get()
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate current geometry values."""
        values = self.get_values()
        
        if not Config.validate_extrusion_depth(values['extrusion_depth']):
            return False, f"Extrusion depth must be between {Config.MIN_EXTRUSION_DEPTH} and {Config.MAX_EXTRUSION_DEPTH}"
        
        if values['bevel_depth'] < 0:
            return False, "Bevel depth cannot be negative"
        
        if values['bevel_depth'] >= values['extrusion_depth']:
            return False, "Bevel depth must be less than extrusion depth"
        
        return True, ""


class ExportPanel:
    """Panel for export configuration."""
    
    def __init__(self, parent, settings_manager: SettingsManager):
        self.parent = parent
        self.settings = settings_manager
        self.setup_widgets()
    
    def setup_widgets(self):
        """Setup export panel widgets."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Export Options", padding="10")
        
        # Format selection
        format_frame = ttk.Frame(self.frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(format_frame, text="Export Format:").pack(anchor=tk.W)
        self.export_format_var = tk.StringVar(value=self.settings.get('export_format'))
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.export_format_var,
            values=list(Config.SUPPORTED_EXPORT_FORMATS),
            state="readonly",
            width=15
        )
        format_combo.pack(anchor=tk.W, pady=(2, 0))
        
        # Scale and output directory
        options_frame = ttk.Frame(self.frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Export scale
        scale_frame = ttk.Frame(options_frame)
        scale_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Label(scale_frame, text="Scale Factor:").pack(anchor=tk.W)
        self.export_scale_var = tk.DoubleVar(value=self.settings.get('export_scale'))
        scale_spinbox = ttk.Spinbox(
            scale_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.export_scale_var,
            width=10,
            format="%.1f"
        )
        scale_spinbox.pack(anchor=tk.W, pady=(2, 0))
        
        # Output directory
        output_frame = ttk.Frame(self.frame)
        output_frame.pack(fill=tk.X)
        
        ttk.Label(output_frame, text="Output Directory:").pack(anchor=tk.W)
        
        output_select_frame = ttk.Frame(output_frame)
        output_select_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.output_dir_var = tk.StringVar(value=self.settings.get('output_directory'))
        self.output_entry = ttk.Entry(output_select_frame, textvariable=self.output_dir_var)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_output_button = ttk.Button(
            output_select_frame,
            text="Browse...",
            command=self.browse_output_directory
        )
        self.browse_output_button.pack(side=tk.RIGHT, padx=(5, 0))
    
    def browse_output_directory(self):
        """Open output directory browser dialog."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )
        
        if directory:
            self.output_dir_var.set(directory)
    
    def get_values(self) -> Dict[str, Any]:
        """Get current export values."""
        return {
            'export_format': self.export_format_var.get(),
            'export_scale': self.export_scale_var.get(),
            'output_directory': self.output_dir_var.get()
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate current export values."""
        values = self.get_values()
        
        if not Config.validate_export_format(values['export_format']):
            return False, f"Unsupported export format: {values['export_format']}"
        
        if values['export_scale'] <= 0:
            return False, "Export scale must be positive"
        
        output_dir = Path(values['output_directory'])
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create output directory: {e}"
        
        return True, ""


class PreviewPanel:
    """Panel for 3D preview display."""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_mesh = None
        self.setup_widgets()
    
    def setup_widgets(self):
        """Setup preview panel widgets."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="3D Preview", padding="10")
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure
            self.fig = Figure(figsize=(6, 4), dpi=100)
            self.ax = self.fig.add_subplot(111, projection='3d')
            
            # Create canvas
            self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Control buttons
            control_frame = ttk.Frame(self.frame)
            control_frame.pack(fill=tk.X, pady=(10, 0))
            
            self.refresh_button = ttk.Button(
                control_frame,
                text="Refresh Preview",
                command=self.refresh_preview
            )
            self.refresh_button.pack(side=tk.LEFT)
            
            self.save_preview_button = ttk.Button(
                control_frame,
                text="Save Preview",
                command=self.save_preview
            )
            self.save_preview_button.pack(side=tk.LEFT, padx=(5, 0))
            
            # Initialize empty preview
            self.show_empty_preview()
        else:
            # Show message if matplotlib not available
            message_label = ttk.Label(
                self.frame,
                text="3D Preview not available\n(matplotlib not installed)",
                justify=tk.CENTER
            )
            message_label.pack(expand=True)
    
    def show_empty_preview(self):
        """Show empty preview state."""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        self.ax.clear()
        self.ax.text(0.5, 0.5, 0.5, 'No preview available\nGenerate 3D text to see preview',
                    horizontalalignment='center', verticalalignment='center',
                    transform=self.ax.transAxes, fontsize=12)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.canvas.draw()
    
    def update_preview(self, mesh_data: Dict):
        """Update preview with new mesh data."""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        try:
            self.current_mesh = mesh_data
            mesh = mesh_data.get('mesh')
            
            if not mesh or not mesh.get('vertices') or not mesh.get('faces'):
                self.show_empty_preview()
                return
            
            vertices = np.array(mesh['vertices'])
            faces = np.array(mesh['faces'])
            
            # Clear previous plot
            self.ax.clear()
            
            # Plot the mesh
            for face in faces:
                if len(face) >= 3:
                    # Get vertices for this face
                    face_vertices = vertices[face[:3]]  # Use first 3 vertices for triangulation
                    
                    # Create triangle
                    triangle = [[face_vertices[0], face_vertices[1], face_vertices[2], face_vertices[0]]]
                    
                    # Plot triangle edges
                    for tri in triangle:
                        tri = np.array(tri)
                        self.ax.plot(tri[:, 0], tri[:, 1], tri[:, 2], 'b-', alpha=0.6, linewidth=0.5)
            
            # Set equal aspect ratio and labels
            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Y')
            self.ax.set_zlabel('Z')
            
            # Set view limits based on mesh bounds
            if vertices.size > 0:
                bounds = mesh_data.get('bounds', {})
                if bounds:
                    min_bounds = bounds.get('min', vertices.min(axis=0))
                    max_bounds = bounds.get('max', vertices.max(axis=0))
                    
                    self.ax.set_xlim(min_bounds[0], max_bounds[0])
                    self.ax.set_ylim(min_bounds[1], max_bounds[1])
                    self.ax.set_zlim(min_bounds[2], max_bounds[2])
            
            # Set title
            stats = mesh_data.get('total_vertices', 0), mesh_data.get('total_faces', 0)
            self.ax.set_title(f'3D Text Preview\n{stats[0]} vertices, {stats[1]} faces')
            
            self.canvas.draw()
            
        except Exception as e:
            logging.error(f"Failed to update preview: {e}")
            self.show_empty_preview()
    
    def refresh_preview(self):
        """Refresh the current preview."""
        if self.current_mesh:
            self.update_preview(self.current_mesh)
    
    def save_preview(self):
        """Save preview image to file."""
        if not MATPLOTLIB_AVAILABLE or not self.current_mesh:
            messagebox.showwarning("Warning", "No preview available to save")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Preview Image",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Preview saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save preview: {e}")


class GUIApplication:
    """Main GUI application class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Text Generator")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.settings = SettingsManager()
        self.generator = Text3DGenerator()
        self.current_results = None
        
        # Setup GUI
        self.setup_menu()
        self.setup_widgets()
        self.setup_bindings()
        
        # Apply saved settings
        self.apply_settings()
        
        # Setup logging
        self.setup_logging()
    
    def setup_menu(self):
        """Setup application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Export...", command=self.export_model, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_application, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences...", command=self.show_preferences)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh Preview", command=self.refresh_preview)
        view_menu.add_command(label="Show Statistics", command=self.show_statistics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="API Documentation", command=self.show_api_docs)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_widgets(self):
        """Setup main application widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for input controls
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Text input panel
        self.text_panel = TextInputPanel(left_frame, self.settings)
        self.text_panel.frame.pack(fill=tk.X, pady=(0, 10))
        
        # Geometry panel
        self.geometry_panel = GeometryPanel(left_frame, self.settings)
        self.geometry_panel.frame.pack(fill=tk.X, pady=(0, 10))
        
        # Export panel
        self.export_panel = ExportPanel(left_frame, self.settings)
        self.export_panel.frame.pack(fill=tk.X, pady=(0, 10))
        
        # Control buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.generate_button = ttk.Button(
            button_frame,
            text="Generate 3D Text",
            command=self.generate_3d_text,
            style="Accent.TButton"
        )
        self.generate_button.pack(fill=tk.X, pady=(0, 5))
        
        self.preview_button = ttk.Button(
            button_frame,
            text="Preview Only",
            command=self.preview_only
        )
        self.preview_button.pack(fill=tk.X, pady=(0, 5))
        
        self.export_button = ttk.Button(
            button_frame,
            text="Export Model",
            command=self.export_model,
            state=tk.DISABLED
        )
        self.export_button.pack(fill=tk.X)
        
        # Right panel for preview and status
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Preview panel
        self.preview_panel = PreviewPanel(right_frame)
        self.preview_panel.frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Status panel
        status_frame = ttk.LabelFrame(right_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X)
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=6,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_bindings(self):
        """Setup keyboard bindings."""
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-e>', lambda e: self.export_model())
        self.root.bind('<Control-q>', lambda e: self.quit_application())
        self.root.bind('<F5>', lambda e: self.refresh_preview())
        
        # Auto-preview on text change
        self.text_panel.text_var.trace('w', self.on_text_change)
    
    def setup_logging(self):
        """Setup logging to status panel."""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)
                self.text_widget.update()
        
        # Add GUI handler to root logger
        gui_handler = GUILogHandler(self.status_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def apply_settings(self):
        """Apply saved settings to GUI."""
        # Window geometry
        geometry = self.settings.get('window_geometry')
        if geometry:
            try:
                self.root.geometry(geometry)
            except:
                pass
    
    def save_settings(self):
        """Save current GUI settings."""
        # Window geometry
        self.settings.set('window_geometry', self.root.geometry())
        
        # Input values
        text_values = self.text_panel.get_values()
        geometry_values = self.geometry_panel.get_values()
        export_values = self.export_panel.get_values()
        
        for key, value in text_values.items():
            if key == 'text':
                self.settings.set('last_text', value)
            else:
                self.settings.set(key, value)
        
        for key, value in geometry_values.items():
            self.settings.set(key, value)
        
        for key, value in export_values.items():
            self.settings.set(key, value)
        
        self.settings.save_settings()
    
    def on_text_change(self, *args):
        """Handle text input changes."""
        if self.settings.get('auto_preview', True):
            # Schedule preview update after short delay
            self.root.after(1000, self.auto_preview)
    
    def auto_preview(self):
        """Automatically generate preview if enabled."""
        if self.settings.get('auto_preview', True) and self.text_panel.text_var.get().strip():
            self.preview_only()
    
    def validate_all_inputs(self) -> tuple[bool, str]:
        """Validate all input panels."""
        # Validate text input
        valid, message = self.text_panel.validate()
        if not valid:
            return False, message
        
        # Validate geometry
        valid, message = self.geometry_panel.validate()
        if not valid:
            return False, message
        
        # Validate export
        valid, message = self.export_panel.validate()
        if not valid:
            return False, message
        
        return True, ""
    
    def generate_3d_text(self):
        """Generate 3D text with full workflow."""
        self.run_workflow(export_model=True)
    
    def preview_only(self):
        """Generate preview only without export."""
        self.run_workflow(export_model=False)
    
    def run_workflow(self, export_model: bool = True):
        """Run the 3D text generation workflow."""
        # Validate inputs
        valid, message = self.validate_all_inputs()
        if not valid:
            messagebox.showerror("Validation Error", message)
            return
        
        # Get all input values
        text_values = self.text_panel.get_values()
        geometry_values = self.geometry_panel.get_values()
        export_values = self.export_panel.get_values()
        
        # Disable buttons during processing
        self.generate_button.config(state=tk.DISABLED)
        self.preview_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Generating 3D Text...")
        
        # Run workflow in background thread
        def workflow_thread():
            try:
                # Prepare workflow options
                workflow_options = {
                    'font_size': text_values['font_size'],
                    'character_spacing': text_values['character_spacing'],
                    'extrusion_depth': geometry_values['extrusion_depth'],
                    'bevel_depth': geometry_values['bevel_depth'],
                    'export_format': export_values['export_format'],
                    'export_scale': export_values['export_scale'],
                    'show_preview': False,  # We handle preview in GUI
                    'save_preview': False
                }
                
                # Generate output path if exporting
                output_path = None
                if export_model:
                    text_safe = safe_filename(text_values['text'][:20])
                    if not text_safe:
                        text_safe = "text_3d"
                    
                    extension = export_values['export_format'].lower()
                    if extension == 'gltf':
                        extension = 'glb'
                    
                    output_dir = Path(export_values['output_directory'])
                    output_path = output_dir / f"{text_safe}.{extension}"
                    
                    # Make unique if exists
                    counter = 1
                    while output_path.exists():
                        output_path = output_dir / f"{text_safe}_{counter}.{extension}"
                        counter += 1
                
                # Update progress
                progress.update_progress(10, "Loading font...")
                
                # Run workflow
                results = self.generator.run_workflow(
                    text_values['text'],
                    text_values['font_path'] if text_values['font_path'] else None,
                    str(output_path) if output_path else None,
                    **workflow_options
                )
                
                progress.update_progress(100, "Complete!")
                
                # Store results
                self.current_results = results
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.workflow_completed(results, export_model))
                
            except Exception as e:
                logging.error(f"Workflow failed: {e}")
                self.root.after(0, lambda: self.workflow_failed(str(e)))
            finally:
                self.root.after(0, progress.close)
        
        # Start workflow thread
        thread = threading.Thread(target=workflow_thread, daemon=True)
        thread.start()
    
    def workflow_completed(self, results: Dict, exported: bool):
        """Handle successful workflow completion."""
        # Re-enable buttons
        self.generate_button.config(state=tk.NORMAL)
        self.preview_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)
        
        # Update preview
        geometry_data = results.get('geometry_generation')
        if geometry_data:
            self.preview_panel.update_preview(geometry_data)
        
        # Show success message
        if exported and 'exported_path' in results:
            messagebox.showinfo("Success", f"3D text generated successfully!\nExported to: {results['exported_path']}")
        else:
            messagebox.showinfo("Success", "3D text preview generated successfully!")
        
        # Show statistics if enabled
        if self.settings.get('show_statistics', True):
            self.show_statistics()
    
    def workflow_failed(self, error_message: str):
        """Handle workflow failure."""
        # Re-enable buttons
        self.generate_button.config(state=tk.NORMAL)
        self.preview_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)
        
        # Show error message
        messagebox.showerror("Error", f"Failed to generate 3D text:\n{error_message}")
    
    def export_model(self):
        """Export the current model."""
        if not self.current_results:
            messagebox.showwarning("Warning", "No model to export. Generate 3D text first.")
            return
        
        geometry_data = self.current_results.get('geometry_generation')
        if not geometry_data:
            messagebox.showerror("Error", "No geometry data available for export")
            return
        
        # Get export settings
        export_values = self.export_panel.get_values()
        
        # Ask for output file
        extension = export_values['export_format'].lower()
        if extension == 'gltf':
            extension = 'glb'
        
        filename = filedialog.asksaveasfilename(
            title="Export 3D Model",
            defaultextension=f".{extension}",
            filetypes=[
                (f"{export_values['export_format']} files", f"*.{extension}"),
                ("All files", "*.*")
            ],
            initialdir=export_values['output_directory']
        )
        
        if filename:
            try:
                exported_path = self.generator.export_model(
                    geometry_data,
                    filename,
                    export_values['export_format'],
                    export_scale=export_values['export_scale']
                )
                messagebox.showinfo("Success", f"Model exported to: {exported_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export model: {e}")
    
    def refresh_preview(self):
        """Refresh the 3D preview."""
        self.preview_panel.refresh_preview()
    
    def show_statistics(self):
        """Show processing statistics."""
        if not self.current_results:
            messagebox.showinfo("Statistics", "No processing statistics available.")
            return
        
        stats = self.current_results.get('processing_stats', {})
        if not stats:
            messagebox.showinfo("Statistics", "No processing statistics available.")
            return
        
        # Create statistics window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Processing Statistics")
        stats_window.geometry("400x300")
        stats_window.transient(self.root)
        
        # Statistics text
        stats_text = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD)
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Format statistics
        stats_content = "PROCESSING STATISTICS\n" + "="*50 + "\n\n"
        
        if 'font_path' in stats:
            stats_content += f"Font: {stats['font_path']}\n"
            stats_content += f"Font Size: {stats.get('font_size', 'N/A')}\n\n"
        
        if 'character_count' in stats:
            stats_content += f"Characters: {stats['character_count']}\n"
        
        if 'total_width' in stats:
            stats_content += f"Text Width: {stats['total_width']:.2f}\n\n"
        
        if 'vertices' in stats and 'faces' in stats:
            stats_content += f"Vertices: {stats['vertices']:,}\n"
            stats_content += f"Faces: {stats['faces']:,}\n\n"
        
        if 'extrusion_depth' in stats:
            stats_content += f"Extrusion Depth: {stats['extrusion_depth']}\n"
        
        if 'bevel_depth' in stats:
            stats_content += f"Bevel Depth: {stats['bevel_depth']}\n\n"
        
        if 'export_format' in stats and 'export_path' in stats:
            stats_content += f"Export Format: {stats['export_format']}\n"
            stats_content += f"Export Path: {stats['export_path']}\n\n"
        
        if 'total_time' in stats:
            stats_content += f"Total Time: {stats['total_time']:.2f} seconds\n"
        
        stats_text.insert(tk.END, stats_content)
        stats_text.config(state=tk.DISABLED)
    
    def new_project(self):
        """Start a new project."""
        # Clear inputs
        self.text_panel.text_var.set("")
        self.text_panel.font_path_var.set("")
        
        # Reset to defaults
        self.text_panel.font_size_var.set(Config.DEFAULT_FONT_SIZE)
        self.text_panel.char_spacing_var.set(Config.DEFAULT_CHARACTER_SPACING)
        self.geometry_panel.extrusion_depth_var.set(Config.DEFAULT_EXTRUSION_DEPTH)
        self.geometry_panel.bevel_depth_var.set(Config.DEFAULT_BEVEL_DEPTH)
        self.geometry_panel.bevel_resolution_var.set(Config.DEFAULT_BEVEL_RESOLUTION)
        self.export_panel.export_format_var.set(Config.DEFAULT_EXPORT_FORMAT)
        self.export_panel.export_scale_var.set(Config.DEFAULT_EXPORT_SCALE)
        
        # Clear preview and results
        self.preview_panel.show_empty_preview()
        self.current_results = None
        self.export_button.config(state=tk.DISABLED)
        
        # Clear status
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def show_preferences(self):
        """Show preferences dialog."""
        messagebox.showinfo("Preferences", "Preferences dialog not yet implemented.")
    
    def show_user_guide(self):
        """Show user guide."""
        messagebox.showinfo("User Guide", "User guide will open in browser.\n(Not yet implemented)")
    
    def show_api_docs(self):
        """Show API documentation."""
        messagebox.showinfo("API Documentation", "API documentation will open in browser.\n(Not yet implemented)")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """3D Text Generator
        
A Python application for converting 2D text to 3D models.

Features:
• Support for TTF/OTF fonts
• Multiple export formats (STL, OBJ, PLY, GLTF)
• Real-time 3D preview
• Customizable geometry parameters
• Batch processing capabilities

Version: 1.0.0
"""
        messagebox.showinfo("About", about_text)
    
    def quit_application(self):
        """Quit the application."""
        # Save settings
        self.save_settings()
        
        # Close application
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the GUI application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_application()


def main():
    """Main entry point for GUI application."""
    try:
        app = GUIApplication()
        app.run()
    except Exception as e:
        logging.error(f"GUI application error: {e}")
        messagebox.showerror("Error", f"Failed to start GUI application: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())