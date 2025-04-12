# Rust PaddleOCR

[English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

PaddleOCR 모델을 기반으로 Rust로 구현된 경량 및 효율적인 OCR(광학 문자 인식) 라이브러리입니다. 이 라이브러리는 MNN 추론 프레임워크를 활용하여 고성능 텍스트 감지 및 인식 기능을 제공합니다.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## 특징

- **텍스트 감지**: 이미지에서 텍스트 영역을 정확하게 찾기
- **텍스트 인식**: 감지된 영역에서 텍스트 내용 인식하기
- **고성능**: MNN 추론 프레임워크로 최적화됨
- **최소한의 의존성**: 경량이며 쉽게 통합 가능
- **사용자 정의 가능**: 다양한 사용 사례에 맞게 조정 가능한 매개변수

## 설치

`Cargo.toml`에 다음을 추가하세요:

```toml
[dependencies.rust-paddle-ocr]
git = "https://github.com/zibo-chen/rust-paddle-ocr.git"
```

특정 브랜치나 태그를 지정할 수도 있습니다:

```toml
[dependencies.rust-paddle-ocr]
git = "https://github.com/zibo-chen/rust-paddle-ocr.git"
branch = "main" 
```

### 전제 조건

이 라이브러리는 다음이 필요합니다:
- MNN 형식으로 변환된 사전 훈련된 PaddleOCR 모델
- 텍스트 인식을 위한 문자 집합 파일

## 사용 예시

```rust
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 감지 모델 불러오기
    let mut det = Det::from_file("path/to/det_model.mnn")?;
    
    // 감지 매개변수 사용자 정의 (선택 사항)
    let det = det
        .with_rect_border_size(50)
        .with_merge_boxes(true)
        .with_merge_threshold(10);
    
    // 인식 모델 불러오기
    let mut rec = Rec::from_file("path/to/rec_model.mnn", "path/to/keys.txt")?;
    
    // 인식 매개변수 사용자 정의 (선택 사항)
    let rec = rec
        .with_min_score(0.6)
        .with_punct_min_score(0.1);
    
    // 이미지 열기
    let img = open("path/to/image.jpg")?;
    
    // 텍스트 영역 찾기
    let text_images = det.find_text_img(&img)?;
    
    // 각 감지된 영역에서 텍스트 인식하기
    for text_img in text_images {
        let text = rec.predict_str(&text_img)?;
        println!("인식된 텍스트: {}", text);
    }
    
    Ok(())
}
```

## API 참조

### 텍스트 감지 (Det)

```rust
// 새 감지기 생성
let mut det = Det::from_file("path/to/det_model.mnn")?;

// 텍스트 영역을 찾고 사각형 반환
let rects = det.find_text_rect(&img)?;

// 텍스트 영역을 찾고 자른 이미지 반환
let text_images = det.find_text_img(&img)?;

// 사용자 정의 옵션
let det = det
    .with_rect_border_size(50)      // 감지된 영역의 테두리 크기 설정
    .with_merge_boxes(true)         // 인접한 상자 병합 활성화/비활성화
    .with_merge_threshold(10);      // 상자 병합 임계값 설정
```

### 텍스트 인식 (Rec)

```rust
// 새 인식기 생성
let mut rec = Rec::from_file("path/to/rec_model.mnn", "path/to/keys.txt")?;

// 텍스트 인식하고 문자열 반환
let text = rec.predict_str(&text_img)?;

// 텍스트 인식하고 신뢰도 점수와 함께 문자 반환
let char_scores = rec.predict_char_score(&text_img)?;

// 사용자 정의 옵션
let rec = rec
    .with_min_score(0.6)           // 일반 문자의 최소 신뢰도 설정
    .with_punct_min_score(0.1);    // 문장 부호의 최소 신뢰도 설정
```

## 성능 최적화

이 라이브러리는 다음과 같은 여러 최적화를 포함합니다:
- 효율적인 텐서 관리
- 텍스트 감지를 위한 스마트 박스 병합
- 적응형 이미지 전처리
- 구성 가능한 신뢰도 임계값

## 라이선스

이 프로젝트는 Apache License 2.0에 따라 라이선스가 부여됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 감사의 말

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 원본 OCR 모델 및 연구 제공
- [MNN](https://github.com/alibaba/MNN) - 효율적인 신경망 추론 프레임워크 제공
- [mnn-rs](https://github.com/aftershootco/mnn-rs) - Rust를 위한 MNN 바인딩 제공
