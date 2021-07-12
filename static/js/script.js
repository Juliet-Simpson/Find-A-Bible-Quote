$(document).ready(function(){
  $('.sidenav').sidenav({edge: "right"});
  $('.modal').modal();
  $("select").formSelect();
  $(".collapsible").collapsible();
});

$(function() {
  $('#flash').delay(2500).fadeOut();
});