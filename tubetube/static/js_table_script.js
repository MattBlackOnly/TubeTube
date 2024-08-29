const tableBody = document.getElementById('activity-table-body');
const template = document.getElementById('row-template');
const selectAll = document.getElementById('select-all');
const removeSelected = document.getElementById('remove-selected');
const removeCompleted = document.getElementById('remove-completed');

function renderRow(data) {
    const row = document.importNode(template.content, true);
    const tr = row.querySelector('tr');

    const checkbox = tr.querySelector('.row-select');
    const uniqueId = `checkbox-${data.id}`;
    checkbox.setAttribute('id', uniqueId);
    checkbox.setAttribute('name', `row-select-${data.id}`);

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
        if (status === 'Completed' || status === 'Cancelled') {
            const id = parseInt(row.getAttribute('data-id'), 10);
            completedIds.push(id);
            row.remove();
        }
    });

    if (completedIds.length > 0) {
        socket.emit('remove_items', completedIds);
    }
});
