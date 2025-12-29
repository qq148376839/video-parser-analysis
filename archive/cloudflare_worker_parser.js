/**
 * Cloudflare Workers 视频解析器
 * 部署到Cloudflare Workers，无需服务器
 */

// 从环境变量或KV存储获取z参数
async function generateZParam(videoUrl, env) {
  // 方案1: 从KV存储读取（如果配置了）
  if (env && env.Z_PARAMS_KV) {
    const cachedZParam = await env.Z_PARAMS_KV.get('latest_z_param');
    if (cachedZParam) {
      return cachedZParam;
    }
  }
  
  // 方案2: 从环境变量读取
  if (env && env.DEFAULT_Z_PARAM) {
    return env.DEFAULT_Z_PARAM;
  }
  
  // 默认值（可能已过期，需要定期更新）
  return "b413af76b43b1a0abc231718862417e2";
}

// 获取s1ig参数
function getS1igParam(env) {
  // 从环境变量读取
  if (env && env.DEFAULT_S1IG_PARAM) {
    return env.DEFAULT_S1IG_PARAM;
  }
  return "11397";
}

// 获取g参数
function getGParam(env) {
  // 从环境变量读取
  if (env && env.DEFAULT_G_PARAM !== undefined) {
    return env.DEFAULT_G_PARAM;
  }
  return "";
}

// 构造API URL
function constructApiUrl(videoUrl, zParam, s1igParam, gParam, useHttp = false) {
  // 如果遇到525错误，可以尝试使用HTTP
  const protocol = useHttp ? "http" : "https";
  const baseUrl = `${protocol}://m1-a1.cloud.nnpp.vip:2223/api/v/`;
  const params = new URLSearchParams({
    z: zParam,
    jx: videoUrl,
    s1ig: s1igParam,
    g: gParam
  });
  return `${baseUrl}?${params.toString()}`;
}

// 调用解析API（使用代理）
async function callParserApi(apiUrl, useProxy = false) {
  try {
    let finalUrl = apiUrl;
    let isProxy = false;
    
    // 如果使用代理，包装URL
    if (useProxy) {
      // 尝试不同的代理服务
      // 方案1: allorigins.win（可能被API拒绝）
      // finalUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(apiUrl)}`;
      
      // 方案2: corsproxy.io
      finalUrl = `https://corsproxy.io/?${encodeURIComponent(apiUrl)}`;
      isProxy = true;
    }
    
    const response = await fetch(finalUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://m1-z2.cloud.nnpp.vip:2223/',
        'Origin': 'https://m1-z2.cloud.nnpp.vip:2223',
      },
      cf: {
        // Cloudflare Workers配置
        cacheTtl: 0, // 禁用缓存，避免缓存错误响应
        cacheEverything: false,
      },
      // 增加超时时间
      signal: AbortSignal.timeout(30000), // 30秒超时
    });
    
    // 检查响应状态
    if (!response.ok) {
      let errorText = '';
      try {
        errorText = await response.text();
      } catch (e) {
        errorText = '无法读取错误响应';
      }
      
      // 520/525错误通常是Cloudflare的问题，不是目标服务器的问题
      if (response.status === 520 || response.status === 525) {
        throw new Error(`Cloudflare错误(${response.status}): 无法连接到目标服务器。这可能是因为目标服务器阻止了Cloudflare的请求，或者SSL/TLS配置不兼容。`);
      }
      
      throw new Error(`API请求失败: ${response.status} ${response.statusText}${errorText ? ' - ' + errorText.substring(0, 100) : ''}`);
    }
    
    // 处理响应
    // 注意：响应可能是Brotli压缩的，但fetch会自动解压
    let text = await response.text();
    
    // 如果使用代理，需要解析代理返回的格式
    if (isProxy) {
      try {
        const proxyData = JSON.parse(text);
        // allorigins.win返回格式: {contents: "...", status: {...}}
        text = proxyData.contents || text;
        
        // 检查代理返回的状态
        if (proxyData.status && proxyData.status.http_code !== 200) {
          throw new Error(`代理返回错误: HTTP ${proxyData.status.http_code}`);
        }
      } catch (e) {
        // 如果不是代理格式，继续使用原始文本
        if (e.message.includes('代理返回错误')) {
          throw e;
        }
      }
    }
    
    // 调试：记录响应内容
    console.log('响应内容预览:', text.substring(0, 200));
    
    // 检查是否是错误信息
    if (text.includes('联系QQ') || text.includes('获取json版api地址')) {
      throw new Error('参数已过期，需要更新z参数');
    }
    
    // 尝试解析JSON
    try {
      const jsonData = JSON.parse(text);
      
      // 检查是否是错误响应
      // type: 4000 通常表示错误（但type也可能是字符串"movie"或"tv"）
      if (typeof jsonData.type === 'number' && jsonData.type >= 4000) {
        throw new Error(`API返回错误: type=${jsonData.type}, message=${jsonData.message || jsonData.msg || '未知错误'}`);
      }
      
      // 正常响应应该有data字段，且type应该是"movie"或"tv"
      if (!jsonData.data) {
        // 如果type是数字且不是4000，可能是其他错误码
        if (typeof jsonData.type === 'number') {
          throw new Error(`API返回错误码: type=${jsonData.type}, 响应: ${JSON.stringify(jsonData)}`);
        }
        // 如果type是字符串但不是movie/tv，也可能是错误
        if (typeof jsonData.type === 'string' && jsonData.type !== 'movie' && jsonData.type !== 'tv') {
          throw new Error(`API返回异常响应: type=${jsonData.type}, 响应: ${JSON.stringify(jsonData)}`);
        }
      }
      
      // 调试：记录API响应结构
      console.log('API响应类型:', typeof jsonData);
      console.log('API响应键:', Object.keys(jsonData || {}));
      return jsonData;
    } catch (parseError) {
      // 如果已经是我们抛出的错误，直接抛出
      if (parseError.message.includes('API返回错误') || parseError.message.includes('API返回异常响应')) {
        throw parseError;
      }
      throw new Error(`JSON解析失败: ${parseError.message}, 响应内容: ${text.substring(0, 200)}`);
    }
  } catch (error) {
    // 如果是网络错误，提供更详细的错误信息
    if (error.message.includes('525') || error.message.includes('SSL') || error.message.includes('handshake')) {
      throw new Error(`SSL握手失败(525): 可能是目标服务器SSL配置问题。原始错误: ${error.message}`);
    }
    throw error;
  }
}

// 从API响应中提取m3u8链接
function extractM3u8Urls(apiResponse) {
  const m3u8Urls = [];
  
  function findM3u8(obj, path = '') {
    if (typeof obj === 'object' && obj !== null) {
      if (Array.isArray(obj)) {
        obj.forEach((item, index) => findM3u8(item, `${path}[${index}]`));
      } else {
        Object.entries(obj).forEach(([key, value]) => {
          const currentPath = path ? `${path}.${key}` : key;
          
          if (typeof value === 'string') {
            // 检查是否是m3u8链接
            if (value.includes('.m3u8') && value.startsWith('http')) {
              if (!m3u8Urls.includes(value)) {
                m3u8Urls.push(value);
                console.log(`找到m3u8链接 (${currentPath}): ${value}`);
              }
            }
            // 也检查是否包含m3u8但需要补全URL
            else if (value.includes('.m3u8') && !value.startsWith('http')) {
              // 尝试补全URL
              const fullUrl = value.startsWith('//') ? `https:${value}` : 
                             value.startsWith('/') ? `https://m1-a1.cloud.nnpp.vip:2223${value}` : value;
              if (fullUrl.startsWith('http') && !m3u8Urls.includes(fullUrl)) {
                m3u8Urls.push(fullUrl);
                console.log(`找到相对m3u8链接 (${currentPath}): ${fullUrl}`);
              }
            }
          } else {
            findM3u8(value, currentPath);
          }
        });
      }
    }
  }
  
  findM3u8(apiResponse);
  return m3u8Urls;
}

// 主处理函数
async function parseVideo(videoUrl, env) {
  try {
    // 1. 生成z参数
    const zParam = await generateZParam(videoUrl, env);
    const s1igParam = getS1igParam(env);
    const gParam = getGParam(env);
    
    // 2. 构造API URL（先尝试HTTPS）
    let apiUrl = constructApiUrl(videoUrl, zParam, s1igParam, gParam, false);
    
    // 3. 调用API，如果遇到520/525错误，尝试HTTP，最后尝试代理
    let apiResponse;
    try {
      // 先尝试HTTPS直接连接
      apiResponse = await callParserApi(apiUrl, false);
    } catch (error) {
      // 如果是520/525错误，尝试使用HTTP
      if (error.message.includes('520') || error.message.includes('525') || error.message.includes('SSL') || error.message.includes('Cloudflare错误')) {
        console.log('HTTPS失败，尝试HTTP...');
        apiUrl = constructApiUrl(videoUrl, zParam, s1igParam, gParam, true);
        try {
          apiResponse = await callParserApi(apiUrl, false);
        } catch (httpError) {
          // HTTP也失败，尝试使用代理
          console.log('HTTP也失败，尝试使用代理...');
          try {
            // 使用HTTPS URL通过代理
            const httpsUrl = constructApiUrl(videoUrl, zParam, s1igParam, gParam, false);
            apiResponse = await callParserApi(httpsUrl, true);
          } catch (proxyError) {
            // 所有方法都失败
            throw new Error(`所有连接方式都失败。HTTPS: ${error.message}; HTTP: ${httpError.message}; 代理: ${proxyError.message}`);
          }
        }
      } else {
        throw error;
      }
    }
    
    // 4. 提取m3u8链接
    const m3u8Urls = extractM3u8Urls(apiResponse);
    
    // 调试：记录提取结果
    console.log('提取到的m3u8链接数量:', m3u8Urls.length);
    console.log('API响应结构:', JSON.stringify(apiResponse).substring(0, 500));
    
    if (m3u8Urls.length === 0) {
      // 返回更详细的错误信息，包含API响应
      throw new Error(`未找到m3u8链接。API响应: ${JSON.stringify(apiResponse).substring(0, 500)}`);
    }
    
    return {
      success: true,
      video_url: videoUrl,
      m3u8_urls: m3u8Urls,
      best_m3u8: m3u8Urls[0], // 选择第一个
      api_response: apiResponse
    };
    
  } catch (error) {
    return {
      success: false,
      error: error.message,
      video_url: videoUrl
    };
  }
}

// Cloudflare Workers入口
export default {
  async fetch(request, env, ctx) {
    // 处理CORS
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }
    
    const url = new URL(request.url);
    
    // API端点: /api/parse?video_url=...
    if (url.pathname === '/api/parse') {
      const videoUrl = url.searchParams.get('video_url');
      
      if (!videoUrl) {
        return new Response(JSON.stringify({
          success: false,
          error: '缺少video_url参数'
        }), {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }
      
      const result = await parseVideo(videoUrl, env);
      
      return new Response(JSON.stringify(result), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }
    
    // 健康检查
    if (url.pathname === '/health') {
      return new Response(JSON.stringify({ status: 'ok' }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }
    
    // 默认返回API文档
    return new Response(JSON.stringify({
      message: 'Video Parser API',
      endpoints: {
        '/api/parse': 'GET ?video_url=<视频URL>',
        '/health': 'GET 健康检查'
      }
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  },
};

