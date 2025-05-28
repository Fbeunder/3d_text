"""
Unit tests for text_processor module.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
import sys
sys.path.append('..')
from text_processor import (
    FontLoader, TextProcessor, FontLoadError, TextProcessingError,
    validate_font_file, normalize_text
)


class TestFontLoader(unittest.TestCase):
    """Test cases for FontLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.font_loader = FontLoader()
    
    def test_init(self):
        """Test FontLoader initialization."""
        self.assertIsNone(self.font_loader.font)
        self.assertIsNone(self.font_loader.font_path)
        self.assertIsNone(self.font_loader._face)
        self.assertIsNotNone(self.font_loader.font_size)
    
    @patch('text_processor.validate_font_file')
    @patch('text_processor.freetype')
    def test_load_font_with_freetype_success(self, mock_freetype, mock_validate):
        """Test successful font loading with freetype."""
        mock_validate.return_value = True
        mock_face = Mock()
        mock_freetype.Face.return_value = mock_face
        
        result = self.font_loader.load_font("test.ttf", 24)
        
        self.assertTrue(result)
        self.assertEqual(self.font_loader.font_size, 24)
        mock_face.set_char_size.assert_called_once_with(24 * 64)
    
    @patch('text_processor.validate_font_file')
    @patch('text_processor.freetype', None)
    @patch('text_processor.ImageFont')
    def test_load_font_with_pil_fallback(self, mock_imagefont, mock_validate):
        """Test font loading fallback to PIL."""
        mock_validate.return_value = True
        mock_font = Mock()
        mock_imagefont.truetype.return_value = mock_font
        
        result = self.font_loader.load_font("test.ttf")
        
        self.assertTrue(result)
        self.assertEqual(self.font_loader.font, mock_font)
    
    @patch('text_processor.validate_font_file')
    def test_load_font_invalid_file(self, mock_validate):
        """Test font loading with invalid file."""
        mock_validate.return_value = False
        
        with self.assertRaises(FontLoadError):
            self.font_loader.load_font("invalid.txt")
    
    def test_get_character_outline_no_font(self):
        """Test character outline extraction without loaded font."""
        with self.assertRaises(TextProcessingError):
            self.font_loader.get_character_outline('A')
    
    def test_get_character_outline_multiple_chars(self):
        """Test character outline extraction with multiple characters."""
        self.font_loader._face = Mock()
        
        with self.assertRaises(TextProcessingError):
            self.font_loader.get_character_outline('AB')
    
    @patch('text_processor.freetype')
    def test_get_freetype_outline(self, mock_freetype):
        """Test freetype outline extraction."""
        # Setup mock face with outline data
        mock_face = Mock()
        mock_outline = Mock()
        mock_outline.contours = [3, 7]  # Two contours
        mock_outline.points = [
            (64, 128), (128, 128), (128, 64), (64, 64),  # First contour
            (192, 256), (256, 256), (256, 192), (192, 192)  # Second contour
        ]
        mock_face.glyph.outline = mock_outline
        self.font_loader._face = mock_face
        
        result = self.font_loader.get_character_outline('A')
        
        self.assertEqual(len(result), 2)  # Two contours
        self.assertEqual(len(result[0]), 4)  # First contour has 4 points
        self.assertEqual(len(result[1]), 4)  # Second contour has 4 points
        # Check coordinate conversion from 26.6 fractional points
        self.assertEqual(result[0][0], (1.0, 2.0))  # 64/64, 128/64
    
    def test_get_pil_outline(self):
        """Test PIL outline extraction (fallback)."""
        mock_font = Mock()
        mock_font.getbbox.return_value = (0, 0, 10, 20)
        self.font_loader.font = mock_font
        
        result = self.font_loader.get_character_outline('A')
        
        self.assertEqual(len(result), 1)  # One contour
        self.assertEqual(len(result[0]), 5)  # Rectangle with 5 points (closed)
        self.assertEqual(result[0][0], (0, 0))  # First point
        self.assertEqual(result[0][-1], (0, 0))  # Last point (closed)
    
    def test_get_font_metrics_no_font(self):
        """Test font metrics without loaded font."""
        with self.assertRaises(TextProcessingError):
            self.font_loader.get_font_metrics()
    
    def test_get_font_metrics_freetype(self):
        """Test font metrics with freetype."""
        mock_face = Mock()
        mock_face.ascender = 1024
        mock_face.descender = -256
        mock_face.height = 1280
        mock_face.max_advance_width = 1024
        mock_face.units_per_EM = 1000
        self.font_loader._face = mock_face
        self.font_loader.font_size = 24
        
        metrics = self.font_loader.get_font_metrics()
        
        self.assertEqual(metrics['font_size'], 24)
        self.assertEqual(metrics['ascender'], 16.0)  # 1024/64
        self.assertEqual(metrics['descender'], -4.0)  # -256/64
        self.assertEqual(metrics['height'], 20.0)  # 1280/64
    
    def test_get_font_metrics_pil(self):
        """Test font metrics with PIL."""
        mock_font = Mock()
        mock_font.getmetrics.return_value = (20, 5)
        self.font_loader.font = mock_font
        self.font_loader.font_size = 24
        
        metrics = self.font_loader.get_font_metrics()
        
        self.assertEqual(metrics['font_size'], 24)
        self.assertEqual(metrics['ascender'], 20)
        self.assertEqual(metrics['descender'], 5)
        self.assertEqual(metrics['height'], 25)


class TestTextProcessor(unittest.TestCase):
    """Test cases for TextProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_font_loader = Mock(spec=FontLoader)
        self.text_processor = TextProcessor(self.mock_font_loader)
    
    def test_init(self):
        """Test TextProcessor initialization."""
        processor = TextProcessor()
        self.assertIsNotNone(processor.font_loader)
        self.assertIsNotNone(processor.default_spacing)
    
    def test_parse_text_valid(self):
        """Test parsing valid text."""
        result = self.text_processor.parse_text("Hello World!")
        self.assertEqual(result, "Hello World!")
    
    def test_parse_text_empty(self):
        """Test parsing empty text."""
        with self.assertRaises(TextProcessingError):
            self.text_processor.parse_text("")
    
    def test_parse_text_non_string(self):
        """Test parsing non-string input."""
        with self.assertRaises(TextProcessingError):
            self.text_processor.parse_text(123)
    
    @patch('text_processor.normalize_text')
    def test_parse_text_normalization(self, mock_normalize):
        """Test text normalization during parsing."""
        mock_normalize.return_value = "normalized text"
        
        result = self.text_processor.parse_text("  raw text  ")
        
        mock_normalize.assert_called_once_with("  raw text  ")
        self.assertEqual(result, "normalized text")
    
    def test_validate_characters_valid(self):
        """Test character validation with valid characters."""
        result = self.text_processor._validate_characters("Hello World!")
        self.assertTrue(result)
    
    def test_validate_characters_with_spaces(self):
        """Test character validation with spaces."""
        result = self.text_processor._validate_characters("Hello World")
        self.assertTrue(result)
    
    def test_calculate_layout_simple(self):
        """Test layout calculation for simple text."""
        self.mock_font_loader.font = None
        self.mock_font_loader._face = None
        
        with patch.object(self.text_processor, '_get_character_width', return_value=10.0):
            layout = self.text_processor.calculate_layout("ABC")
        
        self.assertEqual(len(layout), 3)
        self.assertEqual(layout[0]['character'], 'A')
        self.assertEqual(layout[0]['position'], (0.0, 0.0))
        self.assertEqual(layout[1]['character'], 'B')
        self.assertEqual(layout[2]['character'], 'C')
    
    def test_calculate_layout_with_spaces(self):
        """Test layout calculation with spaces."""
        self.mock_font_loader.font = None
        self.mock_font_loader._face = None
        
        with patch.object(self.text_processor, '_get_character_width', return_value=10.0), \
             patch.object(self.text_processor, '_get_space_width', return_value=5.0):
            layout = self.text_processor.calculate_layout("A B")
        
        self.assertEqual(len(layout), 2)  # Spaces are not included in layout
        self.assertEqual(layout[0]['character'], 'A')
        self.assertEqual(layout[1]['character'], 'B')
    
    def test_calculate_layout_custom_spacing(self):
        """Test layout calculation with custom spacing."""
        self.mock_font_loader.font = None
        self.mock_font_loader._face = None
        
        with patch.object(self.text_processor, '_get_character_width', return_value=10.0):
            layout = self.text_processor.calculate_layout("AB", spacing=5.0)
        
        self.assertEqual(layout[0]['position'], (0.0, 0.0))
        self.assertEqual(layout[1]['position'], (15.0, 0.0))  # 10 + 5 spacing
    
    def test_get_character_width_no_font(self):
        """Test character width calculation without font."""
        self.mock_font_loader.font = None
        self.mock_font_loader._face = None
        
        with patch('text_processor.Config') as mock_config:
            mock_config.DEFAULT_CHARACTER_WIDTH = 8.0
            width = self.text_processor._get_character_width('A')
        
        self.assertEqual(width, 8.0)
    
    def test_get_character_width_freetype(self):
        """Test character width calculation with freetype."""
        mock_face = Mock()
        mock_glyph = Mock()
        mock_advance = Mock()
        mock_advance.x = 640  # 26.6 fractional points
        mock_glyph.advance = mock_advance
        mock_face.glyph = mock_glyph
        self.mock_font_loader._face = mock_face
        self.mock_font_loader.font = None
        
        width = self.text_processor._get_character_width('A')
        
        self.assertEqual(width, 10.0)  # 640/64
        mock_face.load_char.assert_called_once_with('A')
    
    def test_get_character_width_pil(self):
        """Test character width calculation with PIL."""
        mock_font = Mock()
        mock_font.getbbox.return_value = (0, 0, 12, 20)
        self.mock_font_loader.font = mock_font
        self.mock_font_loader._face = None
        
        width = self.text_processor._get_character_width('A')
        
        self.assertEqual(width, 12.0)  # bbox[2] - bbox[0]
    
    def test_get_space_width(self):
        """Test space width calculation."""
        with patch.object(self.text_processor, '_get_character_width', return_value=6.0) as mock_width:
            width = self.text_processor._get_space_width()
        
        mock_width.assert_called_once_with(' ')
        self.assertEqual(width, 6.0)
    
    def test_get_text_outlines(self):
        """Test getting outlines for text."""
        mock_outline = [[(0, 0), (10, 0), (10, 10), (0, 10)]]
        self.mock_font_loader.get_character_outline.return_value = mock_outline
        
        outlines = self.text_processor.get_text_outlines("AAB")
        
        self.assertEqual(len(outlines), 2)  # Unique characters A and B
        self.assertIn('A', outlines)
        self.assertIn('B', outlines)
        self.assertEqual(outlines['A'], mock_outline)
    
    def test_get_text_outlines_with_spaces(self):
        """Test getting outlines for text with spaces."""
        mock_outline = [[(0, 0), (10, 0), (10, 10), (0, 10)]]
        self.mock_font_loader.get_character_outline.return_value = mock_outline
        
        outlines = self.text_processor.get_text_outlines("A B")
        
        self.assertEqual(len(outlines), 2)  # A and B, space ignored
        self.assertIn('A', outlines)
        self.assertIn('B', outlines)
        self.assertNotIn(' ', outlines)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    @patch('text_processor.validate_file_path')
    def test_validate_font_file_valid_ttf(self, mock_validate_path):
        """Test font file validation with valid TTF file."""
        mock_validate_path.return_value = True
        
        result = validate_font_file("font.ttf")
        
        self.assertTrue(result)
        mock_validate_path.assert_called_once()
    
    @patch('text_processor.validate_file_path')
    def test_validate_font_file_valid_otf(self, mock_validate_path):
        """Test font file validation with valid OTF file."""
        mock_validate_path.return_value = True
        
        result = validate_font_file("font.otf")
        
        self.assertTrue(result)
    
    @patch('text_processor.validate_file_path')
    def test_validate_font_file_invalid_extension(self, mock_validate_path):
        """Test font file validation with invalid extension."""
        mock_validate_path.return_value = True
        
        result = validate_font_file("font.txt")
        
        self.assertFalse(result)
    
    @patch('text_processor.validate_file_path')
    def test_validate_font_file_invalid_path(self, mock_validate_path):
        """Test font file validation with invalid path."""
        mock_validate_path.return_value = False
        
        result = validate_font_file("nonexistent.ttf")
        
        self.assertFalse(result)
    
    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        result = normalize_text("  Hello World  ")
        self.assertEqual(result, "Hello World")
    
    def test_normalize_text_multiple_spaces(self):
        """Test normalization with multiple spaces."""
        result = normalize_text("Hello    World")
        self.assertEqual(result, "Hello World")
    
    def test_normalize_text_empty(self):
        """Test normalization with empty text."""
        result = normalize_text("")
        self.assertEqual(result, "")
    
    def test_normalize_text_none(self):
        """Test normalization with None input."""
        result = normalize_text(None)
        self.assertEqual(result, "")
    
    def test_normalize_text_mixed_whitespace(self):
        """Test normalization with mixed whitespace."""
        result = normalize_text("Hello\t\n  World")
        self.assertEqual(result, "Hello World")


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestFontLoader))
    test_suite.addTest(unittest.makeSuite(TestTextProcessor))
    test_suite.addTest(unittest.makeSuite(TestUtilityFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print coverage summary
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")