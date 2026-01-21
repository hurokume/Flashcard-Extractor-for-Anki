from openai import OpenAI


class ChatGPT:

    def __init__(self, api_key: str, model: str = "gpt-5-mini", temperature: float = 0.0) -> None:

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.flashcard = {"book": "", "part": "", "is_double": False, "prompt": ""}

    def set_flashcard_info(self, book: str, part: str, is_double: bool, prompt: str) -> None:

        self.flashcard["book"] = book
        self.flashcard["part"] = part
        self.flashcard["is_double"] = is_double
        self.flashcard["prompt"] = prompt

    def extract_flashcards(self, imgs=list[str]) -> str:

        if self.flashcard["book"] == "" or self.flashcard["part"] == "":
            raise ValueError(
                "Flashcard information not set. Please set book, part, is_double, "
                "and prompt before generating flashcards."
            )

        return "test response"
