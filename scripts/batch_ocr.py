#!/usr/bin/env python3
"""
Batch OCR Processing Script

This script processes multiple images with OCR using the Rust PaddleOCR library.
It supports parallel processing, progress tracking, and various output formats.

Usage:
    python batch_ocr.py --input-dir ./images --output-dir ./results
    python batch_ocr.py --image-list file_list.txt --output results.json
    python batch_ocr.py --input-dir ./images --format json --parallel 4
"""

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Optional
import time

class BatchOCRProcessor:
    """Batch OCR processor using Rust PaddleOCR CLI tool."""

    def __init__(self, ocr_binary: str = "ocr", parallel_workers: int = 4):
        self.ocr_binary = ocr_binary
        self.parallel_workers = parallel_workers

    def process_image(self, image_path: Path, output_format: str = "text") -> Dict[str, Any]:
        """
        Process a single image with OCR.

        Args:
            image_path: Path to the image file
            output_format: Output format ("text" or "json")

        Returns:
            Dictionary containing OCR results and metadata
        """
        start_time = time.time()

        try:
            # Build OCR command
            cmd = [self.ocr_binary, "--path", str(image_path)]

            if output_format == "json":
                cmd.extend(["--mode", "json"])

            # Run OCR command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout per image
            )

            processing_time = time.time() - start_time

            if result.returncode == 0:
                output = result.stdout.strip()

                # Parse JSON output if requested
                if output_format == "json":
                    try:
                        ocr_results = json.loads(output)
                    except json.JSONDecodeError:
                        ocr_results = []
                else:
                    # Split text output into lines
                    ocr_results = [line for line in output.split('\n') if line.strip()]

                return {
                    "success": True,
                    "image_path": str(image_path),
                    "processing_time": processing_time,
                    "results": ocr_results,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "image_path": str(image_path),
                    "processing_time": processing_time,
                    "results": [],
                    "error": result.stderr.strip()
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "image_path": str(image_path),
                "processing_time": time.time() - start_time,
                "results": [],
                "error": "Processing timeout (30s)"
            }
        except Exception as e:
            return {
                "success": False,
                "image_path": str(image_path),
                "processing_time": time.time() - start_time,
                "results": [],
                "error": str(e)
            }

    def process_batch(self, image_paths: List[Path], output_format: str = "text",
                     progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """
        Process multiple images in parallel.

        Args:
            image_paths: List of image file paths
            output_format: Output format ("text" or "json")
            progress_callback: Optional callback for progress updates

        Returns:
            List of processing results
        """
        results = []
        completed = 0

        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self.process_image, path, output_format): path
                for path in image_paths
            }

            # Collect results as they complete
            for future in as_completed(future_to_path):
                result = future.result()
                results.append(result)
                completed += 1

                if progress_callback:
                    progress_callback(completed, len(image_paths), result)

        return results

    def save_results(self, results: List[Dict[str, Any]], output_path: Path,
                    output_format: str = "json"):
        """
        Save processing results to file.

        Args:
            results: List of processing results
            output_path: Output file path
            output_format: Output format
        """
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                for result in results:
                    if result["success"]:
                        f.write(f"=== {result['image_path']} ===\n")
                        if isinstance(result["results"], list):
                            for text in result["results"]:
                                f.write(f"{text}\n")
                        else:
                            f.write(f"{result['results']}\n")
                        f.write("\n")
                    else:
                        f.write(f"=== ERROR: {result['image_path']} ===\n")
                        f.write(f"{result['error']}\n\n")


def find_image_files(directory: Path) -> List[Path]:
    """Find all image files in a directory."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    image_files = []

    for ext in image_extensions:
        image_files.extend(directory.rglob(f"*{ext}"))
        image_files.extend(directory.rglob(f"*{ext.upper()}"))

    return sorted(image_files)


def load_image_list(file_path: Path) -> List[Path]:
    """Load image paths from a text file."""
    image_paths = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                path = Path(line)
                if path.exists():
                    image_paths.append(path)
                else:
                    print(f"Warning: File not found: {path}", file=sys.stderr)

    return image_paths


def progress_callback(completed: int, total: int, result: Dict[str, Any]):
    """Print progress update."""
    status = "✓" if result["success"] else "✗"
    print(f"[{completed}/{total}] {status} {Path(result['image_path']).name}")


def main():
    parser = argparse.ArgumentParser(description="Batch OCR processing with Rust PaddleOCR")

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input-dir", type=Path,
                           help="Directory containing images to process")
    input_group.add_argument("--image-list", type=Path,
                           help="Text file containing list of image paths")

    # Output options
    parser.add_argument("--output", type=Path, required=True,
                       help="Output file path")
    parser.add_argument("--format", choices=["text", "json"], default="json",
                       help="Output format (default: json)")

    # Processing options
    parser.add_argument("--parallel", type=int, default=4,
                       help="Number of parallel workers (default: 4)")
    parser.add_argument("--ocr-binary", default="ocr",
                       help="Path to OCR binary (default: ocr)")

    args = parser.parse_args()

    # Get image paths
    if args.input_dir:
        if not args.input_dir.exists():
            print(f"Error: Input directory does not exist: {args.input_dir}", file=sys.stderr)
            sys.exit(1)
        image_paths = find_image_files(args.input_dir)
        print(f"Found {len(image_paths)} images in {args.input_dir}")
    else:
        if not args.image_list.exists():
            print(f"Error: Image list file does not exist: {args.image_list}", file=sys.stderr)
            sys.exit(1)
        image_paths = load_image_list(args.image_list)
        print(f"Loaded {len(image_paths)} images from {args.image_list}")

    if not image_paths:
        print("No images to process.", file=sys.stderr)
        sys.exit(1)

    # Initialize processor
    processor = BatchOCRProcessor(ocr_binary=args.ocr_binary,
                                parallel_workers=args.parallel)

    # Process images
    print(f"Processing {len(image_paths)} images with {args.parallel} workers...")
    start_time = time.time()

    results = processor.process_batch(
        image_paths,
        output_format=args.format,
        progress_callback=progress_callback
    )

    processing_time = time.time() - start_time

    # Print summary
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print(f"\nProcessing completed in {processing_time:.2f} seconds")
    print(f"Successful: {successful}, Failed: {failed}")

    if failed > 0:
        print("\nFailed images:")
        for result in results:
            if not result["success"]:
                print(f"  {result['image_path']}: {result['error']}")

    # Save results
    processor.save_results(results, args.output, args.format)
    print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()