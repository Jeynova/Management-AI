let uploadedData = null;

// Fonction pour uploader un fichier
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
    $('#chatLog').append('<div><strong>Vous:</strong> ' + message + '</div>');
    $('#chatInput').val('');

    $.ajax({
        url: '/data/chat',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ message: message, data: uploadedData }),
        success: function (response) {
            const chatLog = $('#chatLog');

            // Vérifier si la réponse contient une erreur
            if (response.response.startsWith("Erreur")) {
                chatLog.append('<div><strong>Erreur:</strong> ' + response.response + '</div>');
                return;
            }

            // Vérifier si la réponse est du code Python
            if (response.is_code) {
                chatLog.append('<div><strong>Assistant:</strong> Code Python détecté pour un graphique.</div>');

                // Appeler une fonction pour exécuter le code Python côté backend
                $.ajax({
                    url: '/data/execute_code', // Endpoint dédié à l'exécution
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ code: response.response }),
                    success: function (plotResponse) {
                        if (plotResponse.plot_url) {
                            // Afficher le graphique généré
                            chatLog.append('<div><img src="' + plotResponse.plot_url + '"></div>');
                        } else {
                            chatLog.append('<div><strong>Erreur:</strong> Impossible de générer le graphique.</div>');
                        }
                    },
                    error: function () {
                        chatLog.append('<div><strong>Erreur:</strong> Une erreur est survenue lors de l\'exécution du code Python.</div>');
                    }
                });
            }
            // Sinon, gérer comme une réponse textuelle ou un tableau
            else {
                var converter = new showdown.Converter();

                // Vérifier si la réponse contient un tableau Markdown
                const markdownTablePattern = /\|.*\|\n\|[-:]+\|/;
                if (markdownTablePattern.test(response.response)) {
                    // Convertir le tableau Markdown en HTML
                    var html = converter.makeHtml(response.response);
                    chatLog.append('<div><strong>Assistant:</strong> ' + html + '</div>');
                }
                // Vérifier si la réponse est au format JSON (tableau structuré)
                else if (response.response.startsWith("[") || response.response.startsWith("{")) {
                    try {
                        const jsonData = JSON.parse(response.response);

                        // Générer un tableau HTML
                        const table = document.createElement("table");
                        table.border = "1";

                        // Ajouter les en-têtes
                        const headers = Object.keys(jsonData[0]);
                        const thead = document.createElement("thead");
                        const headerRow = document.createElement("tr");
                        headers.forEach(header => {
                            const th = document.createElement("th");
                            th.innerText = header;
                            headerRow.appendChild(th);
                        });
                        thead.appendChild(headerRow);
                        table.appendChild(thead);

                        // Ajouter les lignes de données
                        const tbody = document.createElement("tbody");
                        jsonData.forEach(row => {
                            const tr = document.createElement("tr");
                            headers.forEach(header => {
                                const td = document.createElement("td");
                                td.innerText = row[header];
                                tr.appendChild(td);
                            });
                            tbody.appendChild(tr);
                        });
                        table.appendChild(tbody);

                        // Ajouter le tableau au chatLog
                        chatLog.append('<div><strong>Assistant:</strong></div>');
                        chatLog.append(table);
                    } catch (e) {
                        chatLog.append('<div><strong>Assistant:</strong> ' + response.response + '</div>');
                    }
                }
                // Si pas de tableau, afficher la réponse normale
                else {
                    var html = converter.makeHtml(response.response);
                    chatLog.append('<div><strong>Assistant:</strong> ' + html + '</div>');
                }
            }

            // Afficher un graphique si inclus dans la réponse (base64 direct)
            if (response.plot_url) {
                chatLog.append('<div><img src="data:image/png;base64,' + response.plot_url + '"></div>');
            }
        },
        error: function () {
            $('#chatLog').append('<div><strong>Erreur:</strong> Une erreur est survenue lors de la requête au serveur.</div>');
        }
    });
}


