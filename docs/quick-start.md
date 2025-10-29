# Quick Start Guide

## 🚀 Getting Started with Rust PaddleOCR

This guide will help you get up and running with the Rust PaddleOCR library quickly.

## Prerequisites

- Rust 1.70+ installed
- PaddleOCR model files (detection and recognition models)
- Required system dependencies for image processing

## Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
rust-paddle-ocr = "1.4"
image = "0.25"
```

## Basic Usage

### 1. Initialize the OCR Engine

```rust
use rust_paddle_ocr::OcrEngineManager;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize with default configuration
    OcrEngineManager::initialize(
        "path/to/det_model.mnn",
        "path/to/rec_model.mnn",
        "path/to/keys.txt"
    )?;

    Ok(())
}
```

### 2. Process an Image

```rust
use rust_paddle_ocr::OcrEngineManager;
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize engine
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    // Load image
    let img = open("example.jpg")?;

    // Process OCR
    let texts = OcrEngineManager::process_ocr(img)?;

    // Print results
    for text in texts {
        println!("Found text: {}", text);
    }

    Ok(())
}
```

### 3. Advanced Configuration

```rust
use rust_paddle_ocr::OcrEngineManager;

// Initialize with custom settings
OcrEngineManager::initialize_with_config(
    "models/det_model.mnn",
    "models/rec_model.mnn",
    "models/keys.txt",
    15,    // rect_border_size
    true,  // merge_boxes
    2      // merge_threshold
)?;
```

## API Reference

### High-Level API (Recommended)

- `OcrEngineManager::initialize()` - Initialize global engine
- `OcrEngineManager::process_ocr()` - Complete OCR processing
- `OcrEngineManager::process_ocr_efficient()` - Optimized processing

### Low-Level API (Advanced)

- `Det::from_file()` - Create text detector
- `Rec::from_file()` - Create text recognizer
- `det.find_text_rect()` - Get text regions as rectangles
- `rec.predict_str()` - Recognize text in image

## Performance Tips

1. **Use efficient cropping** for better performance:
   ```rust
   let texts = OcrEngineManager::process_ocr_efficient(img)?;
   ```

2. **Reuse the engine** - initialize once, use many times

3. **Batch process** multiple images when possible

## Troubleshooting

### Common Issues

1. **"OCR engine not initialized"**
   - Make sure to call `initialize()` before processing

2. **Model loading errors**
   - Check file paths are correct
   - Ensure model files are compatible

3. **Memory issues**
   - Use `process_ocr_efficient()` for large images
   - Process images in batches
