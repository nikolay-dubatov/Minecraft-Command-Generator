function showFlashMessage(message, category) {
    const flashContainer = document.createElement('div');
    flashContainer.className = `flash ${category}`;
    flashContainer.innerHTML = `<strong>${category.charAt(0).toUpperCase() + category.slice(1)}:</strong> ${message}`;
    document.querySelector('.flash-messages').appendChild(flashContainer);
    console.log(flashContainer);
    setInterval(() => {
        document.querySelector('.flash-messages').removeChild(flashContainer);
    }, 5000);
}

function $(doc, id) {
    return doc.getElementById(id);
}