/**
 * 浏览器调试脚本：分析 config.url 的用途
 * 
 * 使用方法：
 * 1. 打开浏览器，访问 https://jx.2s0.cn/player/?url=xxx
 * 2. 按 F12 打开开发者工具
 * 3. 切换到 Console 面板
 * 4. 复制此脚本并粘贴到控制台执行
 * 5. 观察输出，查看 config.url 的使用情况
 */

(function() {
    console.log('🔍 开始分析 config.url 的用途...');
    
    // 1. 拦截 YKQ.video 调用
    if (typeof YKQ !== 'undefined' && YKQ.video) {
        const originalVideo = YKQ.video;
        YKQ.video = function(url) {
            console.log('\n📹 [YKQ.video] 被调用');
            console.log('   参数类型:', typeof url);
            console.log('   参数值:', url);
            
            if (typeof url === 'string') {
                console.log('   ✅ URL字符串:', url);
                if (url.includes('m3u8') || url.includes('cachem3u8')) {
                    console.log('   🎬 找到m3u8 URL:', url);
                }
            } else if (url && typeof url === 'object') {
                console.log('   ✅ URL对象:', JSON.stringify(url, null, 2));
                if (url.url) {
                    console.log('   URL字段:', url.url);
                    if (url.url.includes('m3u8') || url.url.includes('cachem3u8')) {
                        console.log('   🎬 找到m3u8 URL:', url.url);
                    }
                }
            }
            
            // 打印调用栈
            console.log('   调用栈:');
            console.trace();
            
            return originalVideo.apply(this, arguments);
        };
        console.log('✅ 已拦截 YKQ.video');
    } else {
        console.log('⚠️ YKQ.video 未找到，等待加载...');
    }
    
    // 2. 拦截 rc4 函数
    if (typeof rc4 !== 'undefined') {
        const originalRc4 = rc4;
        window.rc4 = function(data, key, mode) {
            console.log('\n🔐 [rc4] 被调用');
            console.log('   数据:', data);
            console.log('   密钥:', key);
            console.log('   模式:', mode);
            
            const result = originalRc4(data, key, mode);
            console.log('   解密结果类型:', typeof result);
            console.log('   解密结果长度:', result.length);
            console.log('   解密结果前100字符:', result.substring(0, 100));
            
            // 尝试不同的处理方式
            try {
                // 尝试UTF-8解码
                const utf8Decoded = result.toString('utf8');
                console.log('   UTF-8解码:', utf8Decoded.substring(0, 100));
            } catch(e) {
                console.log('   UTF-8解码失败');
            }
            
            try {
                // 尝试十六进制
                const hex = Buffer.from(result).toString('hex');
                console.log('   十六进制:', hex.substring(0, 200));
            } catch(e) {
                console.log('   十六进制转换失败');
            }
            
            return result;
        };
        console.log('✅ 已拦截 rc4');
    } else {
        console.log('⚠️ rc4 函数未找到，等待加载...');
    }
    
    // 3. 监听 config 对象的变化
    if (typeof config !== 'undefined') {
        console.log('\n📋 [config] 对象已存在');
        console.log('   config.url:', config.url);
        console.log('   config.id:', config.id);
        
        // 尝试解密 config.url
        if (config.url && typeof rc4 !== 'undefined' && config.id) {
            try {
                const YKQ_id = config.id + ' P';
                console.log('\n🔐 尝试解密 config.url...');
                console.log('   密钥:', YKQ_id);
                
                const decrypted = rc4(config.url, YKQ_id, 1);
                console.log('   解密结果:', decrypted);
                console.log('   解密结果类型:', typeof decrypted);
                console.log('   解密结果长度:', decrypted.length);
                
                // 检查是否是URL
                if (typeof decrypted === 'string' && decrypted.startsWith('http')) {
                    console.log('   ✅ 解密后是URL:', decrypted);
                } else {
                    console.log('   ⚠️ 解密后不是URL，可能是二进制数据');
                }
            } catch(e) {
                console.log('   ❌ 解密失败:', e);
            }
        }
    } else {
        console.log('⚠️ config 对象未找到，等待加载...');
        
        // 监听 config 对象的创建
        Object.defineProperty(window, 'config', {
            set: function(value) {
                console.log('\n📋 [config] 对象被设置');
                console.log('   config.url:', value.url);
                console.log('   config.id:', value.id);
                this._config = value;
            },
            get: function() {
                return this._config;
            }
        });
    }
    
    // 4. 监听 YKQ.start 调用
    if (typeof YKQ !== 'undefined' && YKQ.start) {
        const originalStart = YKQ.start;
        YKQ.start = function() {
            console.log('\n🚀 [YKQ.start] 被调用');
            console.log('   config.url:', typeof config !== 'undefined' ? config.url : '未定义');
            console.log('   config.id:', typeof config !== 'undefined' ? config.id : '未定义');
            
            return originalStart.apply(this, arguments);
        };
        console.log('✅ 已拦截 YKQ.start');
    }
    
    // 5. 监听网络请求中的m3u8 URL
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string' && (url.includes('m3u8') || url.includes('cachem3u8'))) {
            console.log('\n🌐 [fetch] 发现m3u8请求');
            console.log('   URL:', url);
            console.log('   参数:', args);
        }
        return originalFetch.apply(this, args);
    };
    
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        if (typeof url === 'string' && (url.includes('m3u8') || url.includes('cachem3u8'))) {
            console.log('\n🌐 [XMLHttpRequest] 发现m3u8请求');
            console.log('   方法:', method);
            console.log('   URL:', url);
        }
        return originalOpen.apply(this, [method, url, ...args]);
    };
    
    console.log('\n✅ 调试脚本已加载完成！');
    console.log('📝 请观察页面加载过程中的输出...');
})();

