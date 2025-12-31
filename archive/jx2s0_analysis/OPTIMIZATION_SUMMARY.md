# get_m3u8_with_paid_key.py 优化总结

## ✅ 已实现的优化

### 1. ✅ JSON结构优化

**新增字段**：
- **`current_index`**（顶层）：记录当前轮询到的key索引
- **`expire_date`**（每个key对象）：key的过期日期（注册日期 + 355天）

**格式转换**：
- 首次加载时，如果是列表格式，自动转换为带元数据的格式
- 之后保存的格式都是带元数据的格式

**示例**：
```json
{
  "current_index": 0,
  "keys": [
    {
      "email": "riowang@rio.edu.kg",
      "password": "qwer1234!",
      "uid": "4059917",
      "key": "cgklotuyDGHILOTW38",
      "register_time": "2025-12-30 16:51:10",
      "expire_date": "2026-12-20 16:51:10"
    }
  ]
}
```

### 2. ✅ 自动轮询功能

**实现方式**：
- 每次调用 `get_m3u8_url()` 时，自动使用下一个key
- 使用 `current_index` 记录当前位置
- 调用后自动更新 `current_index` 到下一个索引
- 循环使用所有key

**工作流程**：
```
调用1 → 使用 keys[0] → 更新 current_index = 1
调用2 → 使用 keys[1] → 更新 current_index = 2
调用3 → 使用 keys[2] → 更新 current_index = 0 (循环)
```

### 3. ✅ 过期key自动删除

**实现方式**：
- 每次调用前检查key是否过期
- 如果过期，自动删除该key
- 自动跳到下一个key
- 更新JSON文件

**过期判断**：
- 过期日期 = 注册日期 + 355天
- 如果当前时间 > 过期日期，则视为过期

**删除流程**：
```
检查 key_info → 过期？
  ├─ 是 → 删除key → 更新索引 → 保存JSON → 继续下一个
  └─ 否 → 使用该key → 更新索引 → 保存JSON → 返回
```

### 4. ✅ 自动更新JSON

**更新时机**：
1. 首次加载时：添加 `expire_date` 字段
2. 每次调用后：更新 `current_index`
3. 删除过期key后：更新 `keys` 列表和 `current_index`

**保存格式**：
- 统一使用带元数据的格式
- 保持JSON格式的一致性

## 🔧 核心方法

### `get_next_valid_key()`

**功能**：
- 获取下一个有效的key
- 检查过期并删除
- 更新索引

**返回值**：
- 有效的key信息字典，或 `None`（如果没有可用key）

### `get_m3u8_url(video_url, retry=True)`

**功能**：
- 自动轮询key获取m3u8 URL
- 如果失败，自动尝试下一个key（如果 `retry=True`）

**参数**：
- `video_url`: 视频URL
- `retry`: 是否重试下一个key（默认：True）

**返回值**：
- m3u8 URL字符串，或 `None`（如果获取失败）

### `get_m3u8_info(video_url)`

**功能**：
- 获取m3u8 URL的详细信息（包括hash和token）

**返回值**：
- 包含 `m3u8_url`、`hash`、`token` 的字典，或 `None`

## 📝 使用示例

### 基本使用

```python
from archive.jx2s0_analysis.get_m3u8_with_paid_key import PaidKeyM3U8Getter

# 创建获取器（自动从JSON文件加载keys）
getter = PaidKeyM3U8Getter("registration_results.json")

# 获取m3u8 URL（自动轮询key）
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
m3u8_url = getter.get_m3u8_url(video_url)

if m3u8_url:
    print(f"m3u8 URL: {m3u8_url}")
else:
    print("获取失败")
```

### 批量处理

```python
getter = PaidKeyM3U8Getter("registration_results.json")

video_urls = [
    "https://www.iqiyi.com/v_1c168e2yzbk.html",
    "https://www.iqiyi.com/v_19rr7qhfg0.html",
]

for video_url in video_urls:
    m3u8_url = getter.get_m3u8_url(video_url)
    if m3u8_url:
        print(f"✅ {video_url} -> {m3u8_url}")
    else:
        print(f"❌ {video_url} -> 获取失败")
```

## 🎯 关键特性

### 1. 自动轮询
- ✅ 每次调用使用不同的key
- ✅ 自动更新索引
- ✅ 循环使用所有key

### 2. 过期管理
- ✅ 自动检测过期key
- ✅ 自动删除过期key
- ✅ 自动跳到下一个key

### 3. 容错处理
- ✅ 如果当前key失败，自动尝试下一个
- ✅ 如果所有key都过期，返回None
- ✅ 如果JSON格式不正确，抛出异常

### 4. 数据持久化
- ✅ 自动保存更新后的JSON
- ✅ 保持数据一致性
- ✅ 支持格式自动转换

## 📊 JSON更新示例

### 首次加载（列表格式 → 带元数据格式）

**输入**：
```json
[
  {
    "uid": "4059917",
    "key": "cgklotuyDGHILOTW38",
    "register_time": "2025-12-30 16:51:10"
  }
]
```

**输出**（自动转换）：
```json
{
  "current_index": 0,
  "keys": [
    {
      "uid": "4059917",
      "key": "cgklotuyDGHILOTW38",
      "register_time": "2025-12-30 16:51:10",
      "expire_date": "2026-12-20 16:51:10"
    }
  ]
}
```

### 调用后（索引更新）

**调用前**：
```json
{
  "current_index": 0,
  "keys": [...]
}
```

**调用后**（假设有3个key）：
```json
{
  "current_index": 1,
  "keys": [...]
}
```

### 过期key删除

**删除前**：
```json
{
  "current_index": 1,
  "keys": [
    {"uid": "4059917", "expire_date": "2026-12-20 16:51:10"},
    {"uid": "4098778", "expire_date": "2025-01-01 00:00:00"}  // 已过期
  ]
}
```

**删除后**：
```json
{
  "current_index": 0,
  "keys": [
    {"uid": "4059917", "expire_date": "2026-12-20 16:51:10"}
  ]
}
```

## ⚠️ 注意事项

1. **JSON文件格式**：
   - 首次加载时，如果是列表格式，会自动转换为带元数据的格式
   - 之后保存的格式都是带元数据的格式

2. **current_index**：
   - 每次调用后自动更新
   - 如果删除过期key，索引会自动调整
   - 如果索引超出范围，自动重置为0

3. **过期检查**：
   - 每次调用前检查key是否过期
   - 过期日期 = 注册日期 + 355天
   - 过期的key会被自动删除

4. **线程安全**：
   - 如果多线程/多进程使用，建议加锁
   - 或者每个进程使用独立的JSON文件

## 🎯 测试建议

1. **测试key轮询**：
   ```bash
   python archive/jx2s0_analysis/test_key_rotation.py
   ```

2. **测试过期key删除**：
   - 手动修改JSON中的 `expire_date` 为过去的时间
   - 运行脚本，观察是否自动删除

3. **测试格式转换**：
   - 使用原始的列表格式JSON
   - 运行脚本，观察是否自动转换

## 📚 相关文件

- `get_m3u8_with_paid_key.py` - 优化后的主脚本
- `PAID_KEY_ROTATION_GUIDE.md` - 详细使用指南
- `test_key_rotation.py` - 测试脚本
- `registration_results.json` - key数据文件

