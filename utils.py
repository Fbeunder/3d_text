"""
Utility functions for 3D Text Generator

Contains helper functions for file operations, validation,
and common utility tasks used throughout the application.
"""

import os
import logging
import hashlib
import json
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
from datetime import datetime


def validate_file_path(path: Union[str, Path]) -> bool:
    """
    Validate if a file path exists and is accessible.
    
    Args:
        path: Path to validate
        
    Returns:
        bool: True if path is valid and accessible
    """
    try:
        path = Path(path)
        return path.exists() and path.is_file()
    except (OSError, ValueError):
        return False


def validate_directory_path(path: Union[str, Path]) -> bool:
    """
    Validate if a directory path exists and is accessible.
    
    Args:
        path: Directory path to validate
        
    Returns:
        bool: True if directory is valid and accessible
    """
    try:
        path = Path(path)
        return path.exists() and path.is_dir()
    except (OSError, ValueError):
        return False


def ensure_directory_exists(path: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        logging.error(f"Failed to create directory {path}: {e}")
        return False


def get_file_extension(path: Union[str, Path]) -> str:
    """
    Get the file extension from a path.
    
    Args:
        path: File path
        
    Returns:
        str: File extension (lowercase, including dot)
    """
    return Path(path).suffix.lower()


def get_file_size(path: Union[str, Path]) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        path: File path
        
    Returns:
        int: File size in bytes, -1 if file doesn't exist
    """
    try:
        return Path(path).stat().st_size
    except (OSError, FileNotFoundError):
        return -1


def get_file_hash(path: Union[str, Path], algorithm: str = 'md5') -> Optional[str]:
    """
    Calculate hash of a file.
    
    Args:
        path: File path
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
        
    Returns:
        str: File hash, None if file doesn't exist or error occurs
    """
    try:
        hash_obj = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except (OSError, FileNotFoundError, ValueError):
        return None


def safe_filename(filename: str, replacement: str = '_') -> str:
    """
    Create a safe filename by replacing invalid characters.
    
    Args:
        filename: Original filename
        replacement: Character to replace invalid characters with
        
    Returns:
        str: Safe filename
    """
    # Characters that are invalid in filenames on most systems
    invalid_chars = '<>:"/\\|?*'
    
    safe_name = filename
    for char in invalid_chars:
        safe_name = safe_name.replace(char, replacement)
    
    # Remove leading/trailing dots and spaces
    safe_name = safe_name.strip('. ')
    
    # Ensure filename is not empty
    if not safe_name:
        safe_name = f"unnamed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return safe_name


def get_unique_filename(directory: Union[str, Path], base_name: str, extension: str = '') -> Path:
    """
    Generate a unique filename in a directory.
    
    Args:
        directory: Target directory
        base_name: Base filename (without extension)
        extension: File extension (with or without leading dot)
        
    Returns:
        Path: Unique file path
    """
    directory = Path(directory)
    
    # Ensure extension starts with dot
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    
    # Start with base name
    counter = 0
    while True:
        if counter == 0:
            filename = f"{base_name}{extension}"
        else:
            filename = f"{base_name}_{counter}{extension}"
        
        file_path = directory / filename
        if not file_path.exists():
            return file_path
        
        counter += 1
        
        # Prevent infinite loop
        if counter > 9999:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{base_name}_{timestamp}{extension}"
            return directory / filename


def read_text_file(path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """
    Read text content from a file.
    
    Args:
        path: File path
        encoding: Text encoding
        
    Returns:
        str: File content, None if error occurs
    """
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except (OSError, FileNotFoundError, UnicodeDecodeError) as e:
        logging.error(f"Failed to read file {path}: {e}")
        return None


def write_text_file(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """
    Write text content to a file.
    
    Args:
        path: File path
        content: Text content to write
        encoding: Text encoding
        
    Returns:
        bool: True if successful
    """
    try:
        path = Path(path)
        ensure_directory_exists(path.parent)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except (OSError, PermissionError) as e:
        logging.error(f"Failed to write file {path}: {e}")
        return False


def read_json_file(path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Read JSON data from a file.
    
    Args:
        path: File path
        
    Returns:
        dict: JSON data, None if error occurs
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Failed to read JSON file {path}: {e}")
        return None


def write_json_file(path: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> bool:
    """
    Write JSON data to a file.
    
    Args:
        path: File path
        data: Data to write
        indent: JSON indentation
        
    Returns:
        bool: True if successful
    """
    try:
        path = Path(path)
        ensure_directory_exists(path.parent)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except (OSError, PermissionError, TypeError) as e:
        logging.error(f"Failed to write JSON file {path}: {e}")
        return False


def list_files_by_extension(directory: Union[str, Path], extensions: List[str]) -> List[Path]:
    """
    List files in a directory with specific extensions.
    
    Args:
        directory: Directory to search
        extensions: List of extensions (with or without leading dot)
        
    Returns:
        List[Path]: List of matching file paths
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        return []
    
    # Normalize extensions
    normalized_extensions = []
    for ext in extensions:
        if not ext.startswith('.'):
            ext = '.' + ext
        normalized_extensions.append(ext.lower())
    
    matching_files = []
    try:
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in normalized_extensions:
                matching_files.append(file_path)
    except (OSError, PermissionError):
        pass
    
    return sorted(matching_files)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes < 0:
        return "Unknown"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_value: Minimum bound
        max_value: Maximum bound
        
    Returns:
        float: Clamped value
    """
    return max(min_value, min(value, max_value))


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values.
    
    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        float: Interpolated value
    """
    return a + (b - a) * clamp(t, 0.0, 1.0)


def setup_logging(log_level: str = 'INFO', log_file: Optional[Path] = None) -> None:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Setup file handler if specified
    if log_file:
        ensure_directory_exists(log_file.parent)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_timestamp(format_string: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Get current timestamp as formatted string.
    
    Args:
        format_string: strftime format string
        
    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime(format_string)


def measure_time(func):
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to measure
        
    Returns:
        Decorated function
    """
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logging.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper


# Validation functions for specific data types
def is_valid_number(value: Any, min_value: float = None, max_value: float = None) -> bool:
    """
    Validate if a value is a valid number within optional bounds.
    
    Args:
        value: Value to validate
        min_value: Optional minimum bound
        max_value: Optional maximum bound
        
    Returns:
        bool: True if valid number
    """
    try:
        num = float(value)
        if min_value is not None and num < min_value:
            return False
        if max_value is not None and num > max_value:
            return False
        return True
    except (ValueError, TypeError):
        return False


def is_valid_string(value: Any, min_length: int = 0, max_length: int = None) -> bool:
    """
    Validate if a value is a valid string within optional length bounds.
    
    Args:
        value: Value to validate
        min_length: Minimum string length
        max_length: Optional maximum string length
        
    Returns:
        bool: True if valid string
    """
    if not isinstance(value, str):
        return False
    
    length = len(value)
    if length < min_length:
        return False
    if max_length is not None and length > max_length:
        return False
    
    return True


if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")
    
    # Test file operations
    test_dir = Path("test_utils")
    ensure_directory_exists(test_dir)
    
    test_file = test_dir / "test.txt"
    write_text_file(test_file, "Hello, World!")
    
    content = read_text_file(test_file)
    print(f"File content: {content}")
    
    file_size = get_file_size(test_file)
    print(f"File size: {format_file_size(file_size)}")
    
    # Cleanup
    test_file.unlink()
    test_dir.rmdir()
    
    print("Utility functions test completed.")