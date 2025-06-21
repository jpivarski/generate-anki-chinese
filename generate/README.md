Generate better definitions, sample sentences, prompts for images and the images themselves with

```bash
export GENERATE_CHINESE_FLASHCARDS=...  # OpenAI api-key

python generate-images.py
```

Make smaller images with

```bash
mkdir images-small

sips -Z 512 images/*.png --out images-small
```

Make the Anki deck with

```bash
python generate-deck.py
```

(Requires https://github.com/kerrickstaley/genanki, which is on PyPI and conda-forge.)

Import the `hsk1.apkg` into Anki Desktop or AnkiDroid. AnkiWeb is a convenient way to get it from laptop to phone.
