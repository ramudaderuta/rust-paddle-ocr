---
name: rust-paddle-ocr
description: This skill provides comprehensive guidance for using the Rust PaddleOCR library, a lightweight and efficient OCR implementation. Use this skill when users need to extract text from images, integrate OCR into Rust applications, process multiple images with OCR, optimize OCR performance, or troubleshoot OCR processing issues. The skill covers basic OCR operations, advanced configuration, batch processing, CLI usage, and integration patterns.
---

# Rust PaddleOCR Skill

## Overview

This skill enables efficient text extraction from images using the Rust PaddleOCR library. It provides comprehensive workflows for OCR processing, from basic text extraction to advanced optimization and integration scenarios.

## Quick Start

### Basic OCR Processing
For simple text extraction from images:

```rust
use rust_paddle_ocr::OcrEngineManager;
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize OCR engine
    OcrEngineManager::initialize("det_model.mnn", "rec_model.mnn", "keys.txt")?;

    // Load image and extract text
    let img = open("image.jpg")?;
    let texts = OcrEngineManager::process_ocr(img)?;

    for text in texts {
        println!("{}", text);
    }
    Ok(())
}
```

### Command Line Usage
For quick OCR processing without code:

```bash
# Basic text extraction
ocr --path image.jpg

# Detailed JSON output with positions
ocr --path image.jpg --mode json

# Verbose logging
ocr --path image.jpg --verbose
```

## Core Capabilities

### 1. Text Extraction and Processing

#### Basic Text Recognition
Extract text from images using the high-level API:
- Initialize `OcrEngineManager` with model paths
- Use `process_ocr()` for end-to-end processing
- Handle results and errors appropriately

#### Advanced Text Processing
For fine-grained control over OCR processing:
- Use `Det` and `Rec` models separately
- Access text regions and positions
- Implement custom processing pipelines

#### Batch Image Processing
Process multiple images efficiently:
- Load the scripts/batch_ocr.py script for Python-based batch processing
- Use parallel processing with Rust's rayon
- Implement progress tracking and error handling

### 2. Model Configuration and Optimization

#### Model Setup
Configure OCR models for optimal performance:
- Download models using scripts/model_downloader.py
- Set up model paths and character dictionaries
- Configure detection and recognition parameters

#### Performance Optimization
Optimize OCR processing speed and accuracy:
- Use EfficientCropper for smart image preprocessing
- Configure batch processing parameters
- Implement caching strategies

#### Memory Management
Handle large images and batch processing:
- Use smart cropping to reduce memory usage
- Implement streaming processing for large datasets
- Monitor memory usage and optimize accordingly

### 3. Integration Patterns

#### Web Service Integration
Integrate OCR into web applications:
- Create REST API endpoints for OCR processing
- Handle file uploads and result formatting
- Implement async processing for large images

#### Desktop Application Integration
Add OCR capabilities to desktop apps:
- Use the C API for cross-language integration
- Implement real-time text recognition
- Handle GUI integration and progress reporting

#### Pipeline Integration
Incorporate OCR into data processing pipelines:
- Chain OCR with other image processing operations
- Implement automated document processing workflows
- Handle error recovery and retry logic

## Workflow Decision Tree

### What type of OCR processing do you need?

**Simple text extraction from one or few images**
→ Use Quick Start basic OCR processing
→ Consider CLI tool for immediate results

**Batch processing of multiple images**
→ Use scripts/batch_ocr.py for Python automation
→ Implement Rust-based batch processing for performance
→ Consider parallel processing options

**Integration into existing application**
→ Use appropriate integration pattern (Web/Desktop/Pipeline)
→ Configure models and parameters for your use case
→ Implement error handling and logging

**Performance optimization needed**
→ Use EfficientCropper for preprocessing
→ Configure model parameters for your specific content
→ Implement caching and batch processing

**Custom OCR requirements**
→ Use low-level Det and Rec APIs
→ Implement custom text processing logic
→ Configure advanced model parameters

## Common Usage Patterns

### Document Processing
Process scanned documents and PDFs:
1. Convert documents to images
2. Apply preprocessing if needed (scripts/image_preprocessor.py)
3. Extract text using OCR
4. Post-process results for your use case

### Real-time Text Recognition
Implement live text extraction:
1. Set up efficient image capture
2. Use optimized model configuration
3. Implement frame-by-frame processing
4. Handle result caching and deduplication

### Multi-language Support
Handle text in different languages:
1. Load appropriate character dictionaries
2. Configure model parameters for language-specific features
3. Implement post-processing for language-specific formatting

## Error Handling and Troubleshooting

### Common Issues
- Model loading failures: Check model paths and formats
- Memory errors: Use EfficientCropper and reduce image sizes
- Poor recognition: Preprocess images and adjust parameters
- Performance issues: Enable parallel processing and caching

### Debug Tools
- Use verbose logging for detailed processing information
- Save debug images with text region overlays
- Benchmark performance using scripts/ocr_benchmark.py

## Resources

### scripts/
Executable code for OCR automation and optimization:

- **batch_ocr.py** - Python script for processing multiple images with OCR
- **ocr_benchmark.py** - Performance testing and benchmarking utilities
- **model_downloader.py** - Automated downloading of required PaddleOCR models
- **image_preprocessor.py** - Image preprocessing utilities for better OCR results

### references/
Comprehensive documentation and guides:

- **api-cheatsheet.md** - Quick reference for common API patterns and methods
- **configuration-guide.md** - Detailed model configuration and optimization guide
- **troubleshooting.md** - Common issues, solutions, and debugging techniques
- **integration-patterns.md** - Examples for different integration scenarios
- **performance-tips.md** - Performance optimization techniques and best practices

### assets/
Templates and example files:

- **example-images/** - Sample images for testing OCR functionality
- **templates/** - Code templates for common use cases (web API, desktop app, CLI tool)
- **model-configs/** - Example model configuration files for different scenarios
