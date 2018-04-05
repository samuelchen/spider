/**
 * Created by samuel on 3/15/18.
 */

// if img misses file.
$(document).ready(function(){
});

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

    if (history.records.hasOwnProperty(novel_id))
        return;


    var record = {
        "novel_id": novel_id,
        "novel_name": novel_name,
        "chapter_id": chapter_id,
        "chapter_name": chapter_name
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
function load_history(){
    var history = Cookies.getJSON('history');
    return history;
}
