import json

with open("whole-db.json") as f:
    users = json.load(f)

#   "gǎ:da": {
#       "box": 0,
#       "key": "gǎ:da",
#       "lastShownDate": 1682740800000,
#       "nextShowDate": 1682740800000
#     },


def merge_leitner_boxes(
    first: dict[str, dict], second: dict[str, dict]
) -> dict[str, dict]:
    merged: dict[str, dict] = {
        term_key: term_data for term_key, term_data in first.items()
    }
    for term_key, term_data in second.items():
        if term_key not in merged:
            merged[term_key] = term_data
        else:
            merged[term_key]["box"] = max(
                merged[term_key]["box"], second[term_key]["box"]
            )
            merged[term_key]["lastShownDate"] = max(
                merged[term_key]["lastShownDate"], second[term_key]["lastShownDate"]
            )
            merged[term_key]["nextShowDate"] = max(
                merged[term_key]["nextShowDate"], second[term_key]["nextShowDate"]
            )
    return merged


target_uid = "OrYAoNVVUYZpOfuoudvdL3ObOLB2"
source_emails = ["marypriceboday@gmail.com"]
merged_user = users.get(target_uid, {})
if not "leitnerBoxes" in merged_user:
    merged_user["leitnerBoxes"] = {"numBoxes": 6, "terms": {}}

for uid in users:
    email = users[uid].get("config", {}).get("userEmail", None)
    print(f"Reviewing user: {uid} / {email}")

    if email not in source_emails:
        continue

    print(f"Merging in user: {uid}")

    merged_user["leitnerBoxes"]["terms"] = merge_leitner_boxes(
        merged_user.get("leitnerBoxes", {}).get("terms", {}),
        users[uid].get("leitnerBoxes", {}).get("terms", {}),
    )

with open(f"user-{target_uid}.json", "w") as f:
    json.dump(merged_user, f, ensure_ascii=False)
