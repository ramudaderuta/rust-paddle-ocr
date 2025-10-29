# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Rust-based OCR (Optical Character Recognition) library that uses PaddleOCR models with the MNN inference framework. The library provides both high-level and low-level APIs for text detection and recognition, with support for thread-safe operations and multiple usage patterns.

## Key Components

### Core Modules
- `src/lib.rs` - Main library entry point, exports all public APIs
- `src/engine.rs` - Thread-safe OCR engine with actor pattern implementation
- `src/det.rs` - Text detection functionality using PaddleOCR models
- `src/rec.rs` - Text recognition functionality using PaddleOCR models
- `src/efficient_cropping.rs` - Performance optimization utilities for image cropping
- `src/error.rs` - Error handling types and definitions
- `src/capi.rs` - C-compatible API for integration with other languages

### CLI Application
- `src/main.rs` - Command-line interface with JSON/text output modes

### Models
- `models/PP-OCRv5_mobile_det_fp16.mnn` - Text detection model (FP16 optimized)
- `models/PP-OCRv5_mobile_rec_fp16.mnn` - Text recognition model (FP16 optimized)
- `models/ppocr_keys_v5.txt` - Character set definitions

## Development Commands

### Building
```bash
# Build the project
cargo build

# Build with optimizations
cargo build --release

# Build C API headers
cargo build --features cbindgen
```

### Running Tests
```bash
# Run unit tests
cargo test

# Run specific test
cargo test test_name

# Run tests with output
cargo test -- --nocapture
```

### Running Benchmarks
```bash
# Run performance benchmarks
cargo bench

# Run specific benchmark
cargo bench bench_name
```

### Running Examples
```bash
# Run simple example
cargo run --example simple

# Run multi-thread example
cargo run --example multi_thread

# Run cropping benchmark
cargo run --example cropping_benchmark
```

### Running CLI Tool
```bash
# Run with image path
cargo run -- --path res/1.png

# Run with JSON output
cargo run -- --path res/1.png --mode json

# Run with verbose logging
cargo run -- --path res/1.png --verbose
```

## Architecture Overview

### Thread-Safe Design
The library uses an actor pattern with message passing for thread safety:
- `OcrEngine` manages a worker thread that holds the actual models
- All operations are performed through message passing via channels
- This prevents race conditions and allows safe concurrent access

### Singleton Pattern
- `OcrEngineManager` provides a global singleton for easy access
- Models are loaded once and shared across the application
- Thread-safe access through mutex protection

### Performance Optimizations
- Smart cropping strategies based on region size
- Lazy session initialization for MNN models
- Tensor name caching to avoid repeated lookups
- Input shape caching to avoid unnecessary resizes
- Parallel processing with Rayon for image preprocessing

### API Layers
1. **High-Level API** (`OcrEngineManager`) - Simple global access
2. **Mid-Level API** (`OcrEngine`) - Instance-based with custom configuration
3. **Low-Level API** (`Det`, `Rec`) - Direct model access
4. **C API** (`capi.rs`) - FFI-compatible interface

## Common Development Tasks

### Adding New OCR Features
1. Extend the `OcrRequest` enum in `engine.rs`
2. Add handler in the worker thread loop
3. Add public method to `OcrEngine` and `OcrEngineManager`
4. Update C API if needed

### Modifying Model Parameters
1. Adjust configuration in `Det` or `Rec` structs
2. Update builder methods (`with_*` functions)
3. Modify preprocessing or postprocessing logic
4. Update documentation and examples

### Performance Optimization
1. Profile with `cargo bench` to identify bottlenecks
2. Consider parallelization with Rayon
3. Optimize memory usage with efficient cropping
4. Cache frequently accessed data

## Integration Patterns

### Web Applications
Use the high-level `OcrEngineManager` with singleton pattern:
```rust
OcrEngineManager::initialize(det_model, rec_model, keys)?;
let texts = OcrEngineManager::process_ocr(image)?;
```

### Desktop Applications
Use the mid-level `OcrEngine` for more control:
```rust
let engine = OcrEngine::new_with_config(...)?;
let texts = engine.process_ocr(image)?;
```

### CLI Tools
Use the built-in CLI or create custom ones with `clap`

### C/C++ Integration
Use the C API through generated `rocr.h` header file

## Error Handling
The library uses `thiserror` for comprehensive error types:
- `OcrError` enum covers all possible error scenarios
- `OcrResult<T>` type alias for `Result<T, OcrError>`
- Proper error propagation with `?` operator
- Specific error variants for different failure modes

## Testing Strategy
- Unit tests for individual components
- Integration tests for end-to-end workflows
- Performance benchmarks for optimization
- Example code that serves as documentation and verification

## Model Management
- FP16 models for better performance/size tradeoff
- Embedded models in CLI binary for easy distribution
- Configurable model paths for flexibility
- Character set files for language support