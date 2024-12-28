document.addEventListener("DOMContentLoaded", function () {
    // Basculer sur le formulaire de création
    document.getElementById("toggleCreate").addEventListener("click", function () {
        fetch('/events/create')
            .then(response => response.text())
            .then(data => {
                document.getElementById("dynamicContent").innerHTML = data;
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
                    document.getElementById("eventDate").value = data.date;
                    document.getElementById("eventDescription").value = data.description;
                })
                .catch(error => console.error("Erreur lors de la génération de l'événement :", error));
        }
    });

    // Soumettre le formulaire via AJAX
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "submitEvent") {
            const title = document.getElementById("eventTitle").value;
            const date = document.getElementById("eventDate").value;
            const description = document.getElementById("eventDescription").value;

            fetch("/api/demo/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ title, date, description })
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert("Événement créé avec succès !");
                        fetch(`/events/${result.event_id}`)
                            .then(response => response.text())
                            .then(data => {
                                document.getElementById("dynamicContent").innerHTML = data;
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
                })
                .catch(error => console.error("Erreur lors de l'affichage du projet :", error));
        }
    });

});