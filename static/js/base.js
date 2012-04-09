$(document).ready(function() {
    $("button").button();
    
    var username_box = $("#login").find("input[name=username]");
    var password_box = $("#login").find("input[name=password]");

    // function used to make AJAX login request
    var login_fn = function() {
	username = username_box.val();
	password = password_box.val();
	
	var ajax_fn = function(json, status) {
	    if (json.status == 'okay') {
		// redirect
		window.location = json.redirect;
	    } else {
		$("#login_error").text(json.message);
	    }
	}
	
	// attempt to login
	$.ajax({ success: ajax_fn,
		 data: { username: username,
			 password: password },
		 dataType: "json",
		 type: "post",
		 url: "/login/" });
    }

    // set up login ajax
    $("#login_btn").click(login_fn);
    
    // set up enter key for username/password textboxes
    username_box.bind('keypress', function(e) {
	if (e.which == 13) { //enter
	    login_fn();
	}
    });

    password_box.bind('keypress', function(e) {
	if (e.which == 13) { //enter
	    login_fn();
	}
    });
    
    
    
    // set up text boxes with default values
    $("input.default").each(function(i, input) {
	var elm = $(input);
        var def = elm.val();
	var is_pw = elm.hasClass('pw');

	elm.focus(function() {
	    if (elm.val() == def) {
		elm.val('');
		if (is_pw)
		    input.setAttribute('type', 'password');
	    }
	});

	elm.blur(function() {
	    if (elm.val() == '') {
		elm.val(def);
		if (is_pw)
		    input.setAttribute('type', 'text');
	    }
	});
    });
});