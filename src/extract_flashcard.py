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

    initialdir = os.getcwd() + "../prompts"
    config_path = filedialog.askopenfilename(
        title="Select flashcard config JSON",
        initialdir=initialdir,
        filetypes=[("JSON Files", "*.json")],
    )
    config_filename = os.path.basename(config_path)

    if not config_path:
        print("[INFO]\tNo config selected. Exiting...")
        exit(0)

    print(f"[INFO]\tSelected config: {config_filename}")

    cfg = ChatGPT.load_config_json(config_path)
    book = cfg["book"]
    part = cfg["part"]
    prompt = cfg["prompt"]
    columns = cfg["columns"]

    print("[INFO]\tSetting flashcard information...")
    chat_gpt.set_flashcard_info(book=book, part=part, prompt=prompt)

    time_start = time.time()

    extracted_data = pd.DataFrame(columns=columns)
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
