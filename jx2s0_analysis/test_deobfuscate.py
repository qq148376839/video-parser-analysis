"""
测试反混淆功能
"""

from deobfuscate_js import JavaScriptDeobfuscator

# 测试代码
test_code = '''
var _0xda7da8 = new XMLHttpRequest();
_0xda7da8['\\x6f\\x6e\\x72\\x65\\x61\\x64\\x79\\x73\\x74\\x61\\x74\\x65\\x63\\x68\\x61\\x6e\\x67\\x65'] = function() {
    var _0x4068b2 = JSON['\\x70\\x61\\x72\\x73\\x65'](_0xda7da8['\\x72\\x65\\x73\\x70\\x6f\\x6e\\x73\\x65\\x54\\x65\\x78\\x74']);
};
_0xda7da8['\\x6f\\x70\\x65\\x6e']('GET', 'https://example.com', true);
_0xda7da8['\\x73\\x65\\x6e\\x64'](null);
'''

print("原始代码:")
print(test_code)
print("\n" + "="*60 + "\n")

deobfuscator = JavaScriptDeobfuscator()
deobfuscated = deobfuscator.deobfuscate(test_code)

print("反混淆后:")
print(deobfuscated)

