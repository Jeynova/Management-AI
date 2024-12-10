async function fetchFeedbackSummary() {
    const response = await fetch("/admin/feedback-summary");
    const data = await response.json();

    if (data.error) {
        document.getElementById("global-analysis").textContent = data.error;
    } else {
        document.getElementById("global-analysis").textContent = data.summary;
        const feedbackList = document.getElementById("feedback-details");
        feedbackList.innerHTML = "";
        data.feedbacks.forEach(feedback => {
            const listItem = document.createElement("li");
            listItem.textContent = `Texte: ${feedback.feedback_text}, Sentiment: ${feedback.sentiment}`;
            feedbackList.appendChild(listItem);
        });
    }
}

// Charger le résumé au chargement de la page
fetchFeedbackSummary();
