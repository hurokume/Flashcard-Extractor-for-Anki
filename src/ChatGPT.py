import base64
import json

from openai import OpenAI


class ChatGPT:

    def __init__(self, api_key: str, model: str = "gpt-5-mini") -> None:

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.flashcard = {"book": "", "part": "", "prompt": ""}

    def set_flashcard_info(self, book: str, part: str, prompt: str) -> None:

        self.flashcard["book"] = book
        self.flashcard["part"] = part
        self.flashcard["prompt"] = prompt

    @staticmethod
    def load_config_json(config_path: str) -> dict:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        required = ["book", "part", "prompt", "columns"]
        missing = [k for k in required if k not in cfg]
        if missing:
            raise ValueError(f"Config JSON missing keys: {missing}")

        # optional
        cfg.setdefault("output_root_key", "flashcards")
        return cfg

    def extract_flashcards(self, img=str) -> str:

        if self.flashcard["book"] == "" or self.flashcard["part"] == "":
            raise ValueError(
                "Flashcard information not set. Please set book, part, is_double, "
                "and prompt before generating flashcards."
            )

        img_base64 = base64.b64encode(img).decode("utf-8")

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": self.flashcard["prompt"]}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Extract flashcard information from the given image.",
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{img_base64}",
                        },
                    ],
                },
            ],
            text={"format": {"type": "json_object"}},
        )

        ugage = self.estimate_cost_usd(response, model=self.model)
        print(f"[INFO]\tEstimated cost for this request: {ugage:.3f} Yen")

        output_text = getattr(response, "output_text", None)

        return output_text

    def estimate_cost_usd(self, response, model: str) -> float:

        rates = {
            "gpt-5": {"in": 1.25, "cached_in": 0.125, "out": 10.00},  # per 1M tokens
            "gpt-5-mini": {"in": 0.25, "cached_in": 0.025, "out": 2.00},  # per 1M tokens
            "gpt-5-nano": {"in": 0.05, "cached_in": 0.005, "out": 0.40},  # per 1M tokens
        }
        r = rates[model]

        usage = getattr(response, "usage", None)
        if usage is None:
            return float("nan")

        in_tok = getattr(usage, "input_tokens", 0) or 0
        out_tok = getattr(usage, "output_tokens", 0) or 0
        cached_in_tok = getattr(usage, "cached_input_tokens", 0) or 0

        usd = (
            (in_tok / 1_000_000) * r["in"]
            + (cached_in_tok / 1_000_000) * r["cached_in"]
            + (out_tok / 1_000_000) * r["out"]
        )

        return usd * 158.16  # JPY conversion
        return usd * 158.16  # JPY conversion
