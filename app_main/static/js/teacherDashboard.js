console.log('teacherDashboard.js загружен!'); // Для отладки

let class_id
let class_id_temp
$(document).ready(function () {
    console.log('DOM готов, jQuery работает'); // Добавлено для отладки
    // Проверяем доступность элементов
    if ($('#submitCreateClass').length === 0) {
        console.error('Кнопка #submitCreateClass не найдена!');
        return;
    }

    // Генерация случайных строк
    function generateRandomString(length, type = 'alphanumeric') {
        const chars = {
            alphanumeric: 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789',
            password: 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789!@#$%^&*'
        };

        let result = '';
        const characters = chars[type] || chars.alphanumeric;

        for (let i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        return result;
    }

    // Создание строки ученика
    function createStudentRow(fio, idx) {
        return `
            <div class="row mb-2 align-items-center student-row" data-idx="${idx}">
                <div class="col-md-10">
                    <input type="text" class="form-control" value="${fio}" readonly>
                </div>
                <div class="col-md-2 text-end">
                    <button type="button" class="btn btn-sm btn-outline-danger remove-student">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // Создание строки с учетными данными
    function createCredentialRow(student, idx) {
        return `
            <tr data-idx="${idx}">
                <td>${student.fio}</td>
                <td><input type="text" class="form-control form-control-sm login-input" 
                       value="${student.login}" data-original="${student.login}"></td>
                <td><input type="text" class="form-control form-control-sm password-input" 
                       value="${student.password}" data-original="${student.password}"></td>
            </tr>
        `;
    }

    // Создание класса
    $('#submitCreateClass').off('click').on('click', async function(e) {
        e.preventDefault();
        
        const form = $('#createClassForm');
        const grade = form.find('select[name="grade"]').val();
        const letter = form.find('input[name="letter"]').val().toUpperCase().slice(0, 1);

        if (!grade) {
            alert("Пожалуйста, выберите номер класса.");
            return;
        }

        try {
            // Показываем индикатор загрузки
            $('#submitCreateClass').prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Создание...');

            const response = await fetch('/teacher/create_class', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    grade: grade,
                    letter: letter || ''
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            if (!data.success) {
                throw new Error(data.error || 'Не удалось создать класс');
            }

            class_id = data.class_id;
            $('#addStudentsClassId').val(class_id);
            $('#addStudentsModal .modal-title').text(
                `Добавить учеников в ${grade}${letter ? '-' + letter : ''} класс`
            );
            
            // Закрываем текущее модальное окно и открываем следующее
            $('#createClassModal').modal('hide');
            $('#addStudentsModal').modal('show');
            
        } catch (error) {
            console.error('Ошибка при создании класса:', error);
            alert(`Произошла ошибка при создании класса: ${error.message}`);
        } finally {
            $('#submitCreateClass').prop('disabled', false).text('Далее');
        }
    });

        // 5. Возвращаемся к первому модальному окну
        //$('#createClassModal').modal('hide');
        //$('#addStudentsClassId').val(class_id);
        //$('#addStudentsModal .modal-title').text(`Добавить учеников в ${grade}${letter ? '-' + letter : ''} класс`);
        //$('#addStudentsModal').modal('show');
    //});

    // Парсинг ФИО из текстового поля
    $('#parseFio').click(function () {
        const lines = $('#bulkInput').val().trim().split('\n');
        const studentsList = $('#studentsList');
        studentsList.empty();

        lines.forEach((line, idx) => {
            if (line.trim()) {
                studentsList.append(createStudentRow(line.trim(), idx));
            }
        });

        if ($('#studentsList .student-row').length > 0) {
            $('#add-bulk-section').hide();
        }
    });

    // Удаление ученика
    $(document).on('click', '.remove-student', function () {
        $(this).closest('.student-row').remove();
        if ($('#studentsList .student-row').length === 0) {
            $('#add-bulk-section').show();
        }
    });

    // Генерация учетных данных
    $('#generateCredentials').click(function () {
        const students = [];
        $('#studentsList .student-row').each(function () {
            const fio = $(this).find('input').val().trim();
            if (fio) {
                students.push({
                    fio: fio,
                    login: generateRandomString(8),
                    password: generateRandomString(10, 'password')
                });
            }
        });

        if (students.length === 0) {
            alert('Пожалуйста, добавьте хотя бы одного ученика.');
            return;
        }

        const tableBody = $('#credentialsTableBody');
        tableBody.empty();

        students.forEach((student, idx) => {
            tableBody.append(createCredentialRow(student, idx));
        });

        $('#addStudentsModal').modal('hide');
        $('#confirmStudentsModal').modal('show');
    });

    // Регистрация учеников
    $('#registerStudents').click(async function () {
        const students = [];
        $('#credentialsTableBody tr').each(function () {
            const fio = $(this).find('td:first').text();
            const login = $(this).find('.login-input').val();
            const password = $(this).find('.password-input').val();

            students.push({
                fio: fio,
                login: login,
                password: password
            });
        });

        const classId = $('#addStudentsClassId').val();

        try {
            const response = await fetch(`/teacher/add_students`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    class_id: classId,
                    students: students
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Неизвестная ошибка');
            }

            if (data.status === 'success') {
                $('#confirmStudentsModal').modal('hide');
                alert(`Успешно зарегистрировано ${students.length} учеников!`);
                
                // Обновляем страницу, чтобы показать новый класс
                window.location.reload();
            } else {
                throw new Error(data.error || 'Не удалось добавить учеников');
            }
        } catch (error) {
            console.error('Ошибка при регистрации учеников:', error);
            alert(`Произошла ошибка: ${error.message}`);
        }


        $('#confirmStudentsModal').modal('hide');

        // Для демонстрации просто закрываем модальное окно
        $('#confirmStudentsModal').modal('hide');
        alert(`Успешно зарегистрировано ${students.length} учеников!`);
    });

    // Валидация измененных логинов
    $(document).on('change', '.login-input', function () {
        const newValue = $(this).val();
        const original = $(this).data('original');

        if (!newValue || newValue.length < 4) {
            alert('Логин должен содержать минимум 4 символа');
            $(this).val(original);
        }
    });

// Добавляем обработку ошибок загрузки скрипта
window.addEventListener('error', function(e) {
    console.error('Ошибка в скрипте:', e.message, 'в', e.filename, 'строка', e.lineno);
});

});