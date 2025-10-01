use image::{DynamicImage, GenericImageView, ImageBuffer};
use imageproc::rect::Rect;
use rayon::prelude::*;
use std::sync::Arc;

/// 高效图像裁剪工具
/// Efficient image cropping utilities
pub struct EfficientCropper;

/// 图像引用包装器，避免不必要的克隆
/// Image reference wrapper to avoid unnecessary clones
pub enum ImageRef {
    Owned(DynamicImage),
    Shared(Arc<DynamicImage>),
}

impl ImageRef {
    pub fn as_dynamic_image(&self) -> &DynamicImage {
        match self {
            ImageRef::Owned(img) => img,
            ImageRef::Shared(img) => img.as_ref(),
        }
    }

    pub fn dimensions(&self) -> (u32, u32) {
        self.as_dynamic_image().dimensions()
    }
}

impl From<DynamicImage> for ImageRef {
    fn from(img: DynamicImage) -> Self {
        ImageRef::Owned(img)
    }
}

impl From<Arc<DynamicImage>> for ImageRef {
    fn from(img: Arc<DynamicImage>) -> Self {
        ImageRef::Shared(img)
    }
}

impl EfficientCropper {
    /// 智能裁剪：根据裁剪区域大小选择最优策略
    /// Smart cropping: choose optimal strategy based on crop area size
    pub fn smart_crop(image: &ImageRef, rect: &Rect) -> DynamicImage {
        let (img_w, img_h) = image.dimensions();
        let crop_area = rect.width() * rect.height();
        let total_area = img_w * img_h;

        // 如果裁剪区域覆盖整个图像，直接克隆
        if rect.left() == 0 && rect.top() == 0 && rect.width() == img_w && rect.height() == img_h {
            return image.as_dynamic_image().clone();
        }

        // 如果裁剪区域很小（<10%），使用像素级拷贝
        if crop_area < total_area / 10 {
            Self::pixel_copy_crop(image.as_dynamic_image(), rect)
        } else {
            // 否则使用标准裁剪
            Self::standard_crop(image.as_dynamic_image(), rect)
        }
    }

    /// 标准裁剪方法
    fn standard_crop(image: &DynamicImage, rect: &Rect) -> DynamicImage {
        image.crop_imm(
            rect.left() as u32,
            rect.top() as u32,
            rect.width(),
            rect.height(),
        )
    }

    /// 像素级拷贝裁剪（对小区域更高效）
    fn pixel_copy_crop(image: &DynamicImage, rect: &Rect) -> DynamicImage {
        let width = rect.width();
        let height = rect.height();
        let x_start = rect.left() as u32;
        let y_start = rect.top() as u32;

        match image {
            DynamicImage::ImageRgba8(img) => {
                let mut cropped = ImageBuffer::new(width, height);
                for y in 0..height {
                    for x in 0..width {
                        let src_x = x_start + x;
                        let src_y = y_start + y;
                        if src_x < img.width() && src_y < img.height() {
                            let pixel = img.get_pixel(src_x, src_y);
                            cropped.put_pixel(x, y, *pixel);
                        }
                    }
                }
                DynamicImage::ImageRgba8(cropped)
            }
            DynamicImage::ImageRgb8(img) => {
                let mut cropped = ImageBuffer::new(width, height);
                for y in 0..height {
                    for x in 0..width {
                        let src_x = x_start + x;
                        let src_y = y_start + y;
                        if src_x < img.width() && src_y < img.height() {
                            let pixel = img.get_pixel(src_x, src_y);
                            cropped.put_pixel(x, y, *pixel);
                        }
                    }
                }
                DynamicImage::ImageRgb8(cropped)
            }
            _ => {
                // 对于其他格式，回退到标准方法
                Self::standard_crop(image, rect)
            }
        }
    }

    /// 批量裁剪：对多个区域进行优化的批量裁剪
    /// Batch cropping: optimized batch cropping for multiple regions
    pub fn batch_crop(image: &ImageRef, rects: &[Rect]) -> Vec<DynamicImage> {
        if rects.is_empty() {
            return Vec::new();
        }

        // 根据矩形数量和大小智能选择处理策略
        let total_area: u32 = rects.iter().map(|r| r.width() * r.height()).sum();
        let avg_area = total_area / rects.len() as u32;
        let image_area = image.dimensions().0 * image.dimensions().1;

        // 如果矩形很少或者平均面积很大，使用串行处理
        if rects.len() < 4 || avg_area > image_area / 8 {
            rects
                .iter()
                .map(|rect| Self::smart_crop(image, rect))
                .collect()
        } else {
            // 否则使用并行处理
            Self::parallel_batch_crop(image, rects)
        }
    }

    /// 并行批量裁剪（使用rayon进行并行处理）
    /// Parallel batch cropping using rayon
    pub fn parallel_batch_crop(image: &ImageRef, rects: &[Rect]) -> Vec<DynamicImage> {
        use rayon::prelude::*;

        // 根据CPU核心数和矩形数量决定并行度
        let cpu_cores = std::thread::available_parallelism()
            .map(|n| n.get())
            .unwrap_or(4);

        // 如果矩形数量较少，直接并行处理
        if rects.len() <= cpu_cores * 2 {
            rects
                .par_iter()
                .map(|rect| Self::smart_crop(image, rect))
                .collect()
        } else {
            // 如果矩形很多，分批并行处理以避免内存压力
            let batch_size = (rects.len() / cpu_cores).max(1);

            rects
                .par_chunks(batch_size)
                .flat_map(|chunk| {
                    chunk
                        .iter()
                        .map(|rect| Self::smart_crop(image, rect))
                        .collect::<Vec<_>>()
                })
                .collect()
        }
    }

    /// 优化的批量裁剪，预先分析所有矩形
    /// Optimized batch cropping with pre-analysis of all rectangles
    pub fn optimized_batch_crop(image: &ImageRef, rects: &[Rect]) -> Vec<DynamicImage> {
        if rects.is_empty() {
            return Vec::new();
        }

        let (small_rects, large_rects): (Vec<_>, Vec<_>) =
            rects.iter().enumerate().partition(|(_, rect)| {
                let area = rect.width() * rect.height();
                area < image.dimensions().0 * image.dimensions().1 / 10
            });

        let small_results: Vec<_> = small_rects
            .into_par_iter()
            .map(|(idx, rect)| (idx, Self::pixel_copy_crop(image.as_dynamic_image(), rect)))
            .collect();

        let large_results: Vec<_> = large_rects
            .into_iter()
            .map(|(idx, rect)| (idx, Self::standard_crop(image.as_dynamic_image(), rect)))
            .collect();

        let mut results = vec![None; rects.len()];

        for (idx, result) in small_results.into_iter().chain(large_results) {
            results[idx] = Some(result);
        }

        results.into_iter().map(|r| r.unwrap()).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use image::{DynamicImage, Rgba, RgbaImage};

    fn create_test_image() -> DynamicImage {
        let img = RgbaImage::from_fn(100, 100, |x, y| {
            Rgba([(x % 256) as u8, (y % 256) as u8, ((x + y) % 256) as u8, 255])
        });
        DynamicImage::ImageRgba8(img)
    }

    #[test]
    fn test_smart_crop() {
        let image = create_test_image();
        let image_ref = ImageRef::from(image);

        // 测试小区域裁剪
        let small_rect = Rect::at(10, 10).of_size(20, 20);
        let cropped = EfficientCropper::smart_crop(&image_ref, &small_rect);
        assert_eq!(cropped.dimensions(), (20, 20));

        // 测试大区域裁剪
        let large_rect = Rect::at(10, 10).of_size(80, 80);
        let cropped = EfficientCropper::smart_crop(&image_ref, &large_rect);
        assert_eq!(cropped.dimensions(), (80, 80));
    }

    #[test]
    fn test_batch_crop() {
        let image = create_test_image();
        let image_ref = ImageRef::from(image);

        let rects = vec![
            Rect::at(0, 0).of_size(20, 20),
            Rect::at(30, 30).of_size(25, 25),
            Rect::at(60, 60).of_size(30, 30),
        ];

        let results = EfficientCropper::batch_crop(&image_ref, &rects);
        assert_eq!(results.len(), 3);
        assert_eq!(results[0].dimensions(), (20, 20));
        assert_eq!(results[1].dimensions(), (25, 25));
        assert_eq!(results[2].dimensions(), (30, 30));
    }
}
