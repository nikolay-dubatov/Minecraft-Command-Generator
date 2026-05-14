function $(id) {
    return document.getElementById(id);
}

async function generateSummonCommand() {
    const formData = {
        entity: $('entity').value, 
        position: getPosition($('x-field').value, $('y-field').value, $('z-field').value),
        customName: getCustomName()
    };
    console.log(formData)
    const response = await fetch('/generate/summon', {
        method: 'POST', 
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(formData)
    });
    const data = await response.json()
    $('result').innerHTML = 
        `<div class="command-box"><strong>Сгенерированная команда: </strong><br><code>${data.command}</code></div>`;
}

function getPosition(x, y, z) {
    const position = `${x} ${y} ${z}`;
    return position;
}

function getCustomName() {
    try {
        const custom_name = $('custom-name').value; 
        return custom_name;
    } catch {
        return null;
    }
}