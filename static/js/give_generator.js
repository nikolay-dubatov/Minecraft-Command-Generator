async function generateGiveCommand() {
    const formData = {
        player: document.getElementById('player').value,
        item: document.getElementById('item').value,
        count: document.getElementById('count').value
    };
    const response = await fetch('/generate/give', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(formData)
    });
    if (response.status === 200) {
        const data = await response.json();
        document.getElementById('result').innerHTML = 
            `<div class="command-box"><strong>Сгенерированная команда: </strong><br><code>${data.command}</code></div>`;
        }
}
document.addEventListener('DOMContentLoaded', () => {
    console.log('Give generator script loaded');
});