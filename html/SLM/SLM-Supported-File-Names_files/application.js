!function ($) {
  $(function(){
    var $window = $(window)
    // side bar
    setTimeout(function () {
      $('.sidenav').affix({
        offset: { top: 0, bottom: 0 }
      })
    }, 100)
  })
}(window.jQuery)
