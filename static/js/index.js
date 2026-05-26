function showFlashMessage(message, category) {
    const flashContainer = document.createElement('div');
    flashContainer.className = `flash ${category}`;
    const escapedMessage = message
        .replace(/&/g, '%amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '%gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    flashContainer.innerHTML = `<strong>${category.charAt(0).toUpperCase() + category.slice(1)}:</strong> ${escapedMessage}`;
    const flashMessages = $('.flash-messages');
    if (!flashMessages) {
        console.error('Container .flash-messages not found in DOM');
        return;
    }
    $('.flash-messages').appendChild(flashContainer);
    setTimeout(() => {
        flashContainer.remove();
    }, 5000);
}

function $(selector) {
    return document.querySelector(selector);
}

async function getLatest() {
    const url = '/api/minecraft/latest';
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    if (result.success) {
        return result.latest;
    } else {
        throw new Error(result.error || 'Unknown error in latest version response');
    }
}

async function getVersionsList() {
    const url = '/api/minecraft/releases';
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    if (result.success) {
        return result.versions;
    } else {
        throw new Error(result.error || 'Unknown error in version list response');
    }
}

async function getData(data_type, version_id) {
    const url = `/api/minecraft/${data_type}/${version_id}`;
    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        if (result.success) {
            return result.data;
        } else {
            throw new Error(result.error || 'Unknown error in data response');
        }
    } catch (error) {
        console.error('Error fetching versions list:', error);
        showFlashMessage(`Failed to load versions: ${error.message}`, 'error');
        return [];
    }
}

async function initVersionSelect() {
    const versionSelect = $('#version')
    if (!versionSelect) return;

    const versions = await getVersionsList();
    versions.forEach(version => {
        const option = document.createElement('option');
        option.value = version;
        option.textContent = version;
        versionSelect.appendChild(option);
    });

    if (versions.length > 0) {
        versionSelect.value = versions[0];
    }
}

document.addEventListener('DOMContentLoaded', initVersionSelect);