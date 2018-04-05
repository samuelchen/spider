/**
 * Created by samuel on 3/15/18.
 */

// if img misses file.
$(document).ready(function(){
});

function get_site_info() {
    var author = document.getElementsByTagName("meta")["author"]['content'];
    var info = author.split(" ");
    return info;
}