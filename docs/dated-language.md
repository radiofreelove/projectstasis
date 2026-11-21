# Dated language

Wording on this site whose truth depends on the date. Each entry gives the exact wording, where it is, the day it stops reading as true, and what to do then.

This is a list, not a change. No page wording and no claim changed when it was written. Every entry is tied to a checkpoint in [data/review.json](../data/review.json), so `tools/check_review_dates.py` and the weekly check raise it when its date passes.

- **Swept on:** Nov. 15, 2026, at version 0.3.9 beta.
- **Swept:** every page in `src/pages`, every statement in `data/claims.json`, and every checkpoint in `data/review.json`.
- **Not swept:** claim notes, the docs, and the text inside the tools. Where a check script repeats a dated sentence, the entry names the file.
- **Pages** are named by their file in `src/pages`. A claim id is given where the wording carries one.

## The actions

| Action | What it means |
|---|---|
| Comes down | Delete the wording. Nothing replaces it. |
| Flips to past tense | The fact stays. Only the tense changes. The entry names the new wording. |
| Replaced | New wording takes its place. The entry names it, or says what must be read first. |
| Source check first | Do not reword from the calendar alone. Re-read the named source, then decide. |

A date passing is never proof of what a state did. Where the new wording depends on what a state now says, the action is "Source check first".

## Keeping this list current

- When you add wording with a date in it, or wording like "not yet", "right now", "still", "as of", or "starting", add an entry here and a checkpoint in `data/review.json`.
- When you do the work in an entry, remove the entry in the same change.
- Re-sweep when a guide is added.

## 1. Dec. 11, 2026: the date states were asked to tell the federal agency

Checkpoint: `2026-12-11` (it was already in the file).

| # | Exact wording | Where | Expires | Action |
|---|---|---|---|---|
| 1.1 | "As of Nov. 14, 2026, OHA's pages about the new rules did not say what Oregon will choose." | `oregon/index.html`, `oregon/rules.html`, `oregon/denied.html`. Claim C-HH-STATE | Dec. 11, 2026, and each time the pages are searched again | Source check first. If nothing changed, replace only the date in "As of". If Oregon has chosen, replace the sentence with what OHA says, and cite that source. |
| 1.2 | "As of Nov. 14, 2026, Utah's pages about the new rules did not say what Utah will choose." | `utah/utah.html`, `utah/utah-rules.html`, `utah/utah-denied.html`. Claim U-HH-STATE | Same | Same, from Utah's pages. |
| 1.3 | "On Nov. 17, 2026, HCA announced Washington will pursue delayed enforcement of the work rules. Through June 30, 2027, people in Apple Health for Adults will not lose or be denied coverage for not meeting the work rules." | `washington/washington.html`, `washington/washington-rules.html`, `washington/washington-denied.html`. Claim WA-HH-05 (updated Nov. 21, 2026 from WA27) | Dec. 11, 2026 (confirm CMS approval), then June 30, 2027 | Source check first (WA27, WA01, WA03, WA22, medicaid.gov). Confirm CMS approval; comes down or flips to past tense on June 30, 2027 (group 6). |
| 1.4 | "A state that wants it from Jan. 1, 2027 was asked to tell the agency by Dec. 11, 2026." | `oregon/rules.html`, `utah/utah-rules.html`, `washington/washington-rules.html`. Claims C-HH-HOW, U-HH-HOW, WA-HH-04 | Does not expire on Dec. 11, 2026. It is already in the past tense and stays true. It comes down with the rest of the hold harmless wording (group 6). | No change on Dec. 11, 2026. |
| 1.5 | "Oral argument is set for Jan. 12, 2027. As of Nov. 21, 2026, no court order has changed these rules." | `oregon/index.html`, `oregon/rules.html` (C-OR-OZ); `washington/washington.html`, `washington/washington-rules.html` (WA-OR-OZ) | Jan. 12, 2027 (checkpoint `2027-01-12`) | Source check first (S44, S45, WA14, and D. Or. docket `6:26-cv-02435-AA`). Update with any ruling or new schedule and move the "As of" date. |

## 2. Dec. 10, 2026: the court ruling "as of" lines

Checkpoints: `2026-12-10` and `2027-04-29` (both were already in the file).

| # | Exact wording | Where | Expires | Action |
|---|---|---|---|---|
| 2.1 | "As of Nov. 10, 2026, OHA's pages had not said what changes." | `oregon/health.html`, `oregon/reasons.html`. Claim C-COURT | Dec. 10, 2026, and each re-check after | Source check first (S01, S03, S07, S24, and the docket, S40). If nothing changed, replace only the date. If OHA has spoken, replace the sentence with what OHA says. |
| 2.2 | "As of Nov. 10, 2026, Utah's pages had not said what changes." | `utah/utah-health.html`, `utah/utah-reasons.html`. Claim U-COURT | Same | Same, from U01 to U04. |

## 3. Jan. 1, 2027: the rules and the checking start

Checkpoints: the first `2026-12-31` entry (already in the file) covers 3.1 to 3.3. The second `2026-12-31` entry, added with this list, covers 3.4 to 3.17.

Each "flips" action below assumes the start date has not moved. Confirm that from each state's page before rewording: S07 for Oregon, U02 for Utah, WA01 for Washington.

| # | Exact wording | Where | Expires | Action |
|---|---|---|---|---|
| 3.1 | "Applying for OHP? New rules start Jan. 1, 2027." and the same headline for Utah Medicaid and Apple Health | Title and headline of `oregon/index.html`, `utah/utah.html`, `washington/washington.html` | Jan. 1, 2027 | Flips to past tense: "New rules started Jan. 1, 2027." |
| 3.2 | "Read this before Jan. 1, 2027." and the "Through Dec. 31, 2026" and "Before Jan. 1, 2027" sentences about 3 months of past bills | The 9 elements marked `data-show-until="2026-12-31"` in `oregon/index.html`, `oregon/bills.html`, `utah/utah.html`, `utah/utah-bills.html`, `washington/washington.html`, `washington/washington-bills.html`. Claims C-RETRO-NOW, U-RETRO-NOW, WA-BILL-01 | Dec. 31, 2026. The browser hides them after that day; readers without JavaScript still see them. | Comes down. |
| 3.3 | "Utah's letter says to send proof of your status by Jan. 1, 2027." and "Utah's letter says to send proof by Jan. 1, 2027." | `utah/utah-reasons.html` (2 places), and `site/assets/js/checker-utah.js`. Claim U-AIAN-PROOF | Jan. 1, 2027 | Source check first (U28, U02): find what Utah says to people who have not sent proof. Then replace. |
| 3.4 | "Starts: Jan. 1, 2027." | `oregon/rules.html` (C-START), `utah/utah-rules.html` (U-START), `washington/washington-rules.html` (WA-HOME-02) | Jan. 1, 2027 | Flips to past tense: "Started: Jan. 1, 2027." |
| 3.5 | "What's new: Starting Jan. 1, 2027, many adults ages 19 to 64 must meet new work or activity rules to get OHP." Utah: "Starting Jan. 1, 2027, some adults ages 19 to 64 must meet new work or activity rules to get Utah Medicaid." Washington: "New federal work rules for Apple Health for Adults start Jan. 1, 2027." | `oregon/index.html` (C-START), `utah/utah.html` (U-START), `washington/washington.html` and `shared/about.html` (WA-HOME-02) | Jan. 1, 2027 | Flips to past tense: "Since Jan. 1, 2027, ... must meet", and "started Jan. 1, 2027" for Washington. |
| 3.6 | "The new rules that start Jan. 1, 2027." Washington: "They start Jan. 1, 2027." | `oregon/words.html` (C-START), `utah/utah-words.html` (U-START), `washington/washington-words.html` (WA-HOME-02) | Jan. 1, 2027 | Flips to past tense: "that started Jan. 1, 2027". |
| 3.7 | "Big changes to OHP start Jan. 1, 2027." and the same line for Utah Medicaid and Apple Health | `shared/about.html`, the purpose line of each guide's About page. No claim. | Jan. 1, 2027 | Flips to past tense: "started Jan. 1, 2027". |
| 3.8 | "Still starting: The work or activity rules still start Jan. 1, 2027. The checking starts then too." and "The rules still start Jan. 1, 2027." | Home and rules page of each guide. Claims C-HH-START, U-HH-START, WA-HH-01 | Jan. 1, 2027 | Replaced: "The work or activity rules started Jan. 1, 2027. The checking started then too." (Washington: "The work rules".) Drop the "Still starting" label. The whole box comes down in group 6. |
| 3.9 | "If you apply: On or after Jan. 1, 2027, you must meet the rules to get coverage." | `utah/utah-rules.html`. Claim U-START-APP | Jan. 1, 2027 | Replaced: "If you apply: You must meet the rules to get coverage." Keep the date only if Utah's page still gives it. |
| 3.10 | "More reviews: Starting Jan. 1, 2027, adults in these 2 programs get a review every 6 months, not every 12." and "Starting Jan. 1, 2027, adults in Adult Expansion Medicaid and TAM get one every 6 months." | `utah/utah-rules.html`, `utah/utah-words.html`. Claim U-SIX-MONTH | Jan. 1, 2027 | Flips to past tense: "Since Jan. 1, 2027". |
| 3.11 | "Starting Jan. 1, 2027, that window gets shorter for most adults." / "that window is shorter" / "On Jan. 1, 2027, that window gets shorter." / "that time gets shorter." / "What changes: Coverage for past bills gets shorter on Jan. 1, 2027." | Description and purpose line of `oregon/bills.html`, `utah/utah-bills.html`, `washington/washington-bills.html`; `washington/washington.html`. Claim WA-HOME-04 where marked | Jan. 1, 2027 | Flips to past tense: "On Jan. 1, 2027, that window got shorter." |
| 3.12 | "Starting Jan. 1, 2027:" 1 month and 2 months of past bills; "From Jan. 1, 2027:"; "Who gets up to 2 months starting Jan. 1, 2027" | `oregon/index.html`, `oregon/bills.html` (C-RETRO-2027); `utah/utah.html`, `utah/utah-bills.html` (U-RETRO-2027); `washington/washington-bills.html` (WA-BILL-02) | Jan. 1, 2027 | Source check first (S01, U02, WA01), then flips: "Since Jan. 1, 2027". |
| 3.13 | "Open Card: Starting in January 2027, Healthier Oregon members move to OHP Open Card." | `oregon/immigration.html`. Claim C-HO-OPENCARD | Jan. 31, 2027 | Source check first (S01, S06): confirm the move happened and when. Then flips: "In January 2027, Healthier Oregon members moved to OHP Open Card." |
| 3.14 | "Starting Jan. 1, 2027, you can call Open Card at 800-562-4620 for help finding providers." | `oregon/immigration.html`. Claim C-OPENCARD-FIND | Jan. 1, 2027 | Source check first (S01): confirm the number. Then replaced: "You can call Open Card at 800-562-4620 for help finding providers." |
| 3.15 | "Until Jan. 1, 2027, the state rule says coverage comes back with no gap, if you are still eligible. A new version of the rule starts Jan. 1, 2027. It keeps the 90 days. It says you do not need a new application. It no longer says "with no gap."" | `washington/washington-denied.html`. Claim WA-DEN-01 | Jan. 1, 2027 | Source check first (WA16: confirm the new version took effect as written). Then replaced: drop the "Until Jan. 1, 2027" sentence and state the rule now in force, with "Before Jan. 1, 2027, the rule said coverage came back with no gap" kept only if it still helps a reader. |
| 3.16 | "It says you do not need to do anything yet." (the July 2026 letter) | `utah/utah-letter.html`. Claims U-LETTER-KEY, U-LETTER-GREEN | Jan. 1, 2027 | Replaced: say the letter was sent before the rules began, so a reader does not take "nothing yet" as true now. Suggested: "It said you did not need to do anything yet. The rules have started since then." |
| 3.17 | "HCA says there is nothing you need to do right now." | `washington/washington.html`, `washington/washington-rules.html`, `washington/washington-letter.html`, and `site/assets/js/checker-washington.js`. Claim WA-HOME-02 | When HCA changes the line; Jan. 15, 2027 at the latest | Source check first (WA01, WA22). The `2027-01-15` checkpoint already in the file owns this one. It is listed here because "right now" has no date of its own. |

## 4. January to March 2027: figures, forms, and letters with a date on them

Checkpoints: `2027-01-15` and `2027-03-01` (already in the file) cover 4.1 to 4.3. The `2027-01-31` entry, added with this list, covers 4.4 to 4.8.

| # | Exact wording | Where | Expires | Action |
|---|---|---|---|---|
| 4.1 | "The paper form is from May 2020. It does not ask about the new rules." | `oregon/apply.html`. Claim C-7210-NOQS | When OHA posts a new OHP 7210; checked Jan. 15, 2027 | Source check first (S10). |
| 4.2 | "The paper form we read is dated April 1, 2026. It does not ask about the new rules." | `utah/utah-apply.html`. Claim U-61MED-NOQS | When Utah posts a new 61MED; checked Jan. 15, 2027 | Source check first (U15). |
| 4.3 | "If you already have it: The rules start at your review, for renewals due in March 2027 or later." | `utah/utah-rules.html`. Claim U-START-MEMBER | March 1, 2027 | Source check first (U04, U13), then flips: "The rules started at reviews for renewals due in March 2027 or later." |
| 4.4 | "In January 2026, Utah said about 83,000 people were in the 2 programs the new rules cover." | `shared/about.html` (Utah). Claim U-UTAH-PEOPLE | Jan. 31, 2027: the figure is then a year old | Source check first (U11, U02): look for a newer count. Replace the month and the number together, or keep both as they are. |
| 4.5 | "OHA and ODHS told lawmakers that about 600,000 people on OHP could be subject to the new rules." | `shared/about.html` (Oregon). Claim C-OHP-PEOPLE. The page gives no date; the claim note gives Sept. 9, 2026. | Jan. 31, 2027: "could be" is a forecast from before the start | Source check first (S30, S07): look for a count from after the start. If there is none, keep the sentence and add its date. |
| 4.6 | "Letters Utah mailed in 2026" and "Utah mailed its 2026 letters about the work rules in English and Spanish." | `utah/utah-letter.html`, `utah/utah-help.html`. Claim U-LETTER-KEY | Jan. 31, 2027: the list is complete only for 2026 | Source check first (U02): look for letters mailed since. Add them, or keep the heading so it says the list is for 2026. |
| 4.7 | "Utah said it would send each affected member a letter by Oct. 1, 2026." | `utah/utah-immigration.html`. Claim U-IMM-LETTER | Oct. 1, 2026. It had passed before this list was written. | Source check first (U27, U02): find whether Utah says the letters went out. Then flips ("Utah sent") or stays as it is. |
| 4.8 | "Utah's pages do not yet say exactly what counts." | `utah/utah-rules.html`. Claim U-ACTIVITY-DEFS | No date of its own; true only until Utah posts definitions | Source check first (U03). Replaced with Utah's definitions when they exist. |

## 5. April and June 2027

Checkpoints: `2027-04-29` and `2027-06-15` (both were already in the file).

| # | Exact wording | Where | Expires | Action |
|---|---|---|---|---|
| 5.1 | "On Oct. 29, 2026, a federal court threw out part of a federal rule that narrowed this reason. Oregon was part of that case." | `oregon/health.html`, `oregon/reasons.html` (C-COURT); the two court notes on `washington/washington-reasons.html` and `washington/washington-health.html` (WA-RSN-15, WA-HLT-04) | April 29, 2027: the end of the court's six-month bar | Source check first (S28, S40, WA14). |
| 5.2 | "Utah's glossary says TAM ends June 30, 2027, and its members move to Adult Expansion Medicaid." | `utah/utah-words.html`. Claim U-W-TAM. Every Utah page that names TAM. | June 30, 2027 | Source check first (U08, U25, U26), then flips: "TAM ended June 30, 2027, and its members moved". |

## 6. June 30, 2027: the last day of a hold harmless period

Checkpoint: `2027-06-30` (it was already in the file). A state may pick a shorter time. If one does, these come down for that state on its own end date.

| # | Exact wording | Where | Expires | Action |
|---|---|---|---|---|
| 6.1 | "Update, Nov. 13, 2026: A new choice for states" and the whole box under it | `oregon/index.html`, `utah/utah.html`, `washington/washington.html` | June 30, 2027 | Comes down. |
| 6.2 | "What's new: The federal government gave each state a choice. Through June 30, 2027, a state may choose not to turn anyone down, and not to end anyone's coverage, only for not meeting the work or activity rules." (Washington: "the work rules") | Home, rules, and turned-down page of each guide. Claims C-HH-OPTION, U-HH-OPTION, WA-HH-02 | June 30, 2027 | Comes down from the home pages. On the rules and turned-down pages: comes down if the state did not use the period. If it did, source check first, then flips to past tense for people whose case dates from that time. |
| 6.3 | "The choice does not protect anyone from being turned down or losing coverage for other reasons, such as income." and "A state can still say no, or end coverage, for other reasons, such as income." | Rules and turned-down page of each guide. Claims C-HH-LIMIT, U-HH-LIMIT, WA-HH-03 | June 30, 2027 | Comes down with 6.2. |
| 6.4 | "A state has to ask the federal Medicaid agency and get its approval. The choice covers applications the state gets, and renewals the state starts, through June 30, 2027. A state may pick a shorter time." | Rules page of each guide. Claims C-HH-HOW, U-HH-HOW, WA-HH-04 | June 30, 2027 | Comes down with 6.2. |
| 6.5 | Entries 1.1 to 1.4 and 3.8, in whatever wording they then have | As listed there | June 30, 2027 | Comes down. |

## 7. Dec. 1, 2027: wording that names 2027 or 2028

Checkpoints: the first `2027-12-01` entry (already in the file) covers 7.1. The second, added with this list, covers 7.2 to 7.5.

| # | Exact wording | Where | Expires | Action |
|---|---|---|---|---|
| 7.1 | "In 2027: No doctor's note is needed." "Starting in 2028: OHP may ask for a statement from a health care provider." "Who can confirm a condition in 2028". "Starting in 2028: OHP may ask for proof of some reasons." | `oregon/health.html` (also its description), `oregon/reasons.html`. Claims C-HEALTH-2027, C-HEALTH-WHO, C-2028-PROOF | Dec. 31, 2027 | Source check first: replaced with OHA's guidance for 2028. |
| 7.2 | "Starting in 2028, OHP may ask for a calendar or schedule." | `oregon/reasons.html`. Claim C-EX-CHILD | Dec. 31, 2027 | Source check first (S02, S03), then replaced: "OHP may ask for a calendar or schedule." |
| 7.3 | "Starting in 2028, OHP may ask for a paper that shows your treatment dates." | `oregon/reasons.html`. Claim C-EX-SUD | Dec. 31, 2027 | Source check first (S03), then replaced: "OHP may ask for a paper that shows your treatment dates." |
| 7.4 | "Tell OHP. In 2027, you do not need a note from a doctor." | `site/assets/js/checker-oregon.js`, the result of the Oregon check. Claim C-HEALTH-2027 | Dec. 31, 2027 | Replaced in the same change as 7.1, and in `docs/checker-logic.md`. |
| 7.5 | "Shorter coverage: Coverage periods go from 12 months to 6 months. That starts at a person's first renewal in 2027." | `washington/washington.html`, `washington/washington-rules.html`. Claim WA-HOME-03 | Dec. 31, 2027: by then each person has had that renewal | Source check first (WA05), then replaced: "Coverage periods are 6 months." |

## 8. No date of its own

These read as true today and will age. Each is owned by a checkpoint that was already in the file, so no checkpoint was added.

| # | Exact wording | Where | Owned by | Action |
|---|---|---|---|---|
| 8.1 | "the new rules", "The new rules, in plain words", "What's new", and "New rules apply" | Every guide: page titles, descriptions, headings, and menus | The second `2027-12-01` checkpoint | Decide then whether "new" still fits a rule that is a year old. If not, replaced with "the work or activity rules" (Washington: "the work rules"), which every page already uses. |
| 8.2 | "This guide is new", with "A person has not yet read each one from start to finish." | `shared/about.html` (Utah and Washington), `shared/sources.html`. Claim U-NEW-GUIDE | `2026-11-24` (Utah), `2026-11-26` (Washington) | Comes down, or is replaced with a line that records the finished source review. |
| 8.3 | "What this page does not say yet", with "We will add it after that."; and "A person on this project has not yet read those rules from start to finish." | `washington/washington-health.html`, `washington/washington-denied.html` | `2026-11-26` | Comes down when the source review is done. |
| 8.4 | "One of them, Apple Health Expansion, was closed to new people as of December 2025." and "As of December 2025, it was closed to new people." | `washington/washington-immigration.html`. Claim WA-IMM-04 | `2026-12-09`, and the 30-day hand check in [maintenance.md](maintenance.md) | Source check first (WA23). Replace the month if HCA gives a newer one. If enrollment opens, the sentence comes down. |
| 8.5 | "Tested so far: Automated checks only. Testing with people who use assistive technology has not happened yet." | `shared/accessibility.html`. Claim C-A11Y-TESTED | No checkpoint. It changes when the testing happens, not on a date ([roadmap.md](roadmap.md)). | Replaced when the testing is done. |
| 8.6 | "We have found {{DOC_COUNT}} so far." (the build puts in the number; it was 22 for Oregon on Nov. 15, 2026) | `shared/about.html`, `utah/utah.html` | No checkpoint. The build counts the registry each time. | No action. |

## Wording inside `data/review.json`

The checkpoints are dated notes too. Two read as out of date on Nov. 15, 2026. They were left as they are, because a checkpoint is changed only when its work is done.

| # | Exact wording | Where | Why it is out of date | Action |
|---|---|---|---|---|
| 9.1 | "WA25 is still marked 'opened': false, and three drafting claims remain (WA-CHK-01, WA-IMM-04, WA-RSN-15)." | The `2026-11-26` checkpoint | Release 0.3.8 beta (Nov. 14, 2026) marked WA25 read in full and settled the three claims. | Replaced when that checkpoint is done or moved: drop the sentence, and drop the three claims from the reading order if nothing else is open on them. |
| 9.2 | "they had none on Nov. 10" and "none appeared through the Nov. 6 entries" | The `2026-12-10` checkpoint | True as history. Each re-check makes the dates older. | Replaced with the new dates when the checkpoint is moved forward. |

## Looked at and left out

These have a date in them and do not expire, because they state a past event in the past tense:

- "A federal rule called "public charge" changed on Sept. 18, 2026." and "Benefits you got before Sept. 18, 2026 will not count under the new process." (`oregon/immigration.html`, C-PUBLIC-CHARGE)
- "Since Oct. 1, 2026, Utah Medicaid is mostly for 4 groups of people." (`utah/utah-immigration.html`, U-IMM-OCT) and "From Oct. 1, 2026, fewer noncitizen adults can get federally funded Medicaid." (`washington/washington-immigration.html`, WA-IMM-01)
- "The Utah Medicaid guide was added on Nov. 10, 2026." and "The Apple Health guide was added on Nov. 12, 2026." (`shared/about.html`)
- "Mailed in April 2026." and "Mailed in July 2026." (`utah/utah-letter.html`, U-LETTER-KEY)
- "On Nov. 13, 2026, the federal government gave each state a choice." The date stays true; the sentences around it are in group 6.
