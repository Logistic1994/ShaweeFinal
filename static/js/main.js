$(document).ready(function () {

var uid_prefix = "images/upload_process";
var global_style_name = null;
var global_uid = null;
var global_styled_uid = null;
var global_orig_image = null;
var global_styled_image = null;
var global_orig_image_data = null;
var global_styled_image_data = null;
var global_transparency = null;


function IsImageOk(img) {
    if (!img.complete) {
        return false;
    }
    if (typeof img.naturalWidth !== "undefined" && img.naturalWidth === 0) {
        return false;
    }
    return true;
}

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
                    }
                }
            }
        }
        if (uid === null) {
            console.log(data);
        } else {
            console.log(uid);
            if (global_uid == uid) {
                console.log("Same as before uid.");
                return;
            }
            global_uid = uid;
            clear_all_image();
            $("#ori_img").attr({"src": uid_prefix + "/" + uid});
            global_orig_image = load_image(uid_prefix + "/" + uid, function () {
                console.log("Global orig image loaded.");
            });
            style(uid);
        }
    },
    fail: function (e, data) {
        console.log("Fail");
    },
    change: function(e, data) {
        console.log("Change");
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

$('input:radio[name=style_option]').click(function () {
    if (global_uid !== null) {
        style(global_uid);
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

function style(uid) {
    console.log("Do style.")
    // 获取风格名
    var style_name = $('input:radio[name=style_option]:checked').val();
    if (style_name == global_style_name) {
        return;
    }
    global_style_name = style_name;
    console.log(style_name);
    // 获取风格图
    $.ajax({
        "url": "style",
        "type": "GET",
        "data": {
            "style_name": style_name,
            "uid": uid
        },
        "dataType": "json",
        "success": function(data) {
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
            } else {
                console.log("Failed.");
            }
        }
    });
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

function load_image(img_src, onload) {
    var img = new Image();
    img.onload = onload;
    img.src = img_src;
    return img;
}

function load_image_data() {
    console.log("Load image data.");
    var width = global_orig_image.width;
    var height = global_orig_image.height;
    var canvas = document.getElementById("style_show");
    var context = canvas.getContext("2d");
    canvas.width = width;
    canvas.height = height;
    context.drawImage(global_orig_image, 0, 0);
    global_orig_image_data = context.getImageData(0, 0, width, height).data;
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(global_styled_image, 0, 0);
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

    var width = global_orig_image.width;
    var height = global_orig_image.height;
    var pixels = 4 * width * height;

    var canvas = document.getElementById("style_show");
    var context = canvas.getContext("2d");
    context.drawImage(global_orig_image, 0, 0);
    var final_image = context.getImageData(0, 0, width, height);
    var final_image_data = final_image.data;

    while (pixels--) {
        final_image_data[pixels] = global_orig_image_data[pixels] * (1.0 - transparency)
                                + global_styled_image_data[pixels] * transparency;
    }
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.putImageData(final_image, 0, 0);
}
})








