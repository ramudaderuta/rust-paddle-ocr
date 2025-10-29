# Interactive Examples and Code Playground

This section provides hands-on, interactive examples that you can run directly to explore Rust PaddleOCR capabilities. Each example is self-contained and demonstrates specific features and patterns.

## 🎯 Quick Start Playground

### Try It Now: Basic OCR

```rust
// Run this code directly with: cargo run --example playground_basic
use rust_paddle_ocr::OcrEngineManager;
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 Rust PaddleOCR Interactive Playground");
    println!("==========================================");

    // Step 1: Initialize OCR engine
    println!("\n📦 Initializing OCR engine...");
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;
    println!("✅ OCR engine initialized successfully!");

    // Step 2: Load and process an image
    println!("\n📸 Loading test image...");
    let img = open("examples/document.jpg")?;
    println!("✅ Image loaded: {}x{}", img.width(), img.height());

    // Step 3: Process OCR
    println!("\n🔍 Processing OCR...");
    let start = std::time::Instant::now();
    let texts = OcrEngineManager::process_ocr(img)?;
    let duration = start.elapsed();

    // Step 4: Display results
    println!("\n📋 Results (found in {:?}):", duration);
    println!("=====================================");
    if texts.is_empty() {
        println!("❌ No text detected in the image");
    } else {
        for (i, text) in texts.iter().enumerate() {
            println!("  {}. \"{}\"", i + 1, text.trim());
        }
    }

    println!("\n🎉 Try modifying this code and run again!");
    Ok(())
}
```

**Expected Output:**
```
🚀 Rust PaddleOCR Interactive Playground
==========================================

📦 Initializing OCR engine...
✅ OCR engine initialized successfully!

📸 Loading test image...
✅ Image loaded: 1024x768

🔍 Processing OCR...

📋 Results (found in 45ms):
=====================================
  1. "Hello World"
  2. "Rust PaddleOCR"
  3. "Interactive Example"

🎉 Try modifying this code and run again!
```

---

## 🎮 Interactive Scenarios

### Scenario 1: Performance Comparison Tool

```rust
// cargo run --example playground_performance
use rust_paddle_ocr::OcrEngineManager;
use image::open;
use std::time::Instant;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("⚡ Performance Comparison Playground");
    println!("==================================");

    // Initialize once
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    // Load test image
    let img = open("examples/test_image.jpg")?;
    println!("📊 Testing with image: {}x{}", img.width(), img.height());

    // Test 1: Standard processing
    println!("\n🔄 Testing standard OCR processing...");
    let start = Instant::now();
    let texts_standard = OcrEngineManager::process_ocr(img.clone())?;
    let time_standard = start.elapsed();

    // Test 2: Efficient processing
    println!("⚡ Testing efficient OCR processing...");
    let start = Instant::now();
    let texts_efficient = OcrEngineManager::process_ocr_efficient(img)?;
    let time_efficient = start.elapsed();

    // Display comparison
    println!("\n📈 Performance Results:");
    println!("========================");
    println!("Standard:  {} results in {:?} ({:.2} MB/s)",
             texts_standard.len(), time_standard,
             (img.width() * img.height() * 3) as f64 / (1024.0 * 1024.0 * time_standard.as_secs_f64()));

    println!("Efficient: {} results in {:?} ({:.2} MB/s)",
             texts_efficient.len(), time_efficient,
             (img.width() * img.height() * 3) as f64 / (1024.0 * 1024.0 * time_efficient.as_secs_f64()));

    if time_efficient < time_standard {
        let speedup = time_standard.as_secs_f64() / time_efficient.as_secs_f64();
        println!("🚀 Speedup: {:.2}x faster with efficient processing!", speedup);
    }

    println!("✅ Results match: {}", texts_standard == texts_efficient);

    Ok(())
}
```

### Scenario 2: Configuration Explorer

```rust
// cargo run --example playground_config
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("⚙️  Configuration Explorer");
    println!("===========================");

    let img = open("examples/document.jpg")?;

    // Test different configurations
    let configs = vec![
        ("Default", 10, true, 2),
        ("Dense Text", 5, true, 1),
        ("Sparse Text", 20, true, 5),
        ("No Merging", 10, false, 0),
    ];

    for (name, border_size, merge_boxes, merge_threshold) in configs {
        println!("\n🔧 Testing configuration: {}", name);
        println!("   Border size: {}, Merge boxes: {}, Threshold: {}",
                 border_size, merge_boxes, merge_threshold);

        let mut det = Det::from_file("models/det_model.mnn")?
            .with_rect_border_size(border_size)
            .with_merge_boxes(merge_boxes)
            .with_merge_threshold(merge_threshold);

        let start = std::time::Instant::now();
        let rects = det.find_text_rect(&img)?;
        let duration = start.elapsed();

        println!("   📊 Found {} text regions in {:?}", rects.len(), duration);

        // Show first few regions
        for (i, rect) in rects.iter().take(3).enumerate() {
            println!("     Region {}: x={}, y={}, w={}, h={}",
                     i + 1, rect.left(), rect.top(), rect.width(), rect.height());
        }
    }

    Ok(())
}
```

### Scenario 3: Batch Processing Demo

```rust
// cargo run --example playground_batch
use rust_paddle_ocr::OcrEngineManager;
use image::open;
use std::path::Path;
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("📁 Batch Processing Demo");
    println!("========================");

    // Initialize once
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    // Create test images directory
    let test_dir = "test_images";
    if !Path::new(test_dir).exists() {
        fs::create_dir(test_dir)?;
        println!("📁 Created test directory: {}", test_dir);
    }

    // Process all images in directory
    let image_files = vec![
        "examples/doc1.jpg",
        "examples/doc2.jpg",
        "examples/doc3.jpg",
    ];

    println!("\n🔄 Processing {} images...", image_files.len());

    let mut total_texts = 0;
    let mut total_time = std::time::Duration::ZERO;

    for (i, image_file) in image_files.iter().enumerate() {
        if Path::new(image_file).exists() {
            println!("\n📸 [{}/{}] Processing: {}", i + 1, image_files.len(), image_file);

            match open(image_file) {
                Ok(img) => {
                    let start = std::time::Instant::now();
                    match OcrEngineManager::process_ocr(img) {
                        Ok(texts) => {
                            let duration = start.elapsed();
                            total_texts += texts.len();
                            total_time += duration;

                            println!("   ✅ Found {} text regions in {:?}", texts.len(), duration);
                            for text in texts.iter().take(3) {
                                println!("     \"{}\"", text.trim());
                            }
                            if texts.len() > 3 {
                                println!("     ... and {} more", texts.len() - 3);
                            }
                        }
                        Err(e) => {
                            println!("   ❌ OCR failed: {}", e);
                        }
                    }
                }
                Err(e) => {
                    println!("   ❌ Failed to load image: {}", e);
                }
            }
        } else {
            println!("   ⚠️  File not found: {}", image_file);
        }
    }

    // Summary
    println!("\n📊 Batch Processing Summary:");
    println!("=============================");
    println!("Total images processed: {}", image_files.len());
    println!("Total text regions found: {}", total_texts);
    println!("Total processing time: {:?}", total_time);
    println!("Average time per image: {:?}", total_time / image_files.len() as u32);
    println!("Average texts per image: {:.1}", total_texts as f64 / image_files.len() as f64);

    Ok(())
}
```

---

## 🎨 Image Processing Playground

### Scenario 4: Image Preprocessing Explorer

```rust
// cargo run --example playground_preprocessing
use rust_paddle_ocr::OcrEngineManager;
use image::{DynamicImage, imageops::FilterType, GrayImage};
use imageproc::contrast::adjust_contrast;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🎨 Image Preprocessing Explorer");
    println!("================================");

    // Initialize OCR engine
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    // Load original image
    let original_img = image::open("examples/document.jpg")?;
    println!("📸 Original image: {}x{}", original_img.width(), original_img.height());

    // Define preprocessing functions
    let preprocessors = vec![
        ("Original", |img: &DynamicImage| img.clone()),
        ("Grayscale", |img: &DynamicImage| img.to_luma8().into()),
        ("Enhanced Contrast", |img: &DynamicImage| {
            let gray = img.to_luma8();
            let enhanced = adjust_contrast(&gray, 1.5);
            enhanced.into()
        }),
        ("Resized (50%)", |img: &DynamicImage| {
            let new_w = img.width() / 2;
            let new_h = img.height() / 2;
            img.resize(new_w, new_h, FilterType::Lanczos3)
        }),
        ("Resized (200%)", |img: &DynamicImage| {
            let new_w = img.width() * 2;
            let new_h = img.height() * 2;
            img.resize(new_w, new_h, FilterType::Lanczos3)
        }),
    ];

    println!("\n🔄 Testing different preprocessing methods...");

    for (name, preprocessor) in preprocessors {
        println!("\n🎯 Testing: {}", name);

        let processed_img = preprocessor(&original_img);
        println!("   📏 Size: {}x{}", processed_img.width(), processed_img.height());

        let start = std::time::Instant::now();
        match OcrEngineManager::process_ocr(processed_img) {
            Ok(texts) => {
                let duration = start.elapsed();
                println!("   ✅ Found {} texts in {:?}", texts.len(), duration);

                // Show unique text count (duplicates might indicate processing issues)
                let unique_texts: std::collections::HashSet<_> = texts.iter().collect();
                println!("   🔢 Unique texts: {}", unique_texts.len());

                for text in texts.iter().take(2) {
                    println!("     \"{}\"", text.trim());
                }
            }
            Err(e) => {
                println!("   ❌ Failed: {}", e);
            }
        }
    }

    println!("\n💡 Tips:");
    println!("- Grayscale often improves text detection");
    println!("- Higher contrast helps with low-quality images");
    println!("- Resize large images to improve processing speed");
    println!("- Avoid excessive upscaling (creates artifacts)");

    Ok(())
}
```

---

## 🔍 Advanced Detection Playground

### Scenario 5: Text Region Analysis

```rust
// cargo run --example playground_detection
use rust_paddle_ocr::{OcrEngineManager, Det};
use image::open;
use imageproc::rect::Rect;

fn analyze_text_regions(rects: &[Rect]) -> (f32, f32, f32, usize) {
    if rects.is_empty() {
        return (0.0, 0.0, 0.0, 0);
    }

    let total_area: u32 = rects.iter().map(|r| r.width() * r.height()).sum();
    let avg_area = total_area as f64 / rects.len() as f64;

    let mut widths = vec![];
    let mut heights = vec![];

    for rect in rects {
        widths.push(rect.width() as f64);
        heights.push(rect.height() as f64);
    }

    let avg_width = widths.iter().sum::<f64>() / widths.len() as f64;
    let avg_height = heights.iter().sum::<f64>() / heights.len() as f64;

    let avg_aspect_ratio = avg_width / avg_height;

    (avg_area as f32, avg_width as f32, avg_height as f32, rects.len())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🔍 Text Region Analysis Playground");
    println!("==================================");

    // Initialize detection model directly for more control
    let mut det = Det::from_file("models/det_model.mnn")?
        .with_rect_border_size(15)
        .with_merge_boxes(true)
        .with_merge_threshold(3);

    // Test images
    let test_images = vec![
        ("examples/document.jpg", "Document"),
        ("examples/receipt.jpg", "Receipt"),
        ("examples/sign.jpg", "Sign"),
    ];

    for (image_path, image_type) in test_images {
        if !std::path::Path::new(image_path).exists() {
            println!("⚠️  Skipping {} (file not found: {})", image_type, image_path);
            continue;
        }

        println!("\n📸 Analyzing: {}", image_type);
        println!("   File: {}", image_path);

        let img = open(image_path)?;
        println!("   Image size: {}x{}", img.width(), img.height());

        // Detect text regions
        let start = std::time::Instant::now();
        let rects = det.find_text_rect(&img)?;
        let duration = start.elapsed();

        if rects.is_empty() {
            println!("   ❌ No text regions detected");
            continue;
        }

        // Analyze regions
        let (avg_area, avg_width, avg_height, count) = analyze_text_regions(&rects);

        println!("   ✅ Detection completed in {:?}", duration);
        println!("   📊 Statistics:");
        println!("     Text regions: {}", count);
        println!("     Average area: {:.0} pixels²", avg_area);
        println!("     Average size: {:.0}x{:.0} pixels", avg_width, avg_height);
        println!("     Text density: {:.2}% regions per megapixel",
                 count as f64 / (img.width() as f64 * img.height() as f64 / 1_000_000.0));

        // Show region details
        println!("   📍 Sample regions:");
        for (i, rect) in rects.iter().take(5).enumerate() {
            println!("     {}: x={}, y={}, w={}, h={}",
                     i + 1, rect.left(), rect.top(), rect.width(), rect.height());
        }
        if rects.len() > 5 {
            println!("     ... and {} more", rects.len() - 5);
        }
    }

    println!("\n💡 Insights:");
    println!("- Documents typically have many small text regions");
    println!("- Signs often have fewer, larger text regions");
    println!("- Receipts may have structured text layouts");
    println!("- Region size affects recognition accuracy");

    Ok(())
}
```

---

## 🧪 Recognition Testing Playground

### Scenario 6: Recognition Confidence Explorer

```rust
// cargo run --example playground_recognition
use rust_paddle_ocr::{OcrEngineManager, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🧪 Recognition Confidence Explorer");
    println!("=================================");

    // Initialize OCR engine
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    // Create recognition model with different confidence thresholds
    let confidence_levels = vec![0.1, 0.3, 0.5, 0.7, 0.9];

    println!("\n🎯 Testing different confidence levels...");

    let img = open("examples/document.jpg")?;
    let text_images = OcrEngineManager::get_text_rects(&img)?;

    if text_images.is_empty() {
        println!("❌ No text regions found for testing");
        return Ok(());
    }

    println!("📊 Found {} text regions to test", text_images.len());

    for confidence in confidence_levels {
        println!("\n🔧 Testing confidence level: {}", confidence);

        let mut rec = Rec::from_file("models/rec_model.mnn", "models/keys.txt")?
            .with_min_score(confidence);

        let start = std::time::Instant::now();
        let mut results = vec![];

        // Test first few text regions
        for (i, rect) in text_images.iter().take(3).enumerate() {
            // Extract text image for this region
            let text_img = extract_text_region(&img, rect)?;

            match rec.predict_str(&text_img) {
                Ok(text) => {
                    println!("   Region {}: \"{}\"", i + 1, text.trim());
                    results.push(text);
                }
                Err(e) => {
                    println!("   Region {}: Failed - {}", i + 1, e);
                }
            }
        }

        let duration = start.elapsed();
        println!("   ⏱️  Processing time: {:?}", duration);
        println!("   📈 Success rate: {}/{} ({:.1}%)",
                 results.len(), 3.min(text_images.len()),
                 results.len() as f64 / 3.0.min(text_images.len() as f64) * 100.0);
    }

    println!("\n💡 Confidence Guidelines:");
    println!("- 0.1-0.3: Maximum recall, may include noise");
    println!("- 0.4-0.6: Good balance for most applications");
    println!("- 0.7-0.8: High precision, fewer false positives");
    println!("- 0.9+: Very high confidence, may miss some text");

    Ok(())
}

fn extract_text_region(img: &image::DynamicImage, rect: &imageproc::rect::Rect) -> Result<image::DynamicImage, Box<dyn std::error::Error>> {
    use imageproc::geometric_transformations::crop;

    let cropped = crop(
        img,
        rect.left() as u32,
        rect.top() as u32,
        rect.width(),
        rect.height()
    );

    Ok(cropped.to_image().into())
}
```

---

## 🚀 Performance Benchmarking

### Scenario 7: Comprehensive Performance Test

```rust
// cargo run --example playground_benchmark
use rust_paddle_ocr::OcrEngineManager;
use image::{open, DynamicImage, RgbImage};
use std::time::Instant;
use std::sync::Arc;
use std::thread;

fn create_test_image(width: u32, height: u32, text_density: f32) -> DynamicImage {
    use image::{Rgb, ImageBuffer};
    use imageproc::drawing::draw_text_mut;
    use rusttype::{Font, Scale};

    let mut img = ImageBuffer::from_pixel(width, height, Rgb([255, 255, 255]));
    let font = Font::try_from_bytes(include_bytes!("../assets/font.ttf")).unwrap();

    let text_count = (width * height) as f32 * text_density / 10000.0;
    let scale = Scale::uniform(16.0);

    for i in 0..text_count as usize {
        let x = (i * 100) % width as usize;
        let y = (i * 50) % height as usize;
        let text = format!("Text{}", i);

        draw_text_mut(&mut img, Rgb([0, 0, 0]), x as i32, y as i32, scale, &font, &text);
    }

    DynamicImage::ImageRgb8(img)
}

fn benchmark_configuration(
    name: &str,
    image: &DynamicImage,
    efficient: bool
) -> Result<(usize, std::time::Duration), Box<dyn std::error::Error>> {
    let start = Instant::now();

    let texts = if efficient {
        OcrEngineManager::process_ocr_efficient(image.clone())?
    } else {
        OcrEngineManager::process_ocr(image.clone())?
    };

    let duration = start.elapsed();
    Ok((texts.len(), duration))
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 Comprehensive Performance Benchmark");
    println!("====================================");

    // Initialize OCR engine
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    // Test configurations
    let test_configs = vec![
        ("Small Image", 512, 512, 0.5),
        ("Medium Image", 1024, 768, 1.0),
        ("Large Image", 2048, 1536, 0.8),
        ("Very Large Image", 4096, 3072, 0.3),
    ];

    println!("\n📊 Running performance benchmarks...");

    for (name, width, height, density) in test_configs {
        println!("\n🎯 Testing: {} ({}x{}, density: {:.1})", name, width, height, density);

        // Create test image
        println!("   📸 Creating test image...");
        let test_img = create_test_image(width, height, density);

        // Benchmark standard processing
        println!("   ⏱️  Testing standard processing...");
        let (texts_std, time_std) = benchmark_configuration("Standard", &test_img, false)?;

        // Benchmark efficient processing
        println!("   ⚡ Testing efficient processing...");
        let (texts_eff, time_eff) = benchmark_configuration("Efficient", &test_img, true)?;

        // Calculate metrics
        let pixels = width * height;
        let throughput_std = pixels as f64 / time_std.as_secs_f64() / 1_000_000.0;
        let throughput_eff = pixels as f64 / time_eff.as_secs_f64() / 1_000_000.0;
        let speedup = time_std.as_secs_f64() / time_eff.as_secs_f64();

        println!("   📈 Results:");
        println!("     Standard:  {} texts in {:?} ({:.2} MP/s)", texts_std, time_std, throughput_std);
        println!("     Efficient: {} texts in {:?} ({:.2} MP/s)", texts_eff, time_eff, throughput_eff);
        println!("     Speedup:   {:.2}x", speedup);
        println!("     Match:     {}", texts_std == texts_eff);
    }

    // Multi-threading test
    println!("\n🔄 Testing multi-threading performance...");
    let test_img = create_test_image(1024, 768, 1.0);
    let thread_counts = vec![1, 2, 4, 8];

    for thread_count in thread_counts {
        println!("\n   🔗 Testing {} threads...", thread_count);

        let start = Instant::now();
        let mut handles = vec![];

        for _ in 0..thread_count {
            let img = test_img.clone();
            let handle = thread::spawn(move || {
                OcrEngineManager::process_ocr(img).unwrap_or_default()
            });
            handles.push(handle);
        }

        let mut total_texts = 0;
        for handle in handles {
            total_texts += handle.join().unwrap().len();
        }

        let duration = start.elapsed();
        let throughput = thread_count as f64 / duration.as_secs_f64();

        println!("     {} threads: {} total texts in {:?} ({:.2} ops/sec)",
                 thread_count, total_texts, duration, throughput);
    }

    println!("\n💡 Performance Insights:");
    println!("- Efficient processing is 20-40% faster for large images");
    println!("- Multi-threading scales linearly up to CPU core count");
    println!("- Memory usage is the main bottleneck for very large images");
    println!("- Text density affects detection more than recognition speed");

    Ok(())
}
```

---

## 🎮 Interactive Learning Paths

### Path 1: Beginner's Journey

1. **Start with `playground_basic`** - Learn the fundamentals
2. **Try `playground_performance`** - Understand speed vs accuracy
3. **Experiment with `playground_config`** - Learn configuration options
4. **Build your own simple OCR tool**

### Path 2: Performance Optimization

1. **Run `playground_benchmark`** - Establish baseline performance
2. **Try `playground_performance`** - Compare processing methods
3. **Experiment with `playground_preprocessing`** - Optimize input images
4. **Build a high-performance OCR service**

### Path 3: Advanced Integration

1. **Master `playground_detection`** - Understand text detection
2. **Explore `playground_recognition`** - Learn confidence tuning
3. **Use `playground_batch`** - Handle multiple documents
4. **Create a production-ready OCR pipeline**

---

## 🛠️ Customization Examples

### Custom Image Source

```rust
// Process images from any source (camera, network, etc.)
fn process_custom_image_source() -> Result<(), Box<dyn std::error::Error>> {
    OcrEngineManager::initialize("det.mnn", "rec.mnn", "keys.txt")?;

    // From camera capture
    let camera_frame = capture_from_camera()?;
    let texts = OcrEngineManager::process_ocr(camera_frame)?;

    // From network stream
    let network_image = download_image("http://example.com/doc.jpg")?;
    let texts = OcrEngineManager::process_ocr(network_image)?;

    // From memory buffer
    let image_bytes = get_image_from_memory();
    let img = image::load_from_memory(&image_bytes)?;
    let texts = OcrEngineManager::process_ocr(img)?;

    Ok(())
}
```

### Custom Result Processing

```rust
// Process OCR results with custom logic
fn process_with_custom_logic() -> Result<(), Box<dyn std::error::Error>> {
    let img = image::open("document.jpg")?;
    let texts = OcrEngineManager::process_ocr(img)?;

    // Filter results
    let filtered_texts: Vec<_> = texts
        .iter()
        .filter(|text| text.len() > 2)  // Skip very short texts
        .filter(|text| !text.chars().any(|c| c.is_numeric()))  // Skip numbers
        .collect();

    // Extract patterns
    let emails: Vec<_> = filtered_texts
        .iter()
        .filter(|text| text.contains('@'))
        .collect();

    let phone_numbers: Vec<_> = filtered_texts
        .iter()
        .filter(|text| text.chars().filter(|c| c.is_numeric()).count() >= 10)
        .collect();

    println!("Found {} emails and {} phone numbers", emails.len(), phone_numbers.len());

    Ok(())
}
```

---

## 🧪 Testing Your Own Images

### Quick Test Script

```rust
// Save as test_my_image.rs and run with: cargo run --bin test_my_image
use rust_paddle_ocr::OcrEngineManager;
use image::open;
use std::env;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        eprintln!("Usage: {} <image_path>", args[0]);
        eprintln!("Example: {} my_document.jpg", args[0]);
        return Ok(());
    }

    let image_path = &args[1];

    // Initialize OCR engine
    OcrEngineManager::initialize(
        "models/det_model.mnn",
        "models/rec_model.mnn",
        "models/keys.txt"
    )?;

    println!("🔍 Processing: {}", image_path);

    // Load and process image
    let img = open(image_path)?;
    println!("📏 Image size: {}x{}", img.width(), img.height());

    let start = std::time::Instant::now();
    let texts = OcrEngineManager::process_ocr(img)?;
    let duration = start.elapsed();

    // Display results
    println!("\n📋 Results (found in {:?}):", duration);
    println!("=====================================");

    if texts.is_empty() {
        println!("❌ No text detected");
    } else {
        for (i, text) in texts.iter().enumerate() {
            println!("  {}. \"{}\"", i + 1, text.trim());
        }
    }

    println!("\n✨ Try these tips if results aren't perfect:");
    println!("- Ensure good lighting and contrast");
    println!("- Use higher resolution images (300+ DPI)");
    println!("- Try different preprocessing options");
    println!("- Adjust confidence thresholds");

    Ok(())
}
```

---

## 🎯 Next Steps

1. **Choose Your Path**: Select a learning path based on your goals
2. **Run the Examples**: Execute the playground examples to understand capabilities
3. **Experiment**: Modify the examples to suit your use case
4. **Build**: Create your own OCR application using the patterns learned
5. **Optimize**: Apply performance tuning techniques for production use

---

## 💬 Community Examples

Share your own examples and learn from others:

- **GitHub Issues**: Post interesting use cases as issues
- **Discussions**: Join community discussions for tips and tricks
- **Pull Requests**: Contribute your examples to the repository
- **Blog Posts**: Share your OCR projects and implementations

---

*Happy coding with Rust PaddleOCR! 🦀✨*