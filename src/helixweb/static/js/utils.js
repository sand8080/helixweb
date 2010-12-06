if(!String.prototype.startsWith){
    String.prototype.startsWith = function (str) {
        return !this.indexOf(str);
    }
}


function slider(controlId, slidedId) {
    $('#' + controlId).click(function() {
        $('#' + slidedId).slideToggle('slow');
        if (this.innerHTML.startsWith('[+]')) {
            this.innerHTML = '[-]' + this.innerHTML.substr(3)
        } else {
            this.innerHTML = '[+]' + this.innerHTML.substr(3)
        }
    });
}
