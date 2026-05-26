class GiveGenerator {
    constructor() {
        this.currentVersion = null;
        this.latest = null;
        this.items = [];
        this.bindEvents();
        this.init()
    }
    async init() {
        this.latest = await getLatest();
        await this.loadItems(this.latest)
    }
    async loadItems(version) {
        try {
            this.items = await getData('items', version);
            this.updateItemSelect();
        } catch (error) {
            console.error("Failed to load items: ", error);
        }
    }
    updateItemSelect() {
        const itemSelect = $('#item');
        itemSelect.innerHtml = '';
        this.items.forEach(itemId => {
            const option = document.createElement('option');
            const itemName = itemId.replace('minecraft:', '');
            option.value = itemId;
            option.textContent = itemName;
            itemSelect.appendChild(option);
        });
    }
    bindEvents() {
        $('#version').addEventListener('change', async (e) => {
            this.currentVersion = e.target.value;
            await this.loadItems(this.currentVersion);
        });
        $('#give-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.generateGiveCommand();
        });
    }
    async generateGiveCommand() {
        const formData = new FormData($('#give-form'))
        const data = Object.fromEntries(formData);

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