#!/usr/bin/env python

#
# A code to get page_ids of WP chemistry pages and then download these pages
# this is supporting code for publication:
# Peter Ertl
# Molecules in Wikipedia: Analysis of their chemical diversity, functional roles, and popularity
# published in
# J. Chem. Inf. Model. 2025 or 2026
#

import requests
import sys
import os
import time
import json

API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "ChemBot/1.0 (YOUR EMAIL)"
}

# ----------------------------------------------------------------------------
# Fetch list of pages embedding a template Chembox or Infobox_drug
# ----------------------------------------------------------------------------

def getitems(template_name, eicontinue=""):

    time.sleep(1)  # be polite

    params = {
        "action": "query",
        "format": "json",
        "list": "embeddedin",
        "eititle": template_name,
        "eilimit": "500",
    }
    if eicontinue:
        params["eicontinue"] = eicontinue

    resp = requests.get(API_URL, params=params, headers=HEADERS)
    data = resp.json()

    items = data["query"]["embeddedin"]
    next_ei = data.get("continue", {}).get("eicontinue", None)

    return items, next_ei

# ----------------------------------------------------------------------------
# Fetch a page's wikitext
# ----------------------------------------------------------------------------

def get_page_wikitext(page_title):
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": page_title,
        "rvprop": "content",
        "rvslots": "main",
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS)
    data = resp.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    return page["revisions"][0]["slots"]["main"]["*"]

# ----------------------------------------------------------------------------
# Main logic
# ----------------------------------------------------------------------------

template = "Template:Infobox_drug"   # Change to "Template:Chembox" if needed

# Remove old file
if os.path.exists("page_ids.txt"):
    os.remove("page_ids.txt")

# Download all page IDs and titles
eci = ""
with open("page_ids.txt", "a", encoding="utf-8") as fw:
    while True:
        items, eci = getitems(template, eicontinue=eci)
        for item in items:
            fw.write(f"{item['title']}\t{item['pageid']}\n")
        if not eci:
            break

# Download individual pages
with open("page_ids.txt", encoding="utf-8") as f:
    for n, line in enumerate(f, start=1):
        page_title, page_id = line.strip().split("\t")
        sys.stderr.write(f"{n}\r")
        sys.stderr.flush()

        text = get_page_wikitext(page_title)

        with open(f"wp-{page_id}.txt", "w", encoding="utf-8") as fw:
            fw.write(text)

        time.sleep(1)   # polite delay

        # for testing, comment for production
        if n >= 10: break

