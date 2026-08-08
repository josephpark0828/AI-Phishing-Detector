from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
RAW_DIRECTORY = BASE_DIR / "data" / "raw"
OUTPUT_PATH = BASE_DIR / "data" / "messages.csv"


TEXT_COLUMNS = [
    "email text",
    "text",
    "message",
    "body",
    "email_body",
    "email body",
]

SUBJECT_COLUMNS = [
    "subject",
    "email subject",
]

LABEL_COLUMNS = [
    "email type",
    "label",
    "class",
    "type",
    "category",
]


def find_column(dataframe: pd.DataFrame, possible_names: list[str]):
    """Find a column without caring about capitalization or spaces."""

    normalized_columns = {
        str(column).strip().lower(): column
        for column in dataframe.columns
    }

    for possible_name in possible_names:
        if possible_name in normalized_columns:
            return normalized_columns[possible_name]

    return None


def normalize_label(value):
    """Convert different label formats into phishing or legitimate."""

    label = str(value).strip().lower()

    phishing_values = {
        "1",
        "phishing",
        "phishing email",
        "spam",
        "malicious",
        "fraud",
    }

    legitimate_values = {
        "0",
        "legitimate",
        "legitimate email",
        "safe",
        "safe email",
        "ham",
        "benign",
    }

    if label in phishing_values:
        return "phishing"

    if label in legitimate_values:
        return "legitimate"

    return None


def read_csv_safely(csv_path: Path) -> pd.DataFrame:
    """Read a CSV while handling common encoding problems."""

    try:
        return pd.read_csv(
            csv_path,
            encoding="utf-8",
            on_bad_lines="skip",
            low_memory=False,
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            csv_path,
            encoding="latin-1",
            on_bad_lines="skip",
            low_memory=False,
        )


def prepare_data():
    csv_files = list(RAW_DIRECTORY.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files were found in {RAW_DIRECTORY}"
        )

    prepared_files = []

    for csv_path in csv_files:
        print(f"\nReading {csv_path.name}...")

        data = read_csv_safely(csv_path)

        text_column = find_column(data, TEXT_COLUMNS)
        subject_column = find_column(data, SUBJECT_COLUMNS)
        label_column = find_column(data, LABEL_COLUMNS)

        if text_column is None:
            print(
                f"Skipped {csv_path.name}: "
                f"no recognized email-text column."
            )
            print(f"Columns: {list(data.columns)}")
            continue

        if label_column is None:
            print(
                f"Skipped {csv_path.name}: "
                f"no recognized label column."
            )
            print(f"Columns: {list(data.columns)}")
            continue

        message_text = data[text_column].fillna("").astype(str)

        if subject_column is not None:
            subject_text = data[subject_column].fillna("").astype(str)

            message_text = (
                "Subject: "
                + subject_text
                + "\n\n"
                + message_text
            )

        cleaned = pd.DataFrame(
            {
                "message": message_text,
                "label": data[label_column].apply(normalize_label),
                "source": csv_path.stem,
            }
        )

        prepared_files.append(cleaned)

        print(f"Accepted {len(cleaned):,} rows.")

    if not prepared_files:
        raise ValueError(
            "No usable datasets were found. "
            "Check the printed column names."
        )

    combined = pd.concat(
        prepared_files,
        ignore_index=True,
    )

    combined = combined.dropna(
        subset=["message", "label"]
    )

    combined["message"] = (
        combined["message"]
        .astype(str)
        .str.replace("\x00", "", regex=False)
        .str.strip()
    )

    combined = combined[
        combined["message"].str.len() >= 10
    ]

    combined = combined.drop_duplicates(
        subset=["message"]
    )

    combined = combined.sample(
        frac=1,
        random_state=42,
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nPreparation complete.")
    print(f"Saved dataset to: {OUTPUT_PATH}")
    print(f"Total messages: {len(combined):,}")

    print("\nLabel counts:")
    print(combined["label"].value_counts())

    print("\nSource counts:")
    print(combined["source"].value_counts())


if __name__ == "__main__":
    prepare_data()