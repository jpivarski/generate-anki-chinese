import os
import base64
import json

import requests

GENERATE_CHINESE_FLASHCARDS = os.environ["GENERATE_CHINESE_FLASHCARDS"]


class Word:
    group_index = {}

    def __init__(self, group, hanzi, definition):
        self.group = group
        self.hanzi = hanzi
        self.definition = definition
        self.index = self.group_index[group] = self.group_index.get(group, -1) + 1

    def hint_filename(self):
        return f"hints/{self.group}-{self.index:02d}-{self.hanzi}.json"

    def image_filename(self):
        return f"images/{self.group}-{self.index:02d}-{self.hanzi}.png"


with open("all-words.tsv") as file:
    all_words = [Word(*line.rstrip().split("\t")) for line in file]

hsk1 = set(word.hanzi for word in all_words if word.group.startswith("HSK1_"))

for word in all_words:
    if not word.group.startswith("HSK1_"):
        continue

    print(word.group, word.index, word.hanzi, word.definition)
    if os.path.exists(word.hint_filename()):
        with open(word.hint_filename()) as file:
            response = json.load(file)

    else:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GENERATE_CHINESE_FLASHCARDS}",
                },
                json={
                    "model": "gpt-4.1",
                    "messages": [
                        {
                            "role": "developer",
                            "content": 'You are an author of flashcards for learning Chinese words. Given a Chinese word and an English definition (separated by ":"), you respond with the following in JSON format: (1) a numeric score from 0 to 100 indicating the quality of the given definition, with higher scores for clarity and learning potential, not for comprehensiveness, (2) a clear, easy-to-learn English definition, which may or may not be the same as the given definition, (3) a very short Chinese sentence consisting exclusively of words in HSK1*, using the word that can be visualized as an image for the front of the flashcard, (4) a detailed prompt for `gpt-image-1` to generate that image in a soft apocalypse animation style, and (5) an English translation of that sentence.\n\n*Words in HSK1: '
                            + ", ".join(hsk1),
                        },
                        {"role": "user", "content": f"{word.hanzi}: {word.definition}"},
                    ],
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "response",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "given_definition_quality": {"type": "integer"},
                                    "better_definition": {"type": "string"},
                                    "sentence": {"type": "string"},
                                    "image_prompt": {"type": "string"},
                                    "sentence_translation": {"type": "string"},
                                },
                                "required": [
                                    "given_definition_quality",
                                    "better_definition",
                                    "sentence",
                                    "image_prompt",
                                    "sentence_translation",
                                ],
                                "additionalProperties": False,
                            },
                        },
                    },
                },
            ).json()

            print("    prompts: ", len(response.get("choices", [])))
            if len(response.get("choices", [])):
                content = json.loads(response["choices"][0]["message"]["content"])
                if word.hanzi not in content["sentence"]:
                    raise RuntimeError(f"{word.hanzi} not in {content['sentence']} ({content['sentence_translation']})")

            with open(word.hint_filename(), "w") as file:
                json.dump(response, file)

        except Exception as err:
            print(f"{type(err).__name__}: {err}")
            continue

    if len(response.get("choices", [])) != 0:
        content = json.loads(response["choices"][0]["message"]["content"])
        print("    sentence: ", content["sentence_translation"])

    if len(response.get("choices", [])) != 0 and not os.path.exists(
        word.image_filename()
    ):
        try:
            image_response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GENERATE_CHINESE_FLASHCARDS}",
                },
                json={
                    "model": "gpt-image-1",
                    "prompt": content["image_prompt"]
                    + "\n\nUse a soft apocalypse animation style, somewhere between science fiction and fantasy, with an emphasis on serenity and overgrown foliage. Don't put any text in the image.",
                    "output_format": "png",
                    "quality": "low",
                    "size": "1024x1024",
                },
            ).json()

            print("    images: ", len(image_response.get("data", [])))
            if len(image_response.get("data", [])) != 0:
                with open(word.image_filename(), "wb") as file:
                    file.write(base64.b64decode(image_response["data"][0]["b64_json"]))

        except Exception as err:
            print(f"{type(err).__name__}: {err}")
            continue

        if "usage" in response and "usage" in image_response:
            print(
                "    cost: $"
                + str(
                    2 * response["usage"]["prompt_tokens"] / 1e6
                    + 8 * response["usage"]["completion_tokens"] / 1e6
                    + 10 * image_response["usage"]["input_tokens"] / 1e6
                    + 40 * image_response["usage"]["output_tokens"] / 1e6
                )
            )
