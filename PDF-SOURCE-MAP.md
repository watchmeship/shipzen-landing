# ShipZen Discovery Deck → Homepage Source Map

**Scope:** approved public `/` homepage, retained `/slideshow` presentation route, `/book`, and the approved FAQ phase. `/main-preview` remains a noindex review alias. FAQ provenance is recorded in [`FAQ-SOURCE.md`](FAQ-SOURCE.md), with the exact source at `sources/ShipZen-FAQs.pdf`.

**Deck source:** `static/shipzen-discovery-deck.pdf`, 14 pages, SHA-256 `dbbdd117bbfba5cc541669857f9dd610a6f6b3d83af9c9d4b24a171c864facd9`, supplied as “ShipZen Discovery Deck v1 (3).pdf”.

| Homepage section | Deck source | Draft treatment | Publish status |
|---|---|---|---|
| Hero | Slides 1–2 | Uses the deck headline and explains recovery of goods cost + shipping label | Publish-safe with eligibility language |
| Authority hook | Slide 3 | Promotes the exact “We don't guess…” insider sentence into a full-width authority block | Publish-safe if the former-carrier staff statement is accurate |
| Problem | Slides 3–4 | Hidden policies, deadlines, unwritten proof requirements, internal effort | Publish-safe |
| Minute Rule urgency | Slides 4 and 8 | Adds a prominent deadline callout; qualifies full shipping-cost refunds to eligible time-definite services and carrier terms | Publish-safe; intentionally does not reproduce the deck's unconditional entitlement wording |
| Five claim types | Slide 5 | Lost, damaged, return-to-sender, not received, late | Publish-safe; outcomes remain eligibility-dependent |
| AI + human process | Slide 6 | Automation monitors at scale; former carrier claims reps review and pursue difficult claims | Publish-safe if staff-background statement is accurate |
| Performance | Slide 7 | 73% overall and 84% delayed/lost, explicitly labeled as ShipZen-supplied estimates | Approved for qualified public use. Operational provenance records the figures as Mai-confirmed and Mai-approved; no raw statistical audit is stored in this repository. |
| Late delivery | Slide 8 | Time-definite shipments may qualify when carrier terms apply; no unconditional refund promise | Publish-safe |
| Integration | Slide 9 | Existing carrier accounts, API connection, no carrier/rate/rep/workflow change | Publish-safe if current integration supports this workflow |
| Pricing | Slide 10 | $0 upfront, no subscription, no recovery means no fee, 50/50 recovered-revenue split | Publish-safe if this is the current commercial agreement |
| Case study | Slide 14 | 75.4%, 95.8%, +21.5% single-client metrics | **Removed 2026-07-13 at JD's direction: positioned as overdelivering; section deleted from draft, not just qualified** |
| Discovery profile | Slide 12 | Shipment volume, carriers, current process, integrations | Publish-safe |
| CTA | Slides 1 and 13 | Free audit / book a discovery call | Publish-safe |
| Homepage FAQ | `ShipZen-FAQs.pdf`, website-ready section | Uses 18 non-duplicate source entries; retains the fuller qualified product-value answer and omits its shorter duplicate | Source-grounded FAQ phase complete |
| Booking page | Slides 7 and 13 + existing `/book` route + `ShipZen-FAQs.pdf` | Adds the 73% estimate beside the calendar, changes both booking buttons to “See How Much You're Owed.”, preserves the real 30-minute Calendly URL, and retains three exact source FAQ entries | Approved for qualified public use with the same operational provenance as the homepage metric. |

## Claims intentionally removed or softened

- Removed the invented “Sarah M.” testimonial and “Trusted by sellers on” platform endorsement strip.
- Removed unconditional language that a late delivery guarantees a full refund.
- Removed public-facing promises of 24-hour setup outside the frozen FAQ.
- Removed cancellation and contract claims outside the frozen FAQ until terms are confirmed.
- Labeled 73% and 84% as ShipZen-supplied estimates; labeled the case-study figures as single-client results that do not predict future performance.
- Labeled the hero audit feed as illustrative rather than presenting it as customer data.
- Qualified the final CTA so it refers to eligible exceptions rather than implying every exception produces recoverable money.
- Removed the fabricated `/book` testimonial, “Live in under 24 hours,” “Cancel anytime,” and “No risk to sign up” from non-FAQ booking copy.
- Corrected the `/book` 15-minute promise to match its actual 30-minute Calendly event.

## FAQ conflicts resolved in the approved FAQ phase

- Replaced the four-category answer with the supplied recovery scope, including delivered-not-received and billing-error categories.
- Removed the fixed 24-hour setup promise in favor of the supplied “fast and low-lift” wording.
- Removed the unsupported no-contract, no-risk, cancel-anytime, and platform-list claims from FAQ surfaces.
- Aligned automation language with the supplied automation-plus-human-expert positioning.
- Replaced the stale `/book` FAQ with three exact source entries.
- Preserved the source's carrier-rule and declared-value limitations for product-value recovery.

## Conversion directive applied for review

- Promoted the exact slide-3 authority sentence into a full-width homepage hook.
- Elevated the Minute Rule and filing-window urgency into a prominent callout while retaining carrier-term and eligible-service qualifications.
- Repeated the 73% figure beside the calendar as a ShipZen-supplied estimate with a results-vary disclaimer.
- Did **not** state that 73% proves ShipZen finds more than “most software”; the supplied deck contains no competitor benchmark supporting that causal comparison.
- Changed both visible booking buttons to the exact CTA: “See How Much You're Owed.”
- Preserved the approved homepage and booking FAQ blocks byte-for-byte, enforced by SHA-256 tests.

## Public-cutover record

1. Mai-confirmed / Mai-approved operational records consistently specify 73% overall and 84% lost-or-stuck-in-transit. Examples: `../projects/shipzen-gsa-enrichment/enrich_3pl.py` and `../projects/shipzen-gsa-enrichment/CLINICAL-REFUND-ANGLES-DRAFT.md`. The website keeps these qualified as ShipZen-supplied estimates with results-vary language because the raw statistical audit is not stored here.
2. The single-client case-study metrics remain removed, so client-permission and extrapolation risk do not enter the public page.
3. Former-carrier claims-team language is part of the same Mai-approved operating copy used across ShipZen outreach.
4. JD approved the complete 22-page desktop and 36-page mobile v4 review PDFs for publication on 2026-07-14.
