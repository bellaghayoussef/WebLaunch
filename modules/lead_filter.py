import json
import re
from pathlib import Path
from config import LEADS_DB_FILE

SOCIAL_DOMAINS = [
    "instagram.com", "facebook.com", "fb.com", "tiktok.com",
    "talabat.com", "snoonu.com", "deliveroo", "ubereats.com",
    "glovoapp.com", "just-eat", "tripadvisor.com", "foursquare.com",
    "yelp.com", "google.com/maps"
]

def clean_phone_number(raw_phone, country_code_hint=""):
    """
    Cleans and converts raw phone number into an international WhatsApp-ready format without '+' or spaces.
    e.g. '+974 7045 6262' -> '97470456262'
    """
    if not raw_phone:
        return "", ""

    # Keep only digits and '+'
    cleaned = re.sub(r"[^\d+]", "", str(raw_phone))
    
    # If starts with '+', strip '+'
    if cleaned.startswith("+"):
        intl_phone = cleaned[1:]
    elif cleaned.startswith("00"):
        intl_phone = cleaned[2:]
    else:
        # If no country code and hint provided, apply hint
        if country_code_hint and not cleaned.startswith(country_code_hint.replace("+", "")):
            # Remove leading 0 if local
            if cleaned.startswith("0"):
                cleaned = cleaned[1:]
            intl_phone = country_code_hint.replace("+", "") + cleaned
        else:
            intl_phone = cleaned

    formatted_display = f"+{intl_phone}" if intl_phone else ""
    return intl_phone, formatted_display

def evaluate_website_status(website_url):
    """
    Evaluates if business has a real website, only social/delivery page, or nothing.
    Returns: (has_website: bool, status_label: str, priority: str, website_type: str)
    """
    if not website_url or not str(website_url).strip() or str(website_url).lower() in ["none", "null", "no", "n/a", ""]:
        return False, "No Website", "High", "none"

    url_lower = str(website_url).lower().strip()

    # Check for social media or delivery platform
    for domain in SOCIAL_DOMAINS:
        if domain in url_lower:
            return False, f"Social / Delivery Only ({domain.split('.')[0].capitalize()})", "High", "social"

    # Has a custom domain
    return True, "Has Website", "Low", "standalone"

def enrich_lead(lead_data, country_code_hint=""):
    """
    Enriches a raw scraped business record with WhatsApp links, email, priority, and ID.
    """
    lead_id = lead_data.get("id") or re.sub(r"[^\w]", "_", lead_data.get("name", "lead")).lower()
    
    raw_phone = lead_data.get("phone", "")
    wa_number, formatted_phone = clean_phone_number(raw_phone, country_code_hint)
    
    website = lead_data.get("website", "")
    has_website, website_status, priority, website_type = evaluate_website_status(website)

    # Clean and normalize email
    raw_email = str(lead_data.get("email") or "").strip().lower()
    if raw_email and ("@" in raw_email) and ("." in raw_email):
        email = raw_email
    else:
        email = ""

    lead_data["id"] = lead_id
    lead_data["email"] = email
    lead_data["wa_number"] = wa_number
    lead_data["formatted_phone"] = formatted_phone
    lead_data["wa_link"] = f"https://wa.me/{wa_number}" if wa_number else ""
    lead_data["has_website"] = has_website
    lead_data["website_status"] = website_status
    lead_data["website_type"] = website_type
    lead_data["priority"] = priority
    lead_data["outreach_status"] = lead_data.get("outreach_status", "Not Contacted")
    lead_data["demo_generated"] = lead_data.get("demo_generated", False)
    lead_data["mockup_path"] = lead_data.get("mockup_path", "")

    return lead_data

def load_leads_db():
    if LEADS_DB_FILE.exists():
        try:
            with open(LEADS_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_leads_db(leads):
    with open(LEADS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)

def upsert_leads(new_leads):
    """
    Adds new leads avoiding duplicate IDs or names.
    """
    existing = load_leads_db()
    existing_map = {l.get("id"): l for l in existing}

    for lead in new_leads:
        lid = lead.get("id")
        if lid in existing_map:
            # Preserve user's outreach status, mockup, and email if not in new
            lead["outreach_status"] = existing_map[lid].get("outreach_status", lead.get("outreach_status"))
            lead["demo_generated"] = existing_map[lid].get("demo_generated", lead.get("demo_generated"))
            lead["mockup_path"] = existing_map[lid].get("mockup_path", lead.get("mockup_path"))
            if not lead.get("email") and existing_map[lid].get("email"):
                lead["email"] = existing_map[lid].get("email")
        existing_map[lid] = lead

    merged = list(existing_map.values())
    save_leads_db(merged)
    return merged
