# Rust PaddleOCR

[English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

A lightweight and efficient OCR (Optical Character Recognition) library implemented in Rust, based on the PaddleOCR models. This library leverages the MNN inference framework to provide high-performance text detection and recognition capabilities.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## Features

- **Text Detection**: Accurately locate text regions in images
- **Text Recognition**: Recognize text content from the detected regions
- **High Performance**: Optimized with the MNN inference framework
- **Minimal Dependencies**: Lightweight and easy to integrate
- **Customizable**: Adjustable parameters for different use cases
- **Command-line Tool**: Simple command-line interface for OCR recognition

## Installation

Add this to your `Cargo.toml`:

```toml
[dependencies.rust-paddle-ocr]
git = "https://github.com/zibo-chen/rust-paddle-ocr.git"
```

You can also specify a particular branch or tag:

```toml
[dependencies.rust-paddle-ocr]
git = "https://github.com/zibo-chen/rust-paddle-ocr.git"
branch = "main"
```

### Prerequisites

This library requires:
- Pre-trained PaddleOCR models converted to MNN format
- Character set file for text recognition

## Command-line Tool

This library provides a built-in command-line tool for direct OCR recognition:

```bash
# Basic usage
./ocr -p path/to/image.jpg

# Output in JSON format (with detailed information and positions)
./ocr -p path/to/image.jpg -m json

# Show verbose log information
./ocr -p path/to/image.jpg -v
```

### Command-line Options

```
Options:
  -p, --path <IMAGE_PATH>  Path to the image for recognition
  -m, --mode <MODE>        Output mode: json(detailed) or text(simple) [default: text]
  -v, --verbose            Show verbose log information
  -h, --help               Print help information
  -V, --version            Print version information
```

## Usage Example

```rust
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load the detection model
    let mut det = Det::from_file("path/to/det_model.mnn")?;
    
    // Customize detection parameters (optional)
    let det = det
        .with_rect_border_size(50)
        .with_merge_boxes(true)
        .with_merge_threshold(10);
    
    // Load the recognition model
    let mut rec = Rec::from_file("path/to/rec_model.mnn", "path/to/keys.txt")?;
    
    // Customize recognition parameters (optional)
    let rec = rec
        .with_min_score(0.6)
        .with_punct_min_score(0.1);
    
    // Open an image
    let img = open("path/to/image.jpg")?;
    
    // Detect text regions
    let text_images = det.find_text_img(&img)?;
    
    // Recognize text in each detected region
    for text_img in text_images {
        let text = rec.predict_str(&text_img)?;
        println!("Recognized text: {}", text);
    }
    
    Ok(())
}
```

## API Reference

### Text Detection (Det)

```rust
// Create a new detector
let mut det = Det::from_file("path/to/det_model.mnn")?;

// Find text regions and return rectangles
let rects = det.find_text_rect(&img)?;

// Find text regions and return cropped images
let text_images = det.find_text_img(&img)?;

// Customization options
let det = det
    .with_rect_border_size(50)      // Set border size for detected regions
    .with_merge_boxes(true)         // Enable/disable merging adjacent boxes
    .with_merge_threshold(10);      // Set threshold for box merging
```

### Text Recognition (Rec)

```rust
// Create a new recognizer
let mut rec = Rec::from_file("path/to/rec_model.mnn", "path/to/keys.txt")?;

// Recognize text and return a string
let text = rec.predict_str(&text_img)?;

// Recognize text and return characters with confidence scores
let char_scores = rec.predict_char_score(&text_img)?;

// Customization options
let rec = rec
    .with_min_score(0.6)           // Set minimum confidence for regular characters
    .with_punct_min_score(0.1);    // Set minimum confidence for punctuation
```

## Performance Optimization

This library includes several optimizations:
- Efficient tensor management
- Smart box merging for text detection
- Adaptive image preprocessing
- Configurable confidence thresholds

## Example Results

Here are some example results showing the library in action:

### Example 1
![Original Image 1](res/1.png)
![OCR Result 1](res/1_ocr_result.png)

### Example 2
![Original Image 2](res/2.png)
![OCR Result 2](res/2_ocr_result.png)

### Example 3
![Original Image 3](res/3.png)
![OCR Result 3](res/3_ocr_result.png)

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - For the original OCR models and research
- [MNN](https://github.com/alibaba/MNN) - For the efficient neural network inference framework
- [mnn-rs](https://github.com/aftershootco/mnn-rs) - For providing Rust bindings to MNN
