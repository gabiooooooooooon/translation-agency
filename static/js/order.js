// Проверка и инициализация PDF.js
function initializePDFJS() {
  if (typeof pdfjsLib === 'undefined') {
    console.error('PDF.js library is not loaded! Loading now...');
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.min.js';
    script.onload = setupOrderForm;
    document.head.appendChild(script);
    return false;
  }
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js';
  return true;
}

// Константы для расчета
const PRICES = {
  written: {
    perPage: 700,
    minPages: 1
  },
  oral: 3500,
  visa: 5000,
  notarization: 700,
  apostille: 3500
};

// Основная функция настройки формы
function setupOrderForm() {
  // Получаем все элементы формы с проверкой
  const elements = {
    serviceType: document.getElementById('serviceType'),
    fileUploadGroup: document.getElementById('fileUploadGroup'),
    additionalServicesGroup: document.getElementById('additionalServicesGroup'),
    deliveryGroup: document.getElementById('deliveryGroup'),
    deliveryType: document.getElementById('deliveryType'),
    deliveryAddressGroup: document.getElementById('deliveryAddressGroup'),
    deliveryAddress: document.getElementById('deliveryAddress'),
    totalPrice: document.getElementById('totalPrice'),
    notarization: document.getElementById('notarization'),
    apostille: document.getElementById('apostille'),
    documentFile: document.getElementById('documentFile'),
    orderForm: document.getElementById('orderForm'),
    sourceLanguage: document.getElementById('sourceLanguage'),
    targetLanguage: document.getElementById('targetLanguage'),
    comment: document.getElementById('comment')
  };

  // Проверяем, что все элементы существуют
  for (const [key, element] of Object.entries(elements)) {
    if (!element && key !== 'comment') { // comment может быть пустым
      console.error(`Element ${key} not found!`);
      return;
    }
  }

  // Функция обновления видимости полей
  function updateFieldsVisibility() {
    const selectedService = elements.serviceType.value;

    // Управление видимостью групп
    elements.fileUploadGroup.classList.toggle('hidden', !['written', 'visa'].includes(selectedService));
    elements.additionalServicesGroup.classList.toggle('hidden', !['written', 'additional'].includes(selectedService));
    elements.deliveryGroup.classList.toggle('hidden', !selectedService || selectedService === 'oral');

    // Сброс значений при скрытии
    if (elements.additionalServicesGroup.classList.contains('hidden')) {
      elements.notarization.checked = false;
      elements.apostille.checked = false;
    }

    if (elements.deliveryGroup.classList.contains('hidden')) {
      elements.deliveryType.value = '';
      elements.deliveryAddressGroup.classList.add('hidden');
      elements.deliveryAddress.value = '';
    }
  }

  // Функция анализа документа
  async function getDocumentStats(file) {
    if (!file) return { pages: 1, characters: 0 };

    try {
      if (file.type === 'application/pdf') {
        const arrayBuffer = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsArrayBuffer(file);
        });

        const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
        let totalChars = 0;

        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const textContent = await page.getTextContent();
          totalChars += textContent.items.reduce((sum, item) => sum + item.str.length, 0);
        }

        return { pages: pdf.numPages, characters: totalChars };
      } else {
        const text = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsText(file);
        });

        return {
          pages: Math.ceil(text.length / 1800),
          characters: text.length
        };
      }
    } catch (error) {
      console.error('Error analyzing document:', error);
      return { pages: 1, characters: 0 };
    }
  }

  // Расчет стоимости
  async function calculatePrice() {
    let price = 0;
    const file = elements.documentFile.files[0];
    const selectedService = elements.serviceType.value;

    try {
      switch(selectedService) {
        case 'written':
          const stats = await getDocumentStats(file);
          const pages = Math.max(
            Math.ceil(stats.characters / 1800),
            PRICES.written.minPages
          );
          price = pages * PRICES.written.perPage;
          break;
        case 'oral':
          price = PRICES.oral;
          break;
        case 'additional':
          price = 0;
          break;
        case 'visa':
          price = PRICES.visa;
          break;
      }

      // Добавляем доп. услуги
      if (['written', 'additional'].includes(selectedService)) {
        if (elements.notarization.checked) price += PRICES.notarization;
        if (elements.apostille.checked) price += PRICES.apostille;
      }

      elements.totalPrice.textContent = `${price} р.`;
      return price;
    } catch (error) {
      console.error('Error calculating price:', error);
      elements.totalPrice.textContent = 'Ошибка расчета';
      return 0;
    }
  }

  // Настройка обработчиков событий
  function setupEventListeners() {
    elements.serviceType.addEventListener('change', () => {
      updateFieldsVisibility();
      calculatePrice();
    });

    elements.deliveryType.addEventListener('change', () => {
      const showAddress = elements.deliveryType.value === 'delivery';
      elements.deliveryAddressGroup.classList.toggle('hidden', !showAddress);
      elements.deliveryAddress.required = showAddress;
    });

    elements.notarization.addEventListener('change', calculatePrice);
    elements.apostille.addEventListener('change', calculatePrice);
    elements.documentFile.addEventListener('change', calculatePrice);

    // Обработчик отправки формы
    elements.orderForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = elements.orderForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Отправка...';

      try {
        const price = await calculatePrice();
        const formData = new FormData();
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!csrfToken) {
          throw new Error('CSRF token not found');
        }

        // Добавляем файл, если есть
        if (elements.documentFile.files.length > 0) {
          formData.append('document', elements.documentFile.files[0]);
        }

        // Добавляем остальные данные
        formData.append('service_type', elements.serviceType.value);
        formData.append('source_language', elements.sourceLanguage.value);
        formData.append('target_language', elements.targetLanguage.value);
        formData.append('comment', elements.comment.value || '');
        formData.append('delivery_type', elements.deliveryType.value || 'pickup');
        formData.append('delivery_address', elements.deliveryAddress.value || '');
        formData.append('total_price', price);
        formData.append('notarization', elements.notarization.checked);
        formData.append('apostille', elements.apostille.checked);

        const response = await fetch('/submit-order/', {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': csrfToken
          }
        });

        const result = await response.json();

        if (response.ok) {
          window.location.href = `/order-success/?order_id=${result.order_id}`;
        } else {
          alert(`Ошибка: ${result.error || 'Неизвестная ошибка'}`);
        }
      } catch (error) {
        console.error('Form submission error:', error);
        alert('Произошла ошибка при отправке формы: ' + error.message);
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Заказать';
      }
    });
  }

  // Инициализация формы
  updateFieldsVisibility();
  setupEventListeners();
  calculatePrice();
}

// Запуск при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  if (initializePDFJS()) {
    setupOrderForm();
  }
});

// Обработчик отправки формы
elements.orderForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = elements.orderForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Отправка...';

    try {
        const price = await calculatePrice();
        const formData = new FormData(elements.orderForm);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }

        const response = await fetch('/api/orders/', {  // Изменили URL
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json'  // Явно указываем ожидаемый формат
            }
        });

        // Проверяем Content-Type перед парсингом
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Ожидался JSON, но получили: ${text.substring(0, 100)}...`);
        }

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || result.message || 'Неизвестная ошибка сервера');
        }

        window.location.href = `/order-success/?order_id=${result.id}`;
    } catch (error) {
        console.error('Form submission error:', error);
        alert(`Ошибка при отправке формы: ${error.message}`);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Заказать';
    }
});

document.getElementById('orderForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);

    try {
        const response = await fetch('/submit-order/', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        if (result.success) {
            alert('Заказ успешно создан!');
            window.location.href = `/services/order/success/?order_id=${result.order_id}`;
        } else {
            alert(`Ошибка: ${result.error}`);
        }
    } catch (err) {
        console.error('Ошибка отправки формы:', err);
    }
});

const formData = new FormData();
formData.append('service_type', 'translation');
formData.append('source_language', 'en');
formData.append('target_language', 'ru');
formData.append('comment', 'Need a translation');
formData.append('delivery_type', 'pickup');
formData.append('document_file', document.getElementById('file-input').files[0]);  // Предположим, что у тебя есть input с id="file-input"

fetch('http://127.0.0.1:8000/submit_order/', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Success:', data);
})
.catch((error) => {
  console.error('Error:', error);
});