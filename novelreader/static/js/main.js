/**
 * Created by samuel on 3/15/18.
 */

if (!window['main.js']) {

// get site name & domain in array
    function get_site_info() {
        var author = document.getElementsByTagName("meta")["author"]['content'];
        var info = author.split(" ");
        return info;
    }


// read history of novels
    function save_history(novel_id, novel_name, chapter_id, chapter_name) {

        var MAX = 20;
        var history = load_history();
        if (!history) history = {
            indexes: [],
            records: {}
        };

        // This book was read already. Add chapters read count.
        if (history.records.hasOwnProperty(novel_id)) {
            var cnt = history.records[novel_id]['count'];
            cnt += 1;
            history.records[novel_id]['count'] = cnt;
            Cookies.set('history', history, {expires: 36500});

            // if read more than 10 chapters, we count the views of novel.
            if (cnt > 10) {
                add_novel_view_count(novel_id);
            }
            return;
        }

        var record = {
            "novel_id": novel_id,
            "novel_name": novel_name,
            "chapter_id": chapter_id,
            "chapter_name": chapter_name,
            "count": 0
        };
        history.indexes.push(novel_id);
        history.records[novel_id] = record;

        if (history.indexes.length > MAX) {
            var remove_id = history.indexes.shift();
            delete history.records[remove_id];
        }

        Cookies.set('history', history, {expires: 36500});
    }


// load read history
    function load_history() {
        var history = Cookies.getJSON('history');
        return history;
    }


    function add_novel_view_count(novel_id) {
        $.ajax('/stat/', {
            type: 'POST',
            dataType: 'json',
            data: {
                action: 'novel-view',
                novel_id: novel_id,
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
    }

    $(document).ready(function (){
        //$('[data-toggle="tooltip"]').tooltip();
        //$(document).tooltip();
        $('[title]').tooltip();
    });


    window['main.js'] = true;
}