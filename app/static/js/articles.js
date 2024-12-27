document.addEventListener("DOMContentLoaded", function () {
    const addArticleForm = document.querySelector("#addArticleForm");
    const generatedArticleContent = document.getElementById("generatedArticleContent");
    const generatedArticleTitle = document.getElementById("generatedArticleTitle");
    const generatedArticleText = document.getElementById("generatedArticleText");
    const articleFormFields = document.getElementById("articleFormFields");
    const articlesTableBody = document.querySelector("table tbody"); // Sélecteur pour le tableau des articles
    const addArticleModalElement = document.getElementById("addArticleModal");
    const addArticleModal = new bootstrap.Modal(addArticleModalElement);

    addArticleForm.addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent page reload

        const formData = new FormData(addArticleForm);
        const articleData = {
            event_id: document.getElementById("event_id").value,
            conference_id: formData.get("conference_id"),
        };

        fetch(`/api/articles`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(articleData),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Erreur lors de la création de l'article.");
                }
                return response.json();
            })
            .then((data) => {
                console.log("Article Data:", data); // Debugging log

                // Update modal with the generated article
                if (data.article && data.article.content) {
                    generatedArticleTitle.textContent = data.article.title;
                    generatedArticleText.textContent = data.article.content;

                    // Add the article to the table
                    addArticleToTable(data.article);

                    // Show the generated article and hide the form fields
                    articleFormFields.style.display = "none";
                    generatedArticleContent.style.display = "block";
                } else {
                    throw new Error("Le contenu de l'article est manquant.");
                }
            })
            .catch((error) => {
                console.error("Erreur dans la création de l'article:", error);
                alert(error.message || "Une erreur inconnue est survenue.");
            });
    });

    // Reset modal when closed
    addArticleModalElement.addEventListener("hidden.bs.modal", function () {
        // Reset modal to initial state
        articleFormFields.style.display = "block";
        generatedArticleContent.style.display = "none";
        addArticleForm.reset(); // Reset the form fields
    });

    // Fonction pour ajouter un article au tableau
    function addArticleToTable(article) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${article.title}</td>
            <td>${article.conference ? `Conférence : ${article.conference.theme}` : "Événement : Général"}</td>
            <td>
                <a href="#" class="btn btn-primary btn-sm">Voir</a>
            </td>
        `;
        articlesTableBody.appendChild(row);
    }
});

document.getElementById("sponsorForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById("file");
    formData.append("file", fileInput.files[0]);
    formData.append("event_id", document.getElementById("event_id").value);

    fetch(`/api/articles/from-sponsors`, {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Erreur lors de l'importation des sponsors.");
            }
            return response.json();
        })
        .then((data) => {
            alert(data.message);
            // Rafraîchir dynamiquement la table si nécessaire
            console.log("Articles générés :", data.articles);
        })
        .catch((error) => {
            console.error(error);
            alert("Erreur lors de l'importation des sponsors.");
        });
});
