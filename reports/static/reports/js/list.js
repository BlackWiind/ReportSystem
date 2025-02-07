$(document).ready(function () {
  var trigger = $('#offcanvasBtn'),
      overlay = $('.overlay'),
      searchTrigger = $('#searchBtn'),
     isClosed = false;

    trigger.click(function () {
        hamburger_cross();
    });

    searchTrigger.click(function(){
        search();
    });

    function hamburger_cross() {

      if (isClosed == true) {
        overlay.hide();
        trigger.removeClass('is-open');
        trigger.addClass('is-closed');
        isClosed = false;
      } else {
        overlay.show();
        trigger.removeClass('is-closed');
        trigger.addClass('is-open');
        isClosed = true;
      }
  }

  function search(){
    console.log('Типа поиск')
  };

  $('[data-toggle="offcanvas"]').click(function () {
        $('#wrapper').toggleClass('toggled');
  });
});


