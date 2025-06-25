# Rust PaddleOCR

[English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

PaddleOCRモデルをベースにしたRustで実装された軽量で効率的なOCR（光学文字認識）ライブラリです。このライブラリはMNN推論フレームワークを活用して、高性能なテキスト検出と認識機能を提供します。

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## 特徴

- **テキスト検出**: 画像内のテキスト領域を正確に特定
- **テキスト認識**: 検出された領域からテキスト内容を認識
- **複数モデルバージョン対応**: PP-OCRv4とPP-OCRv5モデルをサポート、柔軟に選択可能
- **多言語サポート**: PP-OCRv5は簡体中国語、繁体中国語、英語、日本語、中国語ピンインなど複数の文字タイプをサポート
- **複雑シーン認識**: 手書き文字、縦書きテキスト、難読漢字の認識能力を強化
- **高性能**: MNN推論フレームワークで最適化
- **最小限の依存関係**: 軽量で容易に統合可能
- **カスタマイズ可能**: 異なるユースケース向けの調整可能なパラメータ
- **コマンドラインツール**: OCR認識のための簡単なコマンドラインインターフェース

## モデルバージョン

このライブラリは3つのPaddleOCRモデルバージョンをサポートしています：

### PP-OCRv4
- **安定版**: 十分に検証済み、互換性が良い
- **適用シーン**: 一般的な文書認識、精度要求の高いシーン
- **モデルファイル**:
  - 検出モデル: `ch_PP-OCRv4_det_infer.mnn`
  - 認識モデル: `ch_PP-OCRv4_rec_infer.mnn`
  - 文字セット: `ppocr_keys_v4.txt`

### PP-OCRv5 ⭐️ 推奨
- **最新版**: 新世代文字認識ソリューション
- **多文字タイプサポート**: 簡体中国語、中国語ピンイン、繁体中国語、英語、日本語
- **シーン認識の強化**:
  - 中英複雑手書き文字認識能力が大幅向上
  - 縦書きテキスト認識の最適化
  - 難読漢字認識能力の強化
- **性能向上**: PP-OCRv4と比較してエンドツーエンドで13ポイント向上
- **モデルファイル**:
  - 検出モデル: `PP-OCRv5_mobile_det.mnn`
  - 認識モデル: `PP-OCRv5_mobile_rec.mnn`
  - 文字セット: `ppocr_keys_v5.txt`

### PP-OCRv5 FP16 ⭐️ 新規
- **効率版**: 精度を落とさず、推論速度を向上させ、メモリ使用量を削減
- **適用シーン**: パフォーマンスとメモリ使用量が重要なシーン
- **性能向上**:
  - 推論速度が約9%向上
  - メモリ使用量が約8%削減
  - モデルサイズが半分に縮小
- **モデルファイル**:
  - 検出モデル: `PP-OCRv5_mobile_det_fp16.mnn`
  - 認識モデル: `PP-OCRv5_mobile_rec_fp16.mnn`
  - 文字セット: `ppocr_keys_v5.txt`

### モデル性能比較

| 特徴                | PP-OCRv4 | PP-OCRv5 | PP-OCRv5 FP16 |
|---------------------|----------|----------|---------------|
| 文字タイプサポート  | 中国語、英語 | 簡体中国語、繁体中国語、英語、日本語、中国語ピンイン | 簡体中国語、繁体中国語、英語、日本語、中国語ピンイン |
| 手書き文字認識      | 基本サポート | 大幅強化 | 大幅強化 |
| 縦書きテキスト      | 基本サポート | 最適化向上 | 最適化向上 |
| 難読漢字認識        | 限定サポート | 認識強化 | 認識強化 |
| 推論速度 (FPS)      | 1.1      | 1.2      | 1.2 |
| メモリ使用量 (ピーク)| 422.22MB | 388.41MB | 388.41MB |
| モデルサイズ        | 標準     | 標準     | 半分に縮小 |
| 推奨シーン          | 一般文書 | 複雑多様シーン | 高性能シーン |

### PP-OCRv5 FP16 テストデータ

#### 標準モデル
```
============================================================
テストレポート: 推論速度テスト
============================================================
総時間: 44.23秒
平均推論時間: 884.64ミリ秒
最速推論時間: 744.99ミリ秒
最遅推論時間: 954.03ミリ秒
成功回数: 50
失敗回数: 0
推論速度: 1.1 FPS
メモリ使用量 - 開始: 14.94MB
メモリ使用量 - 終了: 422.22MB
メモリ使用量 - ピーク: 422.22MB
メモリ変化: +407.28MB
```

#### FP16モデル
```
============================================================
テストレポート: 推論速度テスト
============================================================
総時間: 43.33秒
平均推論時間: 866.66ミリ秒
最速推論時間: 719.41ミリ秒
最遅推論時間: 974.93ミリ秒
成功回数: 50
失敗回数: 0
推論速度: 1.2 FPS
メモリ使用量 - 開始: 15.70MB
メモリ使用量 - 終了: 388.41MB
メモリ使用量 - ピーク: 388.41MB
メモリ変化: +372.70MB
```

### テスト方法

以下のコマンドを使用してテストを実行し、性能データを検証できます（テストデータはMac Mini M4に基づく）：

```bash
python test_ffi.py test
```

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

## 使用方法

### Rustライブラリとして使用

PP-OCRv4またはPP-OCRv5モデルを柔軟に選択でき、異なるモデルファイルを読み込むだけで切り替え可能です：

```rust
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // === PP-OCRv5モデルを使用（推奨） ===
    let mut det = Det::from_file("./models/PP-OCRv5_mobile_det.mnn")?;
    let mut rec = Rec::from_file(
        "./models/PP-OCRv5_mobile_rec.mnn", 
        "./models/ppocr_keys_v5.txt"
    )?;
    
    // === またはPP-OCRv4モデルを使用 ===
    // let mut det = Det::from_file("./models/ch_PP-OCRv4_det_infer.mnn")?;
    // let mut rec = Rec::from_file(
    //     "./models/ch_PP-OCRv4_rec_infer.mnn", 
    //     "./models/ppocr_keys_v4.txt"
    // )?;
    
    // 検出パラメータをカスタマイズ（任意）
    let det = det
        .with_rect_border_size(12)  // PP-OCRv5推奨パラメータ
        .with_merge_boxes(false)    // PP-OCRv5推奨パラメータ
        .with_merge_threshold(1);   // PP-OCRv5推奨パラメータ
    
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

## コマンドラインツール

このライブラリには、直接OCR認識を行うための組み込みコマンドラインツールが提供されています：

```bash
# 基本的な使用法
./ocr -p path/to/image.jpg

# JSON形式で出力（詳細情報と位置を含む）
./ocr -p path/to/image.jpg -m json

# 詳細なログ情報を表示
./ocr -p path/to/image.jpg -v

# 現在使用中のモデルバージョンを表示
./ocr --version-info
```

### 異なるバージョンのコンパイル

```bash
# PP-OCRv4モデルを使用するバージョンをコンパイル（デフォルト）
cargo build --release

# PP-OCRv5モデルを使用するバージョンをコンパイル（推奨）
cargo build --release --features v5
```

### コマンドラインオプション

```
オプション:
  -p, --path <IMAGE_PATH>  認識する画像のパス
  -m, --mode <MODE>        出力モード: json(詳細) または text(シンプル) [デフォルト: text]
  -v, --verbose            詳細なログ情報を表示するかどうか
      --version-info       モデルバージョン情報を表示
  -h, --help               ヘルプ情報を表示
  -V, --version            バージョン情報を表示
```

## モデルファイルの取得

以下のチャンネルから事前学習済みMNNモデルを取得できます：

1. **公式モデル**: PaddleOCR公式リポジトリからダウンロードしてMNN形式に変換
2. **プロジェクト提供**: 本プロジェクトの`models/`ディレクトリに変換済みモデルファイルを含む

## PP-OCRv5 vs PP-OCRv4 性能比較

| 特徴 | PP-OCRv4 | PP-OCRv5 |
|------|----------|----------|
| 文字タイプサポート | 中国語、英語 | 簡体中国語、繁体中国語、英語、日本語、中国語ピンイン |
| 手書き文字認識 | 基本サポート | 大幅強化 |
| 縦書きテキスト | 基本サポート | 最適化向上 |
| 難読漢字認識 | 限定サポート | 認識強化 |
| エンドツーエンド精度 | ベースライン | 13%向上 |
| 推奨シーン | 一般文書 | 複雑多様シーン |

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
    .with_rect_border_size(12)
    .with_merge_boxes(false)
    .with_merge_threshold(1);
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
