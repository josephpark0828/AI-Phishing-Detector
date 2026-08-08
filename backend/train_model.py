from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "messages.csv"
MODEL_DIRECTORY = BASE_DIR / "models"
MODEL_PATH = MODEL_DIRECTORY / "phishing_model.joblib"


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "messages.csv was not found. "
            "Run 'python prepare_data.py' first."
        )

    data = pd.read_csv(DATA_PATH)

    required_columns = {"message", "label"}

    if not required_columns.issubset(data.columns):
        raise ValueError(
            "messages.csv must contain message and label columns."
        )

    data = data.dropna(
        subset=["message", "label"]
    )

    data["message"] = data["message"].astype(str)
    data["label"] = data["label"].astype(str)

    data = data[
        data["label"].isin(
            ["phishing", "legitimate"]
        )
    ]

    return data


def create_model() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.98,
                    max_features=150_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    solver="liblinear",
                    random_state=42,
                ),
            ),
        ]
    )


def train_model():
    data = load_data()

    print(f"Total messages: {len(data):,}")
    print("\nClass counts:")
    print(data["label"].value_counts())

    x_train, x_test, y_train, y_test = train_test_split(
        data["message"],
        data["label"],
        test_size=0.20,
        random_state=42,
        stratify=data["label"],
    )

    print(f"\nTraining messages: {len(x_train):,}")
    print(f"Testing messages: {len(x_test):,}")

    model = create_model()

    print("\nTraining model...")
    model.fit(x_train, y_train)

    print("Testing model...")
    predictions = model.predict(x_test)

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            digits=4,
            zero_division=0,
        )
    )

    print("Confusion matrix:")
    print(
        confusion_matrix(
            y_test,
            predictions,
            labels=["legitimate", "phishing"],
        )
    )

    MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()