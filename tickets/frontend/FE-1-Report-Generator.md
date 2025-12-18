# FE-1: Report Generator

**Role**: Frontend Engineer
**Context**: Generate a standalone HTML report for experiment results.

## Requirements
1. Use TailwindCSS v4 (via CDN or built-in styles).
2. Use ReactJS (via CDN) to render the dynamic parts of the report if needed, or just server-side render HTML with embedded React scripts.
3. Structure the report:
   - Summary of the Sweep.
   - Configuration details.
   - Results tables.
   - Charts (see FE-2).
4. The output should be a self-contained HTML file (or set of files) that can be viewed in a browser.

## Acceptance Criteria
- [ ] HTML template created.
- [ ] Tailwind v4 styling applied.
- [ ] Python renderer populates the template with JSON data from the experiment.

