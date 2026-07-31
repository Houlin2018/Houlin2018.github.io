#!/usr/bin/env python3
"""
add_publication.py
===================

Turn a BibTeX entry into a Hugo Blox publication page, automatically.

Usage
-----
    python scripts/add_publication.py path/to/entry.bib
    python scripts/add_publication.py path/to/entry.bib --force
    python scripts/add_publication.py path/to/entry.bib --all
    python scripts/add_publication.py path/to/entry.bib --repo-root /path/to/site

What it does
------------
1. Reads a .bib file (one entry, or many -- e.g. your master references.bib).
2. For each entry tagged keywords={J} (journal article) or keywords={C}
   (conference paper), it creates:
       content/publication/<slug>/index.md   (Hugo front matter)
       content/publication/<slug>/cite.bib    (the raw BibTeX entry)
3. Skips entries whose slug already exists in content/publication/, so you
   can safely re-run this on your whole references.bib as it grows --
   nothing gets duplicated or overwritten unless you pass --force.
4. Does NOT do any sorting itself. Hugo Blox's "collection" widget (used by
   both the "Featured Publications" and "Recent Publications" blocks on the
   homepage, and by the /publication/ list page) reads the `date` field of
   every content/publication/*/index.md file and sorts newest-first at
   build time. So the only thing this script has to get right is the date
   -- ordering is then automatic, on every rebuild, forever.

Other keyword types (P = in preparation, T = talk, D = demo, R = working
paper/preprint) are skipped by default, matching how this site has been
curated so far -- pass --all to include everything instead.

No third-party dependencies. Just Python 3.
"""

import argparse
import datetime
import os
import re
import sys

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Minimal LaTeX-accent -> Unicode conversion, covering the accents that
# actually show up in this site's bib file (Czech/Central-European names
# and German umlauts). Not a full LaTeX de-escaper -- just enough for real
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


def delatex(text):
    for pattern, repl in LATEX_ACCENTS:
        text = re.sub(pattern, repl, text)
    # strip simple one-argument text-formatting commands, keeping their
    # contents, e.g. "\textbf{Xu, H.}" -> "Xu, H." (otherwise the leftover
    # "\textbf" text glues onto the name and breaks author matching below)
    text = re.sub(r"\\text[a-z]+\{([^{}]*)\}", r"\1", text)
    # drop any leftover brace-protection groups, e.g. {Xu} -> Xu
    text = re.sub(r"[{}]", "", text)
    return text


def parse_bib_entries(bib_text):
    """Split a .bib file into raw entry blocks: (entry_type, cite_key, raw_block, fields)."""
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
        # find matching closing brace by depth counting, starting at the '{' after @type
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
        entries.append({
            "type": entry_type,
            "key": cite_key,
            "raw": raw_block,
            "fields": fields,
        })
        i = j + 1
    return entries


def parse_fields(body):
    """Parse `field = {value},` or `field={value},` pairs, honoring nested braces."""
    fields = {}
    i = 0
    n = len(body)
    # skip past the cite key's own trailing comma (body starts right after "key,")
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
            # unbraced value, e.g. month=6 -- read until next comma at depth 0
            j = i
            while j < n and body[j] != ",":
                j += 1
            value = body[i:j]
            i = j
        fields[field_name] = value.strip().strip(",").strip()
        # advance past the comma separating fields
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
            # already "First Last"
            bits = p.split()
            last, first = bits[-1], " ".join(bits[:-1])
        # Houlin Xu, in any initialed form, maps to the site's "admin" author
        if last.lower() == "xu" and first.strip().lower().startswith("h"):
            names.append("admin")
        else:
            names.append(f"{first} {last}".strip())
    return names


def make_slug(cite_key):
    slug = cite_key.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "untitled"


def build_date(fields):
    year = fields.get("year", "").strip() or str(datetime.date.today().year)
    month_raw = fields.get("month", "1").strip().lower()
    month = MONTH_MAP.get(month_raw[:3], None)
    if month is None:
        try:
            month = int(re.sub(r"[^\d]", "", month_raw) or 1)
        except ValueError:
            month = 1
    return f"{int(year):04d}-{month:02d}-01"


def build_front_matter(entry, slug):
    f = entry["fields"]
    title = delatex(f.get("title", "Untitled")).replace("\n", " ")
    title = re.sub(r"\s+", " ", title).strip()
    authors = split_authors(f.get("author", "admin"))

    if entry["type"] == "article":
        pub_type = "article-journal"
        venue = f.get("journal", "")
    elif entry["type"] == "inproceedings":
        pub_type = "paper-conference"
        venue = f.get("booktitle", "")
    else:
        pub_type = "manuscript"
        venue = f.get("booktitle", f.get("journal", f.get("howpublished", "")))
    venue = delatex(venue).strip()

    date_str = build_date(f)
    doi = f.get("doi", "").strip()
    keyword = f.get("keywords", "").strip().upper()

    lines = ["---"]
    # Hugo needs a multi-line-safe title; quote it.
    lines.append(f'title: "{title}"')
    lines.append("authors:")
    for a in authors:
        lines.append(f"- {a}")
    lines.append(f"date: '{date_str}'")
    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        lines.append(f"doi: '{doi_url}'")
    lines.append(f"publishDate: '{datetime.datetime.utcnow().isoformat()}Z'")
    lines.append("publication_types:")
    lines.append(f"- {pub_type}")
    if venue:
        lines.append(f"publication: '*{venue}*'")
    if keyword:
        lines.append("tags:")
        lines.append(f"- {keyword}")
    lines.append("featured: false")
    lines.append("---")
    return "\n".join(lines) + "\n"


def normalize_doi(doi):
    doi = doi.strip().strip("'\"")
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    return doi.lower()


def title_words(title):
    """Break a title into a set of lowercase word tokens, for fuzzy matching.

    Some of this site's older publication pages store the title as an
    unquoted, folded YAML scalar, so a plain regex only picks up the first
    line -- a truncated but otherwise verbatim chunk of the full title.
    Some bib entries also insert an acronym mid-title (e.g. "(slCBM)")
    that the hand-written page title omits. A word-overlap comparison
    (see title_match) tolerates both without needing exact string equality.
    """
    return set(re.findall(r"[a-z0-9]+", title.lower()))


def existing_dois(pub_dir):
    """Scan every content/publication/*/index.md for its doi: field.

    This site's publication folders have been named inconsistently over time
    (art-2 vs art2, scbm vs art8, ...), so matching on slug alone misses
    duplicates. Matching on DOI is reliable regardless of folder naming.
    Returns {normalized_doi: folder_name}.
    """
    found = {}
    if not os.path.isdir(pub_dir):
        return found
    for name in os.listdir(pub_dir):
        index_path = os.path.join(pub_dir, name, "index.md")
        if not os.path.isfile(index_path):
            continue
        with open(index_path, "r", encoding="utf-8") as fh:
            text = fh.read()
        m = re.search(r"^doi:\s*['\"]?([^'\"\n]+)", text, re.MULTILINE)
        if m:
            found[normalize_doi(m.group(1))] = name
    return found


def existing_titles(pub_dir):
    """Scan every content/publication/*/index.md for its title: field.

    Many entries in the site's master bib file have no doi field at all
    (the DOI was hand-added to the page later after a web search), so DOI
    matching alone misses those. Title matching (fuzzy, prefix-tolerant --
    see normalize_title) is the fallback that catches them regardless of
    which folder name or exact title wording was used historically.
    Returns a list of (word_set, folder_name) pairs.
    """
    found = []
    if not os.path.isdir(pub_dir):
        return found
    for name in os.listdir(pub_dir):
        index_path = os.path.join(pub_dir, name, "index.md")
        if not os.path.isfile(index_path):
            continue
        with open(index_path, "r", encoding="utf-8") as fh:
            text = fh.read()
        m = re.search(r"^title:\s*(.*)$", text, re.MULTILINE)
        if not m:
            continue
        raw = m.group(1).strip()
        # strip a matching pair of surrounding quotes, if present
        if len(raw) >= 2 and raw[0] in "'\"" and raw[-1] == raw[0]:
            raw = raw[1:-1]
        words = title_words(raw)
        if words:
            found.append((words, name))
    return found


def title_match(new_title, title_index):
    """Return the folder name of an existing publication with a matching
    title, or None. A match requires the smaller title's words to be almost
    entirely (>=80%) contained in the larger title's words -- tolerant of
    truncation and small wording differences, but requires at least 4
    shared words so short/generic titles can't false-positive on each
    other."""
    new_words = title_words(new_title)
    if not new_words:
        return None
    for existing_words, folder in title_index:
        if not existing_words:
            continue
        overlap = len(new_words & existing_words)
        smaller = min(len(new_words), len(existing_words))
        if overlap >= 4 and overlap / smaller >= 0.8:
            return folder
    return None


def process_bib_file(bib_path, repo_root, force=False, include_all=False):
    with open(bib_path, "r", encoding="utf-8") as fh:
        bib_text = fh.read()

    entries = parse_bib_entries(bib_text)
    pub_dir = os.path.join(repo_root, "content", "publication")
    os.makedirs(pub_dir, exist_ok=True)
    doi_index = existing_dois(pub_dir)
    title_index = existing_titles(pub_dir)

    created, skipped_kw, skipped_exists = [], [], []

    for entry in entries:
        keyword = entry["fields"].get("keywords", "").strip().upper()
        if not include_all and keyword not in ("J", "C"):
            skipped_kw.append((entry["key"], keyword or "(none)"))
            continue

        title = delatex(entry["fields"].get("title", "")).replace("\n", " ")
        title = re.sub(r"\s+", " ", title).strip()

        doi = entry["fields"].get("doi", "").strip()
        if doi and not force:
            existing_folder = doi_index.get(normalize_doi(doi))
            if existing_folder:
                skipped_exists.append((entry["key"], f"{existing_folder} (matched by DOI)"))
                continue

        if title and not force:
            existing_folder = title_match(title, title_index)
            if existing_folder:
                skipped_exists.append((entry["key"], f"{existing_folder} (matched by title)"))
                continue

        slug = make_slug(entry["key"])
        target_dir = os.path.join(pub_dir, slug)
        if os.path.exists(target_dir) and not force:
            skipped_exists.append((entry["key"], slug))
            continue

        os.makedirs(target_dir, exist_ok=True)
        front_matter = build_front_matter(entry, slug)
        with open(os.path.join(target_dir, "index.md"), "w", encoding="utf-8") as fh:
            fh.write(front_matter)
        with open(os.path.join(target_dir, "cite.bib"), "w", encoding="utf-8") as fh:
            fh.write(entry["raw"].strip() + "\n")

        created.append((entry["key"], slug))
        if doi:
            doi_index[normalize_doi(doi)] = slug
        if title:
            title_index.append((title_words(title), slug))

    return created, skipped_kw, skipped_exists


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("bib_file", help="Path to a .bib file (one entry or many)")
    parser.add_argument("--repo-root", default=".", help="Path to the Hugo site root (default: current directory)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing publication folders")
    parser.add_argument("--all", dest="include_all", action="store_true",
                         help="Also import non J/C entries (posters, talks, working papers, etc.)")
    args = parser.parse_args()

    created, skipped_kw, skipped_exists = process_bib_file(
        args.bib_file, args.repo_root, force=args.force, include_all=args.include_all
    )

    if created:
        print(f"Created {len(created)} publication page(s):")
        for key, slug in created:
            print(f"  + {key}  ->  content/publication/{slug}/")
    if skipped_exists:
        print(f"Skipped {len(skipped_exists)} entr(y/ies) that already exist (use --force to overwrite):")
        for key, slug in skipped_exists:
            print(f"  = {key}  ->  content/publication/{slug}/")
    if skipped_kw:
        print(f"Skipped {len(skipped_kw)} entr(y/ies) not tagged J or C (use --all to include everything):")
        for key, kw in skipped_kw:
            print(f"  - {key}  (keywords={kw})")

    if created:
        print("\nNothing else to do -- Hugo's collection widget sorts by date at build time,")
        print("so the new entr(y/ies) will appear correctly ordered in Featured/Recent")
        print("Publications and the All Publications page on your next `hugo` build.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
