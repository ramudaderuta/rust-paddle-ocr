use crate::{OcrEngine, OcrError};
use image::open as image_open;
use libc::{c_char, c_float, c_int, c_uint, size_t};
use std::collections::HashMap;
use std::ffi::{CStr, CString};
use std::ptr;
use std::slice;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;

/// OCR结果状态码
#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum RocrStatus {
    Success = 0,
    InitError = 1,
    FileNotFound = 2,
    ImageLoadError = 3,
    ProcessError = 4,
    MemoryError = 5,
    InvalidParam = 6,
    NotInitialized = 7,
}

/// 文本框位置信息
#[repr(C)]
#[derive(Debug, Clone)]
pub struct RocrTextBox {
    pub text: *mut c_char,
    pub confidence: c_float,
    pub left: c_int,
    pub top: c_int,
    pub width: c_uint,
    pub height: c_uint,
}

/// OCR结果
#[repr(C)]
#[derive(Debug)]
pub struct RocrResult {
    pub status: RocrStatus,
    pub count: size_t,
    pub boxes: *mut RocrTextBox,
}

/// 简单文本结果
#[repr(C)]
#[derive(Debug)]
pub struct RocrSimpleResult {
    pub status: RocrStatus,
    pub count: size_t,
    pub texts: *mut *mut c_char,
}

impl From<OcrError> for RocrStatus {
    fn from(error: OcrError) -> Self {
        match error {
            OcrError::IOError(_) => RocrStatus::FileNotFound,
            OcrError::ImageError(_) => RocrStatus::ImageLoadError,
            OcrError::MNNError(_) => RocrStatus::ProcessError,
            OcrError::EngineError(_) => RocrStatus::NotInitialized,
            OcrError::InputError(_) => RocrStatus::InvalidParam,
            OcrError::OutputError(_) => RocrStatus::ProcessError,
            _ => RocrStatus::ProcessError,
        }
    }
}

/// OCR引擎句柄类型
pub type RocrHandle = size_t;

/// 全局引擎管理器，用于存储和管理引擎实例
static ENGINES: once_cell::sync::OnceCell<Mutex<HashMap<RocrHandle, OcrEngine>>> =
    once_cell::sync::OnceCell::new();
static NEXT_HANDLE: AtomicUsize = AtomicUsize::new(1);

/// 获取下一个可用的句柄ID
fn get_next_handle() -> RocrHandle {
    NEXT_HANDLE.fetch_add(1, Ordering::SeqCst)
}

/// 获取全局引擎映射表
fn get_engines() -> &'static Mutex<HashMap<RocrHandle, OcrEngine>> {
    ENGINES.get_or_init(|| Mutex::new(HashMap::new()))
}

/// 初始化OCR引擎，返回引擎句柄
#[no_mangle]
pub extern "C" fn rocr_create_engine(
    det_model_path: *const c_char,
    rec_model_path: *const c_char,
    keys_path: *const c_char,
) -> RocrHandle {
    if det_model_path.is_null() || rec_model_path.is_null() || keys_path.is_null() {
        return 0;
    }

    let det_path = match unsafe { CStr::from_ptr(det_model_path) }.to_str() {
        Ok(path) => path,
        Err(_) => return 0,
    };

    let rec_path = match unsafe { CStr::from_ptr(rec_model_path) }.to_str() {
        Ok(path) => path,
        Err(_) => return 0,
    };

    let keys_path = match unsafe { CStr::from_ptr(keys_path) }.to_str() {
        Ok(path) => path,
        Err(_) => return 0,
    };

    match OcrEngine::new(det_path, rec_path, keys_path) {
        Ok(engine) => {
            let handle = get_next_handle();
            let engines = get_engines();
            if let Ok(mut map) = engines.lock() {
                map.insert(handle, engine);
                handle
            } else {
                0
            }
        }
        Err(_) => 0,
    }
}

/// 使用自定义配置创建OCR引擎，返回引擎句柄
#[no_mangle]
pub extern "C" fn rocr_create_engine_with_config(
    det_model_path: *const c_char,
    rec_model_path: *const c_char,
    keys_path: *const c_char,
    rect_border_size: c_uint,
    merge_boxes: c_int,
    merge_threshold: c_int,
) -> RocrHandle {
    if det_model_path.is_null() || rec_model_path.is_null() || keys_path.is_null() {
        return 0;
    }

    let det_path = match unsafe { CStr::from_ptr(det_model_path) }.to_str() {
        Ok(path) => path,
        Err(_) => return 0,
    };

    let rec_path = match unsafe { CStr::from_ptr(rec_model_path) }.to_str() {
        Ok(path) => path,
        Err(_) => return 0,
    };

    let keys_path = match unsafe { CStr::from_ptr(keys_path) }.to_str() {
        Ok(path) => path,
        Err(_) => return 0,
    };

    match OcrEngine::new_with_config(
        det_path,
        rec_path,
        keys_path,
        rect_border_size,
        merge_boxes != 0,
        merge_threshold,
    ) {
        Ok(engine) => {
            let handle = get_next_handle();
            let engines = get_engines();
            if let Ok(mut map) = engines.lock() {
                map.insert(handle, engine);
                handle
            } else {
                0
            }
        }
        Err(_) => 0,
    }
}

/// 使用字节数据创建OCR引擎，返回引擎句柄
#[no_mangle]
pub extern "C" fn rocr_create_engine_with_bytes(
    det_model_data: *const u8,
    det_model_size: size_t,
    rec_model_data: *const u8,
    rec_model_size: size_t,
    keys_data: *const u8,
    keys_size: size_t,
    rect_border_size: c_uint,
    merge_boxes: c_int,
    merge_threshold: c_int,
) -> RocrHandle {
    if det_model_data.is_null()
        || rec_model_data.is_null()
        || keys_data.is_null()
        || det_model_size == 0
        || rec_model_size == 0
        || keys_size == 0
    {
        return 0;
    }

    let det_bytes = unsafe { slice::from_raw_parts(det_model_data, det_model_size) };
    let rec_bytes = unsafe { slice::from_raw_parts(rec_model_data, rec_model_size) };
    let keys_bytes = unsafe { slice::from_raw_parts(keys_data, keys_size) };

    match OcrEngine::new_with_config_and_bytes(
        det_bytes,
        rec_bytes,
        keys_bytes,
        rect_border_size,
        merge_boxes != 0,
        merge_threshold,
    ) {
        Ok(engine) => {
            let handle = get_next_handle();
            let engines = get_engines();
            if let Ok(mut map) = engines.lock() {
                map.insert(handle, engine);
                handle
            } else {
                0
            }
        }
        Err(_) => 0,
    }
}

/// 销毁OCR引擎实例
#[no_mangle]
pub extern "C" fn rocr_destroy_engine(handle: RocrHandle) -> RocrStatus {
    if handle == 0 {
        return RocrStatus::InvalidParam;
    }

    let engines = get_engines();
    match engines.lock() {
        Ok(mut map) => {
            if map.remove(&handle).is_some() {
                RocrStatus::Success
            } else {
                RocrStatus::InvalidParam
            }
        }
        Err(_) => RocrStatus::ProcessError,
    }
}

/// 识别图像中的文本（详细模式）
#[no_mangle]
pub extern "C" fn rocr_recognize_detailed(
    handle: RocrHandle,
    image_path: *const c_char,
) -> RocrResult {
    if handle == 0 || image_path.is_null() {
        return RocrResult {
            status: RocrStatus::InvalidParam,
            count: 0,
            boxes: ptr::null_mut(),
        };
    }

    let path = match unsafe { CStr::from_ptr(image_path) }.to_str() {
        Ok(path) => path,
        Err(_) => {
            return RocrResult {
                status: RocrStatus::InvalidParam,
                count: 0,
                boxes: ptr::null_mut(),
            }
        }
    };

    // 加载图像
    let img = match image_open(path) {
        Ok(img) => img,
        Err(_) => {
            return RocrResult {
                status: RocrStatus::ImageLoadError,
                count: 0,
                boxes: ptr::null_mut(),
            }
        }
    };

    let engines = get_engines();
    let engines_guard = match engines.lock() {
        Ok(guard) => guard,
        Err(_) => {
            return RocrResult {
                status: RocrStatus::ProcessError,
                count: 0,
                boxes: ptr::null_mut(),
            }
        }
    };

    let engine = match engines_guard.get(&handle) {
        Some(engine) => engine,
        None => {
            return RocrResult {
                status: RocrStatus::NotInitialized,
                count: 0,
                boxes: ptr::null_mut(),
            }
        }
    };

    // 获取文本区域矩形框
    let text_rects = match engine.get_text_rects(&img) {
        Ok(rects) => rects,
        Err(e) => {
            return RocrResult {
                status: e.into(),
                count: 0,
                boxes: ptr::null_mut(),
            }
        }
    };

    if text_rects.is_empty() {
        return RocrResult {
            status: RocrStatus::Success,
            count: 0,
            boxes: ptr::null_mut(),
        };
    }

    // 获取文本区域图像
    let text_images = match engine.get_text_images(&img) {
        Ok(images) => images,
        Err(e) => {
            return RocrResult {
                status: e.into(),
                count: 0,
                boxes: ptr::null_mut(),
            }
        }
    };

    // 分配结果数组
    let count = text_rects.len();
    let boxes =
        unsafe { libc::malloc(count * std::mem::size_of::<RocrTextBox>()) as *mut RocrTextBox };

    if boxes.is_null() {
        return RocrResult {
            status: RocrStatus::MemoryError,
            count: 0,
            boxes: ptr::null_mut(),
        };
    }

    let boxes_slice = unsafe { slice::from_raw_parts_mut(boxes, count) };

    let mut valid_count = 0;
    for (i, (rect, text_img)) in text_rects.iter().zip(text_images.iter()).enumerate() {
        if i >= count {
            break;
        }

        match engine.recognize_text(text_img.clone()) {
            Ok(text) => {
                // 将Rust字符串转换为C字符串
                let c_text = match CString::new(text) {
                    Ok(c_str) => {
                        let ptr =
                            unsafe { libc::malloc(c_str.as_bytes_with_nul().len()) as *mut c_char };
                        if ptr.is_null() {
                            continue;
                        }
                        unsafe {
                            libc::strcpy(ptr, c_str.as_ptr());
                        }
                        ptr
                    }
                    Err(_) => continue,
                };

                boxes_slice[valid_count] = RocrTextBox {
                    text: c_text,
                    confidence: 1.0,
                    left: rect.left(),
                    top: rect.top(),
                    width: rect.width(),
                    height: rect.height(),
                };
                valid_count += 1;
            }
            Err(_) => continue,
        }
    }

    RocrResult {
        status: RocrStatus::Success,
        count: valid_count,
        boxes,
    }
}

/// 识别图像中的文本（简单模式）
#[no_mangle]
pub extern "C" fn rocr_recognize_simple(
    handle: RocrHandle,
    image_path: *const c_char,
) -> RocrSimpleResult {
    if handle == 0 || image_path.is_null() {
        return RocrSimpleResult {
            status: RocrStatus::InvalidParam,
            count: 0,
            texts: ptr::null_mut(),
        };
    }

    let path = match unsafe { CStr::from_ptr(image_path) }.to_str() {
        Ok(path) => path,
        Err(_) => {
            return RocrSimpleResult {
                status: RocrStatus::InvalidParam,
                count: 0,
                texts: ptr::null_mut(),
            }
        }
    };

    // 加载图像
    let img = match image_open(path) {
        Ok(img) => img,
        Err(_) => {
            return RocrSimpleResult {
                status: RocrStatus::ImageLoadError,
                count: 0,
                texts: ptr::null_mut(),
            }
        }
    };

    let engines = get_engines();
    let engines_guard = match engines.lock() {
        Ok(guard) => guard,
        Err(_) => {
            return RocrSimpleResult {
                status: RocrStatus::ProcessError,
                count: 0,
                texts: ptr::null_mut(),
            }
        }
    };

    let engine = match engines_guard.get(&handle) {
        Some(engine) => engine,
        None => {
            return RocrSimpleResult {
                status: RocrStatus::NotInitialized,
                count: 0,
                texts: ptr::null_mut(),
            }
        }
    };

    // 处理OCR
    let texts = match engine.process_ocr(img) {
        Ok(texts) => texts,
        Err(e) => {
            return RocrSimpleResult {
                status: e.into(),
                count: 0,
                texts: ptr::null_mut(),
            }
        }
    };

    if texts.is_empty() {
        return RocrSimpleResult {
            status: RocrStatus::Success,
            count: 0,
            texts: ptr::null_mut(),
        };
    }

    // 分配文本指针数组
    let count = texts.len();
    let text_ptrs =
        unsafe { libc::malloc(count * std::mem::size_of::<*mut c_char>()) as *mut *mut c_char };

    if text_ptrs.is_null() {
        return RocrSimpleResult {
            status: RocrStatus::MemoryError,
            count: 0,
            texts: ptr::null_mut(),
        };
    }

    let text_ptrs_slice = unsafe { slice::from_raw_parts_mut(text_ptrs, count) };

    let mut valid_count = 0;
    for (i, text) in texts.iter().enumerate() {
        if i >= count {
            break;
        }

        match CString::new(text.clone()) {
            Ok(c_str) => {
                let ptr = unsafe { libc::malloc(c_str.as_bytes_with_nul().len()) as *mut c_char };
                if ptr.is_null() {
                    continue;
                }
                unsafe {
                    libc::strcpy(ptr, c_str.as_ptr());
                }
                text_ptrs_slice[valid_count] = ptr;
                valid_count += 1;
            }
            Err(_) => continue,
        }
    }

    RocrSimpleResult {
        status: RocrStatus::Success,
        count: valid_count,
        texts: text_ptrs,
    }
}

/// 释放详细结果的内存
#[no_mangle]
pub extern "C" fn rocr_free_result(result: *mut RocrResult) {
    if result.is_null() {
        return;
    }

    let result_ref = unsafe { &mut *result };

    if !result_ref.boxes.is_null() && result_ref.count > 0 {
        let boxes_slice = unsafe { slice::from_raw_parts_mut(result_ref.boxes, result_ref.count) };

        // 释放每个文本框的文本内存
        for box_ref in boxes_slice {
            if !box_ref.text.is_null() {
                unsafe {
                    libc::free(box_ref.text as *mut libc::c_void);
                }
            }
        }

        // 释放文本框数组
        unsafe {
            libc::free(result_ref.boxes as *mut libc::c_void);
        }
    }

    result_ref.boxes = ptr::null_mut();
    result_ref.count = 0;
}

/// 释放简单结果的内存
#[no_mangle]
pub extern "C" fn rocr_free_simple_result(result: *mut RocrSimpleResult) {
    if result.is_null() {
        return;
    }

    let result_ref = unsafe { &mut *result };

    if !result_ref.texts.is_null() && result_ref.count > 0 {
        let text_ptrs_slice =
            unsafe { slice::from_raw_parts_mut(result_ref.texts, result_ref.count) };

        // 释放每个文本字符串的内存
        for text_ptr in text_ptrs_slice {
            if !text_ptr.is_null() {
                unsafe {
                    libc::free(*text_ptr as *mut libc::c_void);
                }
            }
        }

        // 释放文本指针数组
        unsafe {
            libc::free(result_ref.texts as *mut libc::c_void);
        }
    }

    result_ref.texts = ptr::null_mut();
    result_ref.count = 0;
}

/// 释放所有OCR引擎资源
#[no_mangle]
pub extern "C" fn rocr_cleanup() {
    let engines = get_engines();
    if let Ok(mut map) = engines.lock() {
        map.clear();
    }
}

/// 获取版本信息
#[no_mangle]
pub extern "C" fn rocr_version() -> *const c_char {
    static VERSION: &str = concat!(env!("CARGO_PKG_VERSION"), "\0");
    VERSION.as_ptr() as *const c_char
}
