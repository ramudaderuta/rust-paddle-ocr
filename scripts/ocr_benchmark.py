#!/usr/bin/env python3
"""
OCR Performance Benchmark Script

This script benchmarks OCR processing performance with various configurations
and image types. It measures processing time, memory usage, and accuracy metrics.

Usage:
    python ocr_benchmark.py --input-dir ./test_images --output benchmark_results.json
    python ocr_benchmark.py --image-list images.txt --workers 1,2,4,8
    python ocr_benchmark.py --config benchmark_config.json
"""

import argparse
import json
import os
import psutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
import statistics
import threading


@dataclass
class BenchmarkResult:
    """Single benchmark result."""
    image_path: str
    image_size: tuple  # (width, height)
    processing_time: float
    memory_usage_mb: float
    success: bool
    error_message: Optional[str] = None
    text_length: int = 0
    text_regions: int = 0


@dataclass
class BenchmarkSummary:
    """Summary of benchmark results."""
    total_images: int
    successful_images: int
    failed_images: int
    avg_processing_time: float
    min_processing_time: float
    max_processing_time: float
    avg_memory_usage: float
    total_processing_time: float
    images_per_second: float


class MemoryMonitor:
    """Monitor memory usage during processing."""

    def __init__(self):
        self.peak_memory = 0
        self.monitoring = False
        self.process = psutil.Process()

    def start_monitoring(self):
        """Start memory monitoring in a separate thread."""
        self.monitoring = True
        self.peak_memory = 0
        self.thread = threading.Thread(target=self._monitor)
        self.thread.daemon = True
        self.thread.start()

    def stop_monitoring(self):
        """Stop monitoring and return peak memory usage."""
        self.monitoring = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        return self.peak_memory

    def _monitor(self):
        """Monitor memory usage."""
        while self.monitoring:
            try:
                memory_mb = self.process.memory_info().rss / 1024 / 1024
                self.peak_memory = max(self.peak_memory, memory_mb)
                time.sleep(0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break


class OCRBenchmark:
    """OCR performance benchmark tool."""

    def __init__(self, ocr_binary: str = "ocr"):
        self.ocr_binary = ocr_binary

    def benchmark_single_image(self, image_path: Path) -> BenchmarkResult:
        """
        Benchmark a single image.

        Args:
            image_path: Path to the image file

        Returns:
            BenchmarkResult with performance metrics
        """
        # Get image size
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                image_size = img.size
        except ImportError:
            # Fallback to file size estimate
            image_size = (0, 0)

        # Start memory monitoring
        monitor = MemoryMonitor()
        monitor.start_monitoring()

        start_time = time.time()

        try:
            # Run OCR command
            cmd = [self.ocr_binary, "--path", str(image_path), "--mode", "json"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            processing_time = time.time() - start_time
            peak_memory = monitor.stop_monitoring()

            if result.returncode == 0:
                # Parse JSON output to get metrics
                try:
                    ocr_results = json.loads(result.stdout)
                    text_length = sum(len(item.get("text", "")) for item in ocr_results)
                    text_regions = len(ocr_results)
                except json.JSONDecodeError:
                    text_length = 0
                    text_regions = 0

                return BenchmarkResult(
                    image_path=str(image_path),
                    image_size=image_size,
                    processing_time=processing_time,
                    memory_usage_mb=peak_memory,
                    success=True,
                    text_length=text_length,
                    text_regions=text_regions
                )
            else:
                return BenchmarkResult(
                    image_path=str(image_path),
                    image_size=image_size,
                    processing_time=processing_time,
                    memory_usage_mb=peak_memory,
                    success=False,
                    error_message=result.stderr.strip()
                )

        except subprocess.TimeoutExpired:
            processing_time = time.time() - start_time
            peak_memory = monitor.stop_monitoring()
            return BenchmarkResult(
                image_path=str(image_path),
                image_size=image_size,
                processing_time=processing_time,
                memory_usage_mb=peak_memory,
                success=False,
                error_message="Processing timeout (60s)"
            )
        except Exception as e:
            processing_time = time.time() - start_time
            peak_memory = monitor.stop_monitoring()
            return BenchmarkResult(
                image_path=str(image_path),
                image_size=image_size,
                processing_time=processing_time,
                memory_usage_mb=peak_memory,
                success=False,
                error_message=str(e)
            )

    def benchmark_batch(self, image_paths: List[Path], workers: int = 1) -> List[BenchmarkResult]:
        """
        Benchmark multiple images with specified number of workers.

        Args:
            image_paths: List of image paths
            workers: Number of parallel workers

        Returns:
            List of benchmark results
        """
        results = []

        if workers == 1:
            # Sequential processing
            for image_path in image_paths:
                result = self.benchmark_single_image(image_path)
                results.append(result)
                print(f"✓ {image_path.name}" if result.success else f"✗ {image_path.name}")
        else:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_path = {
                    executor.submit(self.benchmark_single_image, path): path
                    for path in image_paths
                }

                for future in future_to_path:
                    result = future.result()
                    results.append(result)
                    path = future_to_path[future]
                    print(f"✓ {path.name}" if result.success else f"✗ {path.name}")

        return results

    def create_summary(self, results: List[BenchmarkResult]) -> BenchmarkSummary:
        """Create summary statistics from benchmark results."""
        successful_results = [r for r in results if r.success]

        if not successful_results:
            return BenchmarkSummary(
                total_images=len(results),
                successful_images=0,
                failed_images=len(results),
                avg_processing_time=0,
                min_processing_time=0,
                max_processing_time=0,
                avg_memory_usage=0,
                total_processing_time=0,
                images_per_second=0
            )

        processing_times = [r.processing_time for r in successful_results]
        memory_usage = [r.memory_usage_mb for r in successful_results]
        total_time = sum(processing_times)

        return BenchmarkSummary(
            total_images=len(results),
            successful_images=len(successful_results),
            failed_images=len(results) - len(successful_results),
            avg_processing_time=statistics.mean(processing_times),
            min_processing_time=min(processing_times),
            max_processing_time=max(processing_times),
            avg_memory_usage=statistics.mean(memory_usage),
            total_processing_time=total_time,
            images_per_second=len(successful_results) / total_time if total_time > 0 else 0
        )


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
    return image_paths


def main():
    parser = argparse.ArgumentParser(description="OCR performance benchmark")

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input-dir", type=Path,
                           help="Directory containing test images")
    input_group.add_argument("--image-list", type=Path,
                           help="Text file containing list of image paths")
    input_group.add_argument("--config", type=Path,
                           help="JSON configuration file for benchmark settings")

    # Output options
    parser.add_argument("--output", type=Path, required=True,
                       help="Output file for benchmark results")

    # Benchmark options
    parser.add_argument("--workers", type=str, default="1",
                       help="Comma-separated list of worker counts to test (default: 1)")
    parser.add_argument("--ocr-binary", default="ocr",
                       help="Path to OCR binary (default: ocr)")
    parser.add_argument("--repeat", type=int, default=1,
                       help="Number of times to repeat each test (default: 1)")

    args = parser.parse_args()

    # Handle config file
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)

        image_paths = [Path(p) for p in config.get("image_paths", [])]
        workers_list = config.get("workers", [1])
        repeat = config.get("repeat", 1)
    else:
        # Get image paths
        if args.input_dir:
            image_paths = find_image_files(args.input_dir)
        else:
            image_paths = load_image_list(args.image_list)

        workers_list = [int(w.strip()) for w in args.workers.split(",")]
        repeat = args.repeat

    if not image_paths:
        print("No images to benchmark.", file=sys.stderr)
        sys.exit(1)

    print(f"Benchmarking {len(image_paths)} images")
    print(f"Worker configurations: {workers_list}")
    print(f"Repeats per configuration: {repeat}")

    # Initialize benchmark tool
    benchmark = OCRBenchmark(ocr_binary=args.ocr_binary)

    # Run benchmarks
    all_results = {}

    for workers in workers_list:
        print(f"\n=== Testing with {workers} worker(s) ===")

        worker_results = []

        for repeat_num in range(repeat):
            if repeat > 1:
                print(f"\nRepeat {repeat_num + 1}/{repeat}")

            results = benchmark.benchmark_batch(image_paths, workers)
            worker_results.extend(results)

            # Show summary for this repeat
            summary = benchmark.create_summary(results)
            print(f"  Avg time: {summary.avg_processing_time:.3f}s")
            print(f"  Success rate: {summary.successful_images}/{summary.total_images}")

        all_results[str(workers)] = [asdict(r) for r in worker_results]

    # Create final summary
    final_results = {
        "metadata": {
            "total_images": len(image_paths),
            "worker_configurations": workers_list,
            "repeats_per_config": repeat,
            "timestamp": time.time()
        },
        "results": all_results
    }

    # Save results
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(final_results, f, indent=2)

    print(f"\nBenchmark results saved to: {args.output}")

    # Print summary table
    print("\n=== Performance Summary ===")
    print(f"{'Workers':<8} {'Avg Time (s)':<12} {'Min Time (s)':<12} {'Max Time (s)':<12} {'Images/s':<10} {'Success Rate':<12}")
    print("-" * 70)

    for workers in workers_list:
        results = [BenchmarkResult(**r) for r in all_results[str(workers)]]
        summary = benchmark.create_summary(results)
        success_rate = f"{summary.successful_images}/{summary.total_images}"

        print(f"{workers:<8} {summary.avg_processing_time:<12.3f} "
              f"{summary.min_processing_time:<12.3f} {summary.max_processing_time:<12.3f} "
              f"{summary.images_per_second:<10.2f} {success_rate:<12}")


if __name__ == "__main__":
    main()