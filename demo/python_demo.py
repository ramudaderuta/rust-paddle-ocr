import ctypes
import os
import sys
from ctypes import Structure, c_char_p, c_int, c_uint, c_float, c_size_t, POINTER

# 添加库路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载动态库
try:
    lib = ctypes.CDLL("../target/release/librust_paddle_ocr.so")  # Linux
except OSError:
    try:
        lib = ctypes.CDLL("../target/release/librust_paddle_ocr.dylib")  # macOS
    except OSError:
        lib = ctypes.CDLL("../target/release/librust_paddle_ocr.dll")  # Windows

# 定义状态枚举
class RocrStatus:
    Success = 0
    InvalidHandle = 1
    NullPointer = 2
    FileNotFound = 3
    InvalidImageFormat = 4
    ModelLoadError = 5
    RecognitionError = 6
    Unknown = 7

# 定义结构体
class RocrTextBox(Structure):
    _fields_ = [
        ("TEXT", c_char_p),
        ("CONFIDENCE", c_float),
        ("LEFT", c_int),
        ("TOP", c_int),
        ("WIDTH", c_uint),
        ("HEIGHT", c_uint)
    ]

class RocrSimpleResult(Structure):
    _fields_ = [
        ("STATUS", c_int),
        ("COUNT", c_size_t),
        ("TEXTS", POINTER(c_char_p))
    ]

class RocrResult(Structure):
    _fields_ = [
        ("STATUS", c_int),
        ("COUNT", c_size_t),
        ("BOXES", POINTER(RocrTextBox))
    ]

# 定义函数签名
lib.rocr_version.restype = c_char_p

lib.rocr_create_engine.argtypes = [c_char_p, c_char_p, c_char_p]
lib.rocr_create_engine.restype = ctypes.c_void_p

lib.rocr_recognize_simple.argtypes = [ctypes.c_void_p, c_char_p]
lib.rocr_recognize_simple.restype = RocrSimpleResult

lib.rocr_recognize_detailed.argtypes = [ctypes.c_void_p, c_char_p]
lib.rocr_recognize_detailed.restype = RocrResult

lib.rocr_free_simple_result.argtypes = [POINTER(RocrSimpleResult)]
lib.rocr_free_simple_result.restype = None

lib.rocr_free_result.argtypes = [POINTER(RocrResult)]
lib.rocr_free_result.restype = None

lib.rocr_destroy_engine.argtypes = [ctypes.c_void_p]
lib.rocr_destroy_engine.restype = c_int

lib.rocr_cleanup.restype = None

def main():
    print("=== Rust PaddleOCR Python API Demo ===")
    
    # 模型文件路径
    det_model = b"../models/PP-OCRv5_mobile_det_fp16.mnn"
    rec_model = b"../models/PP-OCRv5_mobile_rec_fp16.mnn"
    keys_file = b"../models/ppocr_keys_v5.txt"
    image_file = b"../res/4.png"
    
    # 显示版本信息
    version = lib.rocr_version().decode('utf-8')
    print(f"OCR库版本: {version}\n")
    
    # 创建OCR引擎
    print("正在创建OCR引擎...")
    engine = lib.rocr_create_engine(det_model, rec_model, keys_file)
    
    if engine == 0:
        print("✗ OCR引擎创建失败")
        return 1
    
    print("✓ OCR引擎创建成功\n")
    
    # 简单模式识别
    print("开始简单模式识别...")
    simple_result = lib.rocr_recognize_simple(engine, image_file)
    
    if simple_result.STATUS == RocrStatus.Success:
        print(f"识别成功，共识别出 {simple_result.COUNT} 个文本:")
        for i in range(simple_result.COUNT):
            text = simple_result.TEXTS[i].decode('utf-8')
            print(f"  - {text}")
    else:
        print(f"简单模式识别失败，状态码: {simple_result.STATUS}")
    
    # 释放简单结果内存
    lib.rocr_free_simple_result(ctypes.byref(simple_result))
    
    print()
    
    # 详细模式识别
    print("开始详细模式识别...")
    detailed_result = lib.rocr_recognize_detailed(engine, image_file)
    
    if detailed_result.STATUS == RocrStatus.Success:
        print(f"详细识别成功，共识别出 {detailed_result.COUNT} 个文本框:")
        for i in range(detailed_result.COUNT):
            box = detailed_result.BOXES[i]
            text = box.TEXT.decode('utf-8')
            print(f"  文本: {text}")
            print(f"  置信度: {box.CONFIDENCE:.2f}")
            print(f"  位置: ({box.LEFT}, {box.TOP}, {box.WIDTH}, {box.HEIGHT})")
            print("  ---")
    else:
        print(f"详细模式识别失败，状态码: {detailed_result.STATUS}")
    
    # 释放详细结果内存
    lib.rocr_free_result(ctypes.byref(detailed_result))
    
    # 销毁引擎
    destroy_status = lib.rocr_destroy_engine(engine)
    if destroy_status == RocrStatus.Success:
        print("\n✓ OCR引擎销毁成功")
    else:
        print(f"\n✗ OCR引擎销毁失败，状态码: {destroy_status}")
    
    # 清理资源
    lib.rocr_cleanup()
    
    print("\nDemo 完成!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
