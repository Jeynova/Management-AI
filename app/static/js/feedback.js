const form = document.getElementById("feedbackForm");
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        feedback: document.getElementById("feedback").value
    };

    try {
        const response = await fetch("/feedback/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        document.getElementById("responseMessage").innerText = result.message || result.error;
    } catch (error) {
        console.error("Erreur lors de l'envoi du feedback:", error);
    }
});
