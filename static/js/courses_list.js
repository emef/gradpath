$(document).ready(function() {
  var populate_fn = function() {
    var parent = $(this);
    var id = $(this).attr('id');
    $.get("../in_section/" + id, function(course_list) {
      var container = parent.find("div.courses");
      container.empty();
      for(var i=0, j=course_list.length; i<j; i++) {
        var course = course_list[i];
        var node = $("<div />");
		    node.html("<a href='../add/" + course.id + "'><img src='/img/add.gif' alt='[+]'></a> " + course.number + ": " + course.title);
		    container.append(node);
	    }
	  });
	  $(this).bind('click', hide_fn);
  }
    
  var hide_fn = function () {
	  $(this).find("div.courses").hide();
	  $(this).bind('click', show_fn);
  }

  var show_fn = function () {
	  $(this).find("div.courses").show();
	  $(this).bind('click', hide_fn);
  }
      
  $('li').bind('click', populate_fn);

});
