var baseid = "#degreebase";
var global = {};

(function() {
    var degree;
    var sectionsource;
    
    function mknode(type) {
	var node = {
	    node_type: type,
	    ptr: $("<div />")
	};
	
	if (type == 'match')
	    label = 'requirement';
	else
	    label = type

	node.header = $("<div class='header' />");
	var txt = $("<span />");
	txt.text(label);
	node.header.append(txt);
	node.ptr.append(node.header);
	node.ptr.addClass('node');
	node.ptr.addClass(type);
	node.btns = $("<div class='buttons' />");
	node.ptr.append(node.btns);
	return node;
    }

    function mkbutton(parent, text, callback) {
	var btn = $("<button></button>");
	btn.text(text);
	btn.click(function() { callback(parent); });
	btn.button();
	parent.btns.append(btn);
    }

    function mkmin(parent, str, val, key) {
	var txt = $("<span />");
	var box = $("<input type='text' class='min' />");
	
	txt.text(str);
	box.val(val);

	box.change(function() {
	    if (box.val() == 'all') {
		delete parent[key];
	    } else {
		parent[key] = box.val();
	    }
	});

	if (!parent.minmap) 
	    parent.minmap = {}

	parent.minmap[key] = box;
	parent.header.append(txt, box)
    }

    function mkcontainer(node_type, extra) {
	var node = mknode(node_type);
	node.children = [];
	node.ptr.append(node.btns);
	node.mincredits = 0;
	node.maxcredits = 0;
	node.minsub = 0;
	if (extra != false) {
	    mkmin(node, 'min. credits', '0', 'mincredits');
	    mkmin(node, 'min. sub-requirements', 'all', 'minsub');
	}
	mkbutton(node, 'add group', addgroup);
	mkbutton(node, 'add requirement', addmatch);
	node.append = function(subnode) {
	    subnode.parent = node;
	    subnode.ptr.insertBefore(node.btns);
	    node.children.push(subnode);
	}
	node.deletenode = function(subnode) {
	    for(i=0; i<node.children.length; i++) {
		if (node.children[i] == subnode) {
		    node.children[i].ptr.remove();
		    node.children.splice(i, 1);
		    return;
		}
	    }
	}
	return node;
    }

    function deletenode(node) {
	node.parent.deletenode(node);
    }
    
    function addgroup(parent) {
	var node = mkcontainer('group');
	parent.append(node);
	mkbutton(node, 'delete', deletenode);
	return node;
    }

    function get_courses(courses, cb) {
	$.ajax({
	    type:"POST",
	    data: {courses: JSON.stringify(courses)},
	    dataType: "json",
	    url: "/administrator/edit_degree/ajax/get_courses/",
	    success: function(r) { 
		if (r.courses) 
		    cb(r.courses);
		$.modal.close();
	    }
	});
    }
    
    function addmatch(parent) {
	var dialog = $("#matchmodal");
	
	var onclose = function() {
	    $.modal.close();
	}

	var onsave = function() {
	    var match = mknode('match', 'requirement');
	    var data = $("<div />");
	    var modalcourse = $("#modalcourse");
	    var modalfilter = $("#modalfilter");

	    var add_course_node = function(course, maxcredits) {
		match.id = course.id;
		var text = course.section.abbreviation + ' ' + 
		    course.number + ': ' + course.title;
		
		if (maxcredits) {
		    var repeat = mkcontainer('repeatable', false);
		    mkbutton(repeat, 'delete', deletenode);
		    repeat.maxcredits = maxcredits;
		    parent.append(repeat);
		    parent = repeat;
		    text += " (repeatable up to " + maxcredits + " credits)";
		} else {
		    mkbutton(match, 'delete', deletenode);
		}

		data.text(text);
		data.insertBefore(match.btns);
		parent.append(match);
	    }

	    var add_filter_node = function(filter) {
		if (filter.section) 
		    match.section = filter.section
		if (filter.minnumber)
		    match.minnumber = filter.minnumber
		if (filter.repeatable) {
		    var repeat = mkcontainer('repeatable', false);
		    mkbutton(repeat, 'delete', deletenode);
		    parent.append(repeat);
		    parent = repeat;
		} else {
		    mkbutton(match, 'delete', deletenode);
		}
		var html = "<div>Course from section " + filter.section.toUpperCase();
		if (filter.minnumber) {
		    html += " with course number greater than " + filter.minnumber;
		}
		html += "</div>";
		if (filter.prereqs.length) {
		    match.prereqs = []
		    html += "Requires a prerequisite from: <ul>";
		    for (var i=0; i<filter.prereqs.length; i++) {
			var prereq = filter.prereqs[i];
			match.prereqs.push(prereq.id)
			html += "<li>" + prereq.section.abbreviation.toUpperCase() + " " +
			    prereq.number + ": " + prereq.title + "</li>";
		    }
		    html += "</ul>";
		}
		data.html(html);
		data.insertBefore(match.btns);
		parent.append(match);
	    }
	    
	    if (modalcourse.hasClass("selected")) {
		var section = modalcourse.find("input[name=section]").val();
		var number = modalcourse.find("input[name=number]").val();
		var maxcredits = modalcourse.find("input[name=maxcredits]").val();
		get_courses([{section: section, number: number}], function(courses) {
		    var course = courses[0];
		    add_course_node(course, maxcredits);
		});
	    } else {
		var section = modalfilter.find("input[name=section]").val();
		var minnumber = modalfilter.find("input[name=minnumber]").val();
		var repeatable = modalfilter.find("input[name=repeatable]").is(':checked');
		console.log(repeatable);
		var prereqs = [];
		var errors = [];
		modalfilter.find("#prereqs > div").each(function() {
		    var s = $(this).find("input[name=psection]").val();
		    var n = $(this).find("input[name=pnumber]").val();
		    prereqs.push({section: s, number: n})
		});
		
		get_courses(prereqs, function(courses) {
		    add_filter_node({
			section: section,
			minnumber: minnumber,
			repeatable: repeatable,
			prereqs: courses
		    });
		});
		
	    }
	    
	}

	$("#reqsave").unbind('click').bind('click', onsave);
	
	dialog.modal({
	    autoOpen: false,
	    onOpen: function(dialog) {
		initreq();
		dialog.container.css("height", "auto");
		dialog.overlay.fadeIn('fast', function () {
		    dialog.container.slideDown('fast', function () {
			dialog.data.fadeIn('fast');
		    });
		});	
	    },
	    onClose: onclose,
	    width: 500,
	    minHeight: 200,
	    draggable: false,
	    modal: true,
	    resizable: false,
	    title: "Requirement Editor",
	    closeOnEscape: false
	});

	$("#matchmodal input[name=section]").each(function() {
	    $(this).autocomplete({
		source:sectionsource
	    });
	});
    }
    
    
    function initreq() {
	var bodies = $("#modalcourse, #modalfilter");
	var tabs = $("#modaltabs *");
	var currentbody = $(bodies[0]);
	var currenttab = $(tabs[0]);
	tabs.each(function (i) {
	    var body = $(bodies[i]);
	    $(this).unbind('click').bind('click', function() {
		currentbody.hide();
		currenttab.removeClass();
		currentbody.removeClass();
		body.show()
		currenttab = $(this);
		currentbody = body;
		currenttab.addClass("selected");
		currentbody.addClass("selected");
	    });
	});

	$("#addprereq").unbind('click').bind('click', function () {
	    function input(name, label) {
		var d = $("<div />");
		d.append( $("<label for='"+name+"'>"+label+"</label>") );
		d.append( $("<input type='text' name='"+name+"' />") );
		return d;
	    }
	    var div = $("<div class='prereq' />");
	    var sections = input("psection", 'section');
	    sections.find("input").autocomplete({ source: sectionsource });
	    div.append( sections );
	    div.append( input("pnumber", 'number') );
	    $("#prereqs").append(div);
	});
	
    }
    
    function fill_id(id, dst) {
	$.ajax({
	    type: 'POST',
	    url:'',
	    dataType: 'json',
	    success: function (r) {
		
	    }
	});
    }
    
    function in_array(key, arr) {
	for (var i=0, j=arr.length; i<j; i++)
	    if (key == arr[i])
		return true;
	return false;
    }
    
    function init() {
	initreq();

	var degree;
	//degree = mkcontainer('degree');
	
	$.ajax({
	    type: 'POST',
	    url: '',
	    dataType: 'json',
	    success: function (r) {
		var allowed = ['node_type', 'mincredits', 'maxcredits', 'minsub', 
			       'id', 'section', 'minnumber', 'prereqs'];
		var add_node = function(node, parent) {
		    var new_node;
		    
		    if (node.node_type == 'match')
			new_node = mknode(node.node_type);
		    else
			new_node = mkcontainer(node.node_type, 'repeatable' != node.node_type);
		    
		    for (key in node) {
			if (in_array(key, allowed)) {
			    new_node[key] = node[key];
			    if (in_array(key, ['mincredits', 'minsub']))
				new_node.minmap[key].val(node[key]);
			}
			if (key == 'id') {
			    get_courses([node.id], function (course) {
				console.log(course);
			    });
			}
		    }

		    if ('children' in node) {
			for (var i in node.children) {
			    add_node(node.children[i], new_node);
			}
		    }
		    
		    if (parent)
			parent.append(new_node);
		    else
			return new_node;
		}
		
		degree = add_node(r);
		$(baseid).append(degree.ptr);
		global.degree = degree;
		
	    }
	});
	
	

	
	$.ajax({
	    type: "GET",
	    url: "/administrator/edit_degree/ajax/sections/",
	    dataType: "json",
	}).success(function(sections) {
	    var source = [];
	    for (var i=0; i < sections.length; i++) {
		var obj = sections[i];
		source.push({label: obj.name, value: obj.abbreviation});
		source.push({label: obj.abbreviation, value: obj.abbreviation});
	    }
	    
	    sectionsource = source;
	    
	    
	});
    }
    
    $(document).ready(init);
})();
