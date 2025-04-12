// file_path: src/error.rs
use thiserror::Error;

/// OCR处理过程中可能出现的错误类型
///
/// Error types that may occur during OCR processing
#[derive(Error, Debug)]
pub enum OcrError {
    /// IO错误，如文件读写失败
    /// IO errors, such as file read/write failures
    #[error("IO error: {0}")]
    IOError(#[from] std::io::Error),

    /// 图像处理错误
    /// Image processing errors
    #[error("Image processing error: {0}")]
    ImageError(#[from] image::ImageError),

    /// MNN推理框架错误
    /// MNN inference framework errors
    #[error("MNN error: {0}")]
    MNNError(#[from] mnn::MNNError),

    /// 张量形状错误
    /// Tensor shape errors
    #[error("Shape error: {0}")]
    ShapeError(#[from] ndarray::ShapeError),

    /// 输入张量数据错误
    /// Input tensor data errors
    #[error("Input tensor data error: {0}")]
    InputError(String),

    /// 输出张量数据错误
    /// Output tensor data errors
    #[error("Output tensor data error: {0}")]
    OutputError(String),

    /// 模型推理错误
    /// Model inference errors
    #[error("Model inference error: {0}")]
    InferenceError(String),
}

/// OCR操作的结果类型
///
/// Result type for OCR operations
pub type OcrResult<T> = Result<T, OcrError>;
