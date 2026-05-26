class SummonGenerator {
    constructor() {
        this.currentVersion = null;
        this.entities = [];
        this.latest = null;
        this.bindEvents();
        this.init()
    }
    async init() {
        this.latest = await getLatest();
        await this.loadEntities(this.latest);
    }
    async loadEntities(version) {
        try {
            this.entities = await getData('entities', version)
            this.updateEntitySelect();
        } catch (error) {
            console.error('Failed to load entities', error);
        }
    }
    updateEntitySelect() {
        const entitySelect = $('#entity');
        if (!entitySelect) return;

        entitySelect.innerHTML = '';

        this.entities.forEach(entityId => {
            const option = document.createElement('option');
            const entityName = entityId.replace('minecraft:', '');
            option.value = entityId;
            option.textContent = entityName;
            entitySelect.appendChild(option);
        });
    }
    bindEvents() {
        $('#version').addEventListener('change', async (e) => {
            this.currentVersion = e.target.value;
            await this.loadEntities(this.currentVersion);
        });
        $('#summon-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.generateSummonCommand();
        })
    }
    async generateSummonCommand() {
        const formData = new FormData($('#summon-form'))
        const data = Object.fromEntries(formData);

        try {
            const response = await fetch('/generate/summon', {
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
            console.error(error);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SummonGenerator();
});