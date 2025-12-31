'use strict';
Object.defineProperty(exports, '__esModule', { value: true });
var _typeof = typeof Symbol === 'function' && typeof Symbol.iterator === 'symbol' ? function (obj) {
    return typeof obj;
} : function (obj) {
    return obj && typeof Symbol === 'function' && obj.constructor === Symbol && obj !== Symbol.prototype ? 'symbol' : typeof obj;
};
var _createClass = function () {
    function defineProperties(target, props) {
        for (var i = 0; i < props.length; i++) {
            var descriptor = props[i];
            descriptor.enumerable = descriptor.enumerable || false;
            descriptor.configurable = true;
            if ('value' in descriptor)
                descriptor.writable = true;
            Object.defineProperty(target, descriptor.key, descriptor);
        }
    }
    return function (Constructor, protoProps, staticProps) {
        if (protoProps)
            defineProperties(Constructor.prototype, protoProps);
        if (staticProps)
            defineProperties(Constructor, staticProps);
        return Constructor;
    };
}();
var _utils = require('./utils');
var _utils2 = _interopRequireDefault(_utils);
function _interopRequireDefault(obj) {
    return obj && obj.__esModule ? obj : { default: obj };
}
function _classCallCheck(instance, Constructor) {
    if (!(instance instanceof Constructor)) {
        throw new TypeError('Cannot call a class as a function');
    }
}
var Danmaku = function () {
    function Danmaku(options) {
        _classCallCheck(this, Danmaku);
        this.options = options;
        this.container = this.options.container;
        this.danTunnel = {
            right: {},
            top: {},
            bottom: {}
        };
        this.danIndex = 0;
        this.dan = [];
        this.showing = true;
        this._opacity = this.options.opacity;
        this.events = this.options.events;
        this.unlimited = this.options.unlimited;
        this._measure('');
        this.load();
    }
    _createClass(Danmaku, [
        {
            key: 'load',
            value: function load() {
                var _this = this;
                var apiurl = void 0;
                if (this.options.api.maximum) {
                    apiurl = this.options.api.address + 'v3/?id=' + this.options.api.id + '&max=' + this.options.api.maximum;
                } else {
                    apiurl = this.options.api.address + 'v3/?id=' + this.options.api.id;
                }
                var endpoints = (this.options.api.addition || []).slice(0);
                endpoints.push(apiurl);
                this.events && this.events.trigger('danmaku_load_start', endpoints);
                this._readAllEndpoints(endpoints, function (results) {
                    _this.dan = [].concat.apply([], results).sort(function (a, b) {
                        return a.time - b.time;
                    });
                    window.requestAnimationFrame(function () {
                        _this.frame();
                    });
                    _this.options.callback();
                    _this.events && _this.events.trigger('danmaku_load_end');
                });
            }
        },
        {
            key: 'reload',
            value: function reload(newAPI) {
                this.options.api = newAPI;
                this.dan = [];
                this.clear();
                this.load();
            }
        },
        {
            key: '_readAllEndpoints',
            value: function _readAllEndpoints(endpoints, callback) {
                var _this2 = this;
                var results = [];
                var readCount = 0;
                var _loop = function _loop(i) {
                    _this2.options.apiBackend.read({
                        url: endpoints[i],
                        success: function success(data) {
                            results[i] = data;
                            ++readCount;
                            if (readCount === endpoints.length) {
                                callback(results);
                            }
                        },
                        error: function error(msg) {
                            _this2.options.error(msg || _this2.options.tran('Danmaku load failed'));
                            results[i] = [];
                            ++readCount;
                            if (readCount === endpoints.length) {
                                callback(results);
                            }
                        }
                    });
                };
                for (var i = 0; i < endpoints.length; ++i) {
                    _loop(i);
                }
            }
        },
        {
            key: 'send',
            value: function send(dan, callback) {
                var _this3 = this;
                var danmakuData = {
                    token: this.options.api.token,
                    id: this.options.api.id,
                    author: this.options.api.user,
                    time: this.options.time(),
                    text: dan.text,
                    color: dan.color,
                    type: dan.type
                };
                this.options.apiBackend.send({
                    url: this.options.api.address + 'v3/',
                    data: danmakuData,
                    success: callback,
                    error: function error(msg) {
                        _this3.options.error(msg || _this3.options.tran('Danmaku send failed'));
                    }
                });
                this.dan.splice(this.danIndex, 0, danmakuData);
                this.danIndex++;
                var danmaku = {
                    text: this.htmlEncode(danmakuData.text),
                    color: danmakuData.color,
                    type: danmakuData.type,
                    border: '2px solid ' + this.options.borderColor
                };
                this.draw(danmaku);
                this.events && this.events.trigger('danmaku_send', danmakuData);
            }
        },
        {
            key: 'frame',
            value: function frame() {
                var _this4 = this;
                if (this.dan.length && !this.paused && this.showing) {
                    var item = this.dan[this.danIndex];
                    var dan = [];
                    while (item && this.options.time() > parseFloat(item.time)) {
                        dan.push(item);
                        item = this.dan[++this.danIndex];
                    }
                    this.draw(dan);
                }
                window.requestAnimationFrame(function () {
                    _this4.frame();
                });
            }
        },
        {
            key: 'opacity',
            value: function opacity(percentage) {
                if (percentage !== undefined) {
                    var items = this.container.getElementsByClassName('dplayer-danmaku-item');
                    for (var i = 0; i < items.length; i++) {
                        items[i].style.opacity = percentage;
                    }
                    this._opacity = percentage;
                    this.events && this.events.trigger('danmaku_opacity', this._opacity);
                }
                return this._opacity;
            }
        },
        {
            key: 'draw',
            value: function draw(dan) {
                var _this5 = this;
                if (this.showing) {
                    var itemHeight = this.options.height;
                    var danWidth = this.container.offsetWidth;
                    var danHeight = this.container.offsetHeight;
                    var itemY = parseInt(danHeight / itemHeight);
                    var danItemRight = function danItemRight(ele) {
                        var eleWidth = ele.offsetWidth || parseInt(ele.style.width);
                        var eleRight = ele.getBoundingClientRect().right || _this5.container.getBoundingClientRect().right + eleWidth;
                        return _this5.container.getBoundingClientRect().right - eleRight;
                    };
                    var danSpeed = function danSpeed(width) {
                        return (danWidth + width) / 5;
                    };
                    var getTunnel = function getTunnel(ele, type, width) {
                        var tmp = danWidth / danSpeed(width);
                        var _loop2 = function _loop2(i) {
                            var item = _this5.danTunnel[type][i + ''];
                            if (item && item.length) {
                                if (type !== 'right') {
                                    return 'continue';
                                }
                                for (var j = 0; j < item.length; j++) {
                                    var danRight = danItemRight(item[j]) - 10;
                                    if (danRight <= danWidth - tmp * danSpeed(parseInt(item[j].style.width)) || danRight <= 0) {
                                        break;
                                    }
                                    if (j === item.length - 1) {
                                        _this5.danTunnel[type][i + ''].push(ele);
                                        ele.addEventListener('animationend', function () {
                                            _this5.danTunnel[type][i + ''].splice(0, 1);
                                        });
                                        return { v: i % itemY };
                                    }
                                }
                            } else {
                                _this5.danTunnel[type][i + ''] = [ele];
                                ele.addEventListener('animationend', function () {
                                    _this5.danTunnel[type][i + ''].splice(0, 1);
                                });
                                return { v: i % itemY };
                            }
                        };
                        for (var i = 0; _this5.unlimited || i < itemY; i++) {
                            var _ret2 = _loop2(i);
                            switch (_ret2) {
                            case 'continue':
                                continue;
                            default:
                                if ((typeof _ret2 === 'undefined' ? 'undefined' : _typeof(_ret2)) === 'object')
                                    return _ret2.v;
                            }
                        }
                        return -1;
                    };
                    if (Object.prototype.toString.call(dan) !== '[object Array]') {
                        dan = [dan];
                    }
                    var docFragment = document.createDocumentFragment();
                    var _loop3 = function _loop3(i) {
                        dan[i].type = _utils2.default.number2Type(dan[i].type);
                        if (!dan[i].color) {
                            dan[i].color = 16777215;
                        }
                        var item = document.createElement('div');
                        item.classList.add('dplayer-danmaku-item');
                        item.classList.add('dplayer-danmaku-' + dan[i].type);
                        if (dan[i].border) {
                            item.innerHTML = '<span style="border:' + dan[i].border + '">' + dan[i].text + '</span>';
                        } else {
                            item.innerHTML = dan[i].text;
                        }
                        item.style.opacity = _this5._opacity;
                        item.style.color = _utils2.default.number2Color(dan[i].color);
                        item.addEventListener('animationend', function () {
                            _this5.container.removeChild(item);
                        });
                        var itemWidth = _this5._measure(dan[i].text);
                        var tunnel = void 0;
                        switch (dan[i].type) {
                        case 'right':
                            tunnel = getTunnel(item, dan[i].type, itemWidth);
                            if (tunnel >= 0) {
                                item.style.width = itemWidth + 1 + 'px';
                                item.style.top = itemHeight * tunnel + 'px';
                                item.style.transform = 'translateX(-' + danWidth + 'px)';
                            }
                            break;
                        case 'top':
                            tunnel = getTunnel(item, dan[i].type);
                            if (tunnel >= 0) {
                                item.style.top = itemHeight * tunnel + 'px';
                            }
                            break;
                        case 'bottom':
                            tunnel = getTunnel(item, dan[i].type);
                            if (tunnel >= 0) {
                                item.style.bottom = itemHeight * tunnel + 'px';
                            }
                            break;
                        default:
                            console.error('Can\'t handled danmaku type: ' + dan[i].type);
                        }
                        if (tunnel >= 0) {
                            item.classList.add('dplayer-danmaku-move');
                            docFragment.appendChild(item);
                        }
                    };
                    for (var i = 0; i < dan.length; i++) {
                        _loop3(i);
                    }
                    this.container.appendChild(docFragment);
                    return docFragment;
                }
            }
        },
        {
            key: 'play',
            value: function play() {
                this.paused = false;
            }
        },
        {
            key: 'pause',
            value: function pause() {
                this.paused = true;
            }
        },
        {
            key: '_measure',
            value: function _measure(text) {
                if (!this.context) {
                    var measureStyle = getComputedStyle(this.container.getElementsByClassName('dplayer-danmaku-item')[0], null);
                    this.context = document.createElement('canvas').getContext('2d');
                    this.context.font = measureStyle.getPropertyValue('font');
                }
                return this.context.measureText(text).width;
            }
        },
        {
            key: 'seek',
            value: function seek() {
                this.clear();
                for (var i = 0; i < this.dan.length; i++) {
                    if (this.dan[i].time >= this.options.time()) {
                        this.danIndex = i;
                        break;
                    }
                    this.danIndex = this.dan.length;
                }
            }
        },
        {
            key: 'clear',
            value: function clear() {
                this.danTunnel = {
                    right: {},
                    top: {},
                    bottom: {}
                };
                this.danIndex = 0;
                this.options.container.innerHTML = '';
                this.events && this.events.trigger('danmaku_clear');
            }
        },
        {
            key: 'htmlEncode',
            value: function htmlEncode(str) {
                return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;').replace(/\//g, '&#x2f;');
            }
        },
        {
            key: 'resize',
            value: function resize() {
                var danWidth = this.container.offsetWidth;
                var items = this.container.getElementsByClassName('dplayer-danmaku-item');
                for (var i = 0; i < items.length; i++) {
                    items[i].style.transform = 'translateX(-' + danWidth + 'px)';
                }
            }
        },
        {
            key: 'hide',
            value: function hide() {
                this.showing = false;
                this.pause();
                this.clear();
                this.events && this.events.trigger('danmaku_hide');
            }
        },
        {
            key: 'show',
            value: function show() {
                this.seek();
                this.showing = true;
                this.play();
                this.events && this.events.trigger('danmaku_show');
            }
        },
        {
            key: 'unlimit',
            value: function unlimit(boolean) {
                this.unlimited = boolean;
            }
        }
    ]);
    return Danmaku;
}();
exports.default = Danmaku;