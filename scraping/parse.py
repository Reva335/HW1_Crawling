import json
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "yelp_reviews.json"
OUTPUT_FILE = ROOT / "data" / "parsed_reviews.csv"

def _pick_author(node: dict) -> str:
    for parent, key in [
        ("user", "markupDisplayName"),
        ("user", "displayName"),
        ("author", "markupDisplayName"),
        ("author", "displayName"),
        ("author", "name"),
    ]:
        v = node.get(parent, {})
        if isinstance(v, dict):
            name = v.get(key)
            if name:
                return name
    return "Unknown"

def _pick_date(node: dict) -> str:
    for k in ["localizedDateTimeForBusiness", "localizedDate", "createdAt", "timeCreated", "date"]:
        v = node.get(k)
        if v:
            if isinstance(v, dict):
                for inner in [
                    "localeDateTimeForBusiness",
                    "display",
                    "value",
                    "isoString",
                ]:
                    inner_v = v.get(inner)
                    if inner_v:
                        return inner_v
                return json.dumps(v, ensure_ascii=False)
            return v
    return ""

def _pick_text(node: dict) -> str:
    t = node.get("text", {})
    if isinstance(t, dict):
        return t.get("full", "") or ""
    if isinstance(t, str):
        return t
    return ""

def _first_present(d: dict, keys: list, default=None):
    for k in keys:
        v = d.get(k)
        if v is not None:
            return v
    return default

def parse_reviews():
    # Load JSON
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    reviews_out = []

    for op in data if isinstance(data, list) else [data]:
        op_data = op.get("data", {}) if isinstance(op, dict) else {}

        business = op_data.get("business") or {}
        biz_name = _first_present(business, ["name", "displayName"], "")
        biz_alias = business.get("alias", "")
        total_reviews = None
        if isinstance(business.get("reviews"), dict):
            total_reviews = business["reviews"].get("totalCount")
        if total_reviews is None:
            lang_counts = business.get("reviewCountsByLanguage", [])
            if isinstance(lang_counts, list) and lang_counts:
                total_reviews = sum(int(x.get("count", 0)) for x in lang_counts)
        if total_reviews is None:
            total_reviews = ""

        review_edges = []
        if isinstance(business.get("reviews"), dict) and isinstance(business["reviews"].get("edges"), list):
            review_edges = business["reviews"]["edges"]

        if not review_edges:
            pass

        for edge in review_edges:
            node = edge.get("node", {}) if isinstance(edge, dict) else {}
            author = _pick_author(node)
            rating = node.get("rating", "")
            date = _pick_date(node)
            text = _pick_text(node)

            reviews_out.append(
                {
                    "business_name": biz_name,
                    "business_alias": biz_alias,
                    "total_reviews": total_reviews,
                    "author": author,
                    "rating": rating,
                    "date": date,
                    "text": text,
                }
            )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "business_name",
        "business_alias",
        "total_reviews",
        "author",
        "rating",
        "date",
        "text",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in reviews_out:
            w.writerow(row)

    print(f"Saved {len(reviews_out)} reviews to {OUTPUT_FILE}")

if __name__ == "__main__":
    parse_reviews()
