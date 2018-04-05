/**
 * Created by wchen8 on 4/5/2018.
 */

/* weiboShare */
function weibo_share(title, msg, site, domain) {
    var site_info = get_site_info();
    if (!site) site = site_info[0];
    if (!domain) domain = site_info[1];

    var wb_shareBtn = $('[data-toggle="share-weibo"]');
    var wb_url = document.URL;
    var wb_appkey = "";
    var wb_title = "【" + site + " " + domain + "】";
    var wb_ralateUid = "1641558241";
    var wb_pic = "";
    var wb_language = "zh_cn";

    wb_shareBtn.attr("href", "http://service.weibo.com/share/share.php?url=" + wb_url
        + "&appkey=" + wb_appkey + "&title=" + wb_title + "&pic=" + wb_pic + "&ralateUid=" + wb_ralateUid
        + "&language=" + wb_language + "");
}

$(document).ready(function(){
    weibo_share();
});
