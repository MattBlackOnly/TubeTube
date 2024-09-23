const tableBody = document.getElementById('activity-table-body');
const template = document.getElementById('row-template');
const selectAll = document.getElementById('select-all');
const removeSelected = document.getElementById('remove-selected');
const removeCompleted = document.getElementById('remove-completed');
let lastChecked = null;

function updateSelectAllState() {
    const allCheckboxes = document.querySelectorAll('.row-select');
    const allChecked = Array.from(allCheckboxes).every(checkbox => checkbox.checked);
    const anyChecked = Array.from(allCheckboxes).some(checkbox => checkbox.checked);

    selectAll.checked = allChecked;
    selectAll.indeterminate = !allChecked && anyChecked;
}

function renderRow(data) {
    const row = document.importNode(template.content, true);
    const tr = row.querySelector('tr');

    const checkbox = tr.querySelector('.row-select');
    const uniqueId = `checkbox-${data.id}`;

    checkbox.setAttribute('id', uniqueId);
    checkbox.setAttribute('name', `row-select-${data.id}`);
    checkbox.addEventListener('change', updateSelectAllState);

    tr.setAttribute('data-id', data.id);
    tr.querySelector('.row-select').setAttribute('data-id', data.id);
    tr.querySelector('.id').textContent = data.id;
    tr.querySelector('.title').textContent = data.title;
    tr.querySelector('.status').textContent = data.status;
    tr.querySelector('.download-progress').textContent = data.progress;
    tableBody.appendChild(tr);
}

socket.on('update_download_list', (items) => {
    tableBody.innerHTML = '';
    for (const id in items) {
        renderRow(items[id]);
    }
});

socket.on('update_download_item', (update) => {
    const item = update.item;
    const row = document.querySelector(`tr[data-id='${item.id}']`);
    if (row) {
        row.querySelector('.status').textContent = item.status;
        row.querySelector('.download-progress').textContent = item.progress;
    }
});

socket.on('remove_download_item', (update) => {
    const row = document.querySelector(`tr[data-id='${update.id}']`);
    if (row) {
        row.remove();
    }

    const rowCount = document.querySelectorAll('#activity-table-body tr').length;
    if (rowCount === 0) {
        selectAll.checked = false;
    }
});

selectAll.addEventListener('change', function () {
    const isChecked = this.checked;
    document.querySelectorAll('.row-select').forEach(checkbox => {
        checkbox.checked = isChecked;
    });
});

removeSelected.addEventListener('click', function () {
    const removeIds = [];
    const cancelIds = [];

    document.querySelectorAll('.row-select:checked').forEach(checkbox => {
        const row = checkbox.closest('tr');
        const id = parseInt(row.getAttribute('data-id'), 10);
        const status = row.querySelector('.status').textContent.trim();

        if (status === 'In Progress' || status === 'Downloading' || status === 'Pending') {
            cancelIds.push(id);
        } else {
            removeIds.push(id);
        }
    });

    if (cancelIds.length > 0) {
        socket.emit('cancel_items', cancelIds);
    }
    if (removeIds.length > 0) {
        socket.emit('remove_items', removeIds);
    }
});

removeCompleted.addEventListener('click', function () {
    const completedIds = [];

    document.querySelectorAll('#activity-table-body tr').forEach(row => {
        const status = row.querySelector('.status').textContent.trim()
        if (status === 'Complete' || status === 'Cancelled') {
            const id = parseInt(row.getAttribute('data-id'), 10);
            completedIds.push(id);
            row.remove();
        }
    });

    if (completedIds.length > 0) {
        socket.emit('remove_items', completedIds);
    }
});

tableBody.addEventListener('click', function (event) {
    if (event.target.classList.contains('row-select')) {
        const currentCheckbox = event.target;

        if (event.shiftKey && lastChecked) {
            const checkboxes = Array.from(document.querySelectorAll('.row-select'));
            const start = checkboxes.indexOf(lastChecked);
            const end = checkboxes.indexOf(currentCheckbox);

            const range = checkboxes.slice(Math.min(start, end), Math.max(start, end) + 1);
            range.forEach(checkbox => {
                checkbox.checked = lastChecked.checked;
            });
        }

        lastChecked = currentCheckbox;
        updateSelectAllState();
        return;
    }

    const row = event.target.closest('tr');
    if (row) {
        const checkbox = row.querySelector('.row-select');
        if (checkbox) {
            checkbox.checked = !checkbox.checked;

            lastChecked = checkbox;
            updateSelectAllState();
        }
    }
});
