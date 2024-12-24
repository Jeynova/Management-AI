document.getElementById("fill-with-ai").addEventListener("click", function () {
    fetch("/api/generate-random-participant")
        .then(response => response.json())
        .then(data => {
            const participant = JSON.parse(data.participant_data);

            // Nettoyer tous les champs
            document.getElementById("nom").value = "";
            document.getElementById("prenom").value = "";
            document.getElementById("email").value = "";
            document.getElementById("sexe").value = "Homme"; // Valeur par défaut
            document.getElementById("age").value = "";
            document.getElementById("profession").value = "";

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