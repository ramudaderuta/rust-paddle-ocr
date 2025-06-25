import ctypes
from ctypes import Structure, POINTER, c_char_p, c_float, c_int, c_uint, c_size_t, c_uint8, c_void_p
from enum import IntEnum
from typing import List, Tuple, Optional
import os
import time
import threading
import gc
import statistics
import resource
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# 获取动态库路径
LIB_PATH = os.path.join(os.path.dirname(__file__), "target/release/librust_paddle_ocr.dylib")

class RocrStatus(IntEnum):
    """OCR结果状态码"""
    SUCCESS = 0
    INIT_ERROR = 1
    FILE_NOT_FOUND = 2
    IMAGE_LOAD_ERROR = 3
    PROCESS_ERROR = 4
    MEMORY_ERROR = 5
    INVALID_PARAM = 6
    NOT_INITIALIZED = 7

class RocrTextBox(Structure):
    """文本框位置信息结构体"""
    _fields_ = [
        ("text", c_char_p),
        ("confidence", c_float),
        ("left", c_int),
        ("top", c_int),
        ("width", c_uint),
        ("height", c_uint),
    ]

class RocrResult(Structure):
    """OCR详细结果结构体"""
    _fields_ = [
        ("status", c_int),
        ("count", c_size_t),
        ("boxes", POINTER(RocrTextBox)),
    ]

class RocrSimpleResult(Structure):
    """简单文本结果结构体"""
    _fields_ = [
        ("status", c_int),
        ("count", c_size_t),
        ("texts", POINTER(c_char_p)),
    ]

class RocrEngine:
    """OCR引擎Python包装类"""
    
    def __init__(self, lib_path: str = LIB_PATH):
        """初始化OCR引擎包装器
        
        Args:
            lib_path: 动态库文件路径
        """
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"动态库文件未找到: {lib_path}")
        
        # 加载动态库
        self.lib = ctypes.CDLL(lib_path)
        self._setup_function_signatures()
        self.handle = 0
    
    def _setup_function_signatures(self):
        """设置函数签名"""
        # rocr_create_engine
        self.lib.rocr_create_engine.argtypes = [c_char_p, c_char_p, c_char_p]
        self.lib.rocr_create_engine.restype = c_size_t
        
        # rocr_create_engine_with_config
        self.lib.rocr_create_engine_with_config.argtypes = [
            c_char_p, c_char_p, c_char_p, c_uint, c_int, c_int
        ]
        self.lib.rocr_create_engine_with_config.restype = c_size_t
        
        # rocr_create_engine_with_bytes
        self.lib.rocr_create_engine_with_bytes.argtypes = [
            POINTER(c_uint8), c_size_t, POINTER(c_uint8), c_size_t,
            POINTER(c_uint8), c_size_t, c_uint, c_int, c_int
        ]
        self.lib.rocr_create_engine_with_bytes.restype = c_size_t
        
        # rocr_destroy_engine
        self.lib.rocr_destroy_engine.argtypes = [c_size_t]
        self.lib.rocr_destroy_engine.restype = c_int
        
        # rocr_recognize_detailed
        self.lib.rocr_recognize_detailed.argtypes = [c_size_t, c_char_p]
        self.lib.rocr_recognize_detailed.restype = RocrResult
        
        # rocr_recognize_simple
        self.lib.rocr_recognize_simple.argtypes = [c_size_t, c_char_p]
        self.lib.rocr_recognize_simple.restype = RocrSimpleResult
        
        # rocr_free_result
        self.lib.rocr_free_result.argtypes = [POINTER(RocrResult)]
        self.lib.rocr_free_result.restype = None
        
        # rocr_free_simple_result
        self.lib.rocr_free_simple_result.argtypes = [POINTER(RocrSimpleResult)]
        self.lib.rocr_free_simple_result.restype = None
        
        # rocr_cleanup
        self.lib.rocr_cleanup.argtypes = []
        self.lib.rocr_cleanup.restype = None
        
        # rocr_version
        self.lib.rocr_version.argtypes = []
        self.lib.rocr_version.restype = c_char_p
    
    def create_engine(self, det_model_path: str, rec_model_path: str, keys_path: str) -> bool:
        """创建OCR引擎
        
        Args:
            det_model_path: 文本检测模型文件路径
            rec_model_path: 文本识别模型文件路径
            keys_path: 字符集文件路径
            
        Returns:
            bool: 创建成功返回True，失败返回False
        """
        det_path_bytes = det_model_path.encode('utf-8')
        rec_path_bytes = rec_model_path.encode('utf-8')
        keys_path_bytes = keys_path.encode('utf-8')
        
        self.handle = self.lib.rocr_create_engine(
            det_path_bytes, rec_path_bytes, keys_path_bytes
        )
        return self.handle != 0
    
    def create_engine_with_config(
        self, 
        det_model_path: str, 
        rec_model_path: str, 
        keys_path: str,
        rect_border_size: int = 50,
        merge_boxes: bool = False,
        merge_threshold: int = 10
    ) -> bool:
        """使用自定义配置创建OCR引擎
        
        Args:
            det_model_path: 文本检测模型文件路径
            rec_model_path: 文本识别模型文件路径
            keys_path: 字符集文件路径
            rect_border_size: 文本框边框大小
            merge_boxes: 是否合并文本框
            merge_threshold: 合并阈值
            
        Returns:
            bool: 创建成功返回True，失败返回False
        """
        det_path_bytes = det_model_path.encode('utf-8')
        rec_path_bytes = rec_model_path.encode('utf-8')
        keys_path_bytes = keys_path.encode('utf-8')
        
        self.handle = self.lib.rocr_create_engine_with_config(
            det_path_bytes, rec_path_bytes, keys_path_bytes,
            rect_border_size, 1 if merge_boxes else 0, merge_threshold
        )
        return self.handle != 0
    
    def create_engine_with_bytes(
        self,
        det_model_data: bytes,
        rec_model_data: bytes,
        keys_data: bytes,
        rect_border_size: int = 50,
        merge_boxes: bool = False,
        merge_threshold: int = 10
    ) -> bool:
        """使用字节数据创建OCR引擎
        
        Args:
            det_model_data: 文本检测模型数据
            rec_model_data: 文本识别模型数据
            keys_data: 字符集数据
            rect_border_size: 文本框边框大小
            merge_boxes: 是否合并文本框
            merge_threshold: 合并阈值
            
        Returns:
            bool: 创建成功返回True，失败返回False
        """
        det_array = (c_uint8 * len(det_model_data)).from_buffer_copy(det_model_data)
        rec_array = (c_uint8 * len(rec_model_data)).from_buffer_copy(rec_model_data)
        keys_array = (c_uint8 * len(keys_data)).from_buffer_copy(keys_data)
        
        self.handle = self.lib.rocr_create_engine_with_bytes(
            det_array, len(det_model_data),
            rec_array, len(rec_model_data),
            keys_array, len(keys_data),
            rect_border_size, 1 if merge_boxes else 0, merge_threshold
        )
        return self.handle != 0
    
    def recognize_detailed(self, image_path: str) -> Tuple[RocrStatus, List[dict]]:
        """识别图像中的文本（详细模式）
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            Tuple[RocrStatus, List[dict]]: 状态码和文本框信息列表
        """
        if self.handle == 0:
            return RocrStatus.NOT_INITIALIZED, []
        
        image_path_bytes = image_path.encode('utf-8')
        result = self.lib.rocr_recognize_detailed(self.handle, image_path_bytes)
        
        status = RocrStatus(result.status)
        text_boxes = []
                
        if status == RocrStatus.SUCCESS and result.count > 0:
            for i in range(result.count):
                box = result.boxes[i]
                text = box.text.decode('utf-8') if box.text else ''
                text_boxes.append({
                    'text': text,
                    'confidence': box.confidence,
                    'left': box.left,
                    'top': box.top,
                    'width': box.width,
                    'height': box.height,
                })
        elif status != RocrStatus.SUCCESS:
            print(f"识别失败，状态码: {status}")
        
        # 释放内存
        self.lib.rocr_free_result(ctypes.byref(result))
        
        return status, text_boxes
    
    def recognize_simple(self, image_path: str) -> Tuple[RocrStatus, List[str]]:
        """识别图像中的文本（简单模式）
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            Tuple[RocrStatus, List[str]]: 状态码和文本列表
        """
        if self.handle == 0:
            return RocrStatus.NOT_INITIALIZED, []
        
        image_path_bytes = image_path.encode('utf-8')
        result = self.lib.rocr_recognize_simple(self.handle, image_path_bytes)
        
        status = RocrStatus(result.status)
        texts = []
        
        
        if status == RocrStatus.SUCCESS and result.count > 0:
            for i in range(result.count):
                text_ptr = result.texts[i]
                if text_ptr:
                    text = text_ptr.decode('utf-8')
                    texts.append(text)
        elif status != RocrStatus.SUCCESS:
            print(f"识别失败，状态码: {status}")
        
        # 释放内存
        self.lib.rocr_free_simple_result(ctypes.byref(result))
        
        return status, texts
    
    def destroy_engine(self) -> RocrStatus:
        """销毁OCR引擎实例"""
        if self.handle == 0:
            return RocrStatus.NOT_INITIALIZED
        
        status = RocrStatus(self.lib.rocr_destroy_engine(self.handle))
        if status == RocrStatus.SUCCESS:
            self.handle = 0
        return status
    
    def get_version(self) -> str:
        """获取版本信息"""
        version_ptr = self.lib.rocr_version()
        return version_ptr.decode('utf-8') if version_ptr else ""
    
    def cleanup(self):
        """清理所有资源"""
        self.lib.rocr_cleanup()
        self.handle = 0
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        if self.handle != 0:
            self.destroy_engine()

# 便捷函数
def create_ocr_engine(det_model_path: str, rec_model_path: str, keys_path: str) -> Optional[RocrEngine]:
    """创建OCR引擎的便捷函数
    
    Args:
        det_model_path: 文本检测模型文件路径
        rec_model_path: 文本识别模型文件路径
        keys_path: 字符集文件路径
        
    Returns:
        Optional[RocrEngine]: 成功返回引擎实例，失败返回None
    """
    engine = RocrEngine()
    if engine.create_engine(det_model_path, rec_model_path, keys_path):
        return engine
    return None

def ocr_recognize_text(image_path: str, det_model_path: str, rec_model_path: str, keys_path: str) -> List[str]:
    """一键OCR识别文本的便捷函数
    
    Args:
        image_path: 图像文件路径
        det_model_path: 文本检测模型文件路径
        rec_model_path: 文本识别模型文件路径
        keys_path: 字符集文件路径
        
    Returns:
        List[str]: 识别出的文本列表
    """
    with RocrEngine() as engine:
        if engine.create_engine(det_model_path, rec_model_path, keys_path):
            status, texts = engine.recognize_simple(image_path)
            if status == RocrStatus.SUCCESS:
                return texts
    return []

@dataclass
class TestResult:
    """测试结果数据类"""
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    success_count: int
    error_count: int
    memory_before: float
    memory_after: float
    memory_peak: float
    error_details: List[str]

class MemoryMonitor:
    """内存监控器（使用标准库）"""
    
    def __init__(self):
        self.peak_memory = 0
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """开始监控内存"""
        self.monitoring = True
        self.peak_memory = self.get_memory_usage()
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控内存"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            current_memory = self.get_memory_usage()
            if current_memory > self.peak_memory:
                self.peak_memory = current_memory
            time.sleep(0.1)
    
    def get_memory_usage(self) -> float:
        """获取当前内存使用量(MB)"""
        try:
            # 使用resource模块获取内存使用情况
            if sys.platform == "darwin" or sys.platform.startswith("linux"):
                # macOS和Linux
                usage = resource.getrusage(resource.RUSAGE_SELF)
                if sys.platform == "darwin":
                    # macOS中ru_maxrss单位是字节
                    return usage.ru_maxrss / 1024 / 1024
                else:
                    # Linux中ru_maxrss单位是KB
                    return usage.ru_maxrss / 1024
            else:
                # Windows等其他平台，尝试读取/proc/self/status
                try:
                    with open('/proc/self/status', 'r') as f:
                        for line in f:
                            if line.startswith('VmRSS:'):
                                return int(line.split()[1]) / 1024  # KB to MB
                except:
                    pass
                # 如果无法获取具体数值，返回一个估算值
                return len(gc.get_objects()) * 0.001  # 粗略估算
        except Exception:
            # 如果所有方法都失败，返回对象数量作为内存使用的代理指标
            return len(gc.get_objects()) * 0.001
    
    def get_peak_memory(self) -> float:
        """获取峰值内存使用量(MB)"""
        return self.peak_memory

class RocrTester:
    """OCR引擎测试器（仅使用标准库）"""
    
    def __init__(self, engine: RocrEngine):
        self.engine = engine
        self.memory_monitor = MemoryMonitor()
    
    def test_inference_speed(self, image_path: str, iterations: int = 100) -> TestResult:
        """测试推理速度
        
        Args:
            image_path: 测试图像路径
            iterations: 测试迭代次数
            
        Returns:
            TestResult: 测试结果
        """
        print(f"开始速度测试，迭代次数: {iterations}")
        
        # 开始监控
        memory_before = self.memory_monitor.get_memory_usage()
        self.memory_monitor.start_monitoring()
        
        times = []
        success_count = 0
        error_count = 0
        errors = []
        
        # 预热
        print("预热中...")
        for _ in range(5):
            try:
                self.engine.recognize_simple(image_path)
            except Exception as e:
                print(f"预热时出错: {e}")
        
        # 正式测试
        print("正式测试中...")
        start_time = time.time()
        
        for i in range(iterations):
            iter_start = time.time()
            try:
                status, _ = self.engine.recognize_simple(image_path)
                iter_time = time.time() - iter_start
                times.append(iter_time)
                
                if status == RocrStatus.SUCCESS:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"迭代 {i}: 状态错误 {status}")
                    
            except Exception as e:
                iter_time = time.time() - iter_start
                times.append(iter_time)
                error_count += 1
                errors.append(f"迭代 {i}: 异常 {str(e)}")
            
            # 每10次迭代显示进度
            if (i + 1) % 10 == 0:
                print(f"  完成 {i + 1}/{iterations} 次测试")
        
        total_time = time.time() - start_time
        
        # 停止监控
        self.memory_monitor.stop_monitoring()
        memory_after = self.memory_monitor.get_memory_usage()
        memory_peak = self.memory_monitor.get_peak_memory()
        
        # 强制垃圾回收
        gc.collect()
        
        return TestResult(
            total_time=total_time,
            avg_time=statistics.mean(times) if times else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0,
            success_count=success_count,
            error_count=error_count,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_peak=memory_peak,
            error_details=errors
        )
    
    def test_memory_leak(self, image_path: str, iterations: int = 1000) -> TestResult:
        """测试内存泄露
        
        Args:
            image_path: 测试图像路径
            iterations: 测试迭代次数
            
        Returns:
            TestResult: 测试结果
        """
        print(f"开始内存泄露测试，迭代次数: {iterations}")
        
        # 初始内存快照
        gc.collect()
        memory_before = self.memory_monitor.get_memory_usage()
        self.memory_monitor.start_monitoring()
        
        times = []
        success_count = 0
        error_count = 0
        errors = []
        memory_samples = []
        object_counts = []  # 追踪对象数量变化
        
        start_time = time.time()
        
        for i in range(iterations):
            iter_start = time.time()
            
            try:
                status, _ = self.engine.recognize_simple(image_path)
                iter_time = time.time() - iter_start
                times.append(iter_time)
                
                if status == RocrStatus.SUCCESS:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"迭代 {i}: 状态错误 {status}")
                    
            except Exception as e:
                iter_time = time.time() - iter_start
                times.append(iter_time)
                error_count += 1
                errors.append(f"迭代 {i}: 异常 {str(e)}")
            
            # 每100次记录内存使用情况
            if (i + 1) % 10 == 0:
                current_memory = self.memory_monitor.get_memory_usage()
                current_objects = len(gc.get_objects())
                memory_samples.append(current_memory)
                object_counts.append(current_objects)
                print(f"  完成 {i + 1}/{iterations} 次测试，当前内存: {current_memory:.2f}MB, 对象数: {current_objects}")
        
        total_time = time.time() - start_time
        
        # 最终内存快照
        self.memory_monitor.stop_monitoring()
        gc.collect()
        time.sleep(1)  # 等待一秒确保资源释放
        memory_after = self.memory_monitor.get_memory_usage()
        memory_peak = self.memory_monitor.get_peak_memory()
        
        # 分析内存趋势
        if len(memory_samples) > 1:
            memory_trend = memory_samples[-1] - memory_samples[0]
            object_trend = object_counts[-1] - object_counts[0]
            print(f"内存趋势: {memory_trend:+.2f}MB")
            print(f"对象数量趋势: {object_trend:+d}")
            
            # 检测潜在的内存泄露
            if memory_trend > 10:  # 如果内存增长超过10MB
                errors.append(f"疑似内存泄露：内存增长 {memory_trend:.2f}MB")
            if object_trend > 1000:  # 如果对象数量增长超过1000
                errors.append(f"疑似对象泄露：对象数量增长 {object_trend}")
        
        return TestResult(
            total_time=total_time,
            avg_time=statistics.mean(times) if times else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0,
            success_count=success_count,
            error_count=error_count,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_peak=memory_peak,
            error_details=errors
        )
    
    def test_concurrent_access(self, image_path: str, num_threads: int = 4, iterations_per_thread: int = 50) -> TestResult:
        """测试并发访问
        
        Args:
            image_path: 测试图像路径
            num_threads: 线程数量
            iterations_per_thread: 每个线程的迭代次数
            
        Returns:
            TestResult: 测试结果
        """
        print(f"开始并发测试，{num_threads} 个线程，每线程 {iterations_per_thread} 次迭代")
        
        memory_before = self.memory_monitor.get_memory_usage()
        self.memory_monitor.start_monitoring()
        
        all_times = []
        total_success = 0
        total_errors = 0
        all_errors = []
        
        def worker_task(thread_id: int):
            """工作线程任务"""
            times = []
            success_count = 0
            error_count = 0
            errors = []
            
            for i in range(iterations_per_thread):
                iter_start = time.time()
                try:
                    status, _ = self.engine.recognize_simple(image_path)
                    iter_time = time.time() - iter_start
                    times.append(iter_time)
                    
                    if status == RocrStatus.SUCCESS:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"线程{thread_id}-迭代{i}: 状态错误 {status}")
                        
                except Exception as e:
                    iter_time = time.time() - iter_start
                    times.append(iter_time)
                    error_count += 1
                    errors.append(f"线程{thread_id}-迭代{i}: 异常 {str(e)}")
            
            return times, success_count, error_count, errors
        
        start_time = time.time()
        
        # 使用线程池执行并发测试
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_task, i) for i in range(num_threads)]
            
            for future in as_completed(futures):
                times, success, errors_count, errors = future.result()
                all_times.extend(times)
                total_success += success
                total_errors += errors_count
                all_errors.extend(errors)
        
        total_time = time.time() - start_time
        
        self.memory_monitor.stop_monitoring()
        memory_after = self.memory_monitor.get_memory_usage()
        memory_peak = self.memory_monitor.get_peak_memory()
        
        return TestResult(
            total_time=total_time,
            avg_time=statistics.mean(all_times) if all_times else 0,
            min_time=min(all_times) if all_times else 0,
            max_time=max(all_times) if all_times else 0,
            success_count=total_success,
            error_count=total_errors,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_peak=memory_peak,
            error_details=all_errors
        )
    
    def test_stress_test(self, image_path: str, duration_seconds: int = 60) -> TestResult:
        """压力测试（持续运行指定时间）
        
        Args:
            image_path: 测试图像路径
            duration_seconds: 测试持续时间（秒）
            
        Returns:
            TestResult: 测试结果
        """
        print(f"开始压力测试，持续时间: {duration_seconds}秒")
        
        memory_before = self.memory_monitor.get_memory_usage()
        self.memory_monitor.start_monitoring()
        
        times = []
        success_count = 0
        error_count = 0
        errors = []
        
        start_time = time.time()
        iteration = 0
        
        while time.time() - start_time < duration_seconds:
            iter_start = time.time()
            try:
                status, _ = self.engine.recognize_simple(image_path)
                iter_time = time.time() - iter_start
                times.append(iter_time)
                
                if status == RocrStatus.SUCCESS:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"迭代 {iteration}: 状态错误 {status}")
                    
            except Exception as e:
                iter_time = time.time() - iter_start
                times.append(iter_time)
                error_count += 1
                errors.append(f"迭代 {iteration}: 异常 {str(e)}")
            
            iteration += 1
            
            # 每100次迭代显示进度
            if iteration % 100 == 0:
                elapsed = time.time() - start_time
                print(f"  已运行 {elapsed:.1f}秒，完成 {iteration} 次测试")
        
        total_time = time.time() - start_time
        
        self.memory_monitor.stop_monitoring()
        memory_after = self.memory_monitor.get_memory_usage()
        memory_peak = self.memory_monitor.get_peak_memory()
        
        gc.collect()
        
        return TestResult(
            total_time=total_time,
            avg_time=statistics.mean(times) if times else 0,
            min_time=min(times) if times else 0,
            max_time=max(times) if times else 0,
            success_count=success_count,
            error_count=error_count,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_peak=memory_peak,
            error_details=errors
        )
    
    def print_test_report(self, test_name: str, result: TestResult):
        """打印测试报告"""
        print(f"\n{'='*60}")
        print(f"测试报告: {test_name}")
        print(f"{'='*60}")
        print(f"总时间: {result.total_time:.2f}秒")
        print(f"平均推理时间: {result.avg_time*1000:.2f}毫秒")
        print(f"最快推理时间: {result.min_time*1000:.2f}毫秒")
        print(f"最慢推理时间: {result.max_time*1000:.2f}毫秒")
        print(f"成功次数: {result.success_count}")
        print(f"失败次数: {result.error_count}")
        if result.success_count > 0:
            print(f"推理速度: {1/result.avg_time:.1f} FPS")
        print(f"内存使用 - 开始: {result.memory_before:.2f}MB")
        print(f"内存使用 - 结束: {result.memory_after:.2f}MB")
        print(f"内存使用 - 峰值: {result.memory_peak:.2f}MB")
        print(f"内存变化: {result.memory_after - result.memory_before:+.2f}MB")
        
        if result.error_details:
            print(f"\n错误详情 (前10条):")
            for error in result.error_details[:10]:
                print(f"  - {error}")
            if len(result.error_details) > 10:
                print(f"  ... 还有 {len(result.error_details) - 10} 条错误")
        
        print(f"{'='*60}")

def run_ffi_tests():
    """运行完整的FFI测试套件"""
    det_model = "models/PP-OCRv5_mobile_det.mnn"
    rec_model = "models/PP-OCRv5_mobile_rec.mnn"
    keys_file = "./models/ppocr_keys_v5.txt"
    image_file = "./res/1.png"
    
    # 检查文件是否存在
    for file_path, name in [(det_model, "检测模型"), (rec_model, "识别模型"), (keys_file, "字符集文件"), (image_file, "测试图像")]:
        if not os.path.exists(file_path):
            print(f"错误: {name} 文件不存在: {file_path}")
            return False
        else:
            print(f"✓ {name} 文件存在: {file_path}")
    
    try:
        with RocrEngine() as engine:
            if not engine.create_engine(det_model, rec_model, keys_file):
                print("✗ OCR引擎创建失败")
                return False
            
            print(f"✓ OCR引擎创建成功，版本: {engine.get_version()}")
            
            tester = RocrTester(engine)
            
            # 1. 速度测试
            speed_result = tester.test_inference_speed(image_file, iterations=50)
            tester.print_test_report("推理速度测试", speed_result)
            
            # 2. 内存泄露测试
            memory_result = tester.test_memory_leak(image_file, iterations=2000)
            tester.print_test_report("内存泄露测试", memory_result)
            
            # 3. 并发测试
            concurrent_result = tester.test_concurrent_access(image_file, num_threads=2, iterations_per_thread=25)
            tester.print_test_report("并发访问测试", concurrent_result)
            
            # 4. 压力测试
            stress_result = tester.test_stress_test(image_file, duration_seconds=30)
            tester.print_test_report("压力测试", stress_result)
            
            return True
            
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False

# 示例用法
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 运行测试套件
        print("开始运行FFI测试套件...")
        success = run_ffi_tests()
        sys.exit(0 if success else 1)
    else:
        # 原有的示例代码
        # 使用示例
        det_model = "models/PP-OCRv5_mobile_det_fp16.mnn"
        rec_model = "models/PP-OCRv5_mobile_rec_fp16.mnn"
        keys_file = "./models/ppocr_keys_v5.txt"
        image_file = "./res/1.png"
        
        # 检查文件是否存在
        import os
        for file_path, name in [(det_model, "检测模型"), (rec_model, "识别模型"), (keys_file, "字符集文件"), (image_file, "测试图像")]:
            if not os.path.exists(file_path):
                print(f"错误: {name} 文件不存在: {file_path}")
                exit(1)
            else:
                print(f"✓ {name} 文件存在: {file_path}")
        
        # 方式1：使用上下文管理器
        with RocrEngine() as engine:
            print(f"正在创建OCR引擎...")
            if engine.create_engine(det_model, rec_model, keys_file):
                print(f"✓ OCR引擎创建成功")
                print(f"OCR库版本: {engine.get_version()}")
                
                # 简单模式识别
                print(f"\n开始简单模式识别...")
                status, texts = engine.recognize_simple(image_file)
                if status == RocrStatus.SUCCESS:
                    print("识别的文本:")
                    for text in texts:
                        print(f"  - {text}")
                else:
                    print(f"简单模式识别失败: {status}")
                
                # 详细模式识别
                print(f"\n开始详细模式识别...")
                status, boxes = engine.recognize_detailed(image_file)
                if status == RocrStatus.SUCCESS:
                    print("详细识别结果:")
                    for box in boxes:
                        print(f"  文本: {box['text']}")
                        print(f"  置信度: {box['confidence']:.2f}")
                        print(f"  位置: ({box['left']}, {box['top']}, {box['width']}, {box['height']})")
                else:
                    print(f"详细模式识别失败: {status}")
            else:
                print("✗ OCR引擎创建失败")
        
        # 方式2：使用便捷函数
        print(f"\n使用便捷函数识别...")
        texts = ocr_recognize_text(image_file, det_model, rec_model, keys_file)
        print("便捷函数识别结果:", texts)
        
        print(f"\n提示: 运行 'python {sys.argv[0]} test' 来执行完整的FFI测试套件")
