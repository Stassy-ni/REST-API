// Глобальная переменная для хранения текущих задач
let currentTasks = [];

function generateTest() {
    const testOutput = document.getElementById('testOutput');
    testOutput.innerHTML = '<h2>Задания по работе с обыкновенными дробями</h2> <p><i>Примечание: при вводе ответа, обыкновенные дроби пишите через / , например, 1/2, а смешанные числа через пробел x y/z, например, 2 3/5.</i></p>';
    
    // Генерируем 5 случайных задач разного типа
    currentTasks = [
        generateImproperToMixedTask(),       // Перевод неправильной дроби в смешанное число
        generateMixedToImproperTask(),       // Перевод смешанного числа в неправильную дробь
        generateSimplifyFractionTask(),      // Сокращение дробей
        generateCommonDenominatorTask(),     // Приведение к общему знаменателю
        generateDivisionToFractionTask()     // Представление деления в виде дроби
    ];

    // Генерация задач
    currentTasks.forEach((task, index) => {
        const taskElement = document.createElement('div');
        taskElement.className = 'task';
        taskElement.id = task.id;
        
        taskElement.innerHTML = `
            <h3>Задача ${index + 1}</h3>
            <p>${task.question}</p>
            <input type="text" id="${task.id}-answer" placeholder="Введите ответ">
            <button class="check-button" onclick="checkAnswer('${task.id}')">Проверить</button>
            <div id="${task.id}-feedback" class="feedback hidden"></div>
            <div id="${task.id}-steps" class="hidden"></div>
        `;
        
        testOutput.appendChild(taskElement);
    });
}

function checkAnswer(taskId) {
    const task = currentTasks.find(t => t.id === taskId);
    if (!task) return;
    
    const answerInput = document.getElementById(`${taskId}-answer`);
    const feedbackElement = document.getElementById(`${taskId}-feedback`);
    const stepsElement = document.getElementById(`${taskId}-steps`);
    
    const userAnswer = answerInput.value.trim().replace(/\s+/g, ' '); // Нормализуем пробелы
    const correctAnswers = task.answer.split(' или ').map(a => a.trim());
    
    // Проверяем, совпадает ли ответ с любым из правильных вариантов
    if (correctAnswers.some(correct => areFractionsEqual(userAnswer, correct))) {
        feedbackElement.innerHTML = '<p class="correct">Правильно! Молодец!</p>';
        feedbackElement.classList.remove('hidden');
        stepsElement.classList.add('hidden');
    } else {
        feedbackElement.innerHTML = '<p class="incorrect">Неправильно. Давайте решим по шагам.</p>';
        feedbackElement.classList.remove('hidden');
        stepsElement.innerHTML = '';
        stepsElement.classList.remove('hidden');
        
        // Добавляем шаги решения
        task.steps.forEach((step, stepIndex) => {
            const stepElement = document.createElement('div');
            stepElement.className = 'step';
            stepElement.innerHTML = `
                <div class="step-question">${step.question}</div>
                <input type="text" id="${taskId}-step-${stepIndex}" placeholder="Введите ответ">
                <button class="check-button" onclick="checkStep('${taskId}', ${stepIndex})">Проверить шаг</button>
                <div id="${taskId}-step-feedback-${stepIndex}" class="feedback hidden"></div>
            `;
            stepsElement.appendChild(stepElement);
        });
    }
}

function checkStep(taskId, stepIndex) {
    const task = currentTasks.find(t => t.id === taskId);
    if (!task || !task.steps[stepIndex]) return;
    
    const step = task.steps[stepIndex];
    const stepInput = document.getElementById(`${taskId}-step-${stepIndex}`);
    const stepFeedback = document.getElementById(`${taskId}-step-feedback-${stepIndex}`);
    
    const userAnswer = stepInput.value.trim();
    const correctAnswers = step.answer.split(' или ').map(a => a.trim());
    
    if (correctAnswers.some(correct => userAnswer === correct)) {
        stepFeedback.innerHTML = '<p class="correct">Верно!</p>';
        stepFeedback.classList.remove('hidden');
    } else {
        stepFeedback.innerHTML = '<p class="incorrect">Неверно. Попробуйте еще раз.</p>';
        stepFeedback.classList.remove('hidden');
    }
}

// Функции для генерации задач

function generateImproperToMixedTask() {
    const denominator = getRandomInt(2, 12);
    const numerator = getRandomInt(denominator + 1, denominator * 3); // Гарантируем неправильную дробь
    
    const whole = Math.floor(numerator / denominator);
    const remainder = numerator % denominator;
    const answerMixed = remainder === 0 ? whole.toString() : `${whole} ${remainder}/${denominator}`;
    const answerSimplified = simplifyFraction(`${remainder}/${denominator}`);
    
    // Если дробную часть можно сократить
    const finalAnswer = answerSimplified !== `${remainder}/${denominator}` ? 
                       `${whole} ${answerSimplified}` : answerMixed;
    
    return {
        id: 'task-' + Date.now() + '-1',
        question: `Преобразуйте неправильную дробь в смешанное число: <span class="math">${numerator}/${denominator}</span>`,
        answer: finalAnswer,
        steps: [
            {
                question: `Разделите числитель на знаменатель: ${numerator} ÷ ${denominator} = ? (целая часть)`,
                answer: whole.toString()
            },
            {
                question: `Найдите остаток от деления: ${numerator} - ${whole} × ${denominator} = ?`,
                answer: remainder.toString()
            },
            {
                question: `Запишите смешанное число: <span class="math">${whole} ?/${denominator}</span>`,
                answer: remainder.toString()
            },
            ...(answerSimplified !== `${remainder}/${denominator}` ? [{
                question: `Сократите дробную часть (если возможно): <span class="math">${remainder}/${denominator} = ?</span>`,
                answer: answerSimplified
            }] : [])
        ]
    };
}

function generateMixedToImproperTask() {
    const whole = getRandomInt(1, 5);
    const denominator = getRandomInt(2, 12);
    const numerator = getRandomInt(1, denominator - 1);
    
    const improperNumerator = whole * denominator + numerator;
    const answer = `${improperNumerator}/${denominator}`;
    
    return {
        id: 'task-' + Date.now() + '-2',
        question: `Преобразуйте смешанное число в неправильную дробь: <span class="math">${whole} ${numerator}/${denominator}</span>`,
        answer: answer,
        steps: [
            {
                question: `Умножьте целую часть на знаменатель: ${whole} × ${denominator} = ?`,
                answer: (whole * denominator).toString()
            },
            {
                question: `Прибавьте числитель: ${whole * denominator} + ${numerator} = ?`,
                answer: improperNumerator.toString()
            },
            {
                question: `Запишите неправильную дробь: <span class="math">?/${denominator}</span>`,
                answer: improperNumerator.toString()
            }
        ]
    };
}

function generateSimplifyFractionTask() {
    const denominator = getRandomInt(4, 24);
    const numerator = getRandomInt(2, denominator - 1);
    
    // Гарантируем, что дробь можно сократить
    const gcd = findGCD(numerator, denominator);
    if (gcd === 1) {
        // Если дробь несократима, создаем сократимую
        const factor = getRandomInt(2, 4);
        const simplifiedNum = getRandomInt(1, 5);
        const simplifiedDenom = getRandomInt(simplifiedNum + 1, 8);
        return generateSimplifyFractionTask(`${simplifiedNum * factor}/${simplifiedDenom * factor}`);
    }
    
    const simplifiedNum = numerator / gcd;
    const simplifiedDenom = denominator / gcd;
    const answer = `${simplifiedNum}/${simplifiedDenom}`;
    
    return {
        id: 'task-' + Date.now() + '-3',
        question: `Сократите дробь: <span class="math">${numerator}/${denominator}</span>`,
        answer: answer,
        steps: [
            {
                question: `Найдите НОД числителя и знаменателя: НОД(${numerator}, ${denominator}) = ?`,
                answer: gcd.toString()
            },
            {
                question: `Разделите числитель на НОД: ${numerator} ÷ ${gcd} = ?`,
                answer: simplifiedNum.toString()
            },
            {
                question: `Разделите знаменатель на НОД: ${denominator} ÷ ${gcd} = ?`,
                answer: simplifiedDenom.toString()
            },
            {
                question: `Запишите сокращенную дробь: <span class="math">?/?</span>`,
                answer: answer
            }
        ]
    };
}

function generateCommonDenominatorTask() {
    const denom1 = getRandomInt(2, 8);
    const denom2 = getRandomInt(2, 8);
    const numerator1 = getRandomInt(1, denom1 - 1);
    const numerator2 = getRandomInt(1, denom2 - 1);
    
    const lcm = findLCM(denom1, denom2);
    const newNum1 = numerator1 * (lcm / denom1);
    const newNum2 = numerator2 * (lcm / denom2);
    
    return {
        id: 'task-' + Date.now() + '-4',
        question: `Приведите дроби к общему знаменателю: <span class="math">${numerator1}/${denom1}</span> и <span class="math">${numerator2}/${denom2}</span>`,
        answer: `${newNum1}/${lcm} и ${newNum2}/${lcm}`,
        steps: [
            {
                question: `Найдите НОК знаменателей: НОК(${denom1}, ${denom2}) = ?`,
                answer: lcm.toString()
            },
            {
                question: `Найдите дополнительный множитель для первой дроби: ${lcm} ÷ ${denom1} = ?`,
                answer: (lcm / denom1).toString()
            },
            {
                question: `Умножьте числитель и знаменатель первой дроби: <span class="math">${numerator1}/${denom1} = ?/${lcm}</span>`,
                answer: newNum1.toString()
            },
            {
                question: `Найдите дополнительный множитель для второй дроби: ${lcm} ÷ ${denom2} = ?`,
                answer: (lcm / denom2).toString()
            },
            {
                question: `Умножьте числитель и знаменатель второй дроби: <span class="math">${numerator2}/${denom2} = ?/${lcm}</span>`,
                answer: newNum2.toString()
            }
        ]
    };
}

function generateDivisionToFractionTask() {
    const num1 = getRandomInt(1, 10);
    const num2 = getRandomInt(1, 10);
    
    const answer = simplifyFraction(`${num1}/${num2}`);
    const answerMixed = toMixedNumber(answer);
    
    return {
        id: 'task-' + Date.now() + '-5',
        question: `Представьте деление в виде дроби (сократите, если возможно): <span class="math">${num1} ÷ ${num2}</span>`,
        answer: answer.includes('/') && parseInt(answer.split('/')[0]) > parseInt(answer.split('/')[1]) ? 
               `${answer} или ${answerMixed}` : answer,
        steps: [
            {
                question: `Запишите деление в виде дроби: <span class="math">${num1} ÷ ${num2} = ?</span>`,
                answer: `${num1}/${num2}`
            },
            ...(answer !== `${num1}/${num2}` ? [{
                question: `Сократите дробь (если возможно): <span class="math">${num1}/${num2} = ?</span>`,
                answer: answer
            }] : []),
            ...(answerMixed !== answer && answerMixed !== `${num1}/${num2}` ? [{
                question: `Преобразуйте в смешанное число (если нужно): <span class="math">${answer} = ?</span>`,
                answer: answerMixed
            }] : [])
        ]
    };
}

// Вспомогательные функции (остаются без изменений)
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function findGCD(a, b) {
    return b ? findGCD(b, a % b) : a;
}

function findLCM(a, b) {
    return (a * b) / findGCD(a, b);
}

function simplifyFraction(fraction) {
    const parts = fraction.split('/');
    if (parts.length !== 2) return fraction;
    
    const numerator = parseInt(parts[0]);
    const denominator = parseInt(parts[1]);
    
    if (isNaN(numerator) || isNaN(denominator)) return fraction;
    if (numerator === 0) return '0';
    
    const gcd = findGCD(numerator, denominator);
    if (gcd === 1) return fraction;
    
    return `${numerator / gcd}/${denominator / gcd}`;
}

function toMixedNumber(fraction) {
    const parts = fraction.split('/');
    if (parts.length !== 2) return fraction;
    
    const numerator = parseInt(parts[0]);
    const denominator = parseInt(parts[1]);
    
    if (isNaN(numerator) || isNaN(denominator)) return fraction;
    if (numerator < denominator) return fraction;
    
    const whole = Math.floor(numerator / denominator);
    const newNumerator = numerator % denominator;
    
    if (newNumerator === 0) return whole.toString();
    return `${whole} ${newNumerator}/${denominator}`;
}

function areFractionsEqual(frac1, frac2) {
    if (frac1 === frac2) return true;
    
    try {
        // Пробуем вычислить числовое значение
        const val1 = evalFraction(frac1);
        const val2 = evalFraction(frac2);
        return Math.abs(val1 - val2) < 0.0001; // Учитываем погрешность вычислений
    } catch (e) {
        return false;
    }
}

function evalFraction(frac) {
    if (!isNaN(frac)) return parseFloat(frac);
    
    // Обработка смешанных чисел (1 1/2)
    const mixedMatch = frac.match(/^(\d+)\s+(\d+)\/(\d+)$/);
    if (mixedMatch) {
        const whole = parseFloat(mixedMatch[1]);
        const num = parseFloat(mixedMatch[2]);
        const denom = parseFloat(mixedMatch[3]);
        return whole + num / denom;
    }
    
    // Обработка простых дробей (1/2)
    const simpleMatch = frac.match(/^(\d+)\/(\d+)$/);
    if (simpleMatch) {
        const num = parseFloat(simpleMatch[1]);
        const denom = parseFloat(simpleMatch[2]);
        return num / denom;
    }
    
    throw new Error("Invalid fraction format");
}