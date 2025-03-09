$(document).ready(() => {
  const $image = $('.image-crop > img');
  $($image).cropper({
    aspectRatio: 1.618,
    preview: '.img-preview',
    done (data) {
      // 输出结果
    }
  });

  const $inputImage = $('#inputImage');
  if (window.FileReader) {
    $inputImage.change(function () {
      const fileReader = new FileReader();
      const files = this.files;
      let file

      if (!files.length) {
        return
      }

      file = files[0];

      if (/^image\/\w+$/.test(file.type)) {
        fileReader.readAsDataURL(file);
        fileReader.onload = function () {
          $inputImage.val('')
          $image.cropper('reset', true).cropper('replace', this.result);
        };
      } else {
        showMessage('请选择图片文件')
      }
    });
  } else {
    $inputImage.addClass('hide')
  }

  $('#download').click(() => {
    window.open($image.cropper('getDataURL'));
  })

  $('#zoomIn').click(() => {
    $image.cropper('zoom', 0.1);
  })

  $('#zoomOut').click(() => {
    $image.cropper('zoom', -0.1);
  })

  $('#rotateLeft').click(() => {
    $image.cropper('rotate', 45);
  })

  $('#rotateRight').click(() => {
    $image.cropper('rotate', -45);
  })

  $('#setDrag').click(() => {
    $image.cropper('setDragMode', 'crop')
  });

  $('#data_1 .input-group.date').datepicker({
    todayBtn: 'linked',
    keyboardNavigation: false,
    forceParse: false,
    calendarWeeks: true,
    autoclose: true
  });

  $('#data_2 .input-group.date').datepicker({
    startView: 1,
    todayBtn: 'linked',
    keyboardNavigation: false,
    forceParse: false,
    autoclose: true,
    format: 'yyyy-mm-dd'
  });

  $('#data_3 .input-group.date').datepicker({
    startView: 2,
    todayBtn: 'linked',
    keyboardNavigation: false,
    forceParse: false,
    autoclose: true
  });

  $('#data_4 .input-group.date').datepicker({
    minViewMode: 1,
    keyboardNavigation: false,
    forceParse: false,
    autoclose: true,
    todayHighlight: true
  });

  $('#data_5 .input-daterange').datepicker({
    keyboardNavigation: false,
    forceParse: false,
    autoclose: true
  });

  const elem = document.querySelector('.js-switch')
  const switchery = new Switchery(elem, {
    color: '#1AB394'
  })

  const elem_2 = document.querySelector('.js-switch_2')
  const switchery_2 = new Switchery(elem_2, {
    color: '#ED5565'
  })

  const elem_3 = document.querySelector('.js-switch_3')
  const switchery_3 = new Switchery(elem_3, {
    color: '#1AB394'
  })

  $('.i-checks').iCheck({
    checkboxClass: 'icheckbox_square-green',
    radioClass: 'iradio_square-green'
  });

  $('.colorpicker-demo1').colorpicker();

  $('.colorpicker-demo2').colorpicker();

  $('.colorpicker-demo3').colorpicker();

  // Code for demos
  function createColorpickers() {
    // Api demo
    const bodyStyle = $('body')[0].style
    $('#demo_apidemo').colorpicker({
      color: bodyStyle.backgroundColor
    }).on('changeColor', (ev) => {
      bodyStyle.backgroundColor = ev.color.toHex();
    })

    // Horizontal mode
    $('#demo_forceformat').colorpicker({
      format: 'rgba', // force this format
      horizontal: true
    });

    $('.demo-auto').colorpicker();

    // Disabled / enabled triggers
    $('.disable-button').click((e) => {
      e.preventDefault();
      $('#demo_endis').colorpicker('disable');
    })

    $('.enable-button').click((e) => {
      e.preventDefault();
      $('#demo_endis').colorpicker('enable');
    })
  }

  createColorpickers();

  // Create / destroy instances
  $('.demo-destroy').click((e) => {
    e.preventDefault();
    $('.demo').colorpicker('destroy');
    $('.disable-button, .enable-button').off('click');
  })

  $('.demo-create').click((e) => {
    e.preventDefault();
    createColorpickers();
  })

  const divStyle = $('.back-change')[0].style
  $('#demo_apidemo').colorpicker({
    color: divStyle.backgroundColor
  }).on('changeColor', (ev) => {
    divStyle.backgroundColor = ev.color.toHex();
  })

  $('.clockpicker').clockpicker();

  $('#file-pretty input[type="file"]').prettyFile();

})
const config = {
  '.chosen-select': {},
  '.chosen-select-deselect': {
    allow_single_deselect: true
  },
  '.chosen-select-no-single': {
    disable_search_threshold: 10
  },
  '.chosen-select-no-results': {
    no_results_text: 'Oops, nothing found!'
  },
  '.chosen-select-width': {
    width: '95%'
  }
};
for (const selector in config) {
  $(selector).chosen(config[selector]);
}

$('#ionrange_1').ionRangeSlider({
  min: 0,
  max: 5000,
  type: 'double',
  prefix: '&yen;',
  maxPostfix: '+',
  prettify: false,
  hasGrid: true
});

$('#ionrange_2').ionRangeSlider({
  min: 0,
  max: 10,
  type: 'single',
  step: 0.1,
  postfix: ' 克',
  prettify: false,
  hasGrid: true
});

$('#ionrange_3').ionRangeSlider({
  min: -50,
  max: 50,
  from: 0,
  postfix: '°',
  prettify: false,
  hasGrid: true
});

$('#ionrange_4').ionRangeSlider({
  values: [
    '一月',
    '二月',
    '三月',
    '四月',
    '五月',
    '六月',
    '七月',
    '八月',
    '九月',
    '十月',
    '十一月',
    '十二月'
  ],
  type: 'single',
  hasGrid: true
});

$('#ionrange_5').ionRangeSlider({
  min: 10000,
  max: 100000,
  step: 100,
  postfix: ' km',
  from: 55000,
  hideMinMax: true,
  hideFromTo: false
});

$('.dial').knob();

$('#basic_slider').noUiSlider({
  start: 40,
  behaviour: 'tap',
  connect: 'upper',
  range: {
    min: 20,
    max: 80
  }
});

$('#range_slider').noUiSlider({
  start: [40, 60],
  behaviour: 'drag',
  connect: true,
  range: {
    min: 20,
    max: 80
  }
});

$('#drag-fixed').noUiSlider({
  start: [40, 60],
  behaviour: 'drag-fixed',
  connect: true,
  range: {
    min: 20,
    max: 80
  }
});
