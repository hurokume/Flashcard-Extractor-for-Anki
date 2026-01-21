import os
from tkinter import filedialog

from ImageProcessing import ImageProcessing as ip

if __name__ == "__main__":
    images_path = filedialog.askopenfilenames(
        title="Select images to merge (2 pages -> 1 image)",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")],
    )

    num_images = len(images_path)
    if num_images == 0:
        print("[INFO]\tNo images selected. Exiting...")
        raise SystemExit(0)

    print(f"[INFO]\tSelected {num_images} images.")

    input_dir = os.path.dirname(images_path[0])
    out_dir = os.path.join(input_dir, "merged_images")
    os.makedirs(out_dir, exist_ok=True)

    print(f"[INFO]\tOutput directory: {out_dir}")

    merged_index = 0

    for i in range(0, num_images, 2):
        img1_path = images_path[i]
        img2_path = images_path[i + 1] if i + 1 < num_images else None

        if not img2_path:
            print(f"[WARN]\tOdd number of images. Skipping last: " f"{os.path.basename(img1_path)}")
            continue

        img1_name = os.path.splitext(os.path.basename(img1_path))[0]
        img2_name = os.path.splitext(os.path.basename(img2_path))[0]

        print(f"[INFO]\tMerging: {img1_name} + {img2_name}")

        with open(img1_path, "rb") as f:
            img1_data = f.read()
        with open(img2_path, "rb") as f:
            img2_data = f.read()

        merged_img_bytes = ip.merge_lr_bytes(img1_data, img2_data)

        safe_img1 = ip.sanitize_filename(img1_name)
        safe_img2 = ip.sanitize_filename(img2_name)

        out_filename = f"merged_{merged_index:04d}_{safe_img1}__{safe_img2}.jpg"
        out_path = os.path.join(out_dir, out_filename)

        with open(out_path, "wb") as f:
            f.write(merged_img_bytes)

        print(f"[INFO]\tSaved: {out_filename}")

        merged_index += 1

    print("[INFO]\tAll images merged successfully.")
