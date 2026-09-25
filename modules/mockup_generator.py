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

def build_multipage_demo_bundle(lead_data, theme):
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
        cta_header_link = "rooms.html"
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

    # Shared CSS Styles
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
      gap: 8px;
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
    .navlinks {{ display: flex; gap: 20px; list-style: none; align-items: center; }}
    .navlink-item {{
      color: #475569;
      font-weight: 600;
      font-size: 0.92rem;
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

    /* SOCIAL PROOF BAR */
    .social-bar {{
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 24px 30px;
      margin-top: -50px;
      position: relative;
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 20px;
      box-shadow: 0 15px 35px -5px rgba(0,0,0,0.08);
    }}
    .social-bar-profile {{ display: flex; align-items: center; gap: 16px; }}
    .social-bar-avatar {{
      width: 56px;
      height: 56px;
      border-radius: 50%;
      padding: 3px;
      background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .social-bar-avatar img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: 50%;
      border: 2px solid #fff;
    }}
    .social-bar-handle {{
      font-weight: 800;
      font-size: 1.15rem;
      color: var(--text-heading);
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .social-bar-stats {{ font-size: 0.88rem; color: var(--muted); }}

    /* REVIEWS & SOCIAL POSTS */
    .reviews-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 24px;
    }}
    .review-card {{
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 26px;
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
    }}
    .review-header {{ display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }}
    .review-avatar {{
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: var(--accent-light);
      color: var(--accent);
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
    }}
    .review-author {{ font-weight: 800; font-size: 0.98rem; color: var(--text-heading); }}
    .review-verified {{ font-size: 0.78rem; color: var(--muted); display: flex; align-items: center; gap: 4px; }}
    .review-verified i {{ color: #10b981; }}
    .review-stars {{ color: #f59e0b; font-size: 0.88rem; margin-bottom: 12px; }}
    .review-text {{ color: var(--text); font-size: 0.92rem; line-height: 1.6; font-style: italic; }}

    .social-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 26px;
    }}
    .social-card {{
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
      transition: 0.3s;
    }}
    .social-card:hover {{ transform: translateY(-4px); box-shadow: 0 16px 32px -6px rgba(0,0,0,0.1); }}
    .social-img {{
      height: 220px;
      background-size: cover;
      background-position: center;
      position: relative;
      padding: 14px;
    }}
    .social-tag {{
      background: rgba(15, 23, 42, 0.8);
      backdrop-filter: blur(8px);
      color: #fff;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 700;
    }}
    .social-overlay {{
      position: absolute;
      bottom: 14px;
      right: 14px;
      display: flex;
      gap: 10px;
    }}
    .social-stat {{
      background: rgba(0,0,0,0.65);
      backdrop-filter: blur(6px);
      color: #fff;
      padding: 4px 10px;
      border-radius: 14px;
      font-size: 0.78rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 5px;
    }}
    .social-body {{ padding: 20px; }}
    .social-caption {{ font-size: 0.9rem; color: var(--text); line-height: 1.5; margin-bottom: 14px; }}
    .social-link-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.84rem;
      font-weight: 700;
      color: #e1306c;
    }}

    /* DISHES & MENU */
    .menu-tabs {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin: 30px 0;
    }}
    .menu-tab {{
      background: #ffffff;
      border: 1px solid var(--card-border);
      color: var(--muted);
      padding: 10px 20px;
      border-radius: 30px;
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
      transition: 0.25s;
    }}
    .menu-tab.active, .menu-tab:hover {{
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
      box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }}
    .menu-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 26px;
    }}
    .dish-card {{
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 26px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: 0.3s;
      box-shadow: 0 8px 22px -4px rgba(0,0,0,0.05);
    }}
    .dish-card:hover {{
      transform: translateY(-5px);
      border-color: var(--accent);
      box-shadow: 0 16px 32px -6px rgba(0,0,0,0.1);
    }}
    .dish-cat-label {{
      font-size: 0.74rem;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--accent);
      letter-spacing: 1px;
      margin-bottom: 4px;
    }}
    .dish-title {{
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--text-heading);
      margin-bottom: 8px;
    }}
    .dish-price-wrap {{ text-align: right; white-space: nowrap; }}
    .dish-price {{ font-size: 1.5rem; font-weight: 900; color: var(--accent); }}
    .dish-curr {{ font-size: 0.85rem; font-weight: 700; color: var(--muted); margin-left: 3px; }}
    .dish-desc {{ color: var(--muted); font-size: 0.92rem; line-height: 1.5; margin-bottom: 20px; flex-grow: 1; }}
    .dish-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 16px;
      border-top: 1px dashed rgba(15, 23, 42, 0.08);
    }}
    .dish-badge {{
      background: var(--accent-light);
      color: var(--accent);
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 0.76rem;
      font-weight: 700;
    }}
    .add-to-cart-btn {{
      background: #f8fafc;
      border: 1px solid rgba(15, 23, 42, 0.12);
      color: var(--text-heading);
      padding: 8px 16px;
      border-radius: 20px;
      font-weight: 700;
      font-size: 0.84rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: 0.25s;
    }}
    .add-to-cart-btn:hover {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }}

    /* HOTEL SUITES */
    .suites-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 30px;
    }}
    .suite-card {{
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-radius: 22px;
      overflow: hidden;
      transition: 0.3s;
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.06);
      display: flex;
      flex-direction: column;
    }}
    .suite-card:hover {{ transform: translateY(-5px); box-shadow: 0 18px 38px -8px rgba(0,0,0,0.12); border-color: var(--accent); }}
    .suite-img {{
      height: 240px;
      background-size: cover;
      background-position: center;
      position: relative;
      padding: 16px;
    }}
    .suite-badge-tag {{
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(8px);
      color: #fff;
      padding: 5px 14px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 800;
    }}
    .suite-body {{ padding: 24px; display: flex; flex-direction: column; flex-grow: 1; }}
    .suite-cat-label {{ font-size: 0.75rem; text-transform: uppercase; font-weight: 800; color: var(--accent); letter-spacing: 1px; }}
    .suite-title {{ font-size: 1.3rem; font-weight: 800; color: var(--text-heading); margin-top: 4px; }}
    .suite-price-wrap {{ text-align: right; white-space: nowrap; }}
    .suite-price {{ font-size: 1.55rem; font-weight: 900; color: var(--accent); }}
    .suite-curr {{ font-size: 0.9rem; font-weight: 800; color: var(--muted); }}
    .suite-per {{ font-size: 0.78rem; color: var(--muted); display: block; margin-top: -3px; }}
    .suite-desc {{ color: var(--muted); font-size: 0.92rem; line-height: 1.6; margin: 14px 0; }}
    .suite-features-wrap {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 22px; }}
    .suite-pill {{
      background: var(--bg-subtle);
      border: 1px solid rgba(0,0,0,0.06);
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--text);
    }}
    .suite-footer {{ margin-top: auto; }}

    /* HOTEL AMENITIES */
    .amenities-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 26px;
    }}
    .amenity-card {{
      background: #ffffff;
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 30px;
      transition: 0.3s;
      box-shadow: 0 8px 22px -4px rgba(0,0,0,0.05);
    }}
    .amenity-card:hover {{ transform: translateY(-4px); border-color: var(--accent); }}
    .amenity-icon {{
      width: 52px;
      height: 52px;
      border-radius: 14px;
      background: var(--accent-light);
      color: var(--accent);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.4rem;
      margin-bottom: 18px;
    }}
    .amenity-title {{ font-size: 1.2rem; font-weight: 800; color: var(--text-heading); margin-bottom: 8px; }}
    .amenity-desc {{ color: var(--muted); font-size: 0.92rem; line-height: 1.6; }}

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

    /* FLOATING CART (RESTAURANTS) */
    .floating-cart-bar {{
      position: fixed;
      bottom: 28px;
      left: 50%;
      transform: translateX(-50%);
      background: #0f172a;
      color: #ffffff;
      padding: 12px 24px;
      border-radius: 40px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      display: none;
      align-items: center;
      gap: 20px;
      z-index: 100;
      border: 1px solid rgba(255,255,255,0.15);
      animation: slideUp 0.3s ease-out;
    }}
    @keyframes slideUp {{
      from {{ transform: translate(-50%, 40px); opacity: 0; }}
      to {{ transform: translate(-50%, 0); opacity: 1; }}
    }}
    .cart-count {{
      background: var(--accent);
      color: #fff;
      width: 26px;
      height: 26px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 0.82rem;
      font-weight: 800;
      margin-right: 6px;
    }}

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

    # Helper to wrap any page in the shared shell
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
    <div style="display:flex;align-items:center;gap:10px;">
      <span class="demo-badge">MAQUETTE PRO MULTI-PAGES</span>
      <span>Proposée avec excellence pour <strong>{name}</strong></span>
    </div>
    <div style="display:flex;align-items:center;gap:14px;">
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
        <div>Maquette Web Pro réalisée par <strong style="color:#fff;">{agency_name}</strong> ({agency_phone})</div>
      </div>
    </div>
  </footer>

  {extra_js}
</body>
</html>"""

    # Common Social Posts and Reviews HTML
    social_images = [theme.get("social_img1"), theme.get("social_img2"), theme.get("social_img3")]
    social_posts = (ai_data and ai_data.get("social_posts")) or [
        {
            "caption": f"Préparation minute sous vos yeux chez {name} 🔥 La passion des saveurs authentiques ! #foodie #{slugify(city)}",
            "likes": "1.8k",
            "comments": "72",
            "tag": "En Cuisine"
        },
        {
            "caption": f"Prêts pour le service du soir. Fraîcheur et générosité garanties à chaque visite chez {name} ! ✨",
            "likes": "1.2k",
            "comments": "48",
            "tag": "Direct WhatsApp"
        },
        {
            "caption": f"Merci à nos fidèles clients de {city} pour vos avis si chaleureux. Vous êtes notre plus belle inspiration ❤️",
            "likes": "2.4k",
            "comments": "115",
            "tag": "Avis Clients"
        }
    ]
    social_feed_html = ""
    for i, post in enumerate(social_posts):
        img_url = social_images[i % len(social_images)]
        social_feed_html += f"""
        <div class="social-card">
          <div class="social-img" style="background-image: url('{img_url}');">
            <span class="social-tag">{post.get('tag', 'Réseaux')}</span>
            <div class="social-overlay">
              <div class="social-stat"><i class="fa-solid fa-heart"></i> {post.get('likes', '1.5k')}</div>
              <div class="social-stat"><i class="fa-solid fa-comment"></i> {post.get('comments', '60')}</div>
            </div>
          </div>
          <div class="social-body">
            <p class="social-caption">{post.get('caption')}</p>
            <a href="{social_ref['url']}" target="_blank" class="social-link-btn">
              <i class="fa-brands {platform_icon}"></i> Voir sur {handle}
            </a>
          </div>
        </div>
        """

    testimonials = (ai_data and ai_data.get("testimonials")) or [
        {
            "author": "Karim M.",
            "date": "Il y a 3 jours",
            "comment": f"Une adresse incontournable à {city} ! Tout est propre, savoureux et la prise de contact WhatsApp est un vrai bonheur de rapidité.",
        },
        {
            "author": "Sarah & Omar",
            "date": "La semaine dernière",
            "comment": "Les portions sont très copieuses et la qualité est constante. Le meilleur rapport qualité-prix sans contestation !",
        },
        {
            "author": "Dr. Tariq B.",
            "date": "Il y a 2 semaines",
            "comment": "Cadre agréable, accueil chaleureux et service rapide. Je recommande vivement pour un déjeuner d'affaires ou un moment en famille.",
        }
    ]
    testimonials_html = ""
    for t in testimonials:
        source_label = "Google Maps & Booking.com" if is_hotel else "Google Maps"
        testimonials_html += f"""
        <div class="review-card">
          <div class="review-header">
            <div class="review-avatar">{t.get('author', 'Client')[0].upper()}</div>
            <div>
              <div class="review-author">{t.get('author')}</div>
              <div class="review-verified"><i class="fa-solid fa-circle-check"></i> Avis vérifié {source_label} • {t.get('date')}</div>
            </div>
          </div>
          <div class="review-stars">
            <i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i>
          </div>
          <p class="review-text">"{t.get('comment')}"</p>
        </div>
        """

    pages = {}

    # ==========================================
    # BRANCH A: HOTEL WEBSITE BUNDLE
    # ==========================================
    if is_hotel:
        hotel_nav = [
            {"id": "index", "label": "Accueil", "url": "index.html"},
            {"id": "rooms", "label": "Suites & Chambres", "url": "rooms.html"},
            {"id": "services", "label": "Services & Spa", "url": "services.html"},
            {"id": "about", "label": "L'Hôtel", "url": "about.html"},
            {"id": "contact", "label": "Réservation & Contact", "url": "contact.html"}
        ]
        suites = get_hotel_suites(name, city, currency)
        
        # 1. Hotel index.html
        hotel_index_content = f"""
        <!-- Hero Section -->
        <section style="padding:70px 0 90px;background:radial-gradient(circle at 85% 20%, var(--accent-light) 0%, transparent 50%), linear-gradient(rgba(255,255,255,0.92), rgba(255,255,255,0.97)), url('{theme['hero_img']}') center/cover no-repeat;background-attachment:fixed;">
          <div class="container">
            <div style="display:grid;grid-template-columns:1.15fr 0.85fr;gap:50px;align-items:center;">
              <div>
                <div style="display:inline-flex;align-items:center;gap:8px;background:#ffffff;border:1px solid var(--border);padding:8px 18px;border-radius:30px;font-size:0.86rem;font-weight:700;color:var(--text-heading);margin-bottom:22px;box-shadow:0 4px 12px rgba(0,0,0,0.04);">
                  <i class="fa-solid fa-crown" style="color:var(--accent);"></i>
                  <span>{hero_badge_text}</span>
                </div>
                <h1 style="font-size:clamp(2.4rem, 4.5vw, 4.2rem);font-weight:900;line-height:1.12;margin-bottom:20px;color:var(--text-heading);">
                  {name}<br>
                  <span style="background:linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{tagline}</span>
                </h1>
                <p style="font-size:clamp(1.05rem, 1.3vw, 1.25rem);color:var(--muted);line-height:1.6;margin-bottom:35px;max-width:680px;">
                  {subtitle}
                </p>
                <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin-bottom:35px;">
                  <a href="{wa_url}?text=Bonjour%20{name}%2C%20je%20souhaite%20r%C3%A9server%20un%20s%C3%A9jour" target="_blank" class="btn-primary">
                    <i class="fa-brands fa-whatsapp"></i> Réserver sur WhatsApp (Direct)
                  </a>
                  <a href="rooms.html" class="btn-outline">
                    <i class="fa-solid fa-bed"></i> Découvrir nos Suites
                  </a>
                </div>
                <div class="features-pills">{pills_html}</div>
              </div>

              <!-- Quick Booking Card -->
              <div>
                <div class="form-box">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid rgba(0,0,0,0.06);">
                    <div>
                      <div style="font-weight:800;font-size:1.15rem;color:var(--text-heading);display:flex;align-items:center;gap:8px;">
                        <i class="fa-solid fa-calendar-check" style="color:var(--accent);"></i> Réservez votre Séjour
                      </div>
                      <div style="font-size:0.82rem;color:var(--muted);margin-top:2px;">Meilleur tarif garanti • Confirmation instantanée</div>
                    </div>
                    <span style="background:rgba(217,119,6,0.12);color:var(--gold);font-weight:800;font-size:0.8rem;padding:4px 10px;border-radius:20px;">5★ Luxe</span>
                  </div>

                  <div class="form-grid">
                    <div class="form-group">
                      <label class="form-label"><i class="fa-regular fa-calendar"></i> Arrivée</label>
                      <input type="date" id="hotelCheckIn" class="form-input">
                    </div>
                    <div class="form-group">
                      <label class="form-label"><i class="fa-regular fa-calendar-check"></i> Départ</label>
                      <input type="date" id="hotelCheckOut" class="form-input">
                    </div>
                    <div class="form-group">
                      <label class="form-label"><i class="fa-solid fa-user-group"></i> Voyageurs</label>
                      <select id="hotelGuests" class="form-input">
                        <option value="1 Adulte">1 Adulte</option>
                        <option value="2 Adultes" selected>2 Adultes</option>
                        <option value="Famille (2 Adultes + Enfants)">Famille (2 Adultes + Enfants)</option>
                        <option value="Séjour VIP / Affaires">Séjour VIP / Affaires</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label class="form-label"><i class="fa-solid fa-bed"></i> Suite souhaitée</label>
                      <select id="hotelSuite" class="form-input">
                        <option value="Suite Royale Panoramique">Suite Royale Panoramique (380 {currency})</option>
                        <option value="Chambre Executive Prestige">Chambre Executive Prestige (240 {currency})</option>
                        <option value="Suite Junior Élégance">Suite Junior Élégance (195 {currency})</option>
                        <option value="Chambre Supérieure Sérénité">Chambre Supérieure Sérénité (145 {currency})</option>
                      </select>
                    </div>
                  </div>

                  <button onclick="bookHotelWhatsApp()" class="btn-primary" style="width:100%;justify-content:center;margin-top:10px;">
                    <i class="fa-brands fa-whatsapp"></i> Vérifier Disponibilité & Réserver
                  </button>
                  <div style="text-align:center;font-size:0.78rem;color:var(--muted);margin-top:12px;">
                    <i class="fa-solid fa-shield-halved" style="color:#10b981;"></i> Réservation sans commission • Conciergerie 24/7
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Social Bar -->
        <div class="container">
          <div class="social-bar">
            <div class="social-bar-profile">
              <div class="social-bar-avatar">
                <img src="{theme['social_img1']}" alt="{name}">
              </div>
              <div>
                <div class="social-bar-handle">{handle} <i class="fa-solid fa-circle-check" style="color:#38bdf8;font-size:0.95rem;"></i></div>
                <div class="social-bar-stats">{followers} abonnés • Résidence de Prestige & Sérénité à {city}</div>
              </div>
            </div>
            <div style="display:flex;gap:20px;align-items:center;">
              <div style="text-align:right;">
                <div style="font-weight:900;font-size:1.2rem;color:var(--text-heading);">{rating_score} / 5 ★★★★★</div>
                <div style="font-size:0.8rem;color:var(--muted);">{review_count} avis certifiés Google & Booking</div>
              </div>
              <a href="{social_ref['url']}" target="_blank" class="btn-outline" style="padding:10px 20px;font-size:0.86rem;">
                <i class="fa-brands {platform_icon}"></i> Suivre
              </a>
            </div>
          </div>
        </div>

        <!-- Featured Suites Preview -->
        <section class="section">
          <div class="container">
            <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:40px;flex-wrap:wrap;gap:20px;">
              <div>
                <span class="section-tag">HOSPITALITÉ DE PRESTIGE</span>
                <h2 class="section-title">Nos Suites Emblématiques</h2>
                <p class="section-sub">Un écrin de luxe conçu pour vous offrir un séjour d'exception au cœur de {city}.</p>
              </div>
              <a href="rooms.html" class="btn-outline" style="padding:10px 22px;font-size:0.9rem;">
                Voir toutes les suites <i class="fa-solid fa-arrow-right"></i>
              </a>
            </div>

            <div class="suites-grid">
              {f'''
              <div class="suite-card">
                <div class="suite-img" style="background-image: url('{suites[0]["img"]}');">
                  <span class="suite-badge-tag">{suites[0]["badge"]}</span>
                </div>
                <div class="suite-body">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                    <div>
                      <span class="suite-cat-label">{suites[0]["category"]}</span>
                      <h3 class="suite-title">{suites[0]["name"]}</h3>
                    </div>
                    <div class="suite-price-wrap">
                      <span class="suite-price">{suites[0]["price"]}</span>
                      <span class="suite-curr">{currency}</span>
                      <span class="suite-per">/ nuit</span>
                    </div>
                  </div>
                  <p class="suite-desc">{suites[0]["desc"]}</p>
                  <div class="suite-features-wrap">
                    {"".join([f'<span class="suite-pill"><i class="fa-solid fa-check"></i> {feat}</span>' for feat in suites[0]["features"][:3]])}
                  </div>
                  <div class="suite-footer">
                    <a href="rooms.html" class="btn-primary" style="width:100%;justify-content:center;padding:12px;">
                      Découvrir cette suite & Réserver
                    </a>
                  </div>
                </div>
              </div>
              <div class="suite-card">
                <div class="suite-img" style="background-image: url('{suites[1]["img"]}');">
                  <span class="suite-badge-tag">{suites[1]["badge"]}</span>
                </div>
                <div class="suite-body">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                    <div>
                      <span class="suite-cat-label">{suites[1]["category"]}</span>
                      <h3 class="suite-title">{suites[1]["name"]}</h3>
                    </div>
                    <div class="suite-price-wrap">
                      <span class="suite-price">{suites[1]["price"]}</span>
                      <span class="suite-curr">{currency}</span>
                      <span class="suite-per">/ nuit</span>
                    </div>
                  </div>
                  <p class="suite-desc">{suites[1]["desc"]}</p>
                  <div class="suite-features-wrap">
                    {"".join([f'<span class="suite-pill"><i class="fa-solid fa-check"></i> {feat}</span>' for feat in suites[1]["features"][:3]])}
                  </div>
                  <div class="suite-footer">
                    <a href="rooms.html" class="btn-primary" style="width:100%;justify-content:center;padding:12px;">
                      Découvrir cette suite & Réserver
                    </a>
                  </div>
                </div>
              </div>
              '''}
            </div>
          </div>
        </section>

        <!-- Services Preview Section -->
        <section class="section" style="background:var(--bg-subtle);">
          <div class="container">
            <div style="text-align:center;max-width:720px;margin:0 auto 40px;">
              <span class="section-tag">PRESTATIONS & BIEN-ÊTRE</span>
              <h2 class="section-title">Installations & Services 5 Étoiles</h2>
              <p class="section-sub" style="margin:0 auto;">Profitez de nos équipements haut de gamme pour vous ressourcer durant votre séjour.</p>
            </div>

            <div class="amenities-grid">
              <div class="amenity-card">
                <div class="amenity-icon"><i class="fa-solid fa-water-ladder"></i></div>
                <h3 class="amenity-title">Piscine & Solarium Privatif</h3>
                <p class="amenity-desc">Bassin chauffé entouré de transats confortables et service de rafraîchissements exclusifs.</p>
              </div>
              <div class="amenity-card">
                <div class="amenity-icon"><i class="fa-solid fa-spa"></i></div>
                <h3 class="amenity-title">Spa & Espace Bien-être</h3>
                <p class="amenity-desc">Hammam traditionnel, sauna finlandais et soins personnalisés par nos thérapeutes experts.</p>
              </div>
              <div class="amenity-card">
                <div class="amenity-icon"><i class="fa-solid fa-bell-concierge"></i></div>
                <h3 class="amenity-title">Conciergerie Privée 24h/24</h3>
                <p class="amenity-desc">Assistance dédiée pour vos réservations exclusives, transferts VIP et découvertes privées.</p>
              </div>
            </div>

            <div style="text-align:center;margin-top:35px;">
              <a href="services.html" class="btn-primary" style="padding:12px 28px;">
                Découvrir l'ensemble de nos services <i class="fa-solid fa-arrow-right"></i>
              </a>
            </div>
          </div>
        </section>

        <!-- Reviews & Social -->
        <section class="section">
          <div class="container">
            <div style="text-align:center;max-width:680px;margin:0 auto 40px;">
              <span class="section-tag">AVIS DE NOS HÔTES</span>
              <h2 class="section-title">Ce Que Disent Nos Voyageurs</h2>
              <p class="section-sub" style="margin:0 auto;">Une réputation d'excellence bâtie sur la confiance et l'attention portée à chaque détail.</p>
            </div>
            <div class="reviews-grid">{testimonials_html}</div>
          </div>
        </section>
        """
        hotel_js = f"""
        <script>
        const waUrl = "{wa_url}";
        const businessName = "{name}";
        function bookHotelWhatsApp() {{
          const checkIn = document.getElementById('hotelCheckIn') ? document.getElementById('hotelCheckIn').value : '';
          const checkOut = document.getElementById('hotelCheckOut') ? document.getElementById('hotelCheckOut').value : '';
          const guests = document.getElementById('hotelGuests') ? document.getElementById('hotelGuests').value : '2 Adultes';
          const suite = document.getElementById('hotelSuite') ? document.getElementById('hotelSuite').value : 'Suite';

          let msg = `Bonjour ${{businessName}} ! Je souhaite réserver un séjour :%0A%0A`;
          msg += `• Suite : ${{suite}}%0A`;
          msg += `• Voyageurs : ${{guests}}%0A`;
          if (checkIn) msg += `• Arrivée : ${{checkIn}}%0A`;
          if (checkOut) msg += `• Départ : ${{checkOut}}%0A`;
          msg += `%0APouvez-vous me confirmer la disponibilité et le tarif pour ces dates ? Merci !`;
          window.open(`${{waUrl}}?text=${{msg}}`, '_blank');
        }}
        window.addEventListener('DOMContentLoaded', () => {{
          const inEl = document.getElementById('hotelCheckIn');
          const outEl = document.getElementById('hotelCheckOut');
          if (inEl && outEl) {{
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            const dayAfter = new Date(today);
            dayAfter.setDate(dayAfter.getDate() + 3);
            inEl.value = tomorrow.toISOString().split('T')[0];
            outEl.value = dayAfter.toISOString().split('T')[0];
          }}
        }});
        </script>
        """
        pages["index.html"] = wrap_page("index", "Accueil & Réservation", hotel_index_content, hotel_nav, extra_js=hotel_js)

        # 2. Hotel rooms.html
        suites_cards_html = ""
        for s in suites:
            feat_tags = "".join([f'<span class="suite-pill"><i class="fa-solid fa-check"></i> {f}</span>' for f in s["features"]])
            encoded_suite = urllib.parse.quote(f"Bonjour {name}, je souhaite réserver la {s['name']} ({s['price']} {currency}/nuit)")
            suites_cards_html += f"""
            <div class="suite-card" data-category="{s['category']}">
              <div class="suite-img" style="background-image: url('{s['img']}');">
                <span class="suite-badge-tag">{s['badge']}</span>
              </div>
              <div class="suite-body">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                  <div>
                    <span class="suite-cat-label">{s['category']}</span>
                    <h3 class="suite-title">{s['name']}</h3>
                  </div>
                  <div class="suite-price-wrap">
                    <span class="suite-price">{s['price']}</span>
                    <span class="suite-curr">{currency}</span>
                    <span class="suite-per">/ nuit</span>
                  </div>
                </div>
                <p class="suite-desc">{s['desc']}</p>
                <div class="suite-features-wrap">
                  {feat_tags}
                </div>
                <div class="suite-footer">
                  <a href="{wa_url}?text={encoded_suite}" target="_blank" class="btn-primary" style="padding:10px 20px;font-size:0.88rem;width:100%;justify-content:center;">
                    <i class="fa-brands fa-whatsapp"></i> Réserver cette Suite
                  </a>
                </div>
              </div>
            </div>
            """
        hotel_rooms_content = f"""
        <section class="section">
          <div class="container">
            <div class="menu-tabs" style="justify-content:center;">
              <button class="menu-tab active" onclick="filterSuites('Tous', this)">Toutes nos Chambres</button>
              <button class="menu-tab" onclick="filterSuites('Suites Royales', this)">Suites Royales</button>
              <button class="menu-tab" onclick="filterSuites('Chambres Executive', this)">Chambres Executive</button>
              <button class="menu-tab" onclick="filterSuites('Chambres Cosy', this)">Chambres Cosy</button>
            </div>

            <div class="suites-grid">
              {suites_cards_html}
            </div>
          </div>
        </section>
        """
        rooms_js = f"""
        <script>
        function filterSuites(category, btnElement) {{
          document.querySelectorAll('.menu-tab').forEach(btn => btn.classList.remove('active'));
          btnElement.classList.add('active');
          const cards = document.querySelectorAll('.suite-card');
          cards.forEach(card => {{
            const cardCat = card.getAttribute('data-category');
            if (category === 'Tous' || cardCat.includes(category)) {{
              card.style.display = 'flex';
            }} else {{
              card.style.display = 'none';
            }}
          }});
        }}
        </script>
        """
        pages["rooms.html"] = wrap_page(
            "rooms", "Suites & Chambres de Prestige", hotel_rooms_content, hotel_nav,
            breadcrumb={"trail": "Suites & Chambres", "title": "Nos Suites & Chambres de Prestige", "subtitle": f"Un havre de confort et de sérénité au cœur de {city} avec service de conciergerie 24/7."},
            extra_js=rooms_js
        )

        # 3. Hotel services.html
        hotel_services_content = f"""
        <section class="section">
          <div class="container">
            <div class="amenities-grid">
              <div class="amenity-card">
                <div class="amenity-icon"><i class="fa-solid fa-water-ladder"></i></div>
                <h3 class="amenity-title">Piscine & Solarium Privatif</h3>
                <p class="amenity-desc">Un bassin d'eau cristalline chauffée, bordé de transats élégants et de cabanes privées. Service de rafraîchissements et cocktails détox servis au bord de l'eau.</p>
              </div>
              <div class="amenity-card">
                <div class="amenity-icon"><i class="fa-solid fa-spa"></i></div>
                <h3 class="amenity-title">Spa & Espace Bien-être Oriental</h3>
                <p class="amenity-desc">Hammam traditionnel en marbre sculpté, rituels aux huiles essentielles rares et massages délassants prodigués par notre équipe de praticiens hautement qualifiés.</p>
              </div>
              <div class="amenity-card">
                <div class="amenity-icon"><i class="fa-solid fa-utensils"></i></div>
                <h3 class="amenity-title">Restaurant Gastronomique & Bar</h3>
                <p class="amenity-desc">Cuisine d'auteur d'inspiration méditerranéenne et locale. Petit-déjeuner buffet gourmet et service en chambre 24h/24 pour satisfaire toutes vos envies à tout instant.</p>
              </div>
              <div class="amenity-card">
                <div class="amenity-icon"><i class="fa-solid fa-car-side"></i></div>
                <h3 class="amenity-title">Service Voiturier & Navette Aéroport VIP</h3>
                <p class="amenity-desc">Transfert haut de gamme depuis et vers les aéroports de {city}. Parking privé surveillé et prise en charge instantanée de votre véhicule par nos voituriers.</p>
              </div>
              <div class="amenity-card">
                <div class="amenity-icon"><i class="fa-solid fa-bell-concierge"></i></div>
                <h3 class="amenity-title">Conciergerie Privée Dédiée 24h/24</h3>
                <p class="amenity-desc">Notre conciergerie veille à exaucer toutes vos exigences : réservations de tables d'exception, billets de spectacles, guides privés et excursions sur-mesure.</p>
              </div>
              <div class="amenity-card">
                <div class="amenity-icon"><i class="fa-solid fa-wifi"></i></div>
                <h3 class="amenity-title">Salons Affaires & Fibre Très Haut Débit</h3>
                <p class="amenity-desc">Connexion Wi-Fi 6 ultra-rapide et sécurisée, salons de réunion feutrés équipés d'écrans 4K et de systèmes de visioconférence pour vos rendez-vous professionnels.</p>
              </div>
            </div>

            <!-- Concierge CTA banner -->
            <div style="background:var(--bg-subtle);border:1px solid var(--card-border);border-radius:24px;padding:45px 35px;text-align:center;margin-top:60px;">
              <span class="section-tag">SERVICE SUR-MESURE</span>
              <h3 style="font-size:1.8rem;font-weight:800;color:var(--text-heading);margin-bottom:12px;">Une Demande Spécifique pour Votre Séjour ?</h3>
              <p style="color:var(--muted);max-width:640px;margin:0 auto 25px;font-size:1rem;">
                Notre conciergerie est disponible instantanément sur WhatsApp pour organiser votre accueil personnalisé avant votre arrivée.
              </p>
              <a href="{wa_url}?text=Bonjour%20{name}%2C%20je%20souhaite%20contacter%20la%20conciergerie" target="_blank" class="btn-primary" style="padding:14px 30px;">
                <i class="fa-brands fa-whatsapp"></i> Échanger avec la Conciergerie Privée
              </a>
            </div>
          </div>
        </section>
        """
        pages["services.html"] = wrap_page(
            "services", "Services & Prestations 5 Étoiles", hotel_services_content, hotel_nav,
            breadcrumb={"trail": "Services & Prestations", "title": "Installations & Services 5 Étoiles", "subtitle": "Des prestations d'exception pensées pour sublimer chaque seconde de votre expérience."}
        )

        # 4. Hotel about.html
        hotel_about_content = f"""
        <section class="section">
          <div class="container">
            <div style="display:grid;grid-template-columns:1.15fr 0.85fr;gap:60px;align-items:center;">
              <div>
                <span class="section-tag">HISTOIRE & ART DE RECEVOIR</span>
                <h2 class="section-title">L'Élégance et l'Hospitalité au Cœur de {city}</h2>
                <p style="color:var(--muted);font-size:1.02rem;line-height:1.7;margin-bottom:20px;">
                  Né de la vision d'offrir une escale hors du temps, <strong>{name}</strong> s'impose comme une référence incontournable de l'hospitalité raffinée. Notre établissement marie avec justesse authenticité architecturale et équipements modernes haut de gamme.
                </p>
                <p style="color:var(--muted);font-size:1.02rem;line-height:1.7;margin-bottom:30px;">
                  Chacun de nos espaces a été dessiné pour susciter la sérénité : hauteurs sous plafond généreuses, matériaux nobles, acoustique travaillée et literie choisie parmi les plus grands artisans du sommeil.
                </p>

                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                  <div style="background:var(--bg-subtle);padding:20px;border-radius:16px;border:1px solid var(--border);">
                    <div style="font-size:1.8rem;font-weight:900;color:var(--accent);margin-bottom:4px;">100%</div>
                    <div style="font-weight:700;color:var(--text-heading);font-size:0.92rem;">Sérénité & Insonorisation</div>
                    <div style="font-size:0.82rem;color:var(--muted);margin-top:2px;">Isolation phonique de pointe</div>
                  </div>
                  <div style="background:var(--bg-subtle);padding:20px;border-radius:16px;border:1px solid var(--border);">
                    <div style="font-size:1.8rem;font-weight:900;color:var(--accent);margin-bottom:4px;">24h/24</div>
                    <div style="font-weight:700;color:var(--text-heading);font-size:0.92rem;">Conciergerie Privée</div>
                    <div style="font-size:0.82rem;color:var(--muted);margin-top:2px;">À votre service permanent</div>
                  </div>
                </div>
              </div>

              <div>
                <img src="{theme['about_img']}" alt="{name}" style="width:100%;height:440px;object-fit:cover;border-radius:24px;border:1px solid var(--card-border);box-shadow:0 20px 45px -10px rgba(0,0,0,0.12);">
              </div>
            </div>
          </div>
        </section>
        """
        pages["about.html"] = wrap_page(
            "about", "L'Établissement & Histoire", hotel_about_content, hotel_nav,
            breadcrumb={"trail": "L'Hôtel", "title": "L'Établissement & Notre Histoire", "subtitle": f"Découvrez l'âme du {name}, où chaque détail raconte une histoire d'élégance et de sérénité."}
        )

        # 5. Hotel contact.html
        hotel_contact_content = f"""
        <section class="section">
          <div class="container">
            <div style="display:grid;grid-template-columns:1.15fr 0.85fr;gap:45px;align-items:start;">
              <!-- Form -->
              <div class="form-box">
                <span class="section-tag">RÉSERVATION DIRECTE GARANTIE</span>
                <h2 style="font-size:1.8rem;font-weight:800;color:var(--text-heading);margin-bottom:8px;">Formulaire de Séjour & Conciergerie</h2>
                <p style="color:var(--muted);font-size:0.92rem;margin-bottom:24px;">Remplissez vos préférences pour recevoir une offre sur-mesure directement sur WhatsApp sous 2 minutes.</p>

                <div class="form-grid">
                  <div class="form-group">
                    <label class="form-label">Nom & Prénom</label>
                    <input type="text" id="guestName" class="form-input" placeholder="Ex: Jean Dupont">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Téléphone WhatsApp</label>
                    <input type="text" id="guestPhone" class="form-input" placeholder="Ex: +216 XX XXX XXX">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Date d'Arrivée</label>
                    <input type="date" id="contactCheckIn" class="form-input">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Date de Départ</label>
                    <input type="date" id="contactCheckOut" class="form-input">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Nombre de Voyageurs</label>
                    <select id="contactGuests" class="form-input">
                      <option value="1 Adulte">1 Adulte</option>
                      <option value="2 Adultes" selected>2 Adultes</option>
                      <option value="Famille (2 Adultes + Enfants)">Famille (2 Adultes + Enfants)</option>
                      <option value="Séjour VIP / Affaires">Séjour VIP / Affaires</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Type de Suite</label>
                    <select id="contactSuite" class="form-input">
                      <option value="Suite Royale Panoramique">Suite Royale Panoramique (380 {currency})</option>
                      <option value="Chambre Executive Prestige">Chambre Executive Prestige (240 {currency})</option>
                      <option value="Suite Junior Élégance">Suite Junior Élégance (195 {currency})</option>
                      <option value="Chambre Supérieure Sérénité">Chambre Supérieure Sérénité (145 {currency})</option>
                    </select>
                  </div>
                  <div class="form-group full">
                    <label class="form-label">Demandes Spécifiques (Optionnel)</label>
                    <textarea id="contactNotes" class="form-input" rows="3" placeholder="Navette aéroport VIP, étage élevé, fleurs d'accueil..."></textarea>
                  </div>
                </div>

                <button onclick="submitHotelContact()" class="btn-primary" style="width:100%;justify-content:center;padding:14px;">
                  <i class="fa-brands fa-whatsapp"></i> Envoyer ma Réservation sur WhatsApp
                </button>
              </div>

              <!-- Information Cards -->
              <div>
                <div style="background:#ffffff;border:1px solid var(--card-border);border-radius:24px;padding:30px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.06);margin-bottom:25px;">
                  <h3 style="font-size:1.2rem;font-weight:800;color:var(--text-heading);margin-bottom:18px;display:flex;align-items:center;gap:10px;">
                    <i class="fa-solid fa-clock" style="color:var(--accent);"></i> Horaires Réception & Check-in
                  </h3>
                  <div style="font-size:0.92rem;color:var(--muted);line-height:1.7;">
                    • Arrivée (Check-in) : à partir de <strong>14h00</strong><br>
                    • Départ (Check-out) : jusqu'à <strong>12h00</strong><br>
                    <span style="color:#10b981;font-weight:700;display:inline-block;margin-top:6px;">
                      <i class="fa-solid fa-circle-check"></i> Réception & Conciergerie ouvertes 24h/24
                    </span>
                  </div>
                </div>

                <div style="background:#ffffff;border:1px solid var(--card-border);border-radius:24px;padding:30px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.06);">
                  <h3 style="font-size:1.2rem;font-weight:800;color:var(--text-heading);margin-bottom:18px;display:flex;align-items:center;gap:10px;">
                    <i class="fa-solid fa-location-dot" style="color:var(--accent);"></i> Localisation & Accès
                  </h3>
                  <p style="font-size:0.92rem;color:var(--muted);margin-bottom:18px;">
                    {address}
                  </p>
                  <a href="{maps_url}" target="_blank" class="btn-outline" style="width:100%;justify-content:center;padding:12px;">
                    <i class="fa-solid fa-map-location-dot"></i> Itinéraire Google Maps
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>
        """
        contact_js = f"""
        <script>
        function submitHotelContact() {{
          const name = document.getElementById('guestName').value || 'Client';
          const phone = document.getElementById('guestPhone').value || '';
          const checkIn = document.getElementById('contactCheckIn').value;
          const checkOut = document.getElementById('contactCheckOut').value;
          const guests = document.getElementById('contactGuests').value;
          const suite = document.getElementById('contactSuite').value;
          const notes = document.getElementById('contactNotes').value;

          let msg = `Bonjour {name} ! Je souhaite réserver un séjour :%0A%0A`;
          msg += `• Nom : ${{name}}%0A`;
          if (phone) msg += `• Tél : ${{phone}}%0A`;
          msg += `• Suite : ${{suite}}%0A`;
          msg += `• Voyageurs : ${{guests}}%0A`;
          if (checkIn) msg += `• Arrivée : ${{checkIn}}%0A`;
          if (checkOut) msg += `• Départ : ${{checkOut}}%0A`;
          if (notes) msg += `• Remarques : ${{notes}}%0A`;
          msg += `%0APouvez-vous me confirmer le tarif et la disponibilité ? Merci !`;
          window.open(`{wa_url}?text=${{msg}}`, '_blank');
        }}
        window.addEventListener('DOMContentLoaded', () => {{
          const inEl = document.getElementById('contactCheckIn');
          const outEl = document.getElementById('contactCheckOut');
          if (inEl && outEl) {{
            const today = new Date();
            const tomorrow = new Date(today);
            tomorrow.setDate(tomorrow.getDate() + 1);
            const dayAfter = new Date(today);
            dayAfter.setDate(dayAfter.getDate() + 3);
            inEl.value = tomorrow.toISOString().split('T')[0];
            outEl.value = dayAfter.toISOString().split('T')[0];
          }}
        }});
        </script>
        """
        pages["contact.html"] = wrap_page(
            "contact", "Réservation & Conciergerie", hotel_contact_content, hotel_nav,
            breadcrumb={"trail": "Réservation & Contact", "title": "Réservation Directe & Conciergerie 24/7", "subtitle": f"Bénéficiez du meilleur tarif garanti sans intermédiaire pour votre séjour à {city}."},
            extra_js=contact_js
        )

    # ==========================================
    # BRANCH B: RESTAURANT / CAFE / BAKERY BUNDLE
    # ==========================================
    else:
        resto_nav = [
            {"id": "index", "label": "Accueil", "url": "index.html"},
            {"id": "menu", "label": "La Carte", "url": "menu.html"},
            {"id": "about", "label": "Notre Histoire", "url": "about.html"},
            {"id": "contact", "label": "Réservation & Accès", "url": "contact.html"}
        ]
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

        cart_js = f"""
        <script>
        const waUrl = "{wa_url}";
        const businessName = "{name}";
        const currency = "{currency}";

        let cart = [];
        function addToCart(dishName, price) {{
          const existing = cart.find(item => item.name === dishName);
          if (existing) {{
            existing.qty += 1;
          }} else {{
            cart.push({{ name: dishName, price: Number(price), qty: 1 }});
          }}
          updateCartUI();
        }}

        function updateCartUI() {{
          const totalItems = cart.reduce((acc, item) => acc + item.qty, 0);
          const totalPrice = cart.reduce((acc, item) => acc + (item.price * item.qty), 0);
          
          const cartBar = document.getElementById('floatingCart');
          if (cartBar) {{
            if (totalItems > 0) {{
              cartBar.style.display = 'flex';
              document.getElementById('cartCount').textContent = totalItems;
              document.getElementById('cartTotal').textContent = totalPrice + ' ' + currency;
            }} else {{
              cartBar.style.display = 'none';
            }}
          }}
        }}

        function checkoutWhatsApp() {{
          if (cart.length === 0) return;
          let orderText = `Bonjour ${{businessName}} ! Je souhaite commander en livraison :%0A%0A`;
          let total = 0;
          cart.forEach(item => {{
            const sub = item.price * item.qty;
            total += sub;
            orderText += `• ${{item.qty}}x ${{item.name}} (${{sub}} ${{currency}})%0A`;
          }});
          orderText += `%0ATotal : ${{total}} ${{currency}}%0A%0AMerci de me confirmer le délai estimé !`;
          window.open(`${{waUrl}}?text=${{orderText}}`, '_blank');
        }}

        function filterMenu(category, btnElement) {{
          document.querySelectorAll('.menu-tab').forEach(btn => btn.classList.remove('active'));
          btnElement.classList.add('active');

          const cards = document.querySelectorAll('.dish-card');
          cards.forEach(card => {{
            const cardCat = card.getAttribute('data-category');
            if (category === 'Tous' || cardCat.includes(category)) {{
              card.style.display = 'flex';
            }} else {{
              card.style.display = 'none';
            }}
          }});
        }}
        </script>
        """

        # 1. Restaurant index.html
        top_dishes_html = ""
        for d in dishes[:3]:
            badge_html = f'<span class="dish-badge">{d.get("badge", "Signature")}</span>'
            top_dishes_html += f"""
            <div class="dish-card" data-category="{d.get('category', 'Spécialités')}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                <div>
                  <div class="dish-cat-label">{d.get('category', 'Menu')}</div>
                  <h3 class="dish-title">{d.get('name')}</h3>
                </div>
                <div class="dish-price-wrap">
                  <span class="dish-price">{d.get('price')}</span>
                  <span class="dish-curr">{currency}</span>
                </div>
              </div>
              <p class="dish-desc">{d.get('desc')}</p>
              <div class="dish-footer">
                {badge_html}
                <button class="add-to-cart-btn" onclick="addToCart('{d.get('name').replace("'", " ")}', {d.get('price')})">
                  <i class="fa-solid fa-plus"></i> Ajouter au panier
                </button>
              </div>
            </div>
            """

        resto_index_content = f"""
        <!-- Hero Section -->
        <section style="padding:70px 0 90px;background:radial-gradient(circle at 85% 20%, var(--accent-light) 0%, transparent 50%), linear-gradient(rgba(255,255,255,0.92), rgba(255,255,255,0.97)), url('{theme['hero_img']}') center/cover no-repeat;background-attachment:fixed;">
          <div class="container">
            <div style="display:grid;grid-template-columns:1.15fr 0.85fr;gap:50px;align-items:center;">
              <div>
                <div style="display:inline-flex;align-items:center;gap:8px;background:#ffffff;border:1px solid var(--border);padding:8px 18px;border-radius:30px;font-size:0.86rem;font-weight:700;color:var(--text-heading);margin-bottom:22px;box-shadow:0 4px 12px rgba(0,0,0,0.04);">
                  <i class="fa-solid {brand_icon}" style="color:var(--accent);"></i>
                  <span>{hero_badge_text}</span>
                </div>
                <h1 style="font-size:clamp(2.4rem, 4.5vw, 4.2rem);font-weight:900;line-height:1.12;margin-bottom:20px;color:var(--text-heading);">
                  {name}<br>
                  <span style="background:linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{tagline}</span>
                </h1>
                <p style="font-size:clamp(1.05rem, 1.3vw, 1.25rem);color:var(--muted);line-height:1.6;margin-bottom:35px;max-width:680px;">
                  {subtitle}
                </p>
                <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin-bottom:35px;">
                  <a href="{wa_url}?text=Bonjour%20{name}%2C%20je%20souhaite%20commander%20en%20direct" target="_blank" class="btn-primary">
                    <i class="fa-brands fa-whatsapp"></i> Commander sur WhatsApp (Direct)
                  </a>
                  <a href="menu.html" class="btn-outline">
                    <i class="fa-solid fa-utensils"></i> Découvrir la Carte
                  </a>
                </div>
                <div class="features-pills">{pills_html}</div>
              </div>

              <!-- Floating Food Card -->
              <div>
                <div style="background:#ffffff;border-radius:24px;border:1px solid var(--card-border);overflow:hidden;box-shadow:0 20px 45px -10px rgba(0,0,0,0.12);position:relative;">
                  <img src="{theme['about_img']}" alt="{name}" style="width:100%;height:270px;object-fit:cover;">
                  <div style="position:absolute;top:16px;left:16px;background:var(--accent);color:#fff;padding:5px 14px;border-radius:20px;font-size:0.78rem;font-weight:800;">
                    🔥 Préparation Artisanale Minute
                  </div>
                  <div style="padding:22px;">
                    <div style="font-weight:800;font-size:1.15rem;color:var(--text-heading);">{name} Expérience</div>
                    <div style="color:var(--muted);font-size:0.88rem;margin:4px 0 12px;">Ingrédients frais du jour préparés avec passion à {city}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                      <span style="font-size:1.25rem;font-weight:900;color:var(--accent);">{rating_score} ★★★★★</span>
                      <a href="menu.html" class="btn-wa" style="padding:8px 16px;font-size:0.82rem;">Voir la Carte</a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Social Bar -->
        <div class="container">
          <div class="social-bar">
            <div class="social-bar-profile">
              <div class="social-bar-avatar">
                <img src="{theme['social_img1']}" alt="{name}">
              </div>
              <div>
                <div class="social-bar-handle">{handle} <i class="fa-solid fa-circle-check" style="color:#38bdf8;font-size:0.95rem;"></i></div>
                <div class="social-bar-stats">{followers} abonnés • Saveurs authentiques & Fait maison à {city}</div>
              </div>
            </div>
            <div style="display:flex;gap:20px;align-items:center;">
              <div style="text-align:right;">
                <div style="font-weight:900;font-size:1.2rem;color:var(--text-heading);">{rating_score} / 5 ★★★★★</div>
                <div style="font-size:0.8rem;color:var(--muted);">{review_count} avis clients vérifiés Google</div>
              </div>
              <a href="{social_ref['url']}" target="_blank" class="btn-outline" style="padding:10px 20px;font-size:0.86rem;">
                <i class="fa-brands {platform_icon}"></i> Suivre
              </a>
            </div>
          </div>
        </div>

        <!-- Featured Dishes Section -->
        <section class="section">
          <div class="container">
            <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:35px;flex-wrap:wrap;gap:20px;">
              <div>
                <span class="section-tag">NOS SPÉCIALITÉS VEDETTES</span>
                <h2 class="section-title">Les Incontournables de la Maison</h2>
                <p class="section-sub">Découvrez nos créations les plus appréciées, préparées minute avec amour.</p>
              </div>
              <a href="menu.html" class="btn-primary" style="padding:12px 24px;font-size:0.9rem;">
                Consulter toute la Carte <i class="fa-solid fa-arrow-right"></i>
              </a>
            </div>

            <div class="menu-grid">
              {top_dishes_html}
            </div>
          </div>
        </section>

        <!-- About Teaser Section -->
        <section class="section" style="background:var(--bg-subtle);">
          <div class="container">
            <div style="display:grid;grid-template-columns:1.15fr 0.85fr;gap:50px;align-items:center;">
              <div>
                <span class="section-tag">SAVOIR-FAIRE & PASSION</span>
                <h2 class="section-title">La Promesse de l'Authenticité</h2>
                <p style="color:var(--muted);font-size:1.02rem;line-height:1.7;margin-bottom:18px;">
                  Chez <strong>{name}</strong>, chaque plat est préparé sur place dans le respect des recettes authentiques. Nous sélectionnons nos matières premières auprès de producteurs rigoureusement choisis pour vous garantir une fraîcheur et une générosité incomparables.
                </p>
                <div style="display:flex;gap:15px;flex-wrap:wrap;margin-bottom:28px;">
                  <span class="pill"><i class="fa-solid fa-leaf" style="color:#10b981;"></i> 100% Ingrédients Frais</span>
                  <span class="pill"><i class="fa-solid fa-fire" style="color:var(--accent);"></i> Cuisson Minute</span>
                  <span class="pill"><i class="fa-solid fa-heart" style="color:#e11d48;"></i> Fait Maison</span>
                </div>
                <a href="about.html" class="btn-outline">
                  Lire notre histoire complète <i class="fa-solid fa-arrow-right"></i>
                </a>
              </div>
              <div>
                <img src="{theme['about_img']}" alt="{name}" style="width:100%;height:380px;object-fit:cover;border-radius:24px;border:1px solid var(--card-border);box-shadow:0 15px 35px -5px rgba(0,0,0,0.1);">
              </div>
            </div>
          </div>
        </section>

        <!-- Reviews & Social Feed -->
        <section class="section">
          <div class="container">
            <div style="text-align:center;max-width:680px;margin:0 auto 40px;">
              <span class="section-tag">AVIS CLIENTS</span>
              <h2 class="section-title">Ils Ont Adoré Leurs Visites</h2>
              <p class="section-sub" style="margin:0 auto;">La satisfaction de nos convives est notre plus grande récompense au quotidien.</p>
            </div>
            <div class="reviews-grid">{testimonials_html}</div>

            <div style="text-align:center;max-width:680px;margin:70px auto 40px;">
              <span class="section-tag">COMMUNAUTÉ INSTAGRAM</span>
              <h2 class="section-title">En Direct de Notre Cuisine</h2>
              <p class="section-sub" style="margin:0 auto;">Retrouvez nos coulisses, nos nouveautés et les moments partagés avec vous.</p>
            </div>
            <div class="social-grid">{social_feed_html}</div>
          </div>
        </section>

        <!-- Floating Live Cart Bar -->
        <div class="floating-cart-bar" id="floatingCart">
          <div style="display:flex;align-items:center;">
            <span class="cart-count" id="cartCount">0</span>
            <span>Panier : <strong id="cartTotal">0 {currency}</strong></span>
          </div>
          <button onclick="checkoutWhatsApp()" class="btn-wa" style="padding:8px 18px;font-size:0.86rem;">
            <i class="fa-brands fa-whatsapp"></i> Valider sur WhatsApp
          </button>
        </div>
        """
        pages["index.html"] = wrap_page("index", "Accueil & Spécialités", resto_index_content, resto_nav, extra_js=cart_js)

        # 2. Restaurant menu.html
        all_dishes_html = ""
        for d in dishes:
            badge_html = f'<span class="dish-badge">{d.get("badge", "Populaire")}</span>'
            all_dishes_html += f"""
            <div class="dish-card" data-category="{d.get('category', 'Spécialités')}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                <div>
                  <div class="dish-cat-label">{d.get('category', 'Menu')}</div>
                  <h3 class="dish-title">{d.get('name')}</h3>
                </div>
                <div class="dish-price-wrap">
                  <span class="dish-price">{d.get('price')}</span>
                  <span class="dish-curr">{currency}</span>
                </div>
              </div>
              <p class="dish-desc">{d.get('desc')}</p>
              <div class="dish-footer">
                {badge_html}
                <button class="add-to-cart-btn" onclick="addToCart('{d.get('name').replace("'", " ")}', {d.get('price')})">
                  <i class="fa-solid fa-plus"></i> Ajouter au panier
                </button>
              </div>
            </div>
            """
        resto_menu_content = f"""
        <section class="section">
          <div class="container">
            <div class="menu-tabs" style="justify-content:center;">
              <button class="menu-tab active" onclick="filterMenu('Tous', this)">Tous les Plats</button>
              <button class="menu-tab" onclick="filterMenu('Spécialités', this)">Spécialités Signature</button>
              <button class="menu-tab" onclick="filterMenu('Plats Chauds', this)">Plats Chauds & Grillades</button>
              <button class="menu-tab" onclick="filterMenu('Entrées & Sauces', this)">Entrées & Mezzés</button>
              <button class="menu-tab" onclick="filterMenu('Desserts & Boissons', this)">Desserts & Boissons</button>
            </div>

            <div class="menu-grid">
              {all_dishes_html}
            </div>
          </div>
        </section>

        <!-- Floating Live Cart Bar -->
        <div class="floating-cart-bar" id="floatingCart">
          <div style="display:flex;align-items:center;">
            <span class="cart-count" id="cartCount">0</span>
            <span>Panier : <strong id="cartTotal">0 {currency}</strong></span>
          </div>
          <button onclick="checkoutWhatsApp()" class="btn-wa" style="padding:8px 18px;font-size:0.86rem;">
            <i class="fa-brands fa-whatsapp"></i> Valider sur WhatsApp
          </button>
        </div>
        """
        pages["menu.html"] = wrap_page(
            "menu", "La Carte Gourmande", resto_menu_content, resto_nav,
            breadcrumb={"trail": "La Carte", "title": "La Carte & Nos Créations", "subtitle": f"Composez votre commande et envoyez-la directement en un clic sur WhatsApp sans intermédiaire."},
            extra_js=cart_js
        )

        # 3. Restaurant about.html
        resto_about_content = f"""
        <section class="section">
          <div class="container">
            <div style="display:grid;grid-template-columns:1.15fr 0.85fr;gap:60px;align-items:center;">
              <div>
                <span class="section-tag">NOTRE HISTOIRE & SAVOIR-FAIRE</span>
                <h2 class="section-title">L'Amour du Bon et du Goût Vrai</h2>
                <p style="color:var(--muted);font-size:1.02rem;line-height:1.7;margin-bottom:20px;">
                  Depuis son ouverture, <strong>{name}</strong> s'attache à perpétuer un esprit de générosité et de convivialité. Nous croyons qu'un bon repas rassemble, apaise et réjouit.
                </p>
                <p style="color:var(--muted);font-size:1.02rem;line-height:1.7;margin-bottom:30px;">
                  Toutes nos préparations sont élaborées chaque matin dans notre atelier à {city}. Nos sauces sont battues maison, nos pains sont dorés à la minute et nos épices sont minutieusement dosées pour créer une signature gustative reconnaissable dès la première bouchée.
                </p>

                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                  <div style="background:var(--bg-subtle);padding:20px;border-radius:16px;border:1px solid var(--border);">
                    <div style="font-size:1.8rem;font-weight:900;color:var(--accent);margin-bottom:4px;">100%</div>
                    <div style="font-weight:700;color:var(--text-heading);font-size:0.92rem;">Fait Maison Minute</div>
                    <div style="font-size:0.82rem;color:var(--muted);margin-top:2px;">Zéro produit réchauffé</div>
                  </div>
                  <div style="background:var(--bg-subtle);padding:20px;border-radius:16px;border:1px solid var(--border);">
                    <div style="font-size:1.8rem;font-weight:900;color:var(--accent);margin-bottom:4px;">30 Min</div>
                    <div style="font-weight:700;color:var(--text-heading);font-size:0.92rem;">Livraison Express</div>
                    <div style="font-size:0.82rem;color:var(--muted);margin-top:2px;">Plats chauds chez vous</div>
                  </div>
                </div>
              </div>

              <div>
                <img src="{theme['about_img']}" alt="{name}" style="width:100%;height:440px;object-fit:cover;border-radius:24px;border:1px solid var(--card-border);box-shadow:0 20px 45px -10px rgba(0,0,0,0.12);">
              </div>
            </div>
          </div>
        </section>
        """
        pages["about.html"] = wrap_page(
            "about", "Notre Histoire & Engagements", resto_about_content, resto_nav,
            breadcrumb={"trail": "Notre Histoire", "title": "Notre Histoire & Philosophie", "subtitle": f"Découvrez l'aventure humaine et culinaire qui anime toute l'équipe de {name} au quotidien."}
        )

        # 4. Restaurant contact.html
        resto_contact_content = f"""
        <section class="section">
          <div class="container">
            <div style="display:grid;grid-template-columns:1.15fr 0.85fr;gap:45px;align-items:start;">
              <!-- Table Reservation Form -->
              <div class="form-box">
                <span class="section-tag">RÉSERVATION DE TABLE WHATSAPP</span>
                <h2 style="font-size:1.8rem;font-weight:800;color:var(--text-heading);margin-bottom:8px;">Réserver une Table en Direct</h2>
                <p style="color:var(--muted);font-size:0.92rem;margin-bottom:24px;">Envoyez votre demande de réservation sur WhatsApp pour confirmation instantanée par notre équipe.</p>

                <div class="form-grid">
                  <div class="form-group">
                    <label class="form-label">Nom & Prénom</label>
                    <input type="text" id="tableName" class="form-input" placeholder="Ex: Karim">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Téléphone WhatsApp</label>
                    <input type="text" id="tablePhone" class="form-input" placeholder="Ex: +216 XX XXX XXX">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Date du Repas</label>
                    <input type="date" id="tableDate" class="form-input">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Heure Souhaitée</label>
                    <select id="tableTime" class="form-input">
                      <option value="12h30">12h30 (Déjeuner)</option>
                      <option value="13h15">13h15 (Déjeuner)</option>
                      <option value="19h30">19h30 (Dîner)</option>
                      <option value="20h30" selected>20h30 (Dîner)</option>
                      <option value="21h30">21h30 (Dîner tardif)</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Nombre de Couverts</label>
                    <select id="tableSeats" class="form-input">
                      <option value="1 Personne">1 Personne</option>
                      <option value="2 Personnes" selected>2 Personnes (Romantique)</option>
                      <option value="4 Personnes">4 Personnes (Famille/Amis)</option>
                      <option value="6 Personnes et plus">6+ Personnes (Grande Table)</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Préférence de Table</label>
                    <select id="tableArea" class="form-input">
                      <option value="Terrasse">Terrasse extérieure</option>
                      <option value="Salle Principale" selected>Salle principale climatisée</option>
                      <option value="Coin Calme">Coin calme & intime</option>
                    </select>
                  </div>
                  <div class="form-group full">
                    <label class="form-label">Notes Spéciales / Occasion</label>
                    <textarea id="tableNotes" class="form-input" rows="2" placeholder="Anniversaire, chaise bébé, intolérances..."></textarea>
                  </div>
                </div>

                <button onclick="submitTableReservation()" class="btn-primary" style="width:100%;justify-content:center;padding:14px;">
                  <i class="fa-brands fa-whatsapp"></i> Confirmer la Réservation sur WhatsApp
                </button>
              </div>

              <!-- Information Cards -->
              <div>
                <div style="background:#ffffff;border:1px solid var(--card-border);border-radius:24px;padding:30px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.06);margin-bottom:25px;">
                  <h3 style="font-size:1.2rem;font-weight:800;color:var(--text-heading);margin-bottom:18px;display:flex;align-items:center;gap:10px;">
                    <i class="fa-solid fa-clock" style="color:var(--accent);"></i> Horaires de Service
                  </h3>
                  <div style="font-size:0.92rem;color:var(--muted);line-height:1.7;">
                    • Lundi – Dimanche : <strong>11h30 – 23h30</strong><br>
                    • Service continu sur place, à emporter & livraison<br>
                    <span style="color:#10b981;font-weight:700;display:inline-block;margin-top:6px;">
                      <i class="fa-solid fa-circle-check"></i> Cuisine actuellement ouverte
                    </span>
                  </div>
                </div>

                <div style="background:#ffffff;border:1px solid var(--card-border);border-radius:24px;padding:30px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.06);">
                  <h3 style="font-size:1.2rem;font-weight:800;color:var(--text-heading);margin-bottom:18px;display:flex;align-items:center;gap:10px;">
                    <i class="fa-solid fa-location-dot" style="color:var(--accent);"></i> Adresse & Contact
                  </h3>
                  <p style="font-size:0.92rem;color:var(--muted);margin-bottom:18px;">
                    {address}
                  </p>
                  <a href="{maps_url}" target="_blank" class="btn-outline" style="width:100%;justify-content:center;padding:12px;">
                    <i class="fa-solid fa-map-location-dot"></i> Itinéraire Google Maps
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>
        """
        table_js = f"""
        <script>
        function submitTableReservation() {{
          const name = document.getElementById('tableName').value || 'Client';
          const phone = document.getElementById('tablePhone').value || '';
          const date = document.getElementById('tableDate').value;
          const time = document.getElementById('tableTime').value;
          const seats = document.getElementById('tableSeats').value;
          const area = document.getElementById('tableArea').value;
          const notes = document.getElementById('tableNotes').value;

          let msg = `Bonjour {name} ! Je souhaite réserver une table :%0A%0A`;
          msg += `• Nom : ${{name}}%0A`;
          if (phone) msg += `• Tél : ${{phone}}%0A`;
          msg += `• Couverts : ${{seats}}%0A`;
          msg += `• Emplacement : ${{area}}%0A`;
          if (date) msg += `• Date : ${{date}}%0A`;
          if (time) msg += `• Heure : ${{time}}%0A`;
          if (notes) msg += `• Notes : ${{notes}}%0A`;
          msg += `%0APouvez-vous me confirmer la table ? Merci !`;
          window.open(`{wa_url}?text=${{msg}}`, '_blank');
        }}
        window.addEventListener('DOMContentLoaded', () => {{
          const dEl = document.getElementById('tableDate');
          if (dEl) {{
            const today = new Date().toISOString().split('T')[0];
            dEl.value = today;
          }}
        }});
        </script>
        """
        pages["contact.html"] = wrap_page(
            "contact", "Réservation de Table & Contact", resto_contact_content, resto_nav,
            breadcrumb={"trail": "Réservation & Contact", "title": "Réservation de Table & Contact Direct", "subtitle": f"Réservez votre table facilement ou commandez directement sur WhatsApp."},
            extra_js=table_js
        )

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
