/**
 * 快速搜索z参数生成逻辑的JavaScript脚本
 * 在浏览器Console中运行此脚本，快速找到z参数相关代码
 * 
 * 使用方法:
 * 1. 打开解析网站: https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx=...
 * 2. 打开浏览器开发者工具 (F12)
 * 3. 切换到Console标签页
 * 4. 复制粘贴此脚本并运行
 */

(function() {
    'use strict';
    
    console.log('='.repeat(60));
    console.log('🔍 z参数生成逻辑搜索工具');
    console.log('='.repeat(60));
    
    // 从URL中提取z参数（如果当前页面有API调用）
    const currentZ = (() => {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('z');
    })();
    
    // 从网络请求中提取z参数
    let capturedZ = null;
    
    // Hook fetch来捕获z参数
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string' && url.includes('api/v')) {
            const zMatch = url.match(/[?&]z=([a-f0-9]{32})/);
            if (zMatch) {
                capturedZ = zMatch[1];
                console.log('\n✅ 捕获到z参数:', capturedZ);
            }
        }
        return originalFetch.apply(this, args);
    };
    
    // 搜索函数
    function searchInScripts(keyword, description) {
        console.log(`\n🔍 搜索: ${description} (${keyword})`);
        console.log('-'.repeat(60));
        
        const scripts = document.querySelectorAll('script');
        let found = false;
        
        scripts.forEach((script, index) => {
            const content = script.textContent || script.innerHTML || '';
            const src = script.src || 'inline';
            
            if (content.includes(keyword)) {
                found = true;
                console.log(`\n📄 脚本 [${index}]: ${src}`);
                
                // 显示匹配的行
                const lines = content.split('\n');
                lines.forEach((line, lineNum) => {
                    if (line.includes(keyword)) {
                        const contextStart = Math.max(0, lineNum - 2);
                        const contextEnd = Math.min(lines.length, lineNum + 3);
                        const context = lines.slice(contextStart, contextEnd);
                        
                        console.log(`\n   行 ${lineNum + 1}:`);
                        context.forEach((ctxLine, ctxIdx) => {
                            const actualLineNum = contextStart + ctxIdx + 1;
                            const marker = ctxIdx === 2 ? '>>>' : '   ';
                            console.log(`   ${marker} ${actualLineNum}: ${ctxLine.trim()}`);
                        });
                    }
                });
            }
        });
        
        if (!found) {
            console.log('   ⚠️ 未找到');
        }
        
        return found;
    }
    
    // 搜索z参数相关代码
    console.log('\n📋 开始搜索...\n');
    
    // 1. 搜索z参数赋值
    searchInScripts('z=', 'z参数赋值');
    searchInScripts('z:', 'z参数对象属性');
    
    // 2. 搜索MD5相关
    searchInScripts('md5', 'MD5函数');
    searchInScripts('MD5', 'MD5函数（大写）');
    
    // 3. 搜索API调用
    searchInScripts('api/v', 'API调用');
    searchInScripts('m1-a1.cloud', 'API域名');
    
    // 4. 如果捕获到z参数，搜索该值
    if (capturedZ) {
        console.log(`\n🔍 搜索z参数值: ${capturedZ}`);
        console.log('-'.repeat(60));
        
        const scripts = document.querySelectorAll('script');
        scripts.forEach((script, index) => {
            const content = script.textContent || script.innerHTML || '';
            if (content.includes(capturedZ)) {
                const src = script.src || 'inline';
                console.log(`\n📄 找到z参数值在脚本 [${index}]: ${src}`);
                
                // 显示上下文
                const pos = content.indexOf(capturedZ);
                const contextStart = Math.max(0, pos - 200);
                const contextEnd = Math.min(content.length, pos + capturedZ.length + 200);
                const context = content.substring(contextStart, contextEnd);
                
                console.log(`   上下文:\n${context}`);
            }
        });
    }
    
    // 5. 搜索函数定义
    console.log('\n🔍 搜索可能的z参数生成函数');
    console.log('-'.repeat(60));
    
    const functionPatterns = [
        /function\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*\([^)]*\)\s*\{[^}]*z[^}]*\}/g,
        /const\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=\s*function\s*\([^)]*\)\s*\{[^}]*z[^}]*\}/g,
        /const\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*z[^}]*\}/g,
    ];
    
    const scripts = document.querySelectorAll('script');
    scripts.forEach((script, index) => {
        const content = script.textContent || script.innerHTML || '';
        functionPatterns.forEach(pattern => {
            const matches = content.match(pattern);
            if (matches) {
                const src = script.src || 'inline';
                console.log(`\n📄 脚本 [${index}]: ${src}`);
                matches.forEach((match, i) => {
                    console.log(`\n   函数 ${i + 1}:`);
                    console.log(`   ${match.substring(0, 300)}...`);
                });
            }
        });
    });
    
    // 6. 提供搜索建议
    console.log('\n' + '='.repeat(60));
    console.log('💡 搜索建议');
    console.log('='.repeat(60));
    console.log('\n1. 使用浏览器全局搜索 (Ctrl+Shift+F):');
    console.log('   - 搜索 "z=" 或 "z:"');
    console.log('   - 搜索 "md5" 或 "MD5"');
    console.log('   - 搜索 "api/v"');
    if (capturedZ) {
        console.log(`   - 搜索 "${capturedZ}"`);
    }
    console.log('\n2. 重点关注网站自己的JS文件（非Chrome扩展）');
    console.log('\n3. 在找到的代码处设置断点，观察z参数的生成过程');
    console.log('\n4. 查看Network标签页，找到API调用，查看调用栈');
    
    // 返回搜索工具对象
    window._zParamSearchTool = {
        search: searchInScripts,
        capturedZ: () => capturedZ,
        searchAll: function() {
            searchInScripts('z=', 'z参数赋值');
            searchInScripts('md5', 'MD5函数');
            searchInScripts('api/v', 'API调用');
        }
    };
    
    console.log('\n✅ 搜索工具已就绪！');
    console.log('💡 使用 window._zParamSearchTool.search("关键词", "描述") 进行自定义搜索');
    
})();

