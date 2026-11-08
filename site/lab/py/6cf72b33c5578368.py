"""Knowledge — retrieval pulls documents in at query time. Trust 0.

Anyone who can write into the corpus can put text in front of the advisor.
"""

CORPUS = [
    {"id": "tmpl-1", "text": "Lisbon: three nights, walking tour, tram 28."},
    {"id": "tmpl-2", "text": "Tokyo: rail pass, Shinjuku, day trip to Hakone."},
]


def search(query):
    hits = [d for d in CORPUS if any(w in d["text"].lower()
                                     for w in query.lower().split())]
    return hits or CORPUS[:1]
