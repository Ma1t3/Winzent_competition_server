/**
 * Function for keeping the current tab active when reloading the page.
 */
function preserveActiveTabOnReload() {
    saveCurrentTabOnTabShown();
    openSavedTabOnReload();
}

function saveCurrentTabOnTabShown() {
    // add # to url on tab shown
    const tabElements = document.querySelectorAll('button[data-bs-toggle="tab"]')
    for (let elem of tabElements) {
        elem.addEventListener('shown.bs.tab', function (event) {
            // for each tab, on click, add # to url
            target = event.target.id.substring(4);
            window.location.hash = target
        })
    }
}

function openSavedTabOnReload() {
    // activate correct tab on reload
    const tab = window.location.hash.substring(1);
    // if url has #nav-..., activate corresponding tab
    if (tab && tab.endsWith("-tab")) {
        const triggerEl = document.getElementById('nav-' + tab);
        new bootstrap.Tab(triggerEl).show()
    }
}

