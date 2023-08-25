// I'M IN BIG PROBLEMS: SWITCHING TRANSLATION AND SEASON!

function fetchReleaseData(releaseId) {
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

function populateTranslations(translations, releaseId) {
  const translationsDiv = document.getElementById("translations");
  translationsDiv.innerHTML = '';
  let firstSelected = false;

  for (const [translation, translationId] of Object.entries(translations)) {
	console.warn(translation, translationId)
	console.warn(Object.entries(translations))
    const { radioButton, label } = createRadioInput("translation", translationId, translation);
    translationsDiv.appendChild(radioButton);
    translationsDiv.appendChild(label);

    if (!firstSelected) {
      radioButton.checked = true;
      firstSelected = true;
    }
  }
	console.log('Momiji..?')
    const translationButtons = document.querySelectorAll('input[name="translation"]')
    console.log(translationButtons)
    translationButtons.forEach(button => {
		const selectedLabel = button.nextElementSibling.textContent;
		console.log(button)
		button.addEventListener('change', event => {
			const translationId = document.querySelector('input[name="translation"]:checked').value
			fetch(`/api/episodes/${releaseId}?translation=${translationId}`).then(response => response.json())
				.then(data => {
					if (data.type === 'streams') {
						console.log('Momiji-sama is Happy!~');
						updateQualities(data.streams);
					} else {
						fetchSeasons(selectedLabel, data, releaseId);
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
		console.log("Momiji-sama desu");
		let { radioButton, label } = createRadioInput("season", seasonId, seasonName);
		console.log(seasonName);
		radioButton.addEventListener('change', () => updateEpisodes(seasons['episodes'], releaseId, seasons['translator_id']))
		seasonsDiv.appendChild(radioButton);
		seasonsDiv.appendChild(label);
		if (!firstSelected) {
			radioButton.checked = true;
			firstSelected = true; 
	}
  }
}

function updateEpisodes(episodes, releaseId, translation=null) {
	console.log(releaseId, translation)
	const season = document.querySelector('input[name="season"]:checked');
	const episodesDiv = document.getElementById("episodes");
	episodesDiv.innerHTML = '';
	episodeSelect = document.createElement('select')
	for (let [episodeId, episodeName] of Object.entries(episodes[season.value])) {
		console.log(episodeId, episodeName)
		episode = document.createElement('option');
		episode.value = episodeId.toString();
		episode.textContent = episodeName;
		episodeSelect.appendChild(episode);
	}
	console.log('Momiji says: What?');
	console.log(episodeSelect);
	episodesDiv.appendChild(episodeSelect);
	console.log(translation)
	episodeSelect.addEventListener('change', event => {
		withTranslation = `/api/streams/${releaseId}?translation=${translation}&season=${season.value}&episode=${episodeSelect.value}`; // These 2 lines are full of problems
		withoutTranslation = `/api/streams/${releaseId}?season=${season.value}&episode=${episodeSelect.value}`;
		fetch(translation ? withTranslation : withoutTranslation).then(response => response.json())
			.then(data => updateQualities(data.streams))
	})
}

function populateSeasons(releaseId) {
  console.log(releaseId)
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
			const season = document.querySelector('input[name="season"]:checked').value;
			const episode = document.querySelector('#episodes select').value;
			fetch(`/api/streams/${releaseId}?translation=${quality}&season=${season}&episode=${episode}`).then(response => response.json())
				.then(data => updateQualities(data.streams))
		}
})}

function updateQualities(data) {
  const qualitiesDiv = document.getElementById("qualities");
  qualitiesDiv.innerHTML = '' // Clear previous content
  console.log(data);
  let firstSelected = false;
  for (let [quality, link] of Object.entries(data)) {
	console.log("Momiji desu")
    let { radioButton, label } = createRadioInput("quality", link, quality);
    console.log(link)
    qualitiesDiv.appendChild(radioButton);
    qualitiesDiv.appendChild(label);
    if (!firstSelected) {
		radioButton.checked = true;
		firstSelected = true
	}
  }
}

//function setupFavoritesButtons(data) {
  //const addToFavoritesButton = document.getElementById("toggleFavorite");
  //const removeFromFavoritesButton = document.getElementById("removeFromFavorites");

  //addToFavoritesButton.addEventListener("click", () => handleFavoritesAction(data.id, "add"));
  //removeFromFavoritesButton.addEventListener("click", () => handleFavoritesAction(data.id, "remove"));
//}

function handleFavoritesAction(releaseId, action) {
  const method = action === "add" ? "POST" : "DELETE";
  fetch(`/api/favorites/${releaseId}`, { method })
    .then(response => response.json())
    .then(result => {
      const message = result.success ? `Successfully ${action}ed from favorites!` : `Failed to ${action} from favorites.`;
      alert(message);
    });
}

function setupStreamButtons() {
  const watchStreamButton = document.getElementById("watchStream");
  watchStreamButton.addEventListener('click', watchStream)
}

function watchStream() {
  console.error('Momiji?')
  const quality = document.querySelector('input[name="quality"]:checked').value;
  console.log(quality)
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
    document.getElementById("releaseTitle").textContent = data.name;
    populateTranslations(data.translations, data.id);
    populateSeasons(releaseId);
    // setupFavoritesButtons(data);
    setupStreamButtons();
    // The player element can be added here dynamically
    // Example: document.getElementById("player").innerHTML = "<iframe src='your_stream_url'></iframe>";
  });
