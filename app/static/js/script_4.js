// Глобальная переменная для хранения текущих задач
        let currentTasks = [];

        function generateTest() {
            const testOutput = document.getElementById('testOutput');
            testOutput.innerHTML = '<h2>Задания по умножению дробей</h2> <p><i>Примечание: при вводе ответа, обыкновенные дроби пишите через / , например, 1/2, а смешанные числа через пробел x y/z, например, 2 3/5.</i></p>';
            
            // Генерируем 5 случайных задач разного уровня сложности
            currentTasks = [
                generateSimpleMultiplicationTask(),    // Простое умножение обыкновенных дробей
                generateMixedNumbersTask(),          // Смешанные числа
                generateSimplificationTask(),        // Задача с сокращением
                generateComplexMultiplicationTask(), // Умножение с разными знаменателями
                generateComplexMixedNumbersTask()    // Сложные смешанные числа
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

        // Функции для генерации задач УМНОЖЕНИЯ
        function generateSimpleMultiplicationTask() {
            const denom1 = getRandomInt(2, 12);
            const denom2 = getRandomInt(2, 12);
            const numerator1 = getRandomInt(1, denom1 - 1);
            const numerator2 = getRandomInt(1, denom2 - 1);
            
            const rawNumerator = numerator1 * numerator2;
            const rawDenominator = denom1 * denom2;
            const answer = simplifyFraction(`${rawNumerator}/${rawDenominator}`);
            
            return {
                id: 'task-' + Date.now() + '-1',
                question: `Вычислите: <span class="math">${numerator1}/${denom1} × ${numerator2}/${denom2}</span>`,
                answer: answer,
                steps: [
                    {
                        question: `Умножьте числители: ${numerator1} × ${numerator2} = ?`,
                        answer: rawNumerator.toString()
                    },
                    {
                        question: `Умножьте знаменатели: ${denom1} × ${denom2} = ?`,
                        answer: rawDenominator.toString()
                    },
                    {
                        question: `Запишите результат: <span class="math">${rawNumerator}/${rawDenominator}</span>`,
                        answer: `${rawNumerator}/${rawDenominator}`
                    },
                    ...(answer !== `${rawNumerator}/${rawDenominator}` ? [{
                        question: `Сократите дробь: <span class="math">${rawNumerator}/${rawDenominator} = ?</span>`,
                        answer: answer
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
            
            const rawNumerator = improperNum1 * improperNum2;
            const rawDenominator = denom1 * denom2;
            const answerFraction = simplifyFraction(`${rawNumerator}/${rawDenominator}`);
            const answerMixed = toMixedNumber(answerFraction);
            
            return {
                id: 'task-' + Date.now() + '-2',
                question: `Вычислите: <span class="math">${whole1} ${numerator1}/${denom1} × ${whole2} ${numerator2}/${denom2}</span>`,
                answer: answerFraction.includes('/') && parseInt(answerFraction.split('/')[0]) > parseInt(answerFraction.split('/')[1]) ? 
                       `${answerFraction} или ${answerMixed}` : answerFraction,
                steps: [
                    {
                        question: `Переведите первую дробь в неправильную: <span class="math">${whole1} ${numerator1}/${denom1} = ?/${denom1}</span>`,
                        answer: improperNum1.toString()
                    },
                    {
                        question: `Переведите вторую дробь: <span class="math">${whole2} ${numerator2}/${denom2} = ?/${denom2}</span>`,
                        answer: improperNum2.toString()
                    },
                    {
                        question: `Умножьте числители: ${improperNum1} × ${improperNum2} = ?`,
                        answer: rawNumerator.toString()
                    },
                    {
                        question: `Умножьте знаменатели: ${denom1} × ${denom2} = ?`,
                        answer: rawDenominator.toString()
                    },
                    {
                        question: `Запишите результат: <span class="math">${rawNumerator}/${rawDenominator}</span>`,
                        answer: `${rawNumerator}/${rawDenominator}`
                    },
                    ...(answerFraction !== `${rawNumerator}/${rawDenominator}` ? [{
                        question: `Сократите дробь: <span class="math">${rawNumerator}/${rawDenominator} = ?</span>`,
                        answer: answerFraction
                    }] : []),
                    ...(answerMixed !== answerFraction && answerMixed !== `${rawNumerator}/${rawDenominator}` ? [{
                        question: `Преобразуйте в смешанную дробь: <span class="math">${answerFraction} = ?</span>`,
                        answer: answerMixed
                    }] : [])
                ]
            };
        }

        function generateSimplificationTask() {
            const denom1 = getRandomInt(2, 8);
            const denom2 = getRandomInt(2, 8);
            let numerator1 = getRandomInt(1, denom1 - 1);
            let numerator2 = getRandomInt(1, denom2 - 1);
            
            // Убедимся, что дроби можно сократить после умножения
            const gcd = findGCD(numerator1 * numerator2, denom1 * denom2);
            if (gcd === 1) {
                numerator1 = Math.floor(denom1 / 2);
                numerator2 = Math.floor(denom2 / 2);
            }
            
            const rawNumerator = numerator1 * numerator2;
            const rawDenominator = denom1 * denom2;
            const answer = simplifyFraction(`${rawNumerator}/${rawDenominator}`);
            
            return {
                id: 'task-' + Date.now() + '-3',
                question: `Вычислите: <span class="math">${numerator1}/${denom1} × ${numerator2}/${denom2}</span>`,
                answer: answer,
                steps: [
                    {
                        question: `Умножьте числители: ${numerator1} × ${numerator2} = ?`,
                        answer: rawNumerator.toString()
                    },
                    {
                        question: `Умножьте знаменатели: ${denom1} × ${denom2} = ?`,
                        answer: rawDenominator.toString()
                    },
                    {
                        question: `Запишите результат: <span class="math">${rawNumerator}/${rawDenominator}</span>`,
                        answer: `${rawNumerator}/${rawDenominator}`
                    },
                    {
                        question: `Сократите дробь: <span class="math">${rawNumerator}/${rawDenominator} = ?</span>`,
                        answer: answer
                    }
                ]
            };
        }

        function generateComplexMultiplicationTask() {
            const denom1 = getRandomInt(3, 8);
            const denom2 = getRandomInt(3, 8);
            let numerator1 = getRandomInt(1, denom1 - 1);
            let numerator2 = getRandomInt(1, denom2 - 1);
            
            // Убедимся, что есть возможность кросс-сокращения
            const crossGCD1 = findGCD(numerator1, denom2);
            const crossGCD2 = findGCD(numerator2, denom1);
            
            if (crossGCD1 === 1 && crossGCD2 === 1) {
                numerator1 = Math.floor(denom2 / 2);
                numerator2 = Math.floor(denom1 / 2);
            }
            
            const simplifiedNum1 = numerator1 / findGCD(numerator1, denom2);
            const simplifiedDenom2 = denom2 / findGCD(numerator1, denom2);
            const simplifiedNum2 = numerator2 / findGCD(numerator2, denom1);
            const simplifiedDenom1 = denom1 / findGCD(numerator2, denom1);
            
            const finalNumerator = simplifiedNum1 * simplifiedNum2;
            const finalDenominator = simplifiedDenom1 * simplifiedDenom2;
            const answer = simplifyFraction(`${finalNumerator}/${finalDenominator}`);
            
            return {
                id: 'task-' + Date.now() + '-4',
                question: `Вычислите: <span class="math">${numerator1}/${denom1} × ${numerator2}/${denom2}</span>`,
                answer: answer,
                steps: [
                    {
                        question: `Сократите ${numerator1} и ${denom2} (НОД = ${findGCD(numerator1, denom2)}): <span class="math">${numerator1}/${denom1} × ${numerator2}/${denom2} = ?/${simplifiedDenom1} × ?/${simplifiedDenom2}</span>`,
                        answer: `${simplifiedNum1}/${simplifiedDenom1} × ${simplifiedNum2}/${simplifiedDenom2}`
                    },
                    {
                        question: `Умножьте числители: ${simplifiedNum1} × ${simplifiedNum2} = ?`,
                        answer: finalNumerator.toString()
                    },
                    {
                        question: `Умножьте знаменатели: ${simplifiedDenom1} × ${simplifiedDenom2} = ?`,
                        answer: finalDenominator.toString()
                    },
                    {
                        question: `Запишите результат: <span class="math">${finalNumerator}/${finalDenominator}</span>`,
                        answer: `${finalNumerator}/${finalDenominator}`
                    },
                    ...(answer !== `${finalNumerator}/${finalDenominator}` ? [{
                        question: `Сократите дробь: <span class="math">${finalNumerator}/${finalDenominator} = ?</span>`,
                        answer: answer
                    }] : [])
                ]
            };
        }

        function generateComplexMixedNumbersTask() {
            const whole1 = getRandomInt(1, 3);
            const whole2 = getRandomInt(1, 3);
            const denom1 = getRandomInt(3, 8);
            const denom2 = getRandomInt(3, 8);
            const numerator1 = getRandomInt(1, denom1 - 1);
            const numerator2 = getRandomInt(1, denom2 - 1);
            
            const improperNum1 = whole1 * denom1 + numerator1;
            const improperNum2 = whole2 * denom2 + numerator2;
            
            // Кросс-сокращение
            const crossGCD1 = findGCD(improperNum1, denom2);
            const crossGCD2 = findGCD(improperNum2, denom1);
            
            const simplifiedNum1 = improperNum1 / crossGCD1;
            const simplifiedDenom2 = denom2 / crossGCD1;
            const simplifiedNum2 = improperNum2 / crossGCD2;
            const simplifiedDenom1 = denom1 / crossGCD2;
            
            const finalNumerator = simplifiedNum1 * simplifiedNum2;
            const finalDenominator = simplifiedDenom1 * simplifiedDenom2;
            const answerFraction = simplifyFraction(`${finalNumerator}/${finalDenominator}`);
            const answerMixed = toMixedNumber(answerFraction);
            
            return {
                id: 'task-' + Date.now() + '-5',
                question: `Вычислите: <span class="math">${whole1} ${numerator1}/${denom1} × ${whole2} ${numerator2}/${denom2}</span>`,
                answer: answerFraction.includes('/') && parseInt(answerFraction.split('/')[0]) > parseInt(answerFraction.split('/')[1]) ? 
                       `${answerFraction} или ${answerMixed}` : answerFraction,
                steps: [
                    {
                        question: `Переведите первую дробь в неправильную: <span class="math">${whole1} ${numerator1}/${denom1} = ?/${denom1}</span>`,
                        answer: improperNum1.toString()
                    },
                    {
                        question: `Переведите вторую дробь: <span class="math">${whole2} ${numerator2}/${denom2} = ?/${denom2}</span>`,
                        answer: improperNum2.toString()
                    },
                    {
                        question: `Сократите ${improperNum1} и ${denom2} (НОД = ${crossGCD1}): <span class="math">${improperNum1}/${denom1} × ${improperNum2}/${denom2} = ?/${simplifiedDenom1} × ?/${simplifiedDenom2}</span>`,
                        answer: `${simplifiedNum1}/${simplifiedDenom1} × ${simplifiedNum2}/${simplifiedDenom2}`
                    },
                    {
                        question: `Умножьте числители: ${simplifiedNum1} × ${simplifiedNum2} = ?`,
                        answer: finalNumerator.toString()
                    },
                    {
                        question: `Умножьте знаменатели: ${simplifiedDenom1} × ${simplifiedDenom2} = ?`,
                        answer: finalDenominator.toString()
                    },
                    {
                        question: `Запишите результат: <span class="math">${finalNumerator}/${finalDenominator}</span>`,
                        answer: `${finalNumerator}/${finalDenominator}`
                    },
                    ...(answerFraction !== `${finalNumerator}/${finalDenominator}` ? [{
                        question: `Сократите дробь: <span class="math">${finalNumerator}/${finalDenominator} = ?</span>`,
                        answer: answerFraction
                    }] : []),
                    ...(answerMixed !== answerFraction ? [{
                        question: `Преобразуйте в смешанную дробь: <span class="math">${answerFraction} = ?</span>`,
                        answer: answerMixed
                    }] : [])
                ]
            };
        }

        // Вспомогательные математические функции
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