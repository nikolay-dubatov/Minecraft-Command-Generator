class GiveGenerator {
    constructor() {
        this.currentVersion = null;
        this.latest = null;
        this.items = [];
        this.autocomplete = null;
        this.bindEvents();
        this.init()
    }
    async init() {
        try {
            this.latest = await getLatest();
            this.currentVersion = this.latest;
            await this.loadItems(this.latest);
        } catch (error) {
            console.error("Failed to initialize GiveGenerator:", error);
            showFlashMessage("Не удалось загрузить данные: " + error.message, "error");
        }
    }
    async loadItems(version) {
        try {
            this.items = await getData('items', version);
            if (this.autocomplete) {
                this.autocomplete.updateDataSource(this.items)
            } else {
                this.initAutocomplete();
            }
        } catch (error) {
            console.error("Failed to load items: ", error);
        }
    }

    initAutocomplete() {
        this.autocomplete = new Autocomplete(
            '#item-search', 
            '#item-suggestions', 
            this.items, 
            (selectedItem) => {
                const hiddenInput = $('#selected-item');
                if (hiddenInput) {
                    hiddenInput.value = selectedItem;
                }
                console.log("Выбран предмет:", selectedItem);
            }
        );
    }

    bindEvents() {
        const versionSelect = $('#version');
        const form = $('#give-form')

        if (versionSelect) {
            versionSelect.addEventListener('change', async (e) => {
                this.currentVersion = e.target.value;
                await this.loadItems(this.currentVersion);
            });
        } else {
            console.error("Element #version not found");
        }
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.generateGiveCommand();
            });
        } else {
            console.error('Element #give-form not found')
        }
    }
    async generateGiveCommand() {
        const formData = new FormData($('#give-form'))
        const data = Object.fromEntries(formData);

        const hiddenItem = $('#selected-item');
        if (hiddenItem && hiddenItem.value) {
            data.item = hiddenItem.value;
        }

        try {
            const response = await fetch('/generate/give', {
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                $('#result').innerHTML = 
                    `<div class="command-box"><strong>Сгенерированная команда: </strong><br><code>${result.command}</code></div>`;
                showFlashMessage(result.message, 'success');
            } else {
                showFlashMessage(result.error, 'error');
            }
        } catch (error) {
            showFlashMessage('Ошибка сети', 'error');
        }
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new GiveGenerator();
});