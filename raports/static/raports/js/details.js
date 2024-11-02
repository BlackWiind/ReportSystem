function execute_command(command, pk){
    if (command == 'created'){
        $.ajax({
            url: '/home/curators_modal/',
            type: "GET",
            success: function (data) {
              $("#UpdateModal").modal('show');
              $("#UpdateModalBody").html(data);
            }
        });
    }
    else if (command == '4'){
        $.ajax({
            url: '/home/purchasers_modal/',
            type: "GET",
            success: function (data) {
              $("#PurchasersModal").modal('show');
              $("#PurchasersModalBody").html(data);
            }
        });
    }
    else{
        let ajax_data = {
            'status': command,
            'pk': pk,
        }
        changeStatus(pk, ajax_data);
    }

}

function transferToPerformer(){
    let purchaser_pk = $("#purchasingSpecialistSelect").val();
    let ajax_data = {
        'assigned_purchasing_specialist': purchaser_pk,
    }
    $("#PurchasersModal").modal('hide');
    changeStatus(my_pk, ajax_data);
}

function changeCuratorsGroup(pk){
    let new_group = $("#curatorGroupsSelect").val();
    let ajax_data = {
        'curators_group': new_group,
        'pk': pk,
    }
    $("#UpdateModal").modal('hide');
    changeStatus(pk, ajax_data);
}

function changeStatus(pk, data){
    let url = '/home/update_raport/' + parseInt(pk) + '/'
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    data.csrfmiddlewaretoken = csrftoken;
    $.ajax({
        url: url,
        type: 'POST',
        dataType: "json",
        data: data,
        success: function(response) {
            location.replace('/home/list/');
        },
        error: function(data) {
            $("#AlertText").html(data.responseJSON.message)
            $(".alert").hide().show('medium');
        }
    })
}

function hideAlert(){
    $(".alert").hide();
}

function hideShow(){
    const elements = document.querySelectorAll('.hiddenElement')
    if  ( $(elements).is(':hidden')){
        $(elements).show();
    }
    else {
        $(elements).hide();
    }
}