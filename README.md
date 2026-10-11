# Junteng Liu — LJT-Homepage

Personal academic homepage based on a fork of [AcademicPages](https://github.com/academicpages/academicpages.github.io).

## Content scope

The site uses only personal information supplied in memory. The existing **About** (`/`) and **Publications** (`/publications/`) pages are the only published HTML content pages. The About page contains the biography, research interests, academic background, research internships, all six publications, scholarship, and contact information.

- `_pages/about.md`: personal profile and sections.
- `_data/publications.yml`: the six recorded publications, with authors, years, venues, authorship roles, and available code information.
- `_includes/publications-list.html`: renders that same complete list on **both** About and Publications.
- `_config.yml`: identity, contact profiles, project-site URL, and exclusions.
- `_data/navigation.yml`: links only to the two pages or sections of About.

No separate skills list, portrait, exact publication dates, paper URLs, or code repository URLs were supplied in memory, so none were invented. Research interests are not recast as unverified skills. The recorded “first-year” and “Present” descriptions are preserved rather than extrapolated. The personal GitHub link remains `Vicent0205`; `ejanadens` is only the authenticated repository owner and hosting account.

Unused template pages, posts, collections, sample downloads, and documentation are excluded from the generated site. The original theme source and license are retained.

## Build and validation

```sh
bundle install
bundle exec jekyll build --strict_front_matter
python3 scripts/validate_homepage.py
```

The validation checks that exactly the two intended HTML pages are generated, that all six publications appear on each, that the stored profile/contact facts are present, and that local links respect `/LJT-Homepage`.

## GitHub Pages

Configured project-site address: `https://ejanadens.github.io/LJT-Homepage/`.

The **Build and deploy homepage** workflow builds, validates, and uploads a Pages artifact. Deployment runs only when GitHub Pages is already enabled with **Settings → Pages → Source: GitHub Actions**. If Pages is disabled or inaccessible, the workflow reports that publishing has not occurred; a successful build alone is not evidence that the site is live. After enabling Pages, rerun the workflow to deploy.
