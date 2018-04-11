/**
 * Created by samuel on 4/11/2018.
 */

if (!window['search.js']) {

    function enable_search_statics() {
        //console.log('- Search statics script installed');
        var container = $("[data-toggle='search-result']");
        var qterm = container.data("qterm");
        var qtype = container.data("qtype");
        var sid = container.data("sid"); // search id

        container.find("a").click(function () {
            var parents = $(this).parentsUntil('search-result');
            var novel_id = null;
            parents.each(function (idx, obj) {
                if (obj.hasAttribute('data-novel-id')) {
                    novel_id = $(obj).data('novel-id');
                }
            });
            $.ajax('/stat/', {
                type: 'POST',
                dataType: 'json',
                data: {
                    action: 'search-hit',
                    novel_id: novel_id,
                    qterm: qterm,
                    qtype: qtype,
                    sid: sid
                },
                beforeSend: function (xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
                },
                success: function (resp) {
                    //do nothing
                },
                error: function (resp) {
                    console.log('Error: ' + resp.status + ' ' + resp.statusText);
                }
            })
        });


        // expires sid after 3 minutes (then the click will add new search record)
        setTimeout(function () {
            container.data("sid", "")
        }, 180);
    }


    $(document).ready(function () {
        console.log("Search scripts installed.");
        enable_search_statics();
    });

    window['search.js'] = true;
}