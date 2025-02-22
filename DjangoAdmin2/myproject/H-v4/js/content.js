const $parentNode = window.parent.document

function $childNode(name) {
  return window.frames[name]
}

// tooltips
$('.tooltip-demo').tooltip({
  selector: '[data-toggle=tooltip]',
  container: 'body'
});

// 使用animation.css修改Bootstrap Modal
$('.modal').appendTo('body')

$('[data-toggle=popover]').popover();

// 折叠ibox
$('.collapse-link').click(function () {
  const ibox = $(this).closest('div.ibox')
  const button = $(this).find('i')
  const content = ibox.find('div.ibox-content')
  content.slideToggle(200);
  button.toggleClass('fa-chevron-up').toggleClass('fa-chevron-down');
  ibox.toggleClass('').toggleClass('border-bottom');
  setTimeout(() => {
    ibox.resize();
    ibox.find('[id^=map-]').resize();
  }, 50);
})

// 关闭ibox
$('.close-link').click(function () {
  const content = $(this).closest('div.ibox')
  content.remove();
})

// 判断当前页面是否在iframe中
if (top == this) {
  const gohome = '<div class="gohome"><a class="animated bounceInUp" href="index.html?v=4.0" title="返回首页"><i class="fa fa-home"></i></a></div>'
  $('body').append(gohome);
}

// animation.css
function animationHover(element, animation) {
  element = $(element);
  element.hover(
    () => {
      element.addClass(`animated ${animation}`)
    },
    () => {
      // 动画完成之前移除class
      window.setTimeout(() => {
        element.removeClass(`animated ${animation}`)
      }, 2000);
    }
  )
}

// 拖动面板
function WinMove() {
  const element = '[class*=col]';
  const handle = '.ibox-title';
  const connect = '[class*=col]';
  $(element).sortable({
    handle,
    connectWith: connect,
    tolerance: 'pointer',
    forcePlaceholderSize: true,
    opacity: 0.8,
  })
    .disableSelection();
};
