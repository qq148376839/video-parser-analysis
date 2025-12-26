# -*- coding: utf-8 -*-
"""
整理jx2s0相关文件到文件夹
"""

import os
import shutil
from pathlib import Path


def organize_jx2s0_files():
    """整理jx2s0相关文件"""
    
    # 当前目录
    current_dir = Path(__file__).parent
    
    # 目标文件夹
    target_dir = current_dir / 'jx2s0_analysis'
    
    # 创建目标文件夹
    if not target_dir.exists():
        target_dir.mkdir()
        print(f"✅ 创建文件夹: {target_dir}")
    
    # jx2s0相关文件列表
    jx2s0_files = [
        # 分析脚本
        'analyze_jx2s0_parser.py',
        'direct_jx2s0_parser.py',
        'direct_jx2s0_parser_simple.py',
        'debug_jx2s0_decrypt.py',
        'test_jx2s0_decrypt.py',
        'test_config_url_decrypt.py',
        
        # 分析文档
        'JX2S0_FINAL_ANALYSIS.md',
        'JX2S0_M3U8_GENERATION_ANALYSIS.md',
        'JX2S0_CODE_FLOW_ANALYSIS.md',
        'JX2S0_DECRYPT_ANALYSIS.md',
        'JX2S0_CODE_ANALYSIS_SUMMARY.md',
        '7ZLPLAYER_XHR_ANALYSIS.md',
        'DEOBFUSCATE_SEARCH_RESULTS.md',
        
        # 数据文件
        'jx2s0_analysis_result.json',
        'jx2s0_decrypt_result.json',
        'config_url_decrypt_result.json',
        
        # HTML文件
        'jx2s0_iframe_page.html',
        'jx2s0_main_page.html',
        
        # JavaScript源文件
        '7zl.js',
        '7zlplayer.js',
        '7zl_deobfuscated.js',
        '7zlplayer_deobfuscated.js',
        
        # 反混淆工具
        'deobfuscate_js.py',
        'search_deobfuscated.py',
        'test_deobfuscate.py',
        'DEOBFUSCATE_README.md',
        'search_results.txt',
    ]
    
    # 移动文件
    moved_files = []
    not_found_files = []
    
    for filename in jx2s0_files:
        source_path = current_dir / filename
        
        if source_path.exists():
            target_path = target_dir / filename
            
            try:
                # 如果目标文件已存在，先删除
                if target_path.exists():
                    target_path.unlink()
                
                # 移动文件
                shutil.move(str(source_path), str(target_path))
                moved_files.append(filename)
                print(f"✅ 移动: {filename}")
            except Exception as e:
                print(f"❌ 移动失败 {filename}: {e}")
        else:
            not_found_files.append(filename)
    
    # 创建README文件
    readme_content = f"""# jx2s0 分析文件集合

## 📋 文件说明

### 分析脚本
- `analyze_jx2s0_parser.py` - 主要分析脚本，使用浏览器自动化分析jx2s0解析逻辑
- `direct_jx2s0_parser.py` - 直接解析器，从网络请求中提取m3u8链接
- `direct_jx2s0_parser_simple.py` - 简化版直接解析器
- `debug_jx2s0_decrypt.py` - 调试RC4解密过程
- `test_jx2s0_decrypt.py` - 测试RC4解密
- `test_config_url_decrypt.py` - 测试config.url解密

### 分析文档
- `JX2S0_FINAL_ANALYSIS.md` - 最终分析总结
- `JX2S0_M3U8_GENERATION_ANALYSIS.md` - m3u8生成分析
- `JX2S0_CODE_FLOW_ANALYSIS.md` - 代码流程分析
- `JX2S0_DECRYPT_ANALYSIS.md` - 解密分析
- `JX2S0_CODE_ANALYSIS_SUMMARY.md` - 代码分析摘要
- `7ZLPLAYER_XHR_ANALYSIS.md` - XMLHttpRequest分析
- `DEOBFUSCATE_SEARCH_RESULTS.md` - 反混淆搜索结果

### 数据文件
- `jx2s0_analysis_result.json` - 分析结果
- `jx2s0_decrypt_result.json` - 解密结果
- `config_url_decrypt_result.json` - config.url解密结果

### HTML文件
- `jx2s0_iframe_page.html` - iframe页面
- `jx2s0_main_page.html` - 主页面

### JavaScript源文件
- `7zl.js` - 主要JavaScript文件（混淆）
- `7zlplayer.js` - 播放器JavaScript文件（混淆）
- `7zl_deobfuscated.js` - 反混淆后的7zl.js
- `7zlplayer_deobfuscated.js` - 反混淆后的7zlplayer.js

### 反混淆工具
- `deobfuscate_js.py` - JavaScript反混淆脚本
- `search_deobfuscated.py` - 在反混淆文件中搜索关键字
- `test_deobfuscate.py` - 测试反混淆功能
- `DEOBFUSCATE_README.md` - 反混淆工具使用说明
- `search_results.txt` - 搜索结果

## 🚀 使用方法

### 1. 分析jx2s0解析逻辑
```bash
python analyze_jx2s0_parser.py
```

### 2. 直接提取m3u8链接
```bash
python direct_jx2s0_parser.py
```

### 3. 反混淆JavaScript文件
```bash
python deobfuscate_js.py
```

### 4. 搜索关键字
```bash
python search_deobfuscated.py
```

## 📝 文件统计

- 总文件数: {len(moved_files)}
- 成功移动: {len(moved_files)}
- 未找到: {len(not_found_files)}

## 📌 注意事项

- 所有文件已从原目录移动到本文件夹
- 如需使用，请确保在正确的目录下运行脚本
- 建议使用相对路径或绝对路径引用这些文件
"""
    
    readme_path = target_dir / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n✅ 创建README文件: {readme_path}")
    
    # 输出统计信息
    print("\n" + "=" * 60)
    print("文件整理完成")
    print("=" * 60)
    print(f"✅ 成功移动: {len(moved_files)} 个文件")
    print(f"❌ 未找到: {len(not_found_files)} 个文件")
    print(f"📁 目标文件夹: {target_dir}")
    
    if not_found_files:
        print("\n未找到的文件:")
        for filename in not_found_files:
            print(f"  - {filename}")


if __name__ == '__main__':
    organize_jx2s0_files()

# 直接执行
organize_jx2s0_files()

