use image::{DynamicImage, GenericImageView};
use mnn::{BackendConfig, ForwardType, Interpreter, PowerMode, PrecisionMode, ScheduleConfig};
use ndarray::{Array, ArrayBase, Dim, OwnedRepr};
use std::{borrow::Cow, path::Path};

use crate::error::OcrResult;

/// 文本识别模型
///
/// Text recognition model that identifies characters in text images
pub struct Rec {
    interpreter: Interpreter,
    session: Option<mnn::Session>,
    keys: Vec<char>,
    min_score: f32,
    punct_min_score: f32,
}

impl Rec {
    const MIN_SCORE_DEFAULT: f32 = 0.6;
    const PUNCT_MIN_SCORE_DEFAULT: f32 = 0.1;

    const PUNCTUATIONS: [char; 49] = [
        ',', '.', '!', '?', ';', ':', '"', '\'', '(', ')', '[', ']', '{', '}', '-', '_', '/', '\\',
        '|', '@', '#', '$', '%', '&', '*', '+', '=', '~', '，', '。', '！', '？', '；', '：', '、',
        '「', '」', '『', '』', '（', '）', '【', '】', '《', '》', '—', '…', '·', '～',
    ];

    /// 创建新的文本识别器实例
    ///
    /// Create a new text recognizer instance
    pub fn new(interpreter: Interpreter, keys: Vec<char>) -> Self {
        Self {
            interpreter,
            session: None,
            keys,
            min_score: Self::MIN_SCORE_DEFAULT,
            punct_min_score: Self::PUNCT_MIN_SCORE_DEFAULT,
        }
    }

    /// 从模型文件和字符集文件创建文本识别器
    ///
    /// Create a text recognizer from model file and character set file
    pub fn from_file(model_path: impl AsRef<Path>, keys_path: impl AsRef<Path>) -> OcrResult<Self> {
        let interpreter = Interpreter::from_file(model_path)?;
        let keys_content = std::fs::read_to_string(keys_path)?;

        let keys = " "
            .chars()
            .chain(keys_content.chars().filter(|x| *x != '\n' && *x != '\r'))
            .chain(" ".chars())
            .collect();

        Ok(Self {
            interpreter,
            session: None,
            keys,
            min_score: Self::MIN_SCORE_DEFAULT,
            punct_min_score: Self::PUNCT_MIN_SCORE_DEFAULT,
        })
    }

    /// 设置常规字符的最小识别置信度阈值
    ///
    /// Set the minimum confidence threshold for regular characters
    pub fn with_min_score(mut self, min_score: f32) -> Self {
        self.min_score = min_score;
        self
    }

    /// 设置标点符号的最小识别置信度阈值
    ///
    /// Set the minimum confidence threshold for punctuation characters
    pub fn with_punct_min_score(mut self, punct_min_score: f32) -> Self {
        self.punct_min_score = punct_min_score;
        self
    }

    #[inline]
    fn is_punctuation(&self, ch: char) -> bool {
        Self::PUNCTUATIONS.contains(&ch)
    }

    /// 识别图像中的文本，返回字符及其置信度
    ///
    /// Recognize text in the image, returning characters and their confidence scores
    pub fn predict_char_score(&mut self, img: &DynamicImage) -> OcrResult<Vec<(char, f32)>> {
        let input = Self::preprocess(img)?;
        let output = self.run_model(&input)?;
        Ok(output)
    }

    /// 识别图像中的文本，返回字符串
    ///
    /// Recognize text in the image, returning a string
    pub fn predict_str(&mut self, img: &DynamicImage) -> OcrResult<String> {
        let ret = self.predict_char_score(img)?;
        Ok(ret.into_iter().map(|x| x.0).collect())
    }

    fn preprocess(img: &DynamicImage) -> OcrResult<ArrayBase<OwnedRepr<f32>, Dim<[usize; 4]>>> {
        let (w, h) = img.dimensions();
        let img = if h <= 48 {
            Cow::Borrowed(img)
        } else {
            Cow::Owned(img.resize_exact(w * 48 / h, 48, image::imageops::FilterType::CatmullRom))
        };

        let (w, h) = img.dimensions();
        let mut input = Array::zeros((1, 3, h as usize, w as usize));

        const MEAN: f32 = 0.5;
        const STD: f32 = 0.5;

        for pixel in img.pixels() {
            let x = pixel.0 as usize;
            let y = pixel.1 as usize;
            let [r, g, b, _] = pixel.2.0;

            input[[0, 0, y, x]] = (r as f32 / 255.0 - MEAN) / STD;
            input[[0, 1, y, x]] = (g as f32 / 255.0 - MEAN) / STD;
            input[[0, 2, y, x]] = (b as f32 / 255.0 - MEAN) / STD;
        }

        Ok(input)
    }

    fn run_model(
        &mut self,
        input: &ArrayBase<OwnedRepr<f32>, Dim<[usize; 4]>>,
    ) -> OcrResult<Vec<(char, f32)>> {
        if self.session.is_none() {
            let mut config = ScheduleConfig::new();
            config.set_type(ForwardType::Auto);
            let mut backend_config = BackendConfig::new();
            backend_config.set_precision_mode(PrecisionMode::High);
            backend_config.set_power_mode(PowerMode::High);
            config.set_backend_config(backend_config);

            let session = self.interpreter.create_session(config)?;
            self.session = Some(session);
        }

        let input_shape = input.shape();
        {
            let session = self.session.as_mut().unwrap();
            let mut input_tensor =
                unsafe { self.interpreter.input_unresized::<f32>(session, "x")? };

            self.interpreter.resize_tensor(
                &mut input_tensor,
                [
                    input_shape[0] as i32,
                    input_shape[1] as i32,
                    input_shape[2] as i32,
                    input_shape[3] as i32,
                ],
            );

            drop(input_tensor);

            self.interpreter.resize_session(session);
        }

        let (output_data, output_shape) = {
            let session = self.session.as_mut().unwrap();
            let mut input_tensor = self.interpreter.input::<f32>(session, "x")?;

            if let Some(flat_data) = input.as_slice() {
                let mut host_tensor = input_tensor.create_host_tensor_from_device(false);
                let host_data_mut = host_tensor.host_mut();
                host_data_mut.copy_from_slice(flat_data);
                input_tensor.copy_from_host_tensor(&host_tensor)?;
            } else {
                let mut host_tensor = input_tensor.create_host_tensor_from_device(false);
                let host_data_mut = host_tensor.host_mut();
                for (i, val) in input.iter().enumerate() {
                    host_data_mut[i] = *val;
                }
                input_tensor.copy_from_host_tensor(&host_tensor)?;
            }

            self.interpreter.run_session(session)?;

            let output = self
                .interpreter
                .output::<f32>(session, "softmax_11.tmp_0")?;
            output.wait(mnn::ffi::MapType::MAP_TENSOR_READ, true);

            let shape = output.shape();
            let output_host_tensor = output.create_host_tensor_from_device(true);
            (output_host_tensor.host().to_vec(), shape)
        };

        let sequence_length = output_shape[1] as usize;
        let vocab_size = output_shape[2] as usize;

        let mut results = Vec::with_capacity(sequence_length);
        let mut last_char: Option<char> = None;

        for i in 0..sequence_length {
            let mut max_idx = 0;
            let mut max_score = 0.0f32;

            for j in 0..vocab_size {
                let offset = i * vocab_size + j;
                if offset < output_data.len() && output_data[offset] > max_score {
                    max_score = output_data[offset];
                    max_idx = j;
                }
            }

            if max_idx > 0 && max_idx < self.keys.len() {
                if let Some(&ch) = self.keys.get(max_idx) {
                    let threshold = if self.is_punctuation(ch) {
                        self.punct_min_score
                    } else {
                        self.min_score
                    };

                    if max_score > threshold {
                        if last_char != Some(ch) || self.is_punctuation(ch) {
                            results.push((ch, max_score));
                        }
                        last_char = Some(ch);
                    } else {
                        if self.is_punctuation(ch) && max_score > self.punct_min_score * 0.8 {
                            results.push((ch, max_score));
                        } else {
                            last_char = None;
                        }
                    }
                }
            } else {
                last_char = None;
            }
        }

        let mut final_results = Vec::with_capacity(results.len());
        let mut i = 0;
        while i < results.len() {
            let (ch, score) = results[i];
            final_results.push((ch, score));

            if self.is_punctuation(ch) {
                while i + 1 < results.len() && results[i + 1].0 == ch {
                    i += 1;
                }
            }

            i += 1;
        }

        Ok(final_results)
    }
}
