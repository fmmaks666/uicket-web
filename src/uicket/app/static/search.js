document.addEventListener('DOMContentLoaded', async function () {
    const searchResults = document.getElementById('searchResults');
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchInput');
    searchButton.addEventListener('click', async function() {
		query = searchInput.value;
		results = await doSearch(query)
		displayResults(results, searchResults)
	});
});
   
async function displayResults(results, container) { 
	while (container.firstChild) {
		container.removeChild(container.firstChild)
	}
    for (const release of results["results"]) {
		const releaseName = release[1]
		const releaseId = release[0]
        const card = document.createElement('div');
        card.classList.add('card');
        
        const nameLabel = document.createElement('div');
        nameLabel.textContent = releaseName;
        card.appendChild(nameLabel);
        
        const button = document.createElement('button');
        button.textContent = 'Watch!';
        button.addEventListener('click', function () {
            window.open(`/release?id=${releaseId}`);
        });
        card.appendChild(button);
        
        container.appendChild(card);
        const cards = document.querySelectorAll('.card');
		cards.forEach(card => {
			const button = card.querySelector('button');
			button.style.width = nameLabel.offsetWidth + 'px';
		});
    }
}
  
async function doSearch(query) {
    try {
		encodedQuery = encodeURIComponent(query)
        const response = await fetch(`/api/search?q=${encodedQuery}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching release data:', error);
        return {'results': []};
    }
}
