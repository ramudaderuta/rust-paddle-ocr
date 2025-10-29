# Performance Optimization Guide

This guide covers performance optimization techniques and best practices for the Rust PaddleOCR library.

## 🚀 Performance Overview

The Rust PaddleOCR library is designed for high performance with several built-in optimizations:

- **Smart cropping strategies** for memory efficiency
- **Zero-copy operations** where possible
- **Parallel processing** with Rayon
- **Lazy initialization** of model sessions
- **Caching** of frequently accessed data

## Benchmarking

### Running Benchmarks

```bash
# Run all benchmarks
cargo bench

# Run specific benchmark
cargo bench -- bench_metrics

# Generate HTML report
cargo bench -- --output-format html
```

### Key Metrics

- **Memory usage**: Peak and average memory consumption
- **Processing time**: Time per image and per text region
- **Throughput**: Images processed per second
- **Accuracy**: Text recognition accuracy (qualitative)

## Optimization Techniques

### 1. Smart Cropping Strategy

The library automatically selects the optimal cropping strategy based on image size:

```rust
// Automatic strategy selection
pub fn smart_crop(image: &ImageRef, rect: &Rect) -> DynamicImage {
    let crop_area = rect.width() * rect.height();
    let total_area = img_w * img_h;

    if crop_area < total_area / 10 {
        // Small regions: pixel-level copying
        Self::pixel_copy_crop(image, rect)
    } else {
        // Large regions: standard cropping
        Self::standard_crop(image, rect)
    }
}
```

**When to use manually:**
```rust
// Force efficient cropping for known small regions
let texts = OcrEngineManager::process_ocr_efficient(img)?;
```

### 2. Memory Management

#### Zero-Copy References

```rust
// Use ImageRef to avoid unnecessary cloning
let shared_img = Arc::new(img);
let img_ref = ImageRef::from(shared_img);

// Pass reference instead of cloning
let texts = OcrEngineManager::process_ocr_efficient(
    img_ref.as_dynamic_image().clone()
)?;
```

#### Lazy Initialization

```rust
// Sessions are created on first use
session: Option<mnn::Session>,

// Tensor names are cached after first lookup
input_tensor_name: Option<String>,
output_tensor_name: Option<String>,
```

### 3. Parallel Processing

#### Rayon Integration

```rust
// Parallel processing of multiple images
use rayon::prelude::*;

let results: Vec<_> = images
    .par_iter()
    .map(|img| OcrEngineManager::process_ocr(img.clone()))
    .collect::<Result<Vec<_>, _>>()?;
```

#### Worker Thread Model

```rust
// Dedicated worker thread prevents blocking main thread
thread::spawn(move || {
    for request in request_receiver {
        // Process OCR requests sequentially
        match request {
            OcrRequest::ProcessOcr { image, result_sender } => {
                let result = perform_ocr(image);
                let _ = result_sender.send(result);
            }
        }
    }
});
```

## Performance Tuning

### Configuration Optimization

#### Border Size Tuning

```rust
// Smaller border for dense text (faster processing)
OcrEngineManager::initialize_with_config(
    det_model, rec_model, keys,
    5,   // rect_border_size - smaller for speed
    true, // merge_boxes
    2     // merge_threshold
)?;

// Larger border for sparse text (better accuracy)
OcrEngineManager::initialize_with_config(
    det_model, rec_model, keys,
    20,  // rect_border_size - larger for accuracy
    true,
    5     // merge_threshold
)?;
```

#### Score Thresholds

```rust
// Adjust recognition thresholds for speed vs accuracy trade-off
let mut rec = Rec::from_file("rec_model.mnn", "keys.txt")?
    .with_min_score(0.8)      // Higher threshold = faster, less sensitive
    .with_punct_min_score(0.2); // Lower for punctuation
```

### Image Preprocessing

#### Resolution Optimization

```rust
// Resize large images before processing
use image::imageops::FilterType;

fn optimize_image_size(img: DynamicImage) -> DynamicImage {
    let (width, height) = img.dimensions();

    // Resize if too large (maintains aspect ratio)
    if width > 2048 || height > 2048 {
        let scale = 2048.0 / width.max(height) as f32;
        let new_width = (width as f32 * scale) as u32;
        let new_height = (height as f32 * scale) as u32;
        img.resize(new_width, new_height, FilterType::Lanczos3)
    } else {
        img
    }
}
```

#### Format Optimization

```rust
// Convert to optimal format for processing
fn optimize_format(img: DynamicImage) -> DynamicImage {
    // RGB8 is generally faster for OCR processing
    img.to_rgb8().into()
}
```

## Memory Profiling

### Memory Usage Analysis

```rust
// Example memory profiling setup
use std::alloc::{GlobalAlloc, System, Layout};

struct MemoryTracker;

#[global_allocator]
static GLOBAL: MemoryTracker = MemoryTracker;

unsafe impl GlobalAlloc for MemoryTracker {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        println!("Allocating {} bytes", layout.size());
        System.alloc(layout)
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        println!("Deallocating {} bytes", layout.size());
        System.dealloc(ptr, layout)
    }
}
```

### Memory Optimization Tips

1. **Reuse buffers**: Process images in batches to reuse memory
2. **Avoid cloning**: Use references and smart pointers
3. **Clear caches**: Clear tensor caches between large jobs
4. **Monitor leaks**: Use tools like `valgrind` or `heaptrack`

## Performance Comparison

### Standard vs Efficient Processing

```rust
use std::time::Instant;

fn benchmark_processing(img: DynamicImage) -> Result<(), Box<dyn std::error::Error>> {
    // Standard processing
    let start = Instant::now();
    let texts_standard = OcrEngineManager::process_ocr(img.clone())?;
    let time_standard = start.elapsed();

    // Efficient processing
    let start = Instant::now();
    let texts_efficient = OcrEngineManager::process_ocr_efficient(img)?;
    let time_efficient = start.elapsed();

    println!("Standard: {} results in {:?}", texts_standard.len(), time_standard);
    println!("Efficient: {} results in {:?}", texts_efficient.len(), time_efficient);
    println!("Speedup: {:.2}x",
             time_standard.as_secs_f64() / time_efficient.as_secs_f64());

    Ok(())
}
```

### Batch vs Individual Processing

```rust
fn benchmark_batch_processing(images: Vec<DynamicImage>) -> Result<(), Box<dyn std::error::Error>> {
    // Individual processing
    let start = Instant::now();
    let mut individual_results = Vec::new();
    for img in &images {
        individual_results.push(OcrEngineManager::process_ocr(img.clone())?);
    }
    let time_individual = start.elapsed();

    // Batch processing with parallelization
    let start = Instant::now();
    let batch_results: Vec<_> = images
        .par_iter()
        .map(|img| OcrEngineManager::process_ocr(img.clone()))
        .collect::<Result<Vec<_>, _>>()?;
    let time_batch = start.elapsed();

    println!("Individual: {} images in {:?}", images.len(), time_individual);
    println!("Batch: {} images in {:?}", images.len(), time_batch);
    println!("Speedup: {:.2}x",
             time_individual.as_secs_f64() / time_batch.as_secs_f64());

    Ok(())
}
```

## Production Optimization

### Resource Pooling

```rust
use std::sync::Arc;
use parking_lot::Mutex;

struct OcrPool {
    engines: Vec<Arc<Mutex<OcrEngine>>>,
    next_engine: std::sync::atomic::AtomicUsize,
}

impl OcrPool {
    fn new(pool_size: usize) -> Result<Self, OcrError> {
        let mut engines = Vec::new();
        for _ in 0..pool_size {
            let engine = OcrEngine::new(
                "det_model.mnn",
                "rec_model.mnn",
                "keys.txt"
            )?;
            engines.push(Arc::new(Mutex::new(engine)));
        }

        Ok(OcrPool {
            engines,
            next_engine: std::sync::atomic::AtomicUsize::new(0),
        })
    }

    fn process(&self, img: DynamicImage) -> OcrResult<Vec<String>> {
        let index = self.next_engine.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
            % self.engines.len();
        let engine = self.engines[index].lock();
        engine.process_ocr(img)
    }
}
```

### Caching Strategy

```rust
use std::collections::HashMap;
use lru::LruCache;

struct OcrCache {
    cache: LruCache<u64, Vec<String>>,
    next_id: std::sync::atomic::AtomicU64,
}

impl OcrCache {
    fn new(capacity: usize) -> Self {
        OcrCache {
            cache: LruCache::new(capacity),
            next_id: std::sync::atomic::AtomicU64::new(0),
        }
    }

    fn get_or_process<F>(&mut self, img: &DynamicImage, processor: F) -> OcrResult<Vec<String>>
    where
        F: FnOnce() -> OcrResult<Vec<String>>,
    {
        // Simple hash based on dimensions (for demonstration)
        let (w, h) = img.dimensions();
        let key = ((w as u64) << 32) | (h as u64);

        if let Some(cached) = self.cache.get(&key) {
            return Ok(cached.clone());
        }

        let result = processor()?;
        self.cache.put(key, result.clone());
        Ok(result)
    }
}
```

## Monitoring and Metrics

### Performance Metrics

```rust
use std::time::{Duration, Instant};
use std::sync::atomic::{AtomicU64, Ordering};

struct PerformanceMetrics {
    total_requests: AtomicU64,
    total_time: AtomicU64,
    memory_peak: AtomicU64,
}

impl PerformanceMetrics {
    fn new() -> Self {
        PerformanceMetrics {
            total_requests: AtomicU64::new(0),
            total_time: AtomicU64::new(0),
            memory_peak: AtomicU64::new(0),
        }
    }

    fn record_request(&self, duration: Duration) {
        self.total_requests.fetch_add(1, Ordering::Relaxed);
        self.total_time.fetch_add(duration.as_nanos() as u64, Ordering::Relaxed);
    }

    fn get_average_time(&self) -> Duration {
        let requests = self.total_requests.load(Ordering::Relaxed);
        let total_nanos = self.total_time.load(Ordering::Relaxed);

        if requests > 0 {
            Duration::from_nanos(total_nanos / requests)
        } else {
            Duration::ZERO
        }
    }
}
```

### Health Checks

```rust
fn health_check() -> Result<(), OcrError> {
    // Test with a simple image
    let test_img = image::RgbImage::new(100, 100).into();

    match OcrEngineManager::process_ocr(test_img) {
        Ok(_) => {
            println!("✅ OCR engine is healthy");
            Ok(())
        }
        Err(e) => {
            println!("❌ OCR engine health check failed: {}", e);
            Err(e)
        }
    }
}
```

## Best Practices Summary

### Do's
✅ **Initialize once** at application startup
✅ **Use efficient cropping** for large images
✅ **Process in batches** when possible
✅ **Monitor memory usage** in production
✅ **Implement caching** for repeated images
✅ **Use parallel processing** for independent tasks

### Don'ts
❌ **Initialize repeatedly** in loops
❌ **Clone large images** unnecessarily
❌ **Ignore error handling** for performance
❌ **Block main thread** with OCR operations
❌ **Forget resource cleanup**
❌ **Skip profiling** before optimization

### Performance Checklist

- [ ] Engine initialized once at startup
- [ ] Using `process_ocr_efficient()` for large images
- [ ] Images preprocessed to optimal size
- [ ] Memory usage monitored in production
- [ ] Error handling doesn't impact performance
- [ ] Caching implemented for repeated requests
- [ ] Parallel processing used where appropriate
- [ ] Resource pooling implemented for high throughput
- [ ] Performance metrics collected and analyzed
- [ ] Health checks implemented for monitoring

## Troubleshooting Performance Issues

### Common Issues and Solutions

1. **Slow initialization**
   - Cause: Model loading overhead
   - Solution: Initialize once, reuse engine

2. **High memory usage**
   - Cause: Image cloning and large tensors
   - Solution: Use efficient cropping, zero-copy references

3. **Processing bottlenecks**
   - Cause: Sequential processing of many images
   - Solution: Implement parallel processing

4. **Memory leaks**
   - Cause: Improper resource cleanup
   - Solution: Use RAII, monitor with profiling tools

### Performance Debugging Tools

```bash
# Memory profiling
valgrind --tool=massif ./target/release/examples/performance_test

# CPU profiling
perf record ./target/release/examples/performance_test
perf report

# Heap profiling
heaptrack ./target/release/examples/performance_test
```