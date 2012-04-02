$(document).ready(function() {
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