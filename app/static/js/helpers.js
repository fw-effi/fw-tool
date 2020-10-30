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

/* Lade alle neuen Mitteilungen um sie bei der "Glocke anzuzeigen" */
function notificationsLoad(onLoad=false) {
    /* Load new Messages Count */
    bevor_count = $("#notifications_count").text()

    $.ajax('/core/notifications/count').done(
        function(count) {
            $("#notifications_count").text(count[0]["message_count"])
            console.log(bevor_count)
            if(count[0]["message_count"] > 0 && count[0]["message_count"] != bevor_count) {
                $("#notifications_count").show()
                if(onLoad == false){ /* Zeige den Banner nur, wenn eine Nachricht während dem Besuch auf einer Seite eintrifft. */
                    showNotification("bg-green","Es sind <strong>"+count[0]["message_count"]+"</strong> neue Mitteilungen vorhanden.")
                }
            }
        }
    );

    /* Load last 10 Messages */
    $.ajax('/core/notifications/10').done(
        function(notifications) {
            notifications = JSON.parse(notifications);

            $("#notifications_messages li").remove();

            for (var i = 0; i < notifications.length; i++) {
                /* Create Message Symbol */
                switch(notifications[i]["type"]) {
                    case "Information":
                        symbol = "<div class='icon-circle bg-light-blue'><i class='material-icons'>info</i></div>";
                }
                payload = JSON.parse(notifications[i]["payload_json"])
                message = "<div class='menu-info'><h4>"+payload["title"]+"</h4><p>"+payload["message"]+"</p>";
                
                create_date = new Date()
                create_date = Date.parse(notifications[i]["date_created"])
                
                element = "<li><a href='"+notifications[i]["url"]+"' class='wave-effect wave-block'>"
                element += symbol
                element += message
                element += "<p><i class='material-icons'>access_time</i>"+moment(create_date).format('DD.MM.YYYY hh:mm')+"</p></div></a>"

                $("#notifications_messages").append(
                    element
                )
            }
        }
    );
}

$('#notifications_button').on('click',function() {
    $("#notifications_count").text("0")
    $("#notifications_count").hide()

    /* Update lastread value in Database */
    $.ajax({
        url: '/core/notifications/lastread',
        type: 'POST'
    });
});

/* Zeige die animierte Notificationselement für z.B. gespeicherte Informationen usw. */
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

/* Start Functions after Page loaded */
notificationsLoad(true)
setInterval(notificationsLoad,60000);