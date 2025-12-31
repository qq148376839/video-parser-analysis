# 付费Key轮询使用指南

## 📋 功能说明

优化后的 `get_m3u8_with_paid_key.py` 支持以下功能：

1. **自动轮询多个key**：每次调用使用不同的key
2. **过期管理**：自动检测并删除过期的key
3. **JSON结构更新**：自动添加 `expire_date` 字段
4. **索引管理**：使用 `current_index` 记录当前轮询位置

## 🔧 JSON格式

### 原始格式（列表）
```json
[
  {
    "email": "riowang@rio.edu.kg",
    "password": "qwer1234!",
    "uid": "4059917",
    "key": "cgklotuyDGHILOTW38",
    "register_time": "2025-12-30 16:51:10"
  }
]
```

### 优化后的格式（带元数据）
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

## 📝 字段说明

### 新增字段

1. **`current_index`**（顶层）
   - 类型：整数
   - 说明：当前轮询到的key索引
   - 默认值：0
   - 更新：每次调用后自动更新到下一个索引

2. **`expire_date`**（每个key对象）
   - 类型：字符串（格式：`YYYY-MM-DD HH:MM:SS`）
   - 说明：key的过期日期（注册日期 + 355天）
   - 自动生成：首次加载时自动计算并添加

## 🎯 工作流程

### 1. 初始化

```python
getter = PaidKeyM3U8Getter("registration_results.json")
```

**自动执行**：
- 加载JSON文件
- 如果是列表格式，转换为带元数据的格式
- 为每个key添加 `expire_date` 字段（如果不存在）
- 保存更新后的JSON

### 2. 获取m3u8 URL

```python
m3u8_url = getter.get_m3u8_url(video_url)
```

**执行流程**：
1. 获取下一个有效的key（`get_next_valid_key()`）
2. 检查key是否过期
   - 如果过期 → 删除该key，跳到下一个
   - 如果未过期 → 使用该key
3. 调用API获取m3u8 URL
4. 更新 `current_index` 到下一个索引
5. 保存JSON文件

### 3. 过期key处理

**自动处理**：
- 调用前检查key是否过期
- 如果过期，自动删除
- 跳到下一个key
- 更新JSON文件

## 💡 使用示例

### 基本使用

```python
from get_m3u8_with_paid_key import PaidKeyM3U8Getter

# 创建获取器
getter = PaidKeyM3U8Getter("registration_results.json")

# 获取m3u8 URL（自动轮询key）
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
m3u8_url = getter.get_m3u8_url(video_url)

if m3u8_url:
    print(f"m3u8 URL: {m3u8_url}")
else:
    print("获取失败")
```

### 获取详细信息

```python
# 获取详细信息（包括hash和token）
info = getter.get_m3u8_info(video_url)

if info:
    print(f"m3u8 URL: {info['m3u8_url']}")
    print(f"Hash: {info['hash']}")
    print(f"Token: {info['token']}")
```

### 批量处理

```python
video_urls = [
    "https://www.iqiyi.com/v_1c168e2yzbk.html",
    "https://www.iqiyi.com/v_19rr7qhfg0.html",
]

getter = PaidKeyM3U8Getter("registration_results.json")

for video_url in video_urls:
    m3u8_url = getter.get_m3u8_url(video_url)
    if m3u8_url:
        print(f"✅ {video_url} -> {m3u8_url}")
    else:
        print(f"❌ {video_url} -> 获取失败")
```

## 🔍 关键特性

### 1. 自动轮询

- 每次调用使用不同的key
- 自动更新 `current_index`
- 循环使用所有key

### 2. 过期管理

- 自动检测过期key
- 自动删除过期key
- 自动跳到下一个key

### 3. 容错处理

- 如果当前key失败，自动尝试下一个
- 如果所有key都过期，返回None
- 如果JSON格式不正确，抛出异常

## 📊 JSON更新示例

### 首次加载（列表格式）

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

## 🎯 最佳实践

1. **定期备份JSON文件**：防止数据丢失
2. **监控key数量**：如果key数量减少，及时补充
3. **错误处理**：处理 `get_m3u8_url` 返回 `None` 的情况
4. **日志记录**：记录使用的key和结果，便于排查问题

