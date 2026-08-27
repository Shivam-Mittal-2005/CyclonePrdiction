const imageInput = document.getElementById("imageInput");

const browseBtn = document.getElementById("browseBtn");

const uploadArea = document.getElementById("uploadArea");

const analyzeBtn = document.getElementById("analyzeBtn");

const previewContainer =
    document.getElementById("previewContainer");

const previewImage =
    document.getElementById("previewImage");

const uploadContent =
    document.getElementById("uploadContent");

const removeImage =
    document.getElementById("removeImage");

const initialResult =
    document.getElementById("initialResult");

const loading =
    document.getElementById("loading");

const result =
    document.getElementById("result");

const error =
    document.getElementById("error");

const errorMessage =
    document.getElementById("errorMessage");

const prediction =
    document.getElementById("prediction");

const confidence =
    document.getElementById("confidence");

const confidenceBar =
    document.getElementById("confidenceBar");

const resultImage =
    document.getElementById("resultImage");


let selectedFile = null;


/* -----------------------------------
   Browse button
----------------------------------- */

browseBtn.addEventListener("click", function (event) {

    event.stopPropagation();

    imageInput.click();

});


/* -----------------------------------
   Upload area click
----------------------------------- */

uploadArea.addEventListener("click", function () {

    if (!selectedFile) {
        imageInput.click();
    }

});


/* -----------------------------------
   File selected
----------------------------------- */

imageInput.addEventListener("change", function () {

    if (this.files.length > 0) {

        handleFile(this.files[0]);

    }

});


/* -----------------------------------
   Drag and drop
----------------------------------- */

uploadArea.addEventListener("dragover", function (event) {

    event.preventDefault();

    uploadArea.style.borderColor = "#42b9f2";

});


uploadArea.addEventListener("dragleave", function () {

    uploadArea.style.borderColor = "";

});


uploadArea.addEventListener("drop", function (event) {

    event.preventDefault();

    uploadArea.style.borderColor = "";

    const files = event.dataTransfer.files;

    if (files.length > 0) {

        handleFile(files[0]);

    }

});


/* -----------------------------------
   Handle file
----------------------------------- */

function handleFile(file) {

    const validTypes = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp"
    ];


    if (!validTypes.includes(file.type)) {

        alert(
            "Please upload a JPG, JPEG, PNG or WEBP image."
        );

        return;

    }


    if (file.size > 10 * 1024 * 1024) {

        alert("Image size must be less than 10 MB.");

        return;

    }


    selectedFile = file;


    const reader = new FileReader();


    reader.onload = function (event) {

        previewImage.src = event.target.result;

        uploadContent.classList.add("hidden");

        previewContainer.classList.remove("hidden");

        analyzeBtn.disabled = false;

    };


    reader.readAsDataURL(file);

}


/* -----------------------------------
   Remove image
----------------------------------- */

removeImage.addEventListener("click", function (event) {

    event.stopPropagation();

    selectedFile = null;

    imageInput.value = "";

    previewImage.src = "";

    previewContainer.classList.add("hidden");

    uploadContent.classList.remove("hidden");

    analyzeBtn.disabled = true;

});


/* -----------------------------------
   Analyze
----------------------------------- */

analyzeBtn.addEventListener("click", async function () {

    if (!selectedFile) {

        return;

    }


    const formData = new FormData();

    formData.append("image", selectedFile);


    // Show loading

    initialResult.classList.add("hidden");

    result.classList.add("hidden");

    error.classList.add("hidden");

    loading.classList.remove("hidden");

    analyzeBtn.disabled = true;


    try {

        const response = await fetch(
            "/predict",
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        loading.classList.add("hidden");


        if (data.success) {

            showResult(data);

        } else {

            showError(
                data.message ||
                "Prediction failed."
            );

        }

    }

    catch (err) {

        loading.classList.add("hidden");

        showError(
            "Unable to connect to the prediction server."
        );

        console.error(err);

    }


    analyzeBtn.disabled = false;

});


/* -----------------------------------
   Show result
----------------------------------- */

function showResult(data) {

    result.classList.remove("hidden");


    prediction.textContent =
        data.prediction;


    confidence.textContent =
        data.confidence + "%";


    confidenceBar.style.width =
        data.confidence + "%";


    resultImage.src =
        data.image_url;

}


/* -----------------------------------
   Show error
----------------------------------- */

function showError(message) {

    error.classList.remove("hidden");

    errorMessage.textContent = message;

}