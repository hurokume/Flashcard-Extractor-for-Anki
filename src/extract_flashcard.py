import json
import os
import time
from tkinter import filedialog

import pandas as pd
import slackweb

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

    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if slack_webhook_url is None:
        print(
            "[WARNING]\tSLACK_WEBHOOK_URL environment variable not set. "
            "Slack notifications disabled."
        )
        slack_notifier = None
    else:
        print("[INFO]\tSLACK_WEBHOOK_URL found. Slack notifications enabled.")
        slack_notifier = slackweb.Slack(url=slack_webhook_url)

    chat_gpt = ChatGPT(api_key=api_key)

    book = "Sample Book"
    part = "Chapter 1"
    prompt = """\
与えられた単語帳のスキャンデータから，\
以下のフォーマットで単語帳情報を抽出してJSON形式で出力してください．\
なお単語帳の1ページには複数の単語が含まれています．
なお，一番最初の階層は "flashcards" としてください．
フォーマット（１単語あたり）:
[
  {
    "no": "必須．単語番号．画像左の左上に記載されている",
    "word": "必須．画像左に含まれる英単語",
    "word_type": "必須．品詞略．画像左の日本語訳の左側に記載されている",
    "meaning": "必須．画像左に含まれる日本語訳．赤字で記載されている",
    "pronunciation": "画像左に含まれる発音記号．画像左の英単語の右側に記載されている",
    "onepoint": "画像左に含まれるワンポイントアドバイス．存在しない場合は空白文字列．！アイコンの右側に記載されている",
    "totteoki": "画像左に含まれるとっておきポイント．存在しない場合は空白文字列．猫アイコンの右側に記載されている"
    "syntax": "画像左に含まれる構文情報．存在しない場合は空白文字列．「構」のアイコンの右側に記載されている",
    "collocation": "画像左に含まれるコロケーション．存在しない場合は空白文字列．「コ」のアイコンの右側に記載されている"
    "idiom": "画像左に含まれるイディオム情報．存在しない場合は空白文字列．「イ」のアイコンの右側に記載されている"
    "derivative": "画像左に含まれる派生語情報．存在しない場合は空白文字列．「派」のアイコンの右側に記載されている"
    "similar_word": "画像左に含まれる類義語情報．存在しない場合は空白文字列．「類」のアイコンの右側に記載されている"
    "antinym": "画像左に含まれる反意語情報．存在しない場合は空白文字列．「反」のアイコンの右側に記載されている"
    "related_word": "画像左に含まれる関連語情報．存在しない場合は空白文字列．「関」のアイコンの右側に記載されている"
    "example_sentence": "必須．画像右に含まれる例文情報．赤字箇所は英単語に対応しており，強調するために*で囲う．"
    "example_sentence_meaning": "必須．画像右に含まれる例文の和訳情報．下線部が例文に対応しており，強調するために*で囲う．"
  },
    ...
]
"""
    column = [
        "no",
        "word",
        "word_type",
        "meaning",
        "pronunciation",
        "onepoint",
        "totteoki",
        "syntax",
        "collocation",
        "idiom",
        "derivative",
        "similar_word",
        "antinym",
        "related_word",
        "example_sentence",
        "example_sentence_meaning",
    ]

    print("[INFO]\tSetting flashcard information...")
    chat_gpt.set_flashcard_info(book=book, part=part, prompt=prompt)

    time_start = time.time()

    extracted_data = pd.DataFrame(columns=column)
    output_csv = "extracted_flashcards.csv"
    output_dir = os.path.dirname(images_path[0])

    for i in range(0, num_images):

        img_path = images_path[i]
        img_filename = os.path.basename(img_path)

        print(f"[INFO]\tProcessing images: {i + 1}/{num_images} - {img_filename}")

        with open(img_path, "rb") as img1_file:
            img_data = img1_file.read()

        response = chat_gpt.extract_flashcards(img=img_data)

        current_time = time.time()
        elapsed_time = current_time - time_start
        estimated_total_time = (elapsed_time / (i + 1)) * num_images
        estimated_remaining_time = estimated_total_time - elapsed_time

        print(
            f"[INFO]\tElapsed time: {elapsed_time:.0f} seconds (Estimated remaining time: "
            f"{(estimated_remaining_time / 60):.2f} minutes)"
        )

        data = json.loads(response)  # response は JSON文字列
        df_response = pd.json_normalize(data["flashcards"])
        extracted_data = pd.concat([extracted_data, df_response], ignore_index=True)

        extracted_data.to_csv(os.path.join(output_dir, output_csv), index=False, encoding="utf-8")

    total_elapsed_time = time.time() - time_start
    total_elapsed_minutes = total_elapsed_time / 60
    print(f"[INFO]\tTotal elapsed time: {total_elapsed_minutes:.2f} minutes")

    if slack_notifier is not None:
        slack_notifier.notify(
            text=(
                f"Flashcard extraction completed in "
                f"{total_elapsed_minutes:.2f} minutes for {num_images} images."
            )
        )
