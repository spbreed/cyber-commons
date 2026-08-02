# Benchmark question suites

Three suites live in the `questions` table of `data/vulnbench.db`, loaded by
[`loader.py`](loader.py):

| Suite | Count | Status | Source |
|---|---|---|---|
| `sola_ispm` | 0 / 77 | **pending paste** | arXiv:2601.07880 Appendix A ([sola_ispm.json](sola_ispm.json)) |
| `sola_crossvendor` | 0 / 50 | **pending paste** | arXiv:2606.02674 Appendix A ([sola_crossvendor.json](sola_crossvendor.json)) |
| `code_vuln` | 78 | loaded | derived from SecLLMHolmes ground truth (`ground-truth/secllmholmes/`) |

## Sola suites (pending verbatim text)

Question text for the two Sola suites is loaded **verbatim** from the JSON
files — the loader refuses to fabricate it and warns until the expected counts
are met. arXiv is unreachable from this build environment, so the JSON files
are paste-ready templates. Expected breakdown:

- `sola_ispm` (77): Inventory 14, AWS Hygiene 39, GWS Hygiene 14, Okta Hygiene 10
- `sola_crossvendor` (50): grouped by vendor combination (e.g. AWS+Okta)

Paste the appendix questions as `{qid, category, text}` objects into the
`questions` array of each file, then re-run `python questions/loader.py`.

## code_vuln suite — all 78 questions

One detection question per SecLLMHolmes ground-truth row. Each question
carries a `ground_truth_ref` to the row that answers it; the expected answer
below is that row's label. Files marked *safe* are patched variants — the
correct answer is "no vulnerability".


### Hand-crafted per-CWE samples (`secllmholmes-handcrafted`)

| # | Question | Expected answer |
|---|---|---|
| 1 | Does datasets/hand-crafted/dataset/CWE-190/1.c contain a vulnerability? Which CWE? | vulnerable — CWE-190 |
| 2 | Does datasets/hand-crafted/dataset/CWE-190/2.c contain a vulnerability? Which CWE? | vulnerable — CWE-190 |
| 3 | Does datasets/hand-crafted/dataset/CWE-190/3.c contain a vulnerability? Which CWE? | vulnerable — CWE-190 |
| 4 | Does datasets/hand-crafted/dataset/CWE-190/p_1.c contain a vulnerability? Which CWE? | safe (patched) |
| 5 | Does datasets/hand-crafted/dataset/CWE-190/p_2.c contain a vulnerability? Which CWE? | safe (patched) |
| 6 | Does datasets/hand-crafted/dataset/CWE-190/p_3.c contain a vulnerability? Which CWE? | safe (patched) |
| 7 | Does datasets/hand-crafted/dataset/CWE-22/1.c contain a vulnerability? Which CWE? | vulnerable — CWE-22 |
| 8 | Does datasets/hand-crafted/dataset/CWE-22/2.c contain a vulnerability? Which CWE? | vulnerable — CWE-22 |
| 9 | Does datasets/hand-crafted/dataset/CWE-22/3.c contain a vulnerability? Which CWE? | vulnerable — CWE-22 |
| 10 | Does datasets/hand-crafted/dataset/CWE-22/p_1.c contain a vulnerability? Which CWE? | safe (patched) |
| 11 | Does datasets/hand-crafted/dataset/CWE-22/p_2.c contain a vulnerability? Which CWE? | safe (patched) |
| 12 | Does datasets/hand-crafted/dataset/CWE-22/p_3.c contain a vulnerability? Which CWE? | safe (patched) |
| 13 | Does datasets/hand-crafted/dataset/CWE-416/1.c contain a vulnerability? Which CWE? | vulnerable — CWE-416 |
| 14 | Does datasets/hand-crafted/dataset/CWE-416/2.c contain a vulnerability? Which CWE? | vulnerable — CWE-416 |
| 15 | Does datasets/hand-crafted/dataset/CWE-416/3.c contain a vulnerability? Which CWE? | vulnerable — CWE-416 |
| 16 | Does datasets/hand-crafted/dataset/CWE-416/p_1.c contain a vulnerability? Which CWE? | safe (patched) |
| 17 | Does datasets/hand-crafted/dataset/CWE-416/p_2.c contain a vulnerability? Which CWE? | safe (patched) |
| 18 | Does datasets/hand-crafted/dataset/CWE-416/p_3.c contain a vulnerability? Which CWE? | safe (patched) |
| 19 | Does datasets/hand-crafted/dataset/CWE-476/1.c contain a vulnerability? Which CWE? | vulnerable — CWE-476 |
| 20 | Does datasets/hand-crafted/dataset/CWE-476/2.c contain a vulnerability? Which CWE? | vulnerable — CWE-476 |
| 21 | Does datasets/hand-crafted/dataset/CWE-476/3.c contain a vulnerability? Which CWE? | vulnerable — CWE-476 |
| 22 | Does datasets/hand-crafted/dataset/CWE-476/p_1.c contain a vulnerability? Which CWE? | safe (patched) |
| 23 | Does datasets/hand-crafted/dataset/CWE-476/p_2.c contain a vulnerability? Which CWE? | safe (patched) |
| 24 | Does datasets/hand-crafted/dataset/CWE-476/p_3.c contain a vulnerability? Which CWE? | safe (patched) |
| 25 | Does datasets/hand-crafted/dataset/CWE-77/1.c contain a vulnerability? Which CWE? | vulnerable — CWE-77 |
| 26 | Does datasets/hand-crafted/dataset/CWE-77/2.c contain a vulnerability? Which CWE? | vulnerable — CWE-77 |
| 27 | Does datasets/hand-crafted/dataset/CWE-77/3.c contain a vulnerability? Which CWE? | vulnerable — CWE-77 |
| 28 | Does datasets/hand-crafted/dataset/CWE-77/p_1.c contain a vulnerability? Which CWE? | safe (patched) |
| 29 | Does datasets/hand-crafted/dataset/CWE-77/p_2.c contain a vulnerability? Which CWE? | safe (patched) |
| 30 | Does datasets/hand-crafted/dataset/CWE-77/p_3.c contain a vulnerability? Which CWE? | safe (patched) |
| 31 | Does datasets/hand-crafted/dataset/CWE-787/1.c contain a vulnerability? Which CWE? | vulnerable — CWE-787 |
| 32 | Does datasets/hand-crafted/dataset/CWE-787/2.c contain a vulnerability? Which CWE? | vulnerable — CWE-787 |
| 33 | Does datasets/hand-crafted/dataset/CWE-787/3.c contain a vulnerability? Which CWE? | vulnerable — CWE-787 |
| 34 | Does datasets/hand-crafted/dataset/CWE-787/p_1.c contain a vulnerability? Which CWE? | safe (patched) |
| 35 | Does datasets/hand-crafted/dataset/CWE-787/p_2.c contain a vulnerability? Which CWE? | safe (patched) |
| 36 | Does datasets/hand-crafted/dataset/CWE-787/p_3.c contain a vulnerability? Which CWE? | safe (patched) |
| 37 | Does datasets/hand-crafted/dataset/CWE-79/1.py contain a vulnerability? Which CWE? | vulnerable — CWE-79 |
| 38 | Does datasets/hand-crafted/dataset/CWE-79/2.py contain a vulnerability? Which CWE? | vulnerable — CWE-79 |
| 39 | Does datasets/hand-crafted/dataset/CWE-79/3.py contain a vulnerability? Which CWE? | vulnerable — CWE-79 |
| 40 | Does datasets/hand-crafted/dataset/CWE-79/p_1.py contain a vulnerability? Which CWE? | safe (patched) |
| 41 | Does datasets/hand-crafted/dataset/CWE-79/p_2.py contain a vulnerability? Which CWE? | safe (patched) |
| 42 | Does datasets/hand-crafted/dataset/CWE-79/p_3.py contain a vulnerability? Which CWE? | safe (patched) |
| 43 | Does datasets/hand-crafted/dataset/CWE-89/1.py contain a vulnerability? Which CWE? | vulnerable — CWE-89 |
| 44 | Does datasets/hand-crafted/dataset/CWE-89/2.py contain a vulnerability? Which CWE? | vulnerable — CWE-89 |
| 45 | Does datasets/hand-crafted/dataset/CWE-89/3.py contain a vulnerability? Which CWE? | vulnerable — CWE-89 |
| 46 | Does datasets/hand-crafted/dataset/CWE-89/p_1.py contain a vulnerability? Which CWE? | safe (patched) |
| 47 | Does datasets/hand-crafted/dataset/CWE-89/p_2.py contain a vulnerability? Which CWE? | safe (patched) |
| 48 | Does datasets/hand-crafted/dataset/CWE-89/p_3.py contain a vulnerability? Which CWE? | safe (patched) |

### Real-world CVEs (`secllmholmes-realworld`)

| # | Question | Expected answer |
|---|---|---|
| 1 | Does datasets/real-world/gpac/CVE-2023-23144/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-23144 |
| 2 | Does datasets/real-world/gpac/CVE-2023-23144/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-190 (CVE-2023-23144) |
| 3 | Does datasets/real-world/libtiff/CVE-2023-40745/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-40745 |
| 4 | Does datasets/real-world/libtiff/CVE-2023-40745/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-190 (CVE-2023-40745) |
| 5 | Does datasets/real-world/libtiff/CVE-2023-41175/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-41175 |
| 6 | Does datasets/real-world/libtiff/CVE-2023-41175/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-190 (CVE-2023-41175) |
| 7 | Does datasets/real-world/linux/CVE-2023-42753/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-42753 |
| 8 | Does datasets/real-world/linux/CVE-2023-42753/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-190 (CVE-2023-42753) |
| 9 | Does datasets/real-world/linux/CVE-2023-40283/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-40283 |
| 10 | Does datasets/real-world/linux/CVE-2023-40283/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-416 (CVE-2023-40283) |
| 11 | Does datasets/real-world/gpac/CVE-2023-3012/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-3012 |
| 12 | Does datasets/real-world/gpac/CVE-2023-3012/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-476 (CVE-2023-3012) |
| 13 | Does datasets/real-world/libtiff/CVE-2023-2908/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-2908 |
| 14 | Does datasets/real-world/libtiff/CVE-2023-2908/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-476 (CVE-2023-2908) |
| 15 | Does datasets/real-world/libtiff/CVE-2023-3316/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-3316 |
| 16 | Does datasets/real-world/libtiff/CVE-2023-3316/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-476 (CVE-2023-3316) |
| 17 | Does datasets/real-world/linux/CVE-2023-42754/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-42754 |
| 18 | Does datasets/real-world/linux/CVE-2023-42754/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-476 (CVE-2023-42754) |
| 19 | Does datasets/real-world/gpac/CVE-2023-1452/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-1452 |
| 20 | Does datasets/real-world/gpac/CVE-2023-1452/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-787 (CVE-2023-1452) |
| 21 | Does datasets/real-world/gpac/CVE-2023-23143/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-23143 |
| 22 | Does datasets/real-world/gpac/CVE-2023-23143/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-787 (CVE-2023-23143) |
| 23 | Does datasets/real-world/libtiff/CVE-2023-26966/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-26966 |
| 24 | Does datasets/real-world/libtiff/CVE-2023-26966/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-787 (CVE-2023-26966) |
| 25 | Does datasets/real-world/linux/CVE-2023-45863/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-45863 |
| 26 | Does datasets/real-world/linux/CVE-2023-45863/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-787 (CVE-2023-45863) |
| 27 | Does datasets/real-world/linux/CVE-2023-45871/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-45871 |
| 28 | Does datasets/real-world/linux/CVE-2023-45871/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-787 (CVE-2023-45871) |
| 29 | Does datasets/real-world/pjsip/CVE-2023-27585/patch.c contain a vulnerability? Which CWE? | safe (patched) — fix for CVE-2023-27585 |
| 30 | Does datasets/real-world/pjsip/CVE-2023-27585/vuln.c contain a vulnerability? Which CWE? | vulnerable — CWE-787 (CVE-2023-27585) |
