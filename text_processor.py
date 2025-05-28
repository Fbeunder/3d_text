"""
Text Processing Module for 3D Text Generator

This module provides functionality for font loading, character outline extraction,
and text layout calculations for 3D text generation.
"""

import os
import logging
from typing import List, Tuple, Dict, Optional, Union
from pathlib import Path

try:
    import freetype
except ImportError:
    freetype = None
    logging.warning("freetype-py not available. Font loading functionality will be limited.")

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    Image = ImageFont = ImageDraw = None
    logging.warning("PIL/Pillow not available. Some text processing features will be limited.")

import numpy as np
from config import Config
from utils import validate_file_path, ensure_directory_exists


class FontLoadError(Exception):
    """Exception raised when font loading fails."""
    pass


class TextProcessingError(Exception):
    """Exception raised when text processing fails."""
    pass


class FontLoader:
    """
    Handles font loading and character outline extraction.
    """
    
    def __init__(self):
        self.font = None
        self.font_path = None
        self.font_size = Config.DEFAULT_FONT_SIZE
        self._face = None
        
    def load_font(self, font_path: Union[str, Path], font_size: int = None) -> bool:
        """
        Load a font file (TTF/OTF).
        
        Args:
            font_path: Path to the font file
            font_size: Font size in points (optional)
            
        Returns:
            bool: True if font loaded successfully
            
        Raises:
            FontLoadError: If font loading fails
        """
        try:
            font_path = Path(font_path)
            
            if not validate_font_file(font_path):
                raise FontLoadError(f"Invalid font file: {font_path}")
            
            if font_size:
                self.font_size = font_size
            
            # Try freetype first for better outline extraction
            if freetype:
                try:
                    self._face = freetype.Face(str(font_path))
                    self._face.set_char_size(self.font_size * 64)  # 26.6 fractional points
                    self.font_path = font_path
                    logging.info(f"Font loaded with freetype: {font_path}")
                    return True
                except Exception as e:
                    logging.warning(f"Freetype loading failed: {e}")
            
            # Fallback to PIL
            if ImageFont:
                try:
                    self.font = ImageFont.truetype(str(font_path), self.font_size)
                    self.font_path = font_path
                    logging.info(f"Font loaded with PIL: {font_path}")
                    return True
                except Exception as e:
                    logging.warning(f"PIL font loading failed: {e}")
            
            raise FontLoadError("No suitable font loading library available")
            
        except Exception as e:
            raise FontLoadError(f"Failed to load font {font_path}: {str(e)}")
    
    def get_character_outline(self, char: str) -> List[List[Tuple[float, float]]]:
        """
        Extract character outline as vector paths.
        
        Args:
            char: Single character to extract outline for
            
        Returns:
            List of contours, each contour is a list of (x, y) points
            
        Raises:
            TextProcessingError: If outline extraction fails
        """
        if not self._face and not self.font:
            raise TextProcessingError("No font loaded")
        
        if len(char) != 1:
            raise TextProcessingError("Only single characters supported")
        
        try:
            if self._face:
                return self._get_freetype_outline(char)
            elif self.font:
                return self._get_pil_outline(char)
            else:
                raise TextProcessingError("No font loading method available")
                
        except Exception as e:
            raise TextProcessingError(f"Failed to extract outline for '{char}': {str(e)}")
    
    def _get_freetype_outline(self, char: str) -> List[List[Tuple[float, float]]]:
        """Extract outline using freetype."""
        self._face.load_char(char)
        outline = self._face.glyph.outline
        
        contours = []
        start = 0
        
        for end in outline.contours:
            contour = []
            for i in range(start, end + 1):
                x, y = outline.points[i]
                # Convert from 26.6 fractional points to float
                contour.append((x / 64.0, y / 64.0))
            contours.append(contour)
            start = end + 1
            
        return contours
    
    def _get_pil_outline(self, char: str) -> List[List[Tuple[float, float]]]:
        """Extract outline using PIL (simplified approach)."""
        # PIL doesn't provide direct outline access, so we create a simplified version
        # This is a fallback method with limited functionality
        bbox = self.font.getbbox(char)
        if not bbox:
            return []
        
        # Create a simple rectangular outline as fallback
        x1, y1, x2, y2 = bbox
        contour = [
            (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
        ]
        return [contour]
    
    def get_font_metrics(self) -> Dict[str, float]:
        """
        Get font metrics and properties.
        
        Returns:
            Dictionary with font metrics
        """
        if not self._face and not self.font:
            raise TextProcessingError("No font loaded")
        
        metrics = {
            'font_size': self.font_size,
            'font_path': str(self.font_path) if self.font_path else None
        }
        
        if self._face:
            metrics.update({
                'ascender': self._face.ascender / 64.0,
                'descender': self._face.descender / 64.0,
                'height': self._face.height / 64.0,
                'max_advance_width': self._face.max_advance_width / 64.0,
                'units_per_em': self._face.units_per_EM
            })
        elif self.font:
            # Limited metrics from PIL
            ascent, descent = self.font.getmetrics()
            metrics.update({
                'ascender': ascent,
                'descender': descent,
                'height': ascent + descent
            })
        
        return metrics


class TextProcessor:
    """
    Handles text parsing, validation, and layout calculations.
    """
    
    def __init__(self, font_loader: FontLoader = None):
        self.font_loader = font_loader or FontLoader()
        self.default_spacing = Config.DEFAULT_CHARACTER_SPACING
        
    def parse_text(self, text: str) -> str:
        """
        Parse and validate input text.
        
        Args:
            text: Input text string
            
        Returns:
            Normalized and validated text
            
        Raises:
            TextProcessingError: If text is invalid
        """
        if not text:
            raise TextProcessingError("Empty text provided")
        
        if not isinstance(text, str):
            raise TextProcessingError("Text must be a string")
        
        # Normalize text
        normalized = normalize_text(text)
        
        # Validate characters are supported
        if not self._validate_characters(normalized):
            raise TextProcessingError("Text contains unsupported characters")
        
        return normalized
    
    def _validate_characters(self, text: str) -> bool:
        """Validate that all characters in text are supported."""
        # For now, accept all printable ASCII characters
        return all(ord(c) >= 32 and ord(c) <= 126 for c in text if not c.isspace())
    
    def calculate_layout(self, text: str, spacing: float = None) -> List[Dict]:
        """
        Calculate character positions for text layout.
        
        Args:
            text: Text to layout
            spacing: Character spacing (optional)
            
        Returns:
            List of character layout information
        """
        if spacing is None:
            spacing = self.default_spacing
        
        parsed_text = self.parse_text(text)
        layout = []
        x_offset = 0.0
        
        for i, char in enumerate(parsed_text):
            if char.isspace():
                # Handle spaces
                space_width = self._get_space_width()
                x_offset += space_width + spacing
                continue
            
            char_info = {
                'character': char,
                'position': (x_offset, 0.0),
                'index': i
            }
            
            # Get character width for next position calculation
            char_width = self._get_character_width(char)
            char_info['width'] = char_width
            
            layout.append(char_info)
            x_offset += char_width + spacing
        
        return layout
    
    def _get_character_width(self, char: str) -> float:
        """Get the width of a character."""
        if not self.font_loader.font and not self.font_loader._face:
            return Config.DEFAULT_CHARACTER_WIDTH
        
        try:
            if self.font_loader._face:
                self.font_loader._face.load_char(char)
                return self.font_loader._face.glyph.advance.x / 64.0
            elif self.font_loader.font:
                bbox = self.font_loader.font.getbbox(char)
                return bbox[2] - bbox[0] if bbox else Config.DEFAULT_CHARACTER_WIDTH
        except:
            pass
        
        return Config.DEFAULT_CHARACTER_WIDTH
    
    def _get_space_width(self) -> float:
        """Get the width of a space character."""
        try:
            return self._get_character_width(' ')
        except:
            return Config.DEFAULT_CHARACTER_WIDTH * 0.5
    
    def get_text_outlines(self, text: str) -> Dict[str, List[List[Tuple[float, float]]]]:
        """
        Get outlines for all characters in text.
        
        Args:
            text: Text to get outlines for
            
        Returns:
            Dictionary mapping characters to their outlines
        """
        parsed_text = self.parse_text(text)
        outlines = {}
        
        for char in set(parsed_text):
            if not char.isspace():
                try:
                    outlines[char] = self.font_loader.get_character_outline(char)
                except Exception as e:
                    logging.warning(f"Failed to get outline for '{char}': {e}")
                    outlines[char] = []
        
        return outlines


# Utility functions

def validate_font_file(path: Union[str, Path]) -> bool:
    """
    Validate if a file is a valid font file.
    
    Args:
        path: Path to font file
        
    Returns:
        bool: True if valid font file
    """
    if not validate_file_path(path):
        return False
    
    path = Path(path)
    valid_extensions = {'.ttf', '.otf', '.woff', '.woff2'}
    
    if path.suffix.lower() not in valid_extensions:
        return False
    
    # Additional validation could be added here
    # (e.g., checking file headers)
    
    return True


def normalize_text(text: str) -> str:
    """
    Normalize text for processing.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    normalized = text.strip()
    
    # Replace multiple spaces with single space
    import re
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized


# Example usage and testing
if __name__ == "__main__":
    # Basic testing
    try:
        # Test font loading
        font_loader = FontLoader()
        
        # Test text processing
        processor = TextProcessor(font_loader)
        
        test_text = "Hello World!"
        parsed = processor.parse_text(test_text)
        layout = processor.calculate_layout(parsed)
        
        print(f"Parsed text: '{parsed}'")
        print(f"Layout: {len(layout)} characters")
        
        for char_info in layout:
            print(f"  {char_info['character']} at {char_info['position']}")
            
    except Exception as e:
        print(f"Error during testing: {e}")