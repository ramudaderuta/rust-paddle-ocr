# Rust PaddleOCR

[English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

PaddleOCRモデルをベースにしたRustで実装された軽量で効率的なOCR（光学文字認識）ライブラリです。このライブラリはMNN推論フレームワークを活用して、高性能なテキスト検出と認識機能を提供します。

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## 特徴

- **テキスト検出**: 画像内のテキスト領域を正確に特定
- **テキスト認識**: 検出された領域からテキスト内容を認識
- **高性能**: MNN推論フレームワークで最適化
- **最小限の依存関係**: 軽量で容易に統合可能
- **カスタマイズ可能**: 異なるユースケース向けの調整可能なパラメータ

## インストール

`Cargo.toml`に以下を追加してください：

```toml
[dependencies.rust-paddle-ocr]
git = "https://github.com/zibo-chen/rust-paddle-ocr.git"
```

特定のブランチやタグを指定することもできます：

```toml
[dependencies.rust-paddle-ocr]
git = "https://github.com/zibo-chen/rust-paddle-ocr.git"
branch = "main" 
```

### 前提条件

このライブラリには以下が必要です：
- MNN形式に変換された事前学習済みPaddleOCRモデル
- テキスト認識用の文字セットファイル

## 使用例

```rust
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 検出モデルを読み込む
    let mut det = Det::from_file("path/to/det_model.mnn")?;
    
    // 検出パラメータをカスタマイズ（任意）
    let det = det
        .with_rect_border_size(50)
        .with_merge_boxes(true)
        .with_merge_threshold(10);
    
    // 認識モデルを読み込む
    let mut rec = Rec::from_file("path/to/rec_model.mnn", "path/to/keys.txt")?;
    
    // 認識パラメータをカスタマイズ（任意）
    let rec = rec
        .with_min_score(0.6)
        .with_punct_min_score(0.1);
    
    // 画像を開く
    let img = open("path/to/image.jpg")?;
    
    // テキスト領域を検出
    let text_images = det.find_text_img(&img)?;
    
    // 検出された各領域のテキストを認識
    for text_img in text_images {
        let text = rec.predict_str(&text_img)?;
        println!("認識されたテキスト: {}", text);
    }
    
    Ok(())
}
```

## API リファレンス

### テキスト検出 (Det)

```rust
// 新しい検出器を作成
let mut det = Det::from_file("path/to/det_model.mnn")?;

// テキスト領域を検出して矩形を返す
let rects = det.find_text_rect(&img)?;

// テキスト領域を検出して切り取られた画像を返す
let text_images = det.find_text_img(&img)?;

// カスタマイズオプション
let det = det
    .with_rect_border_size(50)      // 検出領域の境界サイズを設定
    .with_merge_boxes(true)         // 隣接するボックスの結合を有効/無効化
    .with_merge_threshold(10);      // ボックス結合のしきい値を設定
```

### テキスト認識 (Rec)

```rust
// 新しい認識器を作成
let mut rec = Rec::from_file("path/to/rec_model.mnn", "path/to/keys.txt")?;

// テキストを認識して文字列を返す
let text = rec.predict_str(&text_img)?;

// テキストを認識して信頼度スコア付きの文字を返す
let char_scores = rec.predict_char_score(&text_img)?;

// カスタマイズオプション
let rec = rec
    .with_min_score(0.6)           // 通常文字の最小信頼度を設定
    .with_punct_min_score(0.1);    // 句読点の最小信頼度を設定
```

## パフォーマンス最適化

このライブラリには以下の最適化が含まれています：
- 効率的なテンソル管理
- テキスト検出のためのスマートボックス結合
- 適応型画像前処理
- 設定可能な信頼度しきい値

## 実行例

以下はこのライブラリの実行例です：

### 例 1
![元画像 1](res/1.png)
![OCR 結果 1](res/1_ocr_result.png)

### 例 2
![元画像 2](res/2.png)
![OCR 結果 2](res/2_ocr_result.png)

### 例 3
![元画像 3](res/3.png)
![OCR 結果 3](res/3_ocr_result.png)

## ライセンス

このプロジェクトはApache License 2.0でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 謝辞

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 元のOCRモデルと研究のために
- [MNN](https://github.com/alibaba/MNN) - 効率的なニューラルネットワーク推論フレームワークのために
- [mnn-rs](https://github.com/aftershootco/mnn-rs) - RustにMNNバインディングを提供するために
