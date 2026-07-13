import unittest
from pathlib import Path

import landing_v2


class TemporarySlideshowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        landing_v2.app.config.update(TESTING=True)
        cls.client = landing_v2.app.test_client()
        cls.repo_root = Path(landing_v2.__file__).resolve().parent

    def test_homepage_serves_uploaded_fourteen_slide_deck(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        self.assertIn("data-shipzen-slideshow", html)
        self.assertEqual(html.count('class="slide"'), 14)
        self.assertIn("/static/slides/shipzen-discovery-01.webp", html)
        self.assertIn("/static/slides/shipzen-discovery-14.webp", html)
        self.assertIn("We recover the shipping money carriers don't want you to know about.", html)
        self.assertNotIn("<iframe", html.lower())

    def test_homepage_has_accessible_navigation_and_booking_cta(self):
        html = self.client.get("/").get_data(as_text=True)

        self.assertIn('aria-label="Previous slide"', html)
        self.assertIn('aria-label="Next slide"', html)
        self.assertIn('aria-label="Pause slideshow"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn("ArrowRight", html)
        self.assertIn("ArrowLeft", html)
        self.assertIn("prefers-reduced-motion: reduce", html)
        self.assertIn('href="/book"', html)
        self.assertIn("Start Your Free Audit", html)

    def test_only_current_slide_is_visually_active_during_cross_fades(self):
        html = self.client.get("/").get_data(as_text=True)

        self.assertNotIn(".slide:first-child", html)
        self.assertIn('.slide[aria-hidden="false"]', html)

    def test_root_remains_indexable_and_has_canonical_url(self):
        html = self.client.get("/").get_data(as_text=True).lower()

        self.assertNotIn('content="noindex,nofollow"', html)
        self.assertIn('<link rel="canonical" href="https://shipzen.co/">', html)

    def test_slideshow_alias_serves_same_experience(self):
        response = self.client.get("/slideshow")
        self.assertEqual(response.status_code, 200)
        self.assertIn("data-shipzen-slideshow", response.get_data(as_text=True))

    def test_main_preview_preserves_rewritten_homepage_and_is_not_indexed(self):
        response = self.client.get("/main-preview")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        self.assertIn("Carriers owe you money", html)
        self.assertIn('<meta name="robots" content="noindex,nofollow">', html)

    def test_existing_book_and_lead_routes_remain_available(self):
        self.assertEqual(self.client.get("/book").status_code, 200)
        invalid = self.client.post("/api/lead", json={})
        self.assertEqual(invalid.status_code, 400)

    def test_version_endpoint_advertises_temporary_route_map(self):
        response = self.client.get("/version")
        self.assertEqual(response.status_code, 200)
        routes = response.get_json()["routes"]

        self.assertIn("/", routes)
        self.assertIn("/slideshow", routes)
        self.assertIn("/main-preview", routes)
        self.assertIn("/book", routes)

    def test_all_web_slide_assets_and_pdf_download_exist(self):
        slide_dir = self.repo_root / "static" / "slides"
        expected = [slide_dir / f"shipzen-discovery-{i:02d}.webp" for i in range(1, 15)]
        for path in expected:
            self.assertTrue(path.is_file(), path)
            self.assertGreater(path.stat().st_size, 10_000, path)

            response = self.client.get(f"/static/slides/{path.name}")
            self.assertEqual(response.status_code, 200, path)
            self.assertEqual(response.mimetype, "image/webp")
            response.close()

        pdf_path = self.repo_root / "static" / "shipzen-discovery-deck.pdf"
        self.assertTrue(pdf_path.is_file())
        pdf_response = self.client.get("/static/shipzen-discovery-deck.pdf")
        self.assertEqual(pdf_response.status_code, 200)
        pdf_response.close()


if __name__ == "__main__":
    unittest.main()
