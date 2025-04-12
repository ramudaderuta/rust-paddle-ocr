//! # Rust PaddleOCR
//!
//! 基于 PaddleOCR 模型的 Rust OCR 库，提供轻量级、高效的文字识别功能。
//! A Rust OCR library based on PaddleOCR models, providing lightweight and efficient text recognition.
//!
//! ## 主要功能 (Main Features)
//!
//! - 文本检测 (Text Detection): 定位图像中的文本区域
//! - 文本识别 (Text Recognition): 识别检测到的文本内容
//!
//! ## 使用示例 (Usage Example)
//!
//! ```rust,no_run
//! use rust_paddle_ocr::{Det, Rec};
//! use image::open;
//!
//! fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     // 加载检测模型
//!     // Load detection model
//!     let mut det = Det::from_file("path/to/det_model.mnn")?;
//!     
//!     // 加载识别模型
//!     // Load recognition model
//!     let mut rec = Rec::from_file("path/to/rec_model.mnn", "path/to/keys.txt")?;
//!     
//!     // 打开图像
//!     // Open image
//!     let img = open("path/to/image.jpg")?;
//!     
//!     // 检测文本区域
//!     // Detect text regions
//!     let text_images = det.find_text_img(&img)?;
//!     
//!     // 识别每个文本区域的内容
//!     // Recognize content in each text region
//!     for text_img in text_images {
//!         let text = rec.predict_str(&text_img)?;
//!         println!("Recognized text: {}", text);
//!     }
//!     
//!     Ok(())
//! }
//! ```

pub mod det;
pub mod error;
pub mod rec;

pub use det::Det;
pub use error::{OcrError, OcrResult};
pub use rec::Rec;
