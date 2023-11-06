var alertMessage = $('#alert-message');
var progressBar = $('#progress-bar')

function closeAlert() {
    alertMessage.alert('close')
}

var timer = setInterval(function() {
    var currentWidth = progressBar.width() / progressBar.parent().width() * 100;
    var newWidth = currentWidth - 2
    progressBar.width(newWidth)
    if (currentWidth <= 0) {
        clearInterval(timer);
        closeAlert();
    }
}, 1)