import json

from cnd.utils import audio_url


def audio_mixin(syllabary: str) -> dict:
    audio = sentences.get(syllabary.replace("*", ""), {}).get("audio", None)
    if not audio:
        return {}
    return {"audio": audio_url(audio)}


dict = json.load(open("dict_verbs_large.json"))
sentences = {
    s["syllabary"]: s
    for s in json.load(open("data/cnd/sentences.json"))
    if s["syllabary"]
}

dict_with_audio = {
    index: {
        **entry,
        "sentence": {
            **entry.get("sentence", {}),
            **audio_mixin(entry["sentence"]["syllabary"]),
        },
    }
    for index, entry in dict.items()
}

json.dump(
    dict_with_audio, open("dict_verbs_audio.json", "w"), ensure_ascii=False, indent=2
)
