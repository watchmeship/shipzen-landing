from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

ORIGIN = "http://127.0.0.1:8422"
HOME_URL = f"{ORIGIN}/"
SLIDESHOW_URL = f"{ORIGIN}/slideshow"
BOOK_URL = f"{ORIGIN}/book"
ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)

report: dict[str, Any] = {
    "homeUrl": HOME_URL,
    "slideshowUrl": SLIDESHOW_URL,
    "bookUrl": BOOK_URL,
    "viewports": {},
}
failures: list[str] = []


def record_checks(scope: str, state: dict[str, Any], checks: dict[str, bool]) -> None:
    state["checks"] = checks
    report["viewports"][scope] = state
    failures.extend(f"{scope}: {label}" for label, passed in checks.items() if not passed)


def wait_for_stable_page(page: Page) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception:
        # Third-party font and scheduling requests can stay open. DOM and fonts are the visual gate.
        pass
    page.evaluate("document.fonts.ready.then(() => true)")
    page.wait_for_timeout(250)


def inspect_home(page: Page, name: str, width: int) -> None:
    console_errors: list[str] = []
    page_errors: list[str] = []
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: page_errors.append(str(error)))

    response = page.goto(HOME_URL, wait_until="domcontentloaded", timeout=30_000)
    wait_for_stable_page(page)

    screenshot = ARTIFACTS / f"shipzen-approved-home-{name}.png"
    full_screenshot = ARTIFACTS / f"shipzen-approved-home-{name}-full.png"
    page.screenshot(path=str(screenshot), full_page=False, animations="disabled")
    page.screenshot(path=str(full_screenshot), full_page=True, animations="disabled")

    state = page.evaluate(
        """() => {
          const visible = (element) => {
            if (!element) return false;
            const style = getComputedStyle(element);
            const box = element.getBoundingClientRect();
            return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0
              && box.width > 0 && box.height > 0;
          };
          const rect = (selector) => {
            const element = document.querySelector(selector);
            if (!element) return null;
            const box = element.getBoundingClientRect();
            return {width: Math.round(box.width), height: Math.round(box.height), right: Math.round(box.right)};
          };
          const rgba = (value) => {
            const parts = value.match(/[\d.]+/g) || [];
            return [Number(parts[0] || 0), Number(parts[1] || 0), Number(parts[2] || 0), parts[3] === undefined ? 1 : Number(parts[3])];
          };
          const composite = (foreground, background) => {
            const alpha = foreground[3] + background[3] * (1 - foreground[3]);
            return [0, 1, 2].map((index) => (
              (foreground[index] * foreground[3] + background[index] * background[3] * (1 - foreground[3])) / alpha
            )).concat(alpha);
          };
          const effectiveBackground = (element) => {
            const ancestry = [];
            for (let node = element; node; node = node.parentElement) ancestry.unshift(node);
            return ancestry.reduce(
              (background, node) => composite(rgba(getComputedStyle(node).backgroundColor), background),
              [255, 255, 255, 1]
            );
          };
          const luminance = (channels) => {
            const normalized = channels.slice(0, 3).map((channel) => {
              const value = channel / 255;
              return value <= 0.04045 ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);
            });
            return 0.2126 * normalized[0] + 0.7152 * normalized[1] + 0.0722 * normalized[2];
          };
          const contrast = (foreground, background) => {
            const values = [luminance(rgba(foreground)), luminance(background)].sort((a, b) => b - a);
            return (values[0] + 0.05) / (values[1] + 0.05);
          };
          const contrastSelectors = [
            '.hero-sub', '.stats-disclaimer', '.problem-card p', '.recovery-note', '.faq-ans-inner'
          ];
          const contrastValues = Object.fromEntries(contrastSelectors.map((selector) => {
            const element = document.querySelector(selector);
            return [selector, element ? Number(contrast(getComputedStyle(element).color, effectiveBackground(element)).toFixed(2)) : 0];
          }));
          const ids = [...document.querySelectorAll('[id]')].map((element) => element.id);
          const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
          const missingAnchors = [...document.querySelectorAll('a[href^="#"]')]
            .map((anchor) => anchor.getAttribute('href').slice(1))
            .filter((id) => id && !document.getElementById(decodeURIComponent(id)));
          const unnamedControls = [...document.querySelectorAll('a,button,input,select,textarea')].filter((element) => {
            const name = element.getAttribute('aria-label') || element.getAttribute('title') || element.textContent || element.value || '';
            return !name.trim();
          });
          const headingLevels = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map((heading) => Number(heading.tagName.slice(1)));
          const headingSkips = headingLevels.slice(1).filter((level, index) => level > headingLevels[index] + 1);
          const faqButtons = [...document.querySelectorAll('.faq-q')];
          const faqAriaLinks = faqButtons.filter((button) => {
            const answerId = button.getAttribute('aria-controls');
            return answerId && document.getElementById(answerId) === button.closest('.faq-item').querySelector('.faq-ans');
          });
          const requiredSelectors = [
            '.hero', '.stats-section', '.problem-grid', '.quote-band', '.layer-wrap', '.claims-grid',
            '.steps-grid', '.integ-card', '.results-grid', '#faq', '.cta-section', '.footer'
          ];
          const missingRequired = requiredSelectors.filter((selector) => !document.querySelector(selector));
          const hiddenRequired = requiredSelectors.filter((selector) => !visible(document.querySelector(selector)));
          const failedImages = [...document.images].filter((image) => !image.complete || image.naturalWidth === 0);
          return {
            title: document.title,
            marker: document.body.dataset.shipzenRevamp || '',
            canonical: document.querySelector('link[rel="canonical"]')?.href || '',
            noindexCount: document.querySelectorAll('meta[name="robots"][content="noindex,nofollow"]').length,
            scrollWidth: document.documentElement.scrollWidth,
            viewportWidth: innerWidth,
            sectionCount: document.querySelectorAll('main > section').length,
            missingRequiredCount: missingRequired.length,
            hiddenRequiredCount: hiddenRequired.length,
            failedImageCount: failedImages.length,
            bookCtaCount: document.querySelectorAll('a[href="/book"]').length,
            navBrandPath: new URL(document.querySelector('.nav-brand').href).pathname,
            draftFooterCount: (document.querySelector('.footer-bottom')?.innerText.toLowerCase().match(/draft preview/g) || []).length,
            duplicateIdCount: duplicateIds.length,
            missingAnchorCount: missingAnchors.length,
            unnamedControlCount: unnamedControls.length,
            headingSkipCount: headingSkips.length,
            faqButtonCount: faqButtons.length,
            faqAriaLinkCount: faqAriaLinks.length,
            faqButtonMinHeight: Math.min(...faqButtons.map((button) => button.getBoundingClientRect().height)),
            h1: rect('h1'),
            navCta: rect('.nav .btn-primary'),
            heroPrimary: rect('.hero .btn-primary'),
            heroSecondary: rect('.hero .btn-ghost'),
            contrastValues,
            minimumKeyTextContrast: Math.min(...Object.values(contrastValues)),
            bodyBackground: getComputedStyle(document.body).backgroundColor,
            darkBandUsesGradient: getComputedStyle(document.querySelector('.quote-band')).backgroundImage.includes('gradient'),
            footerBackground: getComputedStyle(document.querySelector('.footer')).backgroundColor,
          };
        }"""
    )

    page.keyboard.press("Tab")
    skip_link_state = page.evaluate(
        """() => {
          const link = document.querySelector('.skip-link');
          if (!link) return {focused: false, visible: false};
          const box = link.getBoundingClientRect();
          return {focused: document.activeElement === link, visible: box.top >= 0 && box.height > 0};
        }"""
    )
    page.keyboard.press("Enter")
    page.wait_for_timeout(75)
    skip_link_state["targetHash"] = page.evaluate("location.hash")

    page.locator(".faq-q").first.click()
    page.wait_for_function(
        "document.querySelector('.faq-ans').getBoundingClientRect().height > 0",
        timeout=2_000,
    )
    faq_state = page.evaluate(
        """() => {
          const item = document.querySelector('.faq-item');
          const button = item.querySelector('.faq-q');
          const answer = item.querySelector('.faq-ans');
          return {
            open: item.classList.contains('open'),
            expanded: button.getAttribute('aria-expanded'),
            answerHeight: Math.round(answer.getBoundingClientRect().height),
          };
        }"""
    )
    faq_screenshot = ARTIFACTS / f"shipzen-approved-home-{name}-faq.png"
    page.locator("#faq").screenshot(path=str(faq_screenshot), animations="disabled")

    state.update(
        {
            "httpStatus": response.status if response else None,
            "skipLink": skip_link_state,
            "faqInteraction": faq_state,
            "consoleErrors": console_errors,
            "pageErrors": page_errors,
            "screenshot": str(screenshot),
            "fullScreenshot": str(full_screenshot),
            "faqScreenshot": str(faq_screenshot),
        }
    )
    checks = {
        "HTTP 200": state["httpStatus"] == 200,
        "approved revamp marker": state["marker"] == "discovery-deck-v1",
        "public root is indexable": state["noindexCount"] == 0,
        "canonical points to public root": state["canonical"] == "https://shipzen.co/",
        "no horizontal overflow": state["scrollWidth"] <= width + 1,
        "all approved sections exist and are visible": state["missingRequiredCount"] == 0 and state["hiddenRequiredCount"] == 0,
        "all page images loaded": state["failedImageCount"] == 0,
        "production home link and footer": state["navBrandPath"] == "/" and state["draftFooterCount"] == 0,
        "booking CTAs present": state["bookCtaCount"] >= 3,
        "no duplicate IDs": state["duplicateIdCount"] == 0,
        "all in-page anchors resolve": state["missingAnchorCount"] == 0,
        "all controls have accessible names": state["unnamedControlCount"] == 0,
        "heading levels do not skip": state["headingSkipCount"] == 0,
        "FAQ controls map to all 18 answers": state["faqButtonCount"] == 18 and state["faqAriaLinkCount"] == 18,
        "FAQ opens accessibly": faq_state["open"] and faq_state["expanded"] == "true" and faq_state["answerHeight"] > 0,
        "FAQ controls meet tap target": state["faqButtonMinHeight"] >= 44,
        "skip link works from keyboard": skip_link_state["focused"] and skip_link_state["visible"] and skip_link_state["targetHash"] == "#main-content",
        "H1 remains inside viewport": state["h1"] is not None and state["h1"]["right"] <= width + 1,
        "navigation CTA is usable": state["navCta"] is not None and state["navCta"]["height"] >= 42,
        "hero CTAs meet tap targets": state["heroPrimary"] is not None and state["heroPrimary"]["height"] >= 48 and state["heroSecondary"] is not None and state["heroSecondary"]["height"] >= 48,
        "key light-surface copy meets WCAG AA": state["minimumKeyTextContrast"] >= 4.5,
        "approved sky/light/navy visual system present": state["bodyBackground"] == "rgb(171, 205, 233)" and state["darkBandUsesGradient"],
        "no browser errors": not console_errors and not page_errors,
    }
    record_checks(name, state, checks)


def inspect_slideshow(page: Page) -> None:
    response = page.goto(SLIDESHOW_URL, wait_until="domcontentloaded", timeout=30_000)
    wait_for_stable_page(page)
    state = page.evaluate(
        """() => ({
          markerPresent: Boolean(document.querySelector('[data-shipzen-slideshow]')),
          noindexCount: document.querySelectorAll('meta[name="robots"][content="noindex,nofollow"]').length,
          slideCount: document.querySelectorAll('.slide').length,
          activeSlideCount: document.querySelectorAll('.slide[aria-hidden="false"]').length,
          scrollWidth: document.documentElement.scrollWidth,
          viewportWidth: innerWidth,
        })"""
    )
    state["httpStatus"] = response.status if response else None
    checks = {
        "HTTP 200": state["httpStatus"] == 200,
        "slideshow marker retained": state["markerPresent"],
        "slideshow remains noindex": state["noindexCount"] == 1,
        "all 14 slides retained": state["slideCount"] == 14,
        "exactly one active slide": state["activeSlideCount"] == 1,
        "no horizontal overflow": state["scrollWidth"] <= state["viewportWidth"] + 1,
    }
    record_checks("slideshow", state, checks)


def inspect_book(page: Page, name: str, width: int) -> None:
    console_errors: list[str] = []
    page_errors: list[str] = []
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: page_errors.append(str(error)))

    response = page.goto(BOOK_URL, wait_until="domcontentloaded", timeout=30_000)
    calendly_loaded = False
    calendly_load_error = ""
    try:
        if width > 600:
            page.locator(".calendly-inline-widget iframe").wait_for(state="visible", timeout=20_000)
            calendly_loaded = True
        else:
            page.locator(".cal-mobile-link").wait_for(state="visible", timeout=5_000)
            calendly_loaded = True
    except Exception as error:
        calendly_load_error = str(error)
    wait_for_stable_page(page)

    artifact_name = name.removeprefix("book").lower()
    screenshot = ARTIFACTS / f"shipzen-approved-book-{artifact_name}.png"
    full_screenshot = ARTIFACTS / f"shipzen-approved-book-{artifact_name}-full.png"
    page.screenshot(path=str(screenshot), full_page=False, animations="disabled")
    page.screenshot(path=str(full_screenshot), full_page=True, animations="disabled")

    state = page.evaluate(
        """() => {
          const faqButtons = [...document.querySelectorAll('.faq-q')];
          const faqAriaLinks = faqButtons.filter((button) => {
            const answerId = button.getAttribute('aria-controls');
            return answerId && document.getElementById(answerId) === button.closest('.faq-item').querySelector('.faq-ans');
          });
          const bodyClone = document.body.cloneNode(true);
          bodyClone.querySelector('.faq-section')?.remove();
          const nonFaqText = bodyClone.innerText;
          const ids = [...document.querySelectorAll('[id]')].map((element) => element.id);
          const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
          const externalBlankLinks = [...document.querySelectorAll('a[target="_blank"]')];
          const inline = document.querySelector('.calendly-inline-widget');
          const mobileLink = document.querySelector('.cal-mobile-link');
          return {
            noindexCount: document.querySelectorAll('meta[name="robots"][content="noindex,nofollow"]').length,
            scrollWidth: document.documentElement.scrollWidth,
            viewportWidth: innerWidth,
            calendlyUrl: inline?.dataset.url || '',
            calendlyIframeCount: document.querySelectorAll('.calendly-inline-widget iframe').length,
            calendlyInlineVisible: inline ? getComputedStyle(inline).display !== 'none' && inline.getBoundingClientRect().height > 0 : false,
            mobileCalendlyLinkVisible: mobileLink ? getComputedStyle(mobileLink).display !== 'none' && mobileLink.getBoundingClientRect().height >= 44 : false,
            mobileCalendlyLinkHref: mobileLink?.href || '',
            proofSectionCount: document.querySelectorAll('.proof-section').length,
            fabricatedTestimonialCount: (nonFaqText.match(/Sarah M\./g) || []).length,
            fifteenMinuteCount: (nonFaqText.match(/15[- ]?minutes?/gi) || []).length,
            thirtyMinuteCount: (nonFaqText.match(/30[- ]?minutes?/gi) || []).length,
            faqButtonCount: faqButtons.length,
            faqAriaLinkCount: faqAriaLinks.length,
            faqButtonMinHeight: Math.min(...faqButtons.map((button) => button.getBoundingClientRect().height)),
            duplicateIdCount: duplicateIds.length,
            unsafeTargetBlankCount: externalBlankLinks.filter((link) => !(link.rel || '').split(/\s+/).includes('noopener')).length,
          };
        }"""
    )
    page.locator(".faq-q").first.click()
    page.wait_for_function(
        "document.querySelector('.faq-ans').getBoundingClientRect().height > 0",
        timeout=2_000,
    )
    faq_state = page.evaluate(
        """() => {
          const item = document.querySelector('.faq-item');
          const button = item.querySelector('.faq-q');
          const answer = item.querySelector('.faq-ans');
          return {
            open: item.classList.contains('open'),
            expanded: button.getAttribute('aria-expanded'),
            answerHeight: Math.round(answer.getBoundingClientRect().height),
          };
        }"""
    )

    ignored_errors = [message for message in console_errors if message == "requestStorageAccess: Permission denied."]
    actionable_errors = [message for message in console_errors if message not in ignored_errors]
    if width > 600:
        responsive_mode = calendly_loaded and state["calendlyInlineVisible"] and state["calendlyIframeCount"] >= 1 and not state["mobileCalendlyLinkVisible"]
    else:
        responsive_mode = calendly_loaded and not state["calendlyInlineVisible"] and state["mobileCalendlyLinkVisible"] and state["mobileCalendlyLinkHref"].startswith("https://calendly.com/shipzen/30min")

    state.update(
        {
            "httpStatus": response.status if response else None,
            "calendlyRendered": calendly_loaded,
            "calendlyLoadError": calendly_load_error,
            "faqInteraction": faq_state,
            "consoleErrors": actionable_errors,
            "ignoredThirdPartyConsoleErrors": ignored_errors,
            "pageErrors": page_errors,
            "screenshot": str(screenshot),
            "fullScreenshot": str(full_screenshot),
        }
    )
    checks = {
        "HTTP 200": state["httpStatus"] == 200,
        "booking page remains noindex": state["noindexCount"] == 1,
        "no horizontal overflow": state["scrollWidth"] <= width + 1,
        "real 30-minute Calendly URL": state["calendlyUrl"].startswith("https://calendly.com/shipzen/30min"),
        "responsive scheduling path is usable": responsive_mode,
        "fabricated proof remains removed": state["proofSectionCount"] == 0 and state["fabricatedTestimonialCount"] == 0,
        "visible call length matches Calendly": state["fifteenMinuteCount"] == 0 and state["thirtyMinuteCount"] >= 2,
        "FAQ controls map to all 3 answers": state["faqButtonCount"] == 3 and state["faqAriaLinkCount"] == 3,
        "FAQ opens accessibly": faq_state["open"] and faq_state["expanded"] == "true" and faq_state["answerHeight"] > 0,
        "FAQ controls meet tap target": state["faqButtonMinHeight"] >= 44,
        "no duplicate IDs": state["duplicateIdCount"] == 0,
        "target-blank links are isolated": state["unsafeTargetBlankCount"] == 0,
        "no browser errors": not actionable_errors and not page_errors,
    }
    record_checks(name, state, checks)


def inspect_no_javascript(page: Page, url: str, name: str, expected_faqs: int) -> None:
    response = page.goto(url, wait_until="load", timeout=30_000)
    faq_boxes = [locator.bounding_box() for locator in page.locator(".faq-ans").all()]
    state = {
        "httpStatus": response.status if response else None,
        "faqAnswerCount": len(faq_boxes),
        "visibleFaqAnswerCount": sum(1 for box in faq_boxes if box and box["height"] > 0),
    }
    checks = {
        "HTTP 200": state["httpStatus"] == 200,
        "all FAQ answers visible without JavaScript": state["faqAnswerCount"] == expected_faqs and state["visibleFaqAnswerCount"] == expected_faqs,
    }
    record_checks(name, state, checks)


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)

    desktop = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
    inspect_home(desktop, "homeDesktop", 1440)
    desktop.close()

    mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True)
    inspect_home(mobile, "homeMobile", 390)
    mobile.close()

    slideshow = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    inspect_slideshow(slideshow)
    slideshow.close()

    book_desktop = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
    inspect_book(book_desktop, "bookDesktop", 1440)
    book_desktop.close()

    book_mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True)
    inspect_book(book_mobile, "bookMobile", 390)
    book_mobile.close()

    home_no_js = browser.new_page(viewport={"width": 1280, "height": 900}, java_script_enabled=False)
    inspect_no_javascript(home_no_js, HOME_URL, "homeNoJavaScript", 18)
    home_no_js.close()

    book_no_js = browser.new_page(viewport={"width": 1280, "height": 900}, java_script_enabled=False)
    inspect_no_javascript(book_no_js, BOOK_URL, "bookNoJavaScript", 3)
    book_no_js.close()

    browser.close()

report["failures"] = failures
report_path = ARTIFACTS / "visual-verification.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
if failures:
    raise SystemExit(1)
