# Rust PaddleOCR

[English](README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

PaddleOCR 모델을 기반으로 Rust로 구현된 경량 및 효율적인 OCR(광학 문자 인식) 라이브러리입니다. 이 라이브러리는 MNN 추론 프레임워크를 활용하여 고성능 텍스트 감지 및 인식 기능을 제공합니다.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## 특징

- **텍스트 감지**: 이미지에서 텍스트 영역을 정확하게 찾기
- **텍스트 인식**: 감지된 영역에서 텍스트 내용 인식하기
- **다중 버전 모델 지원**: PP-OCRv4 및 PP-OCRv5 모델을 지원하여 유연하게 선택 사용
- **다국어 지원**: PP-OCRv5는 간체 중국어, 번체 중국어, 영어, 일본어, 중국어 병음 등 다양한 문자 유형 지원
- **복잡한 시나리오 인식**: 강화된 손글씨, 세로 텍스트, 생소한 문자 인식 능력
- **고성능**: MNN 추론 프레임워크로 최적화됨
- **최소한의 의존성**: 경량이며 쉽게 통합 가능
- **사용자 정의 가능**: 다양한 사용 사례에 맞게 조정 가능한 매개변수
- **명령줄 도구**: OCR 인식을 위한 간단한 명령줄 인터페이스

## 모델 버전

이 라이브러리는 세 가지 PaddleOCR 모델 버전을 지원합니다:

### PP-OCRv4
- **안정 버전**: 충분히 검증되었으며 호환성이 우수함
- **적용 시나리오**: 일반 문서 인식, 정확성이 높게 요구되는 시나리오
- **모델 파일**:
  - 감지 모델: `ch_PP-OCRv4_det_infer.mnn`
  - 인식 모델: `ch_PP-OCRv4_rec_infer.mnn`
  - 문자 집합: `ppocr_keys_v4.txt`

### PP-OCRv5 ⭐️ 권장
- **최신 버전**: 차세대 문자 인식 솔루션
- **다중 문자 유형 지원**: 간체 중국어, 중국어 병음, 번체 중국어, 영어, 일본어
- **강화된 시나리오 인식**:
  - 중영 복합 손글씨 인식 능력 현저히 향상
  - 세로 텍스트 인식 최적화
  - 생소한 문자 인식 능력 강화
- **성능 향상**: PP-OCRv4 대비 엔드 투 엔드 13% 향상
- **모델 파일**:
  - 감지 모델: `PP-OCRv5_mobile_det.mnn`
  - 인식 모델: `PP-OCRv5_mobile_rec.mnn`
  - 문자 집합: `ppocr_keys_v5.txt`

### PP-OCRv5 FP16 ⭐️ 신규
- **효율 버전**: 정확도를 유지하면서 추론 속도를 높이고 메모리 사용량을 줄임
- **적용 시나리오**: 성능과 메모리 사용량이 중요한 시나리오
- **성능 향상**:
  - 추론 속도 약 9% 향상
  - 메모리 사용량 약 8% 감소
  - 모델 크기 절반으로 축소
- **모델 파일**:
  - 감지 모델: `PP-OCRv5_mobile_det_fp16.mnn`
  - 인식 모델: `PP-OCRv5_mobile_rec_fp16.mnn`
  - 문자 집합: `ppocr_keys_v5.txt`

### 모델 성능 비교

| 특징                | PP-OCRv4 | PP-OCRv5 | PP-OCRv5 FP16 |
|---------------------|----------|----------|---------------|
| 문자 유형 지원      | 중국어, 영어 | 간체 중국어, 번체 중국어, 영어, 일본어, 중국어 병음 | 간체 중국어, 번체 중국어, 영어, 일본어, 중국어 병음 |
| 손글씨 인식        | 기본 지원 | 현저히 향상 | 현저히 향상 |
| 세로 텍스트        | 기본 지원 | 최적화 향상 | 최적화 향상 |
| 생소한 문자 인식    | 제한적 지원 | 강화된 인식 | 강화된 인식 |
| 추론 속도 (FPS)    | 1.1      | 1.2      | 1.2 |
| 메모리 사용량 (피크)| 422.22MB | 388.41MB | 388.41MB |
| 모델 크기          | 표준     | 표준     | 절반으로 축소 |
| 권장 시나리오      | 일반 문서 | 복잡하고 다양한 시나리오 | 고성능 시나리오 |

### PP-OCRv5 FP16 테스트 데이터

#### 표준 모델
```
============================================================
테스트 보고서: 추론 속도 테스트
============================================================
총 시간: 44.23초
평균 추론 시간: 884.64밀리초
최고 추론 시간: 744.99밀리초
최저 추론 시간: 954.03밀리초
성공 횟수: 50
실패 횟수: 0
추론 속도: 1.1 FPS
메모리 사용량 - 시작: 14.94MB
메모리 사용량 - 종료: 422.22MB
메모리 사용량 - 피크: 422.22MB
메모리 변화: +407.28MB
```

#### FP16 모델
```
============================================================
테스트 보고서: 추론 속도 테스트
============================================================
총 시간: 43.33초
평균 추론 시간: 866.66밀리초
최고 추론 시간: 719.41밀리초
최저 추론 시간: 974.93밀리초
성공 횟수: 50
실패 횟수: 0
추론 속도: 1.2 FPS
메모리 사용량 - 시작: 15.70MB
메모리 사용량 - 종료: 388.41MB
메모리 사용량 - 피크: 388.41MB
메모리 변화: +372.70MB
```

### 테스트 방법

다음 명령어를 사용하여 테스트를 실행하고 성능 데이터를 검증할 수 있습니다(Mac Mini M4 기준 테스트 데이터):

```bash
python test_ffi.py test
```

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

## 사용 방법

### Rust 라이브러리로 사용

PP-OCRv4 또는 PP-OCRv5 모델을 유연하게 선택하여 사용할 수 있으며, 다른 모델 파일을 로드하기만 하면 됩니다:

```rust
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // === PP-OCRv5 모델 사용 (권장) ===
    let mut det = Det::from_file("./models/PP-OCRv5_mobile_det.mnn")?;
    let mut rec = Rec::from_file(
        "./models/PP-OCRv5_mobile_rec.mnn", 
        "./models/ppocr_keys_v5.txt"
    )?;
    
    // === 또는 PP-OCRv4 모델 사용 ===
    // let mut det = Det::from_file("./models/ch_PP-OCRv4_det_infer.mnn")?;
    // let mut rec = Rec::from_file(
    //     "./models/ch_PP-OCRv4_rec_infer.mnn", 
    //     "./models/ppocr_keys_v4.txt"
    // )?;
    
    // 감지 매개변수 사용자 정의 (선택 사항)
    let det = det
        .with_rect_border_size(12)  // PP-OCRv5 권장 매개변수
        .with_merge_boxes(false)    // PP-OCRv5 권장 매개변수
        .with_merge_threshold(1);   // PP-OCRv5 권장 매개변수
    
    // 인식 매개변수 사용자 정의 (선택 사항)
    let rec = rec
        .with_min_score(0.6)
        .with_punct_min_score(0.1);
    
    // 이미지 열기
    let img = open("path/to/image.jpg")?;
    
    // 텍스트 영역 감지
    let text_images = det.find_text_img(&img)?;
    
    // 각 감지된 영역에서 텍스트 인식하기
    for text_img in text_images {
        let text = rec.predict_str(&text_img)?;
        println!("인식된 텍스트: {}", text);
    }
    
    Ok(())
}
```

## 명령줄 도구

이 라이브러리는 직접 OCR 인식을 수행할 수 있는 내장 명령줄 도구를 제공합니다:

```bash
# 기본 사용법
./ocr -p path/to/image.jpg

# JSON 형식으로 출력 (자세한 정보와 위치 포함)
./ocr -p path/to/image.jpg -m json

# 상세 로그 정보 표시
./ocr -p path/to/image.jpg -v

# 현재 사용 중인 모델 버전 표시
./ocr --version-info
```

### 다른 버전 컴파일

```bash
# PP-OCRv4 모델 사용 버전 컴파일 (기본값)
cargo build --release

# PP-OCRv5 모델 사용 버전 컴파일 (권장)
cargo build --release --features v5
```

### 명령줄 옵션

```
옵션:
  -p, --path <IMAGE_PATH>  인식할 이미지 경로
  -m, --mode <MODE>        출력 모드: json(상세) 또는 text(간단) [기본값: text]
  -v, --verbose            상세 로그 정보 표시 여부
      --version-info       모델 버전 정보 표시
  -h, --help               도움말 정보 출력
  -V, --version            버전 정보 출력
```

## 모델 파일 획득

다음 경로에서 사전 훈련된 MNN 모델을 얻을 수 있습니다:

1. **공식 모델**: PaddleOCR 공식 저장소에서 다운로드하여 MNN 형식으로 변환
2. **프로젝트 제공**: 본 프로젝트의 `models/` 디렉토리에 변환된 모델 파일 포함

## PP-OCRv5 vs PP-OCRv4 성능 비교

| 특징 | PP-OCRv4 | PP-OCRv5 |
|------|----------|----------|
| 문자 유형 지원 | 중국어, 영어 | 간체 중국어, 번체 중국어, 영어, 일본어, 중국어 병음 |
| 손글씨 인식 | 기본 지원 | 현저히 향상 |
| 세로 텍스트 | 기본 지원 | 최적화 향상 |
| 생소한 문자 인식 | 제한적 지원 | 강화된 인식 |
| 엔드 투 엔드 정확도 | 기준 | 13% 향상 |
| 권장 시나리오 | 일반 문서 | 복잡하고 다양한 시나리오 |

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
    .with_rect_border_size(12)      // 감지된 영역의 테두리 크기 설정
    .with_merge_boxes(false)        // 인접한 상자 병합 활성화/비활성화
    .with_merge_threshold(1);       // 상자 병합 임계값 설정
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

## 실행 예시

다음은 이 라이브러리의 실행 예시입니다:

### 예시 1
![원본 이미지 1](res/1.png)
![OCR 결과 1](res/1_ocr_result.png)

### 예시 2
![원본 이미지 2](res/2.png)
![OCR 결과 2](res/2_ocr_result.png)

### 예시 3
![원본 이미지 3](res/3.png)
![OCR 결과 3](res/3_ocr_result.png)

## 라이선스

이 프로젝트는 Apache License 2.0에 따라 라이선스가 부여됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 감사의 말

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 원본 OCR 모델 및 연구 제공
- [MNN](https://github.com/alibaba/MNN) - 효율적인 신경망 추론 프레임워크 제공
- [mnn-rs](https://github.com/aftershootco/mnn-rs) - Rust를 위한 MNN 바인딩 제공
