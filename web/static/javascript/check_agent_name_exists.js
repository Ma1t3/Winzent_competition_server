/**
 * Ajax call to check if agent with given name already exists
 */
let timer = null;
$("#id_name").on('input', function () {
    console.log("onInput triggered")
    clearTimeout(timer);
    timer = setTimeout(checkAgentNameExists.bind(null, $(this).val()), 500);
});

function checkAgentNameExists(inputText) {
    console.log("checkAgentName triggered")
    $.ajax({
        url: 'ajax/check_agent_name_exists',
        data: {
            'agent_name': inputText
        },
        dataType: 'json',
        success: function (data) {
            let name_input = document.getElementById("id_name");
            if (data.agent_name_exists) {
                name_input.classList.add("is-invalid");

                let error_message = document.getElementById("error_1_id_name");
                if (!error_message) {
                    let error_paragraph = document.createElement("p");
                    error_paragraph.classList.add("invalid-feedback");
                    error_paragraph.setAttribute("id", "error_1_id_name");

                    let error_strong = document.createElement("strong");
                    error_strong.textContent = "Agent with this Name already exists."

                    error_paragraph.append(error_strong);
                    name_input.parentElement.appendChild(error_paragraph);
                }
            } else {
                name_input.classList.remove("is-invalid");
            }
        }
    })
}