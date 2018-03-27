/**
 * Created by Samuel on 3/27/2018.
 */

Chapter = {

    _obj_article: null,
    _obj_container: null,
    _obj_left: null,
    _obj_right: null,
    _obj_plus: null,
    _obj_minus: null,
    _obj_font_sel: null,
    _obj_size_sel: null,
    _obj_bgcolor_sel: null,

    _next: '',
    _prev: '',
    _colors: {

    },
    _fonts: {

    },


    set_next: function () {

    },

    set_prev: function () {

    },

    set_bgcolor: function () {

    },

    get_bgcolor: function () {

    },

    set_font: function() {

    },

    get_font: function() {

    },

    load_config: function() {
        function load_config(){
            var article = $(".article");
            var chapter = $(".chapter-block");
            var conf = Cookies.get('config');
            console.log(conf);

            article.css("font-family", conf['font-family']);
            article.css('font-size', conf['font-size'] + 'px');
            chapter.css("background-color", conf['bgcolor']);
        }
    },

    save_config: function() {

    }


};