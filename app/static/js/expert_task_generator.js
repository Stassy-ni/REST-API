document.addEventListener('DOMContentLoaded', function() {
    // Конфигурация
    const apiKey = "sk-HKNmCeRHTWewMlOfkmSpYaPTR0JCr4c1"; // ВАШ API-КЛЮЧ
    const baseUrl = "https://api.proxyapi.ru/openai/v1";
    
    // Элементы интерфейса
    const generateBtn = document.getElementById('generate-task-btn');
    const taskContent = document.getElementById('task-content');
    const answerContent = document.getElementById('answer-content');
    const loadingIndicator = document.getElementById('loading-indicator');
    const saveBtn = document.getElementById('save-task-btn');
    const rejectBtn = document.getElementById('reject-task-btn');
    const categorySelect = document.getElementById('task-category');
    const difficultySelect = document.getElementById('task-difficulty');
    
    // Текущее задание
    let currentTask = {
        text: '',
        answer: '',
        category: 'addition',
        difficulty: 'easy'
    };
    
    // Категории и сложности
    const categories = {
        addition: 'Сложение дробей',
        subtraction: 'Вычитание дробей',
        multiplication: 'Умножение дробей',
        division: 'Деление дробей'
    };
    
    const difficulties = {
        easy: 'Легкий',
        medium: 'Средний',
        hard: 'Сложный'
    };
    
    // Обновляем текущие значения
    categorySelect.addEventListener('change', (e) => {
        currentTask.category = e.target.value;
    });
    
    difficultySelect.addEventListener('change', (e) => {
        currentTask.difficulty = e.target.value;
    });
    
    // Генерация задачи
    generateBtn.addEventListener('click', async () => {
    if (!generateBtn.classList.contains('disabled')) {
        startLoading();
            
            try {
                const prompt = `Сгенерируй ${difficulties[currentTask.difficulty].toLowerCase()} пример по теме "${categories[currentTask.category]}". 

                Строго соблюдай следующие правила:

                1. Формат вывода:
                - Для ЛЕГКОГО и СРЕДНЕГО уровня: 
                "Вычисли: [пример]"
                "Ответ: [ответ]"
                - Для СЛОЖНОГО уровня:
                "Реши задачу: [условие]"
                "Ответ: [ответ]"

                2. Требования к генерации:
                - Всегда используй LaTeX: \\(\\frac{a}{b}\\) для дробей, \\(d\\frac{a}{b}\\) для смешанных чисел
                - Для сложения/вычитания (легкий уровень) - одинаковые знаменатели (2-30)
                - Для умножения/деления (легкий уровень) - простые дроби (знаменатели 2-30)
                - Средний уровень - разные знаменатели (НОК до 80)
                - Сложный уровень - многошаговые операции (НОК до 100)

                3. Ответ должен быть:
                - В формате "x/y" для дробей
                - В формате "z x/y" для смешанных чисел
                - В формате "x" для целых чисел
                - Без пояснений, только числовой ответ

                4. Запрещено:
                - Добавлять посторонний текст
                - Объяснять решение
                - Приводить несколько примеров
                - Использовать десятичные дроби

                Пример правильного вывода для ЛЕГКОГО уровня:
                Вычисли: \\(\\frac{3}{5} + \\frac{1}{5}\\)
                Ответ: 4/5

                Пример правильного вывода для СРЕДНЕГО уровня:
                Вычисли: \\(1\\frac{1}{4} \\times \\frac{2}{3}\\)
                Ответ: 5/6

                Пример правильного вывода для СЛОЖНОГО уровня:
                Реши задачу: В корзине было \\(2\\frac{1}{2}\\) кг яблок, добавили еще \\(1\\frac{3}{4}\\) кг. Сколько стало?
                Ответ: 4 1/4

                Сгенерируй строго ОДИН пример по выбранной категории и сложности, соблюдая все правила.`;
                
                const response = await fetch(`${baseUrl}/chat/completions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${apiKey}`
                    },
                    body: JSON.stringify({
                        model: "gpt-4o",
                        messages: [{ role: "user", content: prompt }],
                        temperature: 0.7 // Добавляем параметр температуры для более предсказуемых ответов
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                const fullResponse = data.choices?.[0]?.message?.content || 'Ошибка генерации';
                
                // Разделяем ответ на задание и решение
                // В функции обработки ответа от API:
                const answerIndex = fullResponse.indexOf("Ответ:");
                if (answerIndex !== -1) {
                    currentTask.text = fullResponse.substring(0, answerIndex).trim();
                    let answer = fullResponse.substring(answerIndex + "Ответ:".length).trim();
                    
                    // Нормализация ответа
                    answer = answer.replace(/\\frac\{(\d+)\}\{(\d+)\}/g, '$1/$2'); // Преобразует \frac{a}{b} в a/b
                    answer = answer.replace(/\s+/g, ' ').trim(); // Удаляет лишние пробелы
                    
                    currentTask.answer = answer;
                } else {
                    currentTask.text = fullResponse;
                    currentTask.answer = "Ответ не был сгенерирован";
                }

                displayTask(); // Добавляем отображение задачи
                enableActionButtons(); // Активируем кнопки
                
            } catch (error) {
                showError('Ошибка генерации: ' + error.message);
                console.error(error);
            } finally {
                stopLoading();
            }
        }
    });
    
    // Сохранение задачи
    saveBtn.addEventListener('click', async () => {
        try {
            await saveTaskToDB();
            showSuccess('Задача успешно сохранена');
            resetGenerator();
        } catch (error) {
            showError('Ошибка сохранения: ' + error.message);
        }
    });
    
    // Отклонение задачи
    rejectBtn.addEventListener('click', () => {
        resetGenerator();
    });
    
    // Вспомогательные функции
    function startLoading() {
        loadingIndicator.style.display = 'block';
        generateBtn.classList.add('disabled');
    }
    
    function stopLoading() {
        loadingIndicator.style.display = 'none';
        generateBtn.classList.remove('disabled');
    }
    
    function displayTask() {
        taskContent.innerHTML = currentTask.text;
        answerContent.innerHTML = currentTask.answer;
        
        if (window.MathJax) {
            MathJax.typesetPromise([taskContent, answerContent])
                .catch(err => console.log('MathJax error:', err));
        }
    }
    
    function enableActionButtons() {
        saveBtn.disabled = false;
        rejectBtn.disabled = false;
    }
    
    function disableActionButtons() {
        saveBtn.disabled = true;
        rejectBtn.disabled = true;
    }
    
    function resetGenerator() {
        taskContent.innerHTML = '';
        answerContent.innerHTML = '';
        disableActionButtons();
    }
    
    function showError(message) {
        // Можно использовать toast или другой механизм уведомлений
        alert(message);
    }
    
    function showSuccess(message) {
        alert(message);
    }
    
    // В функции saveTaskToDB заменим console.log на реальный запрос:
    async function saveTaskToDB() {
        try {
            const response = await fetch('/expert/save-task', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    category: currentTask.category,
                    difficulty: currentTask.difficulty,
                    text: currentTask.text,
                    answer: currentTask.answer
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Неизвестная ошибка сервера');
            }
            
            if (!data.success) {
                throw new Error(data.message || 'Ошибка сохранения');
            }
            
            return data;
        } catch (error) {
            console.error('Ошибка сохранения:', error);
            throw error;
        }
    }

    // Вспомогательная функция для CSRF токена (если нужно)
    function getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.content : '';
    }
});