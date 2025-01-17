document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.favourite-btn');
    const isFavPage = document.getElementById('fav-container')

    buttons.forEach(button => {
        button.addEventListener('click', async (e) => {
            const btn = e.target;
            const type = btn.getAttribute('data-type');
            const id = btn.getAttribute('data-id');
            const isFavourite = btn.classList.contains('favourite');

            try {
                const response = await fetch(`/favoritos/${isFavourite ? 'eliminar' : 'agregar'}/${type}/${id}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(), // Asegúrate de incluir el token CSRF
                    },
                });

                if (response.ok) {
                    if (isFavPage){
                        window.location.reload(); // Elimina el elemento de la listac
                    }
                    else{
                        btn.classList.toggle('favourite');
                    }
                } else {
                    console.error('Error toggling favourite:', response.statusText);
                }
            } catch (error) {
                console.error('Error toggling favourite:', error);
            }
        });
    });

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
