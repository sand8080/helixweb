if(!String.prototype.startsWith){
    String.prototype.startsWith = function (str) {
        return !this.indexOf(str);
    }
}


function _toggle_slider(controlId, slidedId, on_show, on_hide) {
    var ctl = $('#' + controlId)
    var ctl_label = ctl.attr('innerHTML')
    if (ctl_label.startsWith('[+]')) {
        ctl.attr('innerHTML', '[-]' + ctl_label.substr(3))
        on_show()
    } else {
        ctl.attr('innerHTML', '[+]' + ctl_label.substr(3))
        on_hide()
    }
    $('#' + slidedId).slideToggle('slow');
}


function _do_slide(controlId, slidedId, on_show, on_hide) {
    var ctl = $('#' + controlId)

    // check control is href
    if (ctl.attr('href') != null) {
        ctl.attr('href', 'javascript:void(0);')
    }

    $('#' + controlId).click(function() {
        _toggle_slider(controlId, slidedId, on_show, on_hide)
    });
}


function slider(controlId, slidedId) {
    _do_slide(controlId, slidedId, function() {}, function() {})
}


function slider_mem(controlId, slidedId) {
    var cookie_name = 'slider_' + slidedId
    var on_show = function() {
        $.cookie(cookie_name, true, {expires: 3650})
    }

    var on_hide = function() {
        $.cookie(cookie_name, false, {expires: 3650})
    }

    var state = $.cookie(cookie_name) == 'true'
    var is_visible = $('#' + slidedId).is(':visible')
    if (state != is_visible) {
        _toggle_slider(controlId, slidedId, on_show, on_hide)
    }

    _do_slide(controlId, slidedId, on_show, on_hide)

}