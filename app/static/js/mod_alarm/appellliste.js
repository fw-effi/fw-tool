$(document).ready(function () {
    // Select initialize
    $('.select').selectpicker();

    // Tooltip initialize
    $("[rel='tooltip']").tooltip();

    // SmartWizard initialize
    $('#smartwizard').smartWizard({
        theme: 'arrows',
        autoAdjustHeight: false,
        transition: {
            anmiation: 'slide-horizontal',
            speed: '400'
        },
        backButtonSupport: true,
        lang: {
            next: 'Weiter',
            previous: 'Zurück'
        },
        toolbarSettings: {
            toolbarPosition: 'top', // none, top, bottom, both
            toolbarButtonPosition: 'right', // left, right, center
        }
    });

    // Datatable initialize
    var table_times = $('#table-times').DataTable({
        dom: "<'top'f>rt",
        paging: false,
        responsive: true,
        language: {
            "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/German.json"
        },
        columns:
        [
            {"data": "name"},
            {"data": "time_from"},
            {"data": "time_to"},
            {"data": "atemschutz"},
            {
                data: null,
                render: function (data, type, row) {
                    return '<a href="#" class="menu-toggle"><i class="material-icons">edit</i></a> ';
                }
            }
        ]
    });

    // Open IndexedDB connection
    IndexedDB_open()

    // Form validation
    var validator = $('#form').validate({
        debug: true,
        rules: {
            einsatz_nr: "required",
            einsatz_description: "required"
        },
        messages: {
            einsatz_nr: "Bitte trage die Einsatznummer der ELZ ein.",
            einsatz_description: "Bitte trage eine Einsatzbeschreibung ein."
        }
    });

    // SmartWizard LeaveStep Event for validating Forms
    $('#smartwizard').on("leaveStep", function (e, anchorObject, currentStepIndex, nextStepIndex, stepDirection) {
        var currentStep = currentStepIndex + 1
        switch (currentStep) {
            case 1:
                var validation = true;
                $('#step-' + currentStep + ' input').each(function () {
                    validation = validator.element(this);
                })

                if (validation) {
                    saveDataToDB(currentStep)
                }
                return validation;
                break;

            case 2:
                saveDataToDB(currentStep)
                break;

            case 3:
                var data = table_times.data().toArray();
                saveDataToDB(currentStep, data)
        }
    });

    // SmartWizard ShowStep Event to load Data if needed
    $('#smartwizard').on("stepContent", function(e, anchorObject, stepIndex, stepDirection) {
        var currentStep = stepIndex + 1; // Index is last Step, that
       switch(currentStep) {
           case 2:
               // Load selected Firefighters from DB
               IndexedDB_read($('#einsatz_nr').val(), function (result) {
                   if (result === undefined) {
                       alert("Einsatz konnte nicht geladen werden. Bitte wähle in neu aus.")
                   } else {
                       var firefighters = result.firefighters
                       firefighters.forEach(function(item,index) {
                           $('#'+item.id).addClass('active')
                       })
                   }
               });
               break;
           case 3:
               IndexedDB_read($('#einsatz_nr').val(), function (result) {
                   if (result === undefined) {
                       alert("Einsatz konnte nicht geladen werden.")
                   } else {
                       var firefighters = result.firefighters
                       var table = $('#table-times').DataTable();
                        table.clear();
                        table.rows.add(firefighters).draw();
                   }
               });
               break;
       }
    });

    // Edit Person details in step 3
    $("#table-times").on('click', 'tbody td', function () {
        var rowindex = table_times.row(this).index();

        $('#rowId').val(rowindex)
        $('#person').val(table_times.cell(rowindex, 0).data())
        $('#einsatz_from').val(table_times.cell(rowindex, 1).data())
        $('#einsatz_to').val(table_times.cell(rowindex, 2).data())
        $('#atemschutz').val(table_times.cell(rowindex, 3).data())

        $('#EditRowModal').modal('show')
    });

    $('#btnEditRowSave').on('click', function() {
        var rowindex = $('#rowId').val()

        table_times.cell(rowindex, 1).data($('#einsatz_from').val())
        table_times.cell(rowindex, 2).data($('#einsatz_to').val())
        table_times.cell(rowindex, 3).data($('#atemschutz').val())

        $('#EditRowModal').modal('hide')
    });

    $('#btnTimesModalSave').on('click', function() {
        $('#txtTimeFrom').val($('#gen_einsatz_from').val())
        $('#txtTimeTo').val($('#gen_einsatz_to').val())

        $('#TimesModal').modal('hide')
    })
});


// Search Function in List Groups
$('#firefighter_search').on('input', function (e) {
    let input = $(this).val()
    let filter = input.toUpperCase()
    $('.list_firefighter .list-group-item').each(function () {
        let li = $(this)
        let text = li[0].outerText
        let meta = li[0].getAttribute('data-meta')

        if (text.toUpperCase().indexOf(filter) > -1 || meta.toUpperCase().indexOf(filter) > -1) {
            li.removeClass('d-none')
        } else {
            li.addClass('d-none');
        }
    });
});

// Add Person to Presentlist
$('.list_firefighter .list-group-item').on('click', function (e) {
    // Don't jump to the top
    e.preventDefault();

    let li = $(this)
    let id = li[0].getAttribute('id')

    if ($(this).hasClass('active')) {
        // Person no longer present
        $(this).removeClass('active')
    } else {
        // Person is present
        $(this).addClass('active')
    }
});


// Save Data to indexedDB
function saveDataToDB(step, data = {}, callback) {
    switch (step) {
        case 1:
            IndexedDB_read($('#einsatz_nr').val(), function (result) {
                if (result !== undefined) {
                    alert("Für diese Einsatz Nummer wurde bereits ein Appellblatt eröffnet. \n\rEs wird das bestehende Appellblatt geladen.")
                } else {
                    // Neur Einsatz, erstellen und weiter
                    var data = {
                        id: $('#einsatz_nr').val(),
                        description: $('#einsatz_description').val(),
                        firefighters: []
                    }
                    IndexedDB_write($('#einsatz_nr').val(), data, function (result) {
                        if (!result) { // Save Einsatz is failed
                            $('#smartwizard').smartWizard("prev");
                        }
                    });
                }
            });
            break;
        case 2:
            IndexedDB_read($('#einsatz_nr').val(), function (result) {
                result.firefighters = []
                $('#list_firefighter').children().each(function() {
                    if($(this).hasClass('active')) {
                        var firefighter = {
                            id: $(this)[0].getAttribute('id'),
                            name: $(this)[0].outerText,
                            time_from:'',
                            time_to:'',
                            atemschutz:0
                        }
                        result.firefighters.push(firefighter)

                    }
                })

                IndexedDB_write(result.id,result,function(){})
            });
            break;

        case 3:
            IndexedDB_read($('#einsatz_nr').val(), function (result) {
                result.firefighters = data

                IndexedDB_write(result.id,result,function(){})
            });
            break;
    }

}