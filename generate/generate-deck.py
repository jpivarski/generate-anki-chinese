import json
import os
import glob

import genanki

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
        return f"images-small/{self.group}-{self.index:02d}-{self.hanzi}.png"

    def audio_filename(self):
        return f"audio/cmn-{self.hanzi}.mp3"


with open("all-words.tsv") as file:
    all_words = [Word(*line.rstrip().split("\t")) for line in file]


uniqueid1 = 1778988700
uniqueid2 = 1450502968

hanzi_writer = """
<script src="https://cdn.jsdelivr.net/npm/hanzi-writer@3.5/dist/hanzi-writer.min.js"></script>

<div style="margin-left: auto; margin-right: auto; padding: none;">
  <div id="hanzi0" style="display: inline-block; margin: none; padding: none;"></div>
  <div id="hanzi1" style="display: inline-block; margin: none; padding: none;"></div>
  <div id="hanzi2" style="display: inline-block; margin: none; padding: none;"></div>
</div>

<script>
var word = "{{Answer}}";
var writers = [];
if (word.length > 0) {
  writers.push(HanziWriter.create("hanzi0", word[0], {
    width: 80,
    height: 80,
    padding: 0,
    margin: 0,
    showOutline: true,
    strokeColor: '#0000ff',
    strokeAnimationSpeed: 2,
    delayBetweenStrokes: 100
  }));
  document.getElementById("hanzi0").addEventListener("click", function() {
    writers[0].animateCharacter();
  });
}
if (word.length > 1) {
  writers.push(HanziWriter.create("hanzi1", word[1], {
    width: 80,
    height: 80,
    padding: 0,
    margin: 0,
    showOutline: true,
    strokeColor: '#0000ff',
    strokeAnimationSpeed: 2,
    delayBetweenStrokes: 100
  }));
  document.getElementById("hanzi1").addEventListener("click", function() {
    writers[1].animateCharacter();
  });
}
if (word.length > 2) {
  writers.push(HanziWriter.create("hanzi2", word[2], {
    width: 80,
    height: 80,
    padding: 0,
    margin: 0,
    showOutline: true,
    strokeColor: '#0000ff',
    strokeAnimationSpeed: 2,
    delayBetweenStrokes: 100
  }));
  document.getElementById("hanzi2").addEventListener("click", function() {
    writers[2].animateCharacter();
  });
}
</script>
"""

speak = """
<script>
document.getElementById("speak").onclick = function() {
  var utterance = new SpeechSynthesisUtterance(this.textContent);
  utterance.lang = "zh-CN";
  utterance.rate = 0.5;
  window.speechSynthesis.speak(utterance);
};
</script>
"""

model = genanki.Model(
    model_id=uniqueid1,
    name="Basic (type in the answer) (Jim)",
    fields=[
        {"name": "Overview"},
        {"name": "Chinese"},
        {"name": "ChineseBlank"},
        {"name": "English"},
        {"name": "Definition"},
        {"name": "Picture"},
        {"name": "Audio"},
        {"name": "Answer"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": """
<div style="font-size: 15px; line-height: 1; padding-bottom: 0px; margin-bottom: 0px;">&ldquo;{{English}}&rdquo;</div>
<div style="font-size: 40px; padding-top: 0px; margin-top: 0px;" id="speak">{{ChineseBlank}}</div>

{{Picture}}

<div style="margin-left: 10px; margin-right: 10px;">
{{Definition}}
</div>
{{Audio}}

{{type:Answer}}
""" + speak,
            "afmt": """
<div style="font-size: 15px; line-height: 1; padding-bottom: 0px; margin-bottom: 0px;">&ldquo;{{English}}&rdquo;</div>
<div style="font-size: 40px; padding-top: 0px; margin-top: 0px;" id="speak">{{Chinese}}</div>

{{Picture}}
""" + hanzi_writer + """

<div style="margin-left: 10px; margin-right: 10px;">
{{Definition}}
</div>
{{Audio}}

{{type:Answer}}

<hr id=answer>
""" + speak,
        }
    ],
    css="""
.card {
  font-family: 'Noto Sans';
  font-size: 20px;
  line-height: 1.05;
  text-align: center;
  color: black;
  background-color: white;
}

.card.nightMode {
  font-family: 'Noto Sans';
  font-size: 20px;
  line-height: 1.05;
  text-align: center;
  color: black;
  background-color: white;
}
""",
    model_type=0,
)

model_learn = genanki.Model(
    model_id=uniqueid1 + 1,
    name="Basic (type in the answer) (Jim; Learn)",
    fields=model.fields,
    templates=[
        {
            "name": "Card 1",
            "qfmt": """
<div style="font-size: 15px; line-height: 1; padding-bottom: 0px; margin-bottom: 0px;">&ldquo;{{English}}&rdquo;</div>
<div style="font-size: 40px; padding-top: 0px; margin-top: 0px;" id="speak">{{Chinese}}</div>

{{Picture}}
""" + hanzi_writer + """

<div style="margin-left: 10px; margin-right: 10px;">
{{Definition}}
</div>
{{Audio}}

{{type:Answer}}
""" + speak,
            "afmt": """
<div style="font-size: 15px; line-height: 1; padding-bottom: 0px; margin-bottom: 0px;">&ldquo;{{English}}&rdquo;</div>
<div style="font-size: 40px; padding-top: 0px; margin-top: 0px;" id="speak">{{Chinese}}</div>

{{Picture}}
""" + hanzi_writer + """

<div style="margin-left: 10px; margin-right: 10px;">
{{Definition}}
</div>
{{Audio}}

{{type:Answer}}

<hr id=answer>
""" + speak,
        }
    ],
    css=model.css,
)

gist_markdown = []
current_group = None
toc = []

decks = {}

audio_filenames = []
image_filenames = []
count = 0
for word in all_words:
    # FIXME: this is partial
    if word.group == "HSK1_027":
        continue

    if os.path.exists(word.hint_filename()) and os.path.exists(word.image_filename()):
        count += 1;

        if word.group not in decks:
            decks[word.group] = genanki.Deck(uniqueid2 + len(decks), "quiz::" + word.group.replace("_", "::"))
            decks[word.group + "_learn"] = genanki.Deck(uniqueid2 + len(decks), "learn::" + word.group.replace("_", "::"))
        deck = decks[word.group]
        deck_learn = decks[word.group + "_learn"]

        with open(word.hint_filename()) as file:
            response = json.load(file)
        content = json.loads(response["choices"][0]["message"]["content"])
        image = f"<img src=\"{word.image_filename().split('/', 1)[1]}\" style=\"width: 180px; float: left; margin-right: 10px; margin-bottom: 10px;\">"
        chinese = content["sentence"].replace(word.hanzi, f"<span style=\"color: #0000ff;\">{word.hanzi}</span>")
        chinese_blank = content["sentence"].replace(word.hanzi, "<span style=\"text-decoration: underline; color: #0000ff;\">&nbsp;&nbsp;&nbsp;</span>")
        english = content["sentence_translation"]
        definition = content["better_definition"]
        image_filenames.append(word.image_filename())

        if os.path.exists(word.audio_filename()):
            audio = f"[sound:{word.audio_filename().split('/', 1)[1]}]"
        else:
            audio = ""

        overview = f"{word.group}_{word.index:02d} {word.hanzi} {word.definition}"

        deck.add_note(
            genanki.Note(model, ["Q_" + overview, chinese, chinese_blank, english, definition, image, audio, word.hanzi])
        )
        deck_learn.add_note(
            genanki.Note(model_learn, ["L_" + overview, chinese, chinese_blank, english, definition, image, audio, word.hanzi])
        )

        if current_group != word.group:
            gist_markdown.append(f"""## {word.group}
""")
            toc.append(f"- [{word.group}](#{word.group.lower()})")
        current_group = word.group

        gist_markdown.append(f"""### {word.hanzi} :: {content['better_definition']}

“{content['sentence_translation']}”

{content['sentence']}

![](images-verysmall/{word.group}-{word.index:02d}-{word.hanzi}.png)
""")

package = genanki.Package([deck for name, deck in sorted(decks.items())])
package.media_files = image_filenames
package.write_to_file("hsk1.apkg")

with open("../HSK1/README.md", "w") as file:
    file.write("\n".join(toc + [""] + gist_markdown))

print(f"{count} words in the deck")
