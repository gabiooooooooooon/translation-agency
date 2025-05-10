let currentSlide = 0;
const slides = document.querySelectorAll('.slide');

document.addEventListener('DOMContentLoaded', () => {
            showSlide(currentSlide);
        });

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.remove('active');
                if (i === index) slide.classList.add('active');
            });
        }

        function nextSlide() {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        }

        function prevSlide() {
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(currentSlide);
        }

        function toggleMobileMenu() {
            document.querySelector('nav .nav-links').classList.toggle('active');
        }