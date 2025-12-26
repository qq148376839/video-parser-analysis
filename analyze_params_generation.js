/**
 * 分析z和g参数生成逻辑
 * 在Console中运行此脚本，然后触发API调用
 */

(function() {
    'use strict';
    
    console.log('🔍 开始分析参数生成逻辑...');
    
    // 保存所有API调用和相关的变量
    const apiCalls = [];
    const variableSnapshots = [];
    
    // Hook fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string' && url.includes('api/v')) {
            const urlObj = new URL(url);
            const params = Object.fromEntries(urlObj.searchParams);
            
            console.log('\n🔍 [Fetch] 捕获API调用:');
            console.log('   URL:', url);
            console.log('   参数:', params);
            
            // 保存调用栈
            const stack = new Error().stack;
            
            // 保存当前所有全局变量（可能包含参数生成逻辑）
            const globals = {};
            for (const key in window) {
                try {
                    if (typeof window[key] === 'string' || typeof window[key] === 'number') {
                        globals[key] = window[key];
                    }
                } catch (e) {}
            }
            
            apiCalls.push({
                url: url,
                params: params,
                stack: stack,
                globals: globals,
                timestamp: new Date().toISOString()
            });
            
            // 分析参数
            analyzeParams(params, stack);
        }
        return originalFetch.apply(this, args);
    };
    
    // 分析参数生成逻辑
    function analyzeParams(params, stack) {
        console.log('\n📊 参数分析:');
        console.log('   z参数:', params.z);
        console.log('   s1ig参数:', params.s1ig);
        console.log('   g参数:', params.g);
        console.log('   jx参数:', params.jx);
        
        // 分析z参数（32字符，可能是MD5）
        if (params.z) {
            console.log('\n🔍 分析z参数:');
            console.log('   长度:', params.z.length);
            console.log('   格式:', /^[a-f0-9]{32}$/i.test(params.z) ? 'MD5哈希' : '其他格式');
            
            // 尝试查找z参数的生成逻辑
            console.log('   💡 搜索可能的生成逻辑...');
            searchForHashFunction('z', params.z);
        }
        
        // 分析g参数
        if (params.g) {
            console.log('\n🔍 分析g参数:');
            console.log('   值:', params.g);
            console.log('   格式:', /^[a-z0-9]+\.[a-z0-9]+$/i.test(params.g) ? '域名格式' : '其他格式');
            
            // 尝试从m3u8 URL中提取
            if (params.g.includes('.')) {
                const parts = params.g.split('.');
                console.log('   可能的结构:', {
                    subdomain: parts[0],
                    domain_part: parts.slice(1).join('.')
                });
            }
        }
        
        // 分析调用栈
        console.log('\n📋 调用栈分析:');
        const stackLines = stack.split('\n').slice(1, 10);
        stackLines.forEach((line, index) => {
            console.log(`   [${index + 1}]`, line.trim());
            
            // 尝试从调用栈中找到相关文件
            const match = line.match(/at\s+(.+?)\s+\((.+?):(\d+):(\d+)\)/);
            if (match) {
                const [, func, file, lineNum, col] = match;
                console.log(`      函数: ${func}`);
                console.log(`      文件: ${file}`);
                console.log(`      行号: ${lineNum}`);
            }
        });
    }
    
    // 搜索哈希函数
    function searchForHashFunction(paramName, value) {
        // 搜索常见的哈希函数调用
        const hashPatterns = [
            'md5',
            'sha256',
            'sha1',
            'hash',
            'crypto',
            'encrypt',
            'digest'
        ];
        
        console.log(`   🔍 搜索${paramName}参数的哈希函数...`);
        
        // 在全局对象中搜索
        for (const key in window) {
            try {
                const obj = window[key];
                if (typeof obj === 'object' && obj !== null) {
                    const objStr = JSON.stringify(obj).toLowerCase();
                    if (hashPatterns.some(pattern => objStr.includes(pattern))) {
                        console.log(`   ✅ 找到可能相关的对象: ${key}`);
                    }
                }
            } catch (e) {}
        }
        
        // 搜索脚本中的哈希函数
        const scripts = document.querySelectorAll('script');
        scripts.forEach((script, index) => {
            const content = script.textContent || script.innerHTML;
            hashPatterns.forEach(pattern => {
                if (content.toLowerCase().includes(pattern)) {
                    console.log(`   ✅ 脚本[${index}]包含"${pattern}"`);
                    // 提取相关代码
                    const lines = content.split('\n');
                    lines.forEach((line, lineNum) => {
                        if (line.toLowerCase().includes(pattern) && 
                            (line.includes('z') || line.includes('param') || line.includes('api'))) {
                            console.log(`      行 ${lineNum + 1}: ${line.trim().substring(0, 150)}`);
                        }
                    });
                }
            });
        });
    }
    
    // 提供分析函数
    window._analyzeParams = {
        showCalls: function() {
            console.log('\n📋 所有API调用:');
            apiCalls.forEach((call, index) => {
                console.log(`\n[${index + 1}]`);
                console.log('   URL:', call.url);
                console.log('   参数:', call.params);
                console.log('   时间:', call.timestamp);
            });
            return apiCalls;
        },
        
        analyzeZ: function() {
            if (apiCalls.length === 0) {
                console.log('⚠️ 没有捕获到API调用');
                return;
            }
            
            const zValues = apiCalls.map(call => call.params.z).filter(Boolean);
            if (zValues.length === 0) {
                console.log('⚠️ 没有找到z参数');
                return;
            }
            
            console.log('\n🔍 z参数分析:');
            console.log('   所有值:', zValues);
            console.log('   是否相同:', new Set(zValues).size === 1 ? '是（可能是固定值）' : '否（可能是动态生成）');
            console.log('   长度:', zValues[0].length);
            console.log('   格式:', /^[a-f0-9]{32}$/i.test(zValues[0]) ? 'MD5哈希（32位十六进制）' : '其他格式');
            
            // 尝试反向查找
            console.log('\n💡 尝试查找生成逻辑...');
            searchForHashFunction('z', zValues[0]);
        },
        
        analyzeG: function() {
            if (apiCalls.length === 0) {
                console.log('⚠️ 没有捕获到API调用');
                return;
            }
            
            const gValues = apiCalls.map(call => call.params.g).filter(Boolean);
            if (gValues.length === 0) {
                console.log('⚠️ 没有找到g参数');
                return;
            }
            
            console.log('\n🔍 g参数分析:');
            console.log('   所有值:', gValues);
            console.log('   是否相同:', new Set(gValues).size === 1 ? '是（可能是固定值）' : '否（可能是动态生成）');
            
            // 分析g参数的模式
            gValues.forEach((g, index) => {
                console.log(`\n   值[${index + 1}]: ${g}`);
                if (g.includes('.')) {
                    const parts = g.split('.');
                    console.log(`      结构: ${parts[0]}.${parts.slice(1).join('.')}`);
                    console.log(`      可能是: 子域名.域名部分`);
                }
            });
            
            // 尝试从m3u8 URL中匹配
            console.log('\n💡 尝试从m3u8 URL中匹配...');
            const scripts = document.querySelectorAll('script');
            scripts.forEach((script, index) => {
                const content = script.textContent || script.innerHTML;
                gValues.forEach(g => {
                    if (content.includes(g)) {
                        console.log(`   ✅ 脚本[${index}]包含g参数值"${g}"`);
                        const lines = content.split('\n');
                        lines.forEach((line, lineNum) => {
                            if (line.includes(g)) {
                                console.log(`      行 ${lineNum + 1}: ${line.trim().substring(0, 150)}`);
                            }
                        });
                    }
                });
            });
        },
        
        compareCalls: function() {
            if (apiCalls.length < 2) {
                console.log('⚠️ 需要至少2个API调用来比较');
                return;
            }
            
            console.log('\n🔍 比较多个API调用:');
            const params = ['z', 's1ig', 'g', 'jx'];
            params.forEach(param => {
                const values = apiCalls.map(call => call.params[param]).filter(Boolean);
                if (values.length > 0) {
                    const unique = new Set(values);
                    console.log(`   ${param}: ${unique.size === 1 ? '固定值' : '动态值'} (${unique.size}个不同值)`);
                    if (unique.size > 1) {
                        console.log(`      值:`, Array.from(unique));
                    }
                }
            });
        }
    };
    
    console.log('\n✅ 参数分析脚本已加载！');
    console.log('\n📖 使用方法:');
    console.log('   1. 触发API调用（刷新页面或操作页面）');
    console.log('   2. _analyzeParams.showCalls() - 查看所有调用');
    console.log('   3. _analyzeParams.analyzeZ() - 分析z参数');
    console.log('   4. _analyzeParams.analyzeG() - 分析g参数');
    console.log('   5. _analyzeParams.compareCalls() - 比较多个调用');
})();

