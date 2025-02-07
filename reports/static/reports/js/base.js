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

    $('#vocationOkButton').on('click', function () {
            let url = '/new_vocation/'
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            let data = {'deputy': $('#vocation_select').val(),
                        'vocation_start': $('#startDate').val(),
                        'vocation_end': $('#endDate').val(),
                        'csrfmiddlewaretoken': csrftoken,
            };
            $("#vocationModal").modal('hide');
            $.ajax({
                url: url,
                type: 'POST',
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
      });

    $('#vocation_select').select2({
        placeholder: 'Введите имя',
        allowClear: true,
        maximumSelectionLength: 1
    });

    $('#vocation_select').select2({
        dropdownParent: $('#vocationModal .modal-content')
    });

    $('.js-example-basic-multiple').select2();

    $("#vocation_select").select2({
        ajax: {
          type: 'get',
          url: '/usernames_loader/',
          delay: 300,
          dataType: 'json',
          data: function (params) {
            return params.term ? {search: params.term} : {search: ""};
          },
          success: function (data) {
                return {
                    result: $.map(data, function (item) {
                        item.id =  item.id;
                        item.text = item.text || item.name;

                        return {
                            text: item.text,
                            id: item.id
                        }
                    })
                };
              }
            },
        }
    )
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

$(".js-data-example-ajax").select2({
    ajax: {
      type: 'get',
      url: '/usernames_loader/',
      delay: 300,
      dataType: 'json',
      data: function (params) {
        return params.term ? {search: params.term} : {search: ""};
      },
      success: function (data) {
             data =  $.map(data, function (item) {
                              return item;
                            });
            return {
                result: $.map(data, function (item) {
                    item.id =  item.code;
                    item.text = item.text || item.code + ' ' + item.disease;

                    return {
                        text: item.text,
                        id: item.id
                    }
                })
            };
          }
        },
    }
)

