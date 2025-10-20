# Rust PaddleOCR

[English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

A lightweight and efficient OCR (Optical Character Recognition) library implemented in Rust, based on the PaddleOCR models. This library leverages the MNN inference framework to provide high-performance text detection and recognition capabilities.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## Features

- **Text Detection**: Accurately locate text regions in images
- **Text Recognition**: Recognize text content from the detected regions
- **Multi-Version Model Support**: Support for both PP-OCRv4 and PP-OCRv5 models with flexible selection
- **Multi-Language Support**: PP-OCRv5 supports Simplified Chinese, Traditional Chinese, English, Japanese, Chinese Pinyin and more
- **Complex Scene Recognition**: Enhanced handwriting, vertical text, and rare character recognition capabilities
- **High Performance**: Optimized with the MNN inference framework
- **Minimal Dependencies**: Lightweight and easy to integrate
- **Customizable**: Adjustable parameters for different use cases
- **Command-line Tool**: Simple command-line interface for OCR recognition

## Model Versions

This library supports three PaddleOCR model versions:

### PP-OCRv4
- **Stable Version**: Well-tested and highly compatible
- **Use Cases**: Regular document recognition, scenarios requiring high accuracy
- **Model Files**:
  - Detection model: `ch_PP-OCRv4_det_infer.mnn`
  - Recognition model: `ch_PP-OCRv4_rec_infer.mnn`
  - Character set: `ppocr_keys_v4.txt`

### PP-OCRv5 ⭐️ Recommended
- **Latest Version**: Next-generation text recognition solution
- **Multi-Language Support**: The default model (`PP-OCRv5_mobile_rec.mnn`) supports Simplified Chinese, Traditional Chinese, English, Japanese, and Chinese Pinyin
- **Language-Specific Models**: Dedicated models available for 11+ languages for optimal performance:
  - Arabic, Cyrillic, Devanagari, Greek, English
  - East Slavic, Korean, Latin, Tamil, Telugu, Thai
- **Shared Detection**: All V5 language models use the same detection model (`PP-OCRv5_mobile_det.mnn`)
- **Enhanced Scene Recognition**:
  - Significantly improved Chinese-English complex handwriting recognition
  - Optimized vertical text recognition
  - Enhanced rare character recognition capabilities
- **Performance Improvement**: 13% end-to-end improvement compared to PP-OCRv4
- **Model Files** (Default Multi-language):
  - Detection model: `PP-OCRv5_mobile_det.mnn` (shared by all languages)
  - Recognition model: `PP-OCRv5_mobile_rec.mnn` (default, supports Chinese/English/Japanese)
  - Character set: `ppocr_keys_v5.txt`
- **Language-Specific Model Files** (Optional):
  - Recognition models: `{lang}_PP-OCRv5_mobile_rec_infer.mnn`
  - Character sets: `ppocr_keys_{lang}.txt`
  - Available languages: `arabic`, `cyrillic`, `devanagari`, `el` (Greek), `en`, `eslav`, `korean`, `latin`, `ta` (Tamil), `te` (Telugu), `th` (Thai)

### PP-OCRv5 FP16 ⭐️ New
- **Efficient Version**: Provides faster inference speed and lower memory usage without sacrificing accuracy
- **Use Cases**: Scenarios requiring high performance and low memory usage
- **Performance Improvements**:
  - Inference speed increased by ~9%
  - Memory usage reduced by ~8%
  - Model size halved
- **Model Files**:
  - Detection model: `PP-OCRv5_mobile_det_fp16.mnn`
  - Recognition model: `PP-OCRv5_mobile_rec_fp16.mnn`
  - Character set: `ppocr_keys_v5.txt`

### Model Performance Comparison

| Feature             | PP-OCRv4 | PP-OCRv5 | PP-OCRv5 FP16 |
|---------------------|----------|----------|---------------|
| Language Support    | Chinese, English | Multi-language (default supports Chinese/English/Japanese, 11+ dedicated language models available) | Multi-language (default supports Chinese/English/Japanese, 11+ dedicated language models available) |
| Script Support      | Chinese, English | Simplified Chinese, Traditional Chinese, English, Japanese, Chinese Pinyin | Simplified Chinese, Traditional Chinese, English, Japanese, Chinese Pinyin |
| Handwriting Support | Basic    | Enhanced | Enhanced |
| Vertical Text       | Basic    | Optimized | Optimized |
| Rare Character      | Limited  | Enhanced | Enhanced |
| Inference Speed (FPS)| 1.1     | 1.2      | 1.2 |
| Memory Usage (Peak) | 422.22MB | 388.41MB | 388.41MB |
| Model Size          | Standard | Standard | Halved |
| Recommended Use Case| Regular Documents | Complex Scenarios & Multi-language | High-Performance Scenarios & Multi-language |

### PP-OCRv5 FP16 Test Data

#### Standard Model
```
============================================================
Test Report: Inference Speed Test
============================================================
Total Time: 44.23s
Average Inference Time: 884.64ms
Fastest Inference Time: 744.99ms
Slowest Inference Time: 954.03ms
Success Count: 50
Failure Count: 0
Inference Speed: 1.1 FPS
Memory Usage - Start: 14.94MB
Memory Usage - End: 422.22MB
Memory Usage - Peak: 422.22MB
Memory Change: +407.28MB
```

#### FP16 Model
```
============================================================
Test Report: Inference Speed Test
============================================================
Total Time: 43.33s
Average Inference Time: 866.66ms
Fastest Inference Time: 719.41ms
Slowest Inference Time: 974.93ms
Success Count: 50
Failure Count: 0
Inference Speed: 1.2 FPS
Memory Usage - Start: 15.70MB
Memory Usage - End: 388.41MB
Memory Usage - Peak: 388.41MB
Memory Change: +372.70MB
```

### Testing Method

Run the following command to execute the test and verify performance data (based on Mac Mini M4):

```bash
python test_ffi.py test
```

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

## Usage

### As a Rust Library

You can flexibly choose between PP-OCRv4 or PP-OCRv5 models by simply loading different model files:

```rust
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // === Using PP-OCRv5 models (Recommended) ===
    let mut det = Det::from_file("./models/PP-OCRv5_mobile_det.mnn")?;
    let mut rec = Rec::from_file(
        "./models/PP-OCRv5_mobile_rec.mnn", 
        "./models/ppocr_keys_v5.txt"
    )?;
    
    // === Or using PP-OCRv4 models ===
    // let mut det = Det::from_file("./models/ch_PP-OCRv4_det_infer.mnn")?;
    // let mut rec = Rec::from_file(
    //     "./models/ch_PP-OCRv4_rec_infer.mnn", 
    //     "./models/ppocr_keys_v4.txt"
    // )?;
    
    // Customize detection parameters (optional)
    let det = det
        .with_rect_border_size(12)  // Recommended for PP-OCRv5
        .with_merge_boxes(false)    // Recommended for PP-OCRv5
        .with_merge_threshold(1);   // Recommended for PP-OCRv5
    
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

### Using Language-Specific Models

For better recognition accuracy with specific languages, you can use dedicated language models:

```rust
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // All V5 language models share the same detection model
    let mut det = Det::from_file("./models/PP-OCRv5_mobile_det.mnn")?;
    
    // === Example 1: English-specific model ===
    let mut rec_en = Rec::from_file(
        "./models/en_PP-OCRv5_mobile_rec_infer.mnn",
        "./models/ppocr_keys_en.txt"
    )?;
    
    // === Example 2: Korean model ===
    let mut rec_ko = Rec::from_file(
        "./models/korean_PP-OCRv5_mobile_rec_infer.mnn",
        "./models/ppocr_keys_korean.txt"
    )?;
    
    // === Example 3: Arabic model ===
    let mut rec_ar = Rec::from_file(
        "./models/arabic_PP-OCRv5_mobile_rec_infer.mnn",
        "./models/ppocr_keys_arabic.txt"
    )?;
    
    // Process image
    let img = open("path/to/image.jpg")?;
    let text_images = det.find_text_img(&img)?;
    
    for text_img in text_images {
        let text = rec_en.predict_str(&text_img)?;
        println!("Recognized text: {}", text);
    }
    
    Ok(())
}
```

#### Available Language Models

| Language | Model File | Character Set | Use Case |
|----------|------------|---------------|----------|
| Default (Multi-language) | `PP-OCRv5_mobile_rec.mnn` | `ppocr_keys_v5.txt` | Chinese, English, Japanese (Recommended for general use) |
| Arabic | `arabic_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_arabic.txt` | Arabic text recognition |
| Cyrillic | `cyrillic_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_cyrillic.txt` | Russian, Bulgarian, Serbian, etc. |
| Devanagari | `devanagari_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_devanagari.txt` | Hindi, Marathi, Nepali, etc. |
| Greek | `el_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_el.txt` | Greek text recognition |
| English | `en_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_en.txt` | English-only documents |
| East Slavic | `eslav_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_eslav.txt` | Ukrainian, Belarusian, etc. |
| Korean | `korean_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_korean.txt` | Korean text recognition |
| Latin | `latin_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_latin.txt` | Latin script languages |
| Tamil | `ta_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_ta.txt` | Tamil text recognition |
| Telugu | `te_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_te.txt` | Telugu text recognition |
| Thai | `th_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_th.txt` | Thai text recognition |

**Note**: All language-specific models use the same detection model (`PP-OCRv5_mobile_det.mnn`). Choose the appropriate recognition model based on your target language for optimal accuracy.

## Command-line Tool

This library provides a built-in command-line tool for direct OCR recognition:

```bash
# Basic usage
./ocr -p path/to/image.jpg

# Output in JSON format (with detailed information and positions)
./ocr -p path/to/image.jpg -m json

# Show verbose log information
./ocr -p path/to/image.jpg -v

# Show current model version information
./ocr --version-info
```

### Building Different Versions

```bash
# Build with PP-OCRv4 models (default)
cargo build --release

# Build with PP-OCRv5 models (recommended)
cargo build --release --features v5
```

### Command-line Options

```
Options:
  -p, --path <IMAGE_PATH>  Path to the image for recognition
  -m, --mode <MODE>        Output mode: json(detailed) or text(simple) [default: text]
  -v, --verbose            Show verbose log information
      --version-info       Show model version information
  -h, --help               Print help information
  -V, --version            Print version information
```

## Model Files

You can obtain pre-trained MNN models from the following sources:

1. **Official Models**: Download from PaddleOCR official repository and convert to MNN format
2. **Project Provided**: The `models/` directory in this project contains pre-converted model files

## PP-OCRv5 vs PP-OCRv4 Performance Comparison

| Feature | PP-OCRv4 | PP-OCRv5 |
|---------|----------|----------|
| Script Support | Chinese, English | Simplified Chinese, Traditional Chinese, English, Japanese, Chinese Pinyin |
| Handwriting Recognition | Basic support | Significantly enhanced |
| Vertical Text | Basic support | Optimized improvement |
| Rare Character Recognition | Limited support | Enhanced recognition |
| End-to-End Accuracy | Baseline | 13% improvement |
| Recommended Scenarios | Regular documents | Complex and diverse scenarios |

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
    .with_rect_border_size(12)
    .with_merge_boxes(false)
    .with_merge_threshold(1);
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
    .with_min_score(0.6)
    .with_punct_min_score(0.1);
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
