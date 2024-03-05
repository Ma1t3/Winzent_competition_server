/**
 * Function for showing the live log on the experiment page.
 */
function activateLiveLogOnLogfileTabShown(liveLogUrl) {
    // if live-log is available: if logfile tab gets activated, start live-log
    if ($("#liveLog").length) {
        const liveLogTab = document.getElementById('nav-logfile-tab');
        liveLogTab.addEventListener('shown.bs.tab', function (e) {
            startLiveLog(liveLogUrl);
        });
    }
}

function startLiveLog(liveLogUrl) {
    // Live-Log
    if (typeof (EventSource) !== "undefined") {
        const eventSource = new EventSource(liveLogUrl);
        $("#liveLog").text("...\n");
        eventSource.addEventListener("message", event => {
            // on message from server: add new line to live log
            $("#liveLog").append(event.data + "\n");
        });
        eventSource.addEventListener("error", event => {
            // on error (e.g. if live log is ended because experiment is finished): close event source and show finished message
            $('#liveLog').append("Live-Log ended." + "\n");
            // reload page after 2 seconds
            eventSource.close();
            setTimeout(() => {
                location.reload();
            }, 5000);
        });
    } else {
        $('#liveLog').text("Live-Log is not supported in your browser");
    }
}

