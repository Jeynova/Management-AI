document.getElementById("fill-with-ai").addEventListener("click", function () {
    fetch("/api/generate-random-participant")
        .then(response => response.json())
        .then(data => {
            const participant = JSON.parse(data.participant_data);

            // Nettoyer tous les champs
            clearFields()

            // Remplir les champs avec les données générées
            document.getElementById("nom").value = participant.Nom || "";
            document.getElementById("prenom").value = participant.Prenom || "";
            document.getElementById("email").value = participant.Email || "";
            document.getElementById("sexe").value = participant.Sexe || "Homme";
            document.getElementById("age").value = participant.Age || "";
            document.getElementById("profession").value = participant.Profession || "";
        })
        .catch(error => {
            console.error("Erreur lors de la génération des données : ", error);
        });
});

function clearFields() {
    const fields = ["nom", "prenom", "email", "sexe", "age", "profession"];
    fields.forEach((field) => {
        const input = document.getElementById(field);
        input.value = "";
        input.style.transition = "background-color 0.3s ease";
        input.style.backgroundColor = "#f8d7da"; // Couleur d'effacement
        setTimeout(() => (input.style.backgroundColor = ""), 300); // Retour à la normale
    });
}