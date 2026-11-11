# How the 1-minute check works

Each guide has its own check, and both work the same way ([decisions/0013-utah-section.md](decisions/0013-utah-section.md)).

| | Oregon | Utah |
|---|---|---|
| Page | [`src/pages/check.html`](../src/pages/check.html) | [`src/pages/utah-check.html`](../src/pages/utah-check.html) |
| Words, links, and lists | [`checker-oregon.js`](../site/assets/js/checker-oregon.js) | [`checker-utah.js`](../site/assets/js/checker-utah.js) |
| The script that runs it | [`checker.js`](../site/assets/js/checker.js) | the same file |

This page describes every input, every result, and the claim behind each line, so anyone can audit either check without reading code. The promises, steps, and result order below hold for both. The Oregon tables come first, then [the Utah tables](#the-utah-check).

## Promises

- **Nothing leaves the device.** Answers stay in page memory. Nothing is written to storage. The Content Security Policy sets `connect-src 'none'` and `form-action 'none'`, so the browser blocks any network request. `tools/browser_check.py` confirms no storage keys and no outside requests after a full run.
- **No immigration questions.** `tools/check_structure.py` fails the build if any form label mentions immigration or citizenship.
- **No decisions.** Results say "may" and "likely." Every result ends with "Only OHP decides. This check is not a decision." (Utah: "Only the state decides.")
- **One state at a time.** `tools/browser_check.py` fails if a result in one check names the other state's program or links to the other guide.
- **No dead ends.** Every result names a next step and a link.

## Steps

| Step | Question | Answers |
|---|---|---|
| 1 | How old are you? | 18 or younger; 19 to 64; 65 or older |
| 2 | Do any of these fit you? (reasons) | Oregon: 16 choices in 4 groups. Utah: 13 choices in 4 groups. Plus "None of these fit me" |
| 3 | Do any of these fit you? (ways to meet the rules, for the month before you apply) | $580 a month (Oregon: household income; Utah: "I earn," as Utah words it); school at least half-time; 80 hours of activities; "None of these fit me yet" |

"None" boxes clear the other boxes in their step, and the other boxes clear "None." Each step needs at least one answer; otherwise a plain error appears and focus moves to the first choice. "Back" keeps answers. There is no time limit.

## Results

Checked in this order. The headings are the same in both checks. The claims in this table are Oregon's; Utah's are in [the Utah tables](#the-utah-check).

| Condition | Heading shown | Claim |
|---|---|---|
| Age is not 19 to 64 | The new rules do not apply to your age group. | C-WHO-AGE |
| Picked Medicare or "applying because of a disability" | The new rules likely do not apply to you. | C-NA-MEDICARE, C-NA-PROGRAM |
| Picked any other reason | You may not have to meet the new rules. | See table below |
| Picked only ways to meet the rules | You may already meet the new rules. | C-MEET-INCOME, C-MEET-SCHOOL, C-MEET-HOURS |
| Picked nothing in steps 2 and 3 | The new rules may apply to you. | C-LOOKBACK-APP, C-FIND-ACTIVITIES |

When reasons and ways to meet the rules are both picked, the result shows both lists.

## What each reason says (Oregon)

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

## The Utah check

Built on Nov. 10, 2026 from the lists on Utah's pages (U01, U04, U05) and the claims already in the fact log. Utah checks its own records first for every reason, so a reason has a "how" line only where Utah says something specific.

### Results (Utah)

| Condition | Heading shown | What it says | Claim |
|---|---|---|---|
| Age is not 19 to 64 | The new rules do not apply to your age group. | The rules are for adults ages 19 to 64. You can still apply for Utah Medicaid. | U-NA-AGE |
| Picked Medicare or SSI | The new rules likely do not apply to you. | The list of what was picked, then "What to do" | U-NA-MEDICARE, U-NA-GROUP |
| Picked any other reason | You may not have to meet the new rules. | The list of what was picked, then "What to do" | See table below |
| Picked only ways to meet the rules | You may already meet the new rules. | The state checks its records first. If it needs more, you may need to send a form within 30 days, or you could lose your coverage. | U-DATA-FIRST, U-VERIFY-30 |
| Picked nothing in steps 2 and 3 | The new rules may apply to you. | You can still apply. The state looks at the month before you apply. | U-LOOKBACK-APP |

"What to do" after a reason: the state checks records it already has first, and if it confirms the reason, nothing more is needed (U-DATA-FIRST). If it cannot, the person can report the reason in myCase, on the application, or on form 742 (U-TELL-HOW). Utah's page names form 742 but does not link to it, so the check gives the DWS phone number (U-742-NOLINK).

### What each reason says (Utah)

| Value | Label | What the check adds | Claim |
|---|---|---|---|
| pregnant | Pregnant, or getting Medicaid for the months after a birth | Nothing | U-EX-PREG |
| care | Parent, guardian, or caregiver for a child 13 or younger, or for a person with a disability | Nothing | U-EX-CARE |
| health | Blind, or a disability, a mental health condition, a substance use disorder, or a condition that makes daily tasks hard | Utah Medicaid checks its own health records first. If that does not confirm it, you fill out a short form. | U-EX-FRAIL, U-FRAIL-CLAIMS, U-FRAIL-SELF |
| treatment | In a drug or alcohol treatment and rehabilitation program | Utah Medicaid checks its own health records first. | U-EX-SUD, U-FRAIL-PATHS |
| medicare | Medicare Part A or Part B | Utah says the rules do not apply. | U-NA-MEDICARE |
| ssi | Get SSI | Utah says the rules do not apply to people in some other Medicaid groups, like people who get SSI. | U-NA-GROUP |
| snap | Have to meet work rules for SNAP or TANF | Nothing | U-EX-SNAP |
| aian | American Indian or Alaska Native | The state must verify your status. Utah's letter says to send proof by Jan. 1, 2027. | U-EX-AIAN, U-AIAN-PROOF |
| foster | In foster care, or were | Some Utah pages say this means the Former Foster Care program. Ask the state which one fits you. | U-EX-FOSTER |
| veteran | Veteran with a 100% disability | Nothing | U-EX-VET |
| jail | Out of jail or prison in the last 90 days | Nothing | U-EX-JAIL |
| hospital | A patient in a hospital, or lived in a nursing home or another care facility | Utah calls this a short-term hardship. You must ask the state for this exception. | U-HARD-HOSP |
| travel | Had to travel outside your community for medical care for you or a dependent | The same line as hospital | U-HARD-TRAVEL |

### Ways to meet the rules (Utah)

| Value | Label | What the check adds | Claim |
|---|---|---|---|
| income | You earn at least $580 a month | Utah's pages do not say whose income counts. The federal rule counts your household's. Ask the state how it counts yours. | U-MEET-INCOME, U-INCOME-WHOSE |
| school | You go to school at least half-time | Your school decides what counts as half-time. | U-MEET-SCHOOL, U-SCHOOL-WHO |
| hours | 80 hours a month on work, job training, volunteering, or school, added together | Write down your hours. You can print an hours log. | U-MEET-HOURS |

### What the Utah check leaves out, and why

- **County reasons** (a federal emergency or disaster declaration, or high unemployment). The state checks these, and applicants cannot easily know them. The Utah reasons page lists them.
- **"In jail or prison now."** A person using the check is asked only about getting out in the last 90 days.
- **Other Medicaid groups besides SSI,** such as parents with low income. Utah's pages name the group but give no test a person can apply to themselves. The Utah reasons page lists it.
- **What form 742 and the medically frail screener ask.** Utah has not posted them. The check says to ask DWS for form 742. Checkpoint 2027-01-15 covers updating it.

## Changing a check

1. Change the wording in that state's file (`checker-oregon.js` or `checker-utah.js`) and the labels in its page (`src/pages/check.html` or `src/pages/utah-check.html`). Change `checker.js` only to change how both checks work.
2. Update or add the matching claim in `data/claims.json`, and the tables on this page.
3. Run `python3 tools/build.py` and `python3 tools/browser_check.py`. The browser check runs every result path in both checks and picks every choice once.
