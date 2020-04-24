function hexToRgb(hexCode) {
    var patt = /^#([\da-fA-F]{2})([\da-fA-F]{2})([\da-fA-F]{2})$/;
    var matches = patt.exec(hexCode);
    var rgb = "rgb(" + parseInt(matches[1], 16) + "," + parseInt(matches[2], 16) + "," + parseInt(matches[3], 16) + ")";
    return rgb;
}

function hexToRgba(hexCode, opacity) {
    var patt = /^#([\da-fA-F]{2})([\da-fA-F]{2})([\da-fA-F]{2})$/;
    var matches = patt.exec(hexCode);
    var rgb = "rgba(" + parseInt(matches[1], 16) + "," + parseInt(matches[2], 16) + "," + parseInt(matches[3], 16) + "," + opacity + ")";
    return rgb;
}

function reloadLodurData() {
    $("#topRightLodurSyncIcon").addClass("fa-spin");
    $.ajax({
        url: '/lodur/updateData',
        type: 'POST',
        success: function(response) {
            showNotification('alert-success','Lodur Daten aktualisiert');
            console.log(response);
            $("#topRightLodurSyncIcon").removeClass("fa-spin");
            $("#topRightLodurSyncTime").text(moment(new Date()).format('DD.MM.YYYY hh:mm:ss'));
        },
        error: function(error) {
            showNotification('alert-danger','Fehler bei Lodurdaten: ' + error)
            console.log(error);
            $("#topRightLodurSyncIcon").removeClass("fa-spin");
        }
    });
    
}

function showNotification(colorName, text) {
    if (colorName === null || colorName === '') { colorName = 'bg-black'; }
    if (text === null || text === '') { text = 'Turning standard Bootstrap alerts'; }
    var animateEnter = 'animated fadeInRight';
    var animateExit = 'animated fadeOutRight'; 
    var allowDismiss = true;
    var placementFrom = 'top';
    var placementAlign = 'right';

    $.notify({
        message: text
    },
        {
            type: colorName,
            allow_dismiss: allowDismiss,
            newest_on_top: true,
            timer: 9000,
            placement: {
                from: placementFrom,
                align: placementAlign
            },
            animate: {
                enter: animateEnter,
                exit: animateExit
            },
            template: '<div data-notify="container" class="bootstrap-notify-container alert alert-dismissible {0} ' + (allowDismiss ? "p-r-35" : "") + '" role="alert">' +
            '<button type="button" aria-hidden="true" class="close" data-notify="dismiss">×</button>' +
            '<span data-notify="icon"></span> ' +
            '<span data-notify="title">{1}</span> ' +
            '<span data-notify="message">{2}</span>' +
            '<div class="progress" data-notify="progressbar">' +
            '<div class="progress-bar progress-bar-{0}" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>' +
            '</div>' +
            '<a href="{3}" target="{4}" data-notify="url"></a>' +
            '</div>'
        });
}