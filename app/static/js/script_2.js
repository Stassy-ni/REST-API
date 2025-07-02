// Глобальная переменная для хранения текущих задач
let currentTasks = [];

function generateTest() {
    const testOutput = document.getElementById('testOutput');
    testOutput.innerHTML = '<h2>Задания по сложению обыкновенных дробей</h2> <p><i>Примечание: при вводе ответа, обыкновенные дроби пишите через / , например, 1/2, а смешанные числа через пробел x y/z, например, 2 3/5.</i></p>';
    
    // Генерируем 5 случайных задач разного уровня сложности
    currentTasks = [
        generateSimpleAdditionTask(),       // Простое сложение с одинаковыми знаменателями
        generateDifferentDenominatorsTask(), // Разные знаменатели
        generateMixedNumbersTask(),         // Смешанные числа
        generateSimplificationTask(),       // Задача с сокращением
        generateComplexMixedNumbersTask()   // Сложные смешанные числа
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
    
    const userAnswer = answerInput.value.trim().replace(/\s+/g, ' ');
    const correctAnswers = task.answer.split(' или ').map(a => a.trim());
    
    // Функция проверки, является ли дробь правильной
    const isProperFraction = (fraction) => {
        const parts = fraction.split('/');
        if (parts.length !== 2) return true; // не дробь, считаем правильной
        
        const numerator = parseInt(parts[0]);
        const denominator = parseInt(parts[1]);
        
        if (isNaN(numerator) || isNaN(denominator)) return true;
        return numerator < denominator;
    };
    
    // Проверяем ответ пользователя
    let isCorrect = false;
    let needsMixedNumber = false;
    
    // Сначала проверяем на точное совпадение
    if (correctAnswers.some(correct => areFractionsEqual(userAnswer, correct))) {
        isCorrect = true;
    } 
    // Если нет точного совпадения, проверяем значение дроби
    else {
        try {
            const userValue = evalFraction(userAnswer);
            for (const correct of correctAnswers) {
                const correctValue = evalFraction(correct);
                if (Math.abs(userValue - correctValue) < 0.0001) {
                    // Проверяем, является ли дробь правильной
                    if (!isProperFraction(userAnswer)) {
                        needsMixedNumber = true;
                    } else {
                        isCorrect = true;
                    }
                    break;
                }
            }
        } catch (e) {
            // Ошибка парсинга - ответ неверный
        }
    }
    
    if (isCorrect) {
        feedbackElement.innerHTML = '<p class="correct">Правильно! Молодец!</p>';
        feedbackElement.classList.remove('hidden');
        stepsElement.classList.add('hidden');
    } else if (needsMixedNumber) {
        feedbackElement.innerHTML = '<p class="incorrect">Неправильно. Ваш ответ - неправильная дробь. Пожалуйста, представьте ответ в виде смешанной дроби.</p>';
        feedbackElement.classList.remove('hidden');
        stepsElement.classList.add('hidden');
    } else {
        feedbackElement.innerHTML = '<p class="incorrect">Неправильно. Давайте решим по шагам.</p>';
        feedbackElement.classList.remove('hidden');
        stepsElement.innerHTML = '';
        stepsElement.classList.remove('hidden');
        
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

// ===== ГЕНЕРАТОРЫ ЗАДАЧ =====

function generateSimpleAdditionTask() {
    const denominator = getRandomInt(2, 12);
    const numerator1 = getRandomInt(1, denominator - 1);
    const numerator2 = getRandomInt(1, denominator - 1);
    
    const sumNumerator = numerator1 + numerator2;
    const answer = simplifyFraction(`${sumNumerator}/${denominator}`);
    const answerMixed = toMixedNumber(answer);
    
    // Если дробь неправильная, добавляем смешанную форму как вариант ответа
    const finalAnswer = sumNumerator >= denominator ? `${answer} или ${answerMixed}` : answer;
    
    return {
        id: 'task-' + Date.now() + '-1',
        question: `Вычислите: <span class="math">${numerator1}/${denominator} + ${numerator2}/${denominator}</span>`,
        answer: finalAnswer,
        steps: [
            {
                question: `Сложите числители: ${numerator1} + ${numerator2} = ?`,
                answer: sumNumerator.toString()
            },
            {
                question: `Запишите результат с тем же знаменателем: <span class="math">?/${denominator}</span>`,
                answer: sumNumerator.toString()
            },
            ...(answer !== `${sumNumerator}/${denominator}` ? [{
                question: `Сократите дробь (если возможно): <span class="math">${sumNumerator}/${denominator} = ?</span>`,
                answer: answer
            }] : []),
            ...(sumNumerator >= denominator ? [{
                question: `Преобразуйте в смешанную дробь (если нужно): <span class="math">${sumNumerator}/${denominator} = ?</span>`,
                answer: answerMixed
            }] : [])
        ]
    };
}

function generateDifferentDenominatorsTask() {
    const denom1 = getRandomInt(2, 8);
    const denom2 = getRandomInt(2, 8);
    const numerator1 = getRandomInt(1, denom1 - 1);
    const numerator2 = getRandomInt(1, denom2 - 1);
    
    const lcm = findLCM(denom1, denom2);
    const newNum1 = numerator1 * (lcm / denom1);
    const newNum2 = numerator2 * (lcm / denom2);
    
    const sumNumerator = newNum1 + newNum2;
    const answer = simplifyFraction(`${sumNumerator}/${lcm}`);
    const answerMixed = toMixedNumber(answer);
    
    // Если дробь неправильная, добавляем смешанную форму как вариант ответа
    const finalAnswer = sumNumerator >= lcm ? `${answer} или ${answerMixed}` : answer;
    
    return {
        id: 'task-' + Date.now() + '-2',
        question: `Вычислите: <span class="math">${numerator1}/${denom1} + ${numerator2}/${denom2}</span>`,
        answer: finalAnswer,
        steps: [
            {
                question: `Найдите НОК знаменателей ${denom1} и ${denom2}: НОК(${denom1},${denom2}) = ?`,
                answer: lcm.toString()
            },
            {
                question: `Приведите первую дробь к общему знаменателю: <span class="math">${numerator1}/${denom1} = ?/${lcm}</span>`,
                answer: newNum1.toString()
            },
            {
                question: `Приведите вторую дробь к общему знаменателю: <span class="math">${numerator2}/${denom2} = ?/${lcm}</span>`,
                answer: newNum2.toString()
            },
            {
                question: `Сложите числители: ${newNum1} + ${newNum2} = ?`,
                answer: sumNumerator.toString()
            },
            {
                question: `Запишите результат: <span class="math">?/${lcm}</span>`,
                answer: sumNumerator.toString()
            },
            ...(answer !== `${sumNumerator}/${lcm}` ? [{
                question: `Сократите дробь (если возможно): <span class="math">${sumNumerator}/${lcm} = ?</span>`,
                answer: answer
            }] : []),
            ...(sumNumerator >= lcm ? [{
                question: `Преобразуйте в смешанную дробь (если нужно): <span class="math">${sumNumerator}/${lcm} = ?</span>`,
                answer: answerMixed
            }] : [])
        ]
    };
}

function generateMixedNumbersTask() {
    const whole1 = getRandomInt(1, 3);
    const whole2 = getRandomInt(1, 3);
    const denom1 = getRandomInt(2, 6);
    const denom2 = getRandomInt(2, 6);
    const numerator1 = getRandomInt(1, denom1 - 1);
    const numerator2 = getRandomInt(1, denom2 - 1);
    
    const improperNum1 = whole1 * denom1 + numerator1;
    const improperNum2 = whole2 * denom2 + numerator2;
    
    const lcm = findLCM(denom1, denom2);
    const newNum1 = improperNum1 * (lcm / denom1);
    const newNum2 = improperNum2 * (lcm / denom2);
    
    const sumNumerator = newNum1 + newNum2;
    const answerFraction = simplifyFraction(`${sumNumerator}/${lcm}`);
    const answerMixed = toMixedNumber(answerFraction);
    
    // Всегда предлагаем оба варианта для смешанных чисел
    const finalAnswer = `${answerFraction} или ${answerMixed}`;
    
    return {
        id: 'task-' + Date.now() + '-3',
        question: `Вычислите: <span class="math">${whole1} ${numerator1}/${denom1} + ${whole2} ${numerator2}/${denom2}</span>`,
        answer: finalAnswer,
        steps: [
            {
                question: `Переведите смешанные дроби в неправильные: <span class="math">${whole1} ${numerator1}/${denom1} = ?/${denom1}</span>`,
                answer: improperNum1.toString()
            },
            {
                question: `Переведите вторую дробь: <span class="math">${whole2} ${numerator2}/${denom2} = ?/${denom2}</span>`,
                answer: improperNum2.toString()
            },
            {
                question: `Найдите НОК знаменателей ${denom1} и ${denom2}: НОК(${denom1},${denom2}) = ?`,
                answer: lcm.toString()
            },
            {
                question: `Приведите первую дробь к общему знаменателю: <span class="math">${improperNum1}/${denom1} = ?/${lcm}</span>`,
                answer: newNum1.toString()
            },
            {
                question: `Приведите вторую дробь к общему знаменателю: <span class="math">${improperNum2}/${denom2} = ?/${lcm}</span>`,
                answer: newNum2.toString()
            },
            {
                question: `Сложите числители: ${newNum1} + ${newNum2} = ?`,
                answer: sumNumerator.toString()
            },
            {
                question: `Запишите результат: <span class="math">?/${lcm}</span>`,
                answer: sumNumerator.toString()
            },
            ...(answerFraction !== `${sumNumerator}/${lcm}` ? [{
                question: `Сократите дробь (если возможно): <span class="math">${sumNumerator}/${lcm} = ?</span>`,
                answer: answerFraction
            }] : []),
            {
                question: `Преобразуйте в смешанную дробь: <span class="math">${sumNumerator}/${lcm} = ?</span>`,
                answer: answerMixed
            }
        ]
    };
}

function generateSimplificationTask() {
    const denom1 = getRandomInt(4, 12);
    const denom2 = getRandomInt(2, 6);
    const numerator1 = getRandomInt(1, denom1 - 1);
    let numerator2 = getRandomInt(1, denom2 - 1);
    
    // Убедимся, что вторую дробь можно сократить
    const gcd = findGCD(numerator2, denom2);
    if (gcd === 1) {
        numerator2 = Math.floor(numerator2 / 2) * 2;
    }
    
    const simplifiedNum = numerator2 / findGCD(numerator2, denom2);
    const simplifiedDenom = denom2 / findGCD(numerator2, denom2);
    
    const lcm = findLCM(denom1, simplifiedDenom);
    const newNum1 = numerator1 * (lcm / denom1);
    const newNum2 = simplifiedNum * (lcm / simplifiedDenom);
    
    const sumNumerator = newNum1 + newNum2;
    const answer = simplifyFraction(`${sumNumerator}/${lcm}`);
    const answerMixed = toMixedNumber(answer);
    
    // Если дробь неправильная, добавляем смешанную форму как вариант ответа
    const finalAnswer = sumNumerator >= lcm ? `${answer} или ${answerMixed}` : answer;
    
    return {
        id: 'task-' + Date.now() + '-4',
        question: `Вычислите: <span class="math">${numerator1}/${denom1} + ${numerator2}/${denom2}</span>`,
        answer: finalAnswer,
        steps: [
            {
                question: `Сократите вторую дробь: <span class="math">${numerator2}/${denom2} = ?</span>`,
                answer: `${simplifiedNum}/${simplifiedDenom}`
            },
            {
                question: `Найдите НОК знаменателей ${denom1} и ${simplifiedDenom}: НОК(${denom1},${simplifiedDenom}) = ?`,
                answer: lcm.toString()
            },
            {
                question: `Приведите первую дробь к общему знаменателю: <span class="math">${numerator1}/${denom1} = ?/${lcm}</span>`,
                answer: newNum1.toString()
            },
            {
                question: `Приведите вторую дробь к общему знаменателю: <span class="math">${simplifiedNum}/${simplifiedDenom} = ?/${lcm}</span>`,
                answer: newNum2.toString()
            },
            {
                question: `Сложите числители: ${newNum1} + ${newNum2} = ?`,
                answer: sumNumerator.toString()
            },
            {
                question: `Запишите результат: <span class="math">?/${lcm}</span>`,
                answer: sumNumerator.toString()
            },
            ...(answer !== `${sumNumerator}/${lcm}` ? [{
                question: `Сократите дробь (если возможно): <span class="math">${sumNumerator}/${lcm} = ?</span>`,
                answer: answer
            }] : []),
            ...(sumNumerator >= lcm ? [{
                question: `Преобразуйте в смешанную дробь (если нужно): <span class="math">${sumNumerator}/${lcm} = ?</span>`,
                answer: answerMixed
            }] : [])
        ]
    };
}

function generateComplexMixedNumbersTask() {
    const whole1 = getRandomInt(2, 5);
    const whole2 = getRandomInt(1, whole1);
    const denom1 = getRandomInt(3, 8);
    const denom2 = getRandomInt(3, 8);
    const numerator1 = getRandomInt(1, denom1 - 1);
    const numerator2 = getRandomInt(1, denom2 - 1);
    
    const improperNum1 = whole1 * denom1 + numerator1;
    const improperNum2 = whole2 * denom2 + numerator2;
    
    const lcm = findLCM(denom1, denom2);
    const newNum1 = improperNum1 * (lcm / denom1);
    const newNum2 = improperNum2 * (lcm / denom2);
    
    const sumNumerator = newNum1 + newNum2;
    const answerFraction = simplifyFraction(`${sumNumerator}/${lcm}`);
    const answerMixed = toMixedNumber(answerFraction);
    
    // Всегда предлагаем оба варианта для сложных смешанных чисел
    const finalAnswer = `${answerFraction} или ${answerMixed}`;
    
    return {
        id: 'task-' + Date.now() + '-5',
        question: `Вычислите: <span class="math">${whole1} ${numerator1}/${denom1} + ${whole2} ${numerator2}/${denom2}</span>`,
        answer: finalAnswer,
        steps: [
            {
                question: `Переведите смешанные дроби в неправильные: <span class="math">${whole1} ${numerator1}/${denom1} = ?/${denom1}</span>`,
                answer: improperNum1.toString()
            },
            {
                question: `Переведите вторую дробь: <span class="math">${whole2} ${numerator2}/${denom2} = ?/${denom2}</span>`,
                answer: improperNum2.toString()
            },
            {
                question: `Найдите НОК знаменателей ${denom1} и ${denom2}: НОК(${denom1},${denom2}) = ?`,
                answer: lcm.toString()
            },
            {
                question: `Приведите первую дробь к общему знаменателю: <span class="math">${improperNum1}/${denom1} = ?/${lcm}</span>`,
                answer: newNum1.toString()
            },
            {
                question: `Приведите вторую дробь к общему знаменателю: <span class="math">${improperNum2}/${denom2} = ?/${lcm}</span>`,
                answer: newNum2.toString()
            },
            {
                question: `Сложите числители: ${newNum1} + ${newNum2} = ?`,
                answer: sumNumerator.toString()
            },
            {
                question: `Запишите результат: <span class="math">?/${lcm}</span>`,
                answer: sumNumerator.toString()
            },
            ...(answerFraction !== `${sumNumerator}/${lcm}` ? [{
                question: `Сократите дробь (если возможно): <span class="math">${sumNumerator}/${lcm} = ?</span>`,
                answer: answerFraction
            }] : []),
            {
                question: `Преобразуйте в смешанную дробь: <span class="math">${sumNumerator}/${lcm} = ?</span>`,
                answer: answerMixed
            }
        ]
    };
}

// ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

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
        const val1 = evalFraction(frac1);
        const val2 = evalFraction(frac2);
        return Math.abs(val1 - val2) < 0.0001;
    } catch (e) {
        return false;
    }
}

function evalFraction(frac) {
    if (!isNaN(frac)) return parseFloat(frac);
    
    const mixedMatch = frac.match(/^(\d+)\s+(\d+)\/(\d+)$/);
    if (mixedMatch) {
        const whole = parseFloat(mixedMatch[1]);
        const num = parseFloat(mixedMatch[2]);
        const denom = parseFloat(mixedMatch[3]);
        return whole + num / denom;
    }
    
    const simpleMatch = frac.match(/^(\d+)\/(\d+)$/);
    if (simpleMatch) {
        const num = parseFloat(simpleMatch[1]);
        const denom = parseFloat(simpleMatch[2]);
        return num / denom;
    }
    
    throw new Error("Invalid fraction format");
}