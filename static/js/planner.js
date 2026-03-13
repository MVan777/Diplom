document.addEventListener('DOMContentLoaded', function() {
    // Элементы
    const taskModal = document.getElementById('taskModal');
    const multipleTaskModal = document.getElementById('multipleTaskModal');
    const quickAddBtn = document.getElementById('quickAddBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const closeMultipleModalBtn = document.getElementById('closeMultipleModalBtn');
    const cancelMultipleBtn = document.getElementById('cancelMultipleBtn');
    const taskForm = document.getElementById('taskForm');
    const multipleTaskForm = document.getElementById('multipleTaskForm');
    const addTaskButtons = document.querySelectorAll('.add-task-btn');
    const addMultipleBtn = document.getElementById('addMultipleBtn');
    const addAnotherTaskBtn = document.getElementById('addAnotherTaskBtn');
    const tasksContainer = document.getElementById('tasksContainer');
    const globalSearch = document.getElementById('globalSearch');

    // Получаем URL из data-атрибута
    const searchUrl = document.body.dataset.searchUrl;

    // Функции модального окна
    function openModal(priority = 'average') {
        taskModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        const prioritySelect = taskForm?.querySelector('select[name="priority"]');
        if (prioritySelect) prioritySelect.value = priority;

        const deadlineInput = taskForm?.querySelector('input[name="deadline"]');
        if (deadlineInput) {
            function formatLocal(dt) {
                const pad = n => String(n).padStart(2, '0');
                return dt.getFullYear() + '-' + pad(dt.getMonth() + 1) + '-' + pad(dt.getDate()) + 'T' + pad(dt.getHours()) + ':' + pad(dt.getMinutes());
            }
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setHours(18, 0, 0, 0);
            deadlineInput.value = formatLocal(tomorrow);
            deadlineInput.min = formatLocal(new Date());
        }
    }

    function closeModal() {
        taskModal.style.display = 'none';
        document.body.style.overflow = 'auto';
        taskForm?.reset();
    }

    function openMultipleModal() {
        multipleTaskModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        function formatLocal(dt) {
            const pad = n => String(n).padStart(2, '0');
            return dt.getFullYear() + '-' + pad(dt.getMonth() + 1) + '-' + pad(dt.getDate()) + 'T' + pad(dt.getHours()) + ':' + pad(dt.getMinutes());
        }

        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(18, 0, 0, 0);
        const tomorrowStr = formatLocal(tomorrow);

        const dateInputs = multipleTaskForm?.querySelectorAll('input[type="datetime-local"]');
        dateInputs?.forEach(input => {
            input.value = tomorrowStr;
            input.min = formatLocal(new Date());
        });
    }

    function closeMultipleModal() {
        multipleTaskModal.style.display = 'none';
        document.body.style.overflow = 'auto';
        multipleTaskForm?.reset();

        const taskForms = tasksContainer?.querySelectorAll('.task-item-form');
        if (taskForms) {
            for (let i = 1; i < taskForms.length; i++) {
                tasksContainer.removeChild(taskForms[i]);
            }
        }
    }

    // Обработчики событий
    if (quickAddBtn) quickAddBtn.addEventListener('click', () => openModal());
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    if (closeMultipleModalBtn) closeMultipleModalBtn.addEventListener('click', closeMultipleModal);
    if (cancelMultipleBtn) cancelMultipleBtn.addEventListener('click', closeMultipleModal);
    if (addMultipleBtn) addMultipleBtn.addEventListener('click', openMultipleModal);

    addTaskButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const priority = btn.getAttribute('data-priority');
            openModal(priority);
        });
    });

    // Добавление еще одной задачи
    if (addAnotherTaskBtn) {
        addAnotherTaskBtn.addEventListener('click', () => {
            const newTaskForm = document.createElement('div');
            newTaskForm.className = 'task-item-form';
            newTaskForm.innerHTML = `
                <div class="form-group">
                    <input type="text" name="titles[]" class="form-input" placeholder="Название задачи" required>
                </div>
                <div class="form-group">
                    <input type="datetime-local" name="deadlines[]" class="form-input" required>
                </div>
                <div class="form-group">
                    <select name="priorities[]" class="form-select">
                        <option value="ordinary">Обычный</option>
                        <option value="average" selected>Средний</option>
                        <option value="urgent">Срочный</option>
                    </select>
                </div>
                <button type="button" class="remove-task-btn">
                    <i class="fas fa-trash"></i> Удалить
                </button>
            `;

            tasksContainer.appendChild(newTaskForm);

            function formatLocal(dt) {
                const pad = n => String(n).padStart(2, '0');
                return dt.getFullYear() + '-' + pad(dt.getMonth() + 1) + '-' + pad(dt.getDate()) + 'T' + pad(dt.getHours()) + ':' + pad(dt.getMinutes());
            }
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setHours(18, 0, 0, 0);
            const tomorrowStr = formatLocal(tomorrow);
            newTaskForm.querySelector('input[type="datetime-local"]').value = tomorrowStr;
            newTaskForm.querySelector('input[type="datetime-local"]').min = formatLocal(new Date());

            newTaskForm.querySelector('.remove-task-btn').addEventListener('click', function() {
                if (tasksContainer.querySelectorAll('.task-item-form').length > 1) {
                    tasksContainer.removeChild(newTaskForm);
                }
            });
        });
    }

    // Закрытие по клику вне окна
    [taskModal, multipleTaskModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    if (modal === taskModal) closeModal();
                    if (modal === multipleTaskModal) closeMultipleModal();
                }
            });
        }
    });

    // Поиск - используем URL из data-атрибута
    if (globalSearch && searchUrl) {
        globalSearch.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                const searchTerm = this.value.trim();
                if (searchTerm) {
                    window.location.href = `${searchUrl}?search=${encodeURIComponent(searchTerm)}`;
                }
            }
        });
    }
});