(function ($) {
  const O = 'opacity';
  const C = 'CursorMove';
  const M = 'mousemove.drag';
  const U = 'mouseup.drag';
  const D = 'mousedown.drag';
  const W = $(window);
  const A = $(document);
  const timer = null;
  const E = function () {
    this.w.css(O, 1);
    A.unbind(`${M} ${U}`)
  }
  const G = function (e) {
    const m = this;
    const p = m.w.offset();
    const t = p.top;
    const l = p.left;
    const r = W.width() - m.w.outerWidth();
    const b = W.height() - m.w.outerHeight();
    const X = e.pageX;
    const Y = e.pageY;
    let x = m.p.left + (X - m.x) - W.scrollLeft()
    let y = m.p.top + (Y - m.y) - W.scrollTop();
    // 以下逻辑保证在可视范围内移动
    if (l <= 0 && X < m.x)
    {
      x = 0;
      m.x = Math.max(X, 0);
      m.p.left = 0;
    }
    if (t <= 0 && Y < m.y)
    {
      y = 0;
      m.y = Math.max(Y, 0);
      m.p.top = 0;
    }
    if (r <= l - A.scrollLeft() && X > m.x)
    {
      x = r;
      m.x = Math.min(X, r);
      m.p.left = r;
    }
    if (b <= t - A.scrollLeft() && Y > m.y)
    {
      y = b;
      m.y = Math.min(Y, b);
      m.p.top = b;
    }
    m.w.css({ left: x, top: y });
    return false;
  }
  const S = function (e, m) {
    e.preventDefault()
    m = this
    m.w.css(O, 0.8)
    m.p = m.w.offset()
    m.x = e.pageX
    m.y = e.pageY
    A.bind(M, $.proxy(G, m)).bind(U, $.proxy(E, m))
  }
  $.fn.Drag = function (o) {
    return this.each(function () {
      const e = $(this);
      const x = function () {
        this.h = o ? (typeof o === 'string' ? $(o, e[0]) : o) : e;
        this.w = e;
        return this;
      }
      const X = new x()
      e.data('__h', X.h);
      X.h.addClass(C).unbind(D).bind(D, $.proxy(S, X));
    })
  };
  $.fn.unDrag = function () {
    return this.each(function () {
      ($(this).data('__h') || $()).removeClass(C).unbind(D);
    })
  };
})($);
