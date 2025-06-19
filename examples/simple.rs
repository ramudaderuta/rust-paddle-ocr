use image::Rgba;
use imageproc::drawing::draw_hollow_rect_mut;
use log::{error, info};
use rust_paddle_ocr::{Det, OcrResult, Rec};

fn main() -> OcrResult<()> {
    // 初始化日志系统 | Initialize the logging system
    env_logger::init();

    info!("Starting to initialize PaddleOCR models");

    info!("Loading text detection model...");
    let mut det = match Det::from_file("./models/PP-OCRv5_mobile_det.mnn") {
        Ok(det) => {
            let det = det
                .with_rect_border_size(12)
                .with_merge_boxes(false)
                .with_merge_threshold(1);
            info!("Text detection model loaded successfully");
            det
        }
        Err(e) => {
            error!("Failed to load text detection model: {}", e);
            return Err(e);
        }
    };

    info!("Loading text recognition model...");
    let mut rec = match Rec::from_file(
        "./models/PP-OCRv5_mobile_rec.mnn",
        "./models/ppocr_keys_v5.txt",
    ) {
        Ok(rec) => rec,
        Err(e) => {
            error!("Failed to load text recognition model: {}", e);
            return Err(e);
        }
    };

    info!("Loading image...");
    let img = match image::open("./res/4.png") {
        Ok(img) => {
            info!(
                "Image loaded successfully, size: {}x{}",
                img.width(),
                img.height()
            );
            img
        }
        Err(e) => {
            error!("Failed to load image: {}", e);
            return Err(e.into());
        }
    };

    // 创建一个可变的彩色图像副本，用于绘制文本框 | Create a mutable color image copy for drawing text boxes
    let mut debug_image = img.to_rgba8();

    info!("Starting text detection...");
    let text_rects = match det.find_text_rect(&img) {
        Ok(rects) => {
            info!("Detected {} text regions", rects.len());
            if rects.is_empty() {
                error!(
                    "No text regions detected, please check the image or lower the detection threshold"
                );
            }
            rects
        }
        Err(e) => {
            error!("Text detection failed: {}", e);
            return Err(e);
        }
    };

    // 获取文本区域对应的图像 | Get images corresponding to the text regions
    let text_images = match det.find_text_img(&img) {
        Ok(images) => images,
        Err(e) => {
            error!("Failed to extract text region images: {}", e);
            return Err(e);
        }
    };

    // 颜色集合，用于绘制不同的文本框 | Color collection for drawing different text boxes
    let colors = [
        Rgba([255, 0, 0, 255]),   // 红色 | Red
        Rgba([0, 255, 0, 255]),   // 绿色 | Green
        Rgba([0, 0, 255, 255]),   // 蓝色 | Blue
        Rgba([255, 255, 0, 255]), // 黄色 | Yellow
        Rgba([255, 0, 255, 255]), // 紫色 | Purple
        Rgba([0, 255, 255, 255]), // 青色 | Cyan
    ];

    info!("Starting text recognition...");
    for (i, (rect, sub)) in text_rects.iter().zip(text_images.iter()).enumerate() {
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

        // 在矩形边框上绘制索引编号 | Draw index number on the rectangle border
        let _text = match rec.predict_str(sub) {
            Ok(text) => {
                println!("{}", text);
                text
            }
            Err(e) => {
                error!("Failed to recognize text region {}: {}", i + 1, e);
                format!("Error: {}", e)
            }
        };
    }

    // 保存带有文本框的调试图像 | Save debug image with text boxes
    let output_path = "./debug_ocr_result.png";
    info!("Saving image with text boxes to {}", output_path);
    match debug_image.save(output_path) {
        Ok(_) => info!("Debug image saved successfully"),
        Err(e) => error!("Failed to save debug image: {}", e),
    }

    info!("OCR processing completed");
    Ok(())
}
