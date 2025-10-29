#!/usr/bin/env python3
"""
Image Preprocessing for OCR

This script provides various image preprocessing techniques to improve OCR accuracy.
It includes noise reduction, contrast enhancement, skew correction, and more.

Usage:
    python image_preprocessor.py --input image.jpg --output processed.jpg
    python image_preprocessor.py --input-dir ./images --output-dir ./processed
    python image_preprocessor.py --config preprocess_config.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Image preprocessing utilities for OCR."""

    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}

    def load_image(self, image_path: Path) -> np.ndarray:
        """Load image from file."""
        try:
            # Use PIL for better format support
            pil_image = Image.open(image_path)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            raise

    def save_image(self, image: np.ndarray, output_path: Path):
        """Save image to file."""
        try:
            # Convert BGR to RGB for PIL
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            pil_image.save(output_path, quality=95)
        except Exception as e:
            logger.error(f"Error saving image to {output_path}: {e}")
            raise

    def resize_image(self, image: np.ndarray, max_width: int = 2000,
                    max_height: int = 2000) -> np.ndarray:
        """Resize image while maintaining aspect ratio."""
        height, width = image.shape[:2]

        if width <= max_width and height <= max_height:
            return image

        # Calculate scaling factor
        scale = min(max_width / width, max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    def denoise(self, image: np.ndarray, method: str = "bilateral") -> np.ndarray:
        """Apply noise reduction."""
        if method == "bilateral":
            return cv2.bilateralFilter(image, 9, 75, 75)
        elif method == "gaussian":
            return cv2.GaussianBlur(image, (5, 5), 0)
        elif method == "median":
            return cv2.medianBlur(image, 5)
        else:
            logger.warning(f"Unknown denoising method: {method}")
            return image

    def enhance_contrast(self, image: np.ndarray, method: str = "clahe") -> np.ndarray:
        """Enhance image contrast."""
        if method == "clahe":
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)

            # Merge channels and convert back
            lab = cv2.merge([l, a, b])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        elif method == "histogram_eq":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            equalized = cv2.equalizeHist(gray)
            return cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
        else:
            logger.warning(f"Unknown contrast enhancement method: {method}")
            return image

    def binarize(self, image: np.ndarray, method: str = "adaptive") -> np.ndarray:
        """Convert image to binary (black and white)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if method == "adaptive":
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        elif method == "otsu":
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == "simple":
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        else:
            logger.warning(f"Unknown binarization method: {method}")
            return image

        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    def deskew(self, image: np.ndarray) -> np.ndarray:
        """Correct image skew."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Detect lines
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

        if lines is None:
            logger.warning("No lines detected for deskewing")
            return image

        # Calculate angles
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            angles.append(angle)

        if not angles:
            return image

        # Use median angle
        median_angle = np.median(angles)

        # Rotate image
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)

        return cv2.warpAffine(image, rotation_matrix, (width, height),
                            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    def remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """Remove shadows from image."""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # Apply morphological operations to detect shadows
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        shadow = cv2.morphologyEx(l, cv2.MORPH_CLOSE, kernel)
        shadow = cv2.GaussianBlur(shadow, (21, 21), 0)

        # Remove shadows
        l = cv2.divide(l, shadow, scale=255.0)

        # Merge channels and convert back
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def sharpen(self, image: np.ndarray) -> np.ndarray:
        """Apply sharpening filter."""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)

    def process_image(self, image: np.ndarray, config: Dict) -> np.ndarray:
        """
        Apply preprocessing steps based on configuration.

        Args:
            image: Input image as numpy array
            config: Preprocessing configuration dictionary

        Returns:
            Processed image
        """
        processed = image.copy()

        # Resize if specified
        if "resize" in config:
            resize_config = config["resize"]
            processed = self.resize_image(
                processed,
                max_width=resize_config.get("max_width", 2000),
                max_height=resize_config.get("max_height", 2000)
            )

        # Denoise if specified
        if "denoise" in config:
            denoise_config = config["denoise"]
            processed = self.denoise(processed, method=denoise_config.get("method", "bilateral"))

        # Remove shadows if specified
        if config.get("remove_shadows", False):
            processed = self.remove_shadows(processed)

        # Enhance contrast if specified
        if "enhance_contrast" in config:
            contrast_config = config["enhance_contrast"]
            processed = self.enhance_contrast(
                processed,
                method=contrast_config.get("method", "clahe")
            )

        # Sharpen if specified
        if config.get("sharpen", False):
            processed = self.sharpen(processed)

        # Binarize if specified
        if "binarize" in config:
            binarize_config = config["binarize"]
            processed = self.binarize(processed, method=binarize_config.get("method", "adaptive"))

        # Deskew if specified
        if config.get("deskew", False):
            processed = self.deskew(processed)

        return processed

    def get_default_config(self) -> Dict:
        """Get default preprocessing configuration."""
        return {
            "resize": {
                "max_width": 2000,
                "max_height": 2000
            },
            "denoise": {
                "method": "bilateral"
            },
            "remove_shadows": True,
            "enhance_contrast": {
                "method": "clahe"
            },
            "sharpen": True,
            "deskew": False,
            "binarize": {
                "method": "adaptive"
            }
        }

    def get_aggressive_config(self) -> Dict:
        """Get aggressive preprocessing configuration for low-quality images."""
        return {
            "resize": {
                "max_width": 3000,
                "max_height": 3000
            },
            "denoise": {
                "method": "bilateral"
            },
            "remove_shadows": True,
            "enhance_contrast": {
                "method": "clahe"
            },
            "sharpen": True,
            "deskew": True,
            "binarize": {
                "method": "adaptive"
            }
        }

    def get_light_config(self) -> Dict:
        """Get light preprocessing configuration for high-quality images."""
        return {
            "resize": {
                "max_width": 2000,
                "max_height": 2000
            },
            "enhance_contrast": {
                "method": "clahe"
            }
        }


def find_image_files(directory: Path) -> List[Path]:
    """Find all image files in a directory."""
    image_files = []
    for ext in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}:
        image_files.extend(directory.rglob(f"*{ext}"))
        image_files.extend(directory.rglob(f"*{ext.upper()}"))
    return sorted(image_files)


def load_config(config_path: Path) -> Dict:
    """Load preprocessing configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        sys.exit(1)


def save_config(config: Dict, config_path: Path):
    """Save preprocessing configuration to JSON file."""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Image preprocessing for OCR")

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", type=Path,
                           help="Single input image file")
    input_group.add_argument("--input-dir", type=Path,
                           help="Directory containing images to process")

    # Output options
    parser.add_argument("--output", type=Path,
                       help="Output file (for single image)")
    parser.add_argument("--output-dir", type=Path,
                       help="Output directory (for batch processing)")

    # Configuration options
    parser.add_argument("--config", type=Path,
                       help="JSON configuration file")
    parser.add_argument("--preset", choices=["default", "aggressive", "light"],
                       default="default", help="Preprocessing preset")
    parser.add_argument("--save-config", type=Path,
                       help="Save current configuration to file")

    args = parser.parse_args()

    # Initialize preprocessor
    preprocessor = ImagePreprocessor()

    # Load configuration
    if args.config:
        config = load_config(args.config)
    else:
        if args.preset == "default":
            config = preprocessor.get_default_config()
        elif args.preset == "aggressive":
            config = preprocessor.get_aggressive_config()
        elif args.preset == "light":
            config = preprocessor.get_light_config()

    # Save configuration if requested
    if args.save_config:
        save_config(config, args.save_config)

    # Process single image
    if args.input:
        if not args.output:
            logger.error("--output is required when processing single image")
            sys.exit(1)

        if not args.input.exists():
            logger.error(f"Input file not found: {args.input}")
            sys.exit(1)

        logger.info(f"Processing {args.input}...")
        image = preprocessor.load_image(args.input)
        processed = preprocessor.process_image(image, config)
        preprocessor.save_image(processed, args.output)
        logger.info(f"Saved processed image to {args.output}")

    # Process batch
    else:
        if not args.output_dir:
            logger.error("--output-dir is required when processing directory")
            sys.exit(1)

        if not args.input_dir.exists():
            logger.error(f"Input directory not found: {args.input_dir}")
            sys.exit(1)

        args.output_dir.mkdir(parents=True, exist_ok=True)
        image_files = find_image_files(args.input_dir)

        if not image_files:
            logger.warning(f"No image files found in {args.input_dir}")
            sys.exit(0)

        logger.info(f"Found {len(image_files)} images to process")

        for i, image_path in enumerate(image_files, 1):
            logger.info(f"[{i}/{len(image_files)}] Processing {image_path.name}...")

            try:
                image = preprocessor.load_image(image_path)
                processed = preprocessor.process_image(image, config)

                output_path = args.output_dir / image_path.name
                preprocessor.save_image(processed, output_path)

            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                continue

        logger.info(f"Batch processing completed. Results saved to {args.output_dir}")


if __name__ == "__main__":
    main()