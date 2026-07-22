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

    // Получаем ID проекта из data-атрибута (если есть)
    const projectId = document.body.dataset.projectId;

    function openModal(priority = 'average') {
        taskModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        if (taskForm) {
            if (projectId) {

                taskForm.action = `/planner/create/?project=${projectId}`;
            } else {
                taskForm.action = `/planner/create/`;
            }
        }

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

        if (multipleTaskForm) {
            if (projectId) {
                multipleTaskForm.action = `/planner/create/?project=${projectId}`;
            } else {
                multipleTaskForm.action = `/planner/create/`;
            }
        }

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

// Функция сворачивания/разворачивания блока проектов
function toggleProjects() {
    const content = document.getElementById('projectsContent');
    const icon = document.getElementById('projectsToggleIcon');

    content.classList.toggle('collapsed');

    if (content.classList.contains('collapsed')) {
        icon.style.transform = 'rotate(-90deg)';
    } else {
        icon.style.transform = 'rotate(0deg)';
    }
}

// Сохраняем состояние в localStorage
document.addEventListener('DOMContentLoaded', function() {
    const projectsContent = document.getElementById('projectsContent');
    const projectsIcon = document.getElementById('projectsToggleIcon');

    // Проверяем сохраненное состояние
    const isCollapsed = localStorage.getItem('projectsCollapsed') === 'true';

    if (isCollapsed) {
        projectsContent.classList.add('collapsed');
        projectsIcon.style.transform = 'rotate(-90deg)';
    }

    // Обновляем функцию toggle для сохранения состояния
    window.toggleProjects = function() {
        const content = document.getElementById('projectsContent');
        const icon = document.getElementById('projectsToggleIcon');

        content.classList.toggle('collapsed');

        if (content.classList.contains('collapsed')) {
            icon.style.transform = 'rotate(-90deg)';
            localStorage.setItem('projectsCollapsed', 'true');
        } else {
            icon.style.transform = 'rotate(0deg)';
            localStorage.setItem('projectsCollapsed', 'false');
        }
    };
});


document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
    initializeDayClickHandler();
});

let currentDate = new Date();

function initializeCalendar() {
    const prevBtn = document.querySelector('.calendar-nav-btn:first-child');
    const nextBtn = document.querySelector('.calendar-nav-btn:last-child');

    if (prevBtn) {
        prevBtn.onclick = function(e) {
            e.preventDefault();
            changeMonth(-1);
        };
    }

    if (nextBtn) {
        nextBtn.onclick = function(e) {
            e.preventDefault();
            changeMonth(1);
        };
    }
}

function changeMonth(delta) {
    currentDate.setMonth(currentDate.getMonth() + delta);
    loadCalendarData();
}

function loadCalendarData() {
    const month = currentDate.getMonth() + 1;
    const year = currentDate.getFullYear();

    fetch(`/planner/api/calendar-data/?month=${month}&year=${year}`)
        .then(response => response.json())
        .then(data => {
            // Обновляем заголовок и дни одновременно
            updateCalendarHeader(data);

            // Сохраняем текущую прокрутку (если есть)
            const scrollPosition = window.scrollY;

            // Обновляем только дни
            renderCalendarDays(data.days);

            // Восстанавливаем прокрутку
            window.scrollTo(0, scrollPosition);
        })
        .catch(error => {
            console.error('Error loading calendar:', error);
        });
}

function showCalendarLoading() {
    const grid = document.getElementById('calendarGrid');
    if (grid) {
        grid.innerHTML = '<div class="calendar-loading">Загрузка...</div>';
    }
}

function showCalendarError() {
    const grid = document.getElementById('calendarGrid');
    if (grid) {
        grid.innerHTML = '<div class="calendar-error">Ошибка загрузки</div>';
    }
}

function updateCalendarHeader(data) {
    const monthNames = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ];
    const monthName = monthNames[currentDate.getMonth()];
    const year = currentDate.getFullYear();

    const headerElement = document.getElementById('currentMonth');
    if (headerElement) {
        headerElement.textContent = `${monthName} ${year}`;
    }
}

function renderCalendarDays(days) {
    const grid = document.getElementById('calendarGrid');
    if (!grid) return;

    grid.innerHTML = '';

    // Получаем первый день месяца (0 - понедельник, 6 - воскресенье)
    const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
    // Преобразуем (воскресенье = 0) в (понедельник = 0)
    const startOffset = firstDay === 0 ? 6 : firstDay - 1;

    // Добавляем пустые ячейки для выравнивания
    for (let i = 0; i < startOffset; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day empty';
        grid.appendChild(emptyDay);
    }

    // Добавляем дни месяца
    days.forEach(day => {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        if (day.has_tasks) dayElement.classList.add('has-tasks');
        if (day.is_today) dayElement.classList.add('today');

        dayElement.setAttribute('data-date', day.date);

        dayElement.innerHTML = `
            <span class="day-number">${day.day}</span>
            ${day.has_tasks ? `
                <div class="task-dots">
                    <span class="dot urgent-dot" title="Есть задачи"></span>
                    ${day.tasks_count > 1 ? `<span class="tasks-count">+${day.tasks_count - 1}</span>` : ''}
                </div>
            ` : ''}
        `;

        dayElement.onclick = () => showDayTasks(day.date);
        grid.appendChild(dayElement);
    });
}

function initializeDayClickHandler() {
    // Обработчик для закрытия модального окна
    const closeBtn = document.querySelector('#dayTasksModal .modal-close');
    if (closeBtn) {
        closeBtn.onclick = closeDayTasksModal;
    }

    // Закрытие по клику вне модального окна
    window.onclick = function(event) {
        const modal = document.getElementById('dayTasksModal');
        if (event.target == modal) {
            closeDayTasksModal();
        }
    };
}


window.showDayTasks = function(date) {
    console.log('showDayTasks called with date:', date);

    const modal = document.getElementById('dayTasksModal');
    const dateElement = document.getElementById('selectedDate');
    const tasksList = document.getElementById('dayTasksList');

    if (!modal || !dateElement || !tasksList) {
        console.error('Modal elements not found');
        return;
    }

    // Форматируем дату для отображения
    const [year, month, day] = date.split('-');
    const displayDate = new Date(year, month - 1, day).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    dateElement.textContent = displayDate;

    tasksList.innerHTML = '<div class="loading-spinner">Загрузка задач...</div>';
    modal.style.display = 'flex';

    const url = `/planner/api/day-tasks/?date=${date}`;
    console.log('Fetching from:', url);

    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Data received:', data);
        renderDayTasks(data.tasks);
    })
    .catch(error => {
        console.error('Error loading day tasks:', error);
        tasksList.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Ошибка загрузки задач</p>
                <p class="error-help">${error.message}</p>
            </div>
        `;
    });
};



function renderDayTasks(tasks) {
    const tasksList = document.getElementById('dayTasksList');
    const selectedDate = document.getElementById('selectedDate');

    if (!tasksList) return;

    if (!tasks || tasks.length === 0) {
        tasksList.innerHTML = `
            <div class="empty-tasks">
                <i class="fas fa-check-circle"></i>
                <p>На этот день нет задач</p>
                <button class="btn btn-primary btn-sm" onclick="createTaskForDate('${selectedDate ? selectedDate.textContent : ''}')">
                    <i class="fas fa-plus"></i> Создать задачу
                </button>
            </div>
        `;
        return;
    }

    let html = '<div class="tasks-list-mini">';

    tasks.forEach(task => {
        const priorityClass = task.priority === 'Срочный' ? 'urgent' :
                            task.priority === 'Средний' ? 'medium' : 'low';

        // Определяем статус
        let statusBadge = '';

        if (task.status === 'in_progress') {
            statusBadge = '<span class="status-badge status-in-progress"><i class="fas fa-play-circle"></i> В работе</span>';
        } else if (task.status === 'completed') {
            statusBadge = '<span class="status-badge status-completed"><i class="fas fa-check-circle"></i> Выполнено</span>';
        } else {
            statusBadge = '<span class="status-badge status-pending"><i class="fas fa-hourglass-half"></i> Ожидает</span>';
        }

        html += `
            <div class="task-mini-item ${priorityClass} ${task.is_completed ? 'completed' : ''}">
                <div class="task-mini-header">
                    <span class="task-mini-priority priority-${priorityClass}"></span>
                    <a href="${task.url}" class="task-mini-title">${escapeHtml(task.title)}</a>
                    <span class="task-mini-time">${task.deadline}</span>
                </div>
                <div class="task-mini-actions">
                    ${task.status === 'pending' ? `
                    <button onclick="changeTaskStatus(${task.id}, 'start')" class="task-action-start" title="Начать работу">
                        <i class="fas fa-play"></i>
                    </button>
                    ` : ''}
                    ${task.status === 'in_progress' ? `
                    <button onclick="changeTaskStatus(${task.id}, 'pause')" class="task-action-pause" title="Приостановить">
                        <i class="fas fa-pause"></i>
                    </button>
                    ` : ''}
                    ${task.status !== 'completed' ? `
                    <button onclick="changeTaskStatus(${task.id}, 'complete')" class="task-action-complete" title="Выполнить">
                        <i class="fas fa-check"></i>
                    </button>
                    ` : ''}
                    <a href="${task.url}edit/" class="task-action-edit" title="Редактировать" onclick="event.stopPropagation();">
                        <i class="fas fa-edit"></i>
                    </a>
                </div>
                <div class="task-mini-footer">
                    ${statusBadge}
                </div>
            </div>
        `;
    });

    html += `
        <div class="tasks-mini-footer">
            <button class="btn btn-primary btn-sm" onclick="createTaskForDate('${selectedDate ? selectedDate.textContent : ''}')">
                <i class="fas fa-plus"></i> Добавить задачу
            </button>
        </div>
    </div>`;

    tasksList.innerHTML = html;
}

// Функция для изменения статуса через API
function changeTaskStatus(taskId, action) {
    fetch(`/planner/api/task/${taskId}/status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCsrfToken()
        },
        body: `action=${action}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status) {
            // Обновляем текущее модальное окно
            const modal = document.getElementById('dayTasksModal');
            if (modal && modal.style.display === 'flex') {
                const date = document.getElementById('selectedDate').textContent;
                // Перезагружаем задачи
                const dateAttr = document.querySelector('.calendar-day.today')?.dataset.date;
                if (dateAttr) {
                    showDayTasks(dateAttr);
                }
            }
            // Перезагружаем страницу для обновления всех блоков
            setTimeout(() => location.reload(), 500);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при изменении статуса');
    });
}

// Функция для экранирования HTML (безопасность)
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Исправленная функция createTaskForDate
function createTaskForDate(dateStr, priority = 'average') {
    if (!dateStr || dateStr === '') return;

    // Сначала закрываем модальное окно с задачами дня
    closeDayTasksModal();

    // Преобразуем русскую дату обратно в формат
    const dateParts = dateStr.split(' ');
    if (dateParts.length < 3) {
        console.error('Invalid date format:', dateStr);
        return;
    }

    const day = dateParts[0];
    const month = dateParts[1];
    const year = dateParts[2];

    const monthNames = {
        'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
        'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
        'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
    };

    const monthNum = monthNames[month.toLowerCase()];
    if (monthNum) {
        const formattedDate = `${year}-${monthNum}-${String(day).padStart(2, '0')}`;

        const taskModal = document.getElementById('taskModal');
        if (taskModal) {
            // Устанавливаем дату
            const deadlineInput = document.querySelector('#taskForm input[name="deadline"]');
            if (deadlineInput) {
                deadlineInput.value = `${formattedDate}T18:00`;
                deadlineInput.min = new Date().toISOString().slice(0, 16);
            }

            // Устанавливаем приоритет (если передан)
            if (priority) {
                const prioritySelect = document.querySelector('#taskForm select[name="priority"]');
                if (prioritySelect) {
                    prioritySelect.value = priority;
                }
            }

            // Открываем модальное окно
            taskModal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        } else {
            window.location.href = `/planner/create/?deadline=${formattedDate}&priority=${priority}`;
        }
    }
}

// Обновите функцию showDayTasks для правильной обработки
window.showDayTasks = function(date) {
    console.log('showDayTasks called with date:', date);

    const modal = document.getElementById('dayTasksModal');
    const dateElement = document.getElementById('selectedDate');
    const tasksList = document.getElementById('dayTasksList');

    if (!modal || !dateElement || !tasksList) {
        console.error('Modal elements not found');
        return;
    }

    // Форматируем дату для отображения
    const [year, month, day] = date.split('-');
    const displayDate = new Date(year, month - 1, day).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    dateElement.textContent = displayDate;

    tasksList.innerHTML = '<div class="loading-spinner">Загрузка задач...</div>';
    modal.style.display = 'flex';

    const url = `/planner/api/day-tasks/?date=${date}`;
    console.log('Fetching from:', url);

    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Data received:', data);
        renderDayTasks(data.tasks);
    })
    .catch(error => {
        console.error('Error loading day tasks:', error);
        tasksList.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Ошибка загрузки задач</p>
                <p class="error-help">${error.message}</p>
                <button onclick="window.showDayTasks('${date}')" class="btn btn-sm btn-primary mt-2">
                    Повторить
                </button>
            </div>
        `;
    });
};

function closeDayTasksModal() {
    const modal = document.getElementById('dayTasksModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Обновляем функцию для переключения месяцев
function prevMonth() {
    changeMonth(-1);
}

function nextMonth() {
    changeMonth(1);
}

// Статистика и круговая диаграмма
function updateChart(period) {
    // Показываем загрузку
    const chartContainer = document.getElementById('pieChart');
    if (chartContainer) {
        chartContainer.style.opacity = '0.5';
    }

    // Отправляем запрос на сервер
    fetch(`/planner/api/chart-data/?period=${period}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Обновляем центральную статистику
            const totalTasksEl = document.querySelector('.total-tasks');
            if (totalTasksEl) totalTasksEl.textContent = data.total_tasks;

            // Обновляем легенду
            const completedCount = document.getElementById('completedCount');
            const completedPercent = document.getElementById('completedPercent');
            const overdueCount = document.getElementById('overdueCount');
            const overduePercent = document.getElementById('overduePercent');
            const pendingCount = document.getElementById('pendingCount');
            const pendingPercent = document.getElementById('pendingPercent');

            if (completedCount) completedCount.textContent = data.completed;
            if (completedPercent) completedPercent.textContent = `${data.completed_percent}%`;
            if (overdueCount) overdueCount.textContent = data.overdue;
            if (overduePercent) overduePercent.textContent = `${data.overdue_percent}%`;
            if (pendingCount) pendingCount.textContent = data.pending;
            if (pendingPercent) pendingPercent.textContent = `${data.pending_percent}%`;

            // Обновляем детальную статистику
            const statValues = document.querySelectorAll('.stat-item .stat-value');
            if (statValues.length >= 2) {
                statValues[0].textContent = data.avg_completion_time;
                statValues[1].textContent = `${data.productivity}%`;
            }

            // Обновляем круговую диаграмму
            updatePieChart(data);

            // Убираем загрузку
            if (chartContainer) {
                chartContainer.style.opacity = '1';
            }
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
            if (chartContainer) {
                chartContainer.style.opacity = '1';
                chartContainer.innerHTML = `
                    <div style="text-align: center; color: #dc3545; padding: 20px;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Ошибка загрузки</p>
                        <button onclick="updateChart('${period}')" class="btn btn-sm">Повторить</button>
                    </div>
                `;
            }
        });
}

function updatePieChart(data) {
    const container = document.getElementById('pieChart');
    if (!container) return;

    const size = 200;
    const radius = 90;
    const center = size / 2;

    // Данные для диаграммы
    const segments = [
        { value: data.completed, color: '#28a745' },
        { value: data.overdue, color: '#dc3545' },
        { value: data.pending, color: '#ffc107' }
    ];

    // Фильтруем сегменты с value > 0
    const activeSegments = segments.filter(s => s.value > 0);

    if (activeSegments.length === 0 || data.total_tasks === 0) {
        container.innerHTML = `
            <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
                <circle cx="${center}" cy="${center}" r="${radius}"
                        fill="none" stroke="#e9ecef" stroke-width="20"/>
                <text x="${center}" y="${center}" text-anchor="middle"
                      dy=".3em" fill="#6c757d" font-size="14">
                    Нет данных
                </text>
            </svg>
        `;
        return;
    }

    // Вычисляем углы
    let currentAngle = -90;
    let paths = [];

    activeSegments.forEach(segment => {
        const angle = (segment.value / data.total_tasks) * 360;
        const endAngle = currentAngle + angle;

        const startRad = (currentAngle * Math.PI) / 180;
        const endRad = (endAngle * Math.PI) / 180;

        const x1 = center + radius * Math.cos(startRad);
        const y1 = center + radius * Math.sin(startRad);
        const x2 = center + radius * Math.cos(endRad);
        const y2 = center + radius * Math.sin(endRad);

        const largeArc = angle > 180 ? 1 : 0;

        const path = `M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;

        paths.push(`<path d="${path}" fill="${segment.color}" stroke="white" stroke-width="2"/>`);

        currentAngle = endAngle;
    });

    const svg = `
        <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
            ${paths.join('')}
            <circle cx="${center}" cy="${center}" r="${radius - 30}" fill="white"/>
        </svg>
    `;

    container.innerHTML = svg;
}