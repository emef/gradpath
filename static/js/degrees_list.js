$(document).ready(function() {
  var populate_fn = function() {
    var parent = $(this);
    var id = $(this).attr('id');
    $.get("../in_college/" + id, function(degree_list) {
      var container = parent.find("div.degrees");
      container.empty();
      for(var i=0, j=degree_list.length; i<j; i++) {
        var degree = degree_list[i];
        var node = $("<div />");
        node.html("<a href='../add/" + degree.id + "'><img src='/img/add.gif' alt='[+]'></a> " + degree.name + " - " + degree.year);
		    container.append(node);
	    }
	  });
	  $(this).bind('click', hide_fn);
  }
    
  var hide_fn = function () {
	  $(this).find("div.degrees").hide();
	  $(this).bind('click', show_fn);
  }

  var show_fn = function () {
	  $(this).find("div.degrees").show();
	  $(this).bind('click', hide_fn);
  }
      
  $('li').bind('click', populate_fn);

});