#include <stdio.h>
#include <stdlib.h>
#include "../rocr.h"

int main() {
    printf("=== Rust PaddleOCR C API Demo ===\n");
    
    // 模型文件路径
    const char* det_model = "../models/PP-OCRv5_mobile_det.mnn";
    const char* rec_model = "../models/PP-OCRv5_mobile_rec.mnn";
    const char* keys_file = "../models/ppocr_keys_v5.txt";
    const char* image_file = "../res/1.png";
    
    // 显示版本信息
    printf("OCR库版本: %s\n\n", rocr_version());
    
    // 创建OCR引擎
    printf("正在创建OCR引擎...\n");
    ROCR_RocrHandle engine = rocr_create_engine(det_model, rec_model, keys_file);
    
    if (engine == 0) {
        printf("✗ OCR引擎创建失败\n");
        return 1;
    }
    
    printf("✓ OCR引擎创建成功\n\n");
    
    // 简单模式识别
    printf("开始简单模式识别...\n");
    struct ROCR_RocrSimpleResult simple_result = rocr_recognize_simple(engine, image_file);
    
    if (simple_result.STATUS == ROCR_RocrStatus_Success) {
        printf("识别成功，共识别出 %zu 个文本:\n", simple_result.COUNT);
        for (size_t i = 0; i < simple_result.COUNT; i++) {
            printf("  - %s\n", simple_result.TEXTS[i]);
        }
    } else {
        printf("简单模式识别失败，状态码: %d\n", simple_result.STATUS);
    }
    
    // 释放简单结果内存
    rocr_free_simple_result(&simple_result);
    
    printf("\n");
    
    // 详细模式识别
    printf("开始详细模式识别...\n");
    struct ROCR_RocrResult detailed_result = rocr_recognize_detailed(engine, image_file);
    
    if (detailed_result.STATUS == ROCR_RocrStatus_Success) {
        printf("详细识别成功，共识别出 %zu 个文本框:\n", detailed_result.COUNT);
        for (size_t i = 0; i < detailed_result.COUNT; i++) {
            struct ROCR_RocrTextBox* box = &detailed_result.BOXES[i];
            printf("  文本: %s\n", box->TEXT);
            printf("  置信度: %.2f\n", box->CONFIDENCE);
            printf("  位置: (%d, %d, %u, %u)\n", box->LEFT, box->TOP, box->WIDTH, box->HEIGHT);
            printf("  ---\n");
        }
    } else {
        printf("详细模式识别失败，状态码: %d\n", detailed_result.STATUS);
    }
    
    // 释放详细结果内存
    rocr_free_result(&detailed_result);
    
    // 销毁引擎
    enum ROCR_RocrStatus destroy_status = rocr_destroy_engine(engine);
    if (destroy_status == ROCR_RocrStatus_Success) {
        printf("\n✓ OCR引擎销毁成功\n");
    } else {
        printf("\n✗ OCR引擎销毁失败，状态码: %d\n", destroy_status);
    }
    
    // 清理资源
    rocr_cleanup();
    
    printf("\nDemo 完成!\n");
    return 0;
}
