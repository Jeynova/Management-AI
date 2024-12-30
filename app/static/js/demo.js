document.addEventListener("DOMContentLoaded", function () {
    // Basculer sur le formulaire de création
    initializeModalHandlers();
    // Appelez cette fonction après chaque chargement de contenu
    initializeFileUploadHandler();
    document.getElementById("toggleCreate").addEventListener("click", function () {
        fetch('/events/create')
            .then(response => response.text())
            .then(data => {
                document.getElementById("dynamicContent").innerHTML = data;
                initializeModalHandlers();
            })
            .catch(error => console.error("Erreur lors du chargement du formulaire :", error));
    });

    // Retourner à la liste des projets
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "backToProjects") {
            fetch('/events')
                .then(response => response.text())
                .then(data => {
                    document.getElementById("dynamicContent").innerHTML = data;
                    initializeModalHandlers();
                    initializeCarousel()
                    // Réinitialiser le carrousel   
                })
                .catch(error => console.error("Erreur lors du retour à la liste :", error));
        }
    });

    // Activer les onglets Bootstrap
    const tabLinks = document.querySelectorAll('#eventTabs .nav-link');
    tabLinks.forEach((tab) => {
        tab.addEventListener('click', (e) => {
            const targetTab = e.target.getAttribute('href');
            const targetPane = document.querySelector(targetTab);
            const allPanes = document.querySelectorAll('.tab-pane');
            allPanes.forEach((pane) => pane.classList.remove('show', 'active'));
            targetPane.classList.add('show', 'active');
        });
    });

    // Afficher un projet spécifique
    document.addEventListener("click", function (e) {
        if (e.target && e.target.classList.contains("view-project")) {
            const eventId = e.target.getAttribute("data-event-id");
            fetch(`/events/${eventId}`)
                .then(response => response.text())
                .then(data => {
                    document.getElementById("dynamicContent").innerHTML = data;
                    initializeModalHandlers();
                    initializeFileUploadHandler();
                })
                .catch(error => console.error("Erreur lors de l'affichage du projet :", error));
        }
    });

    // Remplir les champs avec ChatGPT
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "generateEvent") {
            fetch("/api/demo/nouveau")
                .then(response => response.json())
                .then(data => {
                    document.getElementById("eventTitle").value = data.title;
                    initializeModalHandlers();
                    initializeFileUploadHandler();

                    // Convertir la date au format attendu par datetime-local
                    const date = new Date(data.date); // Assurez-vous que data.date est parsable
                    const formattedDate = date.toISOString().slice(0, 16); // Format : YYYY-MM-DDTHH:mm
                    document.getElementById("eventDate").value = formattedDate;

                    document.getElementById("eventDescription").value = data.description;
                })
                .catch(error => console.error("Erreur lors de la génération de l'événement :", error));
        }
    });

    // Soumettre le formulaire via AJAX
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "submitEvent") {
            const title = document.getElementById("eventTitle").value.trim();
            const date = document.getElementById("eventDate").value.trim(); // Gère uniquement la date
            const description = document.getElementById("eventDescription").value.trim();

            if (!title || !date || !description) {
                alert("Veuillez remplir tous les champs requis.");
                return;
            }

            fetch("/api/demo/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ title, date, description }) // Pas besoin de convertir l'heure ici
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert("Événement créé avec succès !");
                        fetch(`/events/${result.event_id}`)
                            .then(response => response.text())
                            .then(data => {
                                document.getElementById("dynamicContent").innerHTML = data;
                                initializeModalHandlers();
                                initializeFileUploadHandler();
                            });
                    } else {
                        alert("Erreur : " + result.message);
                    }
                })
                .catch(error => console.error("Erreur lors de la soumission :", error));
        }
    });

    function initializeCarousel() {
        let items = document.querySelectorAll('.carousel .carousel-item');
        const totalItems = items.length;
        const minPerSlide = 4;

        // Désactiver le clonage si le nombre d'éléments est inférieur au minimum requis
        if (totalItems <= minPerSlide) return;

        items.forEach((el) => {
            let next = el.nextElementSibling;
            for (let i = 1; i < minPerSlide; i++) {
                if (!next) {
                    // wrap carousel by using first child
                    next = items[0];
                }
                let cloneChild = next.cloneNode(true);
                el.appendChild(cloneChild.children[0]);
                next = next.nextElementSibling;
            }
        });
    }
    initializeCarousel();
    initializeFileUploadHandler();

    // Écouteur pour générer l'événement complet (assurez-vous que le modal est chargé)
    document.addEventListener("click", function (event) {
        if (event.target && event.target.id === "generateCompleteEvent") {
        // Afficher la modal
        const modal = new bootstrap.Modal(document.getElementById("generationModal"));
        modal.show();

        // Réinitialiser les états
        const stepsList = document.getElementById("generationSteps");
        const spinner = document.getElementById("loadingSpinner");
        stepsList.style.display = "none";
        spinner.style.display = "flex";
        stepsList.innerHTML = ""; // Réinitialiser la liste des étapes

        // Effectuer l'appel pour générer les données
        fetch("/api/generate_full_event", { method: "POST" })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                spinner.style.display = "none";
                stepsList.style.display = "block";

                if (!data.steps || data.steps.length === 0) {
                    const listItem = document.createElement("li");
                    listItem.className = "list-group-item list-group-item-warning";
                    listItem.textContent = "Aucune étape n'a été renvoyée par le serveur.";
                    stepsList.appendChild(listItem);
                    return;
                }

                // Ajouter les étapes à la liste
                data.steps.forEach((step) => {
                    const listItem = document.createElement("li");
                    listItem.className = `list-group-item ${step.success ? "list-group-item-success" : "list-group-item-danger"}`;
                    listItem.textContent = step.message;
                    stepsList.appendChild(listItem);
                });
            })
            .catch((error) => {
                spinner.style.display = "none";
                stepsList.style.display = "block";

                const listItem = document.createElement("li");
                listItem.className = "list-group-item list-group-item-danger";
                listItem.textContent = `Erreur : ${error.message}`;
                stepsList.appendChild(listItem);
            });
        }
    });
    // Écouteur pour afficher un projet spécifique
    document.addEventListener("click", function (e) {
        if (e.target && e.target.classList.contains("view-project")) {
            const eventId = e.target.getAttribute("data-event-id");
            fetch(`/events/${eventId}`)
                .then(response => response.text())
                .then(data => {
                    document.getElementById("dynamicContent").innerHTML = data;
                    initializeModalHandlers();
                    initializeFileUploadHandler();
                })
                .catch(error => console.error("Erreur lors de l'affichage du projet :", error));
        }
    });

    // Gestion de la modal
    const modal = document.getElementById("contentModal");
    const modalTitle = modal.querySelector(".modal-title");
    const modalContent = modal.querySelector("#modalContent");

    modal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const title = button.getAttribute("data-title");
        const content = button.getAttribute("data-content");
        const imageUrl = button.getAttribute("data-image");

        console.log(`Titre : ${title}, Contenu : ${content}, Image : ${imageUrl}`);

        modalTitle.textContent = title || "Titre par défaut";
        modalContent.innerHTML = `
            ${imageUrl ? `<img src="${imageUrl}" alt="${title}" class="img-fluid mb-3">` : ""}
            <p>${content || "Aucun contenu disponible."}</p>
        `;
    });

        document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "uploadFileButton"){
        const fileInput = document.getElementById("fileInput");
        if (!fileInput.files.length) {
            alert("Veuillez sélectionner un fichier.");
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("file", file);

        fetch("/api/analyze", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    alert("Erreur : " + data.error);
                } else {
                    const resultDiv = document.getElementById("analysisResult");
                    resultDiv.innerHTML = `
                        <h4>Analyse des données</h4>
                        <p><strong>Colonnes :</strong> ${data.analysis.columns.join(", ")}</p>
                        <p><strong>Total des lignes :</strong> ${data.analysis.total_rows}</p>
                        <p><strong>Valeurs manquantes :</strong> ${JSON.stringify(data.analysis.missing_values)}</p>
                        <h5>Résumé statistique</h5>
                        <pre>${JSON.stringify(data.analysis.summary, null, 2)}</pre>
                    `;
                }
            })
            .catch((error) => {
                console.error("Erreur :", error);
                alert("Erreur lors de l'analyse du fichier.");
            });
        }
    });
    function initializeModalHandlers() {
        const modal = document.getElementById("contentModal");
        if (!modal) {
            console.error("La modal n'a pas été trouvée dans le DOM.");
            return;
        }

        const modalTitle = modal.querySelector(".modal-title");
        const modalContent = modal.querySelector("#modalContent");

        document.querySelectorAll('[data-bs-toggle="modal"]').forEach((button) => {
            button.addEventListener("click", function () {
                const title = this.getAttribute("data-title") || "Détails";
                const content = this.getAttribute("data-content") || "Contenu non disponible.";
                const imageUrl = this.getAttribute("data-image");

                modalTitle.textContent = title;
                modalContent.innerHTML = `
                ${imageUrl ? `<img src="${imageUrl}" alt="${title}" class="img-fluid mb-3">` : ""}
                <p>${content}</p>
            `;
            });
        });
        document.addEventListener("click", function (e) {
            if (e.target && e.target.id === "analyzeWithGPTButton") {

                const fileInput = document.getElementById("fileInput");
                if (!fileInput.files.length) {
                    alert("Veuillez sélectionner un fichier.");
                    return;
                }

                const file = fileInput.files[0];
                const formData = new FormData();
                formData.append("file", file);

                fetch("/api/analyze_file_with_gpt", {
                    method: "POST",
                    body: formData,
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.error) {
                            alert("Erreur : " + data.error);
                        } else {
                            const resultDiv = document.getElementById("analysisResult");
                            resultDiv.innerHTML = `
                        <h4>Analyse des données avec GPT</h4>
                        <pre>${data.gpt_analysis}</pre>
                    `;
                        }
                    })
                    .catch((error) => {
                        console.error("Erreur :", error);
                        alert("Erreur lors de l'analyse avec GPT.");
                    });
            }
        });
    }

    function initializeFileUploadHandler() {
        const uploadButton = document.getElementById("uploadFileButton");
        if (!uploadButton) {
            console.error("Bouton 'uploadFileButton' introuvable !");
            return;
        }

        uploadButton.addEventListener("click", function () {
            const fileInput = document.getElementById("fileInput");
            if (!fileInput.files.length) {
                alert("Veuillez sélectionner un fichier.");
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append("file", file);

            fetch("/api/analyze_file", {
                method: "POST",
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.error) {
                        alert("Erreur : " + data.error);
                    } else if (!data.analysis || !data.analysis.summary) {
                        alert("Données incomplètes reçues.");
                    } else {
                        const resultDiv = document.getElementById("analysisResult");
                        let tableHTML = `
            <h4>Analyse des données</h4>
            <p><strong>Colonnes :</strong> ${data.analysis.columns.join(", ")}</p>
            <p><strong>Total des lignes :</strong> ${data.analysis.total_rows}</p>
            <p><strong>Valeurs manquantes :</strong></p>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Colonne</th>
                        <th>Valeurs Manquantes</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(data.analysis.missing_values).map(
                            ([col, val]) => `<tr><td>${col}</td><td>${val}</td></tr>`
                        ).join("")}
                </tbody>
            </table>
            <h5>Résumé Statistique</h5>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Colonne</th>
                        ${Object.keys(data.analysis.summary).map(key => `<th>${key}</th>`).join("")}
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(data.analysis.summary).map(
                            ([col, stats]) => `
                            <tr>
                                <td>${col}</td>
                                ${Object.values(stats).map(val => `<td>${val || "N/A"}</td>`).join("")}
                            </tr>
                        `
                        ).join("")}
                </tbody>
            </table>
        `;
                        resultDiv.innerHTML = tableHTML;
                    }
                })
                .catch((error) => {
                    console.error("Erreur :", error);
                    alert("Erreur lors de l'analyse du fichier.");
                });
        });
    }

});

