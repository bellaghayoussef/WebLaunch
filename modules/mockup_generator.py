import os
import re
import json
import urllib.request
import urllib.error
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from config import BASE_DIR, MOCKUP_DIR, SETTINGS_FILE, load_settings

DEMOS_DIR = BASE_DIR / "demos"
DEMOS_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_JSON_FILE = BASE_DIR / "config.json"

THEMES = {
    "hotel_luxury": {
        "id": "hotel_luxury",
        "layout": "hotel_grand",
        "bg": "#faf8f5",
        "bg_subtle": "#f4ede4",
        "card": "#ffffff",
        "card_border": "rgba(180, 83, 9, 0.16)",
        "accent": "#b45309",
        "accent2": "#78350f",
        "accent_light": "rgba(180, 83, 9, 0.08)",
        "gold": "#d97706",
        "text": "#1c1917",
        "text_heading": "#0c0a09",
        "muted": "#78716c",
        "font_heading": "'Playfair Display', Georgia, serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "google_fonts": "family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,500;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700",
        "hero_badge": "⭐ Établissement Hôtelier d'Exception • Confort & Sérénité 5 Étoiles",
        "hero_img": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1600&q=80",
        "about_img": "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=900&q=80",
        "social_img1": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=600&q=80",
        "social_img2": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=600&q=80",
        "social_img3": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=600&q=80",
        "tagline": "Séjour d'Exception, Suites de Prestige & Sérénité Absolue",
        "subtitle": "Vivez un séjour inoubliable au cœur d'un cadre raffiné alliant élégance moderne, service de conciergerie 24/7 et bien-être absolu.",
        "usp_pills": ["✨ Suites & Chambres de Prestige", "🛎️ Conciergerie Privée 24h/24", "🏊 Piscine & Solarium", "⚡ Réservation Directe Garantie"]
    },
    "cafe_lounge": {
        "id": "cafe_lounge",
        "layout": "cafe_artisanal",
        "bg": "#fcfaf7",
        "bg_subtle": "#f5ede2",
        "card": "#ffffff",
        "card_border": "rgba(120, 53, 15, 0.16)",
        "accent": "#854d0e",
        "accent2": "#713f12",
        "accent_light": "rgba(133, 77, 14, 0.08)",
        "gold": "#d97706",
        "text": "#292524",
        "text_heading": "#1c1917",
        "muted": "#78716c",
        "font_heading": "'Fraunces', Georgia, serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "google_fonts": "family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=Plus+Jakarta+Sans:wght@400;500;600;700",
        "hero_badge": "☕ Café de Spécialité Torréfié • Brunch Artisanal & Douceurs",
        "hero_img": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1600&q=80",
        "about_img": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=900&q=80",
        "social_img1": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=600&q=80",
        "social_img2": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?auto=format&fit=crop&w=600&q=80",
        "social_img3": "https://images.unsplash.com/photo-1509785307050-d4066910ec1e?auto=format&fit=crop&w=600&q=80",
        "tagline": "L'Art du Café de Spécialité & Brunch Convivial",
        "subtitle": "Grains soigneusement sélectionnés, torréfaction artisanale, viennoiseries fraîches et latte art dans une ambiance chaleureuse.",
        "usp_pills": ["☕ Cafés d'Origine Pure & V60", "🥐 Pâtisseries & Brunch Fait Maison", "⚡ Commande Express à Emporter"]
    },
    "fast_food": {
        "id": "fast_food",
        "layout": "street_gourmet",
        "bg": "#fffaf5",
        "bg_subtle": "#fee2e2",
        "card": "#ffffff",
        "card_border": "rgba(220, 38, 38, 0.16)",
        "accent": "#dc2626",
        "accent2": "#b91c1c",
        "accent_light": "rgba(220, 38, 38, 0.08)",
        "gold": "#ea580c",
        "text": "#1c1917",
        "text_heading": "#0c0a09",
        "muted": "#78716c",
        "font_heading": "'Outfit', sans-serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "google_fonts": "family=Outfit:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700",
        "hero_badge": "🍔 Smash Burgers Gourmets & Street Food Artisanal Minute",
        "hero_img": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=1600&q=80",
        "about_img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80",
        "social_img1": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?auto=format&fit=crop&w=600&q=80",
        "social_img2": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=600&q=80",
        "social_img3": "https://images.unsplash.com/photo-1576107232684-1279f3908594?auto=format&fit=crop&w=600&q=80",
        "tagline": "Smash Burgers Juteux, Pizzas au Feu de Bois & Frites Maison",
        "subtitle": "Pains briochés dorés, viandes fraîches saisies à haute température et sauces secrètes de la maison.",
        "usp_pills": ["🍔 Pain Brioché Artisanal & Bœuf Frais", "🔥 Cuisson Minute Ultra Chaude", "⚡ Livraison WhatsApp Express 30min"]
    },
    "shawarma": {
        "id": "shawarma",
        "layout": "split_grill",
        "bg": "#fffaf5",
        "bg_subtle": "#fff1e6",
        "card": "#ffffff",
        "card_border": "rgba(234, 88, 12, 0.16)",
        "accent": "#ea580c",
        "accent2": "#c2410c",
        "accent_light": "rgba(234, 88, 12, 0.08)",
        "gold": "#d97706",
        "text": "#1c1917",
        "text_heading": "#0c0a09",
        "muted": "#78716c",
        "font_heading": "'Outfit', sans-serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "google_fonts": "family=Outfit:wght@500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700",
        "hero_badge": "🔥 Spécialiste Grillades & Broches Découpées Minute",
        "hero_img": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783?auto=format&fit=crop&w=1600&q=80",
        "about_img": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=900&q=80",
        "social_img1": "https://images.unsplash.com/photo-1561651823-34feb02250e4?auto=format&fit=crop&w=600&q=80",
        "social_img2": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80",
        "social_img3": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80",
        "tagline": "Le Meilleur Shawarma Artisanal & Grillades au Feu de Bois",
        "subtitle": "Broches découpées minute, viandes fraîches marinées et authentique sauce toum à l'ail maison.",
        "usp_pills": ["🔥 Braisé au Feu de Bois", "🥩 Viandes Fraîches Épicées", "⚡ Livraison WhatsApp Express"]
    },
    "seafood": {
        "id": "seafood",
        "layout": "coastal_luxe",
        "bg": "#f0f9ff",
        "bg_subtle": "#e0f2fe",
        "card": "#ffffff",
        "card_border": "rgba(2, 132, 199, 0.16)",
        "accent": "#0284c7",
        "accent2": "#0369a1",
        "accent_light": "rgba(2, 132, 199, 0.08)",
        "gold": "#0284c7",
        "text": "#082f49",
        "text_heading": "#032034",
        "muted": "#475569",
        "font_heading": "'Playfair Display', Georgia, serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "google_fonts": "family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700",
        "hero_badge": "🌊 Arrivage Frais Quotidien • Pêche Artisanale du Port",
        "hero_img": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=1600&q=80",
        "about_img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=900&q=80",
        "social_img1": "https://images.unsplash.com/photo-1535400255456-984241443b29?auto=format&fit=crop&w=600&q=80",
        "social_img2": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=600&q=80",
        "social_img3": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=600&q=80",
        "tagline": "Pêche du Jour & Spécialités Méditerranéennes",
        "subtitle": "Poissons sauvages, crevettes royales et fruits de mer cuits à la minute sur lit de braise.",
        "usp_pills": ["🌊 Pêche Artisanale du Matin", "🦐 Fruits de Mer Cuits Minute", "⚡ Commande Directe WhatsApp"]
    },
    "bakery": {
        "id": "bakery",
        "layout": "artisanal_boutique",
        "bg": "#fffbf5",
        "bg_subtle": "#fef3c7",
        "card": "#ffffff",
        "card_border": "rgba(217, 119, 6, 0.16)",
        "accent": "#d97706",
        "accent2": "#be123c",
        "accent_light": "rgba(217, 119, 6, 0.08)",
        "gold": "#b45309",
        "text": "#292524",
        "text_heading": "#1c1917",
        "muted": "#78716c",
        "font_heading": "'Fraunces', Georgia, serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "google_fonts": "family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=Plus+Jakarta+Sans:wght@400;500;600;700",
        "hero_badge": "🥐 100% Fait Maison • Levain Naturel & Beurre AOP",
        "hero_img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1600&q=80",
        "about_img": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=900&q=80",
        "social_img1": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80",
        "social_img2": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=600&q=80",
        "social_img3": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80",
        "tagline": "Pâtisserie Fine & Boulangerie Artisanale",
        "subtitle": "Pains au levain naturel, viennoiseries dorées au beurre pur et gâteaux sur-mesure pour vos fêtes.",
        "usp_pills": ["🥖 Farines Françaises & Levain Bio", "🧈 100% Pur Beurre AOP", "⚡ Retrait Express & Livraison"]
    },
    "mandi": {
        "id": "mandi",
        "layout": "royal_heritage",
        "bg": "#fefce8",
        "bg_subtle": "#fef08a",
        "card": "#ffffff",
        "card_border": "rgba(180, 83, 9, 0.16)",
        "accent": "#b45309",
        "accent2": "#c2410c",
        "accent_light": "rgba(180, 83, 9, 0.08)",
        "gold": "#d97706",
        "text": "#1c1917",
        "text_heading": "#0c0a09",
        "muted": "#78716c",
        "font_heading": "'Cinzel', 'Playfair Display', serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "google_fonts": "family=Cinzel:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700",
        "hero_badge": "👑 Recette Ancestrale Mijotée aux 12 Épices Royales",
        "hero_img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=1600&q=80",
        "about_img": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=900&q=80",
        "social_img1": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?auto=format&fit=crop&w=600&q=80",
        "social_img2": "https://images.unsplash.com/photo-1541832676-9b763b0239ab?auto=format&fit=crop&w=600&q=80",
        "social_img3": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=600&q=80",
        "tagline": "Mandi Traditionnel & Biryani aux Épices Royales",
        "subtitle": "Viandes mijotées à l'étouffée servies sur un lit de riz basmati long parfumé au safran.",
        "usp_pills": ["👑 Riz Basmati Long au Safran", "🍖 Agneau Confit Fondant & Épices", "⚡ Plateaux Festifs sur WhatsApp"]
    },
    "home_food": {
        "id": "home_food",
        "layout": "botanical_bistro",
        "bg": "#f0fdf4",
        "bg_subtle": "#dcfce7",
        "card": "#ffffff",
        "card_border": "rgba(5, 150, 105, 0.16)",
        "accent": "#059669",
        "accent2": "#047857",
        "accent_light": "rgba(5, 150, 105, 0.08)",
        "gold": "#10b981",
        "text": "#064e3b",
        "text_heading": "#022c22",
        "muted": "#475569",
        "font_heading": "'Syne', sans-serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "google_fonts": "family=Syne:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700",
        "hero_badge": "🌱 Ingrédients Locaux & Recettes Maison du Marché",
        "hero_img": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1600&q=80",
        "about_img": "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=900&q=80",
        "social_img1": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80",
        "social_img2": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=600&q=80",
        "social_img3": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=600&q=80",
        "tagline": "Cuisine Familiale & Plats Réconfortants Faits Maison",
        "subtitle": "Des recettes authentiques préparées avec amour et des ingrédients du marché sélectionnés chaque matin.",
        "usp_pills": ["🌱 Ingrédients Locaux & Sains", "🍲 Recettes Traditionnelles Maison", "⚡ Commandes Directes en Ligne"]
    },
    "modern": {
        "id": "modern",
        "layout": "contemporary_chic",
        "bg": "#f8fafc",
        "bg_subtle": "#f1f5f9",
        "card": "#ffffff",
        "card_border": "rgba(79, 70, 229, 0.16)",
        "accent": "#4f46e5",
        "accent2": "#4338ca",
        "accent_light": "rgba(79, 70, 229, 0.08)",
        "gold": "#6366f1",
        "text": "#0f172a",
        "text_heading": "#020617",
        "muted": "#64748b",
        "font_heading": "'Space Grotesk', sans-serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "google_fonts": "family=Space+Grotesk:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700",
        "hero_badge": "✨ Gastronomie Contemporaine & Expérience d'Auteur",
        "hero_img": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1600&q=80",
        "about_img": "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=900&q=80",
        "social_img1": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80",
        "social_img2": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=600&q=80",
        "social_img3": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=600&q=80",
        "tagline": "Gastronomie Contemporaine & Expérience Sensorielle",
        "subtitle": "Un mariage raffiné de saveurs traditionnelles et de créativité moderne dans un cadre d'exception.",
        "usp_pills": ["⭐ Créations Gastronomiques d'Auteur", "🍷 Produits de Saison d'Exception", "⚡ Réservation Directe WhatsApp"]
    }
}

def detect_currency(lead_data):
    curr = lead_data.get("currency")
    if curr and curr not in ["$", ""]:
        return curr
    text = (lead_data.get("country", "") + " " + lead_data.get("city", "") + " " + lead_data.get("phone", "")).lower()
    if any(k in text for k in ["tunis", "tunisie", "216"]):
        return "TND"
    elif any(k in text for k in ["qatar", "doha", "974"]):
        return "QAR"
    elif any(k in text for k in ["france", "paris", "lyon", "33"]):
        return "EUR"
    elif any(k in text for k in ["maroc", "morocco", "casablanca", "212"]):
        return "MAD"
    elif any(k in text for k in ["uae", "dubai", "emirates", "971"]):
        return "AED"
    elif any(k in text for k in ["saudi", "riyadh", "jeddah", "966"]):
        return "SAR"
    return "QAR"

def pick_theme_for_lead(lead_data):
    cat_text = (
        str(lead_data.get("category", "")) + " " +
        str(lead_data.get("cuisine", "")) + " " +
        str(lead_data.get("name", ""))
    ).lower()

    # 1. Hotels, Riads, Residences, Resorts, Palaces (Hotel Specific Theme)
    is_fish_dar = any(f in cat_text for f in ["dar el-hout", "dar shat", "dar el hout", "dar el-chouikh", "poisson", "fruits de mer"])
    if any(k in cat_text for k in [
        "hotel", "hôtel", "residence", "résidence", "resort", "palace", "riad",
        "suites", "inn", "hostel", "motel", "chambre d'hote", "guest house", "فندق"
    ]) and not is_fish_dar:
        return THEMES["hotel_luxury"]

    if "hotel" in str(lead_data.get("category", "")).lower():
        return THEMES["hotel_luxury"]

    # 2. Seafood / Poissonnerie
    if any(w in cat_text for w in ["seafood", "fish", "poisson", "fruit de mer", "crevette", "loup", "dorade", "sirene", "sirène", "pecheur", "pêcheur", "dar el-hout", "dar shat"]):
        return THEMES["seafood"]

    # 3. Bakery / Pastry
    if any(w in cat_text for w in ["bakery", "pastry", "cake", "sweet", "dessert", "pain", "boulangerie", "patisserie", "pâtisserie", "croissant"]):
        return THEMES["bakery"]

    # 4. Cafe / Tea / Coffee Roastery / Brunch
    if any(w in cat_text for w in ["cafe", "café", "coffee", "tea", "thé", "salon de the", "salon de thé", "roastery", "espresso", "latte", "lounge", "brunch"]):
        return THEMES["cafe_lounge"]

    # 5. Fast Food / Burgers / Pizza / Snack
    if any(w in cat_text for w in ["burger", "pizza", "fast food", "fast-food", "snack", "tacos", "sandwich", "panini", "street food", "venizia"]):
        return THEMES["fast_food"]

    # 6. Shawarma, Barbecue & Charcoal Grill
    if any(w in cat_text for w in ["shawarma", "chawarma", "grill", "grillade", "turkish", "meat", "bbq", "barbecue", "kebab", "viande", "boucherie", "rotisserie", "charcoal", "mashawi"]):
        return THEMES["shawarma"]

    # 7. Mandi, Biryani, Rice, Couscous & Royal Spices
    if any(w in cat_text for w in ["mandi", "biryani", "afghan", "rice", "curry", "indian", "nepali", "thali", "pakistani", "couscous", "tajine", "oriental", "kabsa"]):
        return THEMES["mandi"]

    # 8. Home Food / Filipino / Asian / Family Kitchen
    if any(w in cat_text for w in ["home", "filipino", "indonesian", "asian", "breakfast", "rozie", "rqaq", "karak", "cantine"]):
        return THEMES["home_food"]

    return THEMES["modern"]

def slugify(text):
    import unicodedata
    clean = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r"[^\w]+", "-", clean.lower()).strip("-")

def get_api_credentials():
    """Load Claude API credentials from config.json or environment."""
    base_url = "https://api.justwoker.icu"
    token = None
    model = "claude-opus-4-8"

    if CONFIG_JSON_FILE.exists():
        try:
            with open(CONFIG_JSON_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                env = cfg.get("env", {})
                base_url = env.get("ANTHROPIC_BASE_URL", base_url)
                token = env.get("ANTHROPIC_AUTH_TOKEN")
                model = env.get("ANTHROPIC_MODEL", model)
        except Exception as e:
            print(f"[MockupGenerator] Error loading config.json: {e}")

    if not token:
        token = os.getenv("ANTHROPIC_AUTH_TOKEN")
        base_url = os.getenv("ANTHROPIC_BASE_URL", base_url)
        model = os.getenv("ANTHROPIC_MODEL", model)

    return base_url, token, model

def extract_social_reference(lead_data):
    """
    Extracts or normalizes social media reference (Instagram handle, Facebook link, TikTok, etc.)
    from the lead's website or custom fields.
    """
    website = (lead_data.get("website", "") or "").strip()
    instagram = (lead_data.get("instagram", "") or "").strip()
    facebook = (lead_data.get("facebook", "") or "").strip()
    tiktok = (lead_data.get("tiktok", "") or "").strip()
    name = lead_data.get("name", "restaurant")
    city_slug = slugify(lead_data.get("city", "ville")).split("-")[0]

    # 1. Instagram direct field
    if instagram:
        handle = instagram.strip().replace("https://www.instagram.com/", "").replace("https://instagram.com/", "").strip("/")
        handle = handle.split("?")[0]
        if not handle.startswith("@"):
            handle = f"@{handle}"
        return {
            "platform": "instagram",
            "handle": handle,
            "url": f"https://instagram.com/{handle.lstrip('@')}"
        }

    # 2. Instagram link in website
    if "instagram.com" in website.lower():
        match = re.search(r"instagram\.com/([^/?#]+)", website)
        if match:
            h = match.group(1).strip()
            if h and h.lower() not in ["p", "reel", "stories", "explore"]:
                return {
                    "platform": "instagram",
                    "handle": f"@{h}",
                    "url": website
                }

    # 3. TikTok
    if tiktok or "tiktok.com" in website.lower():
        tk_src = tiktok or website
        match = re.search(r"tiktok\.com/@?([^/?#]+)", tk_src)
        if match:
            h = match.group(1).strip()
            return {
                "platform": "tiktok",
                "handle": f"@{h}",
                "url": tk_src
            }

    # 4. Facebook
    if facebook or "facebook.com" in website.lower():
        fb_src = facebook or website
        match = re.search(r"facebook\.com/([^/?#]+)", fb_src)
        fb_handle = match.group(1).strip() if match else ""
        if fb_handle and fb_handle.lower() not in ["share", "profile.php", "pages", "groups", "p", "reel"]:
            fb_handle = fb_handle.split("?")[0]
            return {
                "platform": "facebook",
                "handle": f"@{fb_handle}",
                "url": fb_src
            }
        else:
            return {
                "platform": "facebook",
                "handle": f"@{slugify(name).replace('-', '_')}",
                "url": fb_src
            }

    # 5. Smart generated handle based on name and city
    clean_name = re.sub(r'[^a-zA-Z0-9]+', '_', slugify(name)).strip('_')
    generated_handle = f"@{clean_name}_{city_slug}" if city_slug else f"@{clean_name}"
    return {
        "platform": "instagram",
        "handle": generated_handle,
        "url": f"https://instagram.com/{generated_handle.lstrip('@')}"
    }

def fetch_ai_marketing_content(lead_data, theme):
    """
    Uses Claude Opus API from config.json to generate high-converting,
    ultra-tailored copywriting, social proof, menu items, and marketing hooks.
    """
    base_url, token, model = get_api_credentials()
    if not token:
        print("[MockupGenerator] No Anthropic token available; using premium built-in template.")
        return None

    name = lead_data.get("name", "Restaurant")
    category = lead_data.get("category", "") or lead_data.get("cuisine", "Gastronomie")
    city = lead_data.get("city", "Doha")
    country = lead_data.get("country", "Qatar")
    currency = detect_currency(lead_data)
    social_ref = extract_social_reference(lead_data)

    prompt = f"""Tu es le Directeur Artistique & Copywriter Senior pour une prestigieuse agence digitale.
Conçois le contenu marketing haut de gamme pour la maquette du site web de l'établissement suivant :
- Nom : {name}
- Type de cuisine / Catégorie : {category}
- Ville & Pays : {city}, {country}
- Référence Réseaux Sociaux : {social_ref['handle']} ({social_ref['platform']})
- Devise : {currency}

Génère un objet JSON STRICT (sans texte autour, sans markdown) avec la structure exacte suivante :
{{
  "tagline": "Slogan court, percutant et mémorable (ex: Doha's Ultimate Charcoal Grill & Authentic Shawarma)",
  "subtitle": "Description d'accroche de 1-2 phrases soulignant le goût, la fraîcheur et la commande directe WhatsApp.",
  "announcement_badge": "Badge d'annonce exclusif (ex: 🔥 Élu Bestseller 2025 à {city} • Ingrédients 100% Frais)",
  "instagram_handle": "{social_ref['handle']}",
  "followers_count": "15.8k",
  "rating_score": "4.9",
  "review_count": "1,420",
  "story_title": "Titre captivant pour la section Notre Histoire",
  "story_p1": "Paragraphe 1 riche et chaleureux sur la tradition, les saveurs et la passion de l'équipe.",
  "story_p2": "Paragraphe 2 sur la fraîcheur des produits, l'artisanat et la promesse client.",
  "usp_pills": [
    "🔥 Braisé au Feu de Bois",
    "🥩 100% Viande Fraîche du Jour",
    "⚡ Livraison WhatsApp en 30 Min"
  ],
  "dishes": [
    {{
      "name": "Nom du plat signature",
      "category": "Spécialités",
      "price": "38",
      "desc": "Description gourmande et irrésistible avec détails des épices et accompagnements.",
      "badge": "Signature"
    }},
    {{
      "name": "Nom du plat familial / populaire",
      "category": "Plats Chauds",
      "price": "52",
      "desc": "Description gourmande mettant en avant la générosité des portions.",
      "badge": "Bestseller"
    }},
    {{
      "name": "Nom de la formule dégustation",
      "category": "Plats Chauds",
      "price": "75",
      "desc": "Assortiment complet avec sauces maison et accompagnements chauds.",
      "badge": "Recommandé"
    }},
    {{
      "name": "Nom d'une entrée fraîche ou accompagnement",
      "category": "Entrées & Sauces",
      "price": "18",
      "desc": "Fait maison selon la recette secrète du chef.",
      "badge": "Maison"
    }},
    {{
      "name": "Nom d'un dessert ou boisson artisanale",
      "category": "Desserts & Boissons",
      "price": "15",
      "desc": "Touche finale sucrée et rafraîchissante préparée sur place.",
      "badge": "Fait Maison"
    }}
  ],
  "social_posts": [
    {{
      "caption": "Préparation minute sous vos yeux ! Notre engagement : qualité et goût d'exception à chaque bouchée. #foodie #{slugify(city)}",
      "likes": "1.8k",
      "comments": "74",
      "tag": "Reel Tendance"
    }},
    {{
      "caption": "Plateaux prêts pour les livraisons du soir. Commandez en direct sur WhatsApp pour recevoir votre commande ultra chaude ! 🛵",
      "likes": "1.2k",
      "comments": "51",
      "tag": "Story à la Une"
    }},
    {{
      "caption": "Merci à nos fidèles clients à {city} pour vos retours si chaleureux. Vous êtes notre plus grande fierté ❤️",
      "likes": "2.4k",
      "comments": "118",
      "tag": "Avis Client"
    }}
  ],
  "testimonials": [
    {{
      "author": "Karim M.",
      "date": "Il y a 2 jours",
      "rating": 5,
      "comment": "Sans aucun doute la meilleure adresse de {city} ! La viande est tendre, les saveurs sont authentiques et la commande sur WhatsApp est ultra rapide.",
      "verified": true
    }},
    {{
      "author": "Sarah & Omar",
      "date": "La semaine dernière",
      "rating": 5,
      "comment": "Service impeccable, portions très généreuses. C'est devenu notre rituel chaque week-end en famille. Recommandé les yeux fermés !",
      "verified": true
    }},
    {{
      "author": "Dr. Tariq B.",
      "date": "Il y a 3 semaines",
      "rating": 5,
      "comment": "Qualité irréprochable, produits très frais et sauces exquises. Le fait de pouvoir commander directement sans commission change tout.",
      "verified": true
    }}
  ]
}}
Réponds STRICTEMENT par le JSON pur."""

    try:
        payload = {
            "model": model,
            "max_tokens": 900,
            "messages": [{"role": "user", "content": prompt}]
        }
        req = urllib.request.Request(
            f"{base_url}/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": token,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = ""
            if "content" in data and isinstance(data["content"], list):
                for block in data["content"]:
                    if block.get("type") == "text":
                        text = block.get("text", "")
                        break
            if not text and "choices" in data and len(data["choices"]) > 0:
                text = data["choices"][0]["message"]["content"]

            cleaned = re.sub(r"^```json\s*", "", text.strip(), flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            parsed = json.loads(cleaned)
            print(f"[MockupGenerator] AI marketing content successfully generated for {name}!")
            return parsed
    except Exception as e:
        print(f"[MockupGenerator] AI Content generation fallback: {e}")
        return None

def get_hotel_suites(name, city, currency):
    return [
        {
            "name": "Suite Royale Panoramique",
            "category": "Suites Royales",
            "price": "380",
            "desc": f"Notre plus prestigieuse suite offrant une vue imprenable sur {city}. Baignoire balnéo privative, salon séparé et terrasse panoramique.",
            "badge": "Signature 5★",
            "features": ["Lit King-Size Grand Luxe", "Terrasse Privative", "Baignoire Balnéo", "Petit-déjeuner Inclus", "Accès VIP Lounge"],
            "img": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Chambre Executive Prestige",
            "category": "Chambres Executive",
            "price": "240",
            "desc": "Conçue pour les voyageurs exigeants alliant espace de travail raffiné, literie d'exception et salle de bain en marbre.",
            "badge": "Recommandé",
            "features": ["Lit King-Size", "Bureau & Wi-Fi Fibre", "Douche Italienne Marbre", "Minibar Offert"],
            "img": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Suite Junior Élégance",
            "category": "Suites Royales",
            "price": "195",
            "desc": "Une atmosphère douce et feutrée aux tons chauds, idéale pour un séjour romantique ou un moment de détente absolue.",
            "badge": "Coup de Cœur",
            "features": ["Salon Cosy Intégré", "Produits d'Accueil Luxe", "Machine Espresso", "Room Service 24/7"],
            "img": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Chambre Supérieure Sérénité",
            "category": "Chambres Cosy",
            "price": "145",
            "desc": f"Un havre de calme parfaitement insonorisé au cœur de {city}, alliant confort moderne et décoration contemporaine.",
            "badge": "Meilleur Tarif",
            "features": ["Literie Haut de Gamme", "Insonorisation Phonique", "Climatisation Silencieuse", "Coffre-fort"],
            "img": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=800&q=80"
        }
    ]

def render_admin_shell(page_id, page_title, page_content, lead_data, theme, is_hotel):
    settings = load_settings()
    agency_name = settings.get("agency_name", "WebLaunch")
    agency_phone = settings.get("agency_phone", "+216 56 818 880")
    agency_email = settings.get("agency_email", "bellaghayoussef20@gmail.com")

    name = lead_data.get("name", "Établissement")
    city = lead_data.get("city", "Tunis")
    currency = detect_currency(lead_data)
    wa_num = lead_data.get("wa_number", "")
    wa_url = f"https://wa.me/{wa_num}" if wa_num else "#contact"
    brand_icon = "fa-hotel" if is_hotel else "fa-utensils"
    business_type = "Hôtel & Résidence" if is_hotel else "Restaurant & Bar"

    catalog_title = "Suites & Tarifs" if is_hotel else "Carte & Tarifs"
    catalog_url = "admin-rooms.html" if is_hotel else "admin-menu.html"

    admin_nav = [
        {"id": "dashboard", "label": "Tableau de Bord", "icon": "fa-chart-pie", "url": "admin.html"},
        {"id": "reservations", "label": "Réservations & Commandes", "icon": "fa-calendar-check", "url": "admin-reservations.html"},
        {"id": "catalog", "label": catalog_title, "icon": "fa-layer-group", "url": catalog_url},
    ]

    nav_links_html = ""
    for item in admin_nav:
        active_cls = "active" if item["id"] == page_id else ""
        nav_links_html += f"""
        <a href="{item['url']}" class="admin-sidebar-link {active_cls}">
          <i class="fa-solid {item['icon']}"></i>
          <span>{item['label']}</span>
        </a>
        """

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Espace Gérant | {page_title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
  :root {{
    --bg-dark: #0f172a;
    --sidebar-bg: #1e293b;
    --card-bg: #ffffff;
    --main-bg: #f8fafc;
    --accent: {theme.get('accent', '#2563eb')};
    --accent-light: {theme.get('accent_light', 'rgba(37, 99, 235, 0.08)')};
    --text-main: #0f172a;
    --text-muted: #64748b;
    --border: #e2e8f0;
    --font-heading: 'Outfit', sans-serif;
    --font-body: 'Plus Jakarta Sans', sans-serif;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: var(--font-body);
    background: var(--main-bg);
    color: var(--text-main);
    display: flex;
    min-height: 100vh;
  }}
  a {{ text-decoration: none; color: inherit; }}

  /* SIDEBAR */
  .admin-sidebar {{
    width: 280px;
    background: var(--sidebar-bg);
    color: #f1f5f9;
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    z-index: 100;
    padding: 24px 18px;
    border-right: 1px solid rgba(255,255,255,0.08);
  }}
  .admin-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 22px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 25px;
  }}
  .admin-brand-icon {{
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: var(--accent);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
  }}
  .admin-brand-name {{ font-family: var(--font-heading); font-size: 1.15rem; font-weight: 800; color: #fff; line-height: 1.2; }}
  .admin-brand-badge {{ font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }}

  .admin-nav-group {{ display: flex; flex-direction: column; gap: 8px; flex-grow: 1; }}
  .admin-sidebar-link {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 0.92rem;
    font-weight: 600;
    color: #94a3b8;
    transition: 0.2s;
  }}
  .admin-sidebar-link i {{ font-size: 1.1rem; width: 22px; text-align: center; }}
  .admin-sidebar-link:hover {{ background: rgba(255,255,255,0.06); color: #fff; }}
  .admin-sidebar-link.active {{ background: var(--accent); color: #fff; font-weight: 700; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}

  .admin-sidebar-footer {{
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 16px;
    font-size: 0.82rem;
  }}
  .client-site-btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 10px;
    background: rgba(255,255,255,0.1);
    color: #fff;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.85rem;
    margin-top: 10px;
    transition: 0.2s;
  }}
  .client-site-btn:hover {{ background: rgba(255,255,255,0.2); }}

  /* MAIN CONTENT AREA */
  .admin-main {{
    margin-left: 280px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }}
  .admin-topbar {{
    height: 72px;
    background: #ffffff;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    position: sticky;
    top: 0;
    z-index: 80;
  }}
  .admin-content {{
    padding: 32px;
    flex-grow: 1;
  }}

  /* STATS CARDS */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }}
  .kpi-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .kpi-value {{ font-size: 1.8rem; font-weight: 800; color: var(--text-main); font-family: var(--font-heading); margin-top: 4px; }}
  .kpi-label {{ font-size: 0.82rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
  .kpi-icon {{
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.35rem;
  }}

  /* TABLES & CARDS */
  .admin-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 26px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    margin-bottom: 30px;
  }}
  .admin-card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }}
  .admin-card-title {{
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .table-responsive {{ width: 100%; overflow-x: auto; }}
  table.admin-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    text-align: left;
  }}
  table.admin-table th {{
    padding: 12px 16px;
    color: var(--text-muted);
    font-weight: 700;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: #f8fafc;
    border-bottom: 1px solid var(--border);
  }}
  table.admin-table td {{
    padding: 16px;
    border-bottom: 1px solid #f1f5f9;
    color: var(--text-main);
  }}
  table.admin-table tr:hover td {{ background: #fafbfc; }}

  /* BADGES */
  .status-badge {{
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }}
  .status-badge.confirmed {{ background: rgba(16, 185, 129, 0.12); color: #059669; }}
  .status-badge.pending {{ background: rgba(245, 158, 11, 0.12); color: #d97706; }}
  .status-badge.cancelled {{ background: rgba(239, 68, 68, 0.12); color: #dc2626; }}

  .btn-sm-wa {{
    background: #25d366;
    color: #fff;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }}
  .btn-sm-action {{
    background: #f1f5f9;
    color: var(--text-main);
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 700;
    border: 1px solid var(--border);
    cursor: pointer;
  }}
  .btn-sm-action:hover {{ background: #e2e8f0; }}

  @media (max-width: 900px) {{
    .admin-sidebar {{ display: none; }}
    .admin-main {{ margin-left: 0; }}
  }}
</style>
</head>
<body>
  <!-- Sidebar -->
  <aside class="admin-sidebar">
    <div class="admin-brand">
      <div class="admin-brand-icon"><i class="fa-solid {brand_icon}"></i></div>
      <div>
        <div class="admin-brand-name">{name}</div>
        <div class="admin-brand-badge">{business_type} • Back-Office</div>
      </div>
    </div>

    <div class="admin-nav-group">
      <div style="font-size:0.72rem;text-transform:uppercase;color:#64748b;font-weight:800;letter-spacing:1px;padding:0 12px 6px;">Menu Gérant</div>
      {nav_links_html}
    </div>

    <div class="admin-sidebar-footer">
      <div style="color:#94a3b8;font-size:0.76rem;">Propulsé pour {name}</div>
      <div style="font-weight:700;color:#fff;margin:2px 0 6px;">Agence {agency_name}</div>
      <div style="color:#38bdf8;font-size:0.75rem;">Support Pro : {agency_phone}</div>
      <a href="index.html" class="client-site-btn">
        <i class="fa-solid fa-arrow-up-right-from-square"></i> Voir le Site Client
      </a>
    </div>
  </aside>

  <!-- Main View -->
  <div class="admin-main">
    <header class="admin-topbar">
      <div style="display:flex;align-items:center;gap:12px;">
        <span style="background:rgba(16,185,129,0.12);color:#059669;padding:6px 14px;border-radius:20px;font-size:0.82rem;font-weight:700;display:flex;align-items:center;gap:6px;">
          <i class="fa-solid fa-circle" style="font-size:0.6rem;"></i> Établissement Ouvert & Commandes Actives
        </span>
      </div>

      <div style="display:flex;align-items:center;gap:18px;">
        <div style="position:relative;">
          <a href="{wa_url}" target="_blank" class="btn-sm-wa" style="padding:8px 16px;border-radius:20px;">
            <i class="fa-brands fa-whatsapp"></i> Ligne WhatsApp Directe
          </a>
        </div>
        <div style="display:flex;align-items:center;gap:10px;border-left:1px solid var(--border);padding-left:18px;">
          <div style="width:38px;height:38px;border-radius:50%;background:var(--accent-light);color:var(--accent);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.9rem;">
            {name[0].upper()}
          </div>
          <div>
            <div style="font-size:0.86rem;font-weight:700;">Directeur {name}</div>
            <div style="font-size:0.72rem;color:var(--text-muted);">{city}</div>
          </div>
        </div>
      </div>
    </header>

    <main class="admin-content">
      {page_content}
    </main>
  </div>
</body>
</html>
"""
    return html

def build_multipage_demo_bundle(lead_data, theme):
    """
    Builds the complete multi-page bundle including:
    - Customer facing: index.html, menu.html/rooms.html, services.html (if hotel), about.html, contact.html, AND reservation.html
    - Pro Admin portal: admin.html, admin-reservations.html, admin-menu.html / admin-rooms.html
    """
    settings = load_settings()
    agency_name = settings.get("agency_name", "WebLaunch")
    agency_phone = settings.get("agency_phone", "+216 56 818 880")
    agency_email = settings.get("agency_email", "bellaghayoussef20@gmail.com")

    name = lead_data.get("name", "Établissement")
    city = lead_data.get("city", "Tunis")
    country = lead_data.get("country", "Tunisie")
    currency = detect_currency(lead_data)
    wa_num = lead_data.get("wa_number", "")
    wa_url = f"https://wa.me/{wa_num}" if wa_num else "#contact"
    phone = lead_data.get("formatted_phone") or lead_data.get("phone", "+216 71 000 000")
    address = lead_data.get("address", f"{city}, {country}")
    maps_url = lead_data.get("maps_link", f"https://maps.google.com/?q={name}+{city}")

    social_ref = extract_social_reference(lead_data)
    platform = social_ref.get("platform", "instagram")
    platform_icon = "fa-instagram" if platform == "instagram" else ("fa-facebook" if platform == "facebook" else "fa-tiktok")
    handle = social_ref.get("handle", f"@{slugify(name)}")

    is_hotel = (theme.get("id") == "hotel_luxury" or "hotel" in theme.get("id", ""))
    is_cafe = (theme.get("id") == "cafe_lounge")
    is_bakery = (theme.get("id") == "bakery")
    is_fast_food = (theme.get("id") == "fast_food")

    if is_hotel:
        brand_icon = "fa-hotel"
        brand_badge = "Hôtel & Résidence 5★"
        cta_header_text = "Réserver"
        cta_header_link = "reservation.html"
        cta_header_icon = "fa-calendar-check"
    elif is_cafe:
        brand_icon = "fa-mug-hot"
        brand_badge = "Café & Coffee Roastery"
        cta_header_text = "Commander"
        cta_header_link = "menu.html"
        cta_header_icon = "fa-whatsapp"
    elif is_bakery:
        brand_icon = "fa-bread-slice"
        brand_badge = "Boulangerie & Pâtisserie"
        cta_header_text = "Commander"
        cta_header_link = "menu.html"
        cta_header_icon = "fa-whatsapp"
    elif is_fast_food:
        brand_icon = "fa-burger"
        brand_badge = "Street Food & Burgers"
        cta_header_text = "Commander"
        cta_header_link = "menu.html"
        cta_header_icon = "fa-whatsapp"
    elif theme.get("id") == "seafood":
        brand_icon = "fa-fish"
        brand_badge = "Pêche & Fruits de Mer"
        cta_header_text = "Commander"
        cta_header_link = "menu.html"
        cta_header_icon = "fa-whatsapp"
    elif theme.get("id") == "shawarma":
        brand_icon = "fa-fire-flame-curved"
        brand_badge = "Grillades & Broches"
        cta_header_text = "Commander"
        cta_header_link = "menu.html"
        cta_header_icon = "fa-whatsapp"
    else:
        brand_icon = "fa-utensils"
        brand_badge = "Gastronomie & Terroir"
        cta_header_text = "Commander"
        cta_header_link = "menu.html"
        cta_header_icon = "fa-whatsapp"

    # AI Data or rich fallbacks
    ai_data = fetch_ai_marketing_content(lead_data, theme)

    tagline = (ai_data and ai_data.get("tagline")) or theme.get("tagline", "Séjour d'Exception & Sérénité" if is_hotel else "Cuisine d'Excellence & Saveurs Authentiques")
    subtitle = (ai_data and ai_data.get("subtitle")) or theme.get("subtitle", f"Un havre de paix au cœur de {city} alliant élégance moderne et bien-être." if is_hotel else f"Plats préparés à la commande avec des ingrédients frais du jour à {city}.")
    followers = (ai_data and ai_data.get("followers_count")) or "18.4k"
    rating_score = (ai_data and ai_data.get("rating_score")) or "4.9"
    review_count = (ai_data and ai_data.get("review_count")) or "1,380"
    hero_badge_text = theme.get("hero_badge", f"⭐ {rating_score}/5 sur Google Maps • +{review_count} avis certifiés")

    usp_pills = (ai_data and ai_data.get("usp_pills")) or theme.get("usp_pills") or [
        "✨ Excellence & Savoir-Faire",
        "🛎️ Service Attentionné",
        "⚡ Réservation Directe WhatsApp"
    ]
    pills_html = "".join([f'<span class="pill">{p}</span>' for p in usp_pills])

    google_fonts_param = theme.get("google_fonts", "family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700")

    # Import existing data helpers
    from modules.mockup_generator import get_hotel_suites
    suites = get_hotel_suites(name, city, currency)
    dishes = (ai_data and ai_data.get("dishes")) or [
        {
            "name": f"Le Plat Signature {name}",
            "category": "Spécialités",
            "price": "38",
            "desc": "La spécialité secrète de la maison marinée aux épices artisanales et cuite à la perfection.",
            "badge": "Signature"
        },
        {
            "name": "Plateau Dégustation Royal",
            "category": "Plats Chauds",
            "price": "68",
            "desc": "Assortiment généreux pour 2 à 3 personnes avec sauces fraîches maison, pains chauds et garnitures.",
            "badge": "Bestseller"
        },
        {
            "name": "Grillades Mixtes au Feu de Bois",
            "category": "Plats Chauds",
            "price": "52",
            "desc": "Sélection de viandes tendres braisées sur lit de braise, servies avec riz parfumé et frites maison.",
            "badge": "Recommandé"
        },
        {
            "name": "Menu Gourmand Découverte",
            "category": "Plats Chauds",
            "price": "44",
            "desc": "Formule complète avec entrée fraîcheur au choix, plat principal généreux et boisson artisanale.",
            "badge": "Menu Complet"
        },
        {
            "name": "Entrée Fraîcheur & Mezzé Maison",
            "category": "Entrées & Sauces",
            "price": "18",
            "desc": "Préparée chaque matin avec des ingrédients du marché local, huile d'olive vierge et herbes fraîches.",
            "badge": "Fait Maison"
        },
        {
            "name": "Douceur Artisanale & Pâtisserie",
            "category": "Desserts & Boissons",
            "price": "14",
            "desc": "La touche finale gourmande et croustillante préparée sur place selon notre recette traditionnelle.",
            "badge": "Coup de Cœur"
        }
    ]

    # Shared CSS for Customer Site
    shared_css = f"""
    :root {{
      --bg: {theme['bg']};
      --bg-subtle: {theme.get('bg_subtle', '#f8fafc')};
      --card: {theme['card']};
      --card-border: {theme.get('card_border', 'rgba(0,0,0,0.08)')};
      --accent: {theme['accent']};
      --accent2: {theme['accent2']};
      --accent-light: {theme.get('accent_light', 'rgba(180, 83, 9, 0.08)')};
      --gold: {theme['gold']};
      --text: {theme['text']};
      --text-heading: {theme.get('text_heading', '#0f172a')};
      --muted: {theme['muted']};
      --border: rgba(15, 23, 42, 0.08);
      --font-heading: {theme.get('font_heading', "'Outfit', sans-serif")};
      --font-body: {theme.get('font_body', "'Plus Jakarta Sans', sans-serif")};
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: var(--font-body);
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      overflow-x: hidden;
    }}
    h1, h2, h3, h4, h5 {{
      font-family: var(--font-heading);
      letter-spacing: -0.02em;
      color: var(--text-heading);
    }}
    a {{ color: inherit; text-decoration: none; transition: 0.25s; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; }}

    /* DEMO ANNOUNCEMENT BAR */
    .demo-banner {{
      background: linear-gradient(90deg, #0f172a, #1e293b);
      color: #f8fafc;
      padding: 9px 16px;
      font-size: 0.82rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .demo-badge {{
      background: rgba(255,255,255,0.16);
      border: 1px solid rgba(255,255,255,0.25);
      color: #ffffff;
      padding: 3px 12px;
      border-radius: 20px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    .demo-admin-badge {{
      background: linear-gradient(135deg, #3b82f6, #1d4ed8);
      color: #ffffff !important;
      padding: 4px 14px;
      border-radius: 20px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.78rem;
      box-shadow: 0 2px 8px rgba(59,130,246,0.4);
    }}
    .demo-admin-badge:hover {{ filter: brightness(1.1); transform: translateY(-1px); }}
    .demo-agency-link {{ color: #38bdf8; font-weight: 700; }}
    .demo-agency-link:hover {{ text-decoration: underline; }}

    /* HEADER */
    header {{
      position: sticky;
      top: 0;
      z-index: 90;
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    }}
    nav {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 76px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--text-heading);
    }}
    .brand-icon {{
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 1.15rem;
      box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }}
    .brand-meta {{
      font-size: 0.72rem;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--accent);
      letter-spacing: 1px;
      display: block;
      margin-top: -3px;
    }}
    .navlinks {{ display: flex; gap: 18px; list-style: none; align-items: center; }}
    .navlink-item {{
      color: #475569;
      font-weight: 600;
      font-size: 0.90rem;
      padding: 6px 12px;
      border-radius: 8px;
      transition: 0.25s;
      position: relative;
    }}
    .navlink-item:hover {{ color: var(--accent); }}
    .navlink-item.active {{
      color: var(--accent);
      font-weight: 800;
      background: var(--accent-light);
    }}
    .navlink-item.active::after {{
      content: '';
      position: absolute;
      bottom: -8px;
      left: 12px;
      right: 12px;
      height: 3px;
      background: var(--accent);
      border-radius: 2px;
    }}

    .header-actions {{ display: flex; align-items: center; gap: 12px; }}
    .nav-social-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(225, 48, 108, 0.08);
      border: 1px solid rgba(225, 48, 108, 0.2);
      color: #e1306c;
      padding: 7px 14px;
      border-radius: 20px;
      font-size: 0.82rem;
      font-weight: 700;
    }}
    .nav-social-badge:hover {{ background: #e1306c; color: #fff; }}

    .btn-wa {{
      background: #25d366;
      color: #0b2e14;
      padding: 10px 20px;
      border-radius: 30px;
      font-weight: 700;
      font-size: 0.88rem;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: 0.25s;
      box-shadow: 0 4px 14px rgba(37, 211, 102, 0.25);
    }}
    .btn-wa:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(37, 211, 102, 0.4);
      background: #22bf5b;
    }}

    /* SUBPAGE HEADER BANNER */
    .subpage-banner {{
      background: linear-gradient(135deg, var(--bg-subtle) 0%, #ffffff 100%);
      border-bottom: 1px solid var(--border);
      padding: 55px 0 50px;
      position: relative;
    }}
    .breadcrumb-trail {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      color: var(--muted);
      font-weight: 600;
      margin-bottom: 14px;
    }}
    .breadcrumb-trail a {{ color: var(--accent); }}
    .breadcrumb-trail a:hover {{ text-decoration: underline; }}
    .breadcrumb-separator {{ font-size: 0.72rem; opacity: 0.6; }}
    .breadcrumb-current {{ color: var(--text-heading); font-weight: 700; }}
    .subpage-title {{
      font-size: clamp(2rem, 3.8vw, 3rem);
      font-weight: 900;
      color: var(--text-heading);
      margin-bottom: 10px;
    }}
    .subpage-subtitle {{
      font-size: 1.05rem;
      color: var(--muted);
      max-width: 680px;
      line-height: 1.6;
    }}

    /* BUTTONS */
    .btn-primary {{
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      color: #fff;
      padding: 14px 28px;
      border-radius: 30px;
      font-weight: 700;
      font-size: 0.96rem;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 8px 25px rgba(0,0,0,0.12);
      border: none;
      cursor: pointer;
      transition: 0.25s;
    }}
    .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 12px 30px rgba(0,0,0,0.18); }}
    .btn-outline {{
      border: 1px solid rgba(15, 23, 42, 0.16);
      background: #ffffff;
      color: var(--text-heading);
      padding: 14px 26px;
      border-radius: 30px;
      font-weight: 700;
      font-size: 0.96rem;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.03);
      transition: 0.25s;
    }}
    .btn-outline:hover {{ background: #f8fafc; border-color: var(--accent); color: var(--accent); }}

    /* SECTIONS */
    .section {{ padding: 80px 0; position: relative; }}
    .section-tag {{
      color: var(--accent);
      font-weight: 800;
      letter-spacing: 2px;
      text-transform: uppercase;
      font-size: 0.78rem;
      display: block;
      margin-bottom: 10px;
    }}
    .section-title {{
      font-size: clamp(2rem, 3.5vw, 2.7rem);
      font-weight: 800;
      color: var(--text-heading);
      margin-bottom: 18px;
    }}
    .section-sub {{ color: var(--muted); font-size: 1.05rem; max-width: 650px; }}

    /* PILLS */
    .features-pills {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    .pill {{
      background: #ffffff;
      border: 1px solid var(--border);
      padding: 7px 15px;
      border-radius: 20px;
      font-size: 0.84rem;
      font-weight: 600;
      color: var(--text);
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }}

    /* FORMS & INPUTS */
    .form-box {{
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-radius: 24px;
      padding: 34px;
      box-shadow: 0 15px 35px -5px rgba(0,0,0,0.08);
    }}
    .form-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 18px;
    }}
    .form-group {{ display: flex; flex-direction: column; gap: 6px; }}
    .form-group.full {{ grid-column: 1 / -1; }}
    .form-label {{
      font-size: 0.78rem;
      text-transform: uppercase;
      font-weight: 800;
      color: var(--muted);
      letter-spacing: 0.5px;
    }}
    .form-input {{
      width: 100%;
      padding: 12px 16px;
      border-radius: 12px;
      border: 1px solid rgba(15, 23, 42, 0.14);
      font-size: 0.92rem;
      font-family: inherit;
      color: var(--text-heading);
      background: #fdfdfd;
      outline: none;
      transition: 0.25s;
    }}
    .form-input:focus {{ border-color: var(--accent); background: #ffffff; box-shadow: 0 0 0 3px var(--accent-light); }}

    /* FLOATING DIRECT WHATSAPP BUTTON */
    .whatsapp-direct-btn {{
      position: fixed;
      bottom: 28px;
      right: 28px;
      width: 60px;
      height: 60px;
      background: #25d366;
      color: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.8rem;
      box-shadow: 0 8px 30px rgba(37, 211, 102, 0.45);
      z-index: 100;
      transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
      animation: pulseWa 2.5s infinite;
    }}
    .whatsapp-direct-btn:hover {{ transform: scale(1.1); }}
    @keyframes pulseWa {{
      0% {{ box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.55); }}
      70% {{ box-shadow: 0 0 0 18px rgba(37, 211, 102, 0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }}
    }}

    /* FOOTER */
    footer {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 70px 0 35px;
      border-top: 1px solid rgba(255,255,255,0.08);
    }}
    .footer-grid {{
      display: grid;
      grid-template-columns: 1.5fr 1fr 1fr 1.2fr;
      gap: 40px;
      margin-bottom: 50px;
    }}
    .footer-col-title {{
      color: #ffffff;
      font-size: 1.05rem;
      font-weight: 800;
      margin-bottom: 18px;
    }}
    .footer-links {{ list-style: none; }}
    .footer-links li {{ margin-bottom: 10px; }}
    .footer-links a {{ color: #94a3b8; font-size: 0.9rem; }}
    .footer-links a:hover {{ color: #ffffff; }}
    .footer-contact-item {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      font-size: 0.88rem;
      color: #94a3b8;
      margin-bottom: 12px;
    }}
    .footer-contact-item i {{ color: var(--accent); margin-top: 4px; }}
    .footer-bottom {{
      border-top: 1px solid rgba(255,255,255,0.08);
      padding-top: 25px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 15px;
      font-size: 0.82rem;
      color: #64748b;
    }}

    @media (max-width: 900px) {{
      .navlinks {{ display: none; }}
      .footer-grid {{ grid-template-columns: 1fr; gap: 30px; }}
      .form-grid {{ grid-template-columns: 1fr; }}
    }}
    """

    def wrap_page(page_id, page_title, page_content, nav_items, breadcrumb=None, extra_js=""):
        nav_html = ""
        for item in nav_items:
            active_cls = "active" if item["id"] == page_id else ""
            nav_html += f'<li><a href="{item["url"]}" class="navlink-item {active_cls}">{item["label"]}</a></li>'

        breadcrumb_html = ""
        if breadcrumb:
            breadcrumb_html = f"""
            <div class="subpage-banner">
              <div class="container">
                <div class="breadcrumb-trail">
                  <a href="index.html"><i class="fa-solid fa-house"></i> Accueil</a>
                  <span class="breadcrumb-separator"><i class="fa-solid fa-chevron-right"></i></span>
                  <span class="breadcrumb-current">{breadcrumb.get('trail', page_title)}</span>
                </div>
                <h1 class="subpage-title">{breadcrumb.get('title', page_title)}</h1>
                <p class="subpage-subtitle">{breadcrumb.get('subtitle', '')}</p>
              </div>
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="fr" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {page_title}</title>
<meta name="description" content="{name} à {city} — {page_title}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{google_fonts_param}&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
{shared_css}
</style>
</head>
<body>
  <!-- Demo Top Bar -->
  <div class="demo-banner">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <span class="demo-badge">MAQUETTE PRO MULTI-PAGES</span>
      <span>Proposée pour <strong>{name}</strong></span>
    </div>
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <a href="admin.html" class="demo-admin-badge">
        <i class="fa-solid fa-gauge-high"></i> Espace Gérant (Admin)
      </a>
      <span>Agence : <a href="https://wa.me/21656818880" target="_blank" class="demo-agency-link">{agency_name}</a> ({agency_phone})</span>
    </div>
  </div>

  <!-- Header -->
  <header>
    <div class="container">
      <nav>
        <a href="index.html" class="brand">
          <div class="brand-icon"><i class="fa-solid {brand_icon}"></i></div>
          <div>
            <span>{name}</span>
            <span class="brand-meta">{brand_badge}</span>
          </div>
        </a>

        <ul class="navlinks">
          {nav_html}
        </ul>

        <div class="header-actions">
          <a href="{social_ref['url']}" target="_blank" class="nav-social-badge">
            <i class="fa-brands {platform_icon}"></i> {handle}
          </a>
          <a href="{cta_header_link}" class="btn-wa">
            <i class="fa-solid {cta_header_icon}"></i> {cta_header_text}
          </a>
        </div>
      </nav>
    </div>
  </header>

  {breadcrumb_html}

  <main>
    {page_content}
  </main>

  <!-- Floating Direct WhatsApp Button -->
  <a href="{wa_url}?text=Bonjour%20{name}%2C%20je%20souhaite%20des%20renseignements" target="_blank" class="whatsapp-direct-btn" title="Contacter sur WhatsApp">
    <i class="fa-brands fa-whatsapp"></i>
  </a>

  <!-- Footer -->
  <footer>
    <div class="container">
      <div class="footer-grid">
        <div>
          <div class="brand" style="margin-bottom:14px;color:#fff;">
            <div class="brand-icon"><i class="fa-solid {brand_icon}"></i></div>
            <div>
              <span>{name}</span>
              <span class="brand-meta" style="color:#cbd5e1;">{brand_badge}</span>
            </div>
          </div>
          <p style="color:#94a3b8;font-size:0.88rem;max-width:320px;line-height:1.6;margin-bottom:18px;">
            Une expérience exclusive alliant raffinement, service d'exception et contact direct sans intermédiaire.
          </p>
          <a href="{social_ref['url']}" target="_blank" style="display:inline-flex;align-items:center;gap:8px;color:#e1306c;font-weight:700;font-size:0.86rem;">
            <i class="fa-brands {platform_icon}"></i> Suivez-nous sur {handle}
          </a>
        </div>

        <div>
          <div class="footer-col-title">Navigation Rapide</div>
          <ul class="footer-links">
            {nav_html}
            <li><a href="admin.html" style="color:#38bdf8;font-weight:700;"><i class="fa-solid fa-lock" style="font-size:0.75rem;"></i> Espace Gérant (Admin)</a></li>
          </ul>
        </div>

        <div>
          <div class="footer-col-title">Horaires & Service</div>
          <p style="color:#94a3b8;font-size:0.88rem;line-height:1.6;margin-bottom:12px;">
            {'Réception & Conciergerie 24h/24 & 7j/7' if is_hotel else 'Service Continu 7j/7<br>11h30 – 23h30<br>Cuisine ouverte & Livraison rapide'}
          </p>
          <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(16,185,129,0.15);color:#34d399;padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:700;">
            <i class="fa-solid fa-circle" style="font-size:0.6rem;"></i> Ouvert actuellement
          </div>
        </div>

        <div>
          <div class="footer-col-title">Accès & Réservations</div>
          <div class="footer-contact-item">
            <i class="fa-solid fa-location-dot"></i>
            <span>{address}</span>
          </div>
          <div class="footer-contact-item">
            <i class="fa-solid fa-phone"></i>
            <span>{phone}</span>
          </div>
          <div class="footer-contact-item">
            <i class="fa-brands fa-whatsapp" style="color:#25d366;"></i>
            <a href="{wa_url}" target="_blank" style="color:#25d366;font-weight:700;">Ligne Directe WhatsApp</a>
          </div>
          <div style="margin-top:14px;">
            <a href="{maps_url}" target="_blank" class="btn-outline" style="padding:8px 16px;font-size:0.82rem;background:transparent;color:#fff;border-color:rgba(255,255,255,0.2);">
              <i class="fa-solid fa-map-location-dot"></i> Voir sur Google Maps
            </a>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <div>© 2026 {name} • Tous droits réservés.</div>
        <div>Maquette Web Pro & Back-Office réalisés par <strong style="color:#fff;">{agency_name}</strong> ({agency_phone})</div>
      </div>
    </div>
  </footer>

  {extra_js}
</body>
</html>"""

    # Start assembling dictionary of pages
    pages = {}

    # ========================================================
    # 1. CUSTOMER PAGES (HOTEL VS RESTAURANT)
    # ========================================================
    if is_hotel:
        hotel_nav = [
            {"id": "index", "label": "Accueil", "url": "index.html"},
            {"id": "rooms", "label": "Suites & Chambres", "url": "rooms.html"},
            {"id": "services", "label": "Services & Spa", "url": "services.html"},
            {"id": "reservation", "label": "Réservation en Ligne", "url": "reservation.html"},
            {"id": "about", "label": "L'Hôtel", "url": "about.html"},
            {"id": "contact", "label": "Contact & Accès", "url": "contact.html"}
        ]

        # Use existing builders for index, rooms, services, about, contact...
        from modules.mockup_generator import build_multipage_demo_bundle
        base_pages = build_multipage_demo_bundle(lead_data, theme)
        for k, v in base_pages.items():
            pages[k] = v

        # Build dedicated reservation.html for Hotel
        hotel_reservation_content = f"""
        <section class="section">
          <div class="container">
            <div style="display:grid;grid-template-columns:1.2fr 0.8fr;gap:45px;align-items:start;">
              <div class="form-box">
                <span class="section-tag">RÉSERVATION DIRECTE & MEILLEUR TARIF</span>
                <h2 style="font-size:1.85rem;font-weight:800;color:var(--text-heading);margin-bottom:8px;">Planifiez Votre Séjour 5 Étoiles</h2>
                <p style="color:var(--muted);font-size:0.94rem;margin-bottom:26px;">
                  Configurez vos dates et votre suite pour obtenir une confirmation immédiate sans commission d'intermédiaire.
                </p>

                <div class="form-grid">
                  <div class="form-group">
                    <label class="form-label"><i class="fa-regular fa-calendar"></i> Date d'Arrivée (Check-in)</label>
                    <input type="date" id="resIn" class="form-input" onchange="calculateHotelQuote()">
                  </div>
                  <div class="form-group">
                    <label class="form-label"><i class="fa-regular fa-calendar-check"></i> Date de Départ (Check-out)</label>
                    <input type="date" id="resOut" class="form-input" onchange="calculateHotelQuote()">
                  </div>

                  <div class="form-group">
                    <label class="form-label"><i class="fa-solid fa-bed"></i> Choix de la Suite</label>
                    <select id="resSuite" class="form-input" onchange="calculateHotelQuote()">
                      <option value="Suite Royale Panoramique" data-price="380">Suite Royale Panoramique (380 {currency}/nuit)</option>
                      <option value="Chambre Executive Prestige" data-price="240" selected>Chambre Executive Prestige (240 {currency}/nuit)</option>
                      <option value="Suite Junior Élégance" data-price="195">Suite Junior Élégance (195 {currency}/nuit)</option>
                      <option value="Chambre Supérieure Sérénité" data-price="145">Chambre Supérieure Sérénité (145 {currency}/nuit)</option>
                    </select>
                  </div>

                  <div class="form-group">
                    <label class="form-label"><i class="fa-solid fa-user-group"></i> Nombre de Voyageurs</label>
                    <select id="resGuests" class="form-input" onchange="calculateHotelQuote()">
                      <option value="1 Adulte">1 Adulte</option>
                      <option value="2 Adultes" selected>2 Adultes</option>
                      <option value="Famille (2 Adultes + Enfants)">Famille (2 Adultes + Enfants)</option>
                      <option value="Séjour VIP / Délégation">Séjour VIP / Délégation</option>
                    </select>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Nom & Prénom</label>
                    <input type="text" id="resName" class="form-input" placeholder="Ex: Jean Dupont">
                  </div>

                  <div class="form-group">
                    <label class="form-label">Téléphone WhatsApp</label>
                    <input type="text" id="resPhone" class="form-input" placeholder="Ex: +216 XX XXX XXX">
                  </div>

                  <div class="form-group full">
                    <label class="form-label">Options & Services Additionnels</label>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:6px;">
                      <label style="display:flex;align-items:center;gap:10px;font-size:0.88rem;background:#f8fafc;padding:10px 14px;border-radius:10px;border:1px solid #e2e8f0;cursor:pointer;">
                        <input type="checkbox" id="optBreakfast" checked onchange="calculateHotelQuote()"> Petit-déjeuner Buffet Gourmet (Inclus)
                      </label>
                      <label style="display:flex;align-items:center;gap:10px;font-size:0.88rem;background:#f8fafc;padding:10px 14px;border-radius:10px;border:1px solid #e2e8f0;cursor:pointer;">
                        <input type="checkbox" id="optShuttle" onchange="calculateHotelQuote()"> Navette Aéroport VIP (+40 {currency})
                      </label>
                    </div>
                  </div>

                  <div class="form-group full">
                    <label class="form-label">Demandes Spécifiques ou Préférences</label>
                    <textarea id="resNotes" class="form-input" rows="2" placeholder="Étage élevé, arrivée tardive, fleurs d'accueil en chambre..."></textarea>
                  </div>
                </div>

                <button onclick="confirmHotelBookingWhatsApp()" class="btn-primary" style="width:100%;justify-content:center;padding:15px;font-size:1rem;margin-top:10px;">
                  <i class="fa-brands fa-whatsapp"></i> Confirmer la Réservation sur WhatsApp
                </button>
              </div>

              <!-- Live Summary Box -->
              <div>
                <div style="background:#ffffff;border:1px solid var(--card-border);border-radius:24px;padding:30px;box-shadow:0 15px 35px -5px rgba(0,0,0,0.08);position:sticky;top:100px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid var(--border);">
                    <h3 style="font-size:1.15rem;font-weight:800;color:var(--text-heading);">Récapitulatif de Séjour</h3>
                    <span style="background:rgba(16,185,129,0.12);color:#059669;font-weight:800;font-size:0.78rem;padding:4px 10px;border-radius:20px;">Tarif Direct</span>
                  </div>

                  <div style="display:flex;flex-direction:column;gap:12px;font-size:0.92rem;color:var(--text-heading);margin-bottom:20px;">
                    <div style="display:flex;justify-content:space-between;">
                      <span style="color:var(--muted);">Établissement :</span>
                      <strong>{name} 5★</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;">
                      <span style="color:var(--muted);">Durée du séjour :</span>
                      <strong id="summaryNights">2 Nuits</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;">
                      <span style="color:var(--muted);">Suite :</span>
                      <strong id="summarySuite">Chambre Executive Prestige</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;">
                      <span style="color:var(--muted);">Voyageurs :</span>
                      <strong id="summaryGuests">2 Adultes</strong>
                    </div>
                  </div>

                  <div style="background:var(--bg-subtle);border-radius:16px;padding:20px;border:1px solid var(--border);margin-bottom:22px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                      <span style="font-weight:700;color:var(--text-heading);font-size:1.05rem;">Montant Estimé :</span>
                      <div>
                        <span id="summaryTotal" style="font-size:1.8rem;font-weight:900;color:var(--accent);">480</span>
                        <span style="font-weight:800;color:var(--text-heading);">{currency}</span>
                      </div>
                    </div>
                    <div style="font-size:0.78rem;color:var(--muted);margin-top:4px;">Taxes de séjour et Wi-Fi haut débit inclus</div>
                  </div>

                  <div style="font-size:0.82rem;color:var(--muted);line-height:1.6;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;"><i class="fa-solid fa-check" style="color:#10b981;"></i> Annulation sans frais jusqu'à 24h avant</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;"><i class="fa-solid fa-check" style="color:#10b981;"></i> Paiement sécurisé sur place ou à l'arrivée</div>
                    <div style="display:flex;align-items:center;gap:8px;"><i class="fa-solid fa-check" style="color:#10b981;"></i> Prise en charge conciergerie VIP 24h/24</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        """

        hotel_res_js = f"""
        <script>
        function calculateHotelQuote() {{
          const inVal = document.getElementById('resIn').value;
          const outVal = document.getElementById('resOut').value;
          const suiteSel = document.getElementById('resSuite');
          const suiteOption = suiteSel.options[suiteSel.selectedIndex];
          const pricePerNight = Number(suiteOption.getAttribute('data-price') || 240);
          const suiteName = suiteOption.value;
          const guests = document.getElementById('resGuests').value;
          const hasShuttle = document.getElementById('optShuttle').checked;

          let nights = 2;
          if (inVal && outVal) {{
            const d1 = new Date(inVal);
            const d2 = new Date(outVal);
            const diffTime = d2 - d1;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            if (diffDays > 0) nights = diffDays;
          }}

          let total = nights * pricePerNight;
          if (hasShuttle) total += 40;

          document.getElementById('summaryNights').textContent = nights + ' Nuit' + (nights > 1 ? 's' : '');
          document.getElementById('summarySuite').textContent = suiteName;
          document.getElementById('summaryGuests').textContent = guests;
          document.getElementById('summaryTotal').textContent = total;
        }}

        function confirmHotelBookingWhatsApp() {{
          const inVal = document.getElementById('resIn').value;
          const outVal = document.getElementById('resOut').value;
          const suiteSel = document.getElementById('resSuite');
          const suiteName = suiteSel.value;
          const guests = document.getElementById('resGuests').value;
          const name = document.getElementById('resName').value || 'Client';
          const phone = document.getElementById('resPhone').value || '';
          const total = document.getElementById('summaryTotal').textContent;
          const notes = document.getElementById('resNotes').value;
          const hasShuttle = document.getElementById('optShuttle').checked ? 'Oui (+40)' : 'Non';

          let msg = `Bonjour {name} ! Je souhaite confirmer ma réservation de séjour :%0A%0A`;
          msg += `• Voyageur : ${{name}}%0A`;
          if (phone) msg += `• Tél : ${{phone}}%0A`;
          msg += `• Suite : ${{suiteName}}%0A`;
          msg += `• Arrivée : ${{inVal}}%0A`;
          msg += `• Départ : ${{outVal}}%0A`;
          msg += `• Voyageurs : ${{guests}}%0A`;
          msg += `• Navette Aéroport : ${{hasShuttle}}%0A`;
          if (notes) msg += `• Remarques : ${{notes}}%0A`;
          msg += `%0A• Total Estimé : ${{total}} {currency}%0A%0AMerci de me confirmer la réservation et les formalités d'accueil !`;

          window.open(`{wa_url}?text=${{msg}}`, '_blank');
        }}

        window.addEventListener('DOMContentLoaded', () => {{
          const inEl = document.getElementById('resIn');
          const outEl = document.getElementById('resOut');
          if (inEl && outEl) {{
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            const dayAfter = new Date(today);
            dayAfter.setDate(dayAfter.getDate() + 3);
            inEl.value = tomorrow.toISOString().split('T')[0];
            outEl.value = dayAfter.toISOString().split('T')[0];
            calculateHotelQuote();
          }}
        }});
        </script>
        """

        pages["reservation.html"] = wrap_page(
            "reservation", "Réservation en Ligne", hotel_reservation_content, hotel_nav,
            breadcrumb={"trail": "Réservation en Ligne", "title": "Réservation Directe de Votre Séjour", "subtitle": f"Bénéficiez du meilleur tarif direct sans intermédiaire pour votre séjour au {name} à {city}."},
            extra_js=hotel_res_js
        )

    # ========================================================
    # RESTAURANT / CAFE BRANCH
    # ========================================================
    else:
        resto_nav = [
            {"id": "index", "label": "Accueil", "url": "index.html"},
            {"id": "menu", "label": "La Carte", "url": "menu.html"},
            {"id": "reservation", "label": "Réservation de Table", "url": "reservation.html"},
            {"id": "about", "label": "Notre Histoire", "url": "about.html"},
            {"id": "contact", "label": "Contact & Accès", "url": "contact.html"}
        ]

        from modules.mockup_generator import build_multipage_demo_bundle
        base_pages = build_multipage_demo_bundle(lead_data, theme)
        for k, v in base_pages.items():
            pages[k] = v

        # Build dedicated reservation.html for Restaurant
        resto_reservation_content = f"""
        <section class="section">
          <div class="container">
            <div style="display:grid;grid-template-columns:1.2fr 0.8fr;gap:45px;align-items:start;">
              <div class="form-box">
                <span class="section-tag">RÉSERVATION DE TABLE EN DIRECT</span>
                <h2 style="font-size:1.85rem;font-weight:800;color:var(--text-heading);margin-bottom:8px;">Réservez Votre Table en Quelques Clics</h2>
                <p style="color:var(--muted);font-size:0.94rem;margin-bottom:26px;">
                  Choisissez votre date, votre heure et votre zone préférée. Confirmation instantanée par notre maître d'hôtel sur WhatsApp.
                </p>

                <div class="form-grid">
                  <div class="form-group">
                    <label class="form-label"><i class="fa-regular fa-calendar"></i> Date du Repas</label>
                    <input type="date" id="tableResDate" class="form-input" onchange="updateTableSummary()">
                  </div>

                  <div class="form-group">
                    <label class="form-label"><i class="fa-regular fa-clock"></i> Heure du Service</label>
                    <select id="tableResTime" class="form-input" onchange="updateTableSummary()">
                      <optgroup label="Service du Midi (Déjeuner)">
                        <option value="12:15">12:15</option>
                        <option value="12:45" selected>12:45</option>
                        <option value="13:30">13:30</option>
                      </optgroup>
                      <optgroup label="Service du Soir (Dîner)">
                        <option value="19:30">19:30</option>
                        <option value="20:30">20:30</option>
                        <option value="21:30">21:30</option>
                      </optgroup>
                    </select>
                  </div>

                  <div class="form-group">
                    <label class="form-label"><i class="fa-solid fa-users"></i> Nombre de Personnes</label>
                    <select id="tableResGuests" class="form-input" onchange="updateTableSummary()">
                      <option value="1 Personne">1 Personne</option>
                      <option value="2 Personnes" selected>2 Personnes (Table Duo)</option>
                      <option value="4 Personnes">4 Personnes (Famille / Amis)</option>
                      <option value="6 Personnes">6 Personnes</option>
                      <option value="8+ Personnes">8 Personnes ou plus (Grande Table)</option>
                    </select>
                  </div>

                  <div class="form-group">
                    <label class="form-label"><i class="fa-solid fa-chair"></i> Emplacement Souhaité</label>
                    <select id="tableResArea" class="form-input" onchange="updateTableSummary()">
                      <option value="Salle Principale Climatisée" selected>Salle Principale Climatisée</option>
                      <option value="Terrasse Extérieure">Terrasse Extérieure</option>
                      <option value="Espace Salon Intimiste">Espace Salon Intimiste</option>
                    </select>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Nom & Prénom</label>
                    <input type="text" id="tableResName" class="form-input" placeholder="Ex: Karim Ben Salah">
                  </div>

                  <div class="form-group">
                    <label class="form-label">Téléphone WhatsApp</label>
                    <input type="text" id="tableResPhone" class="form-input" placeholder="Ex: +216 XX XXX XXX">
                  </div>

                  <div class="form-group full">
                    <label class="form-label">Occasion Particulière (Optionnel)</label>
                    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:4px;">
                      <button type="button" class="btn-outline" style="padding:6px 14px;font-size:0.8rem;" onclick="setOccasion('Repas d\\\'affaires')">💼 Déjeuner Pro</button>
                      <button type="button" class="btn-outline" style="padding:6px 14px;font-size:0.8rem;" onclick="setOccasion('Anniversaire')">🎂 Anniversaire</button>
                      <button type="button" class="btn-outline" style="padding:6px 14px;font-size:0.8rem;" onclick="setOccasion('Dîner Romantique')">❤️ Romantique</button>
                      <button type="button" class="btn-outline" style="padding:6px 14px;font-size:0.8rem;" onclick="setOccasion('Repas de Famille')">👨‍👩‍👦 Famille</button>
                    </div>
                  </div>

                  <div class="form-group full">
                    <label class="form-label">Remarques ou Préférences Culinaires</label>
                    <textarea id="tableResNotes" class="form-input" rows="2" placeholder="Chaise bébé, table au calme, allergies..."></textarea>
                  </div>
                </div>

                <button onclick="confirmTableBookingWhatsApp()" class="btn-primary" style="width:100%;justify-content:center;padding:15px;font-size:1rem;margin-top:10px;">
                  <i class="fa-brands fa-whatsapp"></i> Envoyer ma Réservation sur WhatsApp
                </button>
              </div>

              <!-- Table Summary Card -->
              <div>
                <div style="background:#ffffff;border:1px solid var(--card-border);border-radius:24px;padding:30px;box-shadow:0 15px 35px -5px rgba(0,0,0,0.08);position:sticky;top:100px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid var(--border);">
                    <h3 style="font-size:1.15rem;font-weight:800;color:var(--text-heading);">Ticket de Réservation</h3>
                    <span style="background:rgba(16,185,129,0.12);color:#059669;font-weight:800;font-size:0.78rem;padding:4px 10px;border-radius:20px;">Direct Cuisine</span>
                  </div>

                  <div style="display:flex;flex-direction:column;gap:14px;font-size:0.92rem;color:var(--text-heading);margin-bottom:22px;">
                    <div style="display:flex;justify-content:space-between;">
                      <span style="color:var(--muted);">Restaurant :</span>
                      <strong>{name}</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;">
                      <span style="color:var(--muted);">Date & Heure :</span>
                      <strong id="summaryTableDateTime">Aujourd'hui à 12:45</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;">
                      <span style="color:var(--muted);">Couverts :</span>
                      <strong id="summaryTableGuests">2 Personnes</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;">
                      <span style="color:var(--muted);">Emplacement :</span>
                      <strong id="summaryTableArea">Salle Principale Climatisée</strong>
                    </div>
                  </div>

                  <div style="background:var(--bg-subtle);border-radius:16px;padding:18px;border:1px solid var(--border);margin-bottom:20px;text-align:center;">
                    <div style="font-size:0.86rem;color:var(--muted);margin-bottom:4px;">Réservation Directe Sans Frais</div>
                    <div style="font-weight:800;color:var(--accent);font-size:1.15rem;">Table Réservée sous votre nom</div>
                  </div>

                  <div style="font-size:0.82rem;color:var(--muted);line-height:1.6;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;"><i class="fa-solid fa-check" style="color:#10b981;"></i> Table gardée 20 minutes après l'horaire</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;"><i class="fa-solid fa-check" style="color:#10b981;"></i> Modification ou annulation facile sur WhatsApp</div>
                    <div style="display:flex;align-items:center;gap:8px;"><i class="fa-solid fa-check" style="color:#10b981;"></i> Accueil chaleureux & service attentionné</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        """

        resto_res_js = f"""
        <script>
        function setOccasion(txt) {{
          const el = document.getElementById('tableResNotes');
          if (el) {{
            el.value = (el.value ? el.value + ' • ' : '') + txt;
          }}
        }}

        function updateTableSummary() {{
          const date = document.getElementById('tableResDate').value;
          const time = document.getElementById('tableResTime').value;
          const guests = document.getElementById('tableResGuests').value;
          const area = document.getElementById('tableResArea').value;

          document.getElementById('summaryTableDateTime').textContent = (date || 'Date choisie') + ' à ' + time;
          document.getElementById('summaryTableGuests').textContent = guests;
          document.getElementById('summaryTableArea').textContent = area;
        }}

        function confirmTableBookingWhatsApp() {{
          const date = document.getElementById('tableResDate').value;
          const time = document.getElementById('tableResTime').value;
          const guests = document.getElementById('tableResGuests').value;
          const area = document.getElementById('tableResArea').value;
          const name = document.getElementById('tableResName').value || 'Client';
          const phone = document.getElementById('tableResPhone').value || '';
          const notes = document.getElementById('tableResNotes').value;

          let msg = `Bonjour {name} ! Je souhaite réserver une table :%0A%0A`;
          msg += `• Nom : ${{name}}%0A`;
          if (phone) msg += `• Tél : ${{phone}}%0A`;
          msg += `• Date : ${{date}}%0A`;
          msg += `• Heure : ${{time}}%0A`;
          msg += `• Couverts : ${{guests}}%0A`;
          msg += `• Emplacement : ${{area}}%0A`;
          if (notes) msg += `• Remarques : ${{notes}}%0A`;
          msg += `%0APouvez-vous me confirmer la table ? Merci beaucoup !`;

          window.open(`{wa_url}?text=${{msg}}`, '_blank');
        }}

        window.addEventListener('DOMContentLoaded', () => {{
          const dEl = document.getElementById('tableResDate');
          if (dEl) {{
            const today = new Date().toISOString().split('T')[0];
            dEl.value = today;
            updateTableSummary();
          }}
        }});
        </script>
        """

        pages["reservation.html"] = wrap_page(
            "reservation", "Réservation de Table", resto_reservation_content, resto_nav,
            breadcrumb={"trail": "Réservation", "title": "Réservez Votre Table en Direct", "subtitle": f"Profitez d'un accueil chaleureux et des meilleures places chez {name} à {city}."},
            extra_js=resto_res_js
        )

    # ========================================================
    # 2. PRO ADMIN PAGES (3 PAGES DÉDIÉES POUR LE GÉRANT)
    # ========================================================
    # render_admin_shell is already defined in scope

    # --- ADMIN PAGE 1: admin.html (Tableau de Bord Exécutif) ---
    if is_hotel:
        kpi_1_val = "14 Confirmées"
        kpi_1_lbl = "Réservations en cours"
        kpi_2_val = "89%"
        kpi_2_lbl = "Taux d'occupation actuel"
        kpi_3_val = f"34,800 {currency}"
        kpi_3_lbl = "Chiffre d'Affaires du Mois"
        kpi_4_val = "4.9 / 5"
        kpi_4_lbl = "Score d'Avis Google & Booking"

        recent_rows = f"""
        <tr>
          <td><strong>#RES-9042</strong></td>
          <td>M. Yassine Mansour<br><span style="font-size:0.78rem;color:#64748b;">+216 98 123 456</span></td>
          <td>Suite Royale Panoramique</td>
          <td>Du 28/09 au 02/10 (4 nuits)</td>
          <td><strong>1,520 {currency}</strong></td>
          <td><span class="status-badge confirmed"><i class="fa-solid fa-circle-check"></i> Confirmé</span></td>
          <td>
            <a href="https://wa.me/21698123456?text=Bonjour%20M.%20Mansour%2C%20votre%20Suite%20Royale%20est%20pr%C3%AAte%20au%20{slugify(name)}" target="_blank" class="btn-sm-wa">
              <i class="fa-brands fa-whatsapp"></i> Échanger
            </a>
          </td>
        </tr>
        <tr>
          <td><strong>#RES-9041</strong></td>
          <td>Sophie Laurent<br><span style="font-size:0.78rem;color:#64748b;">+33 6 12 34 56 78</span></td>
          <td>Chambre Executive Prestige</td>
          <td>Du 29/09 au 01/10 (2 nuits)</td>
          <td><strong>480 {currency}</strong></td>
          <td><span class="status-badge confirmed"><i class="fa-solid fa-circle-check"></i> Confirmé</span></td>
          <td>
            <a href="https://wa.me/33612345678" target="_blank" class="btn-sm-wa">
              <i class="fa-brands fa-whatsapp"></i> Échanger
            </a>
          </td>
        </tr>
        <tr>
          <td><strong>#RES-9039</strong></td>
          <td>Dr. Karim Trabelsi<br><span style="font-size:0.78rem;color:#64748b;">+216 22 789 012</span></td>
          <td>Suite Junior Élégance</td>
          <td>Ce soir (1 nuit)</td>
          <td><strong>195 {currency}</strong></td>
          <td><span class="status-badge pending"><i class="fa-solid fa-clock"></i> Arrivée Proche</span></td>
          <td>
            <a href="https://wa.me/21622789012" target="_blank" class="btn-sm-wa">
              <i class="fa-brands fa-whatsapp"></i> Échanger
            </a>
          </td>
        </tr>
        """
    else:
        kpi_1_val = "38 Commandes"
        kpi_1_lbl = "Commandes & Tables Aujourd'hui"
        kpi_2_val = "46 Couverts"
        kpi_2_lbl = "Réservations ce soir"
        kpi_2_lbl = "Couverts Réservés"
        kpi_3_val = f"2,480 {currency}"
        kpi_3_lbl = "Recettes estimées (Jour)"
        kpi_4_val = "100%"
        kpi_4_lbl = "Commandes sans commission"

        recent_rows = f"""
        <tr>
          <td><strong>#CMD-4182</strong></td>
          <td>Amine K.<br><span style="font-size:0.78rem;color:#64748b;">+216 55 432 109</span></td>
          <td>Table 4 pers. (Terrasse)</td>
          <td>Ce soir à 20h30</td>
          <td><strong>148 {currency}</strong></td>
          <td><span class="status-badge confirmed"><i class="fa-solid fa-circle-check"></i> Table Confirmée</span></td>
          <td>
            <a href="https://wa.me/21655432109?text=Bonjour%20Amine%2C%20votre%20table%20est%20r%C3%A9serv%C3%A9e" target="_blank" class="btn-sm-wa">
              <i class="fa-brands fa-whatsapp"></i> Échanger
            </a>
          </td>
        </tr>
        <tr>
          <td><strong>#CMD-4181</strong></td>
          <td>Salma R.<br><span style="font-size:0.78rem;color:#64748b;">+216 94 887 654</span></td>
          <td>Livraison Express (3 Plats)</td>
          <td>À livrer sous 25 min</td>
          <td><strong>84 {currency}</strong></td>
          <td><span class="status-badge pending"><i class="fa-solid fa-fire"></i> En Cuisine</span></td>
          <td>
            <a href="https://wa.me/21694887654" target="_blank" class="btn-sm-wa">
              <i class="fa-brands fa-whatsapp"></i> Échanger
            </a>
          </td>
        </tr>
        <tr>
          <td><strong>#CMD-4180</strong></td>
          <td>Hassen M.<br><span style="font-size:0.78rem;color:#64748b;">+216 29 112 334</span></td>
          <td>Plateau Dégustation Royal</td>
          <td>À emporter (13h15)</td>
          <td><strong>68 {currency}</strong></td>
          <td><span class="status-badge confirmed"><i class="fa-solid fa-bag-shopping"></i> Prêt</span></td>
          <td>
            <a href="https://wa.me/21629112334" target="_blank" class="btn-sm-wa">
              <i class="fa-brands fa-whatsapp"></i> Échanger
            </a>
          </td>
        </tr>
        """

    admin_dashboard_content = f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:28px;">
      <div>
        <h1 style="font-size:1.8rem;font-weight:900;color:var(--text-main);font-family:var(--font-heading);">Tableau de Bord Exécutif</h1>
        <p style="color:var(--text-muted);font-size:0.92rem;">Vue d'ensemble de l'activité, réservations en temps réel et performance.</p>
      </div>
      <div>
        <span style="font-size:0.82rem;color:var(--text-muted);background:#fff;border:1px solid var(--border);padding:8px 16px;border-radius:20px;font-weight:700;">
          <i class="fa-regular fa-calendar"></i> Aujourd'hui • Mise à jour instantanée
        </span>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div>
          <div class="kpi-label">{kpi_1_lbl}</div>
          <div class="kpi-value">{kpi_1_val}</div>
        </div>
        <div class="kpi-icon" style="background:rgba(37,99,235,0.1);color:#2563eb;"><i class="fa-solid fa-calendar-check"></i></div>
      </div>

      <div class="kpi-card">
        <div>
          <div class="kpi-label">{kpi_2_lbl}</div>
          <div class="kpi-value">{kpi_2_val}</div>
        </div>
        <div class="kpi-icon" style="background:rgba(16,185,129,0.1);color:#059669;"><i class="fa-solid fa-users"></i></div>
      </div>

      <div class="kpi-card">
        <div>
          <div class="kpi-label">{kpi_3_lbl}</div>
          <div class="kpi-value">{kpi_3_val}</div>
        </div>
        <div class="kpi-icon" style="background:rgba(217,119,6,0.1);color:#d97706;"><i class="fa-solid fa-coins"></i></div>
      </div>

      <div class="kpi-card">
        <div>
          <div class="kpi-label">{kpi_4_lbl}</div>
          <div class="kpi-value">{kpi_4_val}</div>
        </div>
        <div class="kpi-icon" style="background:rgba(168,85,247,0.1);color:#9333ea;"><i class="fa-solid fa-shield-halved"></i></div>
      </div>
    </div>

    <!-- Recent Bookings Table -->
    <div class="admin-card">
      <div class="admin-card-header">
        <h2 class="admin-card-title"><i class="fa-solid fa-clock-rotate-left" style="color:var(--accent);"></i> Dernières Réservations & Commandes Directes</h2>
        <a href="admin-reservations.html" style="color:var(--accent);font-weight:700;font-size:0.86rem;">Voir toutes les réservations <i class="fa-solid fa-arrow-right"></i></a>
      </div>

      <div class="table-responsive">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Réf</th>
              <th>Client</th>
              <th>{'Suite Réservée' if is_hotel else 'Prestation / Table'}</th>
              <th>Date / Créneau</th>
              <th>Montant</th>
              <th>Statut</th>
              <th>Contact Direct</th>
            </tr>
          </thead>
          <tbody>
            {recent_rows}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Performance & Insights -->
    <div style="display:grid;grid-template-columns:1.2fr 0.8fr;gap:25px;">
      <div class="admin-card">
        <div class="admin-card-header">
          <h2 class="admin-card-title"><i class="fa-solid fa-chart-simple" style="color:var(--accent);"></i> Fréquentation de la Semaine</h2>
          <span style="font-size:0.8rem;color:var(--text-muted);font-weight:600;">Affluence Hebdomadaire</span>
        </div>
        <div style="display:flex;align-items:flex-end;justify-content:space-between;height:180px;padding-top:20px;">
          <div style="text-align:center;width:12%;"><div style="background:#e2e8f0;height:70px;border-radius:6px;margin-bottom:8px;"></div><span style="font-size:0.75rem;font-weight:700;color:var(--text-muted);">Lun</span></div>
          <div style="text-align:center;width:12%;"><div style="background:#e2e8f0;height:95px;border-radius:6px;margin-bottom:8px;"></div><span style="font-size:0.75rem;font-weight:700;color:var(--text-muted);">Mar</span></div>
          <div style="text-align:center;width:12%;"><div style="background:#e2e8f0;height:120px;border-radius:6px;margin-bottom:8px;"></div><span style="font-size:0.75rem;font-weight:700;color:var(--text-muted);">Mer</span></div>
          <div style="text-align:center;width:12%;"><div style="background:#e2e8f0;height:130px;border-radius:6px;margin-bottom:8px;"></div><span style="font-size:0.75rem;font-weight:700;color:var(--text-muted);">Jeu</span></div>
          <div style="text-align:center;width:12%;"><div style="background:var(--accent);height:170px;border-radius:6px;margin-bottom:8px;"></div><span style="font-size:0.75rem;font-weight:700;color:var(--accent);">Ven</span></div>
          <div style="text-align:center;width:12%;"><div style="background:var(--accent);height:180px;border-radius:6px;margin-bottom:8px;"></div><span style="font-size:0.75rem;font-weight:700;color:var(--accent);">Sam</span></div>
          <div style="text-align:center;width:12%;"><div style="background:var(--accent);height:160px;border-radius:6px;margin-bottom:8px;"></div><span style="font-size:0.75rem;font-weight:700;color:var(--accent);">Dim</span></div>
        </div>
      </div>

      <div class="admin-card">
        <div class="admin-card-header">
          <h2 class="admin-card-title"><i class="fa-solid fa-bolt" style="color:#d97706;"></i> Actions Rapides Gérant</h2>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px;">
          <a href="{'admin-rooms.html' if is_hotel else 'admin-menu.html'}" class="btn-sm-action" style="padding:12px;display:flex;align-items:center;gap:10px;">
            <i class="fa-solid fa-pen-to-square" style="color:var(--accent);"></i>
            <span>Modifier les prix & disponibilités</span>
          </a>
          <a href="admin-reservations.html" class="btn-sm-action" style="padding:12px;display:flex;align-items:center;gap:10px;">
            <i class="fa-solid fa-list-check" style="color:#059669;"></i>
            <span>Traiter les réservations en attente</span>
          </a>
          <a href="index.html" target="_blank" class="btn-sm-action" style="padding:12px;display:flex;align-items:center;gap:10px;">
            <i class="fa-solid fa-eye" style="color:#6366f1;"></i>
            <span>Tester l'expérience client en direct</span>
          </a>
        </div>
      </div>
    </div>
    """
    pages["admin.html"] = render_admin_shell("dashboard", "Tableau de Bord", admin_dashboard_content, lead_data, theme, is_hotel)

    # --- ADMIN PAGE 2: admin-reservations.html (Gestion Complète) ---
    all_reservations_rows = recent_rows + f"""
    <tr>
      <td><strong>#RES-9037</strong></td>
      <td>Mohamed Ali K.<br><span style="font-size:0.78rem;color:#64748b;">+216 97 654 321</span></td>
      <td>{'Suite Junior Élégance' if is_hotel else 'Menu Dégustation 2 pers.'}</td>
      <td>Le 03/10</td>
      <td><strong>{'195' if is_hotel else '92'} {currency}</strong></td>
      <td><span class="status-badge confirmed"><i class="fa-solid fa-circle-check"></i> Confirmé</span></td>
      <td>
        <a href="https://wa.me/21697654321" target="_blank" class="btn-sm-wa"><i class="fa-brands fa-whatsapp"></i> Échanger</a>
      </td>
    </tr>
    <tr>
      <td><strong>#RES-9035</strong></td>
      <td>Inès Bouazizi<br><span style="font-size:0.78rem;color:#64748b;">+216 24 555 777</span></td>
      <td>{'Chambre Supérieure Sérénité' if is_hotel else 'Table Famille (6 Couverts)'}</td>
      <td>Le 05/10</td>
      <td><strong>{'145' if is_hotel else '180'} {currency}</strong></td>
      <td><span class="status-badge pending"><i class="fa-solid fa-clock"></i> En Attente</span></td>
      <td>
        <a href="https://wa.me/21624555777" target="_blank" class="btn-sm-wa"><i class="fa-brands fa-whatsapp"></i> Échanger</a>
      </td>
    </tr>
    """

    admin_reservations_content = f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:28px;">
      <div>
        <h1 style="font-size:1.8rem;font-weight:900;color:var(--text-main);font-family:var(--font-heading);">Gestion des Réservations & Commandes</h1>
        <p style="color:var(--text-muted);font-size:0.92rem;">Consultez, confirmez et échangez directement avec les clients sur WhatsApp.</p>
      </div>
      <div>
        <button onclick="alert('Réservation manuelle ajoutée !')" class="btn-primary" style="padding:10px 20px;font-size:0.88rem;">
          <i class="fa-solid fa-plus"></i> Nouvelle Réservation
        </button>
      </div>
    </div>

    <div class="admin-card">
      <div style="display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap;">
        <button class="btn-sm-action" style="background:var(--accent);color:#fff;border-color:var(--accent);">Toutes (12)</button>
        <button class="btn-sm-action">Confirmées (9)</button>
        <button class="btn-sm-action">En Attente (3)</button>
        <button class="btn-sm-action">Terminées</button>
      </div>

      <div class="table-responsive">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Réf</th>
              <th>Client</th>
              <th>{'Chambre / Suite' if is_hotel else 'Prestation / Table'}</th>
              <th>Date / Séjour</th>
              <th>Total</th>
              <th>Statut</th>
              <th>Action WhatsApp</th>
            </tr>
          </thead>
          <tbody>
            {all_reservations_rows}
          </tbody>
        </table>
      </div>
    </div>
    """
    pages["admin-reservations.html"] = render_admin_shell("reservations", "Gestion des Réservations", admin_reservations_content, lead_data, theme, is_hotel)

    # --- ADMIN PAGE 3: admin-rooms.html (Hôtel) ou admin-menu.html (Restaurant) ---
    if is_hotel:
        rooms_rows = ""
        for s in suites:
            rooms_rows += f"""
            <tr>
              <td>
                <div style="display:flex;align-items:center;gap:12px;">
                  <img src="{s['img']}" alt="{s['name']}" style="width:54px;height:42px;object-fit:cover;border-radius:8px;">
                  <div>
                    <strong>{s['name']}</strong>
                    <div style="font-size:0.75rem;color:var(--text-muted);">{s['badge']}</div>
                  </div>
                </div>
              </td>
              <td><span style="font-weight:700;color:var(--accent);">{s['category']}</span></td>
              <td>
                <div style="display:flex;align-items:center;gap:6px;">
                  <input type="number" value="{s['price']}" style="width:70px;padding:4px 8px;border:1px solid #cbd5e1;border-radius:6px;font-weight:800;font-size:0.9rem;">
                  <span style="font-weight:700;font-size:0.82rem;">{currency}</span>
                </div>
              </td>
              <td>
                <span class="status-badge confirmed"><i class="fa-solid fa-circle"></i> Disponible</span>
              </td>
              <td>
                <button onclick="alert('Tarif mis à jour pour {s['name']} !')" class="btn-sm-action" style="color:var(--accent);font-weight:700;">
                  <i class="fa-solid fa-floppy-disk"></i> Enregistrer
                </button>
              </td>
            </tr>
            """

        admin_catalog_content = f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:28px;">
          <div>
            <h1 style="font-size:1.8rem;font-weight:900;color:var(--text-main);font-family:var(--font-heading);">Gestion des Suites, Chambres & Tarifs</h1>
            <p style="color:var(--text-muted);font-size:0.92rem;">Modifiez instantanément vos prix par nuitée et l'état des suites.</p>
          </div>
          <div>
            <button onclick="alert('Modal d\\'ajout de suite ouvert !')" class="btn-primary" style="padding:10px 20px;font-size:0.88rem;">
              <i class="fa-solid fa-plus"></i> Ajouter une Suite
            </button>
          </div>
        </div>

        <div class="admin-card">
          <div class="table-responsive">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Suite / Chambre</th>
                  <th>Catégorie</th>
                  <th>Prix / Nuit</th>
                  <th>Disponibilité</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {rooms_rows}
              </tbody>
            </table>
          </div>
        </div>
        """
        pages["admin-rooms.html"] = render_admin_shell("catalog", "Gestion des Suites & Tarifs", admin_catalog_content, lead_data, theme, is_hotel)

    else:
        menu_rows = ""
        for d in dishes:
            menu_rows += f"""
            <tr>
              <td>
                <div>
                  <strong>{d['name']}</strong>
                  <div style="font-size:0.75rem;color:var(--text-muted);">{d.get('desc', '')[:55]}...</div>
                </div>
              </td>
              <td><span style="font-weight:700;color:var(--accent);">{d['category']}</span></td>
              <td>
                <div style="display:flex;align-items:center;gap:6px;">
                  <input type="number" value="{d['price']}" style="width:65px;padding:4px 8px;border:1px solid #cbd5e1;border-radius:6px;font-weight:800;font-size:0.9rem;">
                  <span style="font-weight:700;font-size:0.82rem;">{currency}</span>
                </div>
              </td>
              <td>
                <span class="status-badge confirmed"><i class="fa-solid fa-circle"></i> En Stock</span>
              </td>
              <td>
                <button onclick="alert('Prix sauvegardé pour {d['name']} !')" class="btn-sm-action" style="color:var(--accent);font-weight:700;">
                  <i class="fa-solid fa-floppy-disk"></i> Enregistrer
                </button>
              </td>
            </tr>
            """

        admin_catalog_content = f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:28px;">
          <div>
            <h1 style="font-size:1.8rem;font-weight:900;color:var(--text-main);font-family:var(--font-heading);">Gestion de la Carte, Plats & Prix</h1>
            <p style="color:var(--text-muted);font-size:0.92rem;">Ajustez vos tarifs et activez/désactivez des plats en cuisine en direct.</p>
          </div>
          <div>
            <button onclick="alert('Modal d\\'ajout de plat ouvert !')" class="btn-primary" style="padding:10px 20px;font-size:0.88rem;">
              <i class="fa-solid fa-plus"></i> Nouveau Plat
            </button>
          </div>
        </div>

        <div class="admin-card">
          <div class="table-responsive">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Nom du Plat</th>
                  <th>Catégorie</th>
                  <th>Prix Actuel</th>
                  <th>Disponibilité Cuisine</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {menu_rows}
              </tbody>
            </table>
          </div>
        </div>
        """
        pages["admin-menu.html"] = render_admin_shell("catalog", "Gestion de la Carte & Prix", admin_catalog_content, lead_data, theme, is_hotel)

    return pages


def generate_interactive_demo_html(lead_data, theme):
    """
    Backward-compatible entry point returning the index.html content of the multi-page bundle.
    """
    bundle = build_multipage_demo_bundle(lead_data, theme)
    return bundle.get("index.html", "")

def generate_mockup(lead_data):
    """
    1. Generates an ultra-pro, interactive, AI-enhanced HTML website in demos/{slug}/index.html
    2. Takes a real high-res browser screenshot with Selenium Chrome headless
    3. Adds a browser frame with window controls and saves to static/mockups/{slug}.png
    """
    name = lead_data.get("name", "Restaurant")
    slug = slugify(name)
    theme = pick_theme_for_lead(lead_data)

    # 1. Generate Full Multi-Page Website Demo Bundle
    demo_dir = DEMOS_DIR / slug
    demo_dir.mkdir(parents=True, exist_ok=True)
    html_file = demo_dir / "index.html"
    
    pages = build_multipage_demo_bundle(lead_data, theme)
    for filename, page_content in pages.items():
        with open(demo_dir / filename, "w", encoding="utf-8") as f:
            f.write(page_content)

    # 2. Capture screenshot with Selenium Chrome headless
    out_filename = f"{slug}.png"
    out_filepath = MOCKUP_DIR / out_filename
    temp_raw_screenshot = MOCKUP_DIR / f"raw_{slug}.png"

    screenshot_captured = False
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,850")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get(html_file.resolve().as_uri())
        # Small wait for fonts/animations to paint
        import time
        time.sleep(1.8)
        driver.save_screenshot(str(temp_raw_screenshot.resolve()))
        driver.quit()
        screenshot_captured = True
    except Exception as e:
        print(f"[MockupGenerator] Selenium screenshot fallback: {e}")

    # 3. Create browser mockup frame with Pillow
    if screenshot_captured and temp_raw_screenshot.exists():
        try:
            raw_img = Image.open(temp_raw_screenshot)
            # Crop to 1280x800
            content_img = raw_img.crop((0, 0, 1280, 800))

            # Create final canvas with light browser top bar (44px + 800px = 844px)
            final_img = Image.new("RGB", (1280, 844), color=(241, 245, 249))
            draw = ImageDraw.Draw(final_img)

            # Draw sleek light browser chrome
            draw.rectangle([(0, 0), (1280, 44)], fill=(241, 245, 249))
            draw.line([(0, 43), (1280, 43)], fill=(226, 232, 240), width=1)
            
            # Window buttons (macOS style)
            draw.ellipse([(18, 16), (30, 28)], fill=(255, 95, 86))
            draw.ellipse([(38, 16), (50, 28)], fill=(255, 189, 46))
            draw.ellipse([(58, 16), (70, 28)], fill=(39, 201, 63))
            
            # Browser search bar (pure white pill with subtle border and dark slate text)
            draw.rounded_rectangle([(180, 8), (1100, 36)], radius=6, fill=(255, 255, 255), outline=(226, 232, 240))
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
            except Exception:
                font = ImageFont.load_default()
            draw.text((200, 13), f"🔒 https://www.{slug}.com", fill=(71, 85, 105), font=font)

            # Paste webpage
            final_img.paste(content_img, (0, 44))
            final_img.save(out_filepath, format="PNG", optimize=True)
            
            # Cleanup temp raw
            if temp_raw_screenshot.exists():
                temp_raw_screenshot.unlink()

        except Exception as e:
            print(f"[MockupGenerator] Pillow framing failed: {e}")
            if temp_raw_screenshot.exists():
                temp_raw_screenshot.replace(out_filepath)
    else:
        print("[MockupGenerator] Screenshot capture fallback - generating light Pillow mockup")
        try:
            fb_img = Image.new("RGB", (1280, 844), color=(255, 255, 255))
            fb_draw = ImageDraw.Draw(fb_img)
            fb_draw.rectangle([(0, 0), (1280, 44)], fill=(241, 245, 249))
            fb_draw.line([(0, 43), (1280, 43)], fill=(226, 232, 240), width=1)
            fb_draw.ellipse([(18, 16), (30, 28)], fill=(255, 95, 86))
            fb_draw.ellipse([(38, 16), (50, 28)], fill=(255, 189, 46))
            fb_draw.ellipse([(58, 16), (70, 28)], fill=(39, 201, 63))
            fb_draw.rounded_rectangle([(180, 8), (1100, 36)], radius=6, fill=(255, 255, 255), outline=(226, 232, 240))
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
                big_font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36)
            except Exception:
                font = ImageFont.load_default()
                big_font = font
            fb_draw.text((200, 13), f"🔒 https://www.{slug}.com", fill=(71, 85, 105), font=font)
            fb_draw.text((100, 150), name, fill=(15, 23, 42), font=big_font)
            fb_img.save(out_filepath, format="PNG", optimize=True)
        except Exception as fb_err:
            print(f"[MockupGenerator] Pure fallback failed: {fb_err}")

    demo_url = f"/demo/{slug}"
    mockup_url = f"/static/mockups/{out_filename}"

    return {
        "filename": out_filename,
        "filepath": str(out_filepath),
        "url": mockup_url,
        "demo_url": demo_url
    }
