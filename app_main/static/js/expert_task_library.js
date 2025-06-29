document.addEventListener('DOMContentLoaded', function() {
    // Переключение между кратким и полным видом задания
    document.querySelectorAll('.toggle-task').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const preview = row.querySelector('.task-preview');
            const full = row.querySelector('.task-full');
            
            if (preview.style.display === 'none') {
                preview.style.display = '';
                full.style.display = 'none';
                this.innerHTML = '<i class="bi bi-arrows-expand"></i>';
            } else {
                preview.style.display = 'none';
                full.style.display = '';
                this.innerHTML = '<i class="bi bi-arrows-collapse"></i>';
                
                // Обновляем MathJax для отображения формул
                if (window.MathJax) {
                    MathJax.typesetPromise([full]).catch(err => console.log('MathJax error:', err));
                }
            }
        });
    });

    // Фильтрация заданий
    const searchInput = document.getElementById('search-tasks');
    const categoryFilter = document.getElementById('filter-category');
    
    function filterTasks() {
        const searchText = searchInput.value.toLowerCase();
        const category = categoryFilter.value;
        
        document.querySelectorAll('#tasks-table-body tr').forEach(row => {
            const taskText = row.querySelector('.task-preview').textContent.toLowerCase();
            const taskCategory = row.getAttribute('data-category');
            
            const matchesSearch = taskText.includes(searchText);
            const matchesCategory = !category || taskCategory === category;
            
            row.style.display = (matchesSearch && matchesCategory) ? '' : 'none';
        });
    }
    
    searchInput.addEventListener('input', filterTasks);
    categoryFilter.addEventListener('change', filterTasks);

    // Удаление задания
    let taskToDelete = null;
    const deleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    
    document.querySelectorAll('.delete-task').forEach(btn => {
        btn.addEventListener('click', function() {
            taskToDelete = this.getAttribute('data-task-id');
            deleteModal.show();
        });
    });
    
    document.getElementById('confirm-delete-btn').addEventListener('click', async function() {
        if (taskToDelete) {
            try {
                const response = await fetch(`/expert/delete-task/${taskToDelete}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken() // Добавляем CSRF токен
                    }
                });

                // Проверяем, что ответ в JSON формате
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    const text = await response.text();
                    throw new Error(`Ожидался JSON, получено: ${text.substring(0, 100)}...`);
                }

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.message || 'Ошибка сервера');
                }

                // Успешное удаление
                const deletedRow = document.querySelector(`tr[data-task-id="${taskToDelete}"]`);
                if (deletedRow) {
                    deletedRow.remove();
                    
                    // Проверяем, остались ли задания
                    const remainingRows = document.querySelectorAll('#tasks-table-body tr:not(.no-tasks-row)');
                    if (remainingRows.length === 0) {
                        showNoTasksMessage();
                    }
                }

            } catch (error) {
                console.error('Ошибка при удалении:', error);
                alert(error.message);
            } finally {
                deleteModal.hide();
                taskToDelete = null;
            }
        }
    });

    // Функция для отображения сообщения "Нет заданий"
    function showNoTasksMessage() {
        const tbody = document.getElementById('tasks-table-body');
        if (!tbody.querySelector('.no-tasks-row')) {
            const row = document.createElement('tr');
            row.className = 'no-tasks-row';
            row.innerHTML = `
                <td colspan="5" class="text-center py-4 text-muted">
                    Нет сохраненных заданий
                </td>
            `;
            tbody.appendChild(row);
        }
    }

    // Функция для получения CSRF токена
    function getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.content : '';
    }
});