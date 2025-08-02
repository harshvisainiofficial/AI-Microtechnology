// Scroll-triggered animations for about sections
function initAboutAnimations() {
    const sections = document.querySelectorAll('.animate-section');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-in');
                }, index * 200); // Stagger the animations
            } else {
                // Remove animation class when out of view to allow re-triggering
                entry.target.classList.remove('animate-in');
            }
        });
    }, {
        threshold: 0.2,
        rootMargin: '0px 0px -50px 0px'
    });
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initAboutAnimations);