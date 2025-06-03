document.addEventListener('DOMContentLoaded', function() {
    const reviewForm = document.getElementById('reviewForm');
    const reviewComment = document.getElementById('reviewComment');
    const reviewsList = document.getElementById('reviewsList');
    const ratingNumbers = document.getElementById('ratingCounter').querySelectorAll('.rating-number');
    const selectedRatingInput = document.getElementById('selectedRating');
    
    let selectedRating = 0;
    
    // Обработка выбора рейтинга
    ratingNumbers.forEach(number => {
      number.addEventListener('click', function() {
        selectedRating = parseInt(this.getAttribute('data-rating'));
        selectedRatingInput.value = selectedRating;
        
        ratingNumbers.forEach((n, index) => {
          if (index < selectedRating) {
            n.classList.add('active');
          } else {
            n.classList.remove('active');
          }
        });
      });
      
      number.addEventListener('mouseover', function() {
        const rating = parseInt(this.getAttribute('data-rating'));
        
        ratingNumbers.forEach((n, index) => {
          if (index < rating) {
            n.classList.add('active');
          } else {
            n.classList.remove('active');
          }
        });
      });
      
      number.addEventListener('mouseout', function() {
        ratingNumbers.forEach((n, index) => {
          if (index < selectedRating) {
            n.classList.add('active');
          } else {
            n.classList.remove('active');
          }
        });
      });
    });
    
    // Обработка отправки формы
    reviewForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      if (selectedRating === 0) {
        alert('Пожалуйста, выберите оценку от 1 до 5');
        return;
      }
      
      // Здесь должна быть логика отправки отзыва на сервер
      // Для примера просто добавим отзыв в список
      
      const newReview = document.createElement('div');
      newReview.className = 'review-item';
      
      newReview.innerHTML = `
        <div class="review-meta">
          <span class="review-email">Новый пользователь</span>
          <span class="review-date">${new Date().toLocaleDateString('ru-RU')}, ${new Date().toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'})}</span>
        </div>
        <div class="review-rating">
          Оценка: <span class="review-rating-value">${selectedRating} из 5</span>
        </div>
        <p class="review-text">${reviewComment.value}</p>
      `;
      
      reviewsList.prepend(newReview);
      reviewComment.value = '';
      selectedRating = 0;
      selectedRatingInput.value = 0;
      ratingNumbers.forEach(n => n.classList.remove('active'));
      alert('Спасибо за ваш отзыв!');
      
      // В реальном приложении здесь бы был fetch-запрос к серверу
      // fetch('/api/reviews', { 
      //   method: 'POST', 
      //   headers: {
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify({
      //     text: reviewComment.value,
      //     rating: selectedRating
      //   }) 
      // })
    });
    
    // В реальном приложении здесь бы загружались отзывы с сервера
    // fetch('/api/reviews')
    //   .then(response => response.json())
    //   .then(reviews => {
    //     reviews.forEach(review => {
    //       const reviewElement = document.createElement('div');
    //       reviewElement.className = 'review-item';
    //       
    //       reviewElement.innerHTML = `
    //         <div class="review-meta">
    //           <span class="review-email">${review.email}</span>
    //           <span class="review-date">${new Date(review.date).toLocaleString('ru-RU')}</span>
    //         </div>
    //         <div class="review-rating">
    //           Оценка: <span class="review-rating-value">${review.rating} из 5</span>
    //         </div>
    //         <p class="review-text">${review.text}</p>
    //       `;
    //       reviewsList.appendChild(reviewElement);
    //     });
    //   });
  });