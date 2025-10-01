use std::time::Instant;
use image::{DynamicImage, Rgba, RgbaImage};
use imageproc::rect::Rect;
use rust_paddle_ocr::efficient_cropping::{EfficientCropper, ImageRef};

/// 创建一个测试图像
fn create_test_image(width: u32, height: u32) -> DynamicImage {
    let img = RgbaImage::from_fn(width, height, |x, y| {
        Rgba([
            (x % 256) as u8,
            (y % 256) as u8,
            ((x + y) % 256) as u8,
            255,
        ])
    });
    DynamicImage::ImageRgba8(img)
}

/// 创建一组测试的裁剪区域
fn create_test_rects() -> Vec<Rect> {
    vec![
        // 小区域 (适合像素级拷贝)
        Rect::at(10, 10).of_size(20, 20),
        Rect::at(50, 50).of_size(30, 25),
        Rect::at(100, 100).of_size(15, 15),
        
        // 中等区域
        Rect::at(200, 200).of_size(80, 60),
        Rect::at(300, 150).of_size(100, 80),
        
        // 大区域 (适合标准裁剪)
        Rect::at(400, 300).of_size(200, 150),
        Rect::at(100, 400).of_size(300, 200),
        
        // 更多小区域用于批量测试
        Rect::at(50, 150).of_size(25, 25),
        Rect::at(150, 50).of_size(20, 30),
        Rect::at(250, 250).of_size(35, 35),
    ]
}

/// 基准测试：标准裁剪方法
fn benchmark_standard_cropping(image: &DynamicImage, rects: &[Rect], iterations: usize) -> std::time::Duration {
    let start = Instant::now();
    
    for _ in 0..iterations {
        let mut _results = Vec::with_capacity(rects.len());
        for rect in rects {
            let cropped = image.crop_imm(
                rect.left() as u32,
                rect.top() as u32,
                rect.width(),
                rect.height(),
            );
            _results.push(cropped);
        }
    }
    
    start.elapsed()
}

/// 基准测试：智能裁剪方法
fn benchmark_smart_cropping(image: &DynamicImage, rects: &[Rect], iterations: usize) -> std::time::Duration {
    let image_ref = ImageRef::from(image.clone());
    let start = Instant::now();
    
    for _ in 0..iterations {
        let mut _results = Vec::with_capacity(rects.len());
        for rect in rects {
            let cropped = EfficientCropper::smart_crop(&image_ref, rect);
            _results.push(cropped);
        }
    }
    
    start.elapsed()
}

/// 基准测试：批量裁剪方法
fn benchmark_batch_cropping(image: &DynamicImage, rects: &[Rect], iterations: usize) -> std::time::Duration {
    let image_ref = ImageRef::from(image.clone());
    let start = Instant::now();
    
    for _ in 0..iterations {
        let _results = EfficientCropper::batch_crop(&image_ref, rects);
    }
    
    start.elapsed()
}

/// 基准测试：并行批量裁剪方法
fn benchmark_parallel_batch_cropping(image: &DynamicImage, rects: &[Rect], iterations: usize) -> std::time::Duration {
    let image_ref = ImageRef::from(image.clone());
    let start = Instant::now();
    
    for _ in 0..iterations {
        let _results = EfficientCropper::parallel_batch_crop(&image_ref, rects);
    }
    
    start.elapsed()
}

fn format_duration(duration: std::time::Duration) -> String {
    if duration.as_millis() > 0 {
        format!("{:.2}ms", duration.as_secs_f64() * 1000.0)
    } else {
        format!("{:.2}μs", duration.as_micros() as f64)
    }
}

fn main() {
    println!("🚀 OCR裁剪性能基准测试");
    println!("=====================");
    
    // 创建测试图像
    let test_image = create_test_image(800, 600);
    let test_rects = create_test_rects();
    
    println!("测试配置:");
    println!("- 图像尺寸: {}x{}", test_image.width(), test_image.height());
    println!("- 裁剪区域数量: {}", test_rects.len());
    println!("- 每种方法迭代次数: 1000次");
    println!();
    
    // 热身运行
    println!("🔥 热身运行...");
    for _ in 0..10 {
        let _ = benchmark_standard_cropping(&test_image, &test_rects, 1);
        let _ = benchmark_smart_cropping(&test_image, &test_rects, 1);
    }
    
    println!("📊 开始性能测试...");
    println!();
    
    // 基准测试
    let iterations = 1000;
    
    // 标准裁剪
    println!("1️⃣  标准裁剪 (image.crop_imm):");
    let standard_time = benchmark_standard_cropping(&test_image, &test_rects, iterations);
    println!("   总时间: {}", format_duration(standard_time));
    println!("   平均每次: {}", format_duration(standard_time / iterations as u32));
    println!();
    
    // 智能裁剪
    println!("2️⃣  智能裁剪 (EfficientCropper::smart_crop):");
    let smart_time = benchmark_smart_cropping(&test_image, &test_rects, iterations);
    println!("   总时间: {}", format_duration(smart_time));
    println!("   平均每次: {}", format_duration(smart_time / iterations as u32));
    
    // 计算性能提升
    let improvement = if smart_time < standard_time {
        let speedup = standard_time.as_secs_f64() / smart_time.as_secs_f64();
        format!("🚀 提升 {:.2}x", speedup)
    } else {
        let slowdown = smart_time.as_secs_f64() / standard_time.as_secs_f64();
        format!("🐌 降低 {:.2}x", slowdown)
    };
    println!("   性能对比: {}", improvement);
    println!();
    
    // 批量裁剪
    println!("3️⃣  批量裁剪 (EfficientCropper::batch_crop):");
    let batch_time = benchmark_batch_cropping(&test_image, &test_rects, iterations);
    println!("   总时间: {}", format_duration(batch_time));
    println!("   平均每次: {}", format_duration(batch_time / iterations as u32));
    
    let batch_improvement = if batch_time < standard_time {
        let speedup = standard_time.as_secs_f64() / batch_time.as_secs_f64();
        format!("🚀 提升 {:.2}x", speedup)
    } else {
        let slowdown = batch_time.as_secs_f64() / standard_time.as_secs_f64();
        format!("🐌 降低 {:.2}x", slowdown)
    };
    println!("   性能对比: {}", batch_improvement);
    println!();
    
    // 并行批量裁剪
    println!("4️⃣  并行批量裁剪 (EfficientCropper::parallel_batch_crop):");
    let parallel_time = benchmark_parallel_batch_cropping(&test_image, &test_rects, iterations);
    println!("   总时间: {}", format_duration(parallel_time));
    println!("   平均每次: {}", format_duration(parallel_time / iterations as u32));
    
    let parallel_improvement = if parallel_time < standard_time {
        let speedup = standard_time.as_secs_f64() / parallel_time.as_secs_f64();
        format!("🚀 提升 {:.2}x", speedup)
    } else {
        let slowdown = parallel_time.as_secs_f64() / standard_time.as_secs_f64();
        format!("🐌 降低 {:.2}x", slowdown)
    };
    println!("   性能对比: {}", parallel_improvement);
    println!();
    
    // 总结
    println!("📈 性能总结:");
    println!("=============");
    
    let results = vec![
        ("标准裁剪", standard_time),
        ("智能裁剪", smart_time),
        ("批量裁剪", batch_time),
        ("并行批量裁剪", parallel_time),
    ];
    
    // 找到最快的方法
    let fastest = results.iter().min_by_key(|(_, time)| *time).unwrap();
    println!("🏆 最快方法: {} ({})", fastest.0, format_duration(fastest.1));
    
    // 显示所有方法的相对性能
    for (name, time) in &results {
        let relative_performance = fastest.1.as_secs_f64() / time.as_secs_f64();
        if *time == fastest.1 {
            println!("   {} - 基准 (1.00x)", name);
        } else {
            println!("   {} - {:.2}x 慢", name, 1.0 / relative_performance);
        }
    }
    
    println!();
    println!("💡 推荐使用: {}", fastest.0);
}