# How the 1-minute check works

The check is part of the Oregon guide only. The Utah guide has no check yet ([decisions/0013-utah-section.md](decisions/0013-utah-section.md)).

The check lives in [`src/pages/check.html`](../src/pages/check.html) and [`site/assets/js/checker.js`](../site/assets/js/checker.js). This page describes every input, every result, and the claim behind each line, so anyone can audit it without reading code.

## Promises

- **Nothing leaves the device.** Answers stay in page memory. Nothing is written to storage. The Content Security Policy sets `connect-src 'none'` and `form-action 'none'`, so the browser blocks any network request. `tools/browser_check.py` confirms no storage keys and no outside requests after a full run.
- **No immigration questions.** `tools/check_structure.py` fails the build if any form label mentions immigration or citizenship.
- **No decisions.** Results say "may" and "likely." Every result ends with "Only OHP decides. This check is not a decision."
- **No dead ends.** Every result names a next step and a link.

## Steps

| Step | Question | Answers |
|---|---|---|
| 1 | How old are you? | 18 or younger; 19 to 64; 65 or older |
| 2 | Do any of these fit you? (reasons) | 16 choices in 4 groups, plus "None of these fit me" |
| 3 | Do any of these fit you? (ways to meet the rules, for the month before you apply) | $580 household income; school at least half-time; 80 hours of activities; "None of these fit me yet" |

"None" boxes clear the other boxes in their step, and the other boxes clear "None." Each step needs at least one answer; otherwise a plain error appears and focus moves to the first choice. "Back" keeps answers. There is no time limit.

## Results

Checked in this order:

| Condition | Heading shown | Claim |
|---|---|---|
| Age is not 19 to 64 | The new rules do not apply to your age group. | C-WHO-AGE |
| Picked Medicare or "applying because of a disability" | The new rules likely do not apply to you. | C-NA-MEDICARE, C-NA-PROGRAM |
| Picked any other reason | You may not have to meet the new rules. | See table below |
| Picked only ways to meet the rules | You may already meet the new rules. | C-MEET-INCOME, C-MEET-SCHOOL, C-MEET-HOURS |
| Picked nothing in steps 2 and 3 | The new rules may apply to you. | C-LOOKBACK-APP, C-FIND-ACTIVITIES |

When reasons and ways to meet the rules are both picked, the result shows both lists.

## What each reason says

| Value | Label | How OHP checks it, as shown | Claim |
|---|---|---|---|
| pregnant | Pregnant now or in the last 12 months | Tell OHP. No proof is needed. | C-EX-PREG |
| child | Care for a child 13 or younger | Tell OHP how you are related. From 2028, OHP may ask for a calendar or schedule. | C-EX-CHILD |
| caregiver | Care for someone with a disability or serious health condition | Tell OHP. If you do not live with them and are not related, you need at least 80 hours of care a month. | C-EX-CARE |
| health | Serious or disabling health condition | Tell OHP. In 2027, no doctor's note. | C-EX-HEALTH, C-HEALTH-2027 |
| ssi | Get SSI or SSDI | Tell OHP. OHA counts this as a qualifying health condition. | C-EX-SSI |
| treatment | Drug or alcohol treatment now or in the last 5 years | Tell OHP. From 2028, OHP may ask for treatment dates. | C-EX-SUD |
| medicare | Have Medicare | The rules do not apply. OHP can usually check this itself. | C-NA-MEDICARE |
| disability_ohp | Applying for OHP because of a disability | The rules do not apply to OHP programs based on disability. | C-NA-PROGRAM |
| snap | Get SNAP and meet SNAP work rules | OHP checks this. Being excused from SNAP work rules is not enough. | C-EX-SNAP |
| tanf | Get TANF and meet TANF work rules | OHP checks this. | C-EX-TANF |
| aian | American Indian or Alaska Native | Tell OHP. No proof is needed. | C-EX-AIAN |
| foster | In foster care at 18 and under 26 | OHP checks this. | C-EX-FOSTER |
| veteran | Veteran with a 100% VA disability rating | Tell OHP. If asked, send the VA award letter. | C-EX-VET |
| jail | Out of jail or prison in the last 4 months | Tell OHP. No proof is needed. | C-EX-JAIL |
| hospital | At least one night as a patient in a hospital, nursing, or behavioral health facility | Tell OHP. | C-EX-HOSP |
| travel | Away 7 or more days in a month for medical care | Tell OHP. | C-EX-TRAVEL |

County-based reasons (disaster declarations, high unemployment) are not asked, because OHP checks them and applicants cannot easily know them. The reasons page lists them.

## What the check does not ask, on purpose

- Immigration or citizenship status.
- Names, birth dates, addresses, case numbers, or income amounts.
- Health diagnoses. It asks only whether a serious or disabling condition fits.

## Changing the check

1. Change the wording in `checker.js` and the labels in `src/pages/check.html`.
2. Update or add the matching claim in `data/claims.json`, and this table.
3. Run `python3 tools/build.py` and `python3 tools/browser_check.py`. The browser check runs every result path.
