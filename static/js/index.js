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

class Autocomplete {
    constructor(inputId, suggestionsId, dataSource = [], onSelect = () => {}) {
        this.input = $(inputId);
        this.suggestionsList = $(suggestionsId);
        this.dataSource = dataSource;
        this.onSelect = onSelect;
        this.filteredItems = [];
        this.activeIndex = -1;

        this.setupEventListeners();
    }

    setupEventListeners() {
        this.input.addEventListener('input', (e) => this.updateSuggestions(e.target.value));
        this.input.addEventListener('blur', () => setTimeout(() => this.hideSuggestions(), 200));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));

        document.addEventListener('click', (e) => {
            if (this.input.contains(e.target) && !this.suggestionsList.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    updateSuggestions(searchTerm) {
        if (!searchTerm) {
            this.hideSuggestions();
            return;
        }

        this.filteredItems = this.dataSource.filter(item => 
            item.replace('minecraft:', '').toLowerCase().includes(searchTerm.toLowerCase())
        );

        this.renderSuggestions();
    }

    renderSuggestions() {
        this.suggestionsList.innerHTML = '';
        if (this.filteredItems.length === 0) {
            const li = document.createElement('li');
            li.className = 'suggestion-item';
            li.textContent = 'Ничего не найдено';
            this.suggestionsList.appendChild(li);
            this.showSuggestions();
            return;
        }

        this.filteredItems.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = `suggestions-item${index === this.activeIndex ? ' active' : ''}`;
            li.textContent = item.replace('minecraft:', '');
            li.addEventListener('click', () => this.selectItem(item));
            this.suggestionsList.appendChild(li);
        });

        this.scrollToActive();
        this.showSuggestions();
    }

    scrollToActive() {
        const activeItem = this.suggestionsList.querySelector('.suggestions-item.active');
        if (!activeItem) return;

        const container = this.suggestionsList;
        const itemTop = activeItem.offsetTop;
        const itemHeight = activeItem.offsetHeight;
        const containerHeight = container.clientHeight;
        const scrollTop = container.scrollTop;

        if (itemTop < scrollTop) {
            container.scrollTop = itemTop;
        } else if (itemTop + itemHeight > scrollTop + containerHeight) {
            container.scrollTop = itemTop + itemHeight - containerHeight;
        }
    }

    selectItem(item) {
        this.input.value = item.replace('minecraft:', '');
        this.hideSuggestions();
        this.onSelect(item);
    }

    showSuggestions() {
        this.suggestionsList.style.display = 'block';
    }

    hideSuggestions() {
        this.suggestionsList.style.display = 'none';
        this.activeIndex = -1;
    }

    handleKeydown(e) {
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.activeIndex = (this.activeIndex + 1) % this.filteredItems.length;
                this.renderSuggestions();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.activeIndex = this.activeIndex <= 0 ? this.filteredItems.length - 1 : this.activeIndex - 1;
                this.renderSuggestions();
                break;
            case 'Enter':
                e.preventDefault();
                if (this.activeIndex >= 0 && this.filteredItems[this.activeIndex]) {
                    e.preventDefault();
                    this.selectItem(this.filteredItems[this.activeIndex]);
                }
                break;
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }

    updateDataSource(newDataSource) {
        this.dataSource = newDataSource;
        const currentValue = this.input.value;
        if (currentValue) {
            this.updateSuggestions(currentValue);
        } else {
            this.hideSuggestions();
        }
    }
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