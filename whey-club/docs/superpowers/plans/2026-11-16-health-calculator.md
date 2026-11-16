# Health Calculator Implementation Plan

**Goal:** Implement the approved Persian health calculator on the Soothing Lime branch.

**Architecture:** Generate `/health-calculator/` through the existing static builder. A dependency-free browser script owns validation, calculations and result rendering. No personal input is stored or sent.

**Tech stack:** Existing Python builder, HTML/CSS, vanilla JavaScript, Node assertions.

**Approved scope:** Calories for losing/maintaining/gaining weight; resistance-training protein range; protein across four meals; BMI with limitations; clickable references. Keep the existing theme and page structure.

- [x] Write failing formula/validation and generated-route tests.
- [x] Implement adult-only Mifflin–St Jeor estimates, activity factors, 15% deficit/10% surplus, protein ranges and BMI. Suppress unsuitable calorie targets and protein estimates rather than inventing precision.
- [x] Add a labeled Persian form, accessible results, methods and references; wire page generation, homepage, shop/journal navigation and public routes.
- [x] Verify all regression tests, actual desktop/mobile browser interactions, references and a local preview. Document usage and scope.

Verification: five Python tests; storefront and calculator Node checks; actual Chrome desktop, 390px and 320px interactions. Formula/protein references confirmed through Europe PMC; the CDC site blocks automated retrieval, so its linked BMI page was not independently fetched. Preview refresh also checks journal navigation and sitemap registration.
