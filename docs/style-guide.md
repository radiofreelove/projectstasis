# Content style guide

The site is written for people applying for OHP, many of whom are stressed, short on time, reading on a phone, or reading in a second language. Write for them.

## The page pattern (Smart Brevity, adapted)

1. **Headline (h1):** a plain question or statement. "OHP sent me a letter. Now what?"
2. **Purpose line:** one sentence on what the page is for. Every page has one, so nobody wonders why it exists.
3. **The short version:** 3 to 5 bullets, each a bold label and one line. Someone who reads only this part should know what to do.
4. **Details:** short sections with plain headings. Extra detail goes in a `class="more"` wrapper so "Just the key points" mode can hide it.
5. **Next step:** a callout with a link.
6. **Sources:** added by the build from the page's metadata.

Inspired by Axios's Smart Brevity approach. No text from that book is used here.

## Words

- Plain word first, OHP's word second, the first time: "a reason you do not have to meet the rules (OHP calls this an exemption)." Then use the word OHP uses, so people recognize it on letters.
- On Utah pages, do the same with Utah's words: "the work or activity rules (Utah calls this the community engagement requirement)," "reasons (Utah calls these exclusions and exceptions)."
- One idea per sentence. Aim for 8 words per sentence or fewer on average.
- Literal language. No idioms, sayings, or jokes.
- "May" for anything OHP decides. Never "you are exempt," "you qualify," or "you will get."
- "You" for the reader. "OHP" for the program and its decisions. "OHA" and "ODHS" only when naming who publishes something.
- On Utah pages: "the state" for whoever decides or asks, "DWS" (spelled out the first time on a page) when the reader has to call, write to, or visit it, and "Utah Medicaid" for the program. Never "OHP" on a Utah page.
- Say "apply again," not "reapply." Say "turned down," then "denied" only when quoting.
- People first, and only describe people when it matters to the rule.

## Numbers and dates

- Digits for all numbers: 3 months, 80 hours, $580.
- Give a plain equivalent when it helps: "80 hours a month (about 20 hours a week)."
- Dates with the year, month abbreviated as in AP style: Jan. 1, 2027. Use a non-breaking space between the month and day in HTML (`Jan.&nbsp;1`).
- Phone numbers as 800-699-9075, wrapped in `<span class="nowrap">`.
- Never copy numbers that change often (income limits, office hours). Link to them.

## Punctuation and format

- Sentence-case headings.
- No em dashes or en dashes. Use a period, a colon, or parentheses.
- Straight quotes.
- No emoji.
- Bold for labels only, not for whole sentences.
- No all caps, no italics for long text, no underlines except links.

## Links

- Link text says where it goes: "Find a free community partner near you," not "click here."
- Mark PDFs with `<span class="tag">PDF</span>`.
- Never open a new window.
- Every outside address must be in `data/sources.json`; the build enforces this.

## Facts

- Every factual sentence carries `data-claim` with a claim ID from `data/claims.json`.
- The claim's sources must be in the page's `sources:` metadata.
- If a source is ambiguous, say less, link to the source, and log the ambiguity in [corrections.md](corrections.md).

## Reading level

Run `python3 tools/check_reading_level.py`. Target grade 6. Above grade 8 fails. Names of programs and conditions can push a page up; that is acceptable when the name is what people will see on their letters.
