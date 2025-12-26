/**
 * 持久化API参数分析脚本
 * 使用MutationObserver和页面加载事件，确保在页面刷新后也能工作
 * 
 * 使用方法：
 * 1. 安装Tampermonkey扩展
 * 2. 创建新脚本
 * 3. 粘贴此代码
 * 4. 保存并启用
 */

// ==UserScript==
// @name         API参数分析器
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  分析videocdn.ihelpy.net的API参数生成逻辑
// @author       You
// @match        https://videocdn.ihelpy.net/*
// @match        https://m1-z2.cloud.nnpp.vip:2223/*
// @match        https://m1-a1.cloud.nnpp.vip:2223/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function() {
    'use strict';
    
    console.log('🚀 [UserScript] API参数分析器已启动');
    
    // 禁用debugger
    const disableDebugger = function() {
        window.debugger = function() {};
        try {
            Object.defineProperty(window, 'debugger', {
                get: function() { return function() {}; },
                set: function() {},
                configurable: true
            });
        } catch (e) {}
    };
    
    disableDebugger();
    
    // 存储API调用
    const apiCalls = [];
    
    // Hook fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
            const urlObj = new URL(url);
            const params = Object.fromEntries(urlObj.searchParams);
            
            console.log('\n🔍 [Fetch] 捕获API调用:');
            console.log('   URL:', url);
            console.log('   参数:', params);
            
            apiCalls.push({
                type: 'fetch',
                url: url,
                params: params,
                headers: args[1]?.headers || {},
                timestamp: new Date().toISOString()
            });
            
            // 保存到localStorage
            try {
                localStorage.setItem('_apiCalls', JSON.stringify(apiCalls));
            } catch (e) {}
        }
        return originalFetch.apply(this, args);
    };
    
    // Hook XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        this._url = url;
        if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
            const urlObj = new URL(url);
            const params = Object.fromEntries(urlObj.searchParams);
            
            console.log('\n🔍 [XHR] 捕获API调用:');
            console.log('   URL:', url);
            console.log('   参数:', params);
            
            apiCalls.push({
                type: 'xhr',
                method: method,
                url: url,
                params: params,
                timestamp: new Date().toISOString()
            });
            
            try {
                localStorage.setItem('_apiCalls', JSON.stringify(apiCalls));
            } catch (e) {}
        }
        return originalXHROpen.apply(this, [method, url, ...args]);
    };
    
    // 提供全局函数
    window._analyzeApiParams = {
        showCalls: function() {
            const saved = localStorage.getItem('_apiCalls');
            if (saved) {
                const calls = JSON.parse(saved);
                console.log('\n📋 所有API调用:');
                calls.forEach((call, index) => {
                    console.log(`\n[${index + 1}]`, call.type.toUpperCase());
                    console.log('   URL:', call.url);
                    console.log('   参数:', call.params);
                    console.log('   时间:', call.timestamp);
                    if (call.headers) {
                        console.log('   请求头:', call.headers);
                    }
                });
                return calls;
            } else {
                console.log('⚠️ 没有保存的API调用');
                return [];
            }
        },
        
        clear: function() {
            localStorage.removeItem('_apiCalls');
            console.log('✅ 已清除保存的数据');
        }
    };
    
    // 页面加载完成后显示提示
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('\n✅ API参数分析器已就绪');
            console.log('💡 使用 _analyzeApiParams.showCalls() 查看所有API调用');
        });
    } else {
        console.log('\n✅ API参数分析器已就绪');
        console.log('💡 使用 _analyzeApiParams.showCalls() 查看所有API调用');
    }
})();

