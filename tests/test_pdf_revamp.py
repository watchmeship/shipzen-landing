import hashlib
import re
import unittest
from pathlib import Path

import landing_v2


FAQ_START = "<!-- FAQ -->"
FAQ_END = "<!-- CTA BANNER -->"
FAQ_SOURCE_PDF = Path(__file__).parents[1] / "sources" / "ShipZen-FAQs.pdf"
FAQ_SOURCE_SHA256 = "fc26e811f847407c1c91d8436ab3f4c346edaac69e5b4a0ee73de54e0dc31c3e"
APPROVED_HOME_FAQ_SHA256 = "94a91ec0429998c39824eb3eddcff773c85cec4ecccf64a80bfe2a2bb277b2de"
APPROVED_BOOK_FAQ_SHA256 = "f9a39e635983c777671b6de1a3f18ff30c0c95617b8d5179d3875b37c2b5432b"
WEBSITE_FAQ_QUESTIONS = (
    "What does ShipZen do?",
    "How is ShipZen different from basic claims software?",
    "Do we need to switch carriers?",
    "How long does setup take?",
    "What carriers do you support?",
    "What shipping issues can you recover for?",
    "Can ShipZen recover the product value too, or only the shipping cost?",
    "How far back can you audit?",
    "Does filing claims hurt our carrier relationship?",
    "What if we signed a late-delivery waiver?",
    "How much does ShipZen cost?",
    "How does the 50/50 split work?",
    "Do you take the refund before we receive it?",
    "How do we see what was recovered?",
    "Is our data secure?",
    "What does our team need to do after setup?",
    "What happens if a claim is denied?",
    "How do we get started?",
)


class PdfSourcedRevampTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        landing_v2.app.config.update(TESTING=True)
        cls.client = landing_v2.app.test_client()
        response = cls.client.get("/main-preview")
        assert response.status_code == 200
        cls.html = response.get_data(as_text=True)
        cls.lower_html = cls.html.lower()

        faq_start = cls.html.index(FAQ_START)
        faq_end = cls.html.index(FAQ_END, faq_start)
        cls.faq_block = cls.html[faq_start:faq_end]
        cls.non_faq_html = cls.html[:faq_start] + cls.html[faq_end:]
        cls.non_faq_lower = cls.non_faq_html.lower()

        book_response = cls.client.get("/book")
        assert book_response.status_code == 200
        cls.book_html = book_response.get_data(as_text=True)
        book_faq_start = cls.book_html.index('  <div class="faq-section">')
        book_faq_end = cls.book_html.index('  <div class="bottom-cta">', book_faq_start)
        cls.book_faq_block = cls.book_html[book_faq_start:book_faq_end]
        cls.book_non_faq_html = cls.book_html[:book_faq_start] + cls.book_html[book_faq_end:]

    def test_main_preview_identifies_the_pdf_sourced_revamp(self):
        self.assertIn('data-shipzen-revamp="discovery-deck-v1"', self.html)
        self.assertIn(
            "<h1>The shipping money carriers don't want you to know about.</h1>",
            self.html,
        )
        self.assertIn("cost of your goods", self.lower_html)
        self.assertIn("shipping label", self.lower_html)

    def test_page_covers_all_five_claim_categories_from_the_pdf(self):
        for claim_type in (
            "Lost Packages",
            "Damaged Goods",
            "Return to Sender",
            "Not Received",
            "Late Deliveries",
        ):
            with self.subTest(claim_type=claim_type):
                self.assertIn(claim_type, self.html)

    def test_page_explains_the_two_layer_ai_and_human_process(self):
        self.assertIn("The AI &amp; Human Advantage", self.html)
        self.assertIn("Layer 1: AI Automation", self.html)
        self.assertIn("Layer 2: Human Expertise", self.html)
        self.assertIn("former carrier", self.lower_html)
        self.assertIn("review", self.lower_html)

    def test_authority_hook_uses_the_discovery_deck_wording(self):
        self.assertIn(
            "We don't guess how to get a claim approved. We know, because we used to be the ones denying them.",
            self.non_faq_html,
        )
        self.assertNotIn("Built by people who know the internal playbook.", self.non_faq_html)

    def test_minute_rule_is_prominent_urgent_and_eligibility_qualified(self):
        self.assertIn('class="minute-rule-callout"', self.non_faq_html)
        self.assertIn("The Minute Rule", self.non_faq_html)
        self.assertIn("even by a single minute", self.non_faq_lower)
        self.assertIn("If you miss the deadline, the money is gone.", self.non_faq_html)
        self.assertIn("eligible time-definite service", self.non_faq_lower)
        self.assertIn("carrier terms", self.non_faq_lower)

    def test_page_states_the_pdf_pricing_model_plainly(self):
        self.assertIn("Success-Based Pricing", self.html)
        self.assertIn("50/50", self.html)
        self.assertIn("No upfront fees", self.html)
        self.assertIn("no subscriptions", self.lower_html)
        self.assertIn("you pay nothing", self.lower_html)

    def test_estimated_performance_is_contextualized_without_promises(self):
        self.assertIn("73%", self.html)
        self.assertIn("84%", self.html)
        self.assertIn("Estimated Results", self.html)
        self.assertIn("Estimated overall win rate", self.html)
        self.assertIn("results vary", self.lower_html)
        self.assertNotIn("historical reported", self.non_faq_lower)

        visible_non_faq = re.sub(r"<[^>]+>", " ", self.non_faq_html)
        promise_scan = visible_non_faq.replace("Guaranteed service", "")
        self.assertIsNone(
            re.search(r"\bguarantee(?:d|s)?\b", promise_scan, flags=re.IGNORECASE),
            "Non-FAQ copy must not turn performance or eligibility into a guarantee",
        )

    def test_page_removes_single_client_case_study_and_invented_testimonial(self):
        self.assertNotIn("E-Commerce Impact Analysis", self.html)
        self.assertNotIn("75.4%", self.html)
        self.assertNotIn("95.8%", self.html)
        self.assertNotIn("+21.5%", self.html)
        self.assertNotIn("measured beyond claim count", self.html)
        self.assertNotIn("Single-client case study", self.html)
        self.assertNotIn('class="case-study', self.html)
        self.assertNotIn("Sarah M.", self.html)
        self.assertNotIn("Trusted by e-commerce businesses", self.html)
        self.assertNotIn("Trusted by sellers on", self.html)

    def test_integration_and_late_shipment_copy_is_publish_safe(self):
        self.assertIn("Seamless Integration", self.html)
        self.assertIn("existing carrier accounts", self.lower_html)
        self.assertIn("no changes to your carriers", self.lower_html)
        self.assertIn("time-definite", self.lower_html)
        self.assertIn("carrier terms", self.lower_html)
        self.assertNotIn("full refund", self.non_faq_lower)
        self.assertNotIn("every unfiled exception", self.non_faq_lower)
        self.assertNotIn("cancel anytime", self.non_faq_lower)
        self.assertNotIn("most merchants are fully set up within 24 hours", self.non_faq_lower)

    def test_faq_matches_the_supplied_website_ready_source(self):
        self.assertEqual(hashlib.sha256(FAQ_SOURCE_PDF.read_bytes()).hexdigest(), FAQ_SOURCE_SHA256)
        self.assertEqual(self.faq_block.count('class="faq-item"'), 18)
        for question in WEBSITE_FAQ_QUESTIONS:
            with self.subTest(question=question):
                self.assertIn(question, self.faq_block)

        self.assertIn("the first $100 of shipment value is typically covered", self.faq_block)
        self.assertNotIn("Can you recover product value too?", self.faq_block)
        for stale_claim in (
            "Four main categories",
            "73% win rate",
            "fully set up within 24 hours",
            "No contract and no risk",
            "cancel anytime",
        ):
            with self.subTest(stale_claim=stale_claim):
                self.assertNotIn(stale_claim, self.faq_block)

        self.assertEqual(self.book_faq_block.count('class="faq-item"'), 3)
        for question in (
            "What does ShipZen do?",
            "How much does ShipZen cost?",
            "Do we need to switch carriers?",
        ):
            with self.subTest(book_question=question):
                self.assertIn(question, self.book_faq_block)
        self.assertNotIn("cancel anytime", self.book_faq_block.lower())
        self.assertNotIn("within 24 hours", self.book_faq_block.lower())

    def test_conversion_copy_phase_preserves_approved_faq_bytes(self):
        self.assertEqual(
            hashlib.sha256(self.faq_block.encode()).hexdigest(),
            APPROVED_HOME_FAQ_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.book_faq_block.encode()).hexdigest(),
            APPROVED_BOOK_FAQ_SHA256,
        )

    def test_booking_page_removes_fabricated_proof_and_matches_the_real_call_length(self):
        non_faq_book = self.book_html.replace(self.book_faq_block, "")
        self.assertNotIn("Sarah M.", non_faq_book)
        self.assertNotIn("Live in under 24 hours", non_faq_book)
        self.assertNotIn("Cancel anytime", non_faq_book)
        self.assertNotIn("15-Minute", non_faq_book)
        self.assertNotIn("15 minutes", non_faq_book)
        self.assertIn("Free 30-Minute Refund Audit", non_faq_book)
        self.assertIn("30 minutes", non_faq_book)
        self.assertIn("https://calendly.com/shipzen/30min", non_faq_book)
        self.assertIn('class="cal-mobile-link btn-book"', non_faq_book)
        self.assertIn("See How Much You're Owed.", non_faq_book)
        self.assertNotIn("Book Your Free Call", non_faq_book)
        self.assertIn('class="book-win-rate"', non_faq_book)
        self.assertIn("73% estimated overall win rate", non_faq_book.lower())
        self.assertIn("results vary", non_faq_book.lower())
        self.assertNotIn("means we find money most software misses", non_faq_book.lower())
        self.assertIn("matchMedia('(min-width: 601px)')", non_faq_book)
        self.assertIn("<noscript>", non_faq_book)
        self.assertIn("book-faq-answer-", non_faq_book)
        self.assertIn("btn.setAttribute('aria-controls',answer.id)", non_faq_book)

    def test_public_homepage_slideshow_alias_and_booking_routes_are_available(self):
        root = self.client.get("/")
        self.assertEqual(root.status_code, 200)
        root_html = root.get_data(as_text=True)
        self.assertIn('data-shipzen-revamp="discovery-deck-v1"', root_html)
        self.assertNotIn('content="noindex,nofollow"', root_html)
        slideshow = self.client.get("/slideshow")
        self.assertEqual(slideshow.status_code, 200)
        self.assertIn("data-shipzen-slideshow", slideshow.get_data(as_text=True))
        self.assertEqual(self.client.get("/book").status_code, 200)
        self.assertIn('<meta name="robots" content="noindex,nofollow">', self.html)

    def test_content_is_visible_without_javascript_and_primary_ctas_book_calls(self):
        self.assertNotIn(".fade-in{opacity:0", self.html.replace(" ", ""))
        self.assertIn('href="/book"', self.html)
        self.assertGreaterEqual(self.html.count('href="/book"'), 2)
        self.assertIn('class="skip-link"', self.html)
        self.assertNotIn('aria-live="polite"', self.non_faq_html)
        self.assertIn("prefers-reduced-motion", self.html)
        self.assertIn("<noscript>", self.html)
        self.assertIn(".faq-ans{max-height:none!important", self.html.replace(" ", ""))

    def test_faq_runtime_enhancement_links_each_button_to_its_answer(self):
        self.assertIn("answer.id='faq-answer-'", self.non_faq_html)
        self.assertIn("button.setAttribute('aria-controls',answer.id)", self.non_faq_html)


if __name__ == "__main__":
    unittest.main()
