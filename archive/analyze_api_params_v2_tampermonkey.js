// ==UserScript==
// @name         API参数分析工具 - 增强反调试版
// @namespace    http://tampermonkey.net/
// @version      2.1
// @description  分析API参数生成逻辑，彻底禁用debugger干扰
// @author       You
// @match        *://*/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    
    // 防止重复运行
    if (window._apiParamsAnalyzerLoaded) {
        console.log('⚠️ 分析脚本已加载，跳过重复加载');
        return;
    }
    window._apiParamsAnalyzerLoaded = true;
    
    console.log('🚀 开始分析API参数生成逻辑（Tampermonkey增强版）...');
    
    // ============================================
    // 1. 彻底禁用debugger（必须在最前面执行）
    // ============================================
    const disableDebugger = function() {
        // 方法1: 覆盖debugger关键字（通过Proxy）
        try {
            const handler = {
                get: function(target, prop) {
                    if (prop === 'debugger') {
                        return function() {};
                    }
                    return target[prop];
                }
            };
            window = new Proxy(window, handler);
        } catch (e) {}
        
        // 方法2: Hook Function构造函数 - 移除代码中的debugger语句
        const originalFunction = window.Function;
        window.Function = function(...args) {
            // 最后一个参数是函数体
            if (args.length > 0) {
                const lastArg = args[args.length - 1];
                if (typeof lastArg === 'string') {
                    // 移除debugger语句
                    args[args.length - 1] = lastArg.replace(/debugger\s*;?/gi, '');
                }
            }
            return originalFunction.apply(this, args);
        };
        
        // 保持Function的原型链
        window.Function.prototype = originalFunction.prototype;
        window.Function.prototype.constructor = window.Function;
        
        // 方法3: Hook eval - 移除eval中的debugger
        const originalEval = window.eval;
        window.eval = function(code) {
            if (typeof code === 'string') {
                code = code.replace(/debugger\s*;?/gi, '');
            }
            return originalEval.call(this, code);
        };
        
        // 方法4: Hook setTimeout/setInterval - 移除回调中的debugger
        const originalSetTimeout = window.setTimeout;
        const originalSetInterval = window.setInterval;
        
        window.setTimeout = function(callback, delay, ...args) {
            if (typeof callback === 'string') {
                callback = callback.replace(/debugger\s*;?/gi, '');
            } else if (typeof callback === 'function') {
                const originalCallback = callback;
                callback = function(...cbArgs) {
                    try {
                        return originalCallback.apply(this, cbArgs);
                    } catch (e) {
                        if (e.message && e.message.includes('debugger')) {
                            return;
                        }
                        throw e;
                    }
                };
            }
            return originalSetTimeout.call(this, callback, delay, ...args);
        };
        
        window.setInterval = function(callback, delay, ...args) {
            if (typeof callback === 'string') {
                callback = callback.replace(/debugger\s*;?/gi, '');
            } else if (typeof callback === 'function') {
                const originalCallback = callback;
                callback = function(...cbArgs) {
                    try {
                        return originalCallback.apply(this, cbArgs);
                    } catch (e) {
                        if (e.message && e.message.includes('debugger')) {
                            return;
                        }
                        throw e;
                    }
                };
            }
            return originalSetInterval.call(this, callback, delay, ...args);
        };
        
        // 方法5: Hook requestAnimationFrame
        const originalRAF = window.requestAnimationFrame;
        if (originalRAF) {
            window.requestAnimationFrame = function(callback) {
                if (typeof callback === 'function') {
                    const originalCallback = callback;
                    callback = function(...args) {
                        try {
                            return originalCallback.apply(this, args);
                        } catch (e) {
                            if (e.message && e.message.includes('debugger')) {
                                return;
                            }
                            throw e;
                        }
                    };
                }
                return originalRAF.call(this, callback);
            };
        }
        
        // 方法6: 覆盖Function.prototype.toString（防止检测）
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
            const result = originalToString.apply(this, arguments);
            // 移除返回字符串中的debugger
            return result.replace(/debugger\s*;?/gi, '');
        };
        
        // 方法7: 使用Object.defineProperty覆盖debugger
        try {
            Object.defineProperty(window, 'debugger', {
                get: function() { 
                    return function() {}; 
                },
                set: function() {},
                configurable: true,
                enumerable: false
            });
        } catch (e) {}
        
        // 方法8: 监听并拦截包含debugger的脚本执行
        try {
            const originalCreateElement = document.createElement;
            document.createElement = function(tagName) {
                const element = originalCreateElement.call(document, tagName);
                if (tagName.toLowerCase() === 'script') {
                    // Hook text 属性
                    const textDesc = Object.getOwnPropertyDescriptor(HTMLScriptElement.prototype, 'text');
                    if (textDesc && textDesc.set) {
                        const originalTextGetter = textDesc.get;
                        const originalTextSetter = textDesc.set;
                        Object.defineProperty(element, 'text', {
                            set: function(value) {
                                if (typeof value === 'string') {
                                    value = value.replace(/debugger\s*;?/gi, '');
                                }
                                originalTextSetter.call(this, value);
                            },
                            get: function() {
                                if (originalTextGetter) {
                                    return originalTextGetter.call(this);
                                }
                                return element.textContent;
                            },
                            configurable: true,
                            enumerable: true
                        });
                    }
                    
                    // Hook textContent 属性
                    const textContentDesc = Object.getOwnPropertyDescriptor(Node.prototype, 'textContent');
                    if (textContentDesc && textContentDesc.set) {
                        const originalTextContentGetter = textContentDesc.get;
                        const originalTextContentSetter = textContentDesc.set;
                        Object.defineProperty(element, 'textContent', {
                            set: function(value) {
                                if (typeof value === 'string') {
                                    value = value.replace(/debugger\s*;?/gi, '');
                                }
                                originalTextContentSetter.call(this, value);
                            },
                            get: function() {
                                if (originalTextContentGetter) {
                                    return originalTextContentGetter.call(this);
                                }
                                return '';
                            },
                            configurable: true,
                            enumerable: true
                        });
                    }
                }
                return element;
            };
        } catch (e) {
            // 如果Hook失败，静默忽略
            console.log('⚠️ createElement Hook失败（可忽略）:', e.message);
        }
        
        // 方法9: Hook script标签的innerHTML/textContent设置
        try {
            const scriptProto = HTMLScriptElement.prototype;
            const innerHTMLDesc = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML');
            if (innerHTMLDesc && innerHTMLDesc.set) {
                const originalInnerHTMLGetter = innerHTMLDesc.get;
                const originalInnerHTMLSetter = innerHTMLDesc.set;
                
                Object.defineProperty(scriptProto, 'innerHTML', {
                    set: function(value) {
                        if (typeof value === 'string') {
                            value = value.replace(/debugger\s*;?/gi, '');
                        }
                        originalInnerHTMLSetter.call(this, value);
                    },
                    get: function() {
                        if (originalInnerHTMLGetter) {
                            return originalInnerHTMLGetter.call(this);
                        }
                        // 如果getter不存在，使用默认行为
                        return this.textContent;
                    },
                    configurable: true,
                    enumerable: true
                });
            }
        } catch (e) {
            // 如果Hook失败，静默忽略（某些浏览器可能不支持）
            console.log('⚠️ innerHTML Hook失败（可忽略）:', e.message);
        }
    };
    
    // 立即执行，确保在所有其他代码之前
    disableDebugger();
    console.log('✅ Debugger已彻底禁用（Hook Function/eval/setTimeout等）');
    
    // ============================================
    // 2. Hook fetch请求
    // ============================================
    const hookFetch = function() {
        // 延迟执行，等待fetch API可用
        const tryHookFetch = function() {
            if (!window.fetch) {
                setTimeout(tryHookFetch, 100);
                return;
            }
            
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                    console.log('\n🔍 [Fetch] 捕获API调用:');
                    console.log('   URL:', url);
                    
                    try {
                        const urlObj = new URL(url, window.location.href);
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
        
        tryHookFetch();
    };
    
    hookFetch();
    
    // ============================================
    // 3. Hook XMLHttpRequest
    // ============================================
    const hookXHR = function() {
        // 延迟执行，等待XMLHttpRequest可用
        const tryHookXHR = function() {
            if (!window.XMLHttpRequest) {
                setTimeout(tryHookXHR, 100);
                return;
            }
            
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
                        const urlObj = new URL(url, window.location.href);
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
        
        tryHookXHR();
    };
    
    hookXHR();
    
    // ============================================
    // 4. 监听网络请求（使用Performance API）
    // ============================================
    const setupPerformanceObserver = function() {
        const trySetupObserver = function() {
            if (!window.PerformanceObserver) {
                setTimeout(trySetupObserver, 100);
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
        
        trySetupObserver();
    };
    
    setupPerformanceObserver();
    
    // ============================================
    // 5. 搜索参数生成函数（延迟执行）
    // ============================================
    const searchCode = function() {
        if (!document || !document.querySelectorAll) {
            setTimeout(searchCode, 500);
            return;
        }
        
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
    
    // ============================================
    // 6. 查找全局变量（延迟执行）
    // ============================================
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
    
    // ============================================
    // 7. 提供辅助函数（持久化到localStorage）
    // ============================================
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
                    const urlObj = new URL(url, window.location.href);
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
            },
            
            // 重新禁用debugger（手动调用）
            disableDebugger: function() {
                disableDebugger();
                console.log('✅ Debugger已重新禁用');
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
        console.log('   _analyzeApiParams.disableDebugger() - 重新禁用debugger');
    };
    
    setupHelpers();
    
    // ============================================
    // 8. 监听页面卸载，自动保存
    // ============================================
    const setupUnloadListener = function() {
        if (window.addEventListener) {
            window.addEventListener('beforeunload', function() {
                if (window._analyzeApiParams && window._apiCalls) {
                    window._analyzeApiParams.save();
                }
            });
        }
    };
    
    setupUnloadListener();
    
    console.log('\n✅ 分析脚本已加载完成（Tampermonkey增强版）！');
    console.log('💡 提示: 刷新页面后API调用会被自动捕获');
    console.log('💡 提示: Debugger已彻底禁用，可以正常使用F12调试');
    console.log('💡 提示: 如果页面刷新导致变量丢失，使用 _analyzeApiParams.load() 恢复');
})();

