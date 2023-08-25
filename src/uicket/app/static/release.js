async function fetchReleaseData(releaseId) {
  return fetch(`/api/${releaseId}`, { method: "GET" }).then(response => response.json());
}

function createRadioInput(name, value, labelText) {
  const radioButton = document.createElement("input");
  radioButton.type = "radio";
  radioButton.name = name;
  radioButton.value = value;

  const label = document.createElement("label");
  label.textContent = labelText;

  return { radioButton, label };
}

async function populateTranslations(translations, releaseId) {
  const translationsDiv = document.getElementById("translations");
  translationsDiv.innerHTML = '';
  let firstSelected = false;

  for (const [translation, translationId] of Object.entries(translations)) {
    const { radioButton, label } = createRadioInput("translation", translationId, translation);
    translationsDiv.appendChild(radioButton);
    translationsDiv.appendChild(label);

    if (!firstSelected) {
      radioButton.checked = true;
      firstSelected = true;
    }
  }
    const translationButtons = document.querySelectorAll('input[name="translation"]')
    translationButtons.forEach(button => {
		const selectedLabel = button.nextElementSibling.textContent;
		button.addEventListener('change', event => {
			const translationId = document.querySelector('input[name="translation"]:checked').value
			fetch(`/api/episodes/${releaseId}?translation=${translationId}`).then(response => response.json())
				.then(data => {
					if (data.type === 'streams') {
						updateQualities(data.streams);
					} else {
						console.log('Momiji-sama calls fetchSeasons from callback in populateTranslations')
						//console.log(selectedLabel, data, releaseId)
						//fetchSeasons(selectedLabel, data, releaseId);
						//const season = document.getElementById("seasons").value;
						// Porting stuff:
						const selectedLabel = event.target.nextElementSibling.textContent;
						const translation = event.target.value;
						fetchSeasons(selectedLabel, data, releaseId);
						updateEpisodes(data['seasons'][selectedLabel]['episodes'], releaseId, translation);
						const season = document.querySelector('input[name="season"]:checked').value.toString();
						const episode = document.querySelector('#episodes select').value;
						console.log('se', season, episode)
						fetch(`/api/streams/${releaseId}?translation=${translation}&season=${season}&episode=${episode}`).then(response => response.json())
							.then(data => updateQualities(data.streams))
					}
				});
			});
		});
}

function fetchSeasons(translationName, series, releaseId) {
	const seasons = series['seasons'][translationName];
	const seasonsDiv = document.getElementById("seasons");
	const episodesDiv = document.getElementById("episodes");
	seasonsDiv.innerHTML = '';
	let firstSelected = false;
	for (let [seasonId, seasonName] of Object.entries(seasons['seasons'])) {
		let { radioButton, label } = createRadioInput("season", seasonId, seasonName);
		radioButton.addEventListener('change', () => {
			updateEpisodes(seasons['episodes'], releaseId, seasons['translator_id']);
			const currentSeason = event.target.value;
			const currentEpisode = document.querySelector('#episodes select').value.toString();
			console.log('es', currentEpisode, currentSeason)
			withTranslation = `/api/streams/${releaseId}?translation=${seasons['translator_id']}&season=${currentSeason}&episode=${currentEpisode}`; // These 2 lines are full of problems
			fetch(withTranslation).then(response => response.json())
				.then(data => updateQualities(data.streams));
		});
		seasonsDiv.appendChild(radioButton);
		seasonsDiv.appendChild(label);
		if (!firstSelected) {
			radioButton.checked = true;
			firstSelected = true; 
	}
  }
}

function updateEpisodes(episodes, releaseId, translation) {
	const season = document.querySelector('input[name="season"]:checked');
	const episodesDiv = document.getElementById("episodes");
	episodesDiv.innerHTML = '';
	episodeSelect = document.createElement('select')
	for (let [episodeId, episodeName] of Object.entries(episodes[season.value])) {
		episode = document.createElement('option');
		episode.value = episodeId.toString();
		episode.textContent = episodeName;
		episodeSelect.appendChild(episode);
	}
	episodesDiv.appendChild(episodeSelect);
	episodeSelect.addEventListener('change', event => {
		const currentSeason = document.querySelector('input[name="season"]:checked').value;
		const currentEpisode = event.target.value;
		console.log('se', currentSeason, currentEpisode);
		withTranslation = `/api/streams/${releaseId}?translation=${translation}&season=${currentSeason}&episode=${currentEpisode}`; // These 2 lines are full of problems
		withoutTranslation = `/api/streams/${releaseId}?season=${currentSeason}&episode=${currentEpisode}`;
		fetch(translation ? withTranslation : withoutTranslation).then(response => response.json())
			.then(data => updateQualities(data.streams));
	});
}

function handleSeasonChange() {}

function populateSeasons(releaseId) {
  const seasonsDiv = document.getElementById("seasons");
  const episodesDiv = document.getElementById("episodes");
  const quality = document.querySelector('input[name="translation"]:checked').value;
  fetch(`/api/episodes/${releaseId}?translation=${quality}`).then(response => response.json())
	.then(data => {
		if (data.type === "streams") {
			seasonsDiv.remove();
			episodesDiv.remove();
			updateQualities(data.streams);
		} else {
			const translationButtons = document.querySelector('input[name="translation"]:checked')
			const selectedLabel = translationButtons.nextElementSibling.textContent;
			fetchSeasons(selectedLabel, data, releaseId);
			updateEpisodes(data['seasons'][selectedLabel]['episodes'], releaseId, quality);
			const season = document.querySelector('input[name="season"]:checked').value.toString();
			const episode = document.querySelector('#episodes select').value;
			console.log('se', season, episode)
			fetch(`/api/streams/${releaseId}?translation=${quality}&season=${season}&episode=${episode}`).then(response => response.json())
				.then(data => updateQualities(data.streams))
		}
})}

async function updateQualities(data) {
  const qualitiesDiv = document.getElementById("qualities");
  qualitiesDiv.innerHTML = '' // Clear previous content
  let firstSelected = false;
  for (let [quality, link] of Object.entries(data)) {
    let { radioButton, label } = createRadioInput("quality", link, quality);
    qualitiesDiv.appendChild(radioButton);
    qualitiesDiv.appendChild(label);
    if (!firstSelected) {
		radioButton.checked = true;
		firstSelected = true
	}
  }
}

async function setupFavorites(releaseId) {
  const toggleFavoriteButton = document.getElementById("toggleFavorite");
  const favoritesList = Cookies.get('Favorites');
  const favorites = JSON.parse(favoritesList);
  toggleFavoriteButton.textContent = !favorites.includes(releaseId) ? 'Add Favorite' : 'Remove Favorite'
  toggleFavoriteButton.addEventListener('click', () => toggleFavorite(releaseId,toggleFavoriteButton))
}

function toggleFavorite(releaseId, button) {
  const favoritesList = Cookies.get('Favorites');
  const favorites = JSON.parse(favoritesList);
  const method = !favorites.includes(releaseId) ? "POST" : "DELETE";
  fetch(`/api/favorites/${releaseId}`, {'method': method})
    .then((response) => {console.warn(response.json());button.textContent = favorites.includes(releaseId) ? 'Add Favorite' : 'Remove Favorite'});
}

function setupStreamButtons() {
  const watchStreamButton = document.getElementById("watchStream");
  watchStreamButton.addEventListener('click', watchStream)
}

function watchStream() {
  const quality = document.querySelector('input[name="quality"]:checked').value;
  const player = document.getElementById('player');
  player.innerHTML = '';
  frame = document.createElement('iframe');
  frame.setAttribute('src', quality);
  frame.setAttribute('allowfullscreen', '');
  const copyLink = document.createElement('button');
  copyLink.textContent = 'Copy Link';
  copyLink.addEventListener('click', () => {navigator.clipboard.writeText(quality).catch(error => console.error(error))});
  player.appendChild(frame);
  player.appendChild(copyLink)
}

const params = new URLSearchParams(window.location.search);
const releaseId = params.get('id');

fetchReleaseData(releaseId)
  .then(data => {
	setupFavorites(data.id);
    document.getElementById("releaseTitle").textContent = data.name;
    populateTranslations(data.translations, data.id);
    populateSeasons(releaseId);
    setupStreamButtons();
    // The player element can be added here dynamically
    // Example: document.getElementById("player").innerHTML = "<iframe src='your_stream_url'></iframe>";
  });
