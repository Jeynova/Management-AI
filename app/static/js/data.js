let uploadedData = null;

function uploadFile() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];
    var formData = new FormData();
    formData.append('file', file);

    $.ajax({
        url: '/data/upload',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            $('#fileInfo').html('<p>' + response.message + '</p>');
            uploadedData = response.data;
        },
        error: function (response) {
            $('#fileInfo').html('<p>' + response.error + '</p>');
        }
    });
}

function sendMessage() {
    var message = $('#chatInput').val();
    $('#chatLog').append('<div><strong>You:</strong> ' + message + '</div>');
    $('#chatInput').val('');

    $.ajax({
        url: '/data/chat',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ message: message, data: uploadedData }),
        success: function (response) {
            $('#chatLog').append('<div><strong>ChatGPT:</strong> ' + response.response + '</div>');
            if (response.plot_url) {
                $('#chatLog').append('<div><img src="data:image/png;base64,' + response.plot_url + '"></div>');
            }
        }
    });
}