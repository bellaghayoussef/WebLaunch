import os
import sys
import csv
import io

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
from config import load_settings, save_settings, STATIC_DIR, MOCKUP_DIR, BASE_DIR
from modules.scraper import search_businesses, COUNTRIES, CATEGORIES
from modules.lead_filter import (
    load_leads_db,
    save_leads_db,
    upsert_leads,
    enrich_lead
)
from modules.mockup_generator import generate_mockup
from modules.outreach import generate_outreach_messages, send_email_with_mockup

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
app.config["SECRET_KEY"] = os.urandom(24)

# =========================================================================
# WEB PAGES
# =========================================================================

@app.route("/")
def index():
    settings = load_settings()
    leads = load_leads_db()
    # Stats
    total_leads = len(leads)
    needs_website = sum(1 for l in leads if not l.get("has_website"))
    contacted = sum(1 for l in leads if l.get("outreach_status") not in ["Not Contacted", "", None])
    demos_built = sum(1 for l in leads if l.get("demo_generated"))

    return render_template(
        "index.html",
        countries=COUNTRIES,
        categories=CATEGORIES,
        leads=leads,
        stats={
            "total": total_leads,
            "needs_website": needs_website,
            "contacted": contacted,
            "demos": demos_built
        },
        settings=settings
    )

@app.route("/demo/<slug>")
@app.route("/demo/<slug>/")
@app.route("/demo/<slug>/<path:page>")
def live_demo(slug, page="index.html"):
    if not page:
        page = "index.html"
    if not page.endswith(".html") and "." not in page:
        page = f"{page}.html"
    demo_file = BASE_DIR / "demos" / slug / page
    if demo_file.exists():
        with open(demo_file, "r", encoding="utf-8") as f:
            return f.read()
    # Fallback to index.html if specific page is missing
    index_file = BASE_DIR / "demos" / slug / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return f"<h1>Démo non trouvée pour {slug}</h1>", 404

@app.route("/leads")
def leads_view():
    leads = load_leads_db()
    settings = load_settings()
    return render_template("leads.html", leads=leads, settings=settings)

@app.route("/settings", methods=["GET", "POST"])
def settings_view():
    if request.method == "POST":
        data = {
            "agency_name": request.form.get("agency_name", "WebLaunch Agency"),
            "agency_phone": request.form.get("agency_phone", "+974 5000 0000"),
            "agency_email": request.form.get("agency_email", ""),
            "default_language": request.form.get("default_language", "fr"),
            "smtp": {
                "host": request.form.get("smtp_host", "smtp.gmail.com"),
                "port": int(request.form.get("smtp_port", 587)),
                "user": request.form.get("smtp_user", ""),
                "password": request.form.get("smtp_password", ""),
                "from_email": request.form.get("smtp_from", ""),
                "use_tls": "use_tls" in request.form
            }
        }
        save_settings(data)
        return redirect(url_for("settings_view", saved=1))

    settings = load_settings()
    return render_template("settings.html", settings=settings)

# =========================================================================
# REST API ENDPOINTS
# =========================================================================

@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.json or {}
    country = data.get("country", "qatar")
    city = data.get("city", "Doha")
    category = data.get("category", "restaurant")
    only_no_website = data.get("only_no_website", True)
    limit = int(data.get("limit", 20))

    try:
        found_leads = search_businesses(
            country_key=country,
            city=city,
            category_key=category,
            only_no_website=only_no_website,
            limit=limit
        )

        # Upsert into database
        all_leads = upsert_leads(found_leads)

        return jsonify({
            "success": True,
            "count": len(found_leads),
            "leads": found_leads,
            "total_saved": len(all_leads)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/leads", methods=["GET"])
def api_get_leads():
    leads = load_leads_db()
    return jsonify({"leads": leads})

@app.route("/api/leads/update", methods=["POST"])
def api_update_lead():
    data = request.json or {}
    lead_id = data.get("id")
    if not lead_id:
        return jsonify({"success": False, "error": "Lead ID required"}), 400

    leads = load_leads_db()
    updated = False
    for l in leads:
        if l.get("id") == lead_id:
            if "outreach_status" in data:
                l["outreach_status"] = data["outreach_status"]
            if "notes" in data:
                l["notes"] = data["notes"]
            if "email" in data:
                l["email"] = data["email"]
            if "phone" in data:
                l["phone"] = data["phone"]
                enr = enrich_lead(l)
                l.update(enr)
            updated = True
            break

    if updated:
        save_leads_db(leads)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Lead not found"}), 404

@app.route("/api/leads/<lead_id>", methods=["DELETE"])
def api_delete_lead(lead_id):
    leads = load_leads_db()
    filtered = [l for l in leads if l.get("id") != lead_id]
    save_leads_db(filtered)
    return jsonify({"success": True, "count": len(filtered)})

@app.route("/api/generate-mockup/<lead_id>", methods=["POST"])
def api_generate_mockup(lead_id):
    leads = load_leads_db()
    target_lead = next((l for l in leads if l.get("id") == lead_id), None)
    
    if not target_lead:
        # Fallback payload from request body
        target_lead = request.json
        if not target_lead:
            return jsonify({"success": False, "error": "Lead introuvable"}), 404

    try:
        mockup_res = generate_mockup(target_lead)
        target_lead["mockup_path"] = mockup_res["url"]
        target_lead["demo_url"] = mockup_res.get("demo_url", "")
        target_lead["demo_generated"] = True
        save_leads_db(leads)

        return jsonify({
            "success": True,
            "mockup_url": mockup_res["url"],
            "demo_url": mockup_res.get("demo_url", ""),
            "filename": mockup_res["filename"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/outreach/<lead_id>", methods=["GET"])
def api_get_outreach(lead_id):
    leads = load_leads_db()
    target = next((l for l in leads if l.get("id") == lead_id), None)
    if not target:
        return jsonify({"success": False, "error": "Lead not found"}), 404

    lang = request.args.get("lang")
    mockup_url = target.get("mockup_path", "")
    demo_url = target.get("demo_url", "")
    
    messages = generate_outreach_messages(target, mockup_url=mockup_url, demo_url=demo_url, lang=lang)
    return jsonify({"success": True, "messages": messages, "lead": target})

@app.route("/api/send-email", methods=["POST"])
def api_send_email():
    data = request.json or {}
    to_email = data.get("to_email")
    subject = data.get("subject")
    body = data.get("body")
    lead_id = data.get("lead_id")
    
    if not to_email or not subject or not body:
        return jsonify({"success": False, "error": "Destinataire, objet et message requis"}), 400

    leads = load_leads_db()
    target = next((l for l in leads if l.get("id") == lead_id), None)
    
    mockup_filepath = None
    if target and target.get("mockup_path"):
        filename = os.path.basename(target["mockup_path"])
        mockup_filepath = MOCKUP_DIR / filename

    res = send_email_with_mockup(to_email, subject, body, mockup_filepath=mockup_filepath)
    if target:
        target["email"] = to_email
        if res["success"]:
            target["outreach_status"] = "Contacted (Email)"
        save_leads_db(leads)

    return jsonify(res)

@app.route("/api/export-csv", methods=["GET"])
def api_export_csv():
    leads = load_leads_db()
    output = io.StringIO()
    writer = csv.writer(output)

    # Compatible with restaurant-leads.csv format
    headers = [
        "Restaurant Name", "Area/City", "Cuisine Type", "Has Website",
        "Website Status", "Website URL", "Phone/WhatsApp", "WhatsApp Link",
        "Email", "Priority", "Status", "Demo Built", "Mockup Link", "Notes"
    ]
    writer.writerow(headers)

    for l in leads:
        writer.writerow([
            l.get("name", ""),
            f"{l.get('city', '')} ({l.get('country', '')})",
            l.get("category", ""),
            "Yes" if l.get("has_website") else "No",
            l.get("website_status", ""),
            l.get("website", ""),
            l.get("formatted_phone") or l.get("phone", ""),
            l.get("wa_link", ""),
            l.get("email", ""),
            l.get("priority", "High"),
            l.get("outreach_status", "Not Contacted"),
            "Yes" if l.get("demo_generated") else "No",
            l.get("mockup_path", ""),
            l.get("notes", "")
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="leads_export.csv"
    )

if __name__ == "__main__":
    settings = load_settings()
    port = settings.get("port", 5050)
    print(f"\n=======================================================")
    print(f"🎯 LeadHunter Flask Server starting at http://localhost:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
