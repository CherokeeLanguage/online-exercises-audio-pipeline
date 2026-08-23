from traceback import print_exc
from flask import Flask, request
from flask_cors import CORS

from parsing.prefixes_syllabary import all_parses

app = Flask(__name__)
CORS(app)


@app.post("/parse-word")
def parse_word():
    query = request.json
    if query is None:
        return {"type": "error", "error": "Could not parse query"}

    syllabary = query.get("syllabary", "")

    parses = list(str(p) for p in all_parses(syllabary))

    return {
        "type": "success",
        "parses": parses,
    }
