$(document).ready(function () {
    $('#create-visual-form').on('submit', function (e) {
        e.preventDefault(); // Empêche le rechargement de la page
        const formData = {
            title: $('#title').val(),
            prompt: $('#prompt').val(),
            associated_type: $('#associated_type').val(),
            associated_id: $('#associated_id').val() || null,
        };

        // Afficher la modal et le spinner
        $('#modal-visual-img').hide();
        $('#loading-spinner').show();
        $('#visualModal').modal('show');

        $.ajax({
            url: '/api/generate-visual',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                // Charger l'image dans la modal
                $('#modal-visual-img').attr('src', response.image_url);
                $('#loading-spinner').hide(); // Cacher le spinner
                $('#modal-visual-img').show(); // Afficher l'image

                // Ajouter le visuel dans le tableau
                const newVisualRow = `
                <tr>
                    <td>${response.visual_id}</td>
                    <td>${formData.title}</td>
                    <td>
                        <a href="${response.image_url}" target="_blank">
                            <img src="${response.image_url}" alt="${formData.title}" style="width: 100px;">
                        </a>
                    </td>
                </tr>`;
                $('#visuals-table tbody').append(newVisualRow);
            },
            error: function (xhr) {
                $('#loading-spinner').hide();
                alert('Erreur : ' + xhr.responseJSON.error);
            }
        });
    });
});