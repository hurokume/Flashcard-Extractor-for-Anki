from io import BytesIO

from PIL import Image


class ImageProcessing:

    @staticmethod
    def merge_lr_bytes(
        img1_data: bytes,
        img2_data: bytes,
        *,
        bg_color: str = "white",
        quality: int = 95,
    ) -> bytes:

        img1 = Image.open(BytesIO(img1_data)).convert("RGB")
        img2 = Image.open(BytesIO(img2_data)).convert("RGB")

        target_h = max(img1.height, img2.height)

        def resize_to_h(img: Image.Image, h: int) -> Image.Image:
            if img.height == h:
                return img
            new_w = round(img.width * h / img.height)
            return img.resize((new_w, h), Image.Resampling.LANCZOS)

        img1 = resize_to_h(img1, target_h)
        img2 = resize_to_h(img2, target_h)

        merged = Image.new(
            "RGB",
            (img1.width + img2.width, target_h),
            bg_color,
        )
        merged.paste(img1, (0, 0))
        merged.paste(img2, (img1.width, 0))

        out = BytesIO()
        merged.save(out, format="JPEG", quality=quality)
        return out.getvalue()

    @staticmethod
    def sanitize_filename(name: str) -> str:

        return "".join(c for c in name if c.isalnum() or c in ("-", "_"))
