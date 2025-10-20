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
- **다국어 지원**: 기본 모델（`PP-OCRv5_mobile_rec.mnn`）은 간체 중국어, 번체 중국어, 영어, 일본어, 중국어 병음을 지원
- **전용 언어 모델**: 11개 이상의 언어를 위한 전용 모델로 최적의 성능 제공:
  - 아랍어, 키릴 문자, 데바나가리 문자, 그리스어, 영어
  - 동슬라브어, 한국어, 라틴어, 타밀어, 텔루구어, 태국어
- **공유 감지 모델**: 모든 V5 언어 모델은 동일한 감지 모델（`PP-OCRv5_mobile_det.mnn`）을 사용
- **강화된 시나리오 인식**:
  - 중영 복합 손글씨 인식 능력 현저히 향상
  - 세로 텍스트 인식 최적화
  - 생소한 문자 인식 능력 강화
- **성능 향상**: PP-OCRv4 대비 엔드 투 엔드 13% 향상
- **모델 파일**（기본 다국어）:
  - 감지 모델: `PP-OCRv5_mobile_det.mnn`（모든 언어 공유）
  - 인식 모델: `PP-OCRv5_mobile_rec.mnn`（기본값, 중국어/영어/일본어 지원）
  - 문자 집합: `ppocr_keys_v5.txt`
- **전용 언어 모델 파일**（선택사항）:
  - 인식 모델: `{lang}_PP-OCRv5_mobile_rec_infer.mnn`
  - 문자 집합: `ppocr_keys_{lang}.txt`
  - 지원 언어: `arabic`（아랍어）, `cyrillic`（키릴 문자）, `devanagari`（데바나가리 문자）, `el`（그리스어）, `en`（영어）, `eslav`（동슬라브어）, `korean`（한국어）, `latin`（라틴어）, `ta`（타밀어）, `te`（텔루구어）, `th`（태국어）

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
| 언어 지원           | 중국어, 영어 | 다국어（기본적으로 중국어/영어/일본어 지원, 11개 이상의 전용 언어 모델 제공） | 다국어（기본적으로 중국어/영어/일본어 지원, 11개 이상의 전용 언어 모델 제공） |
| 문자 유형 지원      | 중국어, 영어 | 간체 중국어, 번체 중국어, 영어, 일본어, 중국어 병음 | 간체 중국어, 번체 중국어, 영어, 일본어, 중국어 병음 |
| 손글씨 인식        | 기본 지원 | 현저히 향상 | 현저히 향상 |
| 세로 텍스트        | 기본 지원 | 최적화 향상 | 최적화 향상 |
| 생소한 문자 인식    | 제한적 지원 | 강화된 인식 | 강화된 인식 |
| 추론 속도 (FPS)    | 1.1      | 1.2      | 1.2 |
| 메모리 사용량 (피크)| 422.22MB | 388.41MB | 388.41MB |
| 모델 크기          | 표준     | 표준     | 절반으로 축소 |
| 권장 시나리오      | 일반 문서 | 복잡한 시나리오 및 다국어 | 고성능 시나리오 및 다국어 |

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

### 전용 언어 모델 사용

특정 언어의 인식 정확도를 향상시키기 위해 전용 언어 모델을 사용할 수 있습니다:

```rust
use rust_paddle_ocr::{Det, Rec};
use image::open;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 모든 V5 언어 모델은 동일한 감지 모델을 공유
    let mut det = Det::from_file("./models/PP-OCRv5_mobile_det.mnn")?;
    
    // === 예시 1: 영어 전용 모델 ===
    let mut rec_en = Rec::from_file(
        "./models/en_PP-OCRv5_mobile_rec_infer.mnn",
        "./models/ppocr_keys_en.txt"
    )?;
    
    // === 예시 2: 한국어 모델 ===
    let mut rec_ko = Rec::from_file(
        "./models/korean_PP-OCRv5_mobile_rec_infer.mnn",
        "./models/ppocr_keys_korean.txt"
    )?;
    
    // === 예시 3: 아랍어 모델 ===
    let mut rec_ar = Rec::from_file(
        "./models/arabic_PP-OCRv5_mobile_rec_infer.mnn",
        "./models/ppocr_keys_arabic.txt"
    )?;
    
    // 이미지 처리
    let img = open("path/to/image.jpg")?;
    let text_images = det.find_text_img(&img)?;
    
    for text_img in text_images {
        let text = rec_en.predict_str(&text_img)?;
        println!("인식된 텍스트: {}", text);
    }
    
    Ok(())
}
```

#### 사용 가능한 언어 모델

| 언어 | 모델 파일 | 문자 집합 | 사용 사례 |
|------|----------|----------|---------|
| 기본（다국어） | `PP-OCRv5_mobile_rec.mnn` | `ppocr_keys_v5.txt` | 중국어, 영어, 일본어（일반 용도에 권장） |
| 아랍어 | `arabic_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_arabic.txt` | 아랍어 텍스트 인식 |
| 키릴 문자 | `cyrillic_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_cyrillic.txt` | 러시아어, 불가리아어, 세르비아어 등 |
| 데바나가리 문자 | `devanagari_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_devanagari.txt` | 힌디어, 마라티어, 네팔어 등 |
| 그리스어 | `el_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_el.txt` | 그리스어 텍스트 인식 |
| 영어 | `en_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_en.txt` | 영어 전용 문서 |
| 동슬라브어 | `eslav_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_eslav.txt` | 우크라이나어, 벨라루스어 등 |
| 한국어 | `korean_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_korean.txt` | 한국어 텍스트 인식 |
| 라틴어 | `latin_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_latin.txt` | 라틴 문자 언어 |
| 타밀어 | `ta_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_ta.txt` | 타밀어 텍스트 인식 |
| 텔루구어 | `te_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_te.txt` | 텔루구어 텍스트 인식 |
| 태국어 | `th_PP-OCRv5_mobile_rec_infer.mnn` | `ppocr_keys_th.txt` | 태국어 텍스트 인식 |

**참고**: 모든 전용 언어 모델은 동일한 감지 모델（`PP-OCRv5_mobile_det.mnn`）을 사용합니다. 대상 언어에 따라 적절한 인식 모델을 선택하면 최적의 정확도를 얻을 수 있습니다.

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
| 언어 지원 | 중국어, 영어 | 다국어（기본적으로 중국어/영어/일본어 지원, 11개 이상의 전용 언어 모델 제공） |
| 문자 유형 지원 | 중국어, 영어 | 간체 중국어, 번체 중국어, 영어, 일본어, 중국어 병음 |
| 손글씨 인식 | 기본 지원 | 현저히 향상 |
| 세로 텍스트 | 기본 지원 | 최적화 향상 |
| 생소한 문자 인식 | 제한적 지원 | 강화된 인식 |
| 엔드 투 엔드 정확도 | 기준 | 13% 향상 |
| 권장 시나리오 | 일반 문서 | 복잡한 시나리오 및 다국어 |

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
    .with_rect_border_size(12)
    .with_merge_boxes(false)
    .with_merge_threshold(1);
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
    .with_min_score(0.6)
    .with_punct_min_score(0.1);
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
