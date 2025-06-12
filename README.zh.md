# Rust PaddleOCR

[English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

一个基于PaddleOCR模型的轻量级高效OCR（光学字符识别）Rust库。该库利用MNN推理框架提供高性能的文本检测和识别功能。

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## 特性

- **文本检测**：准确定位图像中的文本区域
- **文本识别**：识别检测区域中的文本内容
- **多版本模型支持**：支持 PP-OCRv4 和 PP-OCRv5 模型，灵活选择使用
- **多语言支持**：PP-OCRv5 支持简体中文、繁体中文、英文、日文、中文拼音等多种文字类型
- **复杂场景识别**：增强的手写体、竖排文本、生僻字识别能力
- **高性能**：使用MNN推理框架优化
- **最小依赖**：轻量级且易于集成
- **可自定义**：针对不同用例的可调整参数
- **命令行工具**：提供简单的命令行界面进行OCR识别

## 模型版本

该库支持两个PaddleOCR模型版本：

### PP-OCRv4
- **稳定版本**：经过充分验证，兼容性好
- **适用场景**：常规文档识别，对准确性要求较高的场景
- **模型文件**：
  - 检测模型：`ch_PP-OCRv4_det_infer.mnn`
  - 识别模型：`ch_PP-OCRv4_rec_infer.mnn`
  - 字符集：`ppocr_keys_v4.txt`

### PP-OCRv5 ⭐️ 推荐
- **最新版本**：新一代文字识别解决方案
- **多文字类型支持**：简体中文、中文拼音、繁体中文、英文、日文
- **增强场景识别**：
  - 中英复杂手写体识别能力显著提升
  - 竖排文本识别优化
  - 生僻字识别能力增强
- **性能提升**：相比PP-OCRv4端到端提升13个百分点
- **模型文件**：
  - 检测模型：`PP-OCRv5_mobile_det.mnn`
  - 识别模型：`PP-OCRv5_mobile_rec.mnn`
  - 字符集：`ppocr_keys_v5.txt`

## 安装

在`Cargo.toml`中添加：

```toml
[dependencies.rust-paddle-ocr]
git = "https://github.com/zibo-chen/rust-paddle-ocr.git"

```

您也可以指定特定分支或标签：

```toml
[dependencies.rust-paddle-ocr]
git = "https://github.com/zibo-chen/rust-paddle-ocr.git"
branch = "main"
```

### 前提条件

该库需要：
- 转换为MNN格式的预训练PaddleOCR模型
- 用于文本识别的字符集文件

## 使用方式

### 作为rust库使用

可以灵活选择使用 PP-OCRv4 或 PP-OCRv5 模型,只需加载不同模型文件即可：

```rust
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // === 使用 PP-OCRv5 模型（推荐） ===
    let mut det = Det::from_file("./models/PP-OCRv5_mobile_det.mnn")?;
    let mut rec = Rec::from_file(
        "./models/PP-OCRv5_mobile_rec.mnn", 
        "./models/ppocr_keys_v5.txt"
    )?;
    
    // === 或使用 PP-OCRv4 模型 ===
    // let mut det = Det::from_file("./models/ch_PP-OCRv4_det_infer.mnn")?;
    // let mut rec = Rec::from_file(
    //     "./models/ch_PP-OCRv4_rec_infer.mnn", 
    //     "./models/ppocr_keys_v4.txt"
    // )?;
    
    // 自定义检测参数（可选）
    let det = det
        .with_rect_border_size(12)  // PP-OCRv5 推荐参数
        .with_merge_boxes(false)    // PP-OCRv5 推荐参数
        .with_merge_threshold(1);   // PP-OCRv5 推荐参数
    
    // 自定义识别参数（可选）
    let rec = rec
        .with_min_score(0.6)
        .with_punct_min_score(0.1);
    
    // 打开图像
    let img = open("path/to/image.jpg")?;
    
    // 检测文本区域
    let text_images = det.find_text_img(&img)?;
    
    // 识别每个检测区域中的文本
    for text_img in text_images {
        let text = rec.predict_str(&text_img)?;
        println!("识别的文本: {}", text);
    }
    
    Ok(())
}
```

## 命令行工具

该库提供了一个内置的命令行工具，可以直接进行OCR识别：

```bash
# 基本用法
./ocr -p path/to/image.jpg

# 输出JSON格式（包含详细信息和位置）
./ocr -p path/to/image.jpg -m json

# 显示详细日志信息
./ocr -p path/to/image.jpg -v

# 显示当前使用的模型版本
./ocr --version-info
```

### 编译不同版本

```bash
# 编译使用 PP-OCRv4 模型的版本（默认）
cargo build --release

# 编译使用 PP-OCRv5 模型的版本（推荐）
cargo build --release --features v5
```

### 命令行选项

```
选项:
  -p, --path <IMAGE_PATH>  要识别的图像路径
  -m, --mode <MODE>        输出模式: json(详细) 或 text(简单) [默认: text]
  -v, --verbose            是否显示详细日志
      --version-info       显示模型版本信息
  -h, --help               显示帮助信息
  -V, --version            显示版本信息
```

## 模型文件获取

您可以从以下渠道获取预训练的MNN模型：

1. **官方模型**：从 PaddleOCR 官方仓库下载并转换为 MNN 格式
2. **项目提供**：本项目的 `models/` 目录包含了转换好的模型文件

## PP-OCRv5 vs PP-OCRv4 性能对比

| 特性 | PP-OCRv4 | PP-OCRv5 |
|------|----------|----------|
| 文字类型支持 | 中文、英文 | 简体中文、繁体中文、英文、日文、中文拼音 |
| 手写体识别 | 基础支持 | 显著增强 |
| 竖排文本 | 基础支持 | 优化提升 |
| 生僻字识别 | 有限支持 | 增强识别 |
| 端到端准确率 | 基准 | 提升 13% |
| 推荐场景 | 常规文档 | 复杂多样场景 |

## API 参考

### 文本检测 (Det)

```rust
// 创建新的检测器
let mut det = Det::from_file("path/to/det_model.mnn")?;

// 查找文本区域并返回矩形
let rects = det.find_text_rect(&img)?;

// 查找文本区域并返回裁剪后的图像
let text_images = det.find_text_img(&img)?;

// 自定义选项
let det = det
    .with_rect_border_size(12)
    .with_merge_boxes(false)
    .with_merge_threshold(1);
```

### 文本识别 (Rec)

```rust
// 创建新的识别器
let mut rec = Rec::from_file("path/to/rec_model.mnn", "path/to/keys.txt")?;

// 识别文本并返回字符串
let text = rec.predict_str(&text_img)?;

// 识别文本并返回带有置信度分数的字符
let char_scores = rec.predict_char_score(&text_img)?;

// 自定义选项
let rec = rec
    .with_min_score(0.6)           // 设置普通字符的最低置信度
    .with_punct_min_score(0.1);    // 设置标点符号的最低置信度
```

## 性能优化

该库包含几项优化：
- 高效的张量管理
- 智能框合并用于文本检测
- 自适应图像预处理
- 可配置的置信度阈值

## 示例结果

以下是一些展示库实际效果的示例结果：

### 示例 1
![原始图像 1](res/1.png)
![OCR 结果 1](res/1_ocr_result.png)

### 示例 2
![原始图像 2](res/2.png)
![OCR 结果 2](res/2_ocr_result.png)

### 示例 3
![原始图像 3](res/3.png)
![OCR 结果 3](res/3_ocr_result.png)

## 许可证

该项目采用Apache许可证2.0版 - 详情请参阅[LICENSE](LICENSE)文件。

## 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 提供原始OCR模型和研究
- [MNN](https://github.com/alibaba/MNN) - 提供高效的神经网络推理框架
- [mnn-rs](https://github.com/aftershootco/mnn-rs) - 为Rust提供了MNN绑定
