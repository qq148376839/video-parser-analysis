/**
 * 分析API参数生成逻辑的浏览器脚本 v2
 * 改进版：自动在页面加载后运行，并持久化
 * 
 * 使用方法：
 * 方法1: 在页面加载前注入（推荐）
 *   1. 打开Chrome DevTools
 *   2. 进入Sources标签页
 *   3. 点击"Overrides"标签
 *   4. 选择本地文件夹
 *   5. 创建文件覆盖
 * 
 * 方法2: 使用Console（页面加载后）
 *   1. 打开目标页面
 *   2. 按F12打开开发者工具
 *   3. 在Console中粘贴此脚本
 *   4. 刷新页面
 * 
 * 方法3: 使用Snippets（推荐）
 *   1. 打开Chrome DevTools
 *   2. 进入Sources标签页
 *   3. 点击"Snippets"
 *   4. 新建Snippet，粘贴此代码
 *   5. 右键运行
 */

(function() {
    'use strict';
    
    // 防止重复运行
    if (window._apiParamsAnalyzerLoaded) {
        console.log('⚠️ 分析脚本已加载，跳过重复加载');
        return;
    }
    window._apiParamsAnalyzerLoaded = true;
    
    console.log('🚀 开始分析API参数生成逻辑...');
    
    // 1. 禁用debugger（多种方式）
    const disableDebugger = function() {
        // 方法1: 覆盖debugger函数
        window.debugger = function() {};
        
        // 方法2: 使用Object.defineProperty
        try {
            Object.defineProperty(window, 'debugger', {
                get: function() { return function() {}; },
                set: function() {},
                configurable: true
            });
        } catch (e) {}
        
        // 方法3: 删除debugger
        try {
            delete window.debugger;
        } catch (e) {}
        
        // 方法4: 覆盖Function.prototype.toString（防止检测）
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === window.debugger || this.toString === originalToString) {
                return 'function debugger() { [native code] }';
            }
            return originalToString.apply(this, arguments);
        };
    };
    
    disableDebugger();
    console.log('✅ Debugger已禁用');
    
    // 2. Hook fetch请求
    const hookFetch = function() {
        if (!window.fetch) {
            console.log('⚠️ Fetch API不可用');
            return;
        }
        
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const url = args[0];
            if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                console.log('\n🔍 [Fetch] 捕获API调用:');
                console.log('   URL:', url);
                
                try {
                    const urlObj = new URL(url);
                    console.log('   参数:');
                    urlObj.searchParams.forEach((value, key) => {
                        console.log(`     ${key}: ${value}`);
                    });
                    
                    // 保存到全局变量
                    if (!window._apiCalls) {
                        window._apiCalls = [];
                    }
                    window._apiCalls.push({
                        type: 'fetch',
                        url: url,
                        timestamp: new Date().toISOString(),
                        params: Object.fromEntries(urlObj.searchParams),
                        stack: new Error().stack.split('\n').slice(1, 10)
                    });
                } catch (e) {
                    console.log('   无法解析URL:', e);
                }
            }
            return originalFetch.apply(this, args);
        };
        console.log('✅ Fetch已Hook');
    };
    
    hookFetch();
    
    // 3. Hook XMLHttpRequest
    const hookXHR = function() {
        const originalXHROpen = XMLHttpRequest.prototype.open;
        const originalXHRSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._url = url;
            this._method = method;
            if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                console.log('\n🔍 [XHR] 捕获API调用:');
                console.log('   Method:', method);
                console.log('   URL:', url);
                
                try {
                    const urlObj = new URL(url);
                    console.log('   参数:');
                    urlObj.searchParams.forEach((value, key) => {
                        console.log(`     ${key}: ${value}`);
                    });
                    
                    // 保存到全局变量
                    if (!window._apiCalls) {
                        window._apiCalls = [];
                    }
                    window._apiCalls.push({
                        type: 'xhr',
                        method: method,
                        url: url,
                        timestamp: new Date().toISOString(),
                        params: Object.fromEntries(urlObj.searchParams)
                    });
                } catch (e) {
                    console.log('   无法解析URL:', e);
                }
            }
            return originalXHROpen.apply(this, [method, url, ...args]);
        };
        
        XMLHttpRequest.prototype.send = function(...args) {
            if (this._url && (this._url.includes('api/v') || this._url.includes('m1-a1.cloud'))) {
                console.log('   Request Headers:', this.getAllResponseHeaders ? '已设置' : 'N/A');
            }
            return originalXHRSend.apply(this, args);
        };
        console.log('✅ XMLHttpRequest已Hook');
    };
    
    hookXHR();
    
    // 4. 监听网络请求（使用Performance API）
    const setupPerformanceObserver = function() {
        if (!window.PerformanceObserver) {
            console.log('⚠️ PerformanceObserver不可用');
            return;
        }
        
        try {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.name && (entry.name.includes('api/v') || entry.name.includes('m1-a1.cloud'))) {
                        console.log('\n📡 [Performance] 捕获资源:');
                        console.log('   URL:', entry.name);
                        console.log('   类型:', entry.initiatorType);
                    }
                }
            });
            
            observer.observe({ entryTypes: ['resource', 'navigation'] });
            console.log('✅ Performance Observer已启动');
        } catch (e) {
            console.log('⚠️ Performance Observer启动失败:', e);
        }
    };
    
    setupPerformanceObserver();
    
    // 5. 搜索参数生成函数
    const searchCode = function() {
        console.log('\n🔍 搜索参数生成相关代码...');
        
        const searchTerms = ['z=', 'z:', 's1ig', 'api/v', 'm1-a1.cloud', 'e8e56ecaca35c6229baa93884b6b7323'];
        const scripts = document.querySelectorAll('script');
        let found = false;
        
        scripts.forEach((script, index) => {
            if (script.src) {
                // 外部脚本
                if (searchTerms.some(term => script.src.includes(term))) {
                    console.log(`   📄 外部脚本 [${index}]: ${script.src}`);
                    found = true;
                }
            } else {
                // 内联脚本
                const content = script.textContent || script.innerHTML;
                searchTerms.forEach(term => {
                    if (content.includes(term)) {
                        console.log(`   📄 内联脚本 [${index}] 包含 "${term}"`);
                        found = true;
                        // 尝试提取相关代码
                        const lines = content.split('\n');
                        lines.forEach((line, lineNum) => {
                            if (line.includes(term)) {
                                console.log(`      行 ${lineNum + 1}: ${line.trim().substring(0, 150)}`);
                            }
                        });
                    }
                });
            }
        });
        
        if (!found) {
            console.log('   ⚠️ 未找到相关代码，可能在外部的JS文件中');
            console.log('   💡 建议：在Network标签页查看加载的JS文件');
        }
    };
    
    // 延迟搜索，等待脚本加载
    setTimeout(searchCode, 2000);
    
    // 6. 查找全局变量
    const findGlobalVars = function() {
        console.log('\n🔍 查找可能的全局变量...');
        const possibleVars = ['z', 's1ig', 'apiUrl', 'api_url', 'videoUrl', 'video_url', 'config', 'Config'];
        let found = false;
        
        possibleVars.forEach(varName => {
            if (window[varName] !== undefined) {
                console.log(`   ✅ 找到全局变量 ${varName}:`, window[varName]);
                found = true;
            }
        });
        
        if (!found) {
            console.log('   ⚠️ 未找到明显的全局变量');
        }
    };
    
    // 延迟查找，等待页面初始化
    setTimeout(findGlobalVars, 1000);
    
    // 7. 提供辅助函数（持久化到localStorage）
    const setupHelpers = function() {
        window._analyzeApiParams = {
            // 查看所有捕获的API调用
            showCalls: function() {
                if (window._apiCalls && window._apiCalls.length > 0) {
                    console.log('\n📋 所有API调用:');
                    window._apiCalls.forEach((call, index) => {
                        console.log(`\n[${index + 1}] ${call.type.toUpperCase()}`);
                        console.log('   URL:', call.url);
                        console.log('   时间:', call.timestamp);
                        if (call.params) {
                            console.log('   参数:');
                            Object.entries(call.params).forEach(([key, value]) => {
                                console.log(`     ${key}: ${value}`);
                            });
                        }
                        if (call.stack) {
                            console.log('   调用栈:');
                            call.stack.forEach(line => console.log('     ', line));
                        }
                    });
                    return window._apiCalls;
                } else {
                    console.log('⚠️ 尚未捕获到API调用');
                    console.log('💡 提示: 刷新页面或触发API调用');
                    return [];
                }
            },
            
            // 提取参数
            extractParams: function(url) {
                try {
                    const urlObj = new URL(url);
                    const params = {};
                    urlObj.searchParams.forEach((value, key) => {
                        params[key] = value;
                    });
                    console.log('📋 提取的参数:', params);
                    return params;
                } catch (e) {
                    console.error('❌ 解析URL失败:', e);
                    return null;
                }
            },
            
            // 搜索代码中的参数生成逻辑
            searchCode: function(keyword) {
                console.log(`\n🔍 搜索关键词: "${keyword}"`);
                const scripts = document.querySelectorAll('script');
                let found = false;
                
                scripts.forEach((script, index) => {
                    const content = script.textContent || script.innerHTML;
                    if (content.includes(keyword)) {
                        console.log(`\n📄 脚本 [${index}]:`);
                        found = true;
                        const lines = content.split('\n');
                        lines.forEach((line, lineNum) => {
                            if (line.includes(keyword)) {
                                console.log(`   行 ${lineNum + 1}: ${line.trim()}`);
                            }
                        });
                    }
                });
                
                if (!found) {
                    console.log('⚠️ 未找到包含该关键词的代码');
                    console.log('💡 建议：在Network标签页查看加载的JS文件');
                }
            },
            
            // 分析参数z的生成逻辑
            analyzeZ: function() {
                console.log('\n🔍 分析z参数生成逻辑...');
                this.searchCode('z=');
                this.searchCode('e8e56ecaca35c6229baa93884b6b7323');
                console.log('\n💡 提示: z参数可能是MD5/SHA256哈希值');
                console.log('   当前值: e8e56ecaca35c6229baa93884b6b7323');
                console.log('   长度: 32字符（可能是MD5）');
            },
            
            // 分析参数s1ig的生成逻辑
            analyzeS1ig: function() {
                console.log('\n🔍 分析s1ig参数生成逻辑...');
                this.searchCode('s1ig');
                console.log('\n💡 提示: s1ig参数可能是固定值或基于某些规则生成');
                console.log('   当前值: 11402');
            },
            
            // 保存结果到localStorage
            save: function() {
                if (window._apiCalls && window._apiCalls.length > 0) {
                    try {
                        localStorage.setItem('_apiCalls', JSON.stringify(window._apiCalls));
                        console.log('✅ 已保存到localStorage');
                    } catch (e) {
                        console.error('❌ 保存失败:', e);
                    }
                } else {
                    console.log('⚠️ 没有数据可保存');
                }
            },
            
            // 从localStorage加载
            load: function() {
                try {
                    const saved = localStorage.getItem('_apiCalls');
                    if (saved) {
                        window._apiCalls = JSON.parse(saved);
                        console.log('✅ 已从localStorage加载');
                        this.showCalls();
                    } else {
                        console.log('⚠️ localStorage中没有保存的数据');
                    }
                } catch (e) {
                    console.error('❌ 加载失败:', e);
                }
            }
        };
        
        console.log('\n✅ 辅助函数已设置！');
        console.log('\n📖 使用方法:');
        console.log('   _analyzeApiParams.showCalls()      - 查看所有API调用');
        console.log('   _analyzeApiParams.extractParams(url) - 提取URL参数');
        console.log('   _analyzeApiParams.searchCode(keyword) - 搜索代码');
        console.log('   _analyzeApiParams.analyzeZ()      - 分析z参数');
        console.log('   _analyzeApiParams.analyzeS1ig()   - 分析s1ig参数');
        console.log('   _analyzeApiParams.save()           - 保存到localStorage');
        console.log('   _analyzeApiParams.load()          - 从localStorage加载');
    };
    
    setupHelpers();
    
    // 8. 监听页面卸载，自动保存
    window.addEventListener('beforeunload', function() {
        if (window._analyzeApiParams && window._apiCalls) {
            window._analyzeApiParams.save();
        }
    });
    
    console.log('\n✅ 分析脚本已加载完成！');
    console.log('💡 提示: 刷新页面后API调用会被自动捕获');
    console.log('💡 提示: 如果页面刷新导致变量丢失，使用 _analyzeApiParams.load() 恢复');
})();

