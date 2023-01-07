from dataclasses import dataclass
from pathlib import Path
import json
from typing import Optional, Union

from common.structs import PhoneticOrthography


@dataclass
class DatasetMetadata:
    audio_source: Path
    annotations: Path
    terms: Path
    folder: Path
    collection_title: str
    collection_id: str
    phoneticOrthography: PhoneticOrthography

    @staticmethod
    def from_file(path: Union[str, Path]):
        if isinstance(path, str):
            path = Path(path)

        with open(path) as f:
            data = json.load(f)

        return DatasetMetadata(
            audio_source=path.parent / Path(data["audio_source"]),
            annotations=path.parent / Path(data["annotations"]),
            terms=path.parent / Path(data["terms"]),
            folder=path.parent,
            collection_id=data["collection_id"],
            collection_title=data["collection_title"],
            phoneticOrthography=PhoneticOrthography(
                data.get("phonetic_orthography", None)
            ),
        )
