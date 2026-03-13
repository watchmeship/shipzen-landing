#!/usr/bin/env python3
"""
ShipZen Landing Page V2 — GoShippo-Inspired Design
----------------------------------------------------
Standalone Flask app. Runs on port 8422.
Shares the same SQLite DB as v1 for lead capture.
Run with: python3 landing_v2.py
"""

import sqlite3
import os
import re
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "shipzen-landing-v2-2026")

DB_PATH = Path(__file__).resolve().parent / "landing_leads.db"


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS landing_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            phone TEXT,
            website TEXT,
            monthly_shipments TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


def validate_lead(data):
    errors = []
    email = data.get("email", "").strip()
    if not email:
        errors.append("Email is required.")
    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors.append("Please enter a valid email address.")
    return errors


@app.route("/")
def landing():
    return render_template_string(LANDING_HTML)


@app.route("/api/lead", methods=["POST"])
def submit_lead():
    data = request.get_json(silent=True) or {}
    errors = validate_lead(data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    conn = get_db()
    conn.execute(
        """INSERT INTO landing_leads (email, phone, website, monthly_shipments)
           VALUES (?, ?, ?, ?)""",
        (
            data["email"].strip(),
            data.get("phone", "").strip(),
            data.get("website", "").strip(),
            data.get("monthly_shipments", "").strip(),
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "message": "Thanks! We'll send your savings quote within 24 hours."})


LANDING_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ShipZen — Enterprise UPS Ground Rates for E-Commerce</title>
<meta name="description" content="Enterprise UPS Ground rates powered by lane optimization. Save $1–$2 on average per shipping label vs Pirate Ship, ShipStation, EasyShip.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Nunito:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
--bg:#ffffff;--bg-off:#f8fafb;--bg-blue:#f0f5ff;--bg-sage:#F6F4F0;
--navy:#1a1a1a;--body:#475569;--muted:#64748b;
--accent:#1a1a1a;--accent-hover:#333;--cyan:#00b4d8;--green:#10b981;
--border:#e2e8f0;--border-lt:#eef1f5;
--shadow-sm:0 1px 3px rgba(0,0,0,.04);--shadow:0 4px 16px rgba(0,0,0,.06);--shadow-lg:0 12px 40px rgba(0,0,0,.08);
--radius:12px;--radius-lg:16px;--radius-xl:20px;
--max-w:1280px;--tr:.25s ease;
--font-head:'Nunito',sans-serif;--font-body:'Inter',sans-serif;
}
html{font-size:16px;scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{font-family:var(--font-body);color:var(--body);background:#ABCDE9;line-height:1.7}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block}
.container{max-width:var(--max-w);margin:0 auto;padding:0 1.5rem}
.ck{width:16px;height:16px;flex-shrink:0}

/* ===== CLOUD BACKGROUND ===== */
.cloud-bg{position:fixed;inset:0;z-index:0;pointer-events:none}
.cloud-bg .sky-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.8;mix-blend-mode:multiply}
.cloud-bg .sky-gradient{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(166,203,232,.2),rgba(191,217,239,.4),rgba(234,227,214,.6))}
.cloud-bg .cloud-img{position:absolute;width:50%;opacity:.4;mix-blend-mode:screen;filter:blur(24px);pointer-events:none}
.cloud-bg .cloud-l{top:20%;left:-10%}
.cloud-bg .cloud-r{top:30%;right:-10%}

/* All sections sit above cloud bg */
.stats-section,.ent-section,.hiw-section,.cmp-section,.feat-section,.test-section,.faq-section,.cta-section,.footer{position:relative;z-index:1}
/* Frosted glass card treatment */
.glass{background:rgba(255,255,255,.55);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.6)}

/* ===== NAV ===== */
.nav{position:fixed;top:0;left:0;right:0;z-index:100;height:64px;background:rgba(255,255,255,.05);border-bottom:1px solid rgba(255,255,255,.1);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);transition:all .3s}
.nav.scrolled{background:rgba(255,255,255,.95);border-color:var(--border);box-shadow:0 1px 8px rgba(0,0,0,.05)}
.nav-inner{max-width:var(--max-w);margin:0 auto;padding:0 1.5rem;height:64px;display:flex;align-items:center;justify-content:space-between}
.nav-brand{font-family:var(--font-head);font-weight:700;font-size:1.2rem;color:var(--navy);text-decoration:none;display:flex;align-items:center;gap:.5rem;transition:color .3s}
.nav-brand svg{flex-shrink:0}
.nav-actions{display:flex;align-items:center;gap:.75rem}
.btn-contact{font-size:.88rem;font-weight:500;color:var(--body);padding:.45rem 1rem;border-radius:9999px;transition:all var(--tr);text-decoration:none}
.btn-contact:hover{color:var(--navy);background:var(--bg-off)}
.btn-primary{display:inline-flex;align-items:center;gap:.4rem;background:var(--accent);color:#fff;padding:.6rem 1.5rem;border-radius:9999px;font-weight:500;font-size:.88rem;transition:all var(--tr);text-decoration:none;border:none;cursor:pointer;font-family:inherit}
.btn-primary:hover{background:var(--accent-hover);transform:translateY(-1px);box-shadow:0 4px 16px rgba(0,0,0,.15)}
.nav.scrolled .btn-primary{background:var(--accent);color:#fff}

/* ===== HERO ===== */
.hero{padding:calc(64px + 4rem) 0 2rem;position:relative;overflow:visible;z-index:1}
.hero-bg{display:none}
.hero-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:3rem;align-items:start;position:relative;z-index:1}
.hero-left{text-align:left}
.hero-tag{display:inline-flex;align-items:center;gap:.4rem;font-size:.75rem;font-weight:600;color:var(--navy);background:rgba(255,255,255,.6);border:1px solid rgba(255,255,255,.8);padding:.35rem .85rem;border-radius:9999px;margin-bottom:1.25rem;text-transform:uppercase;letter-spacing:.06em;backdrop-filter:blur(8px)}
.hero h1{font-family:var(--font-head);font-size:clamp(2.25rem,5vw,3.75rem);font-weight:600;line-height:1.05;letter-spacing:-.04em;color:var(--navy);margin-bottom:1.25rem}
.hero-sub{font-size:1.1rem;color:var(--body);margin-bottom:2rem;line-height:1.65;max-width:520px}
.hero-ctas{display:flex;align-items:center;gap:1.25rem;flex-wrap:wrap}
.hero-link{font-size:.88rem;font-weight:500;color:var(--navy);display:flex;align-items:center;gap:.35rem;transition:gap var(--tr)}
.hero-link:hover{gap:.55rem}
.hero-link svg{width:16px;height:16px;transition:transform var(--tr)}

/* ===== FORM CARD ===== */
.form-card{background:rgba(255,255,255,.7);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,.8);border-radius:var(--radius-xl);padding:2.5rem;box-shadow:0 8px 32px rgba(0,0,0,.08)}
.form-title{font-family:var(--font-head);font-size:1.5rem;font-weight:600;letter-spacing:-.02em;color:var(--navy);margin-bottom:.3rem}
.form-sub{font-size:.88rem;color:var(--muted);margin-bottom:1.75rem}
.fg{display:grid;grid-template-columns:1fr;gap:.9rem}
.fi{display:flex;flex-direction:column;gap:.3rem}
.fi label{font-size:.68rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.fi input,.fi select{padding:.72rem .9rem;border:1px solid var(--border);border-radius:10px;font-size:.88rem;font-family:inherit;color:var(--navy);background:var(--bg-off);outline:none;transition:all var(--tr);-webkit-appearance:none;appearance:none}
.fi input::placeholder{color:var(--muted)}
.fi input:focus,.fi select:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(37,99,235,.1);background:#fff}
.fi input.err{border-color:#dc2626}
.fi select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath d='M3 5l3 3 3-3' fill='none' stroke='%2394a3b8' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right .85rem center;padding-right:2.2rem}
.f-btns{margin-top:.25rem}
.btn-submit{width:100%;background:var(--accent);color:#fff;border:none;border-radius:9999px;padding:.85rem;font-size:.95rem;font-weight:500;font-family:inherit;cursor:pointer;transition:all var(--tr)}
.btn-submit:hover{background:var(--accent-hover)}
.btn-submit:disabled{opacity:.6;cursor:not-allowed}
.form-trust{display:flex;justify-content:center;gap:1.25rem;margin-top:.5rem;flex-wrap:wrap}
.form-trust span{font-size:.72rem;color:var(--muted);font-weight:500;display:flex;align-items:center;gap:.3rem}
.form-msg{padding:.65rem .85rem;border-radius:8px;font-size:.82rem;font-weight:500;display:none;margin-top:.5rem}
.form-msg.ok{display:block;background:#ecfdf5;color:#059669}
.form-msg.err{display:block;background:#fef2f2;color:#dc2626}

/* ===== LOGO BAR (inside hero) ===== */
.logo-bar{display:flex;align-items:center;gap:1.5rem;padding:0;position:relative;z-index:1}
.logo-bar-label{font-size:.65rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;white-space:nowrap;flex-shrink:0;padding-left:1.5rem}
.logo-track{flex:1;overflow:hidden;mask-image:linear-gradient(to right,transparent 0%,#000 6%,#000 94%,transparent 100%);-webkit-mask-image:linear-gradient(to right,transparent 0%,#000 6%,#000 94%,transparent 100%)}
.logo-scroll{display:flex;align-items:center;gap:3rem;width:max-content;animation:logoMarquee 28s linear infinite}
@keyframes logoMarquee{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.logo-scroll span{display:flex;align-items:center;justify-content:center;flex-shrink:0;opacity:.55;transition:opacity .3s}
.logo-scroll span:hover{opacity:.85}
.logo-scroll span svg{width:56px;height:24px}

/* ===== STATS BAR ===== */
.stats-section{padding:0;background:rgba(255,255,255,.55);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-top:1px solid rgba(255,255,255,.6);border-bottom:1px solid rgba(255,255,255,.6)}
.stats-inner{max-width:var(--max-w);margin:0 auto;padding:2rem 2rem .75rem}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;text-align:center}
.stat-item{padding:1rem .5rem}
.stat-val{font-family:var(--font-head);font-size:clamp(2rem,4vw,3rem);font-weight:700;color:var(--navy);letter-spacing:-.04em;line-height:1.1}
.stat-val .stat-accent{color:var(--cyan)}
.stat-label{font-size:.88rem;color:var(--body);margin-top:.35rem;font-weight:500}
.stats-logos{padding:.4rem 2rem;background:rgba(255,255,255,.3);border-top:1px solid rgba(255,255,255,.45)}

/* ===== SECTION LABELS ===== */
.sl{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:.75rem}
.st{font-family:var(--font-head);font-size:clamp(1.75rem,3.5vw,2.85rem);font-weight:600;letter-spacing:-.035em;color:var(--navy);margin-bottom:.75rem;line-height:1.15}
.sd{color:var(--body);max-width:600px;font-size:1.05rem;margin-bottom:1.75rem;line-height:1.65}
.sl.c,.st.c,.sd.c{text-align:center;margin-left:auto;margin-right:auto}

/* ===== ENTERPRISE CARDS ===== */
.ent-section{padding:3rem 0 4rem}
.ent-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem}
.ent-card{background:rgba(255,255,255,.6);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.7);border-radius:var(--radius-xl);overflow:hidden;display:flex;flex-direction:column;transition:box-shadow .35s,transform .35s}
.ent-card:hover{box-shadow:var(--shadow-lg);transform:translateY(-4px)}
.ent-head{display:flex;justify-content:space-between;align-items:flex-start;padding:1.75rem 1.75rem 0}
.ent-head h3{font-family:var(--font-head);font-size:1.1rem;font-weight:600;line-height:1.35;color:var(--navy);margin:0;max-width:85%}
.ent-ico{width:36px;height:36px;border-radius:10px;background:var(--bg-blue);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.ent-ico svg{width:18px;height:18px;color:#2563eb}
.ent-visual{position:relative;flex:1;min-height:230px;overflow:hidden}
.ent-visual canvas{position:absolute;inset:0;width:100%;height:100%}
.ent-visual::before{content:'';position:absolute;top:0;left:0;right:0;height:40%;background:linear-gradient(to bottom,rgba(255,255,255,.6) 0%,rgba(255,255,255,.6) 15%,rgba(255,255,255,0) 100%);z-index:1;pointer-events:none}

/* ===== HOW IT WORKS ===== */
.hiw-section{padding:3rem 0 4rem}
.hiw-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem}
.hiw-card{background:rgba(255,255,255,.6);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.7);border-radius:var(--radius-xl);overflow:hidden;display:flex;flex-direction:column;transition:box-shadow .35s,transform .35s}
.hiw-card:hover{box-shadow:var(--shadow-lg);transform:translateY(-4px)}
.hiw-head{display:flex;justify-content:space-between;align-items:flex-start;padding:1.75rem 1.75rem 0}
.hiw-head h3{font-family:var(--font-head);font-size:1.1rem;font-weight:600;line-height:1.35;color:var(--navy);margin:0;max-width:85%}
.hiw-ico{width:36px;height:36px;border-radius:10px;background:var(--bg-blue);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.hiw-ico svg{width:18px;height:18px;color:#2563eb}
.hiw-body{padding:1.25rem 1.75rem 1.75rem;flex:1;display:flex;flex-direction:column}
.hiw-desc{font-size:.875rem;color:var(--body);line-height:1.7;flex:1}
.hiw-result{display:flex;align-items:center;gap:.4rem;font-size:.8rem;font-weight:600;color:var(--green);margin-top:1.25rem;padding-top:1rem;border-top:1px solid var(--border-lt)}

/* ===== COMPARISON TABLE ===== */
.cmp-section{padding:3rem 0 4rem}
.cmp-table{max-width:880px;margin:0 auto;overflow-x:auto}
.cmp-table table{width:100%;border-collapse:separate;border-spacing:0;font-size:.85rem;background:rgba(255,255,255,.6);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-radius:var(--radius-xl);border:1px solid rgba(255,255,255,.7);overflow:hidden}
.cmp-table thead tr{background:rgba(255,255,255,.3)}
.cmp-table th{padding:.95rem 1.1rem;font-weight:600;border-bottom:1px solid var(--border-lt);font-size:.82rem}
.cmp-table th:first-child{text-align:left;width:22%}
.cmp-table th:not(:first-child){text-align:center;width:26%}
.cmp-table th.hl{color:#2563eb;border-bottom:2px solid #2563eb;background:rgba(37,99,235,.03)}
.cmp-table th .sub{font-weight:400;font-size:.72rem;color:var(--muted);display:block;margin-top:2px}
.cmp-table td{padding:.8rem 1.1rem;border-bottom:1px solid var(--border-lt);color:var(--body)}
.cmp-table td:first-child{font-weight:600;color:var(--navy)}
.cmp-table td:not(:first-child){text-align:center}
.cmp-table td.hl{font-weight:600;background:rgba(37,99,235,.03);color:#2563eb}
.cmp-table tr:last-child td{border-bottom:none}

/* ===== INTEGRATIONS / FEATURES ===== */
.feat-section{padding:3rem 0 4rem}
.feat-card{background:var(--bg-sage);border-radius:var(--radius-xl);padding:3rem 3.5rem;max-width:780px;margin:0 auto;overflow:hidden}
.feat-card h3{font-family:var(--font-head);font-size:clamp(1.5rem,3vw,2rem);font-weight:600;color:var(--navy);letter-spacing:-.02em;margin-bottom:1.75rem;line-height:1.25}
.integ-track{overflow:hidden;margin:0 -3.5rem;padding:0 3.5rem;-webkit-mask-image:linear-gradient(90deg,transparent,#000 3.5rem,#000 calc(100% - 3.5rem),transparent);mask-image:linear-gradient(90deg,transparent,#000 3.5rem,#000 calc(100% - 3.5rem),transparent);margin-bottom:1.75rem}
.integ-scroll{display:flex;gap:1rem;width:max-content;animation:integMarquee 18s linear infinite}
@keyframes integMarquee{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.integ-icon{width:72px;height:72px;flex-shrink:0;background:#fff;border-radius:16px;display:flex;align-items:center;justify-content:center;box-shadow:0 1px 4px rgba(0,0,0,.04)}
.integ-icon svg{width:48px;height:34px}
.feat-desc{font-size:1.05rem;color:var(--body);line-height:1.7;max-width:620px}

/* ===== TESTIMONIAL ===== */
.test-section{padding:3rem 0 4rem}
.test-card{max-width:680px;margin:0 auto;text-align:left;padding:3rem 3rem 2.5rem;background:rgba(255,255,255,.55);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.6);border-radius:var(--radius-xl);box-shadow:0 8px 32px rgba(0,0,0,.06);position:relative}
.test-quote{font-size:1.15rem;font-weight:500;color:var(--navy);line-height:1.75;font-style:italic;margin-bottom:1.5rem;position:relative;padding-top:2.5rem}
.test-quote::before{content:'\201C';font-size:2.5rem;font-weight:900;color:var(--navy);opacity:.18;position:absolute;top:-.25rem;left:0;font-style:normal;line-height:1}
.test-author{font-size:.88rem;font-weight:700;color:var(--navy)}
.test-role{font-size:.78rem;color:var(--muted);margin-top:.15rem}

/* ===== FAQ ===== */
.faq-section{padding:3rem 0 4rem}
.faq-wrap{max-width:720px;margin:0 auto;background:rgba(255,255,255,.5);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.6);border-radius:var(--radius-xl);padding:1rem 2rem;box-shadow:0 8px 32px rgba(0,0,0,.04)}
.faq-item{border-bottom:1px solid rgba(255,255,255,.6)}
.faq-q{width:100%;background:none;border:none;padding:1.15rem 0;display:flex;align-items:center;justify-content:space-between;cursor:pointer;font-family:var(--font-head);font-size:.95rem;font-weight:600;color:var(--navy);text-align:left;gap:.75rem;transition:color var(--tr)}
.faq-q:hover{color:var(--muted)}
.faq-chevron{width:18px;height:18px;flex-shrink:0;transition:transform .3s;color:var(--muted)}
.faq-item.open .faq-chevron{transform:rotate(180deg)}
.faq-ans{max-height:0;overflow:hidden;transition:max-height .35s}
.faq-item.open .faq-ans{max-height:600px}
.faq-ans-inner{padding:0 0 1.15rem;font-size:.85rem;color:var(--body);line-height:1.75}

/* ===== CTA BANNER ===== */
.cta-section{background:rgba(255,255,255,.55);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-top:1px solid rgba(255,255,255,.6);border-bottom:1px solid rgba(255,255,255,.6)}
.cta-section .container{padding-top:4rem;padding-bottom:4rem}
.cta-inner{text-align:center}
.cta-inner h2{font-family:var(--font-head);font-size:clamp(1.6rem,3.5vw,2.4rem);font-weight:600;letter-spacing:-.03em;color:var(--navy);margin-bottom:.65rem}
.cta-inner p{font-size:.95rem;color:var(--body);max-width:440px;margin:0 auto 1.75rem;line-height:1.7}
.cta-buttons{display:flex;justify-content:center;gap:1rem;flex-wrap:wrap}
.btn-cta-w{display:inline-flex;background:var(--accent);color:#fff;font-weight:500;font-size:.9rem;font-family:inherit;padding:.75rem 1.85rem;border-radius:9999px;border:none;cursor:pointer;transition:all var(--tr);text-decoration:none}
.btn-cta-w:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg)}
.btn-cta-ghost{display:inline-flex;background:transparent;color:var(--navy);font-weight:500;font-size:.88rem;font-family:inherit;padding:.7rem 1.5rem;border-radius:9999px;border:1px solid var(--border-lt);cursor:pointer;transition:all var(--tr);text-decoration:none}
.btn-cta-ghost:hover{background:rgba(0,0,0,.03);border-color:rgba(0,0,0,.15)}

/* ===== FOOTER ===== */
.footer{background:var(--navy);color:#fff;padding:4.5rem 0 2rem}
.footer-grid{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:2.5rem;margin-bottom:3rem}
.footer-brand{display:flex;align-items:center;gap:.5rem;font-family:var(--font-head);font-weight:700;font-size:1.15rem;color:#fff;margin-bottom:.75rem}
.footer-brand svg{flex-shrink:0}
.footer-desc{font-size:.82rem;color:rgba(255,255,255,.5);line-height:1.7;max-width:280px}
.footer-col h4{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:rgba(255,255,255,.4);margin-bottom:1rem}
.footer-col ul{list-style:none}
.footer-col ul li{margin-bottom:.55rem}
.footer-col ul a{font-size:.84rem;color:rgba(255,255,255,.65);transition:color var(--tr);text-decoration:none}
.footer-col ul a:hover{color:#fff}
.footer-bottom{border-top:1px solid rgba(255,255,255,.08);padding-top:1.5rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.75rem}
.footer-copy{font-size:.75rem;color:rgba(255,255,255,.35)}

/* ===== ANIMATIONS ===== */
@keyframes fadeSlideUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
.fade-in{opacity:0;transform:translateY(16px);transition:opacity .6s,transform .6s}
.fade-in.visible{opacity:1;transform:translateY(0)}

/* ===== RESPONSIVE ===== */
@media(max-width:920px){
.hero-grid{grid-template-columns:1fr}
.hero-left{text-align:center}
.hero-sub{margin-left:auto;margin-right:auto}
.hero-ctas{justify-content:center}
.form-card{max-width:480px;margin:0 auto}
}
@media(max-width:768px){
.ent-grid,.hiw-grid{grid-template-columns:1fr}
.stats-grid{grid-template-columns:repeat(2,1fr);gap:1.5rem}
.footer-grid{grid-template-columns:repeat(2,1fr)}
.nav-actions .btn-contact{display:none}
.logo-bar-label{display:none}
}
@media(max-width:480px){
.stats-grid{grid-template-columns:1fr}

.footer-grid{grid-template-columns:1fr}
.logo-scroll{gap:2.5rem}
.hero-ctas{flex-direction:column;align-items:center}
}
</style>
</head>
<body>

<!-- FIXED CLOUD BACKGROUND -->
<div class="cloud-bg">
<img class="sky-img" src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/bfd2f4cf-65ed-4b1a-86d1-a1710619267b_1600w.png" alt="" loading="eager">
<div class="sky-gradient"></div>
<img class="cloud-img cloud-l" src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/4734259a-bad7-422f-981e-ce01e79184f2_1600w.jpg" alt="" loading="eager">
<img class="cloud-img cloud-r" src="https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/917d6f93-fb36-439a-8c48-884b67b35381_1600w.jpg" alt="" loading="eager">
</div>

<!-- NAV -->
<nav class="nav">
<div class="nav-inner">
<a href="#" class="nav-brand">
<svg width="28" height="28" viewBox="0 0 40 40" fill="none"><path d="M4,2L36,2Q39,2 39,5L39,14L7,29L1,14L1,5Q1,2 4,2Z" fill="#1e3a8a"/><path d="M33,11L39,26L39,35Q39,38 36,38L4,38Q1,38 1,35L1,26Z" fill="#00b4d8" opacity=".80"/></svg>
ShipZen
</a>
<div class="nav-actions">
<a href="#contact" class="btn-contact">Contact Sales</a>
<a href="#contact" class="btn-primary">Get Started</a>
</div>
</div>
</nav>

<!-- HERO -->
<section class="hero" id="top">
<div class="hero-bg"><canvas id="gradient-canvas"></canvas></div>
<div class="container">
<div class="hero-grid">
<div class="hero-left">
<div class="hero-tag"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Enterprise UPS Rates</div>
<h1>Stop overpaying for shipping labels.</h1>
<p class="hero-sub">Flat-rate UPS Ground labels across the lower 48 states.<br><strong>Save $1–$2 on average per shipping label.</strong></p>
<div class="hero-ctas">
<a href="#contact" class="btn-primary" style="padding:.7rem 1.75rem;font-size:.95rem">&#128230; Get Your Savings Quote</a>
<a href="#how-it-works" class="hero-link">See how it works <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg></a>
</div>
</div>
<div class="form-card" id="contact">
<div class="form-title">See how much you'd save</div>
<div class="form-sub">Get a custom savings quote in under 24 hours</div>
<form id="lead-form" class="fg" novalidate>
<div class="fi"><label>Email Address</label><input type="email" id="email" placeholder="you@yourstore.com" required></div>
<div class="fi"><label>Phone Number</label><input type="tel" id="phone" placeholder="(555) 123-4567"></div>
<div class="fi"><label>Store URL</label><input type="url" id="website" placeholder="yourstore.com"></div>
<div class="fi"><label>Monthly Shipments</label><select id="monthly_shipments"><option value="" disabled selected>Select estimate...</option><option value="1-100">1 – 100</option><option value="101-500">101 – 500</option><option value="501-1000">501 – 1,000</option><option value="1001-2500">1,001 – 2,500</option><option value="2500+">2,500+</option></select></div>
<div class="f-btns"><button type="submit" class="btn-submit" id="submit-btn">&#128230; Get Your Savings Quote</button></div>
<div class="form-trust">
<span>&#128274; No setup fees</span>
<span>&#10005; No contracts</span>
<span>&#8617; Cancel anytime</span>
</div>
<div class="form-msg" id="form-msg"></div>
</form>
</div>
</div>
</div>

</section>

<!-- STATS BAR -->
<section class="stats-section">
<div class="stats-inner">
<div class="stats-grid">
<div class="stat-item fade-in"><div class="stat-val">$1–$2</div><div class="stat-label">saved per label on average</div></div>
<div class="stat-item fade-in"><div class="stat-val">48</div><div class="stat-label">states with flat-rate coverage</div></div>
<div class="stat-item fade-in"><div class="stat-val">&lt;24<span class="stat-accent">hr</span></div><div class="stat-label">setup and integration time</div></div>
<div class="stat-item fade-in"><div class="stat-val">$0</div><div class="stat-label">hidden fees or monthly charges</div></div>
</div>
</div>
<div class="stats-logos">
<div class="logo-bar">
<div class="logo-bar-label">Trusted by sellers on</div>
<div class="logo-track">
<div class="logo-scroll">
<span><svg viewBox="0 0 60 40" aria-label="Shopify"><g transform="translate(12.5,0) scale(0.137)"><path d="M223.774 57.34c-.201-1.46-1.48-2.268-2.537-2.357-1.055-.088-23.383-1.743-23.383-1.743s-15.507-15.395-17.209-17.099c-1.703-1.703-5.029-1.185-6.32-.805-.19.056-3.388 1.043-8.678 2.68-5.18-14.906-14.322-28.604-30.405-28.604-.444 0-.901.018-1.358.044C129.31 3.407 123.644.779 118.75.779c-37.465 0-55.364 46.835-60.976 70.635-14.558 4.511-24.9 7.718-26.221 8.133-8.126 2.549-8.383 2.805-9.45 10.462C21.3 95.806.038 260.235.038 260.235l165.678 31.042 89.77-19.42S223.973 58.8 223.775 57.34z" fill="#95BF46"/><path d="M156.49 40.848l-14.019 4.339c.005-.988.01-1.96.01-3.023 0-9.264-1.286-16.723-3.349-22.636 8.287 1.04 13.806 10.469 17.358 21.32zm-27.638-19.483c2.304 5.773 3.802 14.058 3.802 25.238 0 .572-.005 1.095-.01 1.624-9.117 2.824-19.024 5.89-28.953 8.966 5.575-21.516 16.025-31.908 25.161-35.828zm-11.131-10.537c1.617 0 3.246.549 4.805 1.622-12.007 5.65-24.877 19.88-30.312 48.297l-22.886 7.088C75.694 46.16 90.81 10.828 117.72 10.828z" fill="#95BF46"/><path d="M221.237 54.983c-1.055-.088-23.383-1.743-23.383-1.743s-15.507-15.395-17.209-17.099c-.637-.634-1.496-.959-2.394-1.099l-12.527 256.233 89.762-19.418S223.972 58.8 223.774 57.34c-.201-1.46-1.48-2.268-2.537-2.357" fill="#5E8E3E"/><path d="M135.242 104.585l-11.069 32.926s-9.698-5.176-21.586-5.176c-17.428 0-18.305 10.937-18.305 13.693 0 15.038 39.2 20.8 39.2 56.024 0 27.713-17.577 45.558-41.277 45.558-28.44 0-42.984-17.7-42.984-17.7l7.615-25.16s14.95 12.835 27.565 12.835c8.243 0 11.596-6.49 11.596-11.232 0-19.616-32.16-20.491-32.16-52.724 0-27.129 19.472-53.382 58.778-53.382 15.145 0 22.627 4.338 22.627 4.338" fill="#FFF"/></g></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="WooCommerce"><g transform="translate(0,2.1) scale(0.234)"><path d="M23.759 0h208.378C245.325 0 256 10.675 256 23.863v79.541c0 13.188-10.675 23.863-23.863 23.863H157.41l10.257 25.118-45.109-25.118H23.863c-13.187 0-23.862-10.675-23.862-23.863V23.863C-.104 10.78 10.57 0 23.759 0z" fill="#9B5C8F"/><path d="M14.578 21.75c1.457-1.978 3.642-3.018 6.556-3.226 5.308-.417 8.326 2.08 9.054 7.492 3.226 21.75 6.764 40.17 10.51 55.259l22.79-43.395c2.082-3.955 4.684-6.036 7.806-6.244 4.579-.312 7.388 2.601 8.533 8.741 2.602 13.84 5.932 25.6 9.886 35.59 2.706-26.432 7.285-45.476 13.737-57.235 1.56-2.914 3.85-4.371 6.868-4.58 2.394-.207 4.579.521 6.556 2.082 1.977 1.561 3.018 3.538 3.226 5.932.104 1.873-.208 3.434-1.04 4.995-4.059 7.493-7.39 20.085-10.095 37.567-2.601 16.963-3.538 30.18-2.914 39.65.209 2.6-.208 4.89-1.248 6.868-1.25 2.289-3.122 3.538-5.516 3.746-2.706.208-5.515-1.04-8.221-3.85-9.678-9.887-17.379-24.664-22.998-44.332-6.765 13.32-11.76 23.31-14.986 29.97-6.14 11.76-11.343 17.796-15.714 18.108-2.81.208-5.203-2.186-7.284-7.18-5.307-13.633-11.031-39.962-17.17-78.986-.417-2.706.207-5.1 1.664-6.972zm223.636 16.338c-3.746-6.556-9.262-10.51-16.65-12.072-1.978-.416-3.85-.624-5.62-.624-9.99 0-18.107 5.203-24.455 15.61-5.412 8.845-8.117 18.627-8.117 29.346 0 8.013 1.665 14.881 4.995 20.605 3.746 6.556 9.262 10.51 16.65 12.071 1.977.417 3.85.625 5.62.625 10.094 0 18.211-5.203 24.455-15.61 5.411-8.95 8.117-18.732 8.117-29.45.104-8.117-1.665-14.882-4.995-20.501zm-13.112 28.826c-1.457 6.868-4.059 11.967-7.91 15.401-3.017 2.706-5.827 3.85-8.428 3.33-2.498-.52-4.58-2.705-6.14-6.764-1.25-3.226-1.873-6.452-1.873-9.47 0-2.601.208-5.203.728-7.596.937-4.267 2.706-8.43 5.515-12.384 3.435-5.1 7.077-7.18 10.823-6.452 2.498.52 4.58 2.706 6.14 6.764 1.249 3.226 1.873 6.452 1.873 9.47 0 2.706-.208 5.307-.728 7.7zm-52.033-28.826c-3.746-6.556-9.366-10.51-16.65-12.072-1.977-.416-3.85-.624-5.62-.624-9.99 0-18.107 5.203-24.455 15.61-5.411 8.845-8.117 18.627-8.117 29.346 0 8.013 1.665 14.881 4.995 20.605 3.746 6.556 9.262 10.51 16.65 12.071 1.978.417 3.85.625 5.62.625 10.094 0 18.211-5.203 24.455-15.61 5.412-8.95 8.117-18.732 8.117-29.45 0-8.117-1.665-14.882-4.995-20.501zm-13.216 28.826c-1.457 6.868-4.059 11.967-7.909 15.401-3.018 2.706-5.828 3.85-8.43 3.33-2.497-.52-4.578-2.705-6.14-6.764-1.248-3.226-1.872-6.452-1.872-9.47 0-2.601.208-5.203.728-7.596.937-4.267 2.706-8.43 5.516-12.384 3.434-5.1 7.076-7.18 10.822-6.452 2.498.52 4.58 2.706 6.14 6.764 1.25 3.226 1.873 6.452 1.873 9.47.105 2.706-.208 5.307-.728 7.7z" fill="#FFF"/></g></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="BigCommerce"><g transform="translate(10,0) scale(1.667)"><path d="M12.645 13.663h3.027c.861 0 1.406-.474 1.406-1.235 0-.717-.545-1.234-1.406-1.234h-3.027c-.1 0-.187.086-.187.172v2.125c.015.1.086.172.187.172zm0 4.896h3.128c.961 0 1.535-.488 1.535-1.35 0-.746-.545-1.35-1.535-1.35h-3.128c-.1 0-.187.087-.187.173v2.34c.015.115.086.187.187.187zM23.72.053l-8.953 8.93h1.464c2.281 0 3.63 1.435 3.63 3 0 1.235-.832 2.14-1.722 2.541-.143.058-.143.259.014.316 1.033.402 1.765 1.48 1.765 2.742 0 1.78-1.19 3.202-3.5 3.202h-6.342c-.1 0-.187-.086-.187-.172V13.85L.062 23.64c-.13.13-.043.359.143.359h23.631a.16.16 0 0 0 .158-.158V.182c.043-.158-.158-.244-.273-.13z" fill="#34313F"/></g></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="Etsy"><g transform="translate(-12.8,-1.75) scale(0.177)"><path d="M108.783 100.639V55.192c0-1.684.168-2.694 3.031-2.694h38.545c6.734 0 10.437 5.724 13.131 16.496l2.188 8.586h6.564c1.177-24.406 2.186-35.011 2.186-35.011s-16.495 1.851-26.258 1.851H98.854l-26.431-.842v7.07l8.923 1.683c6.228 1.179 7.74 2.524 8.249 8.249 0 0 .506 16.832.506 44.607 0 27.771-.506 44.437-.506 44.437 0 5.049-2.021 6.9-8.249 8.082l-8.923 1.684v7.066l26.431-.84h44.101c9.931 0 32.991.84 32.991.84.503-6.061 3.872-33.498 4.377-36.524h-6.228l-6.565 14.981c-5.219 11.78-12.792 12.623-21.21 12.623h-25.082c-8.417 0-12.457-3.367-12.457-10.604v-38.379s18.347 0 24.742.506c4.714.338 7.574 1.684 9.091 8.248l2.021 8.753h7.234l-.503-22.053 1.009-22.217h-7.236l-2.355 9.762c-1.517 6.396-2.525 7.577-9.091 8.248-7.405.844-24.913.675-24.913.675v.167h.003v-.003z" fill="#F56400"/></g></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="Amazon"><text x="5" y="19" font-family="Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="-0.5" fill="#232F3E">amazon</text><path d="M 7 24 Q 30 33 52 24" stroke="#FF9900" stroke-width="2.5" fill="none" stroke-linecap="round"/><path d="M 48 22 L 52 24 L 50 28" stroke="#FF9900" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="eBay"><text x="4" y="28" font-family="Arial,sans-serif" font-size="22" font-weight="700"><tspan fill="#E53238">e</tspan><tspan fill="#0064D2">B</tspan><tspan fill="#F5AF02">a</tspan><tspan fill="#86B817">y</tspan></text></svg></span>

<!-- duplicate set for seamless loop -->
<span><svg viewBox="0 0 60 40" aria-label="Shopify"><g transform="translate(12.5,0) scale(0.137)"><path d="M223.774 57.34c-.201-1.46-1.48-2.268-2.537-2.357-1.055-.088-23.383-1.743-23.383-1.743s-15.507-15.395-17.209-17.099c-1.703-1.703-5.029-1.185-6.32-.805-.19.056-3.388 1.043-8.678 2.68-5.18-14.906-14.322-28.604-30.405-28.604-.444 0-.901.018-1.358.044C129.31 3.407 123.644.779 118.75.779c-37.465 0-55.364 46.835-60.976 70.635-14.558 4.511-24.9 7.718-26.221 8.133-8.126 2.549-8.383 2.805-9.45 10.462C21.3 95.806.038 260.235.038 260.235l165.678 31.042 89.77-19.42S223.973 58.8 223.775 57.34z" fill="#95BF46"/><path d="M156.49 40.848l-14.019 4.339c.005-.988.01-1.96.01-3.023 0-9.264-1.286-16.723-3.349-22.636 8.287 1.04 13.806 10.469 17.358 21.32zm-27.638-19.483c2.304 5.773 3.802 14.058 3.802 25.238 0 .572-.005 1.095-.01 1.624-9.117 2.824-19.024 5.89-28.953 8.966 5.575-21.516 16.025-31.908 25.161-35.828zm-11.131-10.537c1.617 0 3.246.549 4.805 1.622-12.007 5.65-24.877 19.88-30.312 48.297l-22.886 7.088C75.694 46.16 90.81 10.828 117.72 10.828z" fill="#95BF46"/><path d="M221.237 54.983c-1.055-.088-23.383-1.743-23.383-1.743s-15.507-15.395-17.209-17.099c-.637-.634-1.496-.959-2.394-1.099l-12.527 256.233 89.762-19.418S223.972 58.8 223.774 57.34c-.201-1.46-1.48-2.268-2.537-2.357" fill="#5E8E3E"/><path d="M135.242 104.585l-11.069 32.926s-9.698-5.176-21.586-5.176c-17.428 0-18.305 10.937-18.305 13.693 0 15.038 39.2 20.8 39.2 56.024 0 27.713-17.577 45.558-41.277 45.558-28.44 0-42.984-17.7-42.984-17.7l7.615-25.16s14.95 12.835 27.565 12.835c8.243 0 11.596-6.49 11.596-11.232 0-19.616-32.16-20.491-32.16-52.724 0-27.129 19.472-53.382 58.778-53.382 15.145 0 22.627 4.338 22.627 4.338" fill="#FFF"/></g></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="WooCommerce"><g transform="translate(0,2.1) scale(0.234)"><path d="M23.759 0h208.378C245.325 0 256 10.675 256 23.863v79.541c0 13.188-10.675 23.863-23.863 23.863H157.41l10.257 25.118-45.109-25.118H23.863c-13.187 0-23.862-10.675-23.862-23.863V23.863C-.104 10.78 10.57 0 23.759 0z" fill="#9B5C8F"/><path d="M14.578 21.75c1.457-1.978 3.642-3.018 6.556-3.226 5.308-.417 8.326 2.08 9.054 7.492 3.226 21.75 6.764 40.17 10.51 55.259l22.79-43.395c2.082-3.955 4.684-6.036 7.806-6.244 4.579-.312 7.388 2.601 8.533 8.741 2.602 13.84 5.932 25.6 9.886 35.59 2.706-26.432 7.285-45.476 13.737-57.235 1.56-2.914 3.85-4.371 6.868-4.58 2.394-.207 4.579.521 6.556 2.082 1.977 1.561 3.018 3.538 3.226 5.932.104 1.873-.208 3.434-1.04 4.995-4.059 7.493-7.39 20.085-10.095 37.567-2.601 16.963-3.538 30.18-2.914 39.65.209 2.6-.208 4.89-1.248 6.868-1.25 2.289-3.122 3.538-5.516 3.746-2.706.208-5.515-1.04-8.221-3.85-9.678-9.887-17.379-24.664-22.998-44.332-6.765 13.32-11.76 23.31-14.986 29.97-6.14 11.76-11.343 17.796-15.714 18.108-2.81.208-5.203-2.186-7.284-7.18-5.307-13.633-11.031-39.962-17.17-78.986-.417-2.706.207-5.1 1.664-6.972z" fill="#FFF"/></g></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="BigCommerce"><g transform="translate(10,0) scale(1.667)"><path d="M12.645 13.663h3.027c.861 0 1.406-.474 1.406-1.235 0-.717-.545-1.234-1.406-1.234h-3.027c-.1 0-.187.086-.187.172v2.125c.015.1.086.172.187.172zm0 4.896h3.128c.961 0 1.535-.488 1.535-1.35 0-.746-.545-1.35-1.535-1.35h-3.128c-.1 0-.187.087-.187.173v2.34c.015.115.086.187.187.187zM23.72.053l-8.953 8.93h1.464c2.281 0 3.63 1.435 3.63 3 0 1.235-.832 2.14-1.722 2.541-.143.058-.143.259.014.316 1.033.402 1.765 1.48 1.765 2.742 0 1.78-1.19 3.202-3.5 3.202h-6.342c-.1 0-.187-.086-.187-.172V13.85L.062 23.64c-.13.13-.043.359.143.359h23.631a.16.16 0 0 0 .158-.158V.182c.043-.158-.158-.244-.273-.13z" fill="#34313F"/></g></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="Etsy"><g transform="translate(-12.8,-1.75) scale(0.177)"><path d="M108.783 100.639V55.192c0-1.684.168-2.694 3.031-2.694h38.545c6.734 0 10.437 5.724 13.131 16.496l2.188 8.586h6.564c1.177-24.406 2.186-35.011 2.186-35.011s-16.495 1.851-26.258 1.851H98.854l-26.431-.842v7.07l8.923 1.683c6.228 1.179 7.74 2.524 8.249 8.249 0 0 .506 16.832.506 44.607 0 27.771-.506 44.437-.506 44.437 0 5.049-2.021 6.9-8.249 8.082l-8.923 1.684v7.066l26.431-.84h44.101c9.931 0 32.991.84 32.991.84.503-6.061 3.872-33.498 4.377-36.524h-6.228l-6.565 14.981c-5.219 11.78-12.792 12.623-21.21 12.623h-25.082c-8.417 0-12.457-3.367-12.457-10.604v-38.379s18.347 0 24.742.506c4.714.338 7.574 1.684 9.091 8.248l2.021 8.753h7.234l-.503-22.053 1.009-22.217h-7.236l-2.355 9.762c-1.517 6.396-2.525 7.577-9.091 8.248-7.405.844-24.913.675-24.913.675v.167h.003v-.003z" fill="#F56400"/></g></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="Amazon"><text x="5" y="19" font-family="Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="-0.5" fill="#232F3E">amazon</text><path d="M 7 24 Q 30 33 52 24" stroke="#FF9900" stroke-width="2.5" fill="none" stroke-linecap="round"/><path d="M 48 22 L 52 24 L 50 28" stroke="#FF9900" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
<span><svg viewBox="0 0 60 40" aria-label="eBay"><text x="4" y="28" font-family="Arial,sans-serif" font-size="22" font-weight="700"><tspan fill="#E53238">e</tspan><tspan fill="#0064D2">B</tspan><tspan fill="#F5AF02">a</tspan><tspan fill="#86B817">y</tspan></text></svg></span>

</div>
</div>
</div>
</section>

<!-- ENTERPRISE CARDS -->
<section class="ent-section">
<div class="container">
<p class="sl c">Why ShipZen</p>
<h2 class="st c">Enterprise shipping rates without enterprise commitments</h2>
<div style="height:2rem"></div>
<div class="ent-grid">
<div class="ent-card fade-in">
<div class="ent-head">
<h3>Save $1–$2 on average per shipping label</h3>
<div class="ent-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
</div>
<div class="ent-visual"><canvas id="ent-cv-1"></canvas></div>
</div>
<div class="ent-card fade-in">
<div class="ent-head">
<h3>Ship anywhere across<br>all 48 states</h3>
<div class="ent-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></div>
</div>
<div class="ent-visual"><canvas id="ent-cv-2"></canvas></div>
</div>
<div class="ent-card fade-in">
<div class="ent-head">
<h3>No hidden zone fees or dimensional weight charges</h3>
<div class="ent-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div>
</div>
<div class="ent-visual"><canvas id="ent-cv-3"></canvas></div>
</div>
</div>
</div>
</section>

<!-- HOW IT WORKS -->
<section class="hiw-section" id="how-it-works">
<div class="container">
<p class="sl c">How It Works</p>
<h2 class="st c">Three things that make our rates unbeatable</h2>
<p class="sd c">It&rsquo;s not a workaround or a loophole. It&rsquo;s how enterprise logistics pricing has always worked.</p>
<div class="hiw-grid">
<div class="hiw-card fade-in">
<div class="hiw-head">
<h3>We optimize your lanes</h3>
<div class="hiw-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></div>
</div>
<div class="hiw-body">
<p class="hiw-desc">Your shipments get consolidated into predictable, high-frequency routes. UPS builds our volume directly into daily truck schedules, eliminating wasted miles and empty trucks.</p>
<div class="hiw-result"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Lower per-package cost</div>
</div>
</div>
<div class="hiw-card fade-in">
<div class="hiw-head">
<h3>We validate every address</h3>
<div class="hiw-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div>
</div>
<div class="hiw-body">
<p class="hiw-desc">Every address is verified and standardized before a label prints. No correction fees, no failed deliveries, no surprise surcharges. Clean data means lower cost-to-serve.</p>
<div class="hiw-result"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Zero hidden fees</div>
</div>
</div>
<div class="hiw-card fade-in">
<div class="hiw-head">
<h3>We commit 100% to UPS</h3>
<div class="hiw-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
</div>
<div class="hiw-body">
<p class="hiw-desc">No multi-carrier rate-shopping. Our long-term, dedicated UPS Ground commitment gives them the certainty they need to unlock enterprise pricing that aggregators can never access.</p>
<div class="hiw-result"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Enterprise-tier rates</div>
</div>
</div>
</div>
</div>
</section>

<!-- COMPARISON TABLE -->
<section class="cmp-section">
<div class="container">
<p class="sl c">See The Difference</p>
<h2 class="st c">Why our rates beat going direct</h2>
<p class="sd c">Shipping directly through UPS or USPS means paying retail rates with added surcharges. Even aggregators can&rsquo;t unlock the lowest pricing tiers.</p>
<div class="cmp-table fade-in">
<table>
<thead>
<tr>
<th></th>
<th class="hl">ShipZen</th>
<th>Aggregators<span class="sub">Pirate Ship, EasyShip</span></th>
<th>UPS / USPS Direct<span class="sub">Retail rates</span></th>
</tr>
</thead>
<tbody>
<tr><td>Base Rate</td><td class="hl">Enterprise contract pricing</td><td>Discounted, but standard commercial</td><td>Published retail &mdash; highest tier</td></tr>
<tr><td>Zone Surcharges</td><td class="hl">Flat rate &mdash; no zone fees</td><td>Reduced but still applied</td><td>$2&ndash;$8+ per package on long zones</td></tr>
<tr><td>Fuel Surcharge</td><td class="hl">Already included in our rates</td><td>Passed through to seller</td><td>6&ndash;8% added to every shipment</td></tr>
<tr><td>DIM Weight Pricing</td><td class="hl">No dimensional weight charges</td><td>Applied on most packages</td><td>Applied on all packages &gt;1 cu ft</td></tr>
<tr><td>Residential Fees</td><td class="hl">No residential surcharges</td><td>$2&ndash;$4 per delivery</td><td>$4&ndash;$6 per residential delivery</td></tr>
<tr><td>Volume Discounts</td><td class="hl">Enterprise rates from label one</td><td>Pooled volume &mdash; limited tiers</td><td>Requires 500+ pkgs/week minimum</td></tr>
<tr><td>Cost per Label</td><td class="hl" style="font-weight:700;color:var(--accent)">$4&ndash;$8 average</td><td style="font-weight:600;color:#dc2626">$7&ndash;$10+ average</td><td style="font-weight:600;color:#dc2626">$9&ndash;$14+ average</td></tr>
</tbody>
</table>
</div>
</div>
</section>

<!-- FEATURES DETAIL -->
<section class="feat-section" id="features">
<div class="container">
<p class="sl c">Integrations</p>
<h2 class="st c">Guaranteed lowest UPS Ground rates for e-commerce sellers</h2>
<p class="sd c">Keep more profit with enterprise contract rates &mdash; no minimums, no hidden fees.</p>
<div class="feat-card fade-in">
<h3>Integrates seamlessly with the platforms you already use</h3>
<div class="integ-track">
<div class="integ-scroll">

<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="Shopify"><g transform="translate(12.5,0) scale(0.137)"><path d="M223.774 57.34c-.201-1.46-1.48-2.268-2.537-2.357-1.055-.088-23.383-1.743-23.383-1.743s-15.507-15.395-17.209-17.099c-1.703-1.703-5.029-1.185-6.32-.805-.19.056-3.388 1.043-8.678 2.68-5.18-14.906-14.322-28.604-30.405-28.604-.444 0-.901.018-1.358.044C129.31 3.407 123.644.779 118.75.779c-37.465 0-55.364 46.835-60.976 70.635-14.558 4.511-24.9 7.718-26.221 8.133-8.126 2.549-8.383 2.805-9.45 10.462C21.3 95.806.038 260.235.038 260.235l165.678 31.042 89.77-19.42S223.973 58.8 223.775 57.34z" fill="#95BF46"/><path d="M156.49 40.848l-14.019 4.339c.005-.988.01-1.96.01-3.023 0-9.264-1.286-16.723-3.349-22.636 8.287 1.04 13.806 10.469 17.358 21.32zm-27.638-19.483c2.304 5.773 3.802 14.058 3.802 25.238 0 .572-.005 1.095-.01 1.624-9.117 2.824-19.024 5.89-28.953 8.966 5.575-21.516 16.025-31.908 25.161-35.828zm-11.131-10.537c1.617 0 3.246.549 4.805 1.622-12.007 5.65-24.877 19.88-30.312 48.297l-22.886 7.088C75.694 46.16 90.81 10.828 117.72 10.828z" fill="#95BF46"/><path d="M221.237 54.983c-1.055-.088-23.383-1.743-23.383-1.743s-15.507-15.395-17.209-17.099c-.637-.634-1.496-.959-2.394-1.099l-12.527 256.233 89.762-19.418S223.972 58.8 223.774 57.34c-.201-1.46-1.48-2.268-2.537-2.357" fill="#5E8E3E"/><path d="M135.242 104.585l-11.069 32.926s-9.698-5.176-21.586-5.176c-17.428 0-18.305 10.937-18.305 13.693 0 15.038 39.2 20.8 39.2 56.024 0 27.713-17.577 45.558-41.277 45.558-28.44 0-42.984-17.7-42.984-17.7l7.615-25.16s14.95 12.835 27.565 12.835c8.243 0 11.596-6.49 11.596-11.232 0-19.616-32.16-20.491-32.16-52.724 0-27.129 19.472-53.382 58.778-53.382 15.145 0 22.627 4.338 22.627 4.338" fill="#FFF"/></g></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="WooCommerce"><g transform="translate(0,2.1) scale(0.234)"><path d="M23.759 0h208.378C245.325 0 256 10.675 256 23.863v79.541c0 13.188-10.675 23.863-23.863 23.863H157.41l10.257 25.118-45.109-25.118H23.863c-13.187 0-23.862-10.675-23.862-23.863V23.863C-.104 10.78 10.57 0 23.759 0z" fill="#9B5C8F"/><path d="M14.578 21.75c1.457-1.978 3.642-3.018 6.556-3.226 5.308-.417 8.326 2.08 9.054 7.492 3.226 21.75 6.764 40.17 10.51 55.259l22.79-43.395c2.082-3.955 4.684-6.036 7.806-6.244 4.579-.312 7.388 2.601 8.533 8.741 2.602 13.84 5.932 25.6 9.886 35.59 2.706-26.432 7.285-45.476 13.737-57.235 1.56-2.914 3.85-4.371 6.868-4.58 2.394-.207 4.579.521 6.556 2.082 1.977 1.561 3.018 3.538 3.226 5.932.104 1.873-.208 3.434-1.04 4.995-4.059 7.493-7.39 20.085-10.095 37.567-2.601 16.963-3.538 30.18-2.914 39.65.209 2.6-.208 4.89-1.248 6.868-1.25 2.289-3.122 3.538-5.516 3.746-2.706.208-5.515-1.04-8.221-3.85-9.678-9.887-17.379-24.664-22.998-44.332-6.765 13.32-11.76 23.31-14.986 29.97-6.14 11.76-11.343 17.796-15.714 18.108-2.81.208-5.203-2.186-7.284-7.18-5.307-13.633-11.031-39.962-17.17-78.986-.417-2.706.207-5.1 1.664-6.972z" fill="#FFF"/></g></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="BigCommerce"><g transform="translate(10,0) scale(1.667)"><path d="M12.645 13.663h3.027c.861 0 1.406-.474 1.406-1.235 0-.717-.545-1.234-1.406-1.234h-3.027c-.1 0-.187.086-.187.172v2.125c.015.1.086.172.187.172zm0 4.896h3.128c.961 0 1.535-.488 1.535-1.35 0-.746-.545-1.35-1.535-1.35h-3.128c-.1 0-.187.087-.187.173v2.34c.015.115.086.187.187.187zM23.72.053l-8.953 8.93h1.464c2.281 0 3.63 1.435 3.63 3 0 1.235-.832 2.14-1.722 2.541-.143.058-.143.259.014.316 1.033.402 1.765 1.48 1.765 2.742 0 1.78-1.19 3.202-3.5 3.202h-6.342c-.1 0-.187-.086-.187-.172V13.85L.062 23.64c-.13.13-.043.359.143.359h23.631a.16.16 0 0 0 .158-.158V.182c.043-.158-.158-.244-.273-.13z" fill="#34313F"/></g></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="Etsy"><g transform="translate(-12.8,-1.75) scale(0.177)"><path d="M108.783 100.639V55.192c0-1.684.168-2.694 3.031-2.694h38.545c6.734 0 10.437 5.724 13.131 16.496l2.188 8.586h6.564c1.177-24.406 2.186-35.011 2.186-35.011s-16.495 1.851-26.258 1.851H98.854l-26.431-.842v7.07l8.923 1.683c6.228 1.179 7.74 2.524 8.249 8.249 0 0 .506 16.832.506 44.607 0 27.771-.506 44.437-.506 44.437 0 5.049-2.021 6.9-8.249 8.082l-8.923 1.684v7.066l26.431-.84h44.101c9.931 0 32.991.84 32.991.84.503-6.061 3.872-33.498 4.377-36.524h-6.228l-6.565 14.981c-5.219 11.78-12.792 12.623-21.21 12.623h-25.082c-8.417 0-12.457-3.367-12.457-10.604v-38.379s18.347 0 24.742.506c4.714.338 7.574 1.684 9.091 8.248l2.021 8.753h7.234l-.503-22.053 1.009-22.217h-7.236l-2.355 9.762c-1.517 6.396-2.525 7.577-9.091 8.248-7.405.844-24.913.675-24.913.675v.167h.003v-.003z" fill="#F56400"/></g></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="Amazon"><text x="5" y="19" font-family="Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="-0.5" fill="#232F3E">amazon</text><path d="M 7 24 Q 30 33 52 24" stroke="#FF9900" stroke-width="2.5" fill="none" stroke-linecap="round"/><path d="M 48 22 L 52 24 L 50 28" stroke="#FF9900" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="eBay"><text x="4" y="28" font-family="Arial,sans-serif" font-size="22" font-weight="700"><tspan fill="#E53238">e</tspan><tspan fill="#0064D2">B</tspan><tspan fill="#F5AF02">a</tspan><tspan fill="#86B817">y</tspan></text></svg></div>
<!-- duplicate for seamless loop -->

<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="Shopify"><g transform="translate(12.5,0) scale(0.137)"><path d="M223.774 57.34c-.201-1.46-1.48-2.268-2.537-2.357-1.055-.088-23.383-1.743-23.383-1.743s-15.507-15.395-17.209-17.099c-1.703-1.703-5.029-1.185-6.32-.805-.19.056-3.388 1.043-8.678 2.68-5.18-14.906-14.322-28.604-30.405-28.604-.444 0-.901.018-1.358.044C129.31 3.407 123.644.779 118.75.779c-37.465 0-55.364 46.835-60.976 70.635-14.558 4.511-24.9 7.718-26.221 8.133-8.126 2.549-8.383 2.805-9.45 10.462C21.3 95.806.038 260.235.038 260.235l165.678 31.042 89.77-19.42S223.973 58.8 223.775 57.34z" fill="#95BF46"/><path d="M156.49 40.848l-14.019 4.339c.005-.988.01-1.96.01-3.023 0-9.264-1.286-16.723-3.349-22.636 8.287 1.04 13.806 10.469 17.358 21.32zm-27.638-19.483c2.304 5.773 3.802 14.058 3.802 25.238 0 .572-.005 1.095-.01 1.624-9.117 2.824-19.024 5.89-28.953 8.966 5.575-21.516 16.025-31.908 25.161-35.828zm-11.131-10.537c1.617 0 3.246.549 4.805 1.622-12.007 5.65-24.877 19.88-30.312 48.297l-22.886 7.088C75.694 46.16 90.81 10.828 117.72 10.828z" fill="#95BF46"/><path d="M221.237 54.983c-1.055-.088-23.383-1.743-23.383-1.743s-15.507-15.395-17.209-17.099c-.637-.634-1.496-.959-2.394-1.099l-12.527 256.233 89.762-19.418S223.972 58.8 223.774 57.34c-.201-1.46-1.48-2.268-2.537-2.357" fill="#5E8E3E"/><path d="M135.242 104.585l-11.069 32.926s-9.698-5.176-21.586-5.176c-17.428 0-18.305 10.937-18.305 13.693 0 15.038 39.2 20.8 39.2 56.024 0 27.713-17.577 45.558-41.277 45.558-28.44 0-42.984-17.7-42.984-17.7l7.615-25.16s14.95 12.835 27.565 12.835c8.243 0 11.596-6.49 11.596-11.232 0-19.616-32.16-20.491-32.16-52.724 0-27.129 19.472-53.382 58.778-53.382 15.145 0 22.627 4.338 22.627 4.338" fill="#FFF"/></g></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="WooCommerce"><g transform="translate(0,2.1) scale(0.234)"><path d="M23.759 0h208.378C245.325 0 256 10.675 256 23.863v79.541c0 13.188-10.675 23.863-23.863 23.863H157.41l10.257 25.118-45.109-25.118H23.863c-13.187 0-23.862-10.675-23.862-23.863V23.863C-.104 10.78 10.57 0 23.759 0z" fill="#9B5C8F"/><path d="M14.578 21.75c1.457-1.978 3.642-3.018 6.556-3.226 5.308-.417 8.326 2.08 9.054 7.492 3.226 21.75 6.764 40.17 10.51 55.259l22.79-43.395c2.082-3.955 4.684-6.036 7.806-6.244 4.579-.312 7.388 2.601 8.533 8.741 2.602 13.84 5.932 25.6 9.886 35.59 2.706-26.432 7.285-45.476 13.737-57.235 1.56-2.914 3.85-4.371 6.868-4.58 2.394-.207 4.579.521 6.556 2.082 1.977 1.561 3.018 3.538 3.226 5.932.104 1.873-.208 3.434-1.04 4.995-4.059 7.493-7.39 20.085-10.095 37.567-2.601 16.963-3.538 30.18-2.914 39.65.209 2.6-.208 4.89-1.248 6.868-1.25 2.289-3.122 3.538-5.516 3.746-2.706.208-5.515-1.04-8.221-3.85-9.678-9.887-17.379-24.664-22.998-44.332-6.765 13.32-11.76 23.31-14.986 29.97-6.14 11.76-11.343 17.796-15.714 18.108-2.81.208-5.203-2.186-7.284-7.18-5.307-13.633-11.031-39.962-17.17-78.986-.417-2.706.207-5.1 1.664-6.972z" fill="#FFF"/></g></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="BigCommerce"><g transform="translate(10,0) scale(1.667)"><path d="M12.645 13.663h3.027c.861 0 1.406-.474 1.406-1.235 0-.717-.545-1.234-1.406-1.234h-3.027c-.1 0-.187.086-.187.172v2.125c.015.1.086.172.187.172zm0 4.896h3.128c.961 0 1.535-.488 1.535-1.35 0-.746-.545-1.35-1.535-1.35h-3.128c-.1 0-.187.087-.187.173v2.34c.015.115.086.187.187.187zM23.72.053l-8.953 8.93h1.464c2.281 0 3.63 1.435 3.63 3 0 1.235-.832 2.14-1.722 2.541-.143.058-.143.259.014.316 1.033.402 1.765 1.48 1.765 2.742 0 1.78-1.19 3.202-3.5 3.202h-6.342c-.1 0-.187-.086-.187-.172V13.85L.062 23.64c-.13.13-.043.359.143.359h23.631a.16.16 0 0 0 .158-.158V.182c.043-.158-.158-.244-.273-.13z" fill="#34313F"/></g></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="Etsy"><g transform="translate(-12.8,-1.75) scale(0.177)"><path d="M108.783 100.639V55.192c0-1.684.168-2.694 3.031-2.694h38.545c6.734 0 10.437 5.724 13.131 16.496l2.188 8.586h6.564c1.177-24.406 2.186-35.011 2.186-35.011s-16.495 1.851-26.258 1.851H98.854l-26.431-.842v7.07l8.923 1.683c6.228 1.179 7.74 2.524 8.249 8.249 0 0 .506 16.832.506 44.607 0 27.771-.506 44.437-.506 44.437 0 5.049-2.021 6.9-8.249 8.082l-8.923 1.684v7.066l26.431-.84h44.101c9.931 0 32.991.84 32.991.84.503-6.061 3.872-33.498 4.377-36.524h-6.228l-6.565 14.981c-5.219 11.78-12.792 12.623-21.21 12.623h-25.082c-8.417 0-12.457-3.367-12.457-10.604v-38.379s18.347 0 24.742.506c4.714.338 7.574 1.684 9.091 8.248l2.021 8.753h7.234l-.503-22.053 1.009-22.217h-7.236l-2.355 9.762c-1.517 6.396-2.525 7.577-9.091 8.248-7.405.844-24.913.675-24.913.675v.167h.003v-.003z" fill="#F56400"/></g></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="Amazon"><text x="5" y="19" font-family="Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="-0.5" fill="#232F3E">amazon</text><path d="M 7 24 Q 30 33 52 24" stroke="#FF9900" stroke-width="2.5" fill="none" stroke-linecap="round"/><path d="M 48 22 L 52 24 L 50 28" stroke="#FF9900" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
<div class="integ-icon"><svg viewBox="0 0 60 40" aria-label="eBay"><text x="4" y="28" font-family="Arial,sans-serif" font-size="22" font-weight="700"><tspan fill="#E53238">e</tspan><tspan fill="#0064D2">B</tspan><tspan fill="#F5AF02">a</tspan><tspan fill="#86B817">y</tspan></text></svg></div>
</div>
</div>
<p class="feat-desc">Connect ShipZen to your existing e-commerce stack in minutes. Works with Shopify, WooCommerce, BigCommerce, Etsy, Amazon, eBay, and custom integrations via API &mdash; no monthly fees, flat-rate pricing on every label.</p>
</div>
</div>
</section>

<!-- TESTIMONIAL -->
<section class="test-section">
<div class="container">
<p class="sl c">What Sellers Say</p>
<h2 class="st c">Trusted by e-commerce businesses</h2>
<div style="height:1.5rem"></div>
<div class="test-card fade-in">
<div class="test-quote">We switched from Pirate Ship and immediately saw the difference. The flat-rate pricing simplified everything and we're saving more on every shipment. Setup took less than a day.</div>
<div class="test-author">E-Commerce Store Owner</div>
<div class="test-role">500+ shipments/month</div>
</div>
</div>
</section>

<!-- FAQ -->
<section class="faq-section" id="faq">
<div class="container">
<p class="sl c">FAQs</p>
<h2 class="st c">Everything you need to know</h2>
<p class="sd c">Common questions about ShipZen and discounted shipping labels.</p>
<div class="faq-wrap">
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">How does ShipZen offer such low shipping rates?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">ShipZen operates under a direct enterprise-level UPS Ground agreement. We consolidate shipments into predictable, high-frequency lanes so UPS can plan trucks and routes around our volume. We also validate every address before printing, which eliminates correction fees. This combination of lane optimization, clean data, and committed volume qualifies us for enterprise pricing that aggregator platforms simply cannot access.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">How is ShipZen different from Pirate Ship, EasyShip, or other aggregators?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">Aggregators pool thousands of unrelated sellers onto a shared account. The result is &ldquo;noisy&rdquo; volume &mdash; random origins, random destinations, no repeat patterns. UPS can&rsquo;t optimize routes around that, so the pricing reflects the uncertainty. ShipZen is the opposite: dedicated UPS commitment, predictable lanes, and validated data &mdash; which unlocks enterprise-tier pricing.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">How is ShipZen different from 3PLs like ShipStation or ShipHero?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">3PLs handle fragmented volume from thousands of businesses with different packaging, destinations, and timing. They&rsquo;re also structured for multi-carrier flexibility &mdash; optimizing across UPS, FedEx, and USPS simultaneously &mdash; so no single carrier relationship is deep enough for enterprise pricing. ShipZen focuses exclusively on UPS Ground with lane-optimized routes.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">Why can&rsquo;t aggregators or 3PLs match our rates?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">Enterprise pricing tiers require predictable volume, consistent Ground usage, and repeat lanes. Aggregators can&rsquo;t provide that because their volume is inherently unpredictable. 3PLs can&rsquo;t either because their business model is built around variety and multi-carrier flexibility. ShipZen is structured around the exact behaviors UPS incentivizes.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">What shipping services does ShipZen support?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">ShipZen offers UPS Ground service across the lower 48 states with flat-rate pricing. Our intentional focus on a single carrier and service is what allows us to offer enterprise-tier rates.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">What are the weight limits for flat-rate pricing?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">Our flat-rate pricing applies to standard UPS Ground-eligible shipments across a broad weight range &mdash; not just lighter packages. Pricing is organized into weight-based tiers, so your rate is determined by which tier your package falls into, not by the specific destination ZIP code within the lower 48 states.<br><br>This means you get the same predictable, flat rate whether you&rsquo;re shipping to California or Connecticut &mdash; and the savings compared to platforms like Pirate Ship, EasyShip, or ShipStation apply across weight classes, not just for small, light packages.<br><br><strong>Note:</strong> Shipments to Alaska, Hawaii, U.S. territories, PO Boxes, and certain remote ZIP codes fall outside our standard flat-rate structure.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">Are there any monthly fees or minimums?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">No monthly fees, no volume commitments, no minimums. You pay per label, that&rsquo;s it. Cancel anytime.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">What e-commerce platforms does ShipZen integrate with?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">ShipZen works with Shopify, WooCommerce, BigCommerce, Etsy, Amazon, eBay, and offers API access for custom integrations. Most merchants go live within 24 hours.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">What about zone fees or dimensional weight charges?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">None. Our flat-rate pricing is possible because lane optimization averages out distance costs across our network, and address validation removes the hidden fees and risk premiums that make flat rates too risky for aggregator platforms.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">Can I see real savings examples?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">Absolutely. Across hundreds or thousands of shipments per month, the per-package savings add up to a meaningful difference in your bottom line. Request a custom quote to see your exact savings.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">How quickly can I start using ShipZen?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">Most merchants can integrate and start printing labels within 24 hours. Just connect your store and start saving immediately.</div></div></div>
<div class="faq-item"><button class="faq-q" onclick="tFaq(this)">Is there a contract or cancellation fee?<svg class="faq-chevron" viewBox="0 0 20 20" fill="none"><path d="M5 7.5l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="faq-ans"><div class="faq-ans-inner">No contracts, no cancellation fees. Use ShipZen as much or as little as you want. Cancel anytime.</div></div></div>
</div>
</div>
</section>

<!-- CTA BANNER -->
<section class="cta-section">
<div class="container">
<div class="cta-inner fade-in">
<h2>Start saving on every shipment today.</h2>
<p>You&rsquo;re still shipping UPS Ground with full tracking and the same delivery network. The only thing that changes is what you pay.</p>
<div class="cta-buttons">
<a href="#contact" class="btn-cta-w">Get Your Savings Quote</a>
<a href="#how-it-works" class="btn-cta-ghost">Learn How It Works</a>
</div>
</div>
</div>
</section>

<!-- FOOTER -->
<footer class="footer">
<div class="container">
<div class="footer-grid">
<div>
<div class="footer-brand">
<svg width="22" height="22" viewBox="0 0 40 40" fill="none"><path d="M4,2L36,2Q39,2 39,5L39,14L7,29L1,14L1,5Q1,2 4,2Z" fill="#6b8dd6"/><path d="M33,11L39,26L39,35Q39,38 36,38L4,38Q1,38 1,35L1,26Z" fill="#00b4d8" opacity=".80"/></svg>
ShipZen
</div>
<p class="footer-desc">Enterprise UPS Ground rates for e-commerce sellers. No contracts, no minimums, no hidden fees.</p>
</div>
<div class="footer-col">
<h4>Product</h4>
<ul>
<li><a href="#features">Features</a></li>
<li><a href="#how-it-works">How It Works</a></li>
<li><a href="#faq">FAQ</a></li>
</ul>
</div>
<div class="footer-col">
<h4>Integrations</h4>
<ul>
<li><a href="#">Shopify</a></li>
<li><a href="#">WooCommerce</a></li>
<li><a href="#">BigCommerce</a></li>
<li><a href="#">API Access</a></li>
</ul>
</div>
<div class="footer-col">
<h4>Company</h4>
<ul>
<li><a href="#">Privacy Policy</a></li>
<li><a href="#">Terms &amp; Conditions</a></li>
<li><a href="#contact">Contact Sales</a></li>
</ul>
</div>
</div>
<div class="footer-bottom">
<span class="footer-copy">&copy; 2026 ShipZen. All rights reserved.</span>
</div>
</div>
</footer>

<script>
/* FAQ toggle */
function tFaq(b){var i=b.parentElement,o=i.classList.contains('open');document.querySelectorAll('.faq-item.open').forEach(function(e){e.classList.remove('open')});if(!o)i.classList.add('open')}

/* Form submission */
document.getElementById('lead-form').addEventListener('submit',function(e){
e.preventDefault();
var b=document.getElementById('submit-btn'),m=document.getElementById('form-msg');
m.className='form-msg';m.textContent='';
document.querySelectorAll('.err').forEach(function(e){e.classList.remove('err')});
var d={email:document.getElementById('email').value.trim(),phone:document.getElementById('phone').value.trim(),website:document.getElementById('website').value.trim(),monthly_shipments:document.getElementById('monthly_shipments').value};
var errs=[];
if(!d.email){errs.push(1);document.getElementById('email').classList.add('err')}
else if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)){errs.push(1);document.getElementById('email').classList.add('err')}
if(errs.length){m.className='form-msg err';m.textContent='Please enter a valid email address.';return}
b.disabled=true;b.textContent='Submitting...';
fetch('/api/lead',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)})
.then(function(r){return r.json().then(function(j){return{ok:r.ok,data:j}})})
.then(function(r){if(r.ok){m.className='form-msg ok';m.textContent='Thank you! We\'ll send your savings quote within 24 hours.';document.getElementById('lead-form').reset()}else{m.className='form-msg err';m.textContent='Oops! Something went wrong.'}})
.catch(function(){m.className='form-msg err';m.textContent='Oops! Something went wrong.'})
.finally(function(){b.disabled=false;b.innerHTML='\uD83D\uDCE6 Get Your Savings Quote'});
});

/* Intersection observer for fade-in */
var obs=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)e.target.classList.add('visible')})},{threshold:.1,rootMargin:'0px 0px -30px 0px'});
document.querySelectorAll('.fade-in').forEach(function(e){obs.observe(e)});


/* Smooth scroll */
document.querySelectorAll('a[href^="#"]').forEach(function(a){a.addEventListener('click',function(e){var t=document.querySelector(this.getAttribute('href'));if(t){e.preventDefault();t.scrollIntoView({behavior:'smooth',block:'start'})}})});

/* Nav scroll state */
(function(){
var nav=document.querySelector('.nav');
var hero=document.querySelector('.hero');
if(!nav||!hero)return;
function onScroll(){
var heroBottom=hero.getBoundingClientRect().bottom;
if(heroBottom<=64){nav.classList.add('scrolled')}else{nav.classList.remove('scrolled')}
}
window.addEventListener('scroll',onScroll,{passive:true});
onScroll();
})();

/* Visibility-based animation pausing */
var visMap=new Map();
var visObs=new IntersectionObserver(function(entries){
entries.forEach(function(e){visMap.set(e.target,e.isIntersecting)});
},{threshold:0,rootMargin:'50px'});
function isVisible(el){return visMap.get(el)!==false}
function observeCanvas(el){visMap.set(el,true);visObs.observe(el)}

/* WebGL animated mesh gradient — softer pastel version */
(function(){
var c=document.getElementById('gradient-canvas');
if(!c)return;
var gl=c.getContext('webgl')||c.getContext('experimental-webgl');
if(!gl){
c.style.display='none';
c.parentElement.style.background='linear-gradient(135deg,#f0f5ff 0%,#e8f0fe 25%,#dbeafe 50%,#c3dafe 75%,#eff6ff 100%)';
return;
}
function resize(){
var hero=c.closest('.hero');
var dpr=Math.min(window.devicePixelRatio||1,2);
c.width=hero.offsetWidth*dpr;
c.height=hero.offsetHeight*dpr;
c.style.width=hero.offsetWidth+'px';
c.style.height=hero.offsetHeight+'px';
gl.viewport(0,0,c.width,c.height);
}
resize();
window.addEventListener('resize',resize);
var vsrc='attribute vec2 p;void main(){gl_Position=vec4(p,0,1);}';
var fsrc=[
'precision highp float;',
'uniform float t;',
'uniform vec2 res;',
'vec3 cBg=vec3(0.969,0.976,0.988);',
'vec3 c1=vec3(0.271,0.550,0.945);',
'vec3 c2=vec3(0.200,0.430,0.900);',
'vec3 c3=vec3(0.420,0.680,0.975);',
'vec3 c4=vec3(0.165,0.295,0.730);',
'vec3 c5=vec3(0.890,0.935,0.992);',
'vec3 c6=vec3(0.620,0.800,0.985);',
'float ribbon(vec2 uv,float offset,float freq,float amp,float width,float speed){',
'  float diag=uv.x*0.7+uv.y*0.3;',
'  float wave=amp*sin(diag*freq+t*speed+offset);',
'  float perp=-uv.x*0.3+uv.y*0.7;',
'  float d=abs(perp-wave-offset*0.15);',
'  return smoothstep(width,width*0.08,d);',
'}',
'void main(){',
'  vec2 uv=gl_FragCoord.xy/res;',
'  float aspect=res.x/res.y;',
'  vec2 p=vec2(uv.x*aspect,uv.y);',
'  p.x-=aspect*0.5; p.y-=0.5;',
'  float r1=ribbon(p, 0.0, 3.2, 0.16, 0.30, 0.12);',
'  float r2=ribbon(p, 0.6, 3.8, 0.20, 0.24, 0.10);',
'  float r3=ribbon(p,-0.5, 2.8, 0.14, 0.38, 0.15);',
'  float r4=ribbon(p, 1.2, 4.2, 0.11, 0.20, 0.08);',
'  float r5=ribbon(p,-1.0, 3.5, 0.18, 0.28, 0.11);',
'  float r6=ribbon(p, 0.3, 2.3, 0.22, 0.35, 0.16);',
'  vec3 col=cBg;',
'  col=mix(col,c5,r6*0.45);',
'  col=mix(col,c3,r3*0.50);',
'  col=mix(col,c6,r5*0.45);',
'  col=mix(col,c1,r1*0.60);',
'  col=mix(col,c4,r2*0.55);',
'  col=mix(col,c2,r4*0.50);',
'  float edge1=ribbon(p, 0.0, 3.2, 0.16, 0.06, 0.12);',
'  float edge2=ribbon(p, 0.6, 3.8, 0.20, 0.05, 0.10);',
'  col=mix(col,vec3(1.0),edge1*0.25);',
'  col=mix(col,vec3(0.96,0.97,1.0),edge2*0.20);',
'  float fade=smoothstep(0.0,0.45,uv.x);',
'  col=mix(cBg,col,fade);',
'  float bfade=smoothstep(0.0,0.15,uv.y);',
'  col=mix(cBg,col,bfade);',
'  gl_FragColor=vec4(col,1.0);',
'}'
].join('\n');
function mkShader(src,type){var s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);return s;}
var vs=mkShader(vsrc,gl.VERTEX_SHADER);
var fs=mkShader(fsrc,gl.FRAGMENT_SHADER);
var prog=gl.createProgram();
gl.attachShader(prog,vs);gl.attachShader(prog,fs);gl.linkProgram(prog);gl.useProgram(prog);
var buf=gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER,buf);
gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
var pLoc=gl.getAttribLocation(prog,'p');
gl.enableVertexAttribArray(pLoc);
gl.vertexAttribPointer(pLoc,2,gl.FLOAT,false,0,0);
var tLoc=gl.getUniformLocation(prog,'t');
var rLoc=gl.getUniformLocation(prog,'res');
observeCanvas(c);
var start=performance.now();
function frame(){
if(isVisible(c)){
var elapsed=(performance.now()-start)/1000;
gl.uniform1f(tLoc,elapsed);
gl.uniform2f(rLoc,c.width,c.height);
gl.drawArrays(gl.TRIANGLE_STRIP,0,4);
}
requestAnimationFrame(frame);
}
frame();
})();

/* Enterprise card canvas animations */
(function(){
function setupCanvas(id){
var c=document.getElementById(id);
if(!c)return null;
var ctx=c.getContext('2d');
function sz(){var r=c.parentElement.getBoundingClientRect();var d=window.devicePixelRatio||1;c.width=r.width*d;c.height=r.height*d;ctx.scale(d,d);c._w=r.width;c._h=r.height;}
sz();window.addEventListener('resize',sz);
return{c:c,ctx:ctx};
}

/* Card 1: Savings accumulator */
var s1=setupCanvas('ent-cv-1');
if(s1)(function(){
var ctx=s1.ctx,c=s1.c;
observeCanvas(c);
var tick=0;
var startSaved=8000+Math.floor(Math.random()*1000);
var packages=[];var totalSaved=startSaved;var savedHistory=[];var maxHistory=180;
function spawnPkg(){
var saved=Math.random()*1.5+0.8;
totalSaved+=saved;
packages.push({x:1.05,y:.3+Math.random()*.4,vx:-(Math.random()*.006+.004),saved:saved,o:1,age:0});
}
function draw(){
if(!isVisible(c)){requestAnimationFrame(draw);return;}
var w=c._w,h=c._h;
ctx.clearRect(0,0,w,h);tick++;
ctx.fillStyle='#f0f5ff';ctx.fillRect(0,0,w,h);
var gbx=w*(.5+Math.sin(tick*.004)*.12);
var gby=h*(.5+Math.cos(tick*.006)*.1);
var glow=ctx.createRadialGradient(gbx,gby,0,gbx,gby,w*.5);
glow.addColorStop(0,'rgba(37,99,235,.06)');glow.addColorStop(1,'rgba(255,255,255,0)');
ctx.fillStyle=glow;ctx.fillRect(0,0,w,h);
if(tick%18===0)spawnPkg();
if(tick%3===0){savedHistory.push(totalSaved);if(savedHistory.length>maxHistory)savedHistory.shift();}
var chartL=0,chartR=w,chartT=h*.55,chartB=h*.9;
var chartW=chartR-chartL,chartH=chartB-chartT;
ctx.strokeStyle='rgba(37,99,235,.05)';ctx.lineWidth=.5;
for(var gy=0;gy<4;gy++){var ly=chartT+gy*(chartH/3);ctx.beginPath();ctx.moveTo(chartL,ly);ctx.lineTo(chartR,ly);ctx.stroke();}
if(savedHistory.length>1){
var maxVal=Math.max.apply(null,savedHistory)*1.1||10;
ctx.save();ctx.beginPath();
var stepX=chartW/(maxHistory-1);
ctx.moveTo(chartR-(savedHistory.length-1)*stepX,chartB-chartH*(savedHistory[0]/maxVal));
for(var i=1;i<savedHistory.length;i++){
var px=chartR-(savedHistory.length-1-i)*stepX;
var py=chartB-chartH*(savedHistory[i]/maxVal);
ctx.lineTo(px,py);
}
ctx.lineTo(chartR,chartB);ctx.lineTo(chartR-(savedHistory.length-1)*stepX,chartB);ctx.closePath();
var areaGrad=ctx.createLinearGradient(0,chartT,0,chartB);
areaGrad.addColorStop(0,'rgba(16,185,129,.12)');areaGrad.addColorStop(1,'rgba(16,185,129,.02)');
ctx.fillStyle=areaGrad;ctx.fill();
ctx.beginPath();
ctx.moveTo(chartR-(savedHistory.length-1)*stepX,chartB-chartH*(savedHistory[0]/maxVal));
for(var i=1;i<savedHistory.length;i++){
var px=chartR-(savedHistory.length-1-i)*stepX;
var py=chartB-chartH*(savedHistory[i]/maxVal);
ctx.lineTo(px,py);
}
ctx.strokeStyle='rgba(16,185,129,.5)';ctx.lineWidth=2;ctx.stroke();
ctx.restore();
}
for(var i=packages.length-1;i>=0;i--){
var p=packages[i];p.x+=p.vx;p.age++;
if(p.x<-.05){packages.splice(i,1);continue;}
var px=p.x*w,py=p.y*h;
ctx.save();
ctx.fillStyle='rgba(37,99,235,'+(p.o*.5)+')';
ctx.fillRect(px-6,py-5,12,10);
ctx.strokeStyle='rgba(37,99,235,'+(p.o*.25)+')';ctx.lineWidth=.5;
ctx.strokeRect(px-6,py-5,12,10);
ctx.restore();
if(p.age<60){
ctx.font='600 '+Math.round(w*.025)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(16,185,129,'+(Math.min(p.age/15,1)*(1-Math.max(0,(p.age-40)/20)))+')';
ctx.textAlign='center';
ctx.fillText('saved',px,py-12);
}
}
var txtX=w*.5;var txtY=h*.28;
ctx.save();ctx.textAlign='center';ctx.textBaseline='middle';
ctx.font='800 '+Math.round(w*.11)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(16,185,129,.75)';
ctx.fillText(totalSaved.toFixed(0)+'+',txtX,txtY);
ctx.font='600 '+Math.round(w*.028)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(37,99,235,.3)';
ctx.fillText('PACKAGES OPTIMIZED',txtX,txtY+w*.075);
ctx.restore();
requestAnimationFrame(draw);
}
draw();
})();

/* Card 2: US Map */
var s2=setupCanvas('ent-cv-2');
if(s2)(function(){
var ctx=s2.ctx,c=s2.c;
observeCanvas(c);
var tick=0;
var usPath=[
[.0021,.0415],[.0272,.0555],[.0364,.0943],[.0407,.0835],[.0379,.0497],
[.032,.016],[.0812,.016],[.1326,.016],[.1497,.016],[.2025,.016],[.2536,.016],
[.3056,.016],[.3576,.016],[.4164,.016],[.4757,.016],[.5116,.016],[.5116,.0002],
[.5175,0],[.5175,0],[.5205,.0226],[.5259,.0295],[.538,.0321],[.5557,.0386],
[.5725,.0514],[.5866,.046],[.6079,.0567],[.6135,.0563],[.629,.0447],
[.6453,.0596],[.6622,.0755],[.6762,.0892],[.6897,.1024],[.6914,.1132],
[.6955,.1173],[.6944,.1213],[.699,.1226],[.7024,.1183],[.7033,.1281],
[.7068,.1346],[.7115,.1346],[.7141,.1396],[.7119,.1469],[.73,.1663],
[.7337,.2036],[.7371,.2393],[.7321,.2636],[.7239,.2863],[.7201,.3007],
[.7197,.305],[.7217,.3108],[.7276,.3173],[.7319,.3173],[.752,.2954],
[.7699,.2889],[.7925,.2684],[.7929,.2643],[.7913,.2517],[.7885,.2436],
[.7963,.2371],[.8134,.2369],[.8293,.237],[.8348,.2209],[.837,.2177],
[.8553,.1881],[.8631,.1805],[.8894,.1802],[.9213,.1802],[.9231,.1701],
[.9286,.168],[.936,.1616],[.9421,.1429],[.9474,.1109],[.9606,.0799],
[.9664,.0907],[.978,.0837],[.9857,.0955],[.9857,.1516],[.997,.1749],[1,.1884],
[.9815,.2083],[.9637,.2225],[.9454,.2347],[.9362,.2591],[.9333,.2684],
[.9331,.2902],[.9388,.312],[.946,.313],[.9442,.298],[.9494,.3071],[.948,.3189],
[.9363,.3256],[.928,.3248],[.9152,.3319],[.9077,.334],[.8976,.336],[.8831,.3479],
[.9086,.3402],[.9137,.348],[.8895,.3603],[.8784,.3604],[.8789,.3554],
[.8737,.3668],[.8788,.3686],[.875,.3982],[.8624,.4299],[.8611,.4193],
[.8573,.4172],[.8516,.4069],[.8552,.429],[.8595,.4363],[.8598,.4519],
[.8543,.4679],[.8445,.5007],[.8429,.4991],[.8483,.4711],[.8394,.4554],
[.8374,.4212],[.8341,.439],[.8378,.4651],[.8263,.4586],[.8382,.4719],[.839,.511],
[.844,.5139],[.8458,.5281],[.8482,.5693],[.8372,.5998],[.8193,.612],
[.8079,.6361],[.7992,.6388],[.7904,.6539],[.788,.6677],[.769,.6944],[.7592,.714],
[.751,.7383],[.7484,.7676],[.7514,.7961],[.7572,.8313],[.7649,.8605],
[.765,.8782],[.7732,.926],[.7726,.9537],[.7719,.9697],[.7676,.9948],[.7624,1],
[.7539,.995],[.7511,.977],[.7445,.9675],[.7354,.9321],[.7273,.9007],
[.7247,.8846],[.7283,.8573],[.7234,.8346],[.7099,.8002],[.7031,.7939],
[.6857,.8126],[.6826,.8105],[.6742,.7913],[.6633,.7812],[.6437,.7863],
[.6283,.7818],[.6151,.7846],[.608,.791],[.6111,.802],[.6108,.8186],[.6145,.8268],
[.6112,.8322],[.6048,.8261],[.5983,.8339],[.5857,.8326],[.5727,.8109],
[.5576,.816],[.545,.8065],[.5343,.8094],[.5197,.819],[.5039,.8495],[.4867,.8672],
[.4772,.8869],[.4733,.9054],[.4731,.9338],[.4739,.9535],[.4772,.9675],
[.4705,.9687],[.4582,.9597],[.4447,.9469],[.4398,.9276],[.436,.8988],
[.4258,.8754],[.4198,.8512],[.4111,.8231],[.3989,.8067],[.3847,.8075],
[.3738,.84],[.3594,.8276],[.3505,.8152],[.3462,.7926],[.3404,.7711],[.3301,.753],
[.3213,.74],[.3149,.7254],[.2849,.7254],[.2849,.7424],[.2712,.7424],
[.2367,.7427],[.1972,.7137],[.171,.6937],[.1727,.6857],[.1506,.6901],
[.131,.6933],[.128,.6723],[.1168,.6486],[.1087,.6437],[.1068,.6319],
[.0971,.6298],[.0909,.6187],[.0748,.6147],[.0704,.608],[.0683,.5855],
[.0515,.5441],[.0371,.4869],[.0377,.4774],[.03,.4638],[.0166,.4294],
[.0142,.3958],[.005,.3734],[.0088,.3393],[.0082,.304],[.0027,.2725],
[.0094,.2337],[.0115,.1964],[.0137,.159],[.0105,.1038],[.0051,.0687],[0,.0496],
[.0021,.0415]
];
var cities=[
{name:'LA',x:.12,y:.63},{name:'SF',x:.04,y:.48},{name:'SEA',x:.03,y:.06},
{name:'DEN',x:.25,y:.40},{name:'DAL',x:.40,y:.76},{name:'CHI',x:.58,y:.28},
{name:'ATL',x:.68,y:.60},{name:'MIA',x:.76,y:.92},{name:'NYC',x:.88,y:.28},
{name:'BOS',x:.94,y:.18},{name:'PHX',x:.18,y:.62},{name:'MSP',x:.48,y:.18},
{name:'KC',x:.45,y:.46},{name:'PDX',x:.03,y:.14},{name:'SLC',x:.20,y:.36}
];
var shipments=[];var deliveries=[];
function spawnShipment(){
var from=cities[Math.floor(Math.random()*cities.length)];
var to=cities[Math.floor(Math.random()*cities.length)];
while(to===from)to=cities[Math.floor(Math.random()*cities.length)];
shipments.push({fx:from.x,fy:from.y,tx:to.x,ty:to.y,progress:0,speed:.006+Math.random()*.004,city:to.name});
}
var pad=.06;
function mx(nx,w){return pad*w+nx*(1-2*pad)*w;}
function my(ny,h){return pad*h+ny*(1-2*pad)*h*.88;}
function tracePath(w,h){
ctx.beginPath();
for(var i=0;i<usPath.length;i++){
var px=mx(usPath[i][0],w),py=my(usPath[i][1],h);
if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py);
}
ctx.closePath();
}
function draw(){
if(!isVisible(c)){requestAnimationFrame(draw);return;}
var w=c._w,h=c._h;
ctx.clearRect(0,0,w,h);
ctx.fillStyle='#f0f5ff';ctx.fillRect(0,0,w,h);
tick++;
var gbx=w*(.5+Math.sin(tick*.003)*.1);
var gby=h*(.5+Math.cos(tick*.004)*.08);
var glow=ctx.createRadialGradient(gbx,gby,0,gbx,gby,w*.5);
glow.addColorStop(0,'rgba(37,99,235,.05)');glow.addColorStop(1,'rgba(255,255,255,0)');
ctx.fillStyle=glow;ctx.fillRect(0,0,w,h);
if(tick%35===0)spawnShipment();
ctx.save();
tracePath(w,h);
var usGrad=ctx.createLinearGradient(0,0,w,h);
usGrad.addColorStop(0,'rgba(37,99,235,.06)');
usGrad.addColorStop(.5,'rgba(37,99,235,.10)');
usGrad.addColorStop(1,'rgba(37,99,235,.05)');
ctx.fillStyle=usGrad;ctx.fill();
ctx.strokeStyle='rgba(37,99,235,.18)';ctx.lineWidth=1.5;ctx.stroke();
ctx.restore();
ctx.save();
tracePath(w,h);ctx.clip();
var pulseR=w*(.25+Math.sin(tick*.008)*.05);
var iglow=ctx.createRadialGradient(w*.5,h*.4,0,w*.5,h*.4,pulseR);
iglow.addColorStop(0,'rgba(37,99,235,.08)');iglow.addColorStop(1,'rgba(37,99,235,0)');
ctx.fillStyle=iglow;ctx.fillRect(0,0,w,h);
ctx.restore();
for(var i=0;i<cities.length;i++){
var ci=cities[i];
var cx=mx(ci.x,w),cy=my(ci.y,h);
var pulse=Math.sin(tick*.03+i)*.3+.7;
ctx.beginPath();ctx.arc(cx,cy,7,0,Math.PI*2);
ctx.fillStyle='rgba(37,99,235,.05)';ctx.fill();
ctx.beginPath();ctx.arc(cx,cy,3,0,Math.PI*2);
ctx.fillStyle='rgba(37,99,235,'+(.35*pulse)+')';ctx.fill();
ctx.font='500 '+Math.round(w*.02)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(37,99,235,.25)';ctx.textAlign='center';
ctx.fillText(ci.name,cx,cy-10);
}
for(var i=shipments.length-1;i>=0;i--){
var s=shipments[i];s.progress+=s.speed;
if(s.progress>=1){
deliveries.push({x:mx(s.tx,w),y:my(s.ty,h),r:0,o:.5});
shipments.splice(i,1);continue;
}
var t=s.progress;
var ease=t<.5?2*t*t:(1-Math.pow(-2*t+2,2)/2);
var acx=mx(s.fx,w)+(mx(s.tx,w)-mx(s.fx,w))*.5;
var acy=Math.min(my(s.fy,h),my(s.ty,h))-h*.12;
var px=(1-ease)*(1-ease)*mx(s.fx,w)+2*(1-ease)*ease*acx+ease*ease*mx(s.tx,w);
var py=(1-ease)*(1-ease)*my(s.fy,h)+2*(1-ease)*ease*acy+ease*ease*my(s.ty,h);
ctx.beginPath();
for(var tt=0;tt<=t;tt+=.02){
var e2=tt<.5?2*tt*tt:(1-Math.pow(-2*tt+2,2)/2);
var tx2=(1-e2)*(1-e2)*mx(s.fx,w)+2*(1-e2)*e2*acx+e2*e2*mx(s.tx,w);
var ty2=(1-e2)*(1-e2)*my(s.fy,h)+2*(1-e2)*e2*acy+e2*e2*my(s.ty,h);
if(tt===0)ctx.moveTo(tx2,ty2);else ctx.lineTo(tx2,ty2);
}
ctx.strokeStyle='rgba(37,99,235,.15)';ctx.lineWidth=1.2;ctx.stroke();
ctx.beginPath();ctx.arc(px,py,3.5,0,Math.PI*2);
ctx.fillStyle='rgba(37,99,235,.7)';ctx.fill();
ctx.beginPath();ctx.arc(px,py,7,0,Math.PI*2);
ctx.fillStyle='rgba(37,99,235,.08)';ctx.fill();
}
for(var i=deliveries.length-1;i>=0;i--){
var d=deliveries[i];d.r+=1;d.o-=.015;
if(d.o<=0){deliveries.splice(i,1);continue;}
ctx.beginPath();ctx.arc(d.x,d.y,d.r,0,Math.PI*2);
ctx.strokeStyle='rgba(16,185,129,'+d.o+')';ctx.lineWidth=1.5;ctx.stroke();
}
ctx.save();ctx.textAlign='center';ctx.textBaseline='middle';
ctx.font='700 '+Math.round(w*.032)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(37,99,235,.12)';
ctx.fillText('SAME RATE EVERYWHERE',w*.5,h*.95);
ctx.restore();
requestAnimationFrame(draw);
}
draw();
})();

/* Card 3: Simple vs complex pricing comparison */
var s3=setupCanvas('ent-cv-3');
if(s3)(function(){
var ctx=s3.ctx,c=s3.c;
observeCanvas(c);
var tick=0;
function draw(){
if(!isVisible(c)){requestAnimationFrame(draw);return;}
var w=c._w,h=c._h;
ctx.clearRect(0,0,w,h);
ctx.fillStyle='#f0f5ff';ctx.fillRect(0,0,w,h);
tick++;
var gbx=w*(.5+Math.sin(tick*.004)*.1);
var gby=h*(.5+Math.cos(tick*.005)*.08);
var glow=ctx.createRadialGradient(gbx,gby,0,gbx,gby,w*.5);
glow.addColorStop(0,'rgba(37,99,235,.04)');glow.addColorStop(1,'rgba(255,255,255,0)');
ctx.fillStyle=glow;ctx.fillRect(0,0,w,h);
var colW=w*.38;var gap=w*.06;
var lx=w*.5-gap/2-colW;var rx=w*.5+gap/2;
var topY=h*.12;
ctx.save();
ctx.fillStyle='rgba(37,99,235,.03)';
ctx.beginPath();ctx.moveTo(lx+8,topY);ctx.lineTo(lx+colW-8,topY);ctx.quadraticCurveTo(lx+colW,topY,lx+colW,topY+8);
ctx.lineTo(lx+colW,h*.88-8);ctx.quadraticCurveTo(lx+colW,h*.88,lx+colW-8,h*.88);
ctx.lineTo(lx+8,h*.88);ctx.quadraticCurveTo(lx,h*.88,lx,h*.88-8);
ctx.lineTo(lx,topY+8);ctx.quadraticCurveTo(lx,topY,lx+8,topY);ctx.closePath();ctx.fill();
ctx.strokeStyle='rgba(37,99,235,.08)';ctx.lineWidth=1;ctx.stroke();
ctx.restore();
ctx.font='700 '+Math.round(w*.035)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(37,99,235,.5)';ctx.textAlign='center';
ctx.fillText('ShipZen',lx+colW/2,topY+h*.06);
var priceY=topY+h*.25;
ctx.font='800 '+Math.round(w*.065)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(37,99,235,.65)';
ctx.fillText('Flat Rate',lx+colW/2,priceY);
ctx.font='500 '+Math.round(w*.025)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(37,99,235,.3)';
ctx.fillText('simple, predictable',lx+colW/2,priceY+h*.06);
var checks=['No zone fees','No DIM weight','No surcharges','No monthly fee'];
for(var i=0;i<checks.length;i++){
var cy=priceY+h*.14+i*h*.08;
ctx.font='500 '+Math.round(w*.028)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(16,185,129,.55)';ctx.textAlign='center';
ctx.fillText('\u2713 '+checks[i],lx+colW/2,cy);
}
ctx.save();
ctx.fillStyle='rgba(220,38,38,.03)';
ctx.beginPath();ctx.moveTo(rx+8,topY);ctx.lineTo(rx+colW-8,topY);ctx.quadraticCurveTo(rx+colW,topY,rx+colW,topY+8);
ctx.lineTo(rx+colW,h*.88-8);ctx.quadraticCurveTo(rx+colW,h*.88,rx+colW-8,h*.88);
ctx.lineTo(rx+8,h*.88);ctx.quadraticCurveTo(rx,h*.88,rx,h*.88-8);
ctx.lineTo(rx,topY+8);ctx.quadraticCurveTo(rx,topY,rx+8,topY);ctx.closePath();ctx.fill();
ctx.strokeStyle='rgba(220,38,38,.06)';ctx.lineWidth=1;ctx.stroke();
ctx.restore();
ctx.font='700 '+Math.round(w*.035)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(220,38,38,.4)';ctx.textAlign='center';
ctx.fillText('Others',rx+colW/2,topY+h*.06);
var fees=[
{label:'Base rate',val:'varies',y:0},
{label:'Zone surcharge',val:'+ extra',y:1},
{label:'Fuel surcharge',val:'+ extra',y:2},
{label:'DIM weight adj.',val:'+ extra',y:3},
{label:'Residential fee',val:'+ extra',y:4}
];
var startY=topY+h*.16;
for(var i=0;i<fees.length;i++){
var fy=startY+i*h*.09;
var wobble=Math.sin(tick*.02+i*1.5)*1;
ctx.font='500 '+Math.round(w*.024)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(220,38,38,.3)';ctx.textAlign='left';
ctx.fillText(fees[i].label,rx+w*.02,fy+wobble);
ctx.textAlign='right';ctx.fillStyle='rgba(220,38,38,.45)';
ctx.fillText(fees[i].val,rx+colW-w*.02,fy+wobble);
if(i>0){
ctx.beginPath();ctx.moveTo(rx+w*.02,fy+wobble+1);ctx.lineTo(rx+colW-w*.02,fy+wobble+1);
ctx.strokeStyle='rgba(220,38,38,.05)';ctx.lineWidth=.5;ctx.stroke();
}
}
var totalY=startY+5*h*.09+h*.03;
ctx.font='700 '+Math.round(w*.04)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(220,38,38,.45)';ctx.textAlign='center';
ctx.fillText('$$$',rx+colW/2,totalY);
ctx.font='500 '+Math.round(w*.022)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(220,38,38,.25)';
ctx.fillText('total after fees',rx+colW/2,totalY+h*.05);
var vsY=h*.45;
ctx.beginPath();ctx.arc(w*.5,vsY,w*.04,0,Math.PI*2);
ctx.fillStyle='#fff';ctx.fill();
ctx.strokeStyle='rgba(37,99,235,.12)';ctx.lineWidth=1;ctx.stroke();
ctx.font='800 '+Math.round(w*.028)+'px Inter,system-ui,sans-serif';
ctx.fillStyle='rgba(37,99,235,.45)';ctx.textAlign='center';ctx.textBaseline='middle';
ctx.fillText('VS',w*.5,vsY);
ctx.textBaseline='alphabetic';
requestAnimationFrame(draw);
}
draw();
})();


})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8422))
    debug = os.getenv("RAILWAY_ENVIRONMENT") is None
    print(f"\n  ShipZen V2 Landing Page running at: http://localhost:{port}\n")
    app.run(debug=debug, host="0.0.0.0", port=port)
