#!/usr/bin/env python3
"""
add_publication.py
===================

Turn a BibTeX entry into an entry on your static homepage, automatically.
No Hugo, no build step -- this just edits two things in the site/ folder:

    site/data/publications.json   (the one data file both index.html and
                                   pages/publications.html read from)
    site/citations/<key>.bib      (the raw citation, for the "Cite" link)

Usage
-----
    python tools/add_publication.py path/to/entry.bib
    python tools/add_publication.py path/to/entry.bib --force
    python tools/add_publication.py path/to/entry.bib --site-dir /path/to/site
    python tools/add_publication.py path/to/entry.bib --pdf path/to/paper.pdf

What it does
------------
1. Reads a .bib file (one entry, or many -- e.g. a whole references.bib).
2. For each entry, works out whether it's a journal article
   (@article), a conference paper (@inproceedings), or something else
   (e.g. keywords={P} for "in preparation" is mapped to type "preparation";
   anything else defaults to "journal" for @article and "conference" for
   @inproceedings).
3. Skips entries that already exist in publications.json, matched by DOI
   first, and by fuzzy title match as a fallback (so it's safe to re-run
   this on your whole references.bib as it grows -- nothing gets
   duplicated unless you pass --force).
4. Appends the new entry to data/publications.json and writes
   citations/<key>.bib. Both pages sort by the `date` field at page-load
   time in the browser, so ordering is automatic on every visit -- you
   never edit HTML by hand.
5. With --pdf, copies the given PDF to assets/pdfs/<key>.pdf and sets the
   entry's "pdf" field, which makes a "PDF" / "Read PDF" link appear that
   opens the file in an in-page viewer (see assets/js/pdf-modal.js)
   instead of navigating away. Only added for entries that only exist as
   a single-entry .bib file (one paper at a time), since one PDF maps to
   one key.

New entries are added with "featured": false. Making something a Featured
Publication (with the case-study write-up and thumbnail image on the
homepage) is a deliberate editorial step -- open data/publications.json,
find the entry, set "featured": true, and add "image" / "imageAlt" / a
"narrative" object with "problem" / "introduced" / "whyItMatters" strings,
plus copy an image into site/assets/images/. That content doesn't exist in a .bib file,
so this script can't invent it for you.

No third-party dependencies. Just Python 3.
"""

import argparse
import datetime
import json
import os
import re
import sys

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Minimal LaTeX-accent -> Unicode conversion, covering the accents that
# show up in this author's bib entries (Czech/Central-European names and
# German umlauts). Not a full LaTeX de-escaper -- just enough for real
# co-author names like Bažant, Zdeněk, Dönmez, Matouš.
LATEX_ACCENTS = [
    (r"\{\\v\{z\}\}", "ž"), (r"\{\\v\{Z\}\}", "Ž"),
    (r"\{\\v\{e\}\}", "ě"), (r"\{\\v\{E\}\}", "Ě"),
    (r"\{\\v\{s\}\}", "š"), (r"\{\\v\{S\}\}", "Š"),
    (r'\{\\"o\}', "ö"), (r'\{\\"O\}', "Ö"),
    (r'\{\\"u\}', "ü"), (r'\{\\"U\}', "Ü"),
    (r"\{\\'e\}", "é"), (r"\{\\'E\}", "É"),
    (r"\\v\{z\}", "ž"), (r"\\v\{e\}", "ě"), (r"\\v\{s\}", "š"),
]

# Name the script's owner so "Xu, H." / "H. Xu" / etc. all normalize to
# the same display string used throughout the site.
OWNER_LAST_NAME = "xu"
OWNER_DISPLAY_NAME = "Houlin Xu"


def delatex(text):
    for pattern, repl in LATEX_ACCENTS:
        text = re.sub(pattern, repl, text)
    # strip simple one-argument text-formatting commands, keeping their
    # contents, e.g. "\textbf{Xu, H.}" -> "Xu, H."
    text = re.sub(r"\\text[a-z]+\{([^{}]*)\}", r"\1", text)
    # drop any leftover brace-protection groups, e.g. {Xu} -> Xu
    text = re.sub(r"[{}]", "", text)
    return text


def parse_bib_entries(bib_text):
    """Split a .bib file into entry dicts: type, cite key, raw block, fields."""
    entries = []
    i = 0
    n = len(bib_text)
    while i < n:
        at = bib_text.find("@", i)
        if at == -1:
            break
        m = re.match(r"@(\w+)\s*\{\s*([^,]+),", bib_text[at:])
        if not m:
            i = at + 1
            continue
        entry_type = m.group(1).lower()
        cite_key = m.group(2).strip()
        brace_start = bib_text.find("{", at)
        depth = 0
        j = brace_start
        while j < n:
            if bib_text[j] == "{":
                depth += 1
            elif bib_text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        raw_block = bib_text[at:j + 1]
        fields = parse_fields(bib_text[brace_start + 1:j])
        entries.append({"type": entry_type, "key": cite_key, "raw": raw_block, "fields": fields})
        i = j + 1
    return entries


def parse_fields(body):
    """Parse `field = {value},` or `field={value},` pairs, honoring nested braces."""
    fields = {}
    n = len(body)
    first_comma = body.find(",")
    i = first_comma + 1 if first_comma != -1 else 0
    while i < n:
        m = re.match(r"\s*([\w]+)\s*=\s*", body[i:])
        if not m:
            i += 1
            continue
        field_name = m.group(1).lower()
        i += m.end()
        if i < n and body[i] == "{":
            depth = 0
            j = i
            while j < n:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            value = body[i + 1:j]
            i = j + 1
        else:
            j = i
            while j < n and body[j] != ",":
                j += 1
            value = body[i:j]
            i = j
        fields[field_name] = value.strip().strip(",").strip()
        comma = body.find(",", i)
        i = comma + 1 if comma != -1 else n
    return fields


def split_authors(author_field):
    parts = [p.strip() for p in re.split(r"\s+and\s+", author_field) if p.strip()]
    names = []
    for p in parts:
        p = delatex(p)
        if "," in p:
            last, first = [x.strip() for x in p.split(",", 1)]
        else:
            bits = p.split()
            last, first = bits[-1], " ".join(bits[:-1])
        if last.lower() == OWNER_LAST_NAME and first.strip().lower().startswith("h"):
            names.append(OWNER_DISPLAY_NAME)
        else:
            names.append(f"{first} {last}".strip())
    return names


def make_key(cite_key):
    key = cite_key.lower()
    key = re.sub(r"[^a-z0-9]+", "-", key).strip("-")
    return key or "untitled"


def build_date(fields):
    year = fields.get("year", "").strip()
    if not year:
        return None
    month_raw = fields.get("month", "1").strip().lower()
    month = MONTH_MAP.get(month_raw[:3])
    if month is None:
        try:
            month = int(re.sub(r"[^\d]", "", month_raw) or 1)
        except ValueError:
            month = 1
    try:
        return f"{int(year):04d}-{month:02d}-01"
    except ValueError:
        return None


def normalize_doi(doi):
    doi = (doi or "").strip().strip("'\"")
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    return doi.lower()


def title_words(title):
    return set(re.findall(r"[a-z0-9]+", (title or "").lower()))


def title_match(new_title, existing_pubs):
    new_words = title_words(new_title)
    if not new_words:
        return None
    for p in existing_pubs:
        existing_words = title_words(p.get("title"))
        if not existing_words:
            continue
        overlap = len(new_words & existing_words)
        smaller = min(len(new_words), len(existing_words))
        if overlap >= 4 and overlap / smaller >= 0.8:
            return p
    return None


def find_duplicate(entry_fields, existing_pubs):
    doi = normalize_doi(entry_fields.get("doi", ""))
    if doi:
        for p in existing_pubs:
            if p.get("doi") and normalize_doi(p["doi"]) == doi:
                return p
    title = delatex(entry_fields.get("title", ""))
    return title_match(title, existing_pubs)


def infer_type(entry):
    keyword = entry["fields"].get("keywords", "").strip().upper()
    if keyword == "P" or keyword == "R":
        return "preparation"
    if entry["type"] == "article":
        return "journal"
    if entry["type"] == "inproceedings":
        return "conference"
    return "journal"


def build_pub_entry(entry):
    f = entry["fields"]
    title = delatex(f.get("title", "Untitled")).replace("\n", " ")
    title = re.sub(r"\s+", " ", title).strip()
    authors = split_authors(f.get("author", OWNER_DISPLAY_NAME))
    pub_type = infer_type(entry)

    if entry["type"] == "article":
        venue = f.get("journal", "")
    elif entry["type"] == "inproceedings":
        venue = f.get("booktitle", "")
    else:
        venue = f.get("booktitle", f.get("journal", f.get("howpublished", "")))
    venue = delatex(venue).strip() or None

    year_str = f.get("year", "").strip()
    year = int(year_str) if year_str.isdigit() else None
    date = build_date(f)
    doi_raw = f.get("doi", "").strip()
    doi = None
    if doi_raw:
        doi = doi_raw if doi_raw.startswith("http") else f"https://doi.org/{doi_raw}"

    key = make_key(entry["key"])
    return {
        "key": key,
        "type": pub_type,
        "title": title,
        "authors": authors,
        "venue": venue,
        "year": year,
        "date": date,
        "doi": doi,
        # root-absolute path: works the same whether it's read from
        # index.html (site root) or pages/publications.html (subfolder)
        "cite": f"/citations/{key}.bib",
        "featured": False,
    }


def load_publications(json_path):
    if not os.path.isfile(json_path):
        return []
    with open(json_path, encoding="utf-8") as fh:
        return json.load(fh)


def save_publications(json_path, pubs):
    # sorted purely for human readability of the file -- the pages
    # re-sort by date in JS regardless of file order.
    def sort_key(p):
        return p.get("date") or "0000-00-00"
    pubs_sorted = sorted(pubs, key=sort_key, reverse=True)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(pubs_sorted, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def process_bib_file(bib_path, site_dir, force=False, pdf_path=None):
    with open(bib_path, encoding="utf-8") as fh:
        bib_text = fh.read()

    entries = parse_bib_entries(bib_text)
    json_path = os.path.join(site_dir, "data", "publications.json")
    citations_dir = os.path.join(site_dir, "citations")
    os.makedirs(citations_dir, exist_ok=True)
    pubs = load_publications(json_path)

    if pdf_path and len(entries) > 1:
        raise SystemExit("--pdf only makes sense with a single-entry .bib file "
                          "(one PDF can't map to multiple publications)")

    added, skipped = [], []

    for entry in entries:
        dup = None if force else find_duplicate(entry["fields"], pubs)
        if dup:
            skipped.append((entry["key"], dup["key"]))
            continue

        pub = build_pub_entry(entry)
        # pub["cite"] is a root-absolute URL path like "/citations/key.bib";
        # strip the leading slash to get the on-disk path under site_dir.
        cite_path = os.path.join(site_dir, pub["cite"].lstrip("/"))
        with open(cite_path, "w", encoding="utf-8") as fh:
            fh.write(entry["raw"].strip() + "\n")

        if pdf_path:
            pdfs_dir = os.path.join(site_dir, "assets", "pdfs")
            os.makedirs(pdfs_dir, exist_ok=True)
            dest = os.path.join(pdfs_dir, f"{pub['key']}.pdf")
            with open(pdf_path, "rb") as src, open(dest, "wb") as dst:
                dst.write(src.read())
            pub["pdf"] = f"/assets/pdfs/{pub['key']}.pdf"

        pubs.append(pub)
        added.append(pub)

    if added:
        save_publications(json_path, pubs)

    return added, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("bib_file", help="Path to a .bib file (one entry or many)")
    parser.add_argument("--site-dir", default="site", help="Path to the site/ folder (default: ./site)")
    parser.add_argument("--force", action="store_true", help="Add even if a DOI/title match already exists")
    parser.add_argument("--pdf", metavar="PATH", help="PDF to attach, copied to assets/pdfs/<key>.pdf "
                                                       "(enables the in-page 'Read PDF' viewer)")
    args = parser.parse_args()

    added, skipped = process_bib_file(args.bib_file, args.site_dir, force=args.force, pdf_path=args.pdf)

    if added:
        print(f"Added {len(added)} publication(s):")
        for p in added:
            pdf_note = f"  (+ site{p['pdf']})" if p.get("pdf") else ""
            print(f"  + {p['key']}  ({p['type']}, {p['date'] or 'no date'})  ->  site{p['cite']}{pdf_note}")
        print("\ndata/publications.json updated. Commit and push site/ to publish --")
        print("no HTML needs editing, both pages re-sort by date automatically.")
    if skipped:
        print(f"Skipped {len(skipped)} entr(y/ies) that already exist (use --force to add anyway):")
        for key, existing_key in skipped:
            print(f"  = {key}  (matches existing entry '{existing_key}')")
    if not added and not skipped:
        print("No entries found in the given .bib file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
