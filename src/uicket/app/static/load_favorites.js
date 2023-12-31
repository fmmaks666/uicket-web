document.addEventListener('DOMContentLoaded', async function () {
    const cardContainer = document.getElementById('cardContainer');
    
    const favoritesCookie = Cookies.get('Favorites');
    const favoritesArray = JSON.parse(favoritesCookie || '[]');
    
    const loadingMessage = document.createElement('div');
    loadingMessage.textContent = 'Loading…';
    // loadingMessage.style.display = 'flex';
    loadingMessage.style.alignItems = 'center';
    loadingMessage.style.justifyContent = 'center';
    loadingMessage.style.height = '100vh';
    
    for (const releaseId of favoritesArray) {
		cardContainer.appendChild(loadingMessage);
        const card = document.createElement('div');
        card.classList.add('card');
        
        const name = await getReleaseName(releaseId);
        const nameLabel = document.createElement('div');
        nameLabel.textContent = name;
        card.appendChild(nameLabel);
        
        const button = document.createElement('button');
        button.textContent = 'Watch!';
        button.addEventListener('click', function () {
            window.location.href = `/api/${releaseId}`;
        });
        card.appendChild(button);
        
        cardContainer.appendChild(card);
        const cards = document.querySelectorAll('.card');
		cards.forEach(card => {
			const button = card.querySelector('button');
			button.style.width = nameLabel.offsetWidth + 'px';
		});
		cardContainer.removeChild(loadingMessage);
    }
    loadingMessage.textContent = '';
    cardContainer.appendChild(loadingMessage);
});

async function getReleaseName(releaseId) {
    try {
        const response = await fetch(`/api/${releaseId}`);
        const data = await response.json();
        return data.name;
    } catch (error) {
        console.error('Error fetching release data:', error);
        return '';
    }
}
