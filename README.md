# Rust PaddleOCR Documentation

Welcome to the comprehensive documentation for the Rust PaddleOCR library. This library provides a lightweight, efficient OCR (Optical Character Recognition) implementation in Rust using PaddleOCR models.

## 📚 Documentation Index

###  📚 Documentation Structure

```
  rust-paddle-ocr/
  ├── README.md                    # 📖 Main documentation index (this file)
  └── docs/                       # 📁 Documentation folder
      ├── api-reference.md             # 📖 Complete API documentation (864 lines)
      ├── interactive-examples.md      # 🎯 Hands-on code playground (870 lines)
      ├── documentation-automation.md  # 📜 CI/CD and automation (1,386 lines)
      ├── troubleshooting.md           # 🚨 Issues and solutions (1,238 lines)
      ├── code-explanation.md         # 🔧 Code analysis and patterns (594 lines)
      ├── architecture.md             # 🏗️ System architecture (279 lines)
      ├── examples.md                # 📝 Usage examples (603 lines)
      ├── performance.md             # ⚡ Performance guide (478 lines)
      ├── quick-start.md             # 🚀 Getting started (137 lines)
      └── code-analysis.md           # 📊 Technical analysis (433 lines)
```

### Getting Started
- [**Quick Start Guide**](docs/quick-start.md) - Get up and running in minutes

### Core Documentation
- [**📖 API Reference**](docs/api-reference.md) - Complete API documentation with examples and performance metrics
- [**🎯 Interactive Examples**](docs/interactive-examples.md) - Hands-on code playground with runnable examples
- [**🔧 Code Analysis & Explanation**](docs/code-explanation.md) - Comprehensive code analysis with visual diagrams and step-by-step explanations
- [**🏗️ Architecture Guide**](docs/architecture.md) - System architecture and component overview
- [**🚨 Troubleshooting Guide**](docs/troubleshooting.md) - Common issues, solutions, and FAQ
- [**Examples Guide**](docs/examples.md) - Comprehensive examples from basic to advanced
- [**Performance Guide**](docs/performance.md) - Optimization techniques and best practices

## 📋 Library Overview

### Key Features
- **Thread-safe OCR engine** with concurrent processing
- **Memory-efficient image processing** with smart cropping
- **High-performance inference** using MNN framework
- **Flexible API** supporting both high-level and low-level usage
- **Production-ready** with comprehensive error handling

### Supported Models
- **Text Detection**: Locate text regions in images
- **Text Recognition**: Identify characters in text regions
- **Multi-language support**: Custom character sets and dictionaries

### Performance Characteristics
- **Fast processing**: Optimized for speed and memory usage
- **Scalable**: Supports batch processing and parallel execution
- **Lightweight**: Minimal overhead and resource usage

## 🏗️ Architecture Highlights

The library is built with several key architectural patterns:

- **Actor Pattern**: Message-passing for thread-safe operations
- **Singleton Pattern**: Global engine manager for easy access
- **Strategy Pattern**: Smart cropping strategies for optimization
- **RAII**: Automatic resource management and cleanup

## 🎯 Use Cases

### Web Applications
- Document processing services
- Image-to-text conversion APIs
- Real-time text extraction

### Desktop Applications
- Document scanning software
- PDF text extraction
- Image analysis tools

### Command-line Tools
- Batch document processing
- Text extraction pipelines
- Data processing workflows

### Embedded Systems
- IoT devices with OCR capabilities
- Mobile applications (via FFI)
- Edge computing solutions

## 📊 Performance Benchmarks

| Feature | Performance | Notes |
|---------|-------------|-------|
| Text Detection | ~50ms per 1024x768 image | Depends on text density |
| Text Recognition | ~10ms per text region | Depends on text length |
| Memory Usage | ~200MB baseline | Varies with image size |
| Concurrent Processing | Linear scaling up to CPU cores | Limited by model loading |

*Benchmark results on Intel i7-10700K, 32GB RAM*

## 🔧 System Requirements

### Minimum Requirements
- **Rust**: 1.70 or later
- **Memory**: 512MB RAM
- **Storage**: 100MB for models
- **OS**: Linux, Windows, macOS

### Recommended Requirements
- **Rust**: 1.75 or later
- **Memory**: 2GB RAM or more
- **Storage**: 500MB for models and cache
- **CPU**: Multi-core processor for parallel processing

### Optional Dependencies
- **fast_image_resize**: For faster image resizing
- **rayon**: For parallel processing (enabled by default)
- **MNN runtime**: For model inference

## 🛠️ Installation Options

### Cargo (Recommended)
```bash
cargo add rust-paddle-ocr
```

### From Source
```bash
git clone https://github.com/zibo-chen/rust-paddle-ocr.git
cd rust-paddle-ocr
cargo build --release
```

### Features
- `default`: Includes fast_image_resize
- `v5`: Enable PaddleOCR v5 model support
- `fast_resize`: Enable fast image resizing optimizations

## 🔗 Related Projects

- **PaddleOCR**: Original Python implementation
- **MNN**: Mobile Neural Network framework
- **Rust Computer Vision**: Other Rust CV libraries

---

**Happy coding with Rust PaddleOCR! 🦀**

If you find this documentation helpful, please consider giving the project a ⭐ on GitHub!