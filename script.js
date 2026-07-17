const API_URL = "https://ig49t3l6zi.execute-api.ap-south-1.amazonaws.com/upload";

const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const uploadBtn = document.getElementById("uploadBtn");

const loading = document.getElementById("loading");
const results = document.getElementById("results");

const animalCards = document.getElementById("animalCards");

const animalCount = document.getElementById("animalCount");
const imageName = document.getElementById("imageName");

let selectedImage = "";

// =========================
// Image Preview
// =========================

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onload = function (e) {

        selectedImage = e.target.result;

        preview.src = selectedImage;

    }

    reader.readAsDataURL(file);

});

// =========================
// Upload Button
// =========================

uploadBtn.addEventListener("click", async function () {

    if (selectedImage == "") {

        alert("Please Select Image");

        return;

    }

    loading.style.display = "block";

    results.style.display = "none";

    animalCards.innerHTML = "";

    try {

        const base64Image = selectedImage.split(",")[1];

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                image: base64Image

            })

        });

        const result = await response.json();

        const data = typeof result.body === "string"
            ? JSON.parse(result.body)
            : result;

        console.log(data);

        loading.style.display = "none";

        showResults(data);

    }

    catch (err) {

        loading.style.display = "none";

        console.log(err);

        alert("Upload Failed");

    }

});

// =========================
// Display Results
// =========================

function showResults(data) {

    results.style.display = "block";

    animalCards.innerHTML = "";

    imageName.innerHTML = data.image;

    animalCount.innerHTML = data.animals.length;

    data.animals.forEach(animal => {

        animalCards.innerHTML += `

        <div class="animal-card fade">

            <h2>

            🦁 ${animal.Animal}

            </h2>

            <p>

            <strong>Count :</strong>

            <span>${animal.Count}</span>

            </p>

            <p>

            <strong>Confidence :</strong>

            <span>${animal.Confidence}%</span>

            </p>

            <div class="badge">

            Detected

            </div>

        </div>

        `;

    });

    results.scrollIntoView({

        behavior: "smooth"

    });

}