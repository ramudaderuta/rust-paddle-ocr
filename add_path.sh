#!/bin/bash

# 指定目录
TARGET_DIR="$1"

# 检查是否提供了目录参数
if [ -z "$TARGET_DIR" ]; then
  echo "请提供目标目录作为参数。"
  exit 1
fi

# 遍历目录下的所有 .rs 文件
find "$TARGET_DIR" -type f -name "*.rs" | while read -r file; do
  # 获取文件相对于项目的路径
  relative_path=$(python3 -c "import os.path; print(os.path.relpath('$file', '$TARGET_DIR'))")
  
  # 检查文件顶部是否已经有路径注释
  if grep -q "^// file_path:" "$file"; then
    # 如果存在，更新路径注释
    perl -pi -e "s#^// file_path:.*#// file_path: $relative_path#" "$file"
  else
    # 如果不存在，添加路径注释
    {
      echo "// file_path: $relative_path"
      cat "$file"
    } > "$file.tmp" && mv "$file.tmp" "$file"
  fi
done

echo "注释添加完成。"