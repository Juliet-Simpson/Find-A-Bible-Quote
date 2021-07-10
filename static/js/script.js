$(document).ready(function(){
  $('.sidenav').sidenav({edge: "right"});
  $('.modal').modal();
});

$(function() {
  $('#flash').delay(0).fadeIn('normal', function() {
     $(this).delay(2500).fadeOut();
  });
});