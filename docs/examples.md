# Examples Guide

This document provides comprehensive examples for using the Rust PaddleOCR library, from basic usage to advanced configurations.

## 📁 Table of Contents

- [Basic Examples](#basic-examples)
- [Advanced Examples](#advanced-examples)
- [Performance Examples](#performance-examples)
- [Error Handling Examples](#error-handling-examples)
- [Integration Examples](#integration-examples)

## Basic Examples

### Example 1: Simple OCR Processing

```rust
// examples/simple.rs
use rust_paddle_ocr::OcrEngineManager;
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize the OCR engine
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    // Load an image
    let img = open("examples/document.jpg")?;

    // Process OCR
    let texts = OcrEngineManager::process_ocr(img)?;

    // Print results
    println!("Found {} text regions:", texts.len());
    for (i, text) in texts.iter().enumerate() {
        println!("  {}: {}", i + 1, text);
    }

    Ok(())
}
```

### Example 2: Batch Processing

```rust
// examples/batch_processing.rs
use rust_paddle_ocr::OcrEngineManager;
use image::open;
use std::path::Path;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize once
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    // Process multiple images
    let image_files = vec![
        "examples/doc1.jpg",
        "examples/doc2.jpg",
        "examples/doc3.jpg",
    ];

    for image_file in image_files {
        println!("Processing: {}", image_file);

        match open(image_file) {
            Ok(img) => {
                match OcrEngineManager::process_ocr(img) {
                    Ok(texts) => {
                        println!("  Found {} text regions", texts.len());
                        for text in texts {
                            println!("    - {}", text);
                        }
                    }
                    Err(e) => eprintln!("  OCR error: {}", e),
                }
            }
            Err(e) => eprintln!("  Failed to load image: {}", e),
        }
    }

    Ok(())
}
```

### Example 3: Text Region Detection Only

```rust
// examples/detection_only.rs
use rust_paddle_ocr::OcrEngineManager;
use image::open;
use imageproc::rect::Rect;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    let img = open("examples/document.jpg")?;

    // Get text regions as rectangles
    let text_rects = OcrEngineManager::get_text_rects(&img)?;

    println!("Found {} text regions:", text_rects.len());
    for (i, rect) in text_rects.iter().enumerate() {
        println!("  {}: x={}, y={}, width={}, height={}",
                 i + 1, rect.left(), rect.top(), rect.width(), rect.height());
    }

    Ok(())
}
```

## Advanced Examples

### Example 4: Custom Configuration

```rust
// examples/custom_config.rs
use rust_paddle_ocr::OcrEngineManager;
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize with custom configuration
    OcrEngineManager::initialize_with_config(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt",
        20,    // rect_border_size: extend text boxes by 20 pixels
        true,  // merge_boxes: merge overlapping text boxes
        5      // merge_threshold: merge boxes within 5 pixels
    )?;

    let img = open("examples/dense_text.jpg")?;

    // Use efficient cropping for better performance
    let texts = OcrEngineManager::process_ocr_efficient(img)?;

    println!("Results with custom configuration:");
    for text in texts {
        println!("  {}", text);
    }

    Ok(())
}
```

### Example 5: Step-by-Step Processing

```rust
// examples/step_by_step.rs
use rust_paddle_ocr::{Det, Rec};
use image::open;
use imageproc::rect::Rect;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load models directly for more control
    let mut det = Det::from_file("models/det_model.mnn")?
        .with_rect_border_size(15)
        .with_merge_boxes(true)
        .with_merge_threshold(3);

    let mut rec = Rec::from_file("models/rec_model.mnn", "models/keys.txt")?;

    let img = open("examples/document.jpg")?;

    // Step 1: Detect text regions
    println!("Step 1: Detecting text regions...");
    let text_rects = det.find_text_rect(&img)?;
    println!("Found {} text regions", text_rects.len());

    // Step 2: Extract text images
    println!("Step 2: Extracting text images...");
    let text_images = det.find_text_img(&img)?;
    println!("Extracted {} text images", text_images.len());

    // Step 3: Recognize each text region
    println!("Step 3: Recognizing text...");
    let mut results = Vec::new();
    for (i, text_img) in text_images.into_iter().enumerate() {
        match rec.predict_str(&text_img) {
            Ok(text) => {
                println!("  Region {}: {}", i + 1, text);
                results.push(text);
            }
            Err(e) => {
                println!("  Region {}: Recognition failed - {}", i + 1, e);
                results.push(format!("[ERROR: {}]", e));
            }
        }
    }

    // Step 4: Display results with positions
    println!("\nFinal Results:");
    for (i, (rect, text)) in text_rects.iter().zip(results.iter()).enumerate() {
        println!("  Text {}: '{}' at ({}, {}) size {}x{}",
                 i + 1, text, rect.left(), rect.top(), rect.width(), rect.height());
    }

    Ok(())
}
```

### Example 6: Memory-Efficient Processing

```rust
// examples/memory_efficient.rs
use rust_paddle_ocr::{OcrEngineManager, EfficientCropper, ImageRef};
use image::open;
use std::sync::Arc;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    let img = open("examples/large_document.jpg")?;

    // Wrap in Arc for shared ownership
    let shared_img = Arc::new(img);
    let img_ref = ImageRef::from(shared_img);

    println!("Processing large image efficiently...");
    let texts = OcrEngineManager::process_ocr_efficient(
        img_ref.as_dynamic_image().clone()
    )?;

    println!("Found {} text regions:", texts.len());
    for text in texts {
        println!("  {}", text);
    }

    Ok(())
}
```

## Performance Examples

### Example 7: Performance Comparison

```rust
// examples/performance_comparison.rs
use rust_paddle_ocr::OcrEngineManager;
use image::open;
use std::time::Instant;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    let img = open("examples/test_image.jpg")?;

    // Test standard processing
    println!("Testing standard processing...");
    let start = Instant::now();
    let texts_standard = OcrEngineManager::process_ocr(img.clone())?;
    let duration_standard = start.elapsed();
    println!("Standard: {} results in {:?}", texts_standard.len(), duration_standard);

    // Test efficient processing
    println!("Testing efficient processing...");
    let start = Instant::now();
    let texts_efficient = OcrEngineManager::process_ocr_efficient(img)?;
    let duration_efficient = start.elapsed();
    println!("Efficient: {} results in {:?}", texts_efficient.len(), duration_efficient);

    // Compare results
    println!("\nComparison:");
    println!("  Speed improvement: {:.2}x",
             duration_standard.as_secs_f64() / duration_efficient.as_secs_f64());
    println!("  Results match: {}", texts_standard == texts_efficient);

    Ok(())
}
```

### Example 8: Multi-threaded Processing

```rust
// examples/multi_threaded.rs
use rust_paddle_ocr::OcrEngineManager;
use image::open;
use std::sync::Arc;
use std::thread;
use std::time::Instant;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize once
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    let image_files = vec![
        "examples/doc1.jpg",
        "examples/doc2.jpg",
        "examples/doc3.jpg",
        "examples/doc4.jpg",
    ];

    let start = Instant::now();

    // Process images in parallel
    let handles: Vec<_> = image_files.into_iter()
        .map(|file| {
            thread::spawn(move || {
                match open(file) {
                    Ok(img) => {
                        match OcrEngineManager::process_ocr(img) {
                            Ok(texts) => Some((file, texts)),
                            Err(e) => {
                                eprintln!("Error processing {}: {}", file, e);
                                None
                            }
                        }
                    }
                    Err(e) => {
                        eprintln!("Failed to load {}: {}", file, e);
                        None
                    }
                }
            })
        })
        .collect();

    // Collect results
    let mut total_texts = 0;
    for handle in handles {
        if let Some((file, texts)) = handle.join().unwrap() {
            println!("{}: {} text regions", file, texts.len());
            total_texts += texts.len();
        }
    }

    let duration = start.elapsed();
    println!("\nProcessed {} images with {} total text regions in {:?}",
             handles.len(), total_texts, duration);

    Ok(())
}
```

## Error Handling Examples

### Example 9: Comprehensive Error Handling

```rust
// examples/error_handling.rs
use rust_paddle_ocr::{OcrEngineManager, OcrError};
use image::open;

fn main() {
    match initialize_and_process() {
        Ok(results) => {
            println!("Successfully processed {} images", results);
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            match e {
                OcrError::ModelLoadError(msg) => {
                    eprintln!("Model loading failed: {}", msg);
                    eprintln!("Please check model file paths and formats");
                }
                OcrError::InferenceError(msg) => {
                    eprintln!("Inference failed: {}", msg);
                    eprintln!("Please check input image format and quality");
                }
                OcrError::ImageError(msg) => {
                    eprintln!("Image processing failed: {}", msg);
                    eprintln!("Please check image file integrity");
                }
                OcrError::EngineError(msg) => {
                    eprintln!("Engine error: {}", msg);
                    eprintln!("Please ensure engine is properly initialized");
                }
            }
        }
    }
}

fn initialize_and_process() -> Result<usize, OcrError> {
    // Initialize with error handling
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    let test_images = vec![
        "examples/test1.jpg",
        "examples/test2.jpg",
        "examples/test3.jpg",
    ];

    let mut processed_count = 0;
    for image_path in test_images {
        match open(image_path) {
            Ok(img) => {
                match OcrEngineManager::process_ocr(img) {
                    Ok(texts) => {
                        println!("{}: {} text regions found", image_path, texts.len());
                        processed_count += 1;
                    }
                    Err(e) => {
                        eprintln!("OCR failed for {}: {}", image_path, e);
                        // Continue with next image
                    }
                }
            }
            Err(e) => {
                eprintln!("Failed to load {}: {}", image_path, e);
                // Continue with next image
            }
        }
    }

    Ok(processed_count)
}
```

## Integration Examples

### Example 10: Web Server Integration

```rust
// examples/web_server.rs
use rust_paddle_ocr::OcrEngineManager;
use image::{DynamicImage, ImageFormat};
use std::sync::Arc;
use std::io::prelude::*;

// Simulate a web server endpoint
async fn ocr_endpoint(image_data: Vec<u8>) -> Result<Vec<String>, Box<dyn std::error::Error>> {
    // Convert bytes to image
    let img = image::load_from_memory(&image_data)?;

    // Process OCR
    let texts = OcrEngineManager::process_ocr(img)?;

    Ok(texts)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize OCR engine once at startup
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    println!("OCR Server initialized and ready!");

    // Simulate processing multiple requests
    let test_images = vec![
        "examples/doc1.jpg",
        "examples/doc2.jpg",
    ];

    for image_path in test_images {
        println!("Processing request for: {}", image_path);

        // Read image file (simulating upload)
        let image_data = std::fs::read(image_path)?;

        // Process in async context
        match ocr_endpoint(image_data).await {
            Ok(texts) => {
                println!("  Found {} text regions", texts.len());
                for text in texts {
                    println!("    - {}", text);
                }
            }
            Err(e) => {
                eprintln!("  Error: {}", e);
            }
        }
    }

    Ok(())
}
```

### Example 11: CLI Application

```rust
// examples/cli_app.rs
use clap::{Arg, Command};
use rust_paddle_ocr::OcrEngineManager;
use image::open;
use std::path::PathBuf;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let matches = Command::new("rust-ocr-cli")
        .version("1.0")
        .about("CLI for Rust PaddleOCR")
        .arg(
            Arg::new("input")
                .short('i')
                .long("input")
                .value_name("FILE")
                .help("Input image file")
                .required(true)
        )
        .arg(
            Arg::new("det-model")
                .short('d')
                .long("det-model")
                .value_name("FILE")
                .help("Detection model file")
                .default_value("models/det_model.mnn")
        )
        .arg(
            Arg::new("rec-model")
                .short('r')
                .long("rec-model")
                .value_name("FILE")
                .help("Recognition model file")
                .default_value("models/rec_model.mnn")
        )
        .arg(
            Arg::new("keys")
                .short('k')
                .long("keys")
                .value_name("FILE")
                .help("Character keys file")
                .default_value("models/keys.txt")
        )
        .arg(
            Arg::new("efficient")
                .short('e')
                .long("efficient")
                .help("Use efficient cropping")
                .action(clap::ArgAction::SetTrue)
        )
        .get_matches();

    // Initialize OCR engine
    let det_model = matches.get_one::<String>("det-model").unwrap();
    let rec_model = matches.get_one::<String>("rec-model").unwrap();
    let keys = matches.get_one::<String>("keys").unwrap();

    println!("Initializing OCR engine...");
    OcrEngineManager::initialize(det_model, rec_model, keys)?;

    // Process image
    let input_file = matches.get_one::<String>("input").unwrap();
    println!("Processing: {}", input_file);

    let img = open(input_file)?;

    let texts = if matches.get_flag("efficient") {
        OcrEngineManager::process_ocr_efficient(img)?
    } else {
        OcrEngineManager::process_ocr(img)?
    };

    // Output results
    println!("\nResults:");
    println!("Found {} text regions:", texts.len());
    for (i, text) in texts.iter().enumerate() {
        println!("  {}: {}", i + 1, text);
    }

    Ok(())
}
```

## Running Examples

Each example can be run with:

```bash
# Run basic example
cargo run --example simple

# Run with specific features
cargo run --example performance_comparison --features fast_resize

# Run CLI example with arguments
cargo run --example cli_app -- --input examples/document.jpg --efficient
```

## Best Practices

1. **Initialize once**: Call `initialize()` at application startup
2. **Error handling**: Always handle `OcrResult` properly
3. **Memory management**: Use `process_ocr_efficient()` for large images
4. **Batch processing**: Process multiple images sequentially for better performance
5. **Resource cleanup**: Let the `Drop` trait handle cleanup automatically