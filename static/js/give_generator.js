$(document, 'give-form').addEventListener('submit', async (e) => {
    e.preventDefault()
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch('/generate/give', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            $(document, 'result').innerHTML = 
                `<div class="command-box"><strong>Сгенерированная команда: </strong><br><code>${result.command}</code></div>`;
            showFlashMessage(result.message, 'success');
        } else {
            showFlashMessage(result.error, 'error');
        }
    } catch (error) {
        showFlashMessage('Ошибка сети', 'error')
    }
});