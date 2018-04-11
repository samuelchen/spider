/**
 * Created by Samuel on 4/5/2018.
 */

if (!window['share.js']) {

    /* weiboShare */
    function weibo_share() {
        console.log('- Weibo share script installed.');
        var site_info = get_site_info();
        var site = site_info[0];
        var domain = site_info[1];

        var wb_share_btn = $('[data-toggle="share-weibo"]');
        var wb_url = document.URL;
        var idx = wb_url.indexOf("#");
        if (idx > 0) wb_url = wb_url.slice(0, idx);
        var wb_appkey = "";
        var wb_title = "快来「" + site + "」 " + domain + "看";
        var wb_ralateUid = "1641558241";
        var wb_pic = "";
        var wb_language = "zh_cn";


        wb_share_btn.click(function () {
            var lc = $(this).data('last-chapter');
            var c = $(this).data('chapter');
            var ext_title = "「" + $(this).data('author') + "」写的《" + $(this).data('novel-name') + "》! ";

            if (c) {
                ext_title += c + '这章写的挺有意思~';
            } else if (lc) {
                ext_title += '已更新到 ' + lc;
            }
            window.open("http://service.weibo.com/share/share.php?url=" + wb_url
            + "&appkey=" + wb_appkey + "&title=" + wb_title + ext_title + "&pic=" + wb_pic + "&ralateUid=" + wb_ralateUid
            + "&language=" + wb_language + "");
        });
    }

    $(document).ready(function () {
        console.log('Share button scripts installed.')
        weibo_share();
    });

    window['share.js'] = true;
}
