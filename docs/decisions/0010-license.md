# 0010. License

- Status: Accepted
- Date: 2026-11-02

## Context

Without a license, nobody else has permission to reuse the code or text, which limits how many people the project can help. Most of this project is words: the page text, the fact log, the source registry, and the docs. A small part is code: the build and check tools, three scripts, one stylesheet, and the workflows.

Creative Commons recommends against using its licenses for software and says they may be used for software documentation ([Creative Commons FAQ](https://creativecommons.org/faq/), checked Nov. 2, 2026). The MIT License is written for software.

## Decision

The maintainer chose two licenses on Nov. 2, 2026.

| What | License | SPDX ID | File |
|---|---|---|---|
| Words and data: every file not listed below | Creative Commons Attribution 4.0 International | `CC-BY-4.0` | [LICENSE](../../LICENSE) |
| Code: `tools/`, `site/assets/js/`, `site/assets/css/`, and `.github/workflows/` | MIT License | `MIT` | [LICENSE-CODE](../../LICENSE-CODE) |
| Logo: `site/assets/img/logo.svg` | None (all rights reserved) | | |

- The copyright notices, in `LICENSE-CODE` and the README, name The Stasis Project, not a person.
- The license texts are unchanged copies of the templates in GitHub's [choosealicense.com repository](https://github.com/github/choosealicense.com) (commit `b054bc8`, Oct. 30, 2026), which GitHub uses to detect licenses. The only edit is the filled-in MIT copyright line.
- The generated pages in `site/` count as words, even though the build adds shared markup to them.
- The logo was left out of both licenses by default when they were added, so that copies cannot look like the original site. The maintainer can add it to CC BY 4.0 later.

## Options considered

| Option | Why it was not chosen |
|---|---|
| MIT for everything | Simpler, but written for software, and it does not require reusers to say what they changed. |
| No conditions (a public domain dedication such as CC0) | Copies would not have to credit the project or link back to it, so out-of-date copies could not be traced to the current site. |
| A NonCommercial license | Hospitals and many clinics are businesses, so it could block the reusers the project most wants. |

## Consequences

- Anyone may copy, share, translate, and adapt the words if they credit the project, link to the license, and say what they changed (CC BY 4.0, section 3(a)).
- The README supplies the site's address with the material. Reusers must keep a link to the material "to the extent reasonably practicable" (section 3(a)(1)(A)(v)), which helps readers of a copy find the current rules.
- The pages on the site do not show a license notice yet, so a visitor who never opens the repository may not know the words are reusable. See [roadmap.md](../roadmap.md).
- Anyone may reuse the code if they keep the copyright and license notice (MIT).
- The CC BY 4.0 grant is irrevocable (section 2(a)(1)). If the project changes licenses later, copies already shared stay under CC BY 4.0.
- Neither license gives trademark rights (CC BY 4.0, section 2(b)(2)), and CC BY 4.0 does not let anyone imply that the project endorses their copy (section 2(a)(6)).
- Contributions are accepted under the same licenses ([CONTRIBUTING.md](../../CONTRIBUTING.md)).
