$(document).ready(function() {


    let n_div = $("#notification");
    let n_content = $('#notification .lead');
    $('#notification .modal-footer').prepend($("#loaderImage").html())
    let notification_ws = new WebSocket('ws://' + window.location.host + '/ws/warehouse/install/notifications/');
    let notif_count = 0
    let n_title = $("#notificationLabel");
    n_title.html('Install Status');

    $('#app_button').click(function() {
        n_div.modal();
        $.get($(this).data('install-url'), function(data) {
            console.log(data)
        });
    })

    notification_ws.onmessage = function(e) {
        let data = JSON.parse(e.data);
        notif_count = notif_count + 1
        let new_element = `<div style="display: none;" id="install_notif_${notif_count}">${data.message}</div>`
        if (data.message == "install_complete") {
            // Hide the loader
            $('#notification .modal-footer').find('img').hide()
            new_element = `<div style="display: none;" id="install_notif_${notif_count}">Install Complete</div>`
        }
        n_content.append(new_element)
        $(`#install_notif_${notif_count}`).show('fast')
    };


});