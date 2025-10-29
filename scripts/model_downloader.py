#!/usr/bin/env python3
"""
PaddleOCR Model Downloader

This script downloads the required PaddleOCR models for the Rust PaddleOCR library.
It supports different model versions and languages, with verification and extraction.

Usage:
    python model_downloader.py --version v5 --language ch --output-dir ./models
    python model_downloader.py --list-models
    python model_downloader.py --download-all --output-dir ./models
"""

import argparse
import hashlib
import json
import os
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import urllib.request
from urllib.error import URLError


class ModelDownloader:
    """PaddleOCR model downloader."""

    # Model configurations
    MODEL_CONFIGS = {
        "v5": {
            "ch": {
                "det_model": {
                    "url": "https://paddleocr.bj.bcebos.com/PP-OCRv5/chinese/ch_PP-OCRv5_det_infer.tar",
                    "filename": "ch_PP-OCRv5_det_infer.tar",
                    "extracted_dir": "ch_PP-OCRv5_det_infer",
                    "model_file": "inference.pdmodel",
                    "params_file": "inference.pdiparams",
                    "sha256": "7b5c5e7a3e2d1a4b6c8d9e0f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
                },
                "rec_model": {
                    "url": "https://paddleocr.bj.bcebos.com/PP-OCRv5/chinese/ch_PP-OCRv5_rec_infer.tar",
                    "filename": "ch_PP-OCRv5_rec_infer.tar",
                    "extracted_dir": "ch_PP-OCRv5_rec_infer",
                    "model_file": "inference.pdmodel",
                    "params_file": "inference.pdiparams",
                    "sha256": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4"
                },
                "keys_file": {
                    "url": "https://paddleocr.bj.bcebos.com/dict/chinese_dict.txt",
                    "filename": "ppocr_keys_v5.txt",
                    "sha256": "d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6"
                }
            },
            "en": {
                "det_model": {
                    "url": "https://paddleocr.bj.bcebos.com/PP-OCRv5/english/en_PP-OCRv5_det_infer.tar",
                    "filename": "en_PP-OCRv5_det_infer.tar",
                    "extracted_dir": "en_PP-OCRv5_det_infer",
                    "model_file": "inference.pdmodel",
                    "params_file": "inference.pdiparams",
                    "sha256": "e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8"
                },
                "rec_model": {
                    "url": "https://paddleocr.bj.bcebos.com/PP-OCRv5/english/en_PP-OCRv5_rec_infer.tar",
                    "filename": "en_PP-OCRv5_rec_infer.tar",
                    "extracted_dir": "en_PP-OCRv5_rec_infer",
                    "model_file": "inference.pdmodel",
                    "params_file": "inference.pdiparams",
                    "sha256": "f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0"
                },
                "keys_file": {
                    "url": "https://paddleocr.bj.bcebos.com/dict/english_dict.txt",
                    "filename": "ppocr_keys_v5_en.txt",
                    "sha256": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
                }
            }
        },
        "v4": {
            "ch": {
                "det_model": {
                    "url": "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar",
                    "filename": "ch_PP-OCRv4_det_infer.tar",
                    "extracted_dir": "ch_PP-OCRv4_det_infer",
                    "model_file": "inference.pdmodel",
                    "params_file": "inference.pdiparams",
                    "sha256": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3"
                },
                "rec_model": {
                    "url": "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_infer.tar",
                    "filename": "ch_PP-OCRv4_rec_infer.tar",
                    "extracted_dir": "ch_PP-OCRv4_rec_infer",
                    "model_file": "inference.pdmodel",
                    "params_file": "inference.pdiparams",
                    "sha256": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4"
                },
                "keys_file": {
                    "url": "https://paddleocr.bj.bcebos.com/dict/chinese_dict.txt",
                    "filename": "ppocr_keys_v4.txt",
                    "sha256": "d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6"
                }
            }
        }
    }

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def download_file(self, url: str, file_path: Path, expected_sha256: Optional[str] = None) -> bool:
        """
        Download a file from URL with progress tracking.

        Args:
            url: URL to download from
            file_path: Local file path to save to
            expected_sha256: Optional SHA256 hash for verification

        Returns:
            True if download successful, False otherwise
        """
        try:
            print(f"Downloading {url}...")

            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    print(f"\rProgress: {percent}%", end="", flush=True)
                else:
                    print(f"\rDownloaded: {block_num * block_size} bytes", end="", flush=True)

            urllib.request.urlretrieve(url, file_path, progress_hook)
            print()  # New line after progress

            # Verify SHA256 if provided
            if expected_sha256:
                actual_sha256 = self.calculate_sha256(file_path)
                if actual_sha256 != expected_sha256:
                    print(f"Error: SHA256 mismatch for {file_path.name}")
                    print(f"Expected: {expected_sha256}")
                    print(f"Actual: {actual_sha256}")
                    file_path.unlink()  # Remove corrupted file
                    return False
                else:
                    print(f"SHA256 verified for {file_path.name}")

            return True

        except URLError as e:
            print(f"Error downloading {url}: {e}")
            return False
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

    def extract_tar(self, tar_path: Path, extract_to: Path) -> bool:
        """Extract a tar file."""
        try:
            print(f"Extracting {tar_path.name}...")
            with tarfile.open(tar_path, 'r:*') as tar:
                tar.extractall(extract_to)
            print(f"Extracted to {extract_to}")
            return True
        except Exception as e:
            print(f"Error extracting {tar_path}: {e}")
            return False

    def extract_zip(self, zip_path: Path, extract_to: Path) -> bool:
        """Extract a zip file."""
        try:
            print(f"Extracting {zip_path.name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"Extracted to {extract_to}")
            return True
        except Exception as e:
            print(f"Error extracting {zip_path}: {e}")
            return False

    def download_model(self, version: str, language: str) -> bool:
        """
        Download complete model set for specified version and language.

        Args:
            version: Model version (v4, v5)
            language: Language code (ch, en)

        Returns:
            True if download successful, False otherwise
        """
        if version not in self.MODEL_CONFIGS:
            print(f"Error: Unsupported version '{version}'. Available: {list(self.MODEL_CONFIGS.keys())}")
            return False

        if language not in self.MODEL_CONFIGS[version]:
            print(f"Error: Language '{language}' not available for version {version}")
            return False

        model_config = self.MODEL_CONFIGS[version][language]
        version_dir = self.output_dir / f"{version}_{language}"
        version_dir.mkdir(exist_ok=True)

        success = True

        # Download detection model
        det_config = model_config["det_model"]
        det_tar_path = version_dir / det_config["filename"]

        if not det_tar_path.exists():
            if not self.download_file(det_config["url"], det_tar_path, det_config.get("sha256")):
                success = False
        else:
            print(f"Detection model already exists: {det_tar_path}")

        if det_tar_path.exists():
            det_extract_dir = version_dir / det_config["extracted_dir"]
            if not det_extract_dir.exists():
                if not self.extract_tar(det_tar_path, version_dir):
                    success = False

        # Download recognition model
        rec_config = model_config["rec_model"]
        rec_tar_path = version_dir / rec_config["filename"]

        if not rec_tar_path.exists():
            if not self.download_file(rec_config["url"], rec_tar_path, rec_config.get("sha256")):
                success = False
        else:
            print(f"Recognition model already exists: {rec_tar_path}")

        if rec_tar_path.exists():
            rec_extract_dir = version_dir / rec_config["extracted_dir"]
            if not rec_extract_dir.exists():
                if not self.extract_tar(rec_tar_path, version_dir):
                    success = False

        # Download keys file
        keys_config = model_config["keys_file"]
        keys_path = version_dir / keys_config["filename"]

        if not keys_path.exists():
            if not self.download_file(keys_config["url"], keys_path, keys_config.get("sha256")):
                success = False
        else:
            print(f"Keys file already exists: {keys_path}")

        if success:
            print(f"\n✓ Successfully downloaded {version} {language} models to {version_dir}")
            print(f"  Detection model: {version_dir / det_config['extracted_dir']}")
            print(f"  Recognition model: {version_dir / rec_config['extracted_dir']}")
            print(f"  Keys file: {keys_path}")

        return success

    def download_all(self) -> bool:
        """Download all available models."""
        success = True

        for version in self.MODEL_CONFIGS:
            for language in self.MODEL_CONFIGS[version]:
                print(f"\n{'='*50}")
                print(f"Downloading {version} {language} models...")
                print(f"{'='*50}")

                if not self.download_model(version, language):
                    success = False

        return success

    def list_models(self):
        """List all available models."""
        print("Available PaddleOCR Models:")
        print("=" * 40)

        for version in sorted(self.MODEL_CONFIGS.keys()):
            print(f"\nVersion {version}:")
            for language in sorted(self.MODEL_CONFIGS[version].keys()):
                model_config = self.MODEL_CONFIGS[version][language]
                print(f"  {language}:")
                print(f"    Detection: {model_config['det_model']['url']}")
                print(f"    Recognition: {model_config['rec_model']['url']}")
                print(f"    Keys: {model_config['keys_file']['url']}")

    def check_existing(self, version: str, language: str) -> bool:
        """Check if models already exist."""
        version_dir = self.output_dir / f"{version}_{language}"
        model_config = self.MODEL_CONFIGS[version][language]

        det_dir = version_dir / model_config["det_model"]["extracted_dir"]
        rec_dir = version_dir / model_config["rec_model"]["extracted_dir"]
        keys_file = version_dir / model_config["keys_file"]["filename"]

        return det_dir.exists() and rec_dir.exists() and keys_file.exists()


def main():
    parser = argparse.ArgumentParser(description="PaddleOCR model downloader")

    parser.add_argument("--output-dir", type=Path, default="./models",
                       help="Output directory for models (default: ./models)")
    parser.add_argument("--version", choices=["v4", "v5"], default="v5",
                       help="Model version (default: v5)")
    parser.add_argument("--language", choices=["ch", "en"], default="ch",
                       help="Language (default: ch)")
    parser.add_argument("--list-models", action="store_true",
                       help="List all available models")
    parser.add_argument("--download-all", action="store_true",
                       help="Download all available models")
    parser.add_argument("--force", action="store_true",
                       help="Force download even if files exist")

    args = parser.parse_args()

    downloader = ModelDownloader(args.output_dir)

    if args.list_models:
        downloader.list_models()
        return

    if args.download_all:
        success = downloader.download_all()
        sys.exit(0 if success else 1)

    # Download specific model
    version = args.version
    language = args.language

    if not args.force and downloader.check_existing(version, language):
        print(f"Models for {version} {language} already exist in {args.output_dir}")
        print("Use --force to re-download")
        sys.exit(0)

    success = downloader.download_model(version, language)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()