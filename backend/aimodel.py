from pathlib import Path
from typing import Any

import joblib


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "phishing_model.joblib"

_model = None


def load_model() -> Any:
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "The trained model was not found. "
                "Run 'python train_model.py' first."
            )

        _model = joblib.load(MODEL_PATH)

    return _model


def predict_phishing(message: str) -> dict:
    if not isinstance(message, str):
        raise TypeError("Message must be text.")

    cleaned_message = message.strip()

    if not cleaned_message:
        raise ValueError("Message cannot be empty.")

    model = load_model()

    predicted_label = str(
        model.predict([cleaned_message])[0]
    )

    probabilities = model.predict_proba(
        [cleaned_message]
    )[0]

    probability_by_label = {
        str(label): float(probability)
        for label, probability in zip(
            model.classes_,
            probabilities,
        )
    }

    phishing_probability = probability_by_label.get(
        "phishing",
        0.0,
    )

    legitimate_probability = probability_by_label.get(
        "legitimate",
        0.0,
    )

    return {
        "label": predicted_label,
        "is_phishing": predicted_label == "phishing",
        "phishing_probability": round(
            phishing_probability,
            4,
        ),
        "legitimate_probability": round(
            legitimate_probability,
            4,
        ),
        "result": (
            "Warning: This message may be phishing."
            if predicted_label == "phishing"
            else "This message appears legitimate."
        ),
    }