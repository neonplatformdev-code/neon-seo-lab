# NEON SEO Lab v1

Dependency-free static fixtures. Cloudflare Pages serves public/ from main, with no build command. Push to main deploys. No backend, CDN or tracker.

## Local checks

`python -B tools/validate.py`
`node --check public/assets/site.js`
Preview: `python -m http.server 8765 --bind 127.0.0.1 --directory public`.

## Independent expectations

- /perfect/: title, description, H1, self-canonical; no missing metadata findings.
- /missing-title/: only title removed; title_not_observed.
- /missing-description/: only description removed; description_not_observed.
- /noindex/: only robots noindex added; indexability_blocked, not actual absence from Google.
- /broken-html/: unfinished trailing comment, containing a textual robots fragment; SeoReportFailure unsupported_html, no successful report/evidence/findings. Browser display may look normal. Do not repair this comment.

Bodies are identical; canonicals are self-referential. No global noindex, robots.txt or sitemap is supplied. Those resources are not evaluated. A hosting fallback for unknown paths does not prove their existence. H1 is a fixture property, not a claimed SEO Report 565 feature. No crawl, JavaScript rendering or search-engine indexation check is claimed.

Public scenarios.json describes expectations, not results. ready_for_testing is not pass. Pin a reviewed local Git commit and use independent checks in tools/validate.py plus captured HTTP bytes. Check final URL, HTTP status, Content-Type/Encoding and SHA-256 before evaluating findings/evidence. Do not use the public JSON as the sole scoring authority. Cloudflare may transform bytes; hash the actual received response. The trusted caller must explicitly authorize https://lab.neonplatform.online. This repository does not execute NEON or automatically approve reports.
