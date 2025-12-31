# 使用示例

## 📋 快速开始

### 方法1：直接运行主脚本

```bash
# 从项目根目录运行
python archive/jx2s0_analysis/get_m3u8_with_paid_key.py
```

脚本会自动：
- 从项目根目录查找 `registration_results.json`
- 自动添加 `expire_date` 字段
- 自动转换JSON格式
- 自动轮询key

### 方法2：在代码中使用

```python
import sys
import os

# 添加路径（如果需要）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'archive', 'jx2s0_analysis'))

from get_m3u8_with_paid_key import PaidKeyM3U8Getter

# 创建获取器
json_file = "registration_results.json"  # 相对于项目根目录
getter = PaidKeyM3U8Getter(json_file)

# 获取m3u8 URL
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
m3u8_url = getter.get_m3u8_url(video_url)

if m3u8_url:
    print(f"m3u8 URL: {m3u8_url}")
```

### 方法3：使用绝对路径

```python
from archive.jx2s0_analysis.get_m3u8_with_paid_key import PaidKeyM3U8Getter

# 使用绝对路径
json_file = r"D:\Python脚本\video-parser-analysis\registration_results.json"
getter = PaidKeyM3U8Getter(json_file)

# 获取m3u8 URL
m3u8_url = getter.get_m3u8_url("https://www.iqiyi.com/v_1c168e2yzbk.html")
```

## 🔧 测试脚本

### 运行测试

```bash
# 从项目根目录运行
cd archive/jx2s0_analysis
python test_key_rotation.py

# 或从项目根目录
python archive/jx2s0_analysis/test_key_rotation.py
```

## 📝 注意事项

1. **JSON文件路径**：
   - 默认从项目根目录查找 `registration_results.json`
   - 也可以使用绝对路径
   - 脚本会自动处理路径问题

2. **首次运行**：
   - 会自动添加 `expire_date` 字段
   - 会自动转换JSON格式（列表 → 带元数据格式）
   - 会保存更新后的JSON文件

3. **Key轮询**：
   - 每次调用使用不同的key
   - 自动更新 `current_index`
   - 循环使用所有key

4. **过期key**：
   - 自动检测并删除
   - 自动跳到下一个key
   - 更新JSON文件

