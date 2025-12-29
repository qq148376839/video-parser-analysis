# 解密问题解决方案

## 🔍 问题分析

### 当前问题
1. **浏览器控制台问题**: `window.ConFig` 是 `undefined`
   - 原因：ConFig 对象在 iframe 中定义，不在主窗口
   - 解决：需要在 iframe 的上下文中访问

2. **Python解密失败**: "Padding is incorrect"
   - 原因：密钥/IV 生成方式可能与 CryptoJS/NotGm 不完全匹配
   - 解决：使用浏览器自动化直接在浏览器中执行 JavaScript 解密

---

## 🎯 解决方案

### 方案1: 浏览器自动化解密（推荐）⭐

**优点**:
- ✅ 直接使用网站原生的 JavaScript 解密函数
- ✅ 无需猜测密钥/IV 生成方式
- ✅ 100% 准确

**使用方法**:
```bash
python browser_decrypt_parser.py
```

**工作原理**:
1. 使用 Playwright 启动浏览器
2. 访问 iframe 页面
3. 等待 ConFig 和 PlayEr 对象加载
4. 直接调用 `PlayEr.ad.uic(ConFig.url)` 执行解密
5. 获取解密后的 URL

---

### 方案2: 改进的Python解密（备选）

**优点**:
- ✅ 不需要浏览器，纯 Python 实现
- ✅ 运行速度快

**缺点**:
- ⚠️ 可能仍然无法匹配所有情况

**使用方法**:
```bash
# 基础版本（已更新）
python final_direct_parser.py

# 增强版本（尝试更多组合）
python final_direct_parser_v2.py
```

**改进内容**:
- 尝试多种密钥生成方式（直接UTF-8、MD5、SHA256）
- 尝试多种IV生成方式（UTF-8编码、十六进制解析+填充）
- 自动处理填充错误

---

## 📋 使用步骤

### 步骤1: 安装依赖

```bash
pip install playwright pycryptodome requests
playwright install chromium
```

### 步骤2: 选择方案

**推荐使用浏览器自动化方案**:
```bash
python browser_decrypt_parser.py
```

**如果浏览器方案不可用，尝试Python解密**:
```bash
python final_direct_parser_v2.py
```

### 步骤3: 查看结果

- 成功后会输出最终的 m3u8 链接
- 结果保存在 JSON 文件中
- m3u8 播放列表保存在 `.m3u8` 文件中

---

## 🔧 调试方法

### 在浏览器中手动测试

1. **打开iframe页面**:
   ```
   https://api.789jiexi.com/player/789.php?code=789jiexi&if=1&url=https://www.iqiyi.com/v_237eaj98iv0.html
   ```

2. **打开开发者工具** (F12)

3. **在Console中执行**:
   ```javascript
   // 检查ConFig对象
   console.log('ConFig:', window.ConFig);
   console.log('ConFig.url:', window.ConFig?.url);
   console.log('ConFig.config.uid:', window.ConFig?.config?.uid);
   
   // 检查PlayEr对象
   console.log('PlayEr:', window.PlayEr);
   console.log('PlayEr.ad.uic:', window.PlayEr?.ad?.uic);
   
   // 执行解密
   if (window.ConFig && window.PlayEr && window.PlayEr.ad && window.PlayEr.ad.uic) {
       const decrypted = window.PlayEr.ad.uic(window.ConFig.url);
       console.log('✅ 解密后的URL:', decrypted);
   } else {
       console.log('❌ 对象不存在');
   }
   ```

### 查看Python解密过程

运行 `final_direct_parser_v2.py` 会输出详细的解密尝试过程：
- 尝试的密钥方式
- 尝试的IV方式
- 每个组合的结果

---

## 📝 技术细节

### CryptoJS/NotGm 解密函数

根据找到的代码：
```javascript
"uic": function(d){
    let ut = NotGm.enc.Utf8.parse('2890' + ConFig['config']['uid'] + 'tB959C'),
        mm = NotGm.enc.Utf8.parse("2F131BE91247866E"),
        decrypted = NotGm.BBS.decrypt(d, ut, {iv: mm, mode: NotGm.mode.CBC, padding: NotGm.pad.Pkcs7});
    return NotGm.enc.Utf8.stringify(decrypted);
}
```

### Python实现要点

1. **密钥生成**:
   - `key_str = '2890' + uid + 'tB959C'`
   - 如果长度不是16/24/32字节，CryptoJS会使用MD5哈希
   - Python: `key = hashlib.md5(key_str.encode('utf-8')).digest()`

2. **IV生成**:
   - `iv_str = '2F131BE91247866E'`
   - `Utf8.parse()` 会将字符串转换为UTF-8字节数组
   - 16个字符 = 16字节（每个字符1字节）

3. **解密模式**:
   - AES-CBC
   - PKCS7填充

---

## 🚀 快速开始

### 最简单的方式（推荐）

```bash
python browser_decrypt_parser.py
```

这会自动：
1. 打开浏览器
2. 访问解析页面
3. 提取 ConFig 对象
4. 执行 JavaScript 解密
5. 获取最终的 m3u8 链接

### 如果浏览器方案失败

```bash
# 尝试改进的Python解密
python final_direct_parser_v2.py
```

---

## ❓ 常见问题

### Q1: 为什么 `window.ConFig` 是 `undefined`？

**A**: ConFig 对象在 iframe 中定义，不在主窗口。需要在 iframe 的上下文中访问。

**解决**: 使用浏览器自动化脚本，它会自动访问 iframe 内容。

### Q2: Python解密一直失败怎么办？

**A**: 使用浏览器自动化方案，直接在浏览器中执行 JavaScript 解密函数。

### Q3: 如何确认解密是否正确？

**A**: 解密后的URL应该以 `http` 开头，并且可能包含 `m3u8` 或 `api/m3u8`。

---

## 📚 相关文件

- `browser_decrypt_parser.py` - 浏览器自动化解密方案（推荐）
- `final_direct_parser.py` - 基础Python解密方案
- `final_direct_parser_v2.py` - 改进的Python解密方案（尝试更多组合）
- `DECRYPT_FAILURE_ANALYSIS.md` - 解密失败原因分析
- `DECRYPT_GUIDE.md` - 解密指南

---

**最后更新**: 2024-12-08



