---
name: rust-paddle-ocr-integration
description: This skill provides comprehensive guidance for integrating the Rust PaddleOCR library into applications. Use this skill when users need to add OCR functionality to Rust projects, including web servers, desktop applications, CLI tools, or embedded systems. The skill covers integration patterns, performance optimization, troubleshooting common issues, and best practices for production deployment.
---

# Rust PaddleOCR Integration

## Overview

This skill enables developers to efficiently integrate OCR (Optical Character Recognition) capabilities into Rust applications using the PaddleOCR library. It provides proven patterns for different application types, performance optimization strategies, and solutions to common integration challenges.

## Folder Structure
```
rust-paddle-ocr/
├── SKILL.md                    # Main skill documentation file
├── Cargo.toml                  # Rust package manifest file
├── Cargo.lock                  # Dependency lock file
├── build.rs                    # Build script for C API header generation
├── CLAUDE.md                   # Project-specific instructions for Claude Code
├── README.md                   # Project overview and usage instructions
├── LICENSE                     # License information file
├── rocr.h                      # Auto-generated C API header file
├── add_path.sh                 # Bash script for development environment setup
├── convert_paddle_to_mnn.py    # Python script for model conversion
├── test_ffi.py                 # Python script for testing C API with ctypes
├── src/                        # Rust source code directory
│   ├── lib.rs                  # Library entry point and public API exports
│   ├── main.rs                 # Command-line interface implementation
│   ├── engine.rs               # Thread-safe OCR engine with actor pattern
│   ├── det.rs                  # Text detection model implementation
│   ├── rec.rs                  # Text recognition model implementation
│   ├── efficient_cropping.rs   # Smart image cropping utilities
│   ├── error.rs                # Error types and handling definitions
│   └── capi.rs                 # C-compatible API interface
├── models/                     # Pre-trained OCR models and character sets
│   ├── PP-OCRv5_mobile_det_fp16.mnn  # Text detection model (FP16)
│   ├── PP-OCRv5_mobile_rec_fp16.mnn  # Text recognition model (FP16)
│   └── ppocr_keys_v5.txt       # Character set definitions
├── examples/                   # Example applications demonstrating usage
│   ├── simple.rs               # Basic OCR usage example
│   ├── multi_thread.rs         # Multi-threaded processing example
│   └── cropping_benchmark.rs   # Performance benchmark for cropping
├── benches/                    # Performance benchmark suite
│   └── bench_metrics.rs        # Benchmark implementation
├── references/                 # Comprehensive documentation
│   ├── quick-start.md          # Getting started guide
│   ├── api-reference.md        # Detailed API documentation
│   ├── architecture.md         # System architecture overview
│   ├── code-explanation.md     # Implementation details
│   ├── examples.md             # Extended examples documentation
│   ├── interactive-examples.md # Interactive code examples
│   ├── performance.md          # Performance optimization guide
│   └── troubleshooting.md      # Common issues and solutions
├── res/                        # Sample images for testing
├── demo/                       # Demo applications
│   ├── c_demo.c                # C API usage demonstration
│   └── python_demo.py          # Python integration example
└── scripts/                    # Utility scripts
    └── (currently empty)
```

## Integration Decision Tree

**First, determine your application type:**

1. **Web Server/API** - Need to process user-uploaded images
2. **Desktop Application** - Building GUI apps for document processing
3. **CLI Tool** - Creating command-line utilities for batch processing
4. **Embedded System** - Integrating OCR into resource-constrained environments

**Then, identify your OCR requirements:**

- **Single Image Processing** - Process one image at a time
- **Batch Processing** - Handle multiple images efficiently
- **Real-time Processing** - Low-latency OCR requirements
- **High Accuracy** - Focus on recognition quality over speed

## 1. Web Server Integration

### Basic Web API Setup

Use the `examples/simple.rs` as a starting point for web integration:

```rust
use rust_paddle_ocr::{OcrEngineManager};
use axum::{extract::Multipart, http::StatusCode, response::Json};
use serde_json::json;

// Initialize OCR engine at startup
OcrEngineManager::initialize_with_config(
    "./models/det_model.mnn",
    "./models/rec_model.mnn",
    "./models/keys.txt",
    12,  // thread count
    false,
    1,
)?;

// OCR endpoint
async fn ocr_endpoint(mut multipart: Multipart) -> Result<Json<serde_json::Value>, StatusCode> {
    while let Some(field) = multipart.next_field().await.unwrap() {
        let bytes = field.bytes().await.unwrap();
        let img = image::load_from_memory(&bytes).map_err(|_| StatusCode::BAD_REQUEST)?;

        match OcrEngineManager::process_ocr(img) {
            Ok(texts) => return Ok(Json(json!({"texts": texts}))),
            Err(_) => return Err(StatusCode::INTERNAL_SERVER_ERROR),
        }
    }
    Err(StatusCode::BAD_REQUEST)
}
```

### Performance Considerations

- **Model Loading**: Initialize once at application startup
- **Thread Pool**: Use `OcrEngineManager::initialize_with_config()` with appropriate thread count
- **Memory Management**: Consider image size limits and cleanup strategies
- **Error Handling**: Implement proper error responses for invalid images

## 2. Desktop Application Integration

### Tauri Integration Pattern

For cross-platform desktop apps, use the C API:

```rust
// In your Rust backend
use rust_paddle_ocr::capi::*;
use std::os::raw::c_char;

#[tauri::command]
async fn process_image_ocr(image_path: String) -> Result<Vec<String>, String> {
    let mut texts = Vec::new();
    let result = unsafe {
        ocr_process_image(
            image_path.as_ptr() as *const c_char,
            texts.as_mut_ptr(),
            texts.len() as i32
        )
    };

    if result == 0 {
        Ok(texts)
    } else {
        Err("OCR processing failed".to_string())
    }
}
```

### GUI Integration Tips

- **Progress Indicators**: OCR can take time, show progress to users
- **Image Preprocessing**: Allow users to adjust image parameters
- **Result Display**: Highlight detected text regions on the original image
- **Batch Processing**: Enable processing multiple documents in sequence

## 3. CLI Tool Integration

### Basic CLI Structure

Use `src/main.rs` as a template:

```rust
use clap::{Arg, Command};
use rust_paddle_ocr::{OcrEngineManager};

fn main() -> OcrResult<()> {
    let matches = Command::new("ocr-tool")
        .arg(Arg::new("input").required(true))
        .arg(Arg::new("output").long("output"))
        .arg(Arg::new("format").long("format").value_parser(["text", "json"]))
        .get_matches();

    // Initialize OCR engine
    OcrEngineManager::initialize("./models/det.mnn", "./models/rec.mnn", "./keys.txt")?;

    // Process image
    let img = image::open(matches.get_one::<String>("input").unwrap())?;
    let texts = OcrEngineManager::process_ocr(img)?;

    // Output results
    match matches.get_one::<String>("format").unwrap_or(&"text".to_string()).as_str() {
        "json" => println!("{}", serde_json::json!(texts)),
        _ => texts.iter().for_each(|t| println!("{}", t)),
    }

    Ok(())
}
```

### CLI Best Practices

- **Progress Bars**: Use `indicatif` for long-running operations
- **Output Formats**: Support plain text, JSON, CSV formats
- **Batch Processing**: Process entire directories
- **Configuration**: Allow model path customization via config files

## 4. Performance Optimization

### Memory Efficiency

Use the efficient cropping features:

```rust
use rust_paddle_ocr::{EfficientCropper, ImageRef};

let cropper = EfficientCropper::new();
let image_ref = ImageRef::from_dynamic_image(&img);

// Smart cropping to reduce processing area
let cropped_regions = cropper.smart_crop(&image_ref)?;
```

### Threading Strategies

For batch processing, use the multi-threading pattern:

```rust
use rayon::prelude::*;

let results: Vec<OcrResult<Vec<String>>> = image_paths
    .par_iter()
    .map(|path| {
        let img = image::open(path)?;
        OcrEngineManager::process_ocr(img)
    })
    .collect();
```

### Model Optimization

- **FP16 Models**: Use `*_fp16.mnn` models for better performance
- **Thread Count**: Set to number of CPU cores (usually 4-12)
- **Image Resizing**: Pre-resize large images before OCR
- **Cropping**: Use smart cropping to focus on text regions

## 5. Troubleshooting Common Issues

### Model Loading Problems

**Issue**: "Failed to load model" errors

**Solutions**:
1. Verify model file paths exist and are readable
2. Check model file integrity (not corrupted)
3. Ensure MNN runtime is properly installed
4. Use absolute paths to avoid relative path issues

```rust
// Debug model loading
let model_path = std::path::Path::new("./models/det_model.mnn");
if !model_path.exists() {
    eprintln!("Model file not found: {:?}", model_path);
    std::process::exit(1);
}
```

### Poor Recognition Accuracy

**Issue**: OCR results are inaccurate or missing text

**Solutions**:
1. **Image Preprocessing**: Enhance contrast, resize appropriately
2. **Model Selection**: Use v5 models for better accuracy
3. **Language Support**: Ensure correct character set files
4. **Image Quality**: Check resolution and lighting

```rust
// Image preprocessing example
let img = image::open("input.jpg")?;
let enhanced = imageproc::contrast::adjust_contrast(&img, 1.2);
let resized = image::imageops::resize(&enhanced, 1024, 768, image::imageops::FilterType::Lanczos3);
```

### Memory Issues

**Issue**: Out of memory errors with large images

**Solutions**:
1. **Image Resizing**: Limit input image size
2. **Batch Processing**: Process images in smaller batches
3. **Memory Cleanup**: Explicitly drop large objects
4. **Efficient Cropping**: Use smart cropping before full processing

```rust
// Memory-efficient processing
let max_size = 2048;
let img = image::open("large_image.jpg")?;
let resized = if img.width() > max_size || img.height() > max_size {
    image::imageops::resize(&img, max_size, max_size, image::imageops::FilterType::Lanczos3)
} else {
    img
};
```

### Performance Bottlenecks

**Issue**: OCR processing is too slow

**Solutions**:
1. **Thread Configuration**: Optimize thread count for your CPU
2. **Model Selection**: Use mobile models for faster processing
3. **Caching**: Cache results for repeated images
4. **Parallel Processing**: Use Rayon for batch operations

## 6. Production Deployment

### Docker Integration

```dockerfile
FROM rust:1.75-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmnn-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy application and models
COPY . /app
WORKDIR /app

# Build and run
RUN cargo build --release
CMD ["./target/release/ocr-app"]
```

### Configuration Management

Use environment variables for model paths:

```rust
fn get_model_path(model_name: &str) -> String {
    std::env::var(format!("OCR_{}_MODEL", model_name.to_uppercase()))
        .unwrap_or_else(|_| format!("./models/{}.mnn", model_name))
}

let det_model = get_model_path("det");
let rec_model = get_model_path("rec");
```

### Error Handling

Implement robust error handling:

```rust
use rust_paddle_ocr::OcrError;

fn process_with_fallback(img: &DynamicImage) -> Vec<String> {
    match OcrEngineManager::process_ocr(img.clone()) {
        Ok(texts) => texts,
        Err(OcrError::ModelLoadError(msg)) => {
            eprintln!("Model error: {}", msg);
            Vec::new()
        }
        Err(OcrError::ImageError(msg)) => {
            eprintln!("Image error: {}", msg);
            Vec::new()
        }
        Err(e) => {
            eprintln!("OCR error: {}", e);
            Vec::new()
        }
    }
}
```

## Resources

### src/
Core Rust implementation files:
- **lib.rs** - Main library entry point, exports all public APIs
- **main.rs** - Command-line interface with JSON/text output modes
- **engine.rs** - Thread-safe OCR engine with actor pattern implementation
- **det.rs** - Text detection functionality using PaddleOCR models
- **rec.rs** - Text recognition functionality using PaddleOCR models
- **efficient_cropping.rs** - Performance optimization utilities for image cropping
- **error.rs** - Error handling types and definitions
- **capi.rs** - C-compatible API for integration with other languages

### models/
Pre-trained PaddleOCR models optimized for MNN:
- **PP-OCRv5_mobile_det_fp16.mnn** - Text detection model (FP16 optimized)
- **PP-OCRv5_mobile_rec_fp16.mnn** - Text recognition model (FP16 optimized)
- **ppocr_keys_v5.txt** - Character set definitions

### examples/
Example applications demonstrating different usage patterns:
- **simple.rs** - Basic OCR usage example
- **multi_thread.rs** - Multi-threaded processing example
- **cropping_benchmark.rs** - Performance benchmark for cropping

### references/
Comprehensive documentation and guides:
- **quick-start.md** - Getting started guide
- **api-reference.md** - Detailed API documentation
- **architecture.md** - System architecture overview
- **code-explanation.md** - Implementation details
- **examples.md** - Extended examples documentation
- **interactive-examples.md** - Interactive code examples
- **performance.md** - Performance optimization guide
- **troubleshooting.md** - Common issues and solutions

### res/
Sample images for testing and demonstration:
- Test images (1.png, 2.png, etc.) with expected OCR result visualizations

### demo/
Demo applications showing integration with other languages:
- **c_demo.c** - C API usage demonstration
- **python_demo.py** - Python integration example

### scripts/
Utility scripts for development and deployment:
- (currently empty)

---
**Quick Start**: Refer to the examples in `examples/simple.rs` to get started. For detailed API documentation, see `references/api-reference.md`.