// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si GSAP est chargé
    if (typeof gsap === 'undefined') {
        console.error('GSAP non chargé. Les animations ne fonctionneront pas.');
        // Fallback : rendre tous les éléments fade-up visibles
        document.querySelectorAll('.fade-up').forEach(el => {
            el.style.opacity = 1;
        });
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    // Animation des éléments avec la classe 'fade-up'
    gsap.utils.toArray('.fade-up').forEach(element => {
        gsap.from(element, {
            scrollTrigger: {
                trigger: element,
                start: 'top 80%',
                end: 'bottom 20%',
                toggleActions: 'play none none reverse'
            },
            y: 50,
            opacity: 0,
            duration: 1,
            ease: 'power2.out'
        });
    });

    // Animation des cartes de projets (si présentes)
    gsap.utils.toArray('.project-card').forEach((card, i) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            scale: 0.9,
            opacity: 0,
            duration: 0.6,
            delay: i * 0.1
        });
    });

    // Effet de scroll sur la navbar
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
});