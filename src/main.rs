use clap::{Parser, ValueEnum};
use log::{error, info};
use rust_paddle_ocr::{Det, OcrError, OcrResult, Rec};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

// 使用 include_bytes! 宏嵌入模型文件到二进制文件中
static DET_MODEL: &[u8] = include_bytes!("../models/ch_PP-OCRv4_det_infer.mnn");
static REC_MODEL: &[u8] = include_bytes!("../models/ch_PP-OCRv4_rec_infer.mnn");
static KEYS_DATA: &[u8] = include_bytes!("../models/ppocr_keys_v1.txt");

// 定义输出模式
#[derive(ValueEnum, Clone, Debug)]
enum OutputMode {
    /// 详细输出模式，使用JSON包含文本内容和位置信息
    Json,
    /// 简单输出模式，仅输出识别的文本内容
    Text,
}

// 命令行参数
#[derive(Parser, Debug)]
#[command(author, version, about = "PaddleOCR command line tool")]
struct Args {
    /// 要识别的图像路径
    #[arg(short, long, value_name = "IMAGE_PATH")]
    path: PathBuf,

    /// 输出模式：json(详细) 或 text(简单)
    #[arg(short, long, value_enum, default_value_t = OutputMode::Text)]
    mode: OutputMode,

    /// 是否显示详细日志
    #[arg(short, long)]
    verbose: bool,
}

// 文本识别结果的JSON表示
#[derive(Serialize, Deserialize)]
struct TextBox {
    text: String,
    confidence: f32,
    position: TextBoxPosition,
}

#[derive(Serialize, Deserialize)]
struct TextBoxPosition {
    left: i32,
    top: i32,
    width: u32,
    height: u32,
}

fn main() -> OcrResult<()> {
    // 解析命令行参数
    let args = Args::parse();

    // 配置日志
    if args.verbose {
        std::env::set_var("RUST_LOG", "info");
    } else {
        std::env::set_var("RUST_LOG", "error");
    }
    env_logger::init();

    info!("Starting PaddleOCR command line tool");

    // 检查输入文件是否存在
    if !args.path.exists() {
        error!("Input image file does not exist: {:?}", args.path);
        return Err(OcrError::InputError(format!(
            "Input file not found: {:?}",
            args.path
        )));
    }

    // 直接从内存加载模型
    info!("Loading detection model from memory...");
    let mut det = Det::from_bytes(DET_MODEL)?
        .with_rect_border_size(12)
        .with_merge_boxes(false)
        .with_merge_threshold(1);

    info!("Loading recognition model from memory...");
    let mut rec = Rec::from_bytes_with_keys(REC_MODEL, KEYS_DATA)?;

    // 加载图像
    info!("Loading image from {:?}...", args.path);
    let img = match image::open(&args.path) {
        Ok(img) => {
            info!("Image loaded, size: {}x{}", img.width(), img.height());
            img
        }
        Err(e) => {
            error!("Failed to load image: {}", e);
            return Err(e.into());
        }
    };

    // 文本检测
    info!("Performing text detection...");
    let text_rects = match det.find_text_rect(&img) {
        Ok(rects) => {
            if rects.is_empty() {
                info!("No text regions detected in the image.");
            } else {
                info!("Found {} text regions", rects.len());
            }
            rects
        }
        Err(e) => {
            error!("Text detection failed: {}", e);
            return Err(e);
        }
    };

    // 获取文本区域
    let text_images = match det.find_text_img(&img) {
        Ok(images) => {
            info!("Successfully extracted {} text images", images.len());
            images
        }
        Err(e) => {
            error!("Failed to extract text images: {}", e);
            return Err(e);
        }
    };

    // 确保文本区域和图像数量一致
    if text_rects.len() != text_images.len() {
        error!(
            "Mismatch between text rectangles ({}) and text images ({})",
            text_rects.len(),
            text_images.len()
        );
        return Err(OcrError::EngineError(
            "Inconsistent detection results".to_string(),
        ));
    }

    // 文本识别并输出结果
    info!("Performing text recognition...");

    // 根据输出模式处理结果
    match args.mode {
        OutputMode::Json => {
            let mut results = Vec::new();

            for (i, (rect, sub_img)) in text_rects.iter().zip(text_images.iter()).enumerate() {
                info!("Processing text region {} of {}", i + 1, text_rects.len());

                // 检查子图像是否有效
                if sub_img.width() == 0 || sub_img.height() == 0 {
                    error!("Invalid subimage with zero dimensions at index {}", i);
                    continue;
                }

                match rec.predict_with_confidence(sub_img) {
                    Ok((text, confidence)) => {
                        results.push(TextBox {
                            text,
                            confidence,
                            position: TextBoxPosition {
                                left: rect.left(),
                                top: rect.top(),
                                width: rect.width(),
                                height: rect.height(),
                            },
                        });
                    }
                    Err(e) => {
                        error!("Failed to recognize text in region {}: {}", i, e);
                    }
                }
            }

            // 输出JSON结果
            let json = serde_json::to_string_pretty(&results)
                .map_err(|e| OcrError::OutputError(e.to_string()))?;
            println!("{}", json);
        }

        OutputMode::Text => {
            // 简单文本模式
            for (i, (_, sub_img)) in text_rects.iter().zip(text_images.iter()).enumerate() {
                info!("Processing text region {} of {}", i + 1, text_rects.len());

                // 检查子图像是否有效
                if sub_img.width() == 0 || sub_img.height() == 0 {
                    error!("Invalid subimage with zero dimensions at index {}", i);
                    continue;
                }

                match rec.predict_str(sub_img) {
                    Ok(text) => {
                        println!("{}", text);
                    }
                    Err(e) => {
                        error!("Failed to recognize text in region {}: {}", i, e);
                    }
                }
            }
        }
    }

    info!("OCR process completed");
    Ok(())
}
