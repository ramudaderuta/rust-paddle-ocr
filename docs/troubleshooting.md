# Troubleshooting Guide and FAQ

This comprehensive troubleshooting guide covers common issues, error scenarios, and solutions for the Rust PaddleOCR library.

## 🚨 Quick Help Section

### Most Common Issues

| Issue | Quick Fix |
|-------|-----------|
| **"OCR engine not initialized"** | Call `OcrEngineManager::initialize()` before processing |
| **Model loading fails** | Check file paths and permissions |
| **Poor recognition accuracy** | Adjust confidence thresholds and preprocessing |
| **High memory usage** | Use `process_ocr_efficient()` for large images |
| **Slow processing** | Enable `fast_resize` feature and optimize image size |

---

## 📋 Table of Contents

- [Installation Issues](#installation-issues)
- [Model Loading Problems](#model-loading-problems)
- [Runtime Errors](#runtime-errors)
- [Performance Issues](#performance-issues)
- [Accuracy Problems](#accuracy-problems)
- [Memory Issues](#memory-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Integration Problems](#integration-problems)
- [FAQ](#frequently-asked-questions)
- [Debugging Tools](#debugging-tools)

---

## 🔧 Installation Issues

### Issue: Cargo Build Fails

#### Error Message:
```
error: failed to compile `rust-paddle-ocr v1.4.2`
```

#### Common Causes and Solutions:

**1. Missing System Dependencies**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential pkg-config libclang-dev

# macOS
xcode-select --install
brew install llvm

# Windows
# Install Visual Studio Build Tools or Visual Studio Community
```

**2. Rust Version Incompatible**
```bash
# Update Rust to latest stable
rustup update stable
rustup default stable

# Check current version
rustc --version  # Should be 1.70+ for full compatibility
```

**3. Feature Flag Conflicts**
```bash
# Try minimal features
cargo build --no-default-features

# Or with specific features
cargo build --features "fast_resize"
```

### Issue: MNN Framework Not Found

#### Error Message:
```
error: failed to resolve: could not find `mnn` in ` Cargo.toml`
```

#### Solutions:

**1. Check MNN Installation**
```bash
# Verify MNN is installed
find /usr -name "*mnn*" 2>/dev/null
pkg-config --exists mnn && echo "MNN found" || echo "MNN not found"
```

**2. Install MNN Manually**
```bash
# Clone MNN repository
git clone https://github.com/alibaba/MNN.git
cd MNN

# Build MNN
mkdir build && cd build
cmake .. -DMNN_BUILD_CONVERTER=OFF -DMNN_BUILD_TOOLS=OFF
make -j$(nproc)
sudo make install
```

**3. Set Environment Variables**
```bash
export MNN_ROOT=/path/to/mnn/install
export PKG_CONFIG_PATH=$MNN_ROOT/lib/pkgconfig:$PKG_CONFIG_PATH
```

---

## 📦 Model Loading Problems

### Issue: Model Files Not Found

#### Error Message:
```
OcrError::ModelLoadError("Failed to load model: No such file or directory")
```

#### Solutions:

**1. Check File Paths**
```rust
use std::path::Path;

fn validate_model_files(det_path: &str, rec_path: &str, keys_path: &str) -> Result<(), String> {
    if !Path::new(det_path).exists() {
        return Err(format!("Detection model not found: {}", det_path));
    }
    if !Path::new(rec_path).exists() {
        return Err(format!("Recognition model not found: {}", rec_path));
    }
    if !Path::new(keys_path).exists() {
        return Err(format!("Keys file not found: {}", keys_path));
    }
    Ok(())
}

// Usage
validate_model_files("models/det_model.mnn", "models/rec_model.mnn", "models/keys.txt")?;
```

**2. Use Absolute Paths**
```rust
use std::env;

fn get_model_path(model_name: &str) -> String {
    let exe_dir = env::current_exe().unwrap()
        .parent().unwrap()  // Get executable directory
        .to_str().unwrap();

    format!("{}/models/{}", exe_dir, model_name)
}

let det_model = get_model_path("det_model.mnn");
let rec_model = get_model_path("rec_model.mnn");
let keys_file = get_model_path("keys.txt");
```

**3. Bundle Models with Binary**
```rust
// In build.rs
use std::env;
use std::fs;
use std::path::Path;

fn main() {
    println!("cargo:rerun-if-changed=models/");

    // Copy models to output directory
    let out_dir = env::var("OUT_DIR").unwrap();
    let models_dir = Path::new(&out_dir).join("models");

    fs::create_dir_all(&models_dir).unwrap();

    fs::copy("models/det_model.mnn", models_dir.join("det_model.mnn")).unwrap();
    fs::copy("models/rec_model.mnn", models_dir.join("rec_model.mnn")).unwrap();
    fs::copy("models/keys.txt", models_dir.join("keys.txt")).unwrap();
}
```

### Issue: Model Format Incompatible

#### Error Message:
```
MNNError("Invalid model format")
```

#### Solutions:

**1. Verify Model Format**
```bash
# Check file magic bytes
file models/det_model.mnn
# Should show: MNN model data

# Check file size
ls -lh models/*.mnn
# Should be reasonable size (not 0 bytes)
```

**2. Reconvert Models**
```python
# Use MNN converter to reconvert models
from MNN import Express as nn

# Convert detection model
nn.convert(
    'models/det_model.onnx',  # Input format
    'models/det_model.mnn',    # Output format
    quantizeFP16=True          # Optional quantization
)

# Convert recognition model
nn.convert(
    'models/rec_model.onnx',
    'models/rec_model.mnn',
    quantizeFP16=True
)
```

**3. Check Model Compatibility**
```rust
// Test model loading with error details
fn test_model_loading(model_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    match mnn::Interpreter::from_file(model_path) {
        Ok(interpreter) => {
            println!("✅ Model loaded successfully");
            println!("   Input count: {}", interpreter.input_count());
            println!("   Output count: {}", interpreter.output_count());
            Ok(())
        }
        Err(e) => {
            eprintln!("❌ Model loading failed: {}", e);
            Err(e.into())
        }
    }
}
```

---

## ⚡ Runtime Errors

### Issue: "OCR engine not initialized"

#### Error Message:
```
OcrError::EngineError("OCR engine not initialized")
```

#### Solutions:

**1. Initialize Before Use**
```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    // ❌ WRONG: Processing before initialization
    // let texts = OcrEngineManager::process_ocr(img)?;

    // ✅ CORRECT: Initialize first
    OcrEngineManager::initialize("det.mnn", "rec.mnn", "keys.txt")?;

    // Now you can process images
    let img = image::open("document.jpg")?;
    let texts = OcrEngineManager::process_ocr(img)?;

    Ok(())
}
```

**2. Check Initialization Status**
```rust
use once_cell::sync::OnceCell;
use std::sync::{Arc, Mutex};

static ENGINE_INSTANCE: OnceCell<Arc<Mutex<Option<OcrEngine>>>> = OnceCell::new();

fn is_initialized() -> bool {
    ENGINE_INSTANCE.get()
        .map(|engine| engine.lock().unwrap().is_some())
        .unwrap_or(false)
}

fn ensure_initialized() -> OcrResult<()> {
    if !is_initialized() {
        return Err(OcrError::EngineError(
            "OCR engine not initialized. Call initialize() first.".to_string()
        ));
    }
    Ok(())
}
```

**3. Use Lazy Initialization Pattern**
```rust
use std::sync::Once;

static INIT: Once = Once::new();

fn get_ocr_result(img: DynamicImage) -> OcrResult<Vec<String>> {
    INIT.call_once(|| {
        OcrEngineManager::initialize("det.mnn", "rec.mnn", "keys.txt")
            .expect("Failed to initialize OCR engine");
    });

    OcrEngineManager::process_ocr(img)
}
```

### Issue: Thread Safety Errors

#### Error Message:
```
OcrError::ThreadError("Poisoned mutex lock")
```

#### Solutions:

**1. Handle Poisoned Locks**
```rust
use std::sync::{Arc, Mutex};

fn safe_engine_access(engine: &Arc<Mutex<OcrEngine>>) -> OcrResult<Vec<String>> {
    match engine.lock() {
        Ok(guard) => {
            // Safe to use the engine
            guard.process_ocr(img)
        }
        Err(poisoned) => {
            // Recover from poisoned lock
            let engine = poisoned.into_inner();
            eprintln!("⚠️  Recovered from poisoned mutex");
            engine.process_ocr(img)
        }
    }
}
```

**2. Avoid Multiple Initializations**
```rust
use std::sync::atomic::{AtomicBool, Ordering};

static INIT_CALLED: AtomicBool = AtomicBool::new(false);

fn safe_initialize() -> OcrResult<()> {
    if INIT_CALLED.swap(true, Ordering::SeqCst) {
        // Already initialized
        return Ok(());
    }

    // Perform initialization
    OcrEngineManager::initialize("det.mnn", "rec.mnn", "keys.txt")
}
```

### Issue: Image Processing Errors

#### Error Message:
```
OcrError::ImageError("Invalid image format")
```

#### Solutions:

**1. Validate Image Before Processing**
```rust
use image::{DynamicImage, ImageFormat};

fn validate_image(img_path: &str) -> Result<DynamicImage, Box<dyn std::error::Error>> {
    let img = image::open(img_path)?;

    // Check image dimensions
    if img.width() == 0 || img.height() == 0 {
        return Err("Invalid image dimensions".into());
    }

    // Check image format
    match img {
        DynamicImage::ImageRgb8(_) | DynamicImage::ImageRgba8(_) |
        DynamicImage::ImageLuma8(_) | DynamicImage::ImageLumaA8(_) => {
            Ok(img)
        }
        _ => {
            // Convert to supported format
            Ok(img.to_rgb8().into())
        }
    }
}

// Usage
let validated_img = validate_image("document.jpg")?;
let texts = OcrEngineManager::process_ocr(validated_img)?;
```

**2. Handle Corrupted Images**
```rust
fn safe_load_image(path: &str) -> Result<DynamicImage, Box<dyn std::error::Error>> {
    // Try loading with error recovery
    match image::open(path) {
        Ok(img) => Ok(img),
        Err(e) => {
            eprintln!("⚠️  Failed to load {}: {}", path, e);

            // Try alternative loading methods
            if let Ok(bytes) = std::fs::read(path) {
                match image::load_from_memory(&bytes) {
                    Ok(img) => Ok(img),
                    Err(e2) => {
                        eprintln!("❌ Alternative loading also failed: {}", e2);
                        Err(format!("Could not load image {}: {}", path, e).into())
                    }
                }
            } else {
                Err(e.into())
            }
        }
    }
}
```

---

## 🐌 Performance Issues

### Issue: Slow Processing Speed

#### Symptoms:
- Processing takes > 1 second per image
- High CPU usage
- Memory usage keeps growing

#### Solutions:

**1. Use Efficient Processing**
```rust
// For large images (> 1000x1000 pixels)
let texts = OcrEngineManager::process_ocr_efficient(large_image)?;

// For small images, standard processing is fine
let texts = OcrEngineManager::process_ocr(small_image)?;
```

**2. Optimize Image Size**
```rust
fn optimize_image_size(img: DynamicImage) -> DynamicImage {
    let (width, height) = img.dimensions();
    let max_size = 2048; // Adjust based on your needs

    if width > max_size || height > max_size {
        let scale = max_size as f32 / width.max(height) as f32;
        let new_width = (width as f32 * scale) as u32;
        let new_height = (height as f32 * scale) as u32;

        println!("🔧 Resizing image from {}x{} to {}x{}",
                 width, height, new_width, new_height);

        img.resize(new_width, new_height, image::imageops::FilterType::Lanczos3)
    } else {
        img
    }
}

let optimized_img = optimize_image_size(original_img);
let texts = OcrEngineManager::process_ocr(optimized_img)?;
```

**3. Enable Fast Resize Feature**
```toml
# In Cargo.toml
[dependencies]
rust-paddle-ocr = { version = "1.4", features = ["fast_resize"] }
```

**4. Batch Processing Optimization**
```rust
use rayon::prelude::*;

fn process_images_batch(image_paths: Vec<&str>) -> OcrResult<Vec<Vec<String>>> {
    // Process in parallel
    let results: Result<Vec<_>, _> = image_paths
        .par_iter()
        .map(|path| {
            let img = image::open(path)?;
            OcrEngineManager::process_ocr(img)
        })
        .collect();

    results
}
```

### Issue: Memory Leaks

#### Symptoms:
- Memory usage continuously increases
- Out-of-memory errors
- System becomes unresponsive

#### Solutions:

**1. Monitor Memory Usage**
```rust
use std::alloc::{GlobalAlloc, Layout, System};
use std::sync::atomic::{AtomicUsize, Ordering};

struct MemoryTracker;

static ALLOCATED: AtomicUsize = AtomicUsize::new(0);

unsafe impl GlobalAlloc for MemoryTracker {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let ptr = System.alloc(layout);
        if !ptr.is_null() {
            ALLOCATED.fetch_add(layout.size(), Ordering::Relaxed);
        }
        ptr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        System.dealloc(ptr, layout);
        ALLOCATED.fetch_sub(layout.size(), Ordering::Relaxed);
    }
}

#[global_allocator]
static GLOBAL: MemoryTracker = MemoryTracker;

fn print_memory_usage() {
    let allocated = ALLOCATED.load(Ordering::Relaxed);
    println!("📊 Memory allocated: {:.2} MB", allocated as f64 / 1024.0 / 1024.0);
}

// Use in processing
fn process_with_monitoring(img: DynamicImage) -> OcrResult<Vec<String>> {
    println!("Before processing:");
    print_memory_usage();

    let result = OcrEngineManager::process_ocr(img)?;

    println!("After processing:");
    print_memory_usage();

    Ok(result)
}
```

**2. Clear Caches Periodically**
```rust
use std::time::{Duration, Instant};

struct OcrProcessor {
    last_cleanup: Instant,
    cleanup_interval: Duration,
}

impl OcrProcessor {
    fn new() -> Self {
        Self {
            last_cleanup: Instant::now(),
            cleanup_interval: Duration::from_secs(300), // 5 minutes
        }
    }

    fn process_and_cleanup(&mut self, img: DynamicImage) -> OcrResult<Vec<String>> {
        // Check if cleanup is needed
        if self.last_cleanup.elapsed() > self.cleanup_interval {
            self.cleanup();
            self.last_cleanup = Instant::now();
        }

        OcrEngineManager::process_ocr(img)
    }

    fn cleanup(&self) {
        println!("🧹 Performing memory cleanup...");

        // Force garbage collection if using a runtime that supports it
        // Clear any caches
        // Reset model sessions if needed

        println!("✅ Cleanup completed");
    }
}
```

---

## 🎯 Accuracy Problems

### Issue: Poor Text Recognition

#### Symptoms:
- Garbled text output
- Missing characters
- Incorrect character recognition

#### Solutions:

**1. Adjust Confidence Thresholds**
```rust
// Lower threshold for more sensitive detection (may include noise)
let mut rec = Rec::from_file("rec_model.mnn", "keys.txt")?
    .with_min_score(0.3)
    .with_punct_min_score(0.1);

// Higher threshold for more accurate detection (may miss some text)
let mut rec = Rec::from_file("rec_model.mnn", "keys.txt")?
    .with_min_score(0.8)
    .with_punct_min_score(0.5);
```

**2. Optimize Image Preprocessing**
```rust
fn enhance_image_for_ocr(img: DynamicImage) -> DynamicImage {
    use imageproc::contrast::adjust_contrast;
    use imageproc::filter::gaussian_blur_f32;

    // Convert to grayscale
    let gray = img.to_luma8();

    // Enhance contrast
    let enhanced = adjust_contrast(&gray, 1.5);

    // Apply slight blur to reduce noise
    let blurred = gaussian_blur_f32(&enhanced, 0.5);

    DynamicImage::ImageLuma8(blurred)
}

let enhanced_img = enhance_image_for_ocr(original_img);
let texts = OcrEngineManager::process_ocr(enhanced_img)?;
```

**3. Test Different Border Sizes**
```rust
// For dense text (small regions close together)
let det = Det::from_file("det_model.mnn")?
    .with_rect_border_size(5)
    .with_merge_threshold(1);

// For sparse text (large regions far apart)
let det = Det::from_file("det_model.mnn")?
    .with_rect_border_size(25)
    .with_merge_threshold(10);
```

**4. Validate Results**
```rust
fn filter_ocr_results(texts: Vec<String>) -> Vec<String> {
    texts.into_iter()
        .filter(|text| {
            // Remove empty or whitespace-only results
            !text.trim().is_empty() &&
            // Remove results that are too short (likely noise)
            text.trim().len() > 1 &&
            // Remove results with too many special characters
            text.chars().filter(|c| c.is_alphabetic() || c.is_numeric()).count() >
            text.chars().count() / 2
        })
        .collect()
}

let raw_texts = OcrEngineManager::process_ocr(img)?;
let filtered_texts = filter_ocr_results(raw_texts);
```

### Issue: Text Detection Misses Regions

#### Symptoms:
- Some text areas not detected
- Inconsistent detection across similar images
- Detection fails on certain fonts

#### Solutions:

**1. Adjust Detection Parameters**
```rust
// Experiment with different configurations
let configs = vec![
    (10, true, 2),   // Default
    (15, true, 3),   // Larger border
    (5, true, 1),    // Smaller border
    (20, false, 0),  // No merging
];

for (border, merge, threshold) in configs {
    let det = Det::from_file("det_model.mnn")?
        .with_rect_border_size(border)
        .with_merge_boxes(merge)
        .with_merge_threshold(threshold);

    let rects = det.find_text_rect(&img)?;
    println!("Config ({}, {}, {}): {} regions found", border, merge, threshold, rects.len());
}
```

**2. Multi-scale Detection**
```rust
fn multi_scale_detection(img: &DynamicImage) -> OcrResult<Vec<imageproc::rect::Rect>> {
    let scales = vec![1.0, 1.5, 0.8, 2.0];
    let mut all_rects = Vec::new();

    for scale in scales {
        let scaled_img = if scale == 1.0 {
            img.clone()
        } else {
            let new_width = (img.width() as f32 * scale) as u32;
            let new_height = (img.height() as f32 * scale) as u32;
            img.resize(new_width, new_height, image::imageops::FilterType::Lanczos3)
        };

        let mut det = Det::from_file("det_model.mnn")?;
        let rects = det.find_text_rect(&scaled_img)?;

        // Scale rectangles back to original size
        let scaled_rects: Vec<_> = rects.into_iter()
            .map(|mut rect| {
                if scale != 1.0 {
                    rect = imageproc::rect::Rect::at(
                        (rect.left() as f32 / scale) as i32,
                        (rect.top() as f32 / scale) as i32
                    ).of_size(
                        (rect.width() as f32 / scale) as u32,
                        (rect.height() as f32 / scale) as u32
                    );
                }
                rect
            })
            .collect();

        all_rects.extend(scaled_rects);
    }

    // Remove duplicates
    all_rects.sort_by_key(|r| (r.left(), r.top()));
    all_rects.dedup();

    Ok(all_rects)
}
```

---

## 💾 Memory Issues

### Issue: Out of Memory Errors

#### Error Message:
```
OutOfMemoryError: Cannot allocate memory
```

#### Solutions:

**1. Use Efficient Processing Mode**
```rust
// Always use efficient processing for large images
let texts = OcrEngineManager::process_ocr_efficient(img)?;
```

**2. Process in Chunks**
```rust
fn process_large_image_in_chunks(img: &DynamicImage, chunk_size: u32) -> OcrResult<Vec<String>> {
    let (width, height) = img.dimensions();
    let mut all_texts = Vec::new();

    for y in (0..height).step_by(chunk_size as usize) {
        for x in (0..width).step_by(chunk_size as usize) {
            let chunk_width = (x + chunk_size).min(width) - x;
            let chunk_height = (y + chunk_size).min(height) - y;

            let chunk = img.crop(x, y, chunk_width, chunk_height);

            if let Ok(texts) = OcrEngineManager::process_ocr(chunk) {
                all_texts.extend(texts);
            }
        }
    }

    Ok(all_texts)
}
```

**3. Limit Concurrent Processing**
```rust
use std::sync::Semaphore;

const MAX_CONCURRENT_OCR: usize = 2;

fn process_with_limit(images: Vec<DynamicImage>) -> Vec<OcrResult<Vec<String>>> {
    let semaphore = Arc::new(Semaphore::new(MAX_CONCURRENT_OCR));
    let mut handles = Vec::new();

    for img in images {
        let semaphore = Arc::clone(&semaphore);
        let handle = std::thread::spawn(move || {
            let _permit = semaphore.acquire().unwrap();
            OcrEngineManager::process_ocr(img)
        });
        handles.push(handle);
    }

    handles.into_iter().map(|h| h.join().unwrap()).collect()
}
```

---

## 🖥️ Platform-Specific Issues

### Windows

#### Issue: DLL Loading Errors

```rust
// Ensure MNN DLLs are in PATH
fn setup_windows_paths() -> Result<(), String> {
    use std::env;

    let mut paths = env::var("PATH").unwrap_or_default();

    // Add MNN library path
    let mnn_path = "C:\\Program Files\\MNN\\bin";
    if !paths.contains(mnn_path) {
        paths.push(';');
        paths.push_str(mnn_path);
        env::set_var("PATH", paths);
    }

    Ok(())
}
```

#### Issue: Long Path Names

```rust
// Use extended-length paths on Windows
fn get_long_path(path: &str) -> String {
    if path.starts_with("\\\\?\\") {
        path.to_string()
    } else if path.len() > 260 {
        format!("\\\\?\\{}", std::fs::canonicalize(path).unwrap_or_else(|_| path.to_string()))
    } else {
        path.to_string()
    }
}
```

### macOS

#### Issue: MNN Framework Not Found

```bash
# Install MNN via Homebrew
brew install mnn

# Or set DYLD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH
```

### Linux

#### Issue: Library Path Issues

```bash
# Add to /etc/ld.so.conf.d/mnn.conf
echo "/usr/local/lib" | sudo tee /etc/ld.so.conf.d/mnn.conf
sudo ldconfig

# Or set LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

---

## 🔗 Integration Problems

### Web Server Integration

#### Issue: Blocking the Event Loop

```rust
// ❌ BAD: Blocks the web server
#[tokio::main]
async fn main() {
    let app = axum::Router::new()
        .route("/ocr", axum::post(ocr_handler));

    axum::Server::bind(&"0.0.0.0:3000".parse().unwrap())
        .serve(app.into_make_service())
        .await
}

async fn ocr_handler(bytes: Vec<u8>) -> Result<Vec<String>, StatusCode> {
    let img = image::load_from_memory(&bytes).unwrap();
    // This blocks the tokio executor!
    OcrEngineManager::process_ocr(img).map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

// ✅ GOOD: Use blocking thread
async fn ocr_handler(bytes: Vec<u8>) -> Result<Vec<String>, StatusCode> {
    let img = image::load_from_memory(&bytes).unwrap();

    tokio::task::spawn_blocking(move || {
        OcrEngineManager::process_ocr(img)
    })
    .await
    .unwrap()
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}
```

### CLI Integration

#### Issue: Argument Parsing

```rust
use clap::{Arg, Command};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let matches = Command::new("ocr-cli")
        .arg(Arg::new("image")
            .required(true)
            .help("Input image file"))
        .arg(Arg::new("model-dir")
            .long("model-dir")
            .default_value("models")
            .help("Directory containing model files"))
        .get_matches();

    let image_path = matches.get_one::<String>("image").unwrap();
    let model_dir = matches.get_one::<String>("model-dir").unwrap();

    // Construct model paths
    let det_model = format!("{}/det_model.mnn", model_dir);
    let rec_model = format!("{}/rec_model.mnn", model_dir);
    let keys_file = format!("{}/keys.txt", model_dir);

    // Validate files exist
    for path in &[&det_model, &rec_model, &keys_file] {
        if !std::path::Path::new(path).exists() {
            return Err(format!("Model file not found: {}", path).into());
        }
    }

    // Initialize OCR
    OcrEngineManager::initialize(&det_model, &rec_model, &keys_file)?;

    // Process image
    let img = image::open(image_path)?;
    let texts = OcrEngineManager::process_ocr(img)?;

    // Output results
    for text in texts {
        println!("{}", text);
    }

    Ok(())
}
```

---

## 🛠️ Debugging Tools

### Diagnostic Tool

```rust
use std::time::Instant;
use std::path::Path;

pub struct OcrDiagnostics {
    pub model_files_exist: bool,
    pub model_sizes: Vec<(String, u64)>,
    pub image_info: Option<(u32, u32, String)>,
    pub processing_time: Option<std::time::Duration>,
    pub memory_usage: Option<usize>,
    pub error_history: Vec<String>,
}

impl OcrDiagnostics {
    pub fn new() -> Self {
        Self {
            model_files_exist: false,
            model_sizes: Vec::new(),
            image_info: None,
            processing_time: None,
            memory_usage: None,
            error_history: Vec::new(),
        }
    }

    pub fn check_models(&mut self, det_path: &str, rec_path: &str, keys_path: &str) -> &mut Self {
        self.model_files_exist = Path::new(det_path).exists() &&
                                Path::new(rec_path).exists() &&
                                Path::new(keys_path).exists();

        if self.model_files_exist {
            self.model_sizes = vec![
                ("det_model.mnn".to_string(), std::fs::metadata(det_path).unwrap().len()),
                ("rec_model.mnn".to_string(), std::fs::metadata(rec_path).unwrap().len()),
                ("keys.txt".to_string(), std::fs::metadata(keys_path).unwrap().len()),
            ];
        }

        self
    }

    pub fn check_image(&mut self, img_path: &str) -> Result<&mut Self, Box<dyn std::error::Error>> {
        let img = image::open(img_path)?;
        let format = format!("{:?}", img.color());
        self.image_info = Some((img.width(), img.height(), format));
        Ok(self)
    }

    pub fn run_performance_test(&mut self, img_path: &str) -> Result<&mut Self, Box<dyn std::error::Error>> {
        let img = image::open(img_path)?;

        let start = Instant::now();
        let _texts = OcrEngineManager::process_ocr(img)?;
        let duration = start.elapsed();

        self.processing_time = Some(duration);
        Ok(self)
    }

    pub fn generate_report(&self) -> String {
        let mut report = String::new();

        report.push_str("🔍 OCR Diagnostics Report\n");
        report.push_str("========================\n\n");

        // Model status
        report.push_str("📦 Model Files:\n");
        if self.model_files_exist {
            report.push_str("  ✅ All model files found\n");
            for (name, size) in &self.model_sizes {
                report.push_str(&format!("    {}: {:.1} MB\n", name, *size as f64 / 1024.0 / 1024.0));
            }
        } else {
            report.push_str("  ❌ Some model files missing\n");
        }

        // Image info
        if let Some((width, height, format)) = &self.image_info {
            report.push_str(&format!("\n📸 Image Info:\n"));
            report.push_str(&format!("  Size: {}x{}\n", width, height));
            report.push_str(&format!("  Format: {}\n", format));
        }

        // Performance
        if let Some(duration) = &self.processing_time {
            report.push_str(&format!("\n⚡ Performance:\n"));
            report.push_str(&format!("  Processing time: {:?}\n", duration));

            let pixels_per_sec = if let Some((w, h, _)) = self.image_info {
                (w * h) as f64 / duration.as_secs_f64()
            } else {
                0.0
            };
            report.push_str(&format!("  Throughput: {:.0} pixels/sec\n", pixels_per_sec));
        }

        // Errors
        if !self.error_history.is_empty() {
            report.push_str("\n❌ Error History:\n");
            for error in &self.error_history {
                report.push_str(&format!("  - {}\n", error));
            }
        }

        report
    }
}

// Usage example
fn run_diagnostics() -> Result<(), Box<dyn std::error::Error>> {
    let mut diagnostics = OcrDiagnostics::new();

    diagnostics
        .check_models("models/det_model.mnn", "models/rec_model.mnn", "models/keys.txt")
        .check_image("test_image.jpg")?
        .run_performance_test("test_image.jpg")?;

    println!("{}", diagnostics.generate_report());

    Ok(())
}
```

### Logging Configuration

```rust
// Initialize logging for debugging
use log::{info, warn, error, debug};

fn init_logging() {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    info!("🚀 Rust PaddleOCR starting up");
    debug!("Debug logging enabled");
}

// Add logging to OCR operations
fn logged_ocr_processing(img: image::DynamicImage) -> OcrResult<Vec<String>> {
    info!("📸 Processing image: {}x{}", img.width(), img.height());

    let start = std::time::Instant::now();
    let result = OcrEngineManager::process_ocr(img);
    let duration = start.elapsed();

    match &result {
        Ok(texts) => {
            info!("✅ OCR completed in {:?}: {} text regions found", duration, texts.len());
            for (i, text) in texts.iter().enumerate() {
                debug!("  [{}]: \"{}\"", i + 1, text.trim());
            }
        }
        Err(e) => {
            error!("❌ OCR failed after {:?}: {}", duration, e);
        }
    }

    result
}
```
