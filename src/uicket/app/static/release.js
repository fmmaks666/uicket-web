const params = new URLSearchParams(window.location.search);
const releaseId = params.get('id')
const data = fetch(`/api/${releaseId}`, { method: "GET" })
  .then(response => response.json())
  .then(data => {
	document.getElementById("releaseTitle").textContent = data.name;
});
const translationsDiv = document.getElementById("translations");
let firstSelected = false;
for (const translation in data.translations) {
  const radioButton = document.createElement("input");
  radioButton.type = "radio";
  radioButton.name = "translation";
  radioButton.value = translation;
  translationsDiv.appendChild(radioButton);
  const label = document.createElement("label");
  label.textContent = translation;
  translationsDiv.appendChild(label);
  if (!firstSelected) {
	  radioButton.checked = true;
	  firstSelected = true
	}
}

if (data.type === "video.tv_series") {
  // fetch()
  const seasonsDiv = document.getElementById("seasons");
  for (const season of data.seasons) {
	const radioButton = document.createElement("input");
	radioButton.type = "radio";
	radioButton.name = "season";
	radioButton.value = season;
	seasonsDiv.appendChild(radioButton);
	const label = document.createElement("label");
	label.textContent = "Season " + season;
	seasonsDiv.appendChild(label);
  }
}


function updateQualities() {
  const selectedQuality = qualityDropdown.value;
  const qualitiesDiv = document.getElementById("qualities");
  qualitiesDiv.innerHTML = ""; // Clear previous content
  for (const quality of data.qualities[selectedQuality]) {
	const radioButton = document.createElement("input");
	radioButton.type = "radio";
	radioButton.name = "quality";
	radioButton.value = quality;
	qualitiesDiv.appendChild(radioButton);
	const label = document.createElement("label");
	label.textContent = quality;
	qualitiesDiv.appendChild(label);
  }
}

const addToFavoritesButton = document.getElementById("addToFavorites");
addToFavoritesButton.addEventListener("click", addToFavorites);

const removeFromFavoritesButton = document.getElementById("removeFromFavorites");
removeFromFavoritesButton.addEventListener("click", removeFromFavorites);

function addToFavorites() {
  fetch(`/api/favorites/${data.id}`, { method: "POST" })
	.then(response => response.json())
	.then(result => {
	  if (result.success) {
		alert("Added to favorites!");
	  } else {
		alert("Failed to add to favorites.");
	  }
	});
}

function removeFromFavorites() {
  fetch(`/api/favorites/${data.id}`, { method: "DELETE" })
	.then(response => response.json())
	.then(result => {
	  if (result.success) {
		alert("Removed from favorites!");
	  } else {
		alert("Failed to remove from favorites.");
	  }
	});
}

const downloadStreamButton = document.getElementById("downloadStream");
downloadStreamButton.addEventListener("click", downloadStream);

function downloadStream() {
  // Implement download functionality
}

const watchStreamButton = document.getElementById("watchStream");
watchStreamButton.addEventListener("click", watchStream);

function watchStream() {
  // Implement watch stream functionality
}

// The player element can be added here dynamically
// Example: document.getElementById("player").innerHTML = "<iframe src='your_stream_url'></iframe>";
console.log(data);

