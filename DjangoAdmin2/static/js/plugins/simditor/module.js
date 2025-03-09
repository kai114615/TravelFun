(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module.
    define('simple-module', ['jquery'], ($) => {
      return (root.returnExportsGlobal = factory($));
    })
  } else if (typeof exports === 'object') {
    // Node. Does not work with strict CommonJS, but
    // only CommonJS-like enviroments that support module.exports,
    // like Node.
    module.exports = factory(require('jquery'));
  } else {
    root.SimpleModule = factory(jQuery);
  }
}(this, ($) => {
  let Module
  const __slice = [].slice

  Module = (function () {
    Module.extend = function (obj) {
      let key, val, _ref;
      if (!((obj != null) && typeof obj === 'object')) {
        return
      }
      for (key in obj) {
        val = obj[key];
        if (key !== 'included' && key !== 'extended') {
          this[key] = val;
        }
      }
      return (_ref = obj.extended) != null ? _ref.call(this) : void 0;
    };

    Module.include = function (obj) {
      let key, val, _ref;
      if (!((obj != null) && typeof obj === 'object')) {
        return
      }
      for (key in obj) {
        val = obj[key];
        if (key !== 'included' && key !== 'extended') {
          this.prototype[key] = val;
        }
      }
      return (_ref = obj.included) != null ? _ref.call(this) : void 0;
    };

    Module.connect = function (cls) {
      if (typeof cls !== 'function') {
        return
      }
      if (!cls.pluginName) {
        throw new Error('Module.connect: cannot connect plugin without pluginName');
        return;
      }
      cls.prototype._connected = true;
      if (!this._connectedClasses) {
        this._connectedClasses = [];
      }
      this._connectedClasses.push(cls);
      if (cls.pluginName) {
        return this[cls.pluginName] = cls;
      }
    }

    Module.prototype.opts = {};

    function Module(opts) {
      let cls, instance, instances, name, _base, _i, _len;
      this.opts = $.extend({}, this.opts, opts);
      (_base = this.constructor)._connectedClasses || (_base._connectedClasses = []);
      instances = (function () {
        let _i, _len, _ref, _results;
        _ref = this.constructor._connectedClasses;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          cls = _ref[_i];
          name = cls.pluginName.charAt(0).toLowerCase() + cls.pluginName.slice(1);
          if (cls.prototype._connected) {
            cls.prototype._module = this;
          }
          _results.push(this[name] = new cls());
        }
        return _results;
      }.call(this))
      if (this._connected) {
        this.opts = $.extend({}, this.opts, this._module.opts);
      } else {
        this._init();
        for (_i = 0, _len = instances.length; _i < _len; _i++) {
          instance = instances[_i];
          if (typeof instance._init === 'function') {
            instance._init();
          }
        }
      }
      this.trigger('initialized');
    }

    Module.prototype._init = function () {};

    Module.prototype.on = function () {
      let args, _ref;
      args = arguments.length >= 1 ? __slice.call(arguments, 0) : [];
      (_ref = $(this)).on.apply(_ref, args);
      return this;
    };

    Module.prototype.one = function () {
      let args, _ref;
      args = arguments.length >= 1 ? __slice.call(arguments, 0) : [];
      (_ref = $(this)).one.apply(_ref, args);
      return this;
    };

    Module.prototype.off = function () {
      let args, _ref;
      args = arguments.length >= 1 ? __slice.call(arguments, 0) : [];
      (_ref = $(this)).off.apply(_ref, args);
      return this;
    };

    Module.prototype.trigger = function () {
      let args, _ref;
      args = arguments.length >= 1 ? __slice.call(arguments, 0) : [];
      (_ref = $(this)).trigger.apply(_ref, args);
      return this;
    };

    Module.prototype.triggerHandler = function () {
      let args, _ref;
      args = arguments.length >= 1 ? __slice.call(arguments, 0) : [];
      return (_ref = $(this)).triggerHandler.apply(_ref, args);
    };

    Module.prototype._t = function () {
      let args, _ref;
      args = arguments.length >= 1 ? __slice.call(arguments, 0) : [];
      return (_ref = this.constructor)._t.apply(_ref, args);
    };

    Module._t = function () {
      let args, key, result, _ref;
      key = arguments[0], args = arguments.length >= 2 ? __slice.call(arguments, 1) : [];
      result = ((_ref = this.i18n[this.locale]) != null ? _ref[key] : void 0) || '';
      if (!(args.length > 0)) {
        return result;
      }
      result = result.replace(/([^%]|^)%(?:(\d+)\$)?s/g, (p0, p, position) => {
        if (position) {
          return p + args[Number.parseInt(position) - 1];
        } else {
          return p + args.shift();
        }
      });
      return result.replace(/%%s/g, '%s');
    };

    Module.i18n = {
      'zh-CN': {}
    }

    Module.locale = 'zh-CN';

    return Module;

  })();

  return Module;

}));
