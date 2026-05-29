class SummonGenerator {
    constructor() {
        this.currentVersion = null;
        this.entities = [];
        this.latest = null;
        this.autocomplete = null;
        this.bindEvents();
        this.init()
    }
    async init() {
        try {
            this.latest = await getLatest();
            this.currentVersion = this.latest;
            await this.loadEntities(this.latest);
        } catch (error) {
            console.error('Failed to initialize SummonGenerator')
        }
    }
    async loadEntities(version) {
        try {
            this.entities = await getData('entities', version);
            if (this.autocomplete) {
                this.autocomplete.updateDataSource(this.entities);
            } else {
                this.initAutocomplete();
            }
        } catch (error) {
            console.error('Failed to load entities', error);
        }
    }
    
    initAutocomplete() {
        this.autocomplete = new Autocomplete(
            '#entity-search', 
            '#entity-suggestions', 
            this.entities, 
            (selectedEntity) => {
                const hiddenInput = $('#selected-entity');
                if (hiddenInput) {
                    hiddenInput.value = selectedEntity;
                }
            }
        );
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