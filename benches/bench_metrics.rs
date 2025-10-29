use criterion::{criterion_group, criterion_main, Criterion};
use image::DynamicImage;
use rust_paddle_ocr::{Det, Rec};
use std::time::Duration;

fn setup() -> (Det, Rec, DynamicImage) {
    // 加载v5版本模型 - 在性能测试前完成
    let det = Det::from_file("./models/PP-OCRv5_mobile_det_fp16.mnn")
        .expect("Failed to load detection model")
        .with_rect_border_size(12)
        .with_merge_boxes(false)
        .with_merge_threshold(1);

    let rec = Rec::from_file(
        "./models/PP-OCRv5_mobile_rec_fp16.mnn",
        "./models/ppocr_keys_v5.txt",
    )
    .expect("Failed to load recognition model");

    // 加载测试图片 - 在性能测试前完成
    let img = image::open("./res/1.png").expect("Failed to load test image");

    (det, rec, img)
}

fn bench_detection(c: &mut Criterion) {
    let (mut det, _, img) = setup();

    let mut group = c.benchmark_group("text_detection");
    group.measurement_time(Duration::from_secs(10));

    group.bench_function("det_model", |b| {
        b.iter(|| {
            det.find_text_rect(&img).expect("Detection failed");
        });
    });

    group.finish();
}

fn bench_recognition(c: &mut Criterion) {
    let (mut det, mut rec, img) = setup();

    // 先检测文本区域
    let text_images = det.find_text_img(&img).expect("Failed to find text images");

    let mut group = c.benchmark_group("text_recognition");
    group.measurement_time(Duration::from_secs(10));

    group.bench_function("rec_model", |b| {
        b.iter(|| {
            // 仅测试第一个文本区域的识别，如果没有文本区域则跳过
            if let Some(text_img) = text_images.first() {
                rec.predict_str(text_img).expect("Recognition failed");
            }
        });
    });

    group.finish();
}

fn bench_end_to_end(c: &mut Criterion) {
    let (mut det, mut rec, img) = setup();

    let mut group = c.benchmark_group("end_to_end");
    group.measurement_time(Duration::from_secs(15));

    group.bench_function("full_pipeline", |b| {
        b.iter(|| {
            // 端到端过程：检测 + 识别
            let text_images = det.find_text_img(&img).expect("Failed to find text images");

            for text_img in &text_images {
                rec.predict_str(text_img).expect("Recognition failed");
            }
        });
    });

    group.finish();
}

criterion_group!(
    benches,
    bench_detection,
    bench_recognition,
    bench_end_to_end
);
criterion_main!(benches);
