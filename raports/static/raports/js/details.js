function execute_command(command, pk){
    if (command == 'transfer'){
        $.ajax({
            url: '/home/curators_modal/',
            type: "GET",
            success: function (data) {
              $("#curatorsModal").modal('show');
              $("#curatorsModal").html(data);
            }
        });
    }
    else if (command == 'to_performer'){
        console.log(command)
    }
    else{
        changeStatus(command, pk)
    }

}

function transferToPerformer(){
    console.log('aaaaaa')
}

function changeCuratorsGroup(pk){
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let url = '/home/change_curators_group/' + parseInt(pk) + '/'
    let new_group = $("#curatorGroupsSelect").val();
    let ajax_data = {
        'new_group': new_group,
        'pk': pk,
        'csrfmiddlewaretoken': csrftoken,
    }
    $.ajax({
        url: url,
        type: 'POST',
        data: ajax_data,
        success: function(response) {
            location.replace('/home/list/');
        }
    })
}

function changeStatus(status, pk){
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let url = '/home/update_raport/' + parseInt(pk) + '/'
    let ajax_data = {
        'status': status,
        'csrfmiddlewaretoken': csrftoken,
    }
    $.ajax({
        url: url,
        type: 'POST',
        data: ajax_data,
        success: function(response) {
            location.replace(url);
        }
    })
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