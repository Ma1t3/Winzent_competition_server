/**
 * Function to verify the file size of the file to be uploaded
 */

let maxFileSize = 50;
let allowedFileTypes = ["zip"];
let megabyteToByteCoefficient = 1048576;

$(document).ready(function () {
    $('#id_file').on('change', function () {
        // (Can't use `typeof FileReader === "function"` because apparently it
        // comes back as "object" on some browsers. So just see if it's there
        // at all.)
        if (!window.FileReader) { // This is VERY unlikely, browser support is near-universal
            console.log("The file API isn't supported on this browser yet.");
            return;
        }

        const input = document.getElementById('id_file');
        if (input.files[0] == null) { // This is VERY unlikely, browser support is near-universal
            addPara("hide", "", "hint_id_file")
        } else if (!allowedFileTypes.includes(input.files[0].name.split('.')[input.files[0].name.split('.').length - 1])) {
            addPara("Please upload your agent in a ." + allowedFileTypes.values().next().value + " format!",
                "red", "hint_id_file");
            document.getElementById("upload_button").disabled = true
        } else if (input.files[0].size > maxFileSize * megabyteToByteCoefficient) {
            addPara("Agent file must be < " + maxFileSize + "MB! Current file is "
                + Math.round(input.files[0].size / megabyteToByteCoefficient) + "MB.",
                "red", "hint_id_file");
            document.getElementById("upload_button").disabled = true
        } else if (allowedFileTypes.includes(input.files[0].name.split('.')[input.files[0].name.split('.').length - 1])) {
            addPara("File is valid for upload!", "green", "hint_id_file");
            console.log("check")
            document.getElementById("upload_button").disabled = false
        } else {
            addPara("hide", "", "hint_id_file")
        }
    });
});

