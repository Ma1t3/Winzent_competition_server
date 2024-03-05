/**
 * Function for displaying error messages
 */
function addPara(text, color, hintElementName) {
    let span = document.getElementById("id_file_alert");
    if (span == null) {
        span = document.createElement("span");
        span.id = "id_file_alert";
        span.appendChild(document.createElement("br"));

        let strong = document.createElement("strong");
        strong.id = "id_file_alert_text";
        strong.classList.add("invalid-feedback");
        strong.style.display = "inline";

        span.appendChild(strong);
        document.getElementById(hintElementName).appendChild(span);
    }

    if (text !== "hide") {
        let strong = document.getElementById("id_file_alert_text");
        strong.textContent = text;
        span.hidden = false;
        strong.style.color = color;
    } else {
        span.hidden = true;
    }

}