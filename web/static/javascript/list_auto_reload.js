/**
 * Function for automatically update the experiment and competition list.
 */
let timer;
let reloadURL;
let reloadList;
function activateAutoreload(reloadURLParam, reloadListParam) {
    reloadURL = reloadURLParam;
    reloadList = reloadListParam;
    timer = setTimeout(reloadTimeout.bind(null), 10000);
}

function reloadTimeout() {
    console.log("Autoreload triggered")

    let checkBox = document.getElementById("checkbox_autoreload");

    if (checkBox.checked === true) {
        console.log("And the experiment list will be reloaded.")
        $.ajax({
            type: 'GET',
            url: reloadURL,
            dataType: 'html',
            success: function (data) {
                $(reloadList).html(data);
                timer = setTimeout(reloadTimeout.bind(null), 10000);
            }
        })
    }
}

function changeAutoreload(setListAutoreloadURL, token) {
    clearTimeout(timer)
    let checkBox = document.getElementById("checkbox_autoreload");

    if (checkBox.checked === true) {
        timer = setTimeout(reloadTimeout.bind(null), 10000);
    }

    $.ajax({
        type: 'POST',
        url: setListAutoreloadURL,
        data: {
            autoreload: checkBox.checked,
            csrfmiddlewaretoken: token
        },
        dataType: 'json',
        success: function (data) {
        }
    })
}