/**
 * Created by samuel on 3/15/18.
 */

if (!window['main.js']) {

    Array.prototype.indexOf = function (val) {
        for (var i = 0; i < this.length; i++) {
            if (this[i] == val) return i;
        }
        return -1;
    };

    Array.prototype.remove = function (val) {
        var index = this.indexOf(val);
        if (index > -1) {
            this.splice(index, 1);
        }
    };

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

        var record = {
            "novel_id": novel_id,
            "novel_name": novel_name,
            "chapter_id": chapter_id,
            "chapter_name": chapter_name,
            "count": 0
        };

        // This book was read already.
        if (history.records.hasOwnProperty(novel_id)) {
            record = history.records[novel_id];
            history.indexes.remove(novel_id);
        }

        if (chapter_id) record['chapter_id'] = chapter_id;
        if (chapter_name) record['chapter_name'] = chapter_name;
        record['count'] += 1;
        history.indexes.unshift(novel_id);
        history.records[novel_id] = record;

        // if read more than 10 chapters, we count the views of novel.
        if (record['count'] > 10) {
            add_novel_view_count(novel_id);
        }

        if (history.indexes.length > MAX) {
            var remove_id = history.indexes.pop();
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