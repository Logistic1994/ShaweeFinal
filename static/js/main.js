// 全局变量
var uid_prefix = "images/upload_process";
var global_style_name = null;
var global_uid = null;
var global_styled_uid = null;
var global_orig_image = null;
var global_styled_image = null;
var global_orig_image_data = null;
var global_styled_image_data = null;
var global_transparency = null;
var global_last_command = null;

$(document).ready(function () {

// 提醒框
function notify_success(msg) {
    $("#warning-alert").hide();
    $("#info-alert").hide();
    $("#success-alert > span").text(msg);
    $("#success-alert").alert();
    $("#success-alert").fadeTo(1300, 500).slideUp(500, function(){
        $("#success-alert").slideUp(500);
    });   
}
function notify_warning(msg) {
    $("#success-alert").hide();
    $("#info-alert").hide();
    $("#warning-alert > span").text(msg);
    $("#warning-alert").alert();
    $("#warning-alert").fadeTo(1300, 500).slideUp(500, function(){
        $("#warning-alert").slideUp(500);
    });   
}
function notify_info(msg) {
    $("#success-alert").hide();
    $("#warning-alert").hide();
    $("#info_msg").text("  " + msg);
    $("#info-alert").show();
    $("#info-alert").fadeTo(1300, 500);
}
function dismiss_info() {
    $("#info-alert").hide();
}

// 禁用与启用
function disable_style_operation() {
    $('input:radio[name=style_option]').each(function(index){
        $(this)[0].disabled = true;
    });
    $('#upload_image')[0].disabled = true;
    $('#load_style_btn')[0].disabled = true;
    console.log('disabled');
}
function enable_style_operation() {
    $('input:radio[name=style_option]').each(function(index){
        $(this)[0].disabled = false;
    });
    $('#upload_image')[0].disabled = false;
    $('#load_style_btn')[0].disabled = false;
    console.log('enabled');
}

// 获取style列表
function get_style_list() {
    disable_style_operation();
    $('#load_style_btn').html('<span class="glyphicon glyphicon-refresh spinning"></span>加载中');
    $.ajax({
        url: '/style_list',
        type: 'GET',
        dataType: 'json'
    })
    .done(function(data) {
        var suc = false;
        if ("status" in data) {
            var status = data["status"];
            if (status == 0) {
                if ("styles" in data) {
                    var styles = data["styles"];
                    show_style_list(styles);
                    suc = true;
                    notify_success("获取风格列表成功!")
                }
            }
        }
        if (!suc) {
            notify_warning("获取风格列表失败，请刷新或者重启服务!");
        }
        enable_style_operation();
        $('#load_style_btn').text('加载');
    })
    .fail(function() {
        notify_warning("获取风格列表失败，请刷新或者重启服务!");
        enable_style_operation();
        $('#load_style_btn').text('加载');
    });
    
}

function do_style(uid) {
    console.log("Do style.")
    // 获取风格名
    var style_name = $('input:radio[name=style_option]:checked').val();
    console.log(style_name);
    var command = uid + ":" + style_name;
    if (global_last_command === command) {
        console.log("No need to style");
        return;
    }
    global_last_command = command;
    global_style_name = style_name;
    disable_style_operation();
    // 获取风格图
    notify_info("进行风格化...");
    $.ajax({
        "url": "style",
        "type": "GET",
        "data": {
            "style_name": style_name,
            "uid": uid
        },
        "dataType": "json",
        "success": function(data) {
            dismiss_info();
            console.log(data);
            if ("status" in data && 0 == data["status"]) {
                var styled_uid = data["styled_uid"];
                if (styled_uid == global_styled_uid) {
                    console.log("Same as before style uid.");
                    return;
                }
                global_styled_uid = styled_uid;
                clear_styled_image();
                $("#styled_img").attr({"src": uid_prefix + "/" + styled_uid});
                global_styled_image = load_image(uid_prefix + "/" + styled_uid, function () {
                    console.log("Global styled image loaded.");
                    load_image_data();
                    $('#slider').val(100);
                    draw(1.0);
                });
                var duration = Number(data["duration"]);
                $("#duration").text(duration.toFixed(2) + "s");
                notify_success("风格化成功!");
            } else {
                console.log("Failed.");
                notify_warning("风格化失败!");
            }
            enable_style_operation();
        },
        "failure": function () {
            dismiss_info();
            notify_warning("风格化失败!");
            enable_style_operation();
        }
    });
}

$('#load_style_btn').click(function() {
    get_style_list();
});

function show_style_list(styles) {
    $("#styles").empty();
    var i = 0;
    styles.forEach(function (style) {
        var $example = $('.style_tmpl:first').clone();
        if (i == 0) {
            $example.find('input').attr({'value': style['name'], 'checked': ''});
        } else {
            $example.find('input').attr({'value': style['name']});
        }
        i = i + 1;
        $example.find('img').attr({'src': style['meta_image']});
        $example.find('label').text(style['chinese_name']);
        $example.appendTo('#styles');
        $example.removeClass('style_tmpl');
        $example.show();
        $example.click(function () {
            console.log("Option clicked.");
            if (global_uid !== null) {
                do_style(global_uid);
            }
        }); 
    });
}

get_style_list();

$('#upload_image').fileupload({
    url: "/upload_image",
    dataType: "json",
    done: function (e, data) {
        var uid = null;
        if ("result" in data) {
            var result = data["result"];
            if ("status" in result) {
                var status = result["status"];
                if (status == 0) {
                    if ("uid" in result) {
                        uid = result["uid"];
                        notify_success("上传图片成功!");
                    }
                }
            }
        }
        
        if (uid === null) {
            console.log(data);
            notify_warning("上传图片失败!");
            enable_style_operation();
        } else {
            console.log(uid);
            if (global_uid == uid) {
                console.log("Same as before uid.");
                do_style(uid);
                return;
            }
            global_uid = uid;
            clear_all_image();
            $("#ori_img").attr({"src": uid_prefix + "/" + uid});
            global_orig_image = load_image(uid_prefix + "/" + uid, function () {
                console.log("Global orig image loaded.");
                do_style(uid);
            });
            
        }

    },
    fail: function (e, data) {
        console.log("Fail");
        notify_warning("上传图片失败!");
        enable_style_operation();
    },
    change: function(e, data) {
        console.log("Change");
        notify_info("上传图片...");
    },
    progressall: function (e, data) {
        console.log(data);
        var progress = parseInt(data.loaded / data.total * 100, 10);
        $('#progress .bar').css(
            'width',
            progress + '%'
        );
    }
});


$("#slider").on('input', function (e) {
    $('#range').text($('#slider').val());
});

$("#slider").on('change', function (e) {
    var v = $('#slider').val();
    if (v == global_transparency) {
        return;
    }
    global_transparency = v;
    draw(global_transparency / 100.0);
});



// 绘图相关
function is_image_ok(img) {
    if (!img.complete) {
        return false;
    }
    if (typeof img.naturalWidth !== "undefined" && img.naturalWidth === 0) {
        return false;
    }
    return true;
}
function clear_all_image() {
    global_orig_image = null;
    global_styled_image = null;
    global_orig_image_data = null;
    global_styled_image_data = null;
}
function clear_styled_image() {
    global_styled_image = null;
    global_styled_image_data = null;
}
// 回调接口
function load_image(img_src, onload) {
    var img = new Image();
    img.crossOrigin = "anonymous";
    img.src = img_src;
    img.onload = onload;
    return img;
}
// 加载并计算出应该显示的风格图
function load_image_data() {
    console.log("Load image data.");
    // 直接从前面Image处获取缩放过的图片大小
    var width = $("#ori_img")[0].width;
    var height = $("#ori_img")[0].height;
    var canvas = document.getElementById("style_show");
    var context = canvas.getContext("2d");
    canvas.width = width;
    canvas.height = height;
    // 连续draw两次，把中间结果保存下来
    context.drawImage(global_orig_image, 0, 0, width, height);
    global_orig_image_data = context.getImageData(0, 0, width, height).data;
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(global_styled_image, 0, 0, width, height);
    global_styled_image_data = context.getImageData(0, 0, width, height).data;
    context.clearRect(0, 0, canvas.width, canvas.height);
}

function draw(transparency) {
    if (transparency < 0.0) {
        transparency = 0.0;
    }
    if (transparency > 1.0) {
        transparency = 1.0;
    }
    var width = $("#ori_img")[0].width;
    var height = $("#ori_img")[0].height;
    var pixels = 4 * width * height;
    var canvas = document.getElementById("style_show");
    var context = canvas.getContext("2d");
    context.drawImage(global_orig_image, 0, 0, width, height);
    var final_image = context.getImageData(0, 0, width, height);
    var final_image_data = final_image.data;
    while (pixels--) {
        final_image_data[pixels] = global_orig_image_data[pixels] * (1.0 - transparency)
                                + global_styled_image_data[pixels] * transparency;
    }
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.putImageData(final_image, 0, 0);
}

function init_draw() {
    global_orig_image = load_image($("#ori_img")[0].src, function () {
        console.log("Global orig image loaded.");
        console.log(is_image_ok(global_orig_image));
        global_styled_image = load_image($("#styled_img")[0].src, function () {
            console.log("Global styled image loaded.");
            console.log(is_image_ok(global_styled_image))
            load_image_data();
            $('#slider').val(100);
            draw(1.0);
        });
    });
}

init_draw();
})








