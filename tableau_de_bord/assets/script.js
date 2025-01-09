document.addEventListener('DOMContentLoaded', function() {
    // Ajoute une animation de fade-in aux éléments au chargement de la page
    const elements = document.querySelectorAll('.fade-in');
    elements.forEach(element => {
        element.classList.add('visible');
    });

    // Ajoute une animation de survol aux boutons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mouseover', () => {
            button.classList.add('hovered');
        });
        button.addEventListener('mouseout', () => {
            button.classList.remove('hovered');
        });
    });

    // Ajoute une animation de défilement aux éléments
    const scrollElements = document.querySelectorAll('.scroll-fade');
    window.addEventListener('scroll', () => {
        scrollElements.forEach(element => {
            if (isElementInViewport(element)) {
                element.classList.add('visible');
            }
        });
    });

    // Fonction pour vérifier si un élément est dans la fenêtre de visualisation
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    // Ajoute des messages de confirmation pour certaines actions
    const submitButton = document.getElementById('submit-button');
    submitButton.addEventListener('click', () => {
        alert('Les données ont été soumises avec succès!');
    });

    // Ajoute des transitions douces pour les entrées de texte
    const textInputs = document.querySelectorAll('input[type="text"]');
    textInputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.style.transition = 'border-color 0.3s ease-in-out';
        });
        input.addEventListener('blur', () => {
            input.style.transition = 'border-color 0.3s ease-in-out';
        });
    });
});