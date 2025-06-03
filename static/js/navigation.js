// Mobile menu toggle
const burger = document.getElementById('burger');
const nav = document.getElementById('nav');
const servicesDropdown = document.getElementById('services-dropdown');
const aboutDropdown = document.getElementById('about-dropdown');
const loginBtn = document.querySelector('.login-btn');
const authDropdown = document.querySelector('.auth-dropdown');

burger.addEventListener('click', () => {
  burger.classList.toggle('active');
  nav.classList.toggle('active');
});

// Mobile dropdown toggle
if (window.innerWidth <= 768) {
  // Services dropdown
  servicesDropdown.addEventListener('click', (e) => {
    e.preventDefault();
    servicesDropdown.classList.toggle('active');
  });
  
  // About dropdown
  aboutDropdown.addEventListener('click', (e) => {
    e.preventDefault();
    aboutDropdown.classList.toggle('active');
  });
  
  // Auth dropdown
  const navAuth = document.querySelector('.nav__auth');
  if (navAuth) {
    loginBtn.addEventListener('click', (e) => {
      e.preventDefault();
      navAuth.classList.toggle('active');
    });
  }
}

// Desktop auth dropdown hover
if (window.innerWidth > 768) {
  const headerAuth = document.querySelector('.header__auth');
  if (headerAuth) {
    headerAuth.addEventListener('mouseenter', () => {
      authDropdown.style.opacity = '1';
      authDropdown.style.visibility = 'visible';
      authDropdown.style.transform = 'translateY(0)';
    });
    
    headerAuth.addEventListener('mouseleave', () => {
      authDropdown.style.opacity = '0';
      authDropdown.style.visibility = 'hidden';
      authDropdown.style.transform = 'translateY(10px)';
    });
  }
}