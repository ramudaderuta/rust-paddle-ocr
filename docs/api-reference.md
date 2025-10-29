# API Reference Documentation

This comprehensive API reference provides detailed documentation for all public APIs, types, and methods in the Rust PaddleOCR library.

## Table of Contents

- [Core Components](#core-components)
- [Engine API](#engine-api)
- [Detection API](#detection-api)
- [Recognition API](#recognition-api)
- [Error Handling](#error-handling)
- [Optimization API](#optimization-api)
- [C API](#c-api)
- [Types and Enums](#types-and-enums)

---

## Core Components

### OcrEngineManager

A thread-safe singleton manager for OCR engine instances. Provides global access to OCR functionality with automatic resource management.

```rust
pub struct OcrEngineManager {
    _private: (),
}
```

#### Methods

##### `initialize`

Initializes the global OCR engine with detection and recognition models.

```rust
pub fn initialize(
    det_model_path: &str,
    rec_model_path: &str,
    keys_path: &str
) -> OcrResult<()>
```

**Parameters:**
- `det_model_path: &str` - Path to the text detection model file (.mnn)
- `rec_model_path: &str` - Path to the text recognition model file (.mnn)
- `keys_path: &str` - Path to the character keys file (.txt)

**Returns:**
- `OcrResult<()>` - Success or error

**Example:**
```rust
use rust_paddle_ocr::OcrEngineManager;

OcrEngineManager::initialize(
    "models/det_model.mnn",
    "models/rec_model.mnn",
    "models/keys.txt"
)?;
```

##### `initialize_with_config`

Initializes the OCR engine with custom configuration parameters.

```rust
pub fn initialize_with_config(
    det_model_path: &str,
    rec_model_path: &str,
    keys_path: &str,
    rect_border_size: u32,
    merge_boxes: bool,
    merge_threshold: i32
) -> OcrResult<()>
```

**Parameters:**
- `det_model_path: &str` - Path to detection model
- `rec_model_path: &str` - Path to recognition model
- `keys_path: &str` - Path to character keys
- `rect_border_size: u32` - Pixels to extend text boxes (default: 10)
- `merge_boxes: bool` - Whether to merge overlapping boxes (default: true)
- `merge_threshold: i32` - Distance threshold for merging (default: 2)

**Example:**
```rust
OcrEngineManager::initialize_with_config(
    "models/det_model.mnn",
    "models/rec_model.mnn",
    "models/keys.txt",
    20,  // Larger border for sparse text
    true,
    5    // Higher merge threshold
)?;
```

##### `process_ocr`

Processes an image and returns recognized text from all detected text regions.

```rust
pub fn process_ocr(image: DynamicImage) -> OcrResult<Vec<String>>
```

**Parameters:**
- `image: DynamicImage` - Input image to process

**Returns:**
- `OcrResult<Vec<String>>` - Vector of recognized text strings

**Performance:** ~50ms per 1024x768 image (varies with text density)

**Example:**
```rust
use image::open;

let img = open("document.jpg")?;
let texts = OcrEngineManager::process_ocr(img)?;
for text in texts {
    println!("{}", text);
}
```

##### `process_ocr_efficient`

Processes an image using memory-efficient cropping strategies for large images.

```rust
pub fn process_ocr_efficient(image: DynamicImage) -> OcrResult<Vec<String>>
```

**Parameters:**
- `image: DynamicImage` - Input image to process

**Returns:**
- `OcrResult<Vec<String>>` - Vector of recognized text strings

**Performance:** 20-40% faster for large images, 50-70% less memory usage

**Example:**
```rust
let img = open("large_document.jpg")?;
let texts = OcrEngineManager::process_ocr_efficient(img)?;
```

##### `get_text_rects`

Returns bounding rectangles for detected text regions without performing recognition.

```rust
pub fn get_text_rects(image: &DynamicImage) -> OcrResult<Vec<imageproc::rect::Rect>>
```

**Parameters:**
- `image: &DynamicImage` - Reference to input image

**Returns:**
- `OcrResult<Vec<Rect>>` - Vector of text region rectangles

**Example:**
```rust
let img = open("document.jpg")?;
let rects = OcrEngineManager::get_text_rects(&img)?;
for (i, rect) in rects.iter().enumerate() {
    println!("Text {}: x={}, y={}, w={}, h={}",
             i, rect.left(), rect.top(), rect.width(), rect.height());
}
```

---

## Engine API

### OcrEngine

Thread-safe OCR engine with actor pattern for concurrent processing.

```rust
pub struct OcrEngine {
    // Private fields managed by actor pattern
}
```

#### Methods

##### `new`

Creates a new OCR engine instance.

```rust
pub fn new(
    det_model_path: &str,
    rec_model_path: &str,
    keys_path: &str
) -> OcrResult<Self>
```

##### `process_ocr`

Processes OCR request (non-blocking, returns via channel).

```rust
pub fn process_ocr(&self, image: DynamicImage) -> OcrResult<Vec<String>>
```

---

## Detection API

### Det

Text detection model using PaddleOCR detection architecture.

```rust
pub struct Det {
    interpreter: Interpreter,
    session: Option<mnn::Session>,
    rect_border_size: u32,
    merge_boxes: bool,
    merge_threshold: i32,
    // Performance optimization fields
    input_tensor_name: Option<String>,
    output_tensor_name: Option<String>,
    last_input_shape: Option<[i32; 4]>,
}
```

#### Methods

##### `from_file`

Creates a detection model from file.

```rust
pub fn from_file(model_path: &str) -> OcrResult<Self>
```

**Parameters:**
- `model_path: &str` - Path to .mnn detection model

**Returns:**
- `OcrResult<Det>` - Detection model instance

##### `with_rect_border_size`

Sets the border size extension for text boxes.

```rust
pub fn with_rect_border_size(mut self, border_size: u32) -> Self
```

**Chainable:** Yes

**Example:**
```rust
let det = Det::from_file("det_model.mnn")?
    .with_rect_border_size(20);
```

##### `with_merge_boxes`

Enables or disables box merging.

```rust
pub fn with_merge_boxes(mut self, merge: bool) -> Self
```

##### `with_merge_threshold`

Sets the distance threshold for merging boxes.

```rust
pub fn with_merge_threshold(mut self, threshold: i32) -> Self
```

##### `find_text_rect`

Detects text regions and returns bounding rectangles.

```rust
pub fn find_text_rect(&mut self, image: &DynamicImage) -> OcrResult<Vec<imageproc::rect::Rect>>
```

**Performance:** ~30ms for 1024x768 image

**Algorithm:** DBNet++ text detection with post-processing

##### `find_text_img`

Detects text regions and returns cropped text images.

```rust
pub fn find_text_img(&mut self, image: &DynamicImage) -> OcrResult<Vec<DynamicImage>>
```

**Returns:** Vector of cropped text images ready for recognition

---

## Recognition API

### Rec

Text recognition model using CRNN (CNN+RNN+CTC) architecture.

```rust
pub struct Rec {
    interpreter: Interpreter,
    session: Option<mnn::Session>,
    keys: Vec<char>,
    min_score: f32,
    punct_min_score: f32,
    #[cfg(feature = "fast_resize")]
    resizer: fast_image_resize::Resizer,
}
```

#### Methods

##### `from_file`

Creates a recognition model from file.

```rust
pub fn from_file(model_path: &str, keys_path: &str) -> OcrResult<Self>
```

**Parameters:**
- `model_path: &str` - Path to .mnn recognition model
- `keys_path: &str` - Path to character keys file

**Character Set:** Supports customizable character dictionaries

##### `with_min_score`

Sets the minimum confidence score for character recognition.

```rust
pub fn with_min_score(mut self, min_score: f32) -> Self
```

**Default:** 0.5

**Range:** 0.0 to 1.0

**Example:**
```rust
let rec = Rec::from_file("rec_model.mnn", "keys.txt")?
    .with_min_score(0.8);  // Higher confidence requirement
```

##### `with_punct_min_score`

Sets the minimum score for punctuation recognition.

```rust
pub fn with_punct_min_score(mut self, min_score: f32) -> Self
```

**Default:** 0.2

**Purpose:** Lower threshold for punctuation (less confident than characters)

##### `predict_str`

Recognizes text from an image.

```rust
pub fn predict_str(&mut self, image: &DynamicImage) -> OcrResult<String>
```

**Parameters:**
- `image: &DynamicImage` - Text region image (typically from detection)

**Returns:**
- `OcrResult<String>` - Recognized text string

**Performance:** ~10ms per text region

**Input Requirements:**
- Height: 32-64 pixels (auto-resized)
- Width: Variable, maintains aspect ratio
- Format: RGB/Grayscale supported

---

## Error Handling

### OcrError

Comprehensive error type for all OCR operations.

```rust
#[derive(Error, Debug)]
pub enum OcrError {
    #[error("IO error: {0}")]
    IOError(#[from] std::io::Error),

    #[error("Image processing error: {0}")]
    ImageError(#[from] image::ImageError),

    #[error("Command line argument error: {0}")]
    ArgError(String),

    #[error("JSON error: {0}")]
    JsonError(String),

    #[error("MNN error: {0}")]
    MNNError(#[from] mnn::MNNError),

    #[error("Shape error: {0}")]
    ShapeError(#[from] ndarray::ShapeError),

    #[error("Input tensor data error: {0}")]
    InputError(String),

    #[error("Output tensor data error: {0}")]
    OutputError(String),

    #[error("Model inference error: {0}")]
    InferenceError(String),

    #[error("Engine error: {0}")]
    EngineError(String),

    #[error("Thread error: {0}")]
    ThreadError(String),

    #[cfg(feature="fast_resize")]
    #[error("Image resize error: {0}")]
    ResizeError(#[from] fast_image_resize::ResizeError),
}
```

### OcrResult

Result type alias for OCR operations.

```rust
pub type OcrResult<T> = Result<T, OcrError>;
```

#### Error Handling Patterns

**Basic Error Handling:**
```rust
match OcrEngineManager::process_ocr(img) {
    Ok(texts) => {
        for text in texts {
            println!("{}", text);
        }
    }
    Err(e) => {
        eprintln!("OCR failed: {}", e);
        // Handle specific error types
        match e {
            OcrError::ModelLoadError(msg) => {
                eprintln!("Model loading failed: {}", msg);
            }
            OcrError::InferenceError(msg) => {
                eprintln!("Inference failed: {}", msg);
            }
            _ => {
                eprintln!("Other error: {}", e);
            }
        }
    }
}
```

**Error Propagation:**
```rust
fn process_document(path: &str) -> OcrResult<Vec<String>> {
    let img = image::open(path)?;  // Converts ImageError to OcrError
    let texts = OcrEngineManager::process_ocr(img)?;
    Ok(texts)
}
```

---

## Optimization API

### EfficientCropper

Performance optimization utilities for memory-efficient image processing.

```rust
pub struct EfficientCropper;
```

#### Methods

##### `smart_crop`

Automatically selects optimal cropping strategy based on region size.

```rust
pub fn smart_crop(image: &ImageRef, rect: &Rect) -> DynamicImage
```

**Strategy Selection:**
- Small regions (< 10% of image): Pixel-level copying
- Large regions (≥ 10%): Standard image cropping

**Performance Benefits:**
- Small regions: ~70% faster processing
- Memory usage: ~50% reduction for large images

##### `pixel_copy_crop`

Efficient pixel-by-pixel copying for small regions.

```rust
pub fn pixel_copy_crop(image: &ImageRef, rect: &Rect) -> DynamicImage
```

##### `standard_crop`

Standard image cropping using image crate.

```rust
pub fn standard_crop(image: &ImageRef, rect: &Rect) -> DynamicImage
```

### ImageRef

Zero-copy image reference wrapper for memory efficiency.

```rust
pub enum ImageRef {
    Owned(DynamicImage),
    Shared(Arc<DynamicImage>),
}
```

#### Methods

##### `from`

Creates ImageRef from various image types.

```rust
impl From<DynamicImage> for ImageRef
impl From<Arc<DynamicImage>> for ImageRef
```

##### `as_dynamic_image`

Returns reference to underlying DynamicImage.

```rust
pub fn as_dynamic_image(&self) -> &DynamicImage
```

---

## C API

### C Functions

FFI interface for C/C++ integration.

#### `ocr_engine_manager_initialize`

```c
int32_t ocr_engine_manager_initialize(
    const char* det_model_path,
    const char* rec_model_path,
    const char* keys_path
);
```

**Returns:** 0 on success, non-zero error code

#### `ocr_engine_manager_process_ocr`

```c
int32_t ocr_engine_manager_process_ocr(
    uint8_t* image_data,
    int32_t width,
    int32_t height,
    int32_t channels,
    char*** results,
    int32_t* result_count
);
```

**Parameters:**
- `image_data: uint8_t*` - Raw image data
- `width: int32_t` - Image width
- `height: int32_t` - Image height
- `channels: int32_t` - Number of channels (1/3/4)
- `results: char***` - Output array of recognized strings
- `result_count: int32_t*` - Number of results

**Memory Management:** Caller must free results array

#### `ocr_engine_manager_free_results`

```c
void ocr_engine_manager_free_results(char** results, int32_t count);
```

---

## Types and Enums

### OcrRequest (Internal)

Message types for actor pattern communication.

```rust
pub enum OcrRequest {
    DetectText {
        image: DynamicImage,
        result_sender: Sender<OcrResult<Vec<DynamicImage>>>
    },
    RecognizeText {
        image: DynamicImage,
        result_sender: Sender<OcrResult<String>>
    },
    ProcessOcr {
        image: DynamicImage,
        result_sender: Sender<OcrResult<Vec<String>>>
    },
    GetTextRects {
        image: DynamicImage,
        result_sender: Sender<OcrResult<Vec<imageproc::rect::Rect>>>
    },
    Shutdown,
}
```

### Configuration Constants

```rust
// Default configuration values
pub const DEFAULT_RECT_BORDER_SIZE: u32 = 10;
pub const DEFAULT_MERGE_THRESHOLD: i32 = 2;
pub const DEFAULT_MIN_SCORE: f32 = 0.5;
pub const DEFAULT_PUNCT_MIN_SCORE: f32 = 0.2;

// Performance thresholds
pub const SMALL_REGION_THRESHOLD: f32 = 0.1;  // 10% of total image area
```

### Feature Flags

```toml
[features]
default = ["fast_image_resize"]
fast_resize = ["dep:fast_image_resize"]
v5 = []  # Enable PaddleOCR v5 model support
```

---

## Performance Characteristics

### Benchmarks

| Operation | Input Size | Time | Memory |
|-----------|------------|------|--------|
| Text Detection | 1024x768 | ~30ms | ~50MB |
| Text Recognition | 32x200 | ~10ms | ~20MB |
| Full OCR Pipeline | 1024x768 | ~50ms | ~200MB |
| Efficient Processing | 1024x768 | ~35ms | ~100MB |

*Results on Intel i7-10700K, 32GB RAM*

### Memory Usage

- **Baseline**: ~200MB (models loaded)
- **Per Image**: +50-100MB during processing
- **Efficient Mode**: -50% memory for large images
- **Concurrent**: +200MB per additional thread

### Scalability

- **Single Thread**: 20 images/second
- **Multi-thread**: Linear scaling up to CPU cores
- **Batch Processing**: 2-3x throughput improvement

---

## Usage Patterns

### Basic Usage Pattern

```rust
// 1. Initialize once
OcrEngineManager::initialize("det.mnn", "rec.mnn", "keys.txt")?;

// 2. Process multiple images
for image_path in image_paths {
    let img = image::open(image_path)?;
    let texts = OcrEngineManager::process_ocr(img)?;
    // Process results...
}
```

### High-Performance Pattern

```rust
// 1. Initialize with custom config
OcrEngineManager::initialize_with_config(
    "det.mnn", "rec.mnn", "keys.txt",
    15, true, 3
)?;

// 2. Use efficient processing for large images
let texts = OcrEngineManager::process_ocr_efficient(large_image)?;
```

### Advanced Pattern

```rust
// 1. Direct model access for fine control
let mut det = Det::from_file("det.mnn")?
    .with_rect_border_size(20)
    .with_merge_boxes(true);

let mut rec = Rec::from_file("rec.mnn", "keys.txt")?
    .with_min_score(0.8);

// 2. Step-by-step processing
let rects = det.find_text_rect(&img)?;
let text_images = det.find_text_img(&img)?;

for (i, text_img) in text_images.into_iter().enumerate() {
    let text = rec.predict_str(&text_img)?;
    println!("Region {}: {}", i, text);
}
```

---

## Integration Examples

### Web Server Integration

```rust
use axum::{extract::Multipart, Json};

async fn ocr_endpoint(mut multipart: Multipart) -> Result<Vec<String>, StatusCode> {
    while let Some(field) = multipart.next_field().await.unwrap() {
        if field.name().unwrap() == "image" {
            let bytes = field.bytes().await.unwrap();
            let img = image::load_from_memory(&bytes).unwrap();

            match OcrEngineManager::process_ocr(img) {
                Ok(texts) => return Ok(Json(texts)),
                Err(_) => return Err(StatusCode::INTERNAL_SERVER_ERROR),
            }
        }
    }
    Err(StatusCode::BAD_REQUEST)
}
```

### CLI Integration

```rust
use clap::{Arg, Command};

let matches = Command::new("ocr-cli")
    .arg(Arg::new("image").required(true))
    .arg(Arg::new("efficient").long("efficient"))
    .get_matches();

let img = image::open(matches.get_one::<String>("image").unwrap())?;
let texts = if matches.get_flag("efficient") {
    OcrEngineManager::process_ocr_efficient(img)?
} else {
    OcrEngineManager::process_ocr(img)?
};

for text in texts {
    println!("{}", text);
}
```

---

## Troubleshooting

### Common Issues

**Model Loading Fails:**
- Check file paths and permissions
- Verify model file integrity
- Ensure MNN runtime is available

**Poor Recognition Accuracy:**
- Adjust `min_score` threshold
- Try different `rect_border_size` values
- Preprocess images (contrast, brightness)

**High Memory Usage:**
- Use `process_ocr_efficient()`
- Process images in smaller batches
- Clear model cache between jobs

**Slow Processing:**
- Enable `fast_resize` feature
- Use multi-threaded processing
- Optimize image resolution before processing

### Performance Tuning

```rust
// For speed (lower accuracy)
let rec = Rec::from_file("rec.mnn", "keys.txt")?
    .with_min_score(0.3);

// For accuracy (slower)
let rec = Rec::from_file("rec.mnn", "keys.txt")?
    .with_min_score(0.8);

// For dense text
let det = Det::from_file("det.mnn")?
    .with_rect_border_size(5)
    .with_merge_threshold(1);

// For sparse text
let det = Det::from_file("det.mnn")?
    .with_rect_border_size(25)
    .with_merge_threshold(10);
```

---

## Version History

### v1.4.2 (Current)
- Added efficient cropping strategies
- Improved memory management
- Enhanced error handling
- C API stability improvements

### v1.4.0
- Actor pattern implementation
- Thread-safe singleton manager
- Performance optimizations
- Multi-threading support

### v1.3.0
- MNN framework integration
- Fast image resize support
- Configuration improvements

---

## License and Support

- **License**: Apache License 2.0
- **Repository**: https://github.com/zibo-chen/rust-paddle-ocr
- **Issues**: https://github.com/zibo-chen/rust-paddle-ocr/issues
- **Documentation**: https://docs.rs/rust-paddle-ocr/

---

*This API reference is automatically generated from source code analysis and stays synchronized with the latest library version.*