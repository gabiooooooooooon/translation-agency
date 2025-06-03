// Slider functionality
const slider = document.getElementById('slider');
const slides = document.querySelectorAll('.slide');
const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');
let currentSlide = 0;
const slideCount = slides.length;

function goToSlide(n) {
  currentSlide = (n + slideCount) % slideCount;
  document.querySelector('.slider__wrapper').style.transform = `translateX(-${currentSlide * 100}%)`;
  
  // Update active class
  slides.forEach(slide => slide.classList.remove('active'));
  slides[currentSlide].classList.add('active');
}

function nextSlide() {
  goToSlide(currentSlide + 1);
}

function prevSlide() {
  goToSlide(currentSlide - 1);
}

nextBtn.addEventListener('click', nextSlide);
prevBtn.addEventListener('click', prevSlide);

// Auto-slide every 5 seconds
let slideInterval = setInterval(nextSlide, 5000);

// Pause on hover
slider.addEventListener('mouseenter', () => {
  clearInterval(slideInterval);
});

slider.addEventListener('mouseleave', () => {
  slideInterval = setInterval(nextSlide, 5000);
});

// Initialize slider
goToSlide(0);