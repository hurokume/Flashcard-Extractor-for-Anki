import os
import time
from tkinter import filedialog

from ChatGPT import ChatGPT

if __name__ == "__main__":

    images_path = filedialog.askopenfilenames(
        title="Select images to resize",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")],
    )

    num_images = len(images_path)

    if num_images == 0:
        print("[INFO]\tNo images selected. Exiting...")
        exit(0)

    print(f"[INFO]\tSelected {num_images} images for resizing.")

    api_key = os.getenv("OPENAI_API_KEY")

    if api_key is None:
        print("[ERROR]\tOPENAI_API_KEY environment variable not set. Exiting...")
        exit(0)
    else:
        print("[INFO]\tOPENAI_API_KEY found.")

    chat_gpt = ChatGPT(api_key=api_key)

    book = "Sample Book"
    part = "Chapter 1"
    is_double = True
    prompt = """\
与えられた単語帳のスキャンデータから，\
以下のフォーマットで単語帳情報を抽出してJSON形式で出力してください．\
なお単語帳の1ページには複数の単語が含まれています．
フォーマット（１単語あたり）:
[
  {
    "no": "単語番号．画像1の左上に記載されている",
    "word": "画像1に含まれる英単語",
    "word_type": "品詞略．画像1の日本語訳の左側に記載されている",
    "meaning": "画像1に含まれる日本語訳．赤字で記載されている",
    "pronunciation": "画像1に含まれる発音記号．画像1の英単語の右側に記載されている",
    "onepoint": "画像1に含まれるワンポイントアドバイス．存在しない場合は空白文字列．！アイコンの右側に記載されている",
    "totteoki": "画像1に含まれるとっておきポイント．存在しない場合は空白文字列．猫アイコンの右側に記載されている"
    "syntax": "画像1に含まれる構文情報．存在しない場合は空白文字列．「構」のアイコンの右側に記載されている",
    "collocation": "画像1に含まれるコロケーション．存在しない場合は空白文字列．「コ」のアイコンの右側に記載されている"
    "idiom": "画像1に含まれるイディオム情報．存在しない場合は空白文字列．「イ」のアイコンの右側に記載されている"
    "derivative": "画像1に含まれる派生語情報．存在しない場合は空白文字列．「派」のアイコンの右側に記載されている"
    "similar_word": "画像1に含まれる類義語情報．存在しない場合は空白文字列．「類」のアイコンの右側に記載されている"
    "antinym": "画像1に含まれる反意語情報．存在しない場合は空白文字列．「反」のアイコンの右側に記載されている"
    "related_word": "画像1に含まれる関連語情報．存在しない場合は空白文字列．「関」のアイコンの右側に記載されている"
    "example_sentence": "画像2に含まれる例文情報．赤字箇所は英単語に対応しており，強調するために*で囲う．"
    "example_sentence_meaning": "画像2に含まれる例文の和訳情報．下線部が例文に対応しており，強調するために*で囲う．"
  },
    ...
]
"""
    print("[INFO]\tSetting flashcard information...")
    chat_gpt.set_flashcard_info(book=book, part=part, is_double=is_double, prompt=prompt)

    time_start = time.time()

    for i in range(0, num_images, 2):
        img1_path = images_path[i]
        img2_path = images_path[i + 1] if i + 1 < num_images else None

        img1_filename = os.path.basename(img1_path)
        img2_filename = os.path.basename(img2_path) if img2_path else "N/A"

        print(f"[INFO]\tProcessing images: {img1_filename}, {img2_filename}")

        with open(img1_path, "rb") as img1_file:
            img1_data = img1_file.read()

        img2_data = None
        if img2_path:
            with open(img2_path, "rb") as img2_file:
                img2_data = img2_file.read()
        else:
            continue

        response = chat_gpt.extract_flashcards(
            imgs=[img1_data, img2_data] if img2_data else [img1_data]
        )

        current_time = time.time()
        elapsed_time = current_time - time_start
        estimated_total_time = (elapsed_time / (i + 2)) * num_images
        print(
            f"[INFO]\tElapsed time: {elapsed_time:.0f} seconds (Estimated remaining time: "
            f"{(elapsed_time / 60):.2f} minutes)"
        )
