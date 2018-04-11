/**
 * Created by samuel on 4/3/2018.
 */


function enable_favorite(){
    console.log('- Favorite button script installed');
    var favorite_triggers = $("[data-toggle='favorite']");

    favorite_triggers.click(function() {
        var icon = $(this).find("i");

        $.ajax('/stat/', {
            type: 'POST',
            dataType: 'json',
            data: {
                action: 'favorite',
                novel_id: $(this).data('novel-id')
            },
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
            },
            success: function(resp) {
                if (resp.status == 'on') {
                    icon.addClass('flag-on');
                } else {
                    icon.removeClass('flag-on');
                }
            },
            error: function(resp) {
                alert('Error: ' + resp.status + ' ' + resp.statusText);
            }
        })
    });
}


function enable_recommends(){
    console.log('- Recommend button script installed');
    var recommend_triggers = $("[data-toggle='recommend']");

    recommend_triggers.click(function(event) {
        var trigger = $(this);
        var icon = trigger.find("i");

        $.ajax('/stat/', {
            type: 'POST',
            dataType: 'json',
            data: {
                action: 'recommend',
                novel_id: trigger.data('novel-id')
            },
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
            },
            success: function(resp) {
                if (resp.status > 0) {
                    trigger.attr('title', '推荐（' + resp.status + '次）');
                    trigger.append(' <span class="badge text-primary" style="font-size:9px">+1</span>');
                    trigger.find('span').fadeOut('slow').fadeIn().fadeOut('slow', function(){
                        $(this).remove();
                    });
                    icon.addClass('flag-on');
                } else {
                    icon.removeClass('flag-on');
                }
            },
            error: function(resp) {
                alert('Error: ' + resp.status + ' ' + resp.statusText);
            }
        })
    });
}


$(document).ready(function() {
    console.log("Action status button scripts installed.");
    enable_favorite();
    enable_recommends();
});