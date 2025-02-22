// ------------------------------
//	 Dialog plugin for jQuery
//   Author : LooseLive@gmail.com
// ------------------------------
(function ($) {
  const WIN = $(window);
  const DOC = $(document);
  const zIndex = ZINDEX = 2;
  const F = $.isFunction;
  const CSS = {
    HASICON: 'HasIcon',
    TIMER: 'HasTimer',
    CURRENT: 'Current',
    LOADING: 'Loading',
    DISABLED: 'Disabled',
    NOTONTOP: 'NotOnTop',
    ENTCLICK: 'ENTCLICK'
  }
  const SPACE = ' ';
  const EVENT = {
    A:	'mousedown',
    B: 'click',
    C: 'keydown',
    D: 'resize',
    E: 'scroll'
  }
  // 从对象中删除该实例，如果对象的实例被删空，重置ZINDEX，避免无限上增
  const DELETE = function (id) {
    delete $.dialog.list[id]
    if ($.isEmptyObject($.dialog.list))
    {
      ZINDEX = zIndex
    }
  }
  function toArray() {
    const a = arguments;
    let A = []
    let i = 0;
    for (; i < a.length; i++)
    {
      if (Array.isArray(a[i]))
      {
        A = $.merge(A, a[i]);
      }
      else if (a[i] != null)
      {
        A.push(a[i]);
      }
    }
    return A;
  }
  $.dialog = function (o) {
    return new $.dialog.fn._init(o);
  };
  $.dialog.list = {};
  // 默认设置
  $.dialog.defaults = {
    // 对话框的唯一标识符，用途：无论何时何地都可通过$.dialog.get('xxx')获取对话框对象。
    id: null,
    // 对话框的标识触发器，用途：防止重复弹出，缓存数据。
    trigger: null,
    /*
		[图标] - int | string
			成功：0 | success
			警告：1 | warning
			错误：2 | error,
			异常：3 | exception
			询问：4 | question
		*/
    icon: null,
    // [标题]
    title: '信息提示',
    // [选项卡] - array
    tab: null,
    /*
		[
			{
				text : string - 选项卡名称,
				content : {icon:独立的图标}跟全局content格式一致,
				button : 跟全局button格式一致,
				active : 是否激活该tab，注意：同时只能激活一个tab，如果定义多个active=true，以最后一个为准
				onActive : 当激活该tab时的事件处理函数
				icon:
			}
		],
		tab的全局触发方式（鼠标事件名称）
		*/
    tabType: 'click',
    /*

		[对话框的内容] - object */
    content: null,
    /*
		{
					//load : {
						url:String,
						[data] : {},
						[success]:Function,
						[error]:Function
					}
					||
					load:string

					//text : string
					//selector : string(选择器表达式) | jquery(元素)
					//iframe : string(框架Url)
					ajax : {url:'bb'}//跟jquery的ajax参数格式一致
		},
		//[按钮] - array
		*/
    button:
		[
		  {
		    text: '确认'
		    /*
				,callback : function - 处理函数,
				cls : string-自定义样式名称,
				url : string,
				disabled : Boolean,
				bindEnter : Boolean
				*/
		  }
		],
    padding: '8px',
    width: null, // string||number - pixels
    height: null, // string||number - pixels
    // 位置参照元素
    refer: null, // jquery||HTMLElement||string(jQuery selector)
    offset: {
      top: 'middel',
      /*
				可使用值枚举:
				字符('top'||'middel'||'bottom'||'xpx'||'%50')
				数字(表示多少像素，与字符值'xpx'同等效果)
			*/
      left: 'center'
      /*
				可使用值枚举:
				字符('left'||'center'||'right'||'80px'||'%60')
				数字(表示多少像素，与字符值'xpx'同等效果)
			, */
    },
    // 是否固定位置
    fixed: true,
    // 遮罩层
    mask: {
      enabled: false,	// 是否启用
      color: '#999',	// 颜色
      opacity: 0.8, // 透明度
      duration: 200 // 透明度渐变动画的速度
    },
    draggable: true, // 是否可拖动
    resizable: false, // 是否可调整自身大小
    timeout: { second: 0, text: 's% 秒后将自动关闭' },
    esc: true, // 是否允许用户按 Esc 键关闭对话框
    onLoad: $.noop,
    onClose: $.noop,
    onEnter: $.noop,
    err: {
      title: 'Error',
      content: '<p style="text-align:center">服务器繁忙或发生错误，请稍后再试！<br />The server is busy or unavailable, please try again later!</p>',
      button: 'Close'
    },
    showErr: true // 内容加载失败时是否显示错误消息
  }
  // 修改全局默认设置的方法
  $.dialog.setup = function (o) {
    $.extend(this.defaults, o);
  };
  $.dialog.get = function (id) {
    return $.dialog.list[id];
  };
  // 关闭所有对话框，参数o-布尔值，是否静默关闭
  $.dialog.close = function (o) {
    for (const i in $.dialog.list) {
      $.dialog.list[i].close(o);
    };
  }
  $.dialog.fn = $.dialog.prototype = {
    version: '1.0.0',
    title (v, d) {
      d = this.dom().title
      // 如果未传入参数，则返回当前标题字符
      if (v === undefined) return d.text()
      if (v === null)v = '';
      d.text(v)
      return this
    },
    tab (o) {
      const e = this
      const d = e.dom()
      const x = d.title;
      if (o === false)
      {
        x.siblings().remove()
      }
      else
      {
        const v = toArray(o);
        if (v.length > 0)
        {
          let i = 0;
          let t = $();
          let n = -1
          for (; i < v.length; i++)
          {
            var m = v[i].type ? v[i].type : e.o.tabType;
            const j = $('<a href="javascript:void(0)" hidefocus="true"></a>').data('_m', m);
            if (v[i].icon)
            {
              j.wrapInner(`<b class="${v[i].icon}">${v[i].text}</b>`);
            }
            else
            {
              j.text(v[i].text)
            }
            j.bind(m + SPACE + EVENT.A, { i }, function (p) {
              if (e.child != null) return
              // 避免对话框可拖动时点击tab所带来的反应
              if (p.type == EVENT.A) return false
              const o = v[p.data.i]
              const b = toArray(o.button !== undefined ? o.button : [], e.o.button)
              const c = o.content;
              // 激活tab事件处理
              if (F(o.onActive))
              {
                if (o.onActive.call(e) == false) return false
              }
              // 切换tab的样式
              $(this).addClass(CSS.CURRENT).siblings().removeClass(CSS.CURRENT)
              // 预清空隐藏按纽栏
              d.button.empty().parent().hide()
              if (c)
              {
                if (typeof c === 'string' && (c.indexOf('#') === 0 || c.indexOf('.') === 0))
                {
                  const w = d.content
                  let z = w.find(c)
                  if (!z[0])
                  {
                    const y = w.data('c');
                    z = $(y).find(c)
                    if (z[0]) w.html(y)
                  }
                  if (z[0])
                  {
                    z.siblings().hide()
                    z.fadeIn('fast')
                    e._ready(b, 1)
                  }
                  else
                  {
                    e._showErr()
                  }
                }
                else
                {
                  e.content(c, b)
                  // 独立的图标处理
                  e.icon(c.icon || e.o.icon)
                }
              }
              else
              {
                e.button(b)
              }
            })
            if (v[i].active === true) n = i
            t = t.add(j)
          }
          x.siblings().remove()
          x.parent().append(t)
          // 如果有需要激活的tab
          if (n > -1)
          {
            const a = t.eq(n);
            if (e._isReady)
            {
              var m = a.data('_m')
              a.triggerHandler(m)
            }
            else
            {
              a.attr('data-active', 1)
            }
          }
        }
      }
      return e
    },
    icon (v) {
      const d = this.dom()
      const b = d.body
      const c = d.icon;
      // 如果未传入参数，则返回图标容器元素
      if (v === undefined) return d
      if (v !== null)
      {
        if (!isNaN(v))
        {
          switch (v)
          {
            case 0: v = 'Success'; break
            case 1: v = 'Warning'; break
            case 2: v = 'Error'; break
            case 3: v = 'Exception'; break
            case 4: v = 'Question'; break
            default : v = null
          }
        }
        b.addClass(CSS.HASICON)
        if (v) c.removeClass().addClass(v).parent().show()
      }
      else
      {
        b.removeClass(CSS.HASICON)
        c.removeClass().parent().hide()
      }
      return this
    },
    content (o, b) {
      const e = this
      const z = b ? 1 : 0
      const c = e.dom().content;
      if (o === undefined) return c
      if (o === null)
      {
        e._ready()
        return e
      }
      if (typeof o === 'string')
      {
        o = { text: o };
      }
      else if (!$.isPlainObject(o))
      {
        o = { selector: o };
      }
      b = b || e.o.button;
      c.empty().addClass(CSS.LOADING)
      $.each(o, (t, v) => {
        switch (t.toLowerCase())
        {
          case 'load' :
            if (typeof v === 'string') v = { url: v };
            c.load(v.url, v.data, (x, y) => {
              if (y === 'success')
              {
                c.removeClass(CSS.LOADING)
                e._ready(b, z)
                if (v.success) v.success.call(e)
              }
              else
              {
                e._showErr()
                if (v.error) v.error.call(e)
              }
            })
            break
          case 'text' :
            c.removeClass(CSS.LOADING).html(v)
            e._ready(b, z)
            break
          case 'selector' :
            // 使用API方式设置内容时如果有需要恢复到原始位置的元素，将其恢复
            e.recovery && e.recovery()
            // 如果是选择器字符或HTMLElement，将其转换为jQuery对象
            if (typeof v === 'string' || v.nodeType === 1) v = $(v)
            if (v[0])
            {
              // -->恢复处理函数
              const display = v[0].style.display
              const prev = v.prev()
              const next = v.next()
              const parent = v.parent();
              e.recovery = function () {
                if (prev[0]) {
                  prev.after(v)
                } else if (next[0]) {
                  next.before(v)
                } else if (parent[0]) {
                  parent.append(v)
                };
                v[0].style.display = display
                e.recovery = null
              }
              // <--
              c.removeClass(CSS.LOADING).append(v.show())
              e._ready(b, z)
            }
            else
            {
              e._showErr()
            }
            break;
          case 'iframe' :
            var iframe = $(`<iframe src="${v}" width="100%" height="100%" scrolling="auto" frameborder="0" marginheight="0" marginwidth="0"></iframe>`);
            c.removeClass(CSS.LOADING).html(iframe)
            iframe.bind('load', function () {
              const i = $(this)
              const d = i[0].contentWindow.document
              const w = Math.max(d.body.scrollWidth, d.documentElement.scrollWidth)
              const h = i.contents().find('body').height();
              if (!e._w) i.width(w)
              if (!e._h) i.height(h)
            });
            e._ready(b, z)
            break
          case 'ajax' :
            v.type = v.type || 'get'
            $.ajax({
              url: v.url,
              type: v.type,
              data: v.data,
              dataType: 'html',
              success(html) {
                c.removeClass(CSS.LOADING).html(html);
                e._ready(b, z);
                if (F(v.success)) v.success.call(e);
              },
              error() {
                if (v.error) v.error.call(e);
                e._showErr();
              }
            })
            break
        }
      })
      return e
    },
    button (o) {
      const e = this; const a = toArray(o); const b = e.dom().button; let i = 0
      b.empty().parent().hide()
      for (; i < a.length; i++)
      {
        const c = $(`<a href="javascript:void(0)" hidefocus="true" data-id="${a[i].text}">${a[i].text}</a>`).bind(EVENT.B, { e, f: a[i].callback }, F(a[i].callback)
          ? function (e, d) {
            if (e.data.e.child != null) return;
            if ($(this).hasClass(CSS.DISABLED))
            {
              return false;
            }
            else
            {
              d = e.data;
              return d.f.call(d.e);
            }
          }
          : $.proxy(e.close, e));
        if (typeof a[i].cls === 'string') c.addClass(a[i].cls)
        if (typeof a[i].url === 'string') c[0].href = a[i].url
        if (a[i].disabled === true) c.addClass(CSS.DISABLED)
        if (a[i].bindEnter) c.addClass(CSS.ENTCLICK)
        b.append(c)
      }
      if (i > 0) b.parent().show()
      return e
    },
    // 改变按钮状态和文本，n-按钮的索引，o-字符或布尔值或纯粹的对象{disabled:Boolean,text:String}
    buttonChange (n, o) {
      const b = this.dom().button;
      d = b.children(`[data-id="${n}"]`);
      if (d.size() === 0) d = b.children().eq(n)
      let disabled = null
      let text = null
      if (typeof o == 'object')
      {
        disabled = o.disabled
        text = o.text
      }
      else
      {
        if (typeof o == 'boolean')
        {
          disabled = o
        }
        else if (typeof o == 'string')
        {
          text = o
        }
      }
      if (disabled !== null)
      {
        if (disabled)
        {
          d.addClass(CSS.DISABLED)
        }
        else
        {
          d.removeClass(CSS.DISABLED)
        }
      }
      if (text !== null)
      {
        d.text(text)
      }
      return this
    },
    padding (v) {
      if (v)
      {
        const c = this.dom().content;
        if (!c.children('iframe')[0])
        {
          c.css('padding', v)
        }
      }
      return this
    },
    width (v) {
      const e = this;
      if (v)
      {
        e.wrapper.width(v)
        e._w = 1
        return e
      }
      if (v === null) return e
      return e.wrapper.width()
    },
    // 设置对话框的高度，如果参数没有明确指定单位（如：em或%），使用px。如果不带参数，返回当前对话框的高度
    height (v) {
      const e = this;
      if (v)
      {
        e.wrapper.height(v)
        e._h = 1
        return e
      }
      if (v === null) return e
      return e.wrapper.height()
    },
    offset (o) {
      const e = this;
      if (o === undefined) return e.lastOffset || e.o.offset
      const refer	= e.o.refer
      const windowW = WIN.width()
      const windowH = WIN.height()
      const width	= e.wrapper.outerWidth()
      const height	= e.wrapper.outerHeight()
      const offset	= { top: Number.parseInt((windowH - height) / 2), left: Number.parseInt((windowW - width) / 2) };
      let set = true
      if (offset.top <= 0) offset.top = 0
      if (offset.left <= 0) offset.left = 0
      if (refer)
      {
        const visibleT = DOC.scrollTop()
        const visibleL = DOC.scrollLeft()
        const visibleB = visibleT + windowH
        const visibleR = visibleL + windowW
        let referW = refer.outerWidth();
        let referH = refer.outerHeight();
        const referOffset = refer.offset()
        let referT = referOffset.top;
        let referL = referOffset.left;
        const referB = referT + referH
        const referR = referL + referW
        let invisibleW = 0;
        let invisibleH = 0;
        const inViewableArea = referT < visibleB && referB > visibleT && referR > visibleL && referL < visibleR;
        if (inViewableArea)
        {
          if (referL < visibleL)
          {
            invisibleW = visibleL - referL
            referL = referL + invisibleW
          }
          else if (referR > visibleR)
          {
            invisibleW = referR - visibleR
          }
          if (referT < visibleT)
          {
            invisibleH = visibleT - referT
            referT = referT + invisibleH
          }
          else if (referB > visibleB)
          {
            invisibleH = referB - visibleB
          }
          referW = referW - invisibleW,
          referH = referH - invisibleH
          o = {
            top: referT + ((referH - height) / 2),
            left: referL + ((referW - width) / 2)
          };
          if (o.top < visibleT)
          {
            o.top = visibleT
          }
          else if (o.top + height > visibleB)
          {
            o.top = visibleB - height
          }
          if (o.left < visibleL)
          {
            o.left = visibleL
          }
          else if (o.left + width > visibleR)
          {
            o.left = visibleR - width
          }
          e.fixed(false).draggable(false)
        }
        else
        {
          e.fixed(false).draggable(e.o.draggable)
          set = false
        }
      }
      $.each(o, (n, val) => {
        if ((typeof val === 'string' && (val.includes('%') || Number.parseInt(val) > 0)) || typeof val === 'number')
        {
          offset[n] = val
        }
        else
        {
          switch (val)
          {
            case 'left' : offset[n] = 0; break
            case 'right'	: offset[n] = windowW - width; break;
            case 'top' : offset[n] = 0; break;
            case 'bottom'	: offset[n] = windowH - height; break;
          }
        }
      })
      if (set)
      {
        e.wrapper.css({
          top: offset.top,
          left: offset.left
        })
        e.lastOffset = offset
      }
      return e
    },
    // 开启或关闭固定定位。参数为false时为关闭，不带参数或参数值为非false时为开启
    fixed (v) {
      if (v === false)
      {
        this.wrapper.css('position', 'absolute')
      }
      else
      {
        this.wrapper.css('position', 'fixed')
      }
      return this
    },
    // 开启或关闭遮罩层。参数为false时为关闭，不带参数或参数值为非false时为开启
    mask (o) {
      const e = this; const t = o;
      // 使用.mask(null)方法关闭遮罩层
      if ((o === false || o === null) && e.MaskLayer != null)
      {
        e.MaskLayer.remove()
        e.MaskLayer = null
        e._mask = 0
      }
      o = o === true ? $.extend({}, $.dialog.defaults.mask, { enabled: true }) : $.extend({}, e.o.mask, o)
      if (t === undefined || o.enabled)
      {
        if (e.MaskLayer === null)
        {
          let a, b;
          if (e.zIndex === ZINDEX - 1)
          {
            a = e.zIndex
            b = e.zIndex = ZINDEX++
          }
          else
          {
            a = ZINDEX++
            b = e.zIndex = ZINDEX++
          }
          e.MaskLayer = $('<p class="jQ_Dialog_MaskLayer"></p>').css({
            backgroundColor: o.color,
            opacity: 0,
            zIndex: a,
            height: '100%',
            width: '100%',
            left: 0,
            top: 0
          })
          $('body').append(e.MaskLayer)
          e.wrapper.css('zIndex', b)
          e._mask = 1
          e._setTop()
        }
        if (e.zIndex < ZINDEX - 1)
        {
          e.MaskLayer.css('zIndex', ZINDEX++)
          e.wrapper.css('zIndex', ZINDEX)
          e.zIndex = ZINDEX
          ZINDEX++;
          e._mask = 1
          e._setTop()
        }
        if (e._closed)
        {
          e.wrapper.show()
          e._closed = 0
        }
        e.MaskLayer.show().animate({ opacity: o.opacity }, o.duration)
      }
      else if (e.MaskLayer != undefined)
      {
        e.MaskLayer.remove()
        e.MaskLayer = null
        e._mask = 0
      }
      return e
    },
    // 开启或关闭拖动。参数为false时为关闭，不带参数或参数值为非false时为开启
    draggable (v) {
      const e = this
      const w = e.wrapper
      const d = e.dom().drag;
      if (v === false)
      {
        w.unDrag()
      }
      else
      {
        w.Drag(d)
      }
      return e
    },
    // 开启或关闭大小缩放。参数为false时为关闭，不带参数或参数值为非false时为开启
    resizable (v) {
      const e = this
      const c = e.dom().content
      const r = e.dom().resizer;
      if (v === false)
      {
        r.hide()
      }
      else
      {
        r.show()
        c.resize({ handler: r, wrapper: e.wrapper })
      }
      return e
    },
    // 倒计时关闭
    timeout (s, t) {
      const e = this
      const o = e.o.timeout
      let second; let text;
      const d = e.dom().foot
      const f = function () {
        if (text)
        {
          text = text.replace('s%', '<b>s%</b>');
          d.addClass(CSS.TIMER).eq(1).html(text.replace('s%', second));
        }
        if (!second) e.close();
        second--
      };
      if (typeof s === 'object')
      {
        second = s.second || o.second
        text = s.text || o.text
      }
      else
      {
        second = s || o.second
        text = t || o.text
      }
      d.removeClass(CSS.TIMER).eq(1).empty()
      clearInterval(e.timer)
      if (second)
      {
        e.timer = setInterval(f, 1000)
        f()
      }
      return e
    },
    // 是否开启Esc键关闭
    esc (v) {
      this.o.esc = v
      return this
    },
    onLoad (f) {
      if (F(f)) this.o.onLoad = f
      return this
    },
    onClose (f) {
      if (F(f)) this.o.onClose = f
      return this
    },
    onEnter (f) {
      if (F(f)) this.o.onEnter = f
      return this
    },
    show () {
      this.wrapper.show()
      return this.__init()
    },
    close (x) {
      const e = this;
      if (e.child != null)
      {
        // 忽略鼠标关闭事件
        if (typeof x === 'object')
        {
          return e
        }
        else
        {
          // 手动模式关闭-静默关闭
          x = true
        }
      }
      if (e._closed) return e
      // 避免对话框可拖动时点击x所带来的反应
      if (typeof x === 'object' && x.type === EVENT.A) return false
      const junior = e.junior();
      // 静默关闭
      if (x === true)
      {
        // 从本窗口的最终子窗口开始关闭
        const c = function (o) {
          o._close();
          if (o.hasOwnProperty('parent') && e != o) arguments.callee(o.parent);
          // 从对象组中删除该实例
          DELETE(o.id);
        }
        c(junior)
        return e
      }
      // 如果关闭回调函数返回false
      if (e.o.onClose.call(e) === false) return e
      // 如果有触发器
      if (e.o.trigger)
      {
        e._close(true)		// 隐藏
      }
      else
      {
        e._close()			// 移除
        DELETE(e.id)		// 从对象组中删除该实例
      }
      return e
    },
    // 获取当前对象的最最终子对象
    junior () {
      if (this.child != null) return this.child.junior()
      return this
    },
    // 创建子窗口的扩展方法
    dialog (o) {
      $.extend(o, { refer: this.wrapper })
      const e = this.child = $.dialog(o);
      e.parent = this
      return e
    },
    // 左右晃动的效果
    shake () {
      const e = this
      const p = [4, 8, 4, 0, -4, -8, -4, 0, 2, 4, 2, 0, -2, -4, -2, 0, 1, 2, 1, 0, -1, -2, -1, 0]
      let t = null;
      const f = function () {
        e.wrapper.css('marginLeft', `${p.shift()}px`)
        if (p.length <= 0) {
          e.wrapper.css('marginLeft', 0);
          clearInterval(t);
        };
      };
      t = setInterval(f, 12)
      return e
    },
    __init () {
      const e = this
      const o = e.o;
      e.title(o.title)
        .tab(o.tab)
        .icon(o.icon)
        .content(o.content)
        .padding(o.padding)
        .width(o.width)
        .height(o.height)
        .offset(o.offset)
        .fixed(o.fixed)
        .mask(o.mask)
        .draggable(o.draggable)
        .resizable(o.resizable)
        .timeout(o.timeout)
        .esc(o.esc)
        .onLoad(o.onLoad)
        .onEnter(o.onEnter)
        .onClose(o.onClose)
        ._event()
      e._closed = 0
      return e
    },
    // 初始化一个对话框实例
    _init (o) {
      const e = this
      let exists = false
      e.o = {}
      e.wrapper = e.child = e.MaskLayer = null
      e.id = `_dialog${ZINDEX}`;
      e.dom = function () {
        const w = this.wrapper
        const d = {
          drag: w.children('thead'),
          title: w.find('.jQ_Dialog_Title span'),
          body: w.find('.jQ_Dialog_Body'),
          icon: w.find('.jQ_Dialog_Icon p'),
          content: w.find('.jQ_Dialog_Content'),
          button: w.find('.jQ_Dialog_Button td'),
          X: w.find('.jQ_Dialog_X').children(),
          resizer: w.find('.jQ_Dialog_Resizer'),
          foot: w.find('tfoot td')
        };
        return d
      }
      $.extend(true, e.o, $.dialog.defaults, o)		// 扩展默认设置的副本
      if (typeof e.o.id === 'string') // 如果设置了对话框的唯一标识且为字符
      {
        e.id = e.o.id
        if (e.o.trigger === null) e.o.trigger = e.id
      }
      if ($.type(e.o.trigger) === 'object' && !e.o.trigger.nodeType)
      {
        // 如果是jQuery对象，将其转换为HTMLElement
        e.o.trigger = e.o.trigger[0]
      }
      // 遍历所有对话框对象，通过其触发器检测对象是否已经存在
      $.each($.dialog.list, (x, y) => {
        if (y.o.trigger != null && y.o.trigger === e.o.trigger)
        {
          y.o = e.o
          e.wrapper = y.wrapper
          e.MaskLayer = y.MaskLayer
          y._isReady = y._onLoadCalled = e._w = e._h = 0
          y.show()
          if (y._mask !== 1 && y.zIndex < ZINDEX - 1)
          {
            y.wrapper.css('zIndex', ZINDEX)
            y.zIndex = ZINDEX++
            y._setTop()
          }
          exists = true
          return false
        }
      })
      // 如果对话框对象不存在
      if (!exists)
      {
        e.wrapper = $($.dialog.template)
        $('body').append(e.wrapper)
        // 将其加入全局对话框对象
        $.dialog.list[e.id] = e
        e.__init()
        if (e._mask !== 1)
        {
          e.wrapper.css('zIndex', ZINDEX)
          e.zIndex = ZINDEX++
          e._setTop()
        }
      }
      return e
    },
    _ready (b, z) {
      const e = this;
      if (!e._isReady)
      {
        const d = e.dom()
        const a = d.title.siblings('[data-active]')
        const c = d.content
        const t = a.data('_m');
        if (a.size() > 0)
        {
          a.removeAttr('data-active').triggerHandler(t)
          return
        }
        c.data('c', c.html())
        e._isReady = 1
        e.button(b)
        setTimeout(() => {
          e.offset(1)
        }, 5)
        if (!e._onLoadCalled)
        {
          setTimeout(() => {
            e.o.onLoad.call(e)
          }, 8)
          e._onLoadCalled = 1
        }
      }
      else if (z)
      {
        e.button(b)
      }
    },
    _close (hide) {
      const e = this;
      e.recovery && e.recovery()
      if (hide == true)
      {
        e.wrapper.hide()
      }
      else
      {
        e.wrapper.remove()
        if (e.zIndex === ZINDEX - 1) ZINDEX--
      }
      if (e.MaskLayer != null)
      {
        e.MaskLayer.animate({ opacity: 0 }, e.o.mask.duration, function () {
          if (hide == true)
          {
            $(this).hide()
          }
          else
          {
            $(this).remove()
            if (e.zIndex === ZINDEX) ZINDEX--
            e.MaskLayer = null
          }
        })
      }
      e._closed = 1
      e._isReady = 0
      e._onLoadCalled = 0
      // 如果有父窗口，将父窗口的子窗口赋值为null
      if (e.hasOwnProperty('parent')) e.parent.child = null
      clearInterval(e.timer)
      // 关闭对话框后取消绑定ESC和回车事件
      DOC.unbind(e._eventName(EVENT.C))
      WIN.unbind(e._eventName(EVENT.D, EVENT.E))
      // 自动激活最顶层的对象
      let i = 0;
      let o = e
      $.each($.dialog.list, (x, y) => {
        if (e.zIndex > y.zIndex)
        {
          if (i === 0)
          {
            i = y.zIndex
            o = y
          }
          else if (y.zIndex > i)
          {
            i = y.zIndex
            o = y
          }
        }
      })
      o._setTop()
    },
    _event () {
      const e = this
      const a = e._eventName(EVENT.A, EVENT.B)
      const c = e._eventName(EVENT.D, EVENT.E)
      const b = e._eventName(EVENT.C);
      // 置顶事件
      e.wrapper.unbind(EVENT.A).bind(EVENT.A, $.proxy(function () {
        if (this.child != null)
        {
          this.child.shake()
          return false
        }
        if (ZINDEX - this.zIndex >= 2)
        {
          this.zIndex = ZINDEX
          $.dialog.list[this.id].wrapper.css('z-index', ZINDEX)
          ZINDEX++;
          this._setTop()
        }
      }, e))
      // 关闭按钮事件
      e.dom().X.unbind(a).bind(a, $.proxy(e.close, e))
      // ESC和回车事件
      DOC.unbind(b).bind(b, (event) => {
        if (e.child != null) return
        if (event.which === 27 && e.o.esc !== false && !e.wrapper.hasClass(CSS.NOTONTOP)) {
          event.result !== false && e.close()
          return false
        }
        if (event.which === 13 && !e.wrapper.hasClass(CSS.NOTONTOP))
        {
          e.o.onEnter()
          e.dom().button.children(`.${CSS.ENTCLICK}`).triggerHandler(EVENT.B)
          return false
        }
      })
      WIN.unbind(c).bind(c, () => {
        e.offset(1)
      });
    },
    _showErr () {
      const e = this
      const s = e.o.err;
      if (e.o.showErr)
      {
        e.icon(3).padding(10).content({ text: s.content }).button([{ text: s.button }])
        if (e.dom().title.siblings().size() === 0) e.title(s.title)
      }
    },
    _setTop () {
      const e = this;
      e.wrapper.removeClass(CSS.NOTONTOP)
      $.each($.dialog.list, (x, y) => {
        if (y.zIndex < e.zIndex) y.wrapper.addClass(CSS.NOTONTOP)
      });
    },
    _eventName () {
      const n = '.'; let r
      for (let i = 0; i < arguments.length; i++)
      {
        if (r)
        {
          r = r + SPACE + arguments[i] + n + this.id
        }
        else
        {
          r = arguments[i] + n + this.id
        }
      }
      return r
    }
  }
  $.dialog.fn._init.prototype = $.dialog.fn;
  $.fn.dialog = function (o) {
    if (!$.isPlainObject(o)) o = {};
    o.refer = o.trigger = this;
    return $.dialog(o);
  };
  $.dialog.template
	= '<table class="jQ_Dialog">'
	  + '<thead>'
	  + '<tr>'
	  + '<th class="jQ_Dialog_Header_Left"></th>'
	  + '<th class="jQ_Dialog_Title"><span></span></th>'
	  + '<th class="jQ_Dialog_X"><a href="javascript:void(0)" hidefocus="true"></a></th>'
	  + '<th class="jQ_Dialog_Header_Right"></th>'
	  + '</tr>'
	  + '</thead>'
	  + '<tbody>'
	+ '<tr>'
+ '<td class="jQ_Dialog_Body_Left"></td>'
+ '<td colspan="2" height="100%">'
+ '<table class="jQ_Dialog_Body">'
+ '<tr><td class="jQ_Dialog_Icon"><p></p></td><td class="jQ_Dialog_Content Loading"></td></tr>'
+ '<tr class="jQ_Dialog_Button"><td colspan="2"></td></tr>'
+ '</table>'
+ '</td>'
+ '<td class="jQ_Dialog_Body_Right"></td>'
+ '</tr>'
+ '</tbody>'
+ '<tfoot>'
+ '<tr>'
+ '<td class="jQ_Dialog_Footer_Left"></td>'
+ '<td class="jQ_Dialog_Footer" colspan="2"></td>'
+ '<td class="jQ_Dialog_Footer_Right"><p class="jQ_Dialog_Resizer"></p></td>'
+ '</tr>'
+ '</tfoot>'
+	'</table>';
})($);
