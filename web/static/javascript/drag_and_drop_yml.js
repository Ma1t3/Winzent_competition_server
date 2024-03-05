/**
 * Function for drag and drop and automatic loading of yml-Files into ERD Text field
 */
function addYamlDragAndDrop(hint_element_name) {
    $('#yamlEditor').on({
        input: function () {
            addPara("hide", "", hint_element_name);
        },
        dragover: function (ev) {
            ev.preventDefault();
        },
        drop: function (ev) {
            ev.preventDefault();

            const files = ev.originalEvent.dataTransfer.files;
            if (files.length === 1) {
                const file = files[0];
                console.log("File " + file.name + " dropped");
                if (file.name.slice(-4) === ".yml") {
                    const reader = new FileReader();
                    reader.addEventListener('load', function (e) {
                        const editor = ace.edit("yamlEditor");
                        editor.session.setValue(e.target.result);
                    });
                    reader.readAsText(file);
                    addPara("hide", "", hint_element_name);
                } else {
                    addPara("Please drop a YML file.", "red", hint_element_name);
                }
            } else {
                addPara("Please drop only one YML file.", "red", hint_element_name);
            }
        }
    })
}