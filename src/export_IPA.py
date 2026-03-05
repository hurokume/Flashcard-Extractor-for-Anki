import os
from tkinter import filedialog

import pandas as pd

from ChatGPT import ChatGPT

if __name__ == "__main__":

    word_path = filedialog.askopenfilenames(
        title="Select word list files (CSV or Excel)",
        filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx;*.xls")],
    )

    num_files = len(word_path)

    if num_files != 1:
        print("[INFO]\tNo images selected. Exiting...")
        exit(0)

    print(f"[INFO]\tSelected {num_files} images for resizing.")

    api_key = os.getenv("OPENAI_API_KEY")

    if api_key is None:
        print("[ERROR]\tOPENAI_API_KEY environment variable not set. Exiting...")
        exit(0)
    else:
        print("[INFO]\tOPENAI_API_KEY found.")

    chat_gpt = ChatGPT(api_key=api_key)

    df = pd.read_csv(word_path[0]) if word_path[0].endswith(".csv") else pd.read_excel(word_path[0])

    if "word" not in df.columns:
        print("[ERROR]\tNo 'word' column found in the input file. Exiting...")
        exit(0)

    words = df["word"].to_list()
    ipa = []
    i = 0

    for word in words:

        if word is None or str(word).strip() == "":
            ipa.append("")
            continue

        try:
            ipa.append(chat_gpt.ipa(word))

        except Exception as e:
            print(f"[ERROR]\tError processing word '{word}': {e}")
            ipa.append("")

        print(f"[INFO]\tProcessed {i + 1}/{len(words)}: '{word}' -> '{ipa[-1]}'")

        i += 1

    df["IPA"] = ipa
    output_path = os.path.splitext(word_path[0])[0] + "_with_IPA.csv"
    df.to_csv(output_path, index=False)
    print(f"[INFO]\tIPA conversion completed. Output saved to: {output_path}")
