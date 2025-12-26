# PlayerJY 解析接口分析总结

## 📋 接口信息

### 主入口
- **URL**: `https://jx.playerjy.com/?ads=0&url={视频URL}`
- **示例**: `https://jx.playerjy.com/?ads=0&url=https://www.iqiyi.com/v_1c168e2yzbk.html`

### 中间层
- **URL**: `https://getdata.staticfile.link/player/{hash}`
- **说明**: 主页面中的iframe，会重定向到media.staticfile.link

### 最终播放页面
- **URL**: `https://media.staticfile.link/?iv={iv}&key={key}&url={视频URL}`
- **示例**: `https://media.staticfile.link/?iv=3130312e33322e3232312e3739&key=d652ece029bb2681283dab579aa72f89&url=https://www.iqiyi.com/v_1c168e2yzbk.html`

## 🔍 URL参数分析

### iv 参数
- **值**: `3130312e33322e3232312e3739`
- **格式**: 十六进制编码
- **解码**: `101.32.221.79` (IP地址)
- **用途**: 可能是服务器IP地址或标识

### key 参数
- **值**: `d652ece029bb2681283dab579aa72f89`
- **格式**: 32位十六进制字符串（MD5哈希）
- **用途**: 可能是验证密钥或签名

### url 参数
- **值**: Base64编码的视频URL
- **示例**: `aHR0cHM6Ly93d3cuaXFpeWkuY29tL3ZfMWMxNjhlMnl6YmsuaHRtbA==`
- **解码**: `https://www.iqiyi.com/v_1c168e2yzbk.html`

## 🎬 播放器信息

### 使用的播放器
- **名称**: LLQPlayer.Pro
- **版本**: 最新版
- **CDN**: 
  - `npm.elemecdn.com/llqplayer@latest`
  - `static-cdn.byteamone.cn/gh/ffsir/CDN/player/llqplayer`

### 关键JS文件
1. `play.start.js` - 播放器启动脚本
2. `play.config.js` - 播放器配置（混淆）
3. `play.common.js` - 公共脚本（可能包含m3u8链接）
4. `engine.js` - 播放器引擎

## 🔐 反爬虫机制

### 检测方式
1. **开发者工具检测**: 打开F12会导致页面崩溃或显示错误
2. **自动化工具检测**: 检测webdriver属性
3. **页面导航循环**: 在getdata和media之间不断跳转
4. **请求异常**: 直接访问media.staticfile.link会返回"请求异常"

### 绕过方法
1. ✅ 使用独立Chrome实例（CDP连接）
2. ✅ 禁用调试器（CDP命令）
3. ✅ 隐藏webdriver属性
4. ✅ 禁用DevTools检测
5. ⚠️ 需要从主页面跳转（不能直接访问media.staticfile.link）

## 📡 API端点

### UPDATEDMKU.php
- **URL**: `https://dmku.byteamone.cn/UPDATEDMKU.php?url={base64编码的视频URL}`
- **用途**: 可能用于更新视频信息或获取播放链接
- **状态**: 需要进一步分析响应内容

## 🎯 发现的问题

### 1. 页面检测自动化工具
- **现象**: 直接访问media.staticfile.link返回"请求异常,请稍后重试"
- **原因**: 服务器端检测到自动化工具
- **解决**: 需要从主页面正常跳转，不能直接访问

### 2. 配置对象未找到
- **现象**: 页面中找不到ConFig、llqplayer等配置对象
- **可能原因**:
  - 配置对象在JS文件中动态创建
  - 需要触发某些事件才能加载
  - 配置数据在API响应中

### 3. m3u8链接位置
- **发现**: 在`play.common.js`响应中找到了m3u8链接
- **说明**: m3u8链接可能在JS文件中硬编码或通过API获取

## 💡 建议的解析方案

### 方案1: 模拟完整流程
1. 访问主页面 `jx.playerjy.com`
2. 获取iframe URL（getdata.staticfile.link）
3. 访问iframe页面，等待跳转到media.staticfile.link
4. 在media.staticfile.link页面中查找配置或m3u8链接

### 方案2: 分析JS文件
1. 下载并分析关键JS文件（play.common.js、play.config.js）
2. 查找m3u8链接的生成逻辑
3. 提取解密函数或API调用

### 方案3: 网络请求分析
1. 监听所有网络请求
2. 检查API响应（特别是UPDATEDMKU.php）
3. 从响应中提取m3u8链接

## 📝 下一步行动

1. ✅ 已完成：创建分析脚本，监听网络请求
2. ⏳ 进行中：分析JS文件中的m3u8链接生成逻辑
3. ⏳ 待完成：分析UPDATEDMKU.php API的响应格式
4. ⏳ 待完成：提取完整的解析流程

## 🔧 技术要点

### Chrome启动参数
```python
--disable-web-security
--disable-site-isolation-trials
--disable-features=BlockInsecurePrivateNetworkRequests
--disable-blink-features=AutomationControlled
```

### 反检测脚本要点
- 隐藏webdriver属性
- 禁用debugger函数
- 覆盖DevTools检测
- 设置真实的浏览器特征

### 关键发现
- iv参数是IP地址的十六进制编码
- key参数是32位MD5哈希
- url参数是Base64编码的视频URL
- m3u8链接可能在play.common.js中

## 📚 相关文件

- `analyze_playerjy_parser.py` - 完整流程分析脚本
- `analyze_media_staticfile.py` - 直接访问media.staticfile.link的脚本
- `browser_decrypt_parser.py` - 参考的浏览器解密方案
- `playerjy_analysis_result.json` - 分析结果（如果生成）
- `media_staticfile_analysis.json` - media.staticfile.link分析结果

