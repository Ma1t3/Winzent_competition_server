/**
 * Function for using the ACE editor for editing YML files
 */
function showCodeEditor(textarea, form) {
    // add div for ace editor
    textarea.after("<div id='yamlEditor'></div>");

    // hide textarea
    textarea.hide();

    // create ace editor and set theme and mode
    const editor = ace.edit("yamlEditor");
    editor.setTheme("ace/theme/chrome");
    editor.session.setMode("ace/mode/yaml");
    editor.setShowPrintMargin(false);
    editor.session.setUseSoftTabs(true);

    // set ace editor value to textarea value
    editor.session.setValue(textarea.val());

    // set ace editor value to textarea value on submit
    form.on('submit', function (delta) {
        textarea.val(editor.getValue())
    });
}