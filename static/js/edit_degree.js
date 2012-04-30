var baseid = "#degreebase";
var global = {};

(function() {
    var degree;
    
    function mknode(type) {
	var node = {
	    node_type: type,
	    ptr: $("<div />")
	};
	node.header = $("<div class='header' />");
	var txt = $("<span />");
	txt.text(type);
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
	    parent[key] = box.val();
	});
	    
	parent.header.append(txt, box)
    }

    function mkcontainer(node_type) {
	var node = mknode(node_type);
	node.children = [];
	node.ptr.append(node.btns);
	node.credits = 0;
	node.sub = 0;
	mkmin(node, 'min. credits', '0', 'credits');
	mkmin(node, 'min. sub-requirements', 'all', 'min');
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

    function addmatch(parent) {
	var dialog = $("<div />");
	var DEBUGBOX = $("<input type='text' />");

	var onclose = function() {
	    var match = mknode('requirement');
	    var txt = $("<span />");
	    txt.text("<match>" + DEBUGBOX.val() + "</match>");
	    txt.insertBefore(match.btns);
	    mkbutton(match, 'delete', deletenode);
	    parent.append(match);
	    dialog.dialog('close');
	}
	
	dialog.append(DEBUGBOX);
	dialog.dialog({
	    autoOpen: false,
	    open: function(event, ui) { $(".ui-dialog-titlebar-close").hide(); },
	    buttons: {
		"Add": onclose,
		"Cancel": function() { console.log('discard the match');  $(this).dialog('close'); }
	    },
	    draggable: false,
	    modal: true,
	    resizable: false,
	    title: "Add a requirement",
	    closeOnEscape: false
	});
	dialog.dialog('open');
    }
    
    
    function init() {
	degree = mkcontainer('degree');
	
	$(baseid).append(degree.ptr);
	addgroup(degree);
	
	global.degree = degree;
    }
    
    $(document).ready(init);
})();
