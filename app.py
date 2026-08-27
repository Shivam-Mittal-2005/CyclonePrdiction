from flask import Flask, render_template, request, jsonify
import os
import uuid
import pickle
import numpy as np
from PIL import Image

app = Flask(__name__)

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

UPLOAD_FOLDER = os.path.join("static", "uploads")
MODEL_PATH = "cyclone_model.pkl"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


# ---------------------------------------------------
# Load Model
# ---------------------------------------------------

print("Loading cyclone prediction model...")

try:
    with open(MODEL_PATH, "rb") as file:
        model = pickle.load(file)

    print("Model loaded successfully.")

except Exception as e:
    print("ERROR while loading model:")
    print(e)
    model = None


# ---------------------------------------------------
# Allowed image extensions
# ---------------------------------------------------

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ---------------------------------------------------
# Image preprocessing
# ---------------------------------------------------

def preprocess_image(image_path):

    image = Image.open(image_path).convert("RGB")

    # Your model expects 224 x 224 x 3
    image = image.resize((224, 224))

    image_array = np.array(image).astype("float32")

    # MobileNetV2 preprocessing
    # Converts pixels from [0,255] to [-1,1]
    image_array = image_array / 127.5 - 1.0

    # Add batch dimension
    image_array = np.expand_dims(image_array, axis=0)

    return image_array


# ---------------------------------------------------
# Prediction
# ---------------------------------------------------

def predict_cyclone(image_path):

    if model is None:
        raise Exception("Model could not be loaded.")

    processed_image = preprocess_image(image_path)

    prediction = model.predict(processed_image, verbose=0)

    print("Raw prediction:", prediction)

    return prediction


# ---------------------------------------------------
# Convert prediction to result
# ---------------------------------------------------

def interpret_prediction(prediction):

    prediction = np.array(prediction)

    # Remove unnecessary dimensions
    prediction = np.squeeze(prediction)

    # -----------------------------------------------
    # CASE 1: Binary classification
    # Example output: [0.82]
    # -----------------------------------------------

    if prediction.ndim == 0:

        probability = float(prediction)

        if probability >= 0.5:
            label = "Cyclone Detected"
            confidence = probability * 100
        else:
            label = "No Cyclone Detected"
            confidence = (1 - probability) * 100

        return label, confidence


    # -----------------------------------------------
    # CASE 2: Binary classification with 2 neurons
    # Example: [0.15, 0.85]
    # -----------------------------------------------

    if len(prediction) == 2:

        class_index = int(np.argmax(prediction))

        confidence = float(prediction[class_index]) * 100

        # CHANGE THESE IF YOUR CLASS ORDER IS DIFFERENT
        class_names = [
            "No Cyclone",
            "Cyclone Detected"
        ]

        label = class_names[class_index]

        return label, confidence


    # -----------------------------------------------
    # CASE 3: Multi-class classification
    # -----------------------------------------------

    class_index = int(np.argmax(prediction))

    confidence = float(prediction[class_index]) * 100

    # IMPORTANT:
    # Replace these with the actual classes
    # used while training your model.
    class_names = [
        "Tropical Depression",
        "Tropical Storm",
        "Cyclone",
        "Severe Cyclone"
    ]

    if class_index < len(class_names):
        label = class_names[class_index]
    else:
        label = f"Class {class_index}"

    return label, confidence


# ---------------------------------------------------
# Home page
# ---------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# ---------------------------------------------------
# Prediction API
# ---------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    try:

        if "image" not in request.files:
            return jsonify({
                "success": False,
                "message": "No image uploaded."
            })

        file = request.files["image"]

        if file.filename == "":
            return jsonify({
                "success": False,
                "message": "Please select an image."
            })

        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "message": "Invalid image format."
            })

        # Generate unique filename
        extension = file.filename.rsplit(".", 1)[1].lower()

        filename = f"{uuid.uuid4().hex}.{extension}"

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        # Prediction
        prediction = predict_cyclone(filepath)

        label, confidence = interpret_prediction(prediction)

        return jsonify({

            "success": True,

            "prediction": label,

            "confidence": round(confidence, 2),

            "image_url": "/" + filepath.replace("\\", "/")

        })

    except Exception as e:

        print("Prediction Error:", e)

        return jsonify({

            "success": False,

            "message": str(e)

        })


# ---------------------------------------------------
# Run Flask
# ---------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )