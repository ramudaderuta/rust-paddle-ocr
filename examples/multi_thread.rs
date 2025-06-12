use image::{DynamicImage, Rgba};
use imageproc::drawing::draw_hollow_rect_mut;
use log::{error, info};
use rust_paddle_ocr::{OcrEngineManager, OcrResult};
use std::path::Path;
use std::thread;
use std::time::Instant;

fn main() -> OcrResult<()> {
    if std::env::var("RUST_LOG").is_err() {
        std::env::set_var("RUST_LOG", "info");
    }
    env_logger::init();

    info!("正在初始化OCR引擎");
    // 初始化全局OCR引擎，使用与simple示例相同的配置
    // Initialize global OCR engine with the same configuration as simple example
    OcrEngineManager::initialize_with_config(
        "./models/ch_PP-OCRv4_det_infer.mnn",
        "./models/ch_PP-OCRv4_rec_infer.mnn",
        "./models/ppocr_keys_v4.txt",
        12,
        false,
        1,
    )?;
    info!("OCR引擎初始化完成");

    // 要处理的图像路径 | Image paths to process
    let image_paths = ["./res/1.png", "./res/2.png", "./res/3.png"];

    // 创建多个线程并发处理图像 | Create multiple threads to process images concurrently
    let mut handles = Vec::new();
    let start_time = Instant::now();

    for (i, path) in image_paths.iter().enumerate() {
        let path_str = path.to_string();
        // 为每个图像创建一个新线程 | Create a new thread for each image
        let handle = thread::spawn(move || -> OcrResult<()> {
            info!("线程 {} 开始处理图像: {}", i, path_str);

            // 加载图像 | Load image
            let img = match image::open(Path::new(&path_str)) {
                Ok(img) => {
                    info!(
                        "线程 {} 成功加载图像, 大小: {}x{}",
                        i,
                        img.width(),
                        img.height()
                    );
                    img
                }
                Err(e) => {
                    error!("线程 {} 加载图像失败: {}", i, e);
                    return Err(e.into());
                }
            };

            // 处理OCR并生成调试图像 | Process OCR and generate debug image
            info!("线程 {} 开始OCR处理", i);
            let result = process_single_image(i, img, &path_str)?;
            info!("线程 {} OCR处理完成", i);

            Ok(result)
        });

        handles.push(handle);
    }

    // 收集所有线程的结果 | Collect results from all threads
    for (i, handle) in handles.into_iter().enumerate() {
        match handle.join() {
            Ok(result) => match result {
                Ok(_) => info!("线程 {} 成功完成处理", i),
                Err(e) => error!("线程 {} 处理失败: {}", i, e),
            },
            Err(e) => error!("线程 {} 异常终止: {:?}", i, e),
        }
    }

    let elapsed = start_time.elapsed();
    info!("所有线程处理完成，总用时: {:.2}秒", elapsed.as_secs_f32());

    Ok(())
}

// 处理单个图像的OCR | Process OCR for a single image
fn process_single_image(thread_id: usize, img: DynamicImage, img_path: &str) -> OcrResult<()> {
    // 创建一个可变的彩色图像副本，用于绘制文本框 | Create a mutable color image copy for drawing text boxes
    let mut debug_image = img.to_rgba8();

    // 颜色集合，用于绘制不同的文本框 | Color collection for drawing different text boxes
    let colors = [
        Rgba([255, 0, 0, 255]),   // 红色 | Red
        Rgba([0, 255, 0, 255]),   // 绿色 | Green
        Rgba([0, 0, 255, 255]),   // 蓝色 | Blue
        Rgba([255, 255, 0, 255]), // 黄色 | Yellow
        Rgba([255, 0, 255, 255]), // 紫色 | Purple
        Rgba([0, 255, 255, 255]), // 青色 | Cyan
    ];

    // 第一步：获取文本区域的矩形框和对应的图像
    // Step 1: Get text region rectangles and corresponding images
    info!("线程 {} 开始检测文本区域", thread_id);
    let text_rects = OcrEngineManager::get_text_rects(&img)?;
    let text_images = OcrEngineManager::get_text_images(&img)?;
    info!("线程 {} 检测到 {} 个文本区域", thread_id, text_rects.len());

    // 第二步：分别对每个文本区域识别 | Step 2: Recognize each text region
    for (i, (rect, text_img)) in text_rects.iter().zip(text_images.iter()).enumerate() {
        // 使用循环颜色绘制矩形框 | Use cycling colors to draw rectangular boxes
        let color = colors[i % colors.len()];

        // 绘制粗一点的矩形框，让边框更明显 | Draw thicker rectangle frames to make borders more visible
        for offset in 0..3 {
            // 扩大1-3个像素绘制多层边框 | Expand 1-3 pixels to draw multiple layers of borders
            let expanded_rect =
                imageproc::rect::Rect::at(rect.left() - offset, rect.top() - offset).of_size(
                    rect.width() + offset as u32 * 2,
                    rect.height() + offset as u32 * 2,
                );
            draw_hollow_rect_mut(&mut debug_image, expanded_rect, color);
        }

        // 识别文本 | Recognize text
        let _text = match OcrEngineManager::recognize_text(text_img.clone()) {
            Ok(text) => {
                info!("线程 {} 识别文本区域 {}: {}", thread_id, i + 1, text);
                text
            }
            Err(e) => {
                error!("线程 {} 识别文本区域 {} 失败: {}", thread_id, i + 1, e);
                format!("Error: {}", e)
            }
        };

        // 可以在这里添加绘制文本内容的代码 | Add code here to draw text content if needed
    }

    // 根据原始图像路径生成调试图像的文件名 | Generate debug image filename based on original image path
    let path = Path::new(img_path);
    let file_stem = path.file_stem().unwrap_or_default().to_string_lossy();
    let output_path = format!("./debug_ocr_result_{}.png", file_stem);

    // 保存带有文本框的调试图像 | Save debug image with text boxes
    info!("线程 {} 保存调试图像到 {}", thread_id, output_path);
    match debug_image.save(&output_path) {
        Ok(_) => info!("线程 {} 调试图像保存成功", thread_id),
        Err(e) => error!("线程 {} 保存调试图像失败: {}", thread_id, e),
    }

    let start_time = Instant::now();
    // 完整的OCR处理，用于获取和显示所有文本 | Complete OCR processing for getting and displaying all text
    let texts = OcrEngineManager::process_ocr(img.clone())?;
    let elapsed = start_time.elapsed();

    info!(
        "线程 {} 完整OCR处理完成，识别到 {} 个文本，用时: {:.2}秒",
        thread_id,
        texts.len(),
        elapsed.as_secs_f32()
    );

    // 打印识别结果 | Print recognition results
    for (j, text) in texts.iter().enumerate() {
        info!("线程 {} 文本 {}: {}", thread_id, j + 1, text);
    }

    Ok(())
}
