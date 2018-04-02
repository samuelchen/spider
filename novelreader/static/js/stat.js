/**
 * Created by wchen8 on 4/3/2018.
 */

//function add_favorite(novel_id, novel_name, cb_success, cb_error){
//    $.ajax('/stat/', {
//        type: 'POST',
//        dataType: 'json',
//        data: {
//            novel_id: novel_id,
//            novel_name: novel_name,
//        },
//        beforeSend: function(xhr, settings) {
//            xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
//        },
//        success: cb_success,
//        error: cb_error
//    })
//}

$(document).ready(function() {
    var favorite_triggers = $("[data-toggle='favorite']");
    console.log(favorite_triggers);
    favorite_triggers.click(function() {
        var icon = $(this).find("i");
        console.log(icon);
        $.ajax('/stat/', {
            type: 'POST',
            dataType: 'json',
            data: {
                novel_id: $(this).data('novel-id'),
                novel_name: $(this).data('novel-name')
            },
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
            },
            success: function(resp) {
                console.log(resp);
                //TODO: color change
                if (resp.status == 'on') {
                    //icon.removeClass('user-icons');
                    icon.addClass('flag-on');
                } else {
                    icon.removeClass('flag-on');
                    //icon.addClass('user-icons');
                }
            },
            error: function(resp) {
                alert('Error: ' + resp.status + ' ' + resp.statusText);
            }
        })
    });
});