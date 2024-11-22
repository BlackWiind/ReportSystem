$(document).ready( function(){
    $('#addTagForm').on('submit', function(e){
        e.preventDefault();
        addNewTag();
        $('#tagModal').modal('hide');
    })
    $('#feedbackForm').on('submit', function(e){
        e.preventDefault();
        feedBack();
        $('#feedbackModal').modal('hide');
    })
})

function addNewTag() {
    let form = document.querySelector('#addTagForm');
    data = new FormData(form);
    let url = '/home/add_new_tag/';

    $.ajax({
        url: url,
        type: 'POST',
        processData: false,
        contentType: false,
        data: data,
        success: function(response) {
            $("#AlertText").html(response.message);
            $(".alert").hide().show('medium');
        },
        error: function(data) {
            $("#AlertText").html(data.responseJSON.message);
            $(".alert").hide().show('medium');
        }
    })
}


function feedBack() {
    let form = document.querySelector('#feedbackForm');
    data = new FormData(form);
    let url = '/home/feedback/';

    $.ajax({
        url: url,
        type: 'POST',
        processData: false,
        contentType: false,
        data: data,
        success: function(response) {
            $("#AlertText").html(response.message);
            $(".alert").hide().show('medium');
        },
        error: function(data) {
            $("#AlertText").html(data.responseJSON.message);
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