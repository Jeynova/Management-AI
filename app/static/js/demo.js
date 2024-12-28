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
        items.forEach((el) => {
            const minPerSlide = 4;
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
    initializeCarousel()

    // Écouteur pour générer l'événement complet (assurez-vous que le modal est chargé)
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "generateCompleteEvent") {
            const modalElement = document.getElementById("generationModal");
            if (!modalElement) {
                console.error("L'élément avec l'ID 'generationModal' est introuvable.");
                return;
            }

            const modal = new bootstrap.Modal(modalElement);
            modal.show();

            const stepsList = document.getElementById("generationSteps");
            if (!stepsList) {
                console.error("L'élément avec l'ID 'generationSteps' est introuvable.");
                return;
            }

            stepsList.innerHTML = ""; // Réinitialiser la liste

            const addStep = (message, isSuccess = true) => {
                const listItem = document.createElement("li");
                listItem.className = `list-group-item ${isSuccess ? "list-group-item-success" : "list-group-item-danger"}`;
                listItem.textContent = message;
                stepsList.appendChild(listItem);
            };

            fetch("/api/generate_full_event", { method: "POST" })
                .then((response) => response.json())
                .then((data) => {
                    data.steps.forEach((step) => addStep(step.message, step.success));
                })
                .catch((error) => {
                    addStep(`Erreur lors de la génération : ${error.message}`, false);
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