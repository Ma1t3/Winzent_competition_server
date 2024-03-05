/**
 * Function to export the experiment results asynchronously
 */
$(document).ready(
    $("#export_data").click(
        async function get_results() {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            var exp_id = $(this).attr("data-value")
            console.log(exp_id)
            await $.ajax('/experiment/generate_export/' + exp_id, {
                    type: 'POST',
                    headers: {'X-CSRFToken': csrftoken},
                    success: function (response) {
                        if (response == "Error!") {
                            alert("Sth. went wrong!")
                        } else if (response == "Permission denied!") {
                            alert("Permission denied!")
                        }
                        window.location = "/experiment/export_data/" + exp_id
                    },
                }
            )
        }))

$(document).ready(
    $("#export_data").click(
        async function information() {
            alert("Please wait and do not leave this page until the download starts! " +
                "This can take some time, depending on the size of the experiment.")

        }
    ))