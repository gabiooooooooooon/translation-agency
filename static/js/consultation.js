document.addEventListener('DOMContentLoaded', function() {
    const consultationType = document.getElementById('consultationType');
    const contactFieldGroup = document.getElementById('contactFieldGroup');
    const contactFieldLabel = document.getElementById('contactFieldLabel');
    const contactField = document.getElementById('contactField');
    
    // Изменение вида консультации
    consultationType.addEventListener('change', function() {
      if (this.value === 'phone') {
        contactFieldGroup.classList.remove('hidden');
        contactFieldLabel.textContent = 'Телефон';
        contactField.placeholder = 'Введите ваш телефон';
        contactField.type = 'tel';
      } else if (this.value === 'email') {
        contactFieldGroup.classList.remove('hidden');
        contactFieldLabel.textContent = 'Электронная почта';
        contactField.placeholder = 'Введите вашу электронную почту';
        contactField.type = 'email';
      } else {
        contactFieldGroup.classList.add('hidden');
      }
    });
    
    // Обработка отправки формы
    document.getElementById('consultationForm').addEventListener('submit', function(e) {
      e.preventDefault();
      
      const name = document.getElementById('clientName').value;
      const type = consultationType.value;
      const contact = contactField.value;
      
      // Здесь можно добавить отправку данных на сервер
      alert(`Спасибо, ${name}! Ваша заявка на ${type === 'phone' ? 'телефонную консультацию' : 'консультацию по email'} принята. Мы свяжемся с вами ${type === 'phone' ? 'по телефону ' + contact : 'по электронной почте ' + contact} в ближайшее время.`);
      
      // Очистка формы
      this.reset();
      contactFieldGroup.classList.add('hidden');
    });
  });