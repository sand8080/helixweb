function calendar(fieldName) {
    $("#id_" + fieldName).datepicker($.datepicker.regional["{{ cur_lang }}"])
    $("#id_" + fieldName).datepicker({
        changeYear: true,
        showOn: "button",
        buttonImage: "/static/images/calendar.gif",
        buttonImageOnly: true
    });
    $("#id_" + fieldName).datepicker("option", "dateFormat", "yy-mm-dd")

    dateParam = $.url.param(fieldName)
    if (dateParam) {
        $("#id_" + fieldName).datepicker("setDate", dateParam)
    }
}
