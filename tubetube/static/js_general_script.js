var socket = io();
const folderSelect = document.getElementById('folder-location-select');
const mediaTypeSwitch = document.getElementById('media-type-switch');
const downloadButton = document.getElementById('download-button');
const spinnerBorder = document.getElementById('spinner-border');

let folderData = {
    audio: {},
    video: {}
};

function populateDropdown() {
    folderSelect.innerHTML = '<option value="" selected>Select folder location</option>';

    const dataToUse = mediaTypeSwitch.checked ? folderData.audio : folderData.video;

    Object.keys(dataToUse).forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        folderSelect.appendChild(option);
    });

    const selectedFolder = localStorage.getItem('selectedFolder');
    if (selectedFolder && dataToUse[selectedFolder]) {
        folderSelect.value = selectedFolder;
    } else {
        folderSelect.value = '';
    }
}

function saveSelection() {
    localStorage.setItem('selectedFolder', folderSelect.value);
    localStorage.setItem('mediaType', mediaTypeSwitch.checked ? 'audio' : 'video');
}

socket.on('update_folder_locations', function (data) {
    folderData = data;
    mediaTypeSwitch.checked = localStorage.getItem('mediaType') === 'audio';
    populateDropdown();
});

mediaTypeSwitch.addEventListener('change', function () {
    populateDropdown();
    saveSelection();
});

folderSelect.addEventListener('change', saveSelection);

downloadButton.addEventListener('click', function () {
    const url = document.getElementById('download-url');

    if (!url.value.trim()) {
        alert('The URL is empty. Please provide a URL to download.');
        return;
    }

    const folderName = document.getElementById('folder-location-select').value;
    const audio_only = mediaTypeSwitch.checked;
    socket.emit('download', { url: url.value, folder_name: folderName, audio_only: audio_only });
    url.disabled = true;
    downloadButton.disabled = true
    spinnerBorder.style.display = 'inline-block';
    setTimeout(() => {
        spinnerBorder.style.display = 'none'
        url.value = '';
        url.disabled = false;
        downloadButton.disabled = false
    }, 5000);
});
