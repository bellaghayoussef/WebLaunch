import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from config import load_settings

def generate_outreach_messages(lead_data, mockup_url="", demo_url="", lang=None):
    """
    Generates personalized outreach copy in Arabic, French, and English for a lead.
    """
    settings = load_settings()
    agency_name = settings.get("agency_name", "WebLaunch")
    agency_phone = settings.get("agency_phone", "+974 5000 0000")
    
    name = lead_data.get("name", "Restaurant")
    city = lead_data.get("city", "votre ville")
    wa_number = lead_data.get("wa_number", "")
    
    display_link = demo_url if demo_url else (f"http://localhost:{settings.get('port', 5050)}{mockup_url}" if mockup_url else "[LIEN DE VOTRE MAQUETTE]")

    # ==========================
    # 1. ARABIC TEMPLATES
    # ==========================
    wa_ar = f"""مرحباً {name} 👋

لاحظت إنه ما عندكم موقع إلكتروني خاص فيكم، فالزبائن اللي يبحثون في قوقل عن مطاعم في {city} يلقون صعوبة للوصول لكم مباشرة.

سويت لكم نموذج موقع مجاني وتصميم كامل عشان تشوفون كيف ممكن يظهر مطعمكم باحترافية 👇
🔗 {display_link}

الموقع يحتوي على:
✅ المنيو كامل مع الأسعار
✅ زر طلب مباشر عبر الواتساب بنقرة واحدة
✅ سرعة فائقة وتوافق 100% مع الجوالات

إذا عجبكم التصميم وأردتم نشره رسمياً، نقدر نجهزه لكم فوراً. بدون أي التزام مسبق — فقط حبيت أشارككم النموذج 🙂

تحياتي،
{agency_name}
هاتف / واتساب: {agency_phone}"""

    email_ar_subject = f"نموذج موقع إلكتروني مجاني لمطعم {name} 🍽️"
    email_ar_body = f"""مرحباً فريق {name}،

أتمنى أن تكونوا بأفضل حال.

لاحظت جودة أطباقكم وسمعتكم الممتازة في {city}، لكن لاحظت أيضاً عدم وجود موقع إلكتروني مستقل خاص بكم. 

الاعتماد فقط على منصات التوصيل (مثل طلبات أو سنونو) يكلّفكم عمولات مرتفعة، بينما الموقع المباشر يُمكّن زبائنكم من الطلب مباشرة بدون عمولة!

قمت بتصميم نموذج موقع تجريبي خاص بمطعم {name} يوضح كيف يمكن أن يبدو موقعكم:
👉 رابط المعاينة: {display_link}

المميزات الأساسية:
- منيو تفاعلي لعرض الأطباق والصور
- زر طلب فوري يفتح محادثة الواتساب تلقائياً مع تفاصيل الطلب
- متوافق تماماً مع جميع الهواتف الذكية وسريع جداً

إذا كنتم مهتمين برؤية النموذج يعمل على أرض الواقع أو إطلاقه، يسعدني التحدث معكم.

مع أطيب التحيات،
{agency_name}
{agency_phone}"""

    # ==========================
    # 2. FRENCH TEMPLATES
    # ==========================
    wa_fr = f"""Bonjour {name} 👋

J'ai découvert votre établissement à {city} et la qualité de ce que vous proposez ! En cherchant vos coordonnées, j'ai remarqué que vous n'avez pas encore de site web indépendant (ou que votre page actuelle ne met pas assez en valeur votre carte).

Pour vous montrer le potentiel, j'ai créé une maquette gratuite et personnalisée de votre futur site web 👇
🔗 {display_link}

Ce site comprend :
✅ Votre menu clair avec vos spécialités
✅ Un bouton direct "Commander sur WhatsApp" en 1 clic
✅ Optimisé pour les smartphones et le référencement Google

Si le résultat vous plaît, nous pouvons le mettre en ligne très rapidement. C'est sans aucun engagement de votre part — jetez-y un coup d'œil 🙂

Bien cordialement,
{agency_name}
Tél / WhatsApp : {agency_phone}"""

    email_fr_subject = f"Maquette de site web offerte pour {name} 🍽️"
    email_fr_body = f"""Bonjour à toute l'équipe de {name},

Je vous contacte car j'ai remarqué votre excellente réputation à {city}, mais également l'absence d'un site web dédié pour votre établissement.

Aujourd'hui, de nombreux clients recherchent où manger directement sur Google. Sans site web, vous perdez des commandes directes au profit des plateformes de livraison qui prennent de lourdes commissions.

Pour vous aider à visualiser ce que cela donnerait, j'ai pris l'initiative de concevoir une première maquette moderne spécialement pour {name} :
👉 Voir la maquette en ligne : {display_link}

Ce que ce site apporte à votre activité :
1. Commandes directes sans intermédiaire (via WhatsApp ou formulaire)
2. Votre carte et vos tarifs accessibles instantanément sur mobile
3. Meilleure visibilité locale sur Google

N'hésitez pas à me dire ce que vous en pensez ! Si vous souhaitez qu'on l'adapte ou qu'on le mette en ligne, je reste à votre entière disposition.

Excellente journée,
{agency_name}
{agency_phone}"""

    # ==========================
    # 3. ENGLISH TEMPLATES
    # ==========================
    wa_en = f"""Hi {name} 👋

I love what you're doing in {city}! While looking for your place on Google, I noticed you don't have a standalone website yet, so potential customers searching online might miss you.

I built a free custom website demo to show you what a modern digital storefront could look like 👇
🔗 {display_link}

It includes:
✅ Full digital menu with your best items
✅ 1-click "Order via WhatsApp" button
✅ Ultra-fast and 100% mobile-friendly

If you like it, we can put it live in 24 hours. No obligation at all — just wanted to share the idea 🙂

Best regards,
{agency_name}
Phone / WhatsApp: {agency_phone}"""

    email_en_subject = f"Free website mockup for {name} 🍽️"
    email_en_body = f"""Hi {name} Team,

I came across your business in {city} and was impressed by your food and reviews!

However, I noticed you don't have an official website yet. Most customers searching for food on Google end up ordering through third-party apps that charge up to 25% in commissions. A direct website allows you to take direct orders with 0% commission!

I took the liberty of creating a free modern website mockup specifically for {name}:
👉 Preview it here: {display_link}

Key highlights:
- Interactive menu with photos and prices
- Direct 1-click WhatsApp order button
- SEO-ready for Google search results

Would love to hear your thoughts! If you'd like to make this your official site, let's connect.

Best regards,
{agency_name}
{agency_phone}"""

    chosen_lang = (lang or lead_data.get("default_lang", "fr")).lower()
    if chosen_lang.startswith("ar"):
        primary_wa = wa_ar
        primary_subject = email_ar_subject
        primary_email = email_ar_body
    elif chosen_lang.startswith("en"):
        primary_wa = wa_en
        primary_subject = email_en_subject
        primary_email = email_en_body
    else:
        primary_wa = wa_fr
        primary_subject = email_fr_subject
        primary_email = email_fr_body

    # Build direct WhatsApp URL
    encoded_wa_text = urllib.parse.quote(primary_wa)
    direct_wa_url = f"https://api.whatsapp.com/send?phone={wa_number}&text={encoded_wa_text}" if wa_number else ""

    return {
        "primary": {
            "whatsapp": primary_wa,
            "email_subject": primary_subject,
            "email_body": primary_email,
            "wa_url": direct_wa_url
        },
        "ar": {
            "whatsapp": wa_ar,
            "email_subject": email_ar_subject,
            "email_body": email_ar_body,
            "wa_url": f"https://api.whatsapp.com/send?phone={wa_number}&text={urllib.parse.quote(wa_ar)}" if wa_number else ""
        },
        "fr": {
            "whatsapp": wa_fr,
            "email_subject": email_fr_subject,
            "email_body": email_fr_body,
            "wa_url": f"https://api.whatsapp.com/send?phone={wa_number}&text={urllib.parse.quote(wa_fr)}" if wa_number else ""
        },
        "en": {
            "whatsapp": wa_en,
            "email_subject": email_en_subject,
            "email_body": email_en_body,
            "wa_url": f"https://api.whatsapp.com/send?phone={wa_number}&text={urllib.parse.quote(wa_en)}" if wa_number else ""
        }
    }

def send_email_with_mockup(to_email, subject, body_text, mockup_filepath=None):
    """
    Sends cold outreach email via SMTP with optional attached mockup image.
    """
    settings = load_settings()
    smtp_cfg = settings.get("smtp", {})

    host = smtp_cfg.get("host")
    port = int(smtp_cfg.get("port", 587))
    user = smtp_cfg.get("user")
    password = smtp_cfg.get("password")
    from_email = smtp_cfg.get("from_email") or user

    if not host or not user or not password:
        return {
            "success": False,
            "error": "Configuration SMTP manquante dans les Paramètres (Host, User, Password requis)."
        }

    try:
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach text
        msg.attach(MIMEText(body_text, "plain", "utf-8"))

        # Attach mockup image if exists
        if mockup_filepath and Path(mockup_filepath).exists():
            with open(mockup_filepath, "rb") as f:
                img_data = f.read()
                image_attachment = MIMEImage(img_data, name=Path(mockup_filepath).name)
                image_attachment.add_header("Content-Disposition", "attachment", filename=Path(mockup_filepath).name)
                msg.attach(image_attachment)

        # Connect and send
        server = smtplib.SMTP(host, port, timeout=12)
        if smtp_cfg.get("use_tls", True):
            server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()

        return {"success": True, "message": f"Email envoyé avec succès à {to_email}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
