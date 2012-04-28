var baseid = "#degreebase";
var global = {};

(function() {
    var degree;
    var colors = ["#E20048", "#6BE400", "#FF4500", "#00B060"];
    
    function updatecolor(node) {
	node.ptr.css("border-color", colors[node.color]);
    }
    
    function mknode(type) {
	var node = {
	    node_type: type,
	    ptr: $("<div />")
	};
	var header = $("<div />");
	header.text(type);
	node.ptr.append(header);
	node.ptr.addClass('node');
	node.ptr.addClass(type);
	return node;
    }

    function mkbuttons(parent) {
	var d = $("<div />");
	var addgrp = $("<button>add group</button>");
	var addmatch = $("<button>add match</button>");
	d.append(addgrp, addmatch);

	addgrp.click(function() {
	    addgroup(parent);
	});
	
	addmatch.click(function() {
	    console.log("ADD MATCH");
	});

	addgrp.button();
	addmatch.button();

	return d;
    }

    function mkdegree() {
	var degree = mknode('degree');
	degree.children = [];
	degree.btns = mkbuttons(degree);
	degree.color = 0;
	degree.ptr.append(degree.btns);
	updatecolor(degree);
	return degree;
    }

    function addgroup(parent) {
	var node = mknode('group');
	node.children = [];
	node.btns = mkbuttons(node);
	node.color = (parent.color + 1) % colors.length;
	
	updatecolor(node);
	node.ptr.append(node.btns);
	node.ptr.insertBefore(parent.btns);
	parent.children.push(node);

	
	return node;
    }
    
    
    function init() {
	degree = mkdegree();
	
	$(baseid).append(degree.ptr);
	addgroup(degree);
	
	global.degree = degree;
    }
    
    $(document).ready(init);
})();
