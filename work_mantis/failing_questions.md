# Failing benchmark questions (full list, per model)

Each row is a `code_vuln` question — *Does <file> contain a vulnerability? Which CWE?* — the model answered wrong. Generated from the committed verdicts + answer keys.


## opus


### hand-crafted — 6 failures  ({'MISS': 2, 'WRONG_CWE': 2, 'FALSE_POSITIVE': 2})

| file | truth | answered | type |
|---|---|---|---|
| CWE-190/2.c | CWE-190 | safe | MISS |
| CWE-476/3.c | CWE-476 | safe | MISS |
| CWE-476/1.c | CWE-476 | vuln:CWE-22 | WRONG_CWE |
| CWE-476/p_2.c | safe | vuln:CWE-22 | FALSE_POSITIVE |
| CWE-476/2.c | CWE-476 | vuln:CWE-22 | WRONG_CWE |
| CWE-476/p_1.c | safe | vuln:CWE-22 | FALSE_POSITIVE |

### real-world — 5 failures  ({'MISS': 2, 'FALSE_POSITIVE': 1, 'WRONG_CWE': 2})

| file | truth | answered | type |
|---|---|---|---|
| CVE-2023-2908/vuln.c | CWE-476 | safe | MISS |
| CVE-2023-1452/patch.c | safe | vuln:CWE-787 | FALSE_POSITIVE |
| CVE-2023-1452/vuln.c | CWE-787 | vuln:CWE-476 | WRONG_CWE |
| CVE-2023-42754/vuln.c | CWE-476 | safe | MISS |
| CVE-2023-42753/vuln.c | CWE-190 | vuln:CWE-787 | WRONG_CWE |

## sonnet


### hand-crafted — 14 failures  ({'FALSE_POSITIVE': 9, 'MISS': 1, 'WRONG_CWE': 4})

| file | truth | answered | type |
|---|---|---|---|
| CWE-77/p_3.c | safe | vuln:CWE-77 | FALSE_POSITIVE |
| CWE-190/2.c | CWE-190 | safe | MISS |
| CWE-416/p_3.c | safe | vuln:CWE-476 | FALSE_POSITIVE |
| CWE-476/3.c | CWE-476 | vuln:CWE-787 | WRONG_CWE |
| CWE-476/1.c | CWE-476 | vuln:CWE-22 | WRONG_CWE |
| CWE-787/p_3.c | safe | vuln:CWE-787 | FALSE_POSITIVE |
| CWE-416/3.c | CWE-416 | vuln:CWE-476 | WRONG_CWE |
| CWE-190/p_1.c | safe | vuln:CWE-476 | FALSE_POSITIVE |
| CWE-89/p_3.py | safe | vuln:CWE-89 | FALSE_POSITIVE |
| CWE-476/p_2.c | safe | vuln:CWE-22 | FALSE_POSITIVE |
| CWE-476/2.c | CWE-476 | vuln:CWE-22 | WRONG_CWE |
| CWE-476/p_1.c | safe | vuln:CWE-22 | FALSE_POSITIVE |
| CWE-22/p_2.c | safe | vuln:CWE-476 | FALSE_POSITIVE |
| CWE-476/p_3.c | safe | vuln:CWE-787 | FALSE_POSITIVE |

### real-world — 2 failures  ({'MISS': 1, 'WRONG_CWE': 1})

| file | truth | answered | type |
|---|---|---|---|
| CVE-2023-2908/vuln.c | CWE-476 | safe | MISS |
| CVE-2023-42753/vuln.c | CWE-190 | vuln:CWE-787 | WRONG_CWE |

## haiku


### hand-crafted — 21 failures  ({'FALSE_POSITIVE': 10, 'MISS': 6, 'WRONG_CWE': 5})

| file | truth | answered | type |
|---|---|---|---|
| CWE-77/p_3.c | safe | vuln:CWE-787 | FALSE_POSITIVE |
| CWE-190/2.c | CWE-190 | safe | MISS |
| CWE-416/p_3.c | safe | vuln:CWE-787 | FALSE_POSITIVE |
| CWE-476/3.c | CWE-476 | vuln:CWE-787 | WRONG_CWE |
| CWE-476/1.c | CWE-476 | vuln:CWE-22 | WRONG_CWE |
| CWE-787/p_3.c | safe | vuln:CWE-787 | FALSE_POSITIVE |
| CWE-190/p_3.c | safe | vuln:CWE-476 | FALSE_POSITIVE |
| CWE-22/2.c | CWE-22 | safe | MISS |
| CWE-416/3.c | CWE-416 | vuln:CWE-787 | WRONG_CWE |
| CWE-190/p_1.c | safe | vuln:CWE-787 | FALSE_POSITIVE |
| CWE-787/2.c | CWE-787 | safe | MISS |
| CWE-190/1.c | CWE-190 | vuln:CWE-416 | WRONG_CWE |
| CWE-89/p_3.py | safe | vuln:CWE-89 | FALSE_POSITIVE |
| CWE-190/3.c | CWE-190 | vuln:CWE-476 | WRONG_CWE |
| CWE-77/p_2.c | safe | vuln:CWE-77 | FALSE_POSITIVE |
| CWE-77/p_1.c | safe | vuln:CWE-77 | FALSE_POSITIVE |
| CWE-22/1.c | CWE-22 | safe | MISS |
| CWE-79/3.py | CWE-79 | safe | MISS |
| CWE-476/p_1.c | safe | vuln:CWE-22 | FALSE_POSITIVE |
| CWE-79/1.py | CWE-79 | safe | MISS |
| CWE-476/p_3.c | safe | vuln:CWE-787 | FALSE_POSITIVE |

### real-world — 17 failures  ({'MISS': 12, 'WRONG_CWE': 2, 'FALSE_POSITIVE': 3})

| file | truth | answered | type |
|---|---|---|---|
| CVE-2023-26966/vuln.c | CWE-787 | safe | MISS |
| CVE-2023-2908/vuln.c | CWE-476 | safe | MISS |
| CVE-2023-23144/vuln.c | CWE-190 | safe | MISS |
| CVE-2023-3012/vuln.c | CWE-476 | vuln:CWE-190 | WRONG_CWE |
| CVE-2023-45871/vuln.c | CWE-787 | safe | MISS |
| CVE-2023-27585/vuln.c | CWE-787 | vuln:CWE-190 | WRONG_CWE |
| CVE-2023-1452/patch.c | safe | vuln:CWE-787 | FALSE_POSITIVE |
| CVE-2023-1452/vuln.c | CWE-787 | safe | MISS |
| CVE-2023-45863/vuln.c | CWE-787 | safe | MISS |
| CVE-2023-40745/vuln.c | CWE-190 | safe | MISS |
| CVE-2023-40283/vuln.c | CWE-416 | safe | MISS |
| CVE-2023-42754/vuln.c | CWE-476 | safe | MISS |
| CVE-2023-27585/patch.c | safe | vuln:CWE-190 | FALSE_POSITIVE |
| CVE-2023-42753/vuln.c | CWE-190 | safe | MISS |
| CVE-2023-41175/vuln.c | CWE-190 | safe | MISS |
| CVE-2023-3316/vuln.c | CWE-476 | safe | MISS |
| CVE-2023-3012/patch.c | safe | vuln:CWE-190 | FALSE_POSITIVE |
