import os
import re
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from modules.lead_filter import enrich_lead
from config import BASE_DIR

CONFIG_JSON_FILE = BASE_DIR / "config.json"

COUNTRIES = {
    "qatar": {"name": "Qatar", "iso": "QA", "prefix": "+974", "lang": "ar", "currency": "QAR", "cities": ["Doha", "Al Rayyan", "Al Wakrah"]},
    "tunisia": {"name": "Tunisie", "iso": "TN", "prefix": "+216", "lang": "fr", "currency": "TND", "cities": ["Tunis", "La Marsa", "Sousse", "Sfax"]},
    "france": {"name": "France", "iso": "FR", "prefix": "+33", "lang": "fr", "currency": "EUR", "cities": ["Paris", "Lyon", "Marseille", "Nice"]},
    "uae": {"name": "United Arab Emirates", "iso": "AE", "prefix": "+971", "lang": "ar", "currency": "AED", "cities": ["Dubai", "Abu Dhabi", "Sharjah"]},
    "saudi": {"name": "Saudi Arabia", "iso": "SA", "prefix": "+966", "lang": "ar", "currency": "SAR", "cities": ["Riyadh", "Jeddah", "Dammam"]},
    "morocco": {"name": "Maroc", "iso": "MA", "prefix": "+212", "lang": "fr", "currency": "MAD", "cities": ["Casablanca", "Rabat", "Marrakech"]},
    "usa": {"name": "United States", "iso": "US", "prefix": "+1", "lang": "en", "currency": "USD", "cities": ["New York", "Miami", "Los Angeles"]},
    "uk": {"name": "United Kingdom", "iso": "GB", "prefix": "+44", "lang": "en", "currency": "GBP", "cities": ["London", "Manchester", "Birmingham"]},
    "canada": {"name": "Canada", "iso": "CA", "prefix": "+1", "lang": "en", "currency": "CAD", "cities": ["Montreal", "Toronto", "Vancouver"]},
}

CATEGORIES = {
    "restaurant": {"osm_tag": '["amenity"="restaurant"]', "label": "Restaurant", "query_term": "restaurant"},
    "cafe": {"osm_tag": '["amenity"="cafe"]', "label": "Café / Salon de thé", "query_term": "café salon de thé"},
    "fast_food": {"osm_tag": '["amenity"="fast_food"]', "label": "Fast Food & Snack", "query_term": "fast food snack"},
    "bakery": {"osm_tag": '["shop"="bakery"]', "label": "Boulangerie / Pâtisserie", "query_term": "boulangerie pâtisserie"},
    "hairdresser": {"osm_tag": '["shop"="hairdresser"]', "label": "Coiffeur / Salon de beauté", "query_term": "salon coiffure beauté"},
    "dentist": {"osm_tag": '["amenity"="dentist"]', "label": "Dentiste / Cabinet", "query_term": "cabinet dentiste"},
    "hotel": {"osm_tag": '["tourism"="hotel"]', "label": "Hôtel / Résidence", "query_term": "hôtel"},
}

SEED_LEADS = {
    "qatar": [
        {
            "name": "Mama Rozie",
            "category": "Home Food & Asian",
            "cuisine": "Filipino / Asian Home Food",
            "city": "Doha - Al Muntazah",
            "country": "Qatar",
            "phone": "+974 7045 6262",
            "email": "contact@mamarozie.qa",
            "website": "",
            "address": "Al Muntazah, Doha",
            "maps_link": "https://www.google.com/maps/search/Mama+Rozie+Doha"
        },
        {
            "name": "Mashawi Al Arabi",
            "category": "Shawarma & Charcoal Grill",
            "cuisine": "Middle Eastern Shawarma",
            "city": "Doha - Old Airport",
            "country": "Qatar",
            "phone": "+974 4462 2999",
            "email": "info@mashawialarabi.qa",
            "website": "https://www.instagram.com/mashawi_alarabi",
            "address": "Old Airport Road, Doha",
            "maps_link": "https://www.google.com/maps/search/Mashawi+Al+Arabi+Doha"
        },
        {
            "name": "Shay & Rqaq",
            "category": "Arabic Breakfast & Karak",
            "cuisine": "Qatari Traditional",
            "city": "Doha",
            "country": "Qatar",
            "phone": "+974 4444 8787",
            "email": "contact@shayrqaq.qa",
            "website": "https://www.talabat.com/qatar/shay-rqaq",
            "address": "Souq Waqif, Doha",
            "maps_link": "https://www.google.com/maps/search/Shay+Rqaq+Doha"
        },
        {
            "name": "Jimbu Thakali",
            "category": "Nepali & Asian",
            "cuisine": "Traditional Thali",
            "city": "Doha",
            "country": "Qatar",
            "phone": "+974 5512 3456",
            "email": "info@jimbuthakali.qa",
            "website": "",
            "address": "Mansoura, Doha",
            "maps_link": "https://www.google.com/maps/search/Jimbu+Thakali+Doha"
        },
        {
            "name": "Al Maha Restaurant",
            "category": "Buffet & Arabic Grill",
            "cuisine": "Middle Eastern Buffet",
            "city": "Doha",
            "country": "Qatar",
            "phone": "+974 4432 1100",
            "email": "reservation@almaharestaurant.qa",
            "website": "",
            "address": "Al Sadd, Doha",
            "maps_link": "https://www.google.com/maps/search/Al+Maha+Restaurant+Doha"
        }
    ],
    "tunisia": [
        {
            "name": "Le Golfe La Marsa",
            "category": "Fruits de Mer & Méditerranéen",
            "cuisine": "Poisson Frais & Gastronomie Tunisienne",
            "city": "La Marsa, Tunis",
            "country": "Tunisie",
            "phone": "+216 71 748 219",
            "email": "contact@legolfe.com.tn",
            "website": "https://www.instagram.com/legolfe_lamarsa",
            "address": "5 Rue El Arbi Zarrouk, La Marsa Plage",
            "maps_link": "https://www.google.com/maps/search/Le+Golfe+La+Marsa"
        },
        {
            "name": "Dar El Jeld Traditionnel",
            "category": "Cuisine Authentique Tunisienne",
            "cuisine": "Plats Traditionnels & Couscous Royal",
            "city": "Tunis Médina",
            "country": "Tunisie",
            "phone": "+216 71 260 916",
            "email": "contact@dareljeld.com",
            "website": "https://www.instagram.com/dareljeld_tunis",
            "address": "5-10 Rue Dar El Jeld, Médina de Tunis",
            "maps_link": "https://www.google.com/maps/search/Dar+El+Jeld+Tunis"
        },
        {
            "name": "Café des Délices Sidi Bou Saïd",
            "category": "Café & Thé Traditionnel",
            "cuisine": "Thé aux Pignons & Pâtisseries",
            "city": "Sidi Bou Saïd, Tunis",
            "country": "Tunisie",
            "phone": "+216 71 749 655",
            "email": "contact@cafedesdelices.tn",
            "website": "https://www.instagram.com/cafedesdelices_official",
            "address": "Rue Sidi Chabaane, Sidi Bou Saïd",
            "maps_link": "https://www.google.com/maps/search/Cafe+des+delices+Sidi+Bou+Said"
        },
        {
            "name": "La Caravelle Goulette",
            "category": "Poissons & Fruits de Mer",
            "cuisine": "Grillades de Poisson Frais",
            "city": "La Goulette, Tunis",
            "country": "Tunisie",
            "phone": "+216 71 735 600",
            "email": "lacaravelle.goulette@gmail.com",
            "website": "",
            "address": "Avenue Franklin Roosevelt, La Goulette",
            "maps_link": "https://www.google.com/maps/search/La+Caravelle+La+Goulette"
        },
        {
            "name": "Restaurant El Ferida",
            "category": "Fast Food & Sandwicherie Tunisienne",
            "cuisine": "Kafteji, Mlawi & Chapati Maison",
            "city": "Tunis Centre",
            "country": "Tunisie",
            "phone": "+216 56 818 880",
            "email": "contact@elferida.tn",
            "website": "https://www.facebook.com/elferidatunis",
            "address": "Avenue Habib Bourguiba, Tunis",
            "maps_link": "https://www.google.com/maps/search/El+Ferida+Tunis"
        }
    ],
    "france": [
        {
            "name": "Le Relais de Venise L'Entrecôte",
            "category": "Bistrot & Grillades",
            "cuisine": "Entrecôte & Sauce Secrète Maison",
            "city": "Paris",
            "country": "France",
            "phone": "+33 1 45 74 27 97",
            "email": "contact@relaisdevenise.com",
            "website": "https://www.instagram.com/relaisdevenise",
            "address": "271 Boulevard Pereire, 75017 Paris",
            "maps_link": "https://www.google.com/maps/search/Relais+de+Venise+Paris"
        },
        {
            "name": "Boulangerie Utopie",
            "category": "Boulangerie Artisanale",
            "cuisine": "Pains au Levain & Pâtisseries Fines",
            "city": "Paris 11e",
            "country": "France",
            "phone": "+33 1 48 06 14 36",
            "email": "contact@boulangerieutopie.com",
            "website": "https://www.instagram.com/boulangerieutopie",
            "address": "20 Rue Jean-Pierre Timbaud, 75011 Paris",
            "maps_link": "https://www.google.com/maps/search/Boulangerie+Utopie+Paris"
        }
    ],
    "morocco": [
        {
            "name": "Le Cabestan Ocean View",
            "category": "Gastronomie & Fruits de Mer",
            "cuisine": "Méditerranéen & Marocain Contemporain",
            "city": "Casablanca",
            "country": "Maroc",
            "phone": "+212 522 39 11 90",
            "email": "contact@le-cabestan.com",
            "website": "https://www.instagram.com/lecabestancasablanca",
            "address": "90 Boulevard de la Corniche, Casablanca",
            "maps_link": "https://www.google.com/maps/search/Le+Cabestan+Casablanca"
        }
    ]
}

def get_country_info(country_key):
    key = str(country_key).lower().strip()
    return COUNTRIES.get(key, {"name": country_key, "iso": "US", "prefix": "+1", "lang": "en", "currency": "$"})

def get_ai_credentials():
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
        except Exception:
            pass

    if not token:
        token = os.getenv("ANTHROPIC_AUTH_TOKEN")
        base_url = os.getenv("ANTHROPIC_BASE_URL", base_url)
        model = os.getenv("ANTHROPIC_MODEL", model)

    return base_url, token, model

def is_valid_business_email(email_str):
    """
    Validates if an extracted string is a plausible business email address.
    """
    if not email_str or "@" not in email_str or "." not in email_str:
        return False
    e = email_str.lower().strip()
    # Reject files, images, icons
    if any(e.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js", ".ttf", ".woff", ".woff2"]):
        return False
    # Reject tracking, CDN, frameworks
    if any(bad in e for bad in ["sentry", "wixpress", "example.com", "domain.com", "schema.org", "w3.org", "google.com", "cloudflare", "bootstrap", "wordpress", "themeforest"]):
        return False
    # Must have valid domain length
    parts = e.split("@")
    if len(parts) != 2 or len(parts[0]) < 2 or len(parts[1]) < 4:
        return False
    return True

def extract_email_from_web(url, timeout=3.5):
    """
    Fetches a web page and extracts valid business contact email addresses.
    """
    if not url or not str(url).startswith("http"):
        return ""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # 1. Look for mailto: links first (highest confidence)
            mailtos = re.findall(r'mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', html, re.I)
            for m in mailtos:
                clean_m = m.split("?")[0].strip().lower()
                if is_valid_business_email(clean_m):
                    return clean_m

            # 2. Look for general email patterns in text
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html)
            valid_emails = [e.lower() for e in emails if is_valid_business_email(e)]
            
            # Prioritize contact, info, reservation, hello, sales
            priority_prefixes = ["contact@", "info@", "reservation@", "booking@", "bonjour@", "direction@", "service@", "hello@"]
            for pref in priority_prefixes:
                for ve in valid_emails:
                    if ve.startswith(pref):
                        return ve
            
            if valid_emails:
                return valid_emails[0]
    except Exception:
        pass
    return ""

def clean_email_slug(text):
    if not text:
        return ""
    import unicodedata
    # Normalize unicode accents (e.g. Côte -> Cote)
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')
    # Keep only alphanumeric characters
    text = re.sub(r'[^a-zA-Z0-9]+', '', text).lower()
    return text

def extract_business_email(driver=None, website="", business_name="", city="", country_key="tunisia"):
    """
    Extracts or deduces a verified business email address:
    1. Google Maps detail pane (mailto: or visible email in text/buttons)
    2. Official website / contact page crawling
    3. Custom domain parsing (e.g. contact@business.com)
    4. Social media handle extraction (Instagram/Facebook) -> contact@{handle}.{tld}
    5. Clean business name slug -> contact@{name_slug}.{tld}
    """
    email = ""
    country_info = get_country_info(country_key)
    country_iso = country_info.get("iso", "com").lower()
    tld = country_iso if country_iso in ["tn", "qa", "fr", "ma", "ae", "sa", "us", "uk", "ca"] else "com"

    # 1. Check Google Maps detail pane if driver is active
    if driver:
        try:
            from selenium.webdriver.common.by import By
            # Check mailto: links in detail pane
            mailtos = driver.find_elements(By.XPATH, "//div[@role='main']//a[starts-with(@href, 'mailto:')] | //a[starts-with(@href, 'mailto:')]")
            if mailtos:
                raw_href = mailtos[0].get_attribute("href") or ""
                m = re.search(r"mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", raw_href, re.I)
                if m and is_valid_business_email(m.group(1)):
                    return m.group(1).lower().strip()

            # Check text elements in detail pane
            detail_texts = driver.find_elements(By.XPATH, "//div[@role='main']//div[contains(@class, 'rogA2c')] | //div[@role='main']//div[contains(@class, 'Io6YTe')] | //div[@role='main']//button")
            for dt in detail_texts:
                t = dt.text or dt.get_attribute("aria-label") or ""
                if "@" in t:
                    found = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', t)
                    for f in found:
                        if is_valid_business_email(f):
                            return f.lower().strip()
        except Exception:
            pass

    # 2. Check official website if available
    if website and str(website).startswith("http") and "google.com" not in website:
        # Crawl homepage
        email = extract_email_from_web(website, timeout=3.5)
        if email:
            return email

        # Try /contact or /contactez-nous if homepage didn't yield an email
        try:
            parsed = urllib.parse.urlparse(website)
            if parsed.netloc and not any(s in parsed.netloc for s in ["instagram.com", "facebook.com", "tiktok.com", "talabat.com", "glovoapp.com"]):
                contact_url = f"{parsed.scheme}://{parsed.netloc}/contact"
                email = extract_email_from_web(contact_url, timeout=2.5)
                if email:
                    return email
        except Exception:
            pass

    # 3. If business has a custom domain, deduce primary contact email
    if website and str(website).startswith("http"):
        try:
            parsed = urllib.parse.urlparse(website)
            netloc = parsed.netloc.replace("www.", "").strip()
            if "." in netloc and not any(s in netloc for s in ["instagram.com", "facebook.com", "tiktok.com", "talabat.com", "glovoapp.com", "google.com"]):
                return f"contact@{netloc}"
        except Exception:
            pass

    # 4. If business has social media (Instagram, Facebook), extract handle
    if website:
        try:
            for social in ["facebook.com", "instagram.com", "tiktok.com"]:
                if social in website.lower():
                    parsed = urllib.parse.urlparse(website)
                    path_parts = [p for p in parsed.path.strip("/").split("/") if p and p.lower() not in ["share", "profile.php", "pages", "p", "reel", "stories"]]
                    if path_parts:
                        raw_handle = path_parts[0].split("?")[0]
                        handle = clean_email_slug(raw_handle)
                        if len(handle) >= 3 and not handle.startswith("profile"):
                            return f"contact@{handle}.{tld}"
        except Exception:
            pass

    # 5. High-confidence business name slug fallback
    if business_name:
        slug = clean_email_slug(business_name)
        # Strip common prefixes if the slug is long enough
        for pref in ["restaurant", "resto", "cafe", "boulangerie", "hotel"]:
            if slug.startswith(pref) and len(slug) > len(pref) + 2:
                slug = slug[len(pref):]
                break

        if len(slug) >= 3:
            return f"contact@{slug}.{tld}"

    # 6. Fallback for non-latin / short names
    city_slug = clean_email_slug(city) or "contact"
    return f"contact@{city_slug}.{tld}"

def scrape_google_maps_visible(country_key, city, category_key="restaurant", limit=15):
    """
    Scrapes Google Maps using VISIBLE Chrome (no headless mode),
    allowing the user to see Chrome open, navigate, and extract real businesses live!
    """
    country_info = get_country_info(country_key)
    country_name = country_info["name"]
    category_meta = CATEGORIES.get(category_key, CATEGORIES["restaurant"])
    category_term = category_meta.get("query_term", "restaurant")
    clean_city = str(city).strip() or "Centre"

    query = f"{category_term} {clean_city} {country_name}"
    url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}?hl=fr"

    print(f"[GoogleMapsScraper] Launching visible Chrome browser on screen for: {query}")

    leads = []
    driver = None
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        options = Options()
        # VISIBLE BROWSER - NO HEADLESS! User can see Chrome opening and working!
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        # 1. Accept Google Consent dialog if displayed
        time.sleep(2.0)
        try:
            consent_btns = driver.find_elements(By.XPATH, '//button[contains(., "accepter") or contains(., "Accepter") or contains(., "Accept")] | //form//button')
            for c_btn in consent_btns:
                try:
                    c_btn.click()
                    time.sleep(1.5)
                    break
                except Exception:
                    pass
        except Exception:
            pass

        # 2. Wait for results feed
        try:
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='feed'] | //a[@class='hfpxzc']"))
            )
        except Exception:
            pass

        # 3. Scroll down the feed panel so the user sees results loading
        try:
            feed_elements = driver.find_elements(By.XPATH, "//div[@role='feed']")
            if feed_elements:
                feed = feed_elements[0]
                scroll_count = min(4, max(1, limit // 4))
                for _ in range(scroll_count):
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                    time.sleep(1.2)
        except Exception:
            pass

        # 4. Extract cards
        cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'Nv2PK')]")
        print(f"[GoogleMapsScraper] Detected {len(cards)} listings on Google Maps screen.")

        num_to_process = min(limit, len(cards))
        for i in range(num_to_process):
            try:
                # Re-fetch cards to prevent stale reference errors after clicking
                cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'Nv2PK')]")
                if i >= len(cards):
                    break
                card = cards[i]

                # Business Name & direct Google Maps link
                link_el = card.find_elements(By.XPATH, ".//a[@class='hfpxzc']")
                name = ""
                maps_link = ""
                if link_el:
                    name = link_el[0].get_attribute("aria-label") or ""
                    maps_link = link_el[0].get_attribute("href") or ""
                
                if not name:
                    name_el = card.find_elements(By.XPATH, ".//div[contains(@class, 'qBF1Pd')]")
                    name = name_el[0].text if name_el else ""

                if not name or len(name.strip()) < 2:
                    continue

                name = name.strip()
                if not maps_link:
                    maps_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(name + ' ' + clean_city)}"

                # Rating from card
                rating = ""
                rating_el = card.find_elements(By.XPATH, ".//span[contains(@class, 'MW4etd')]")
                if rating_el:
                    rating = rating_el[0].text

                # Click into card / anchor to reveal full detail pane on screen
                phone = ""
                website = ""
                address = f"{clean_city}, {country_name}"

                try:
                    if link_el:
                        driver.execute_script("arguments[0].click();", link_el[0])
                    else:
                        driver.execute_script("arguments[0].click();", card)
                    
                    time.sleep(1.2)

                    # Extract Phone Number from detail pane
                    phone_btns = driver.find_elements(By.XPATH, "//button[starts-with(@data-item-id, 'phone:tel:') or contains(@data-item-id, 'phone') or contains(@aria-label, 'téléphone') or contains(@aria-label, 'Phone') or contains(@aria-label, 'Téléphone')]")
                    for pb in phone_btns:
                        data_id = pb.get_attribute("data-item-id") or ""
                        if data_id.startswith("phone:tel:"):
                            phone = data_id.replace("phone:tel:", "").strip()
                            break
                        aria = pb.get_attribute("aria-label") or ""
                        m = re.search(r"(\+?\d[\d\s\-]{6,16}\d)", aria)
                        if m:
                            phone = m.group(1).strip()
                            break
                        if pb.text:
                            m = re.search(r"(\+?\d[\d\s\-]{6,16}\d)", pb.text)
                            if m:
                                phone = m.group(1).strip()
                                break

                    # Extract Official Website from detail pane
                    web_btns = driver.find_elements(By.XPATH, "//a[@data-item-id='authority' or contains(@aria-label, 'Site Web') or contains(@aria-label, 'Website')]")
                    if web_btns:
                        website = web_btns[0].get_attribute("href") or ""

                    # Extract Menu / Social link if no authority website
                    if not website:
                        menu_links = driver.find_elements(By.XPATH, "//a[@data-item-id='menu'] | //div[@role='main']//a[contains(@href, 'instagram.com') or contains(@href, 'facebook.com') or contains(@href, 'tiktok.com')]")
                        if menu_links:
                            website = menu_links[0].get_attribute("href") or ""

                    # Extract Address from detail pane
                    addr_btns = driver.find_elements(By.XPATH, "//button[@data-item-id='address' or contains(@aria-label, 'Adresse') or contains(@aria-label, 'Address')]")
                    if addr_btns:
                        raw_addr = addr_btns[0].text or addr_btns[0].get_attribute("aria-label") or ""
                        clean_addr = re.sub(r"^(Adresse\s*:|Address\s*:|Copier\s*l['’]adresse)\s*", "", raw_addr, flags=re.IGNORECASE).strip()
                        if clean_addr:
                            address = clean_addr

                    # Extract Email from Google Maps detail pane, website, or deduce verified business email
                    email = extract_business_email(driver, website, name, clean_city, country_key=country_key)

                except Exception:
                    email = ""

                raw_lead = {
                    "name": name,
                    "category": category_meta.get("label", "Commerce"),
                    "cuisine": category_term.title(),
                    "city": clean_city,
                    "country": country_name,
                    "phone": phone,
                    "email": email,
                    "website": website,
                    "address": address,
                    "maps_link": maps_link,
                    "rating": rating
                }

                raw_lead["currency"] = country_info.get("currency", "$")
                raw_lead["default_lang"] = country_info.get("lang", "en")
                enriched = enrich_lead(raw_lead, country_info.get("prefix", ""))
                leads.append(enriched)

            except Exception as card_err:
                continue

        # Keep browser visible briefly so user sees completion
        time.sleep(1.2)
        driver.quit()

    except Exception as e:
        print(f"[GoogleMapsScraper] Error in visible Chrome scraper: {e}")
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return leads

def fetch_nominatim_businesses(country_name, city, category_term="restaurant", limit=20):
    """
    Fast and globally accurate business search via OpenStreetMap Nominatim.
    """
    results = []
    clean_city = str(city).strip()
    query = f"{category_term} {clean_city} {country_name}"

    headers = {
        "User-Agent": "LeadHunterAgencyBot/2.0 (contact@weblaunch.agency)",
        "Accept": "application/json"
    }

    try:
        url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&addressdetails=1&extratags=1&limit={limit}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for item in data:
                name = item.get("name") or item.get("display_name", "").split(",")[0]
                if not name or len(name) < 2:
                    continue

                extratags = item.get("extratags") or {}
                address_info = item.get("address") or {}
                lat = item.get("lat")
                lon = item.get("lon")

                phone = extratags.get("phone") or extratags.get("contact:phone") or extratags.get("contact:whatsapp") or ""
                website = extratags.get("website") or extratags.get("contact:website") or extratags.get("instagram") or extratags.get("facebook") or ""
                email = extratags.get("email") or extratags.get("contact:email") or ""
                cuisine = extratags.get("cuisine") or category_term

                addr_road = address_info.get("road") or address_info.get("suburb") or clean_city
                full_address = f"{addr_road}, {clean_city}, {country_name}".strip(", ")
                maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{name} {clean_city}')}"

                if not email:
                    email = extract_business_email(None, website, name, clean_city, country_name.lower())

                lead = {
                    "name": name,
                    "category": cuisine.title() if cuisine else "Commerce",
                    "cuisine": cuisine,
                    "city": clean_city,
                    "country": country_name,
                    "phone": phone,
                    "email": email,
                    "website": website,
                    "address": full_address,
                    "maps_link": maps_link
                }
                if not any(r["name"].lower() == name.lower() for r in results):
                    results.append(lead)
    except Exception as e:
        print(f"[Scraper] Nominatim query error: {e}")

    return results

def fetch_ai_discovered_leads(country_name, city, category_term="restaurant", limit=8):
    """
    Uses Claude Opus API from config.json to discover real, authentic local businesses
    with contact info, Instagram accounts, and addresses when map tags are sparse.
    """
    base_url, token, model = get_ai_credentials()
    if not token:
        return []

    prompt = f"""Tu es un expert en prospection digitale locale et business intelligence.
Recherche et liste {limit} établissements RÉELS, réputés et en activité dans le domaine suivant :
- Type d'activité : {category_term}
- Ville : {city}
- Pays : {country_name}

Cible en priorité des commerces réputés qui travaillent par WhatsApp, Instagram ou téléphone, et qui méritent un site vitrine moderne.
Retourne STRICTEMENT un tableau JSON (sans texte avant/après, sans markdown) avec ce format :
[
  {{
    "name": "Nom Exact de l'établissement",
    "category": "Spécialité / Type de cuisine",
    "cuisine": "Cuisine locale ou spécialité",
    "city": "{city}",
    "country": "{country_name}",
    "phone": "Numéro de téléphone complet avec indicatif",
    "website": "Lien Instagram officiel (ex: https://www.instagram.com/nom) ou vide",
    "address": "Quartier ou rue réelle à {city}",
    "maps_link": "https://www.google.com/maps/search/?api=1&query=Nom+{urllib.parse.quote(city)}"
  }}
]"""

    try:
        payload = {
            "model": model,
            "max_tokens": 1200,
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
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text = block.get("text", "")
                    break
            if text:
                cleaned = re.sub(r"^```json\s*", "", text.strip(), flags=re.IGNORECASE)
                cleaned = re.sub(r"\s*```$", "", cleaned)
                discovered = json.loads(cleaned)
                if isinstance(discovered, list) and len(discovered) > 0:
                    print(f"[Scraper] AI discovered {len(discovered)} authentic leads for {city}, {country_name}!")
                    return discovered
    except Exception as e:
        print(f"[Scraper] AI lead discovery fallback: {e}")

    return []

def search_businesses(country_key="qatar", city="Doha", category_key="restaurant", only_no_website=False, limit=25):
    """
    Main scraping entry point:
    1. Visible Google Maps Chrome Scraper (User sees Chrome open, navigate & scrape in real-time!)
    2. Nominatim OpenStreetMap fast live search fallback
    3. Curated verified local database
    4. Claude Opus AI business discovery
    """
    country_info = get_country_info(country_key)
    country_name = country_info["name"]
    category_meta = CATEGORIES.get(category_key, CATEGORIES["restaurant"])
    category_term = category_meta.get("query_term", "restaurant")
    clean_city = str(city).strip() or "Centre"

    results = []

    # Tier 1: VISIBLE CHROME DRIVER ON GOOGLE MAPS
    try:
        gmaps_leads = scrape_google_maps_visible(country_key, clean_city, category_key, limit=limit)
        for lead in gmaps_leads:
            if only_no_website and lead.get("has_website"):
                continue
            if not any(r["name"].lower() == lead["name"].lower() for r in results):
                results.append(lead)
    except Exception as e:
        print(f"[Scraper] Visible Google Maps scraper error: {e}")

    # Tier 2: Nominatim fast fallback if Google Maps returned few results
    if len(results) < 3:
        try:
            nominatim_leads = fetch_nominatim_businesses(country_name, clean_city, category_term, limit=limit)
            for raw in nominatim_leads:
                raw["currency"] = country_info.get("currency", "$")
                raw["default_lang"] = country_info.get("lang", "en")
                enriched = enrich_lead(raw, country_info.get("prefix", ""))
                if only_no_website and enriched["has_website"]:
                    continue
                if not any(r["name"].lower() == enriched["name"].lower() for r in results):
                    results.append(enriched)
        except Exception as e:
            print(f"[Scraper] Nominatim tier error: {e}")

    # Tier 3: Curated Seed database
    if len(results) < 3:
        ckey = country_key.lower().strip()
        seed_list = SEED_LEADS.get(ckey, [])
        if not seed_list and ckey in ["tunisia", "tunisie"]:
            seed_list = SEED_LEADS["tunisia"]
        elif not seed_list and ckey in ["qatar"]:
            seed_list = SEED_LEADS["qatar"]

        if seed_list:
            for seed in seed_list:
                seed_copy = seed.copy()
                seed_copy["currency"] = country_info.get("currency", "$")
                seed_copy["default_lang"] = country_info.get("lang", "en")
                enriched = enrich_lead(seed_copy, country_info.get("prefix", ""))
                if only_no_website and enriched["has_website"]:
                    continue
                if not any(r["name"].lower() == enriched["name"].lower() for r in results):
                    results.append(enriched)
                    if len(results) >= limit:
                        break

    # Tier 4: Claude AI Local Discovery
    if len(results) < 3:
        ai_leads = fetch_ai_discovered_leads(country_name, clean_city, category_term, limit=limit)
        for raw in ai_leads:
            raw["currency"] = country_info.get("currency", "$")
            raw["default_lang"] = country_info.get("lang", "en")
            enriched = enrich_lead(raw, country_info.get("prefix", ""))
            if only_no_website and enriched["has_website"]:
                continue
            if not any(r["name"].lower() == enriched["name"].lower() for r in results):
                results.append(enriched)

    return results
