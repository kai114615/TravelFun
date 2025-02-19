/*!
 * Responsive 2.5.0
 * 2014-2023 SpryMedia Ltd - datatables.net/license
 */
(function(factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD
        define(['jquery', 'datatables.net'], function($) {
            return factory($, window, document);
        });
    }
    else if (typeof exports === 'object') {
        // CommonJS
        var jq = require('jquery');
        var cjsRequires = function(root, $) {
            if (!$.fn.dataTable) {
                require('datatables.net')(root, $);
            }
        };

        if (typeof window === 'undefined') {
            module.exports = function(root, $) {
                if (!root) {
                    root = window;
                }
                if (!$) {
                    $ = jq;
                }
                cjsRequires(root, $);
                return factory($, root, root.document);
            };
        }
        else {
            cjsRequires(window, jq);
            module.exports = factory(jq, window, window.document);
        }
    }
    else {
        // Browser
        factory(jQuery, window, document);
    }
}(function($, window, document) {
    'use strict';
    var DataTable = $.fn.dataTable;
    var Responsive = function(settings, opts) {
        if (!DataTable.versionCheck || !DataTable.versionCheck('1.10.10')) {
            throw 'DataTables Responsive requires DataTables 1.10.10 or newer';
        }
        this.s = {
            dt: new DataTable.Api(settings),
            columns: [],
            current: []
        };
        if (this.s.dt.settings()[0].responsive) {
            return;
        }
        if (opts && typeof opts.details === 'string') {
            opts.details = {type: opts.details};
        }
        this.c = $.extend(true, {}, Responsive.defaults, DataTable.defaults.responsive, opts);
        settings.responsive = this;
        this._constructor();
    };
    // ... 更多代碼 ...
})); 