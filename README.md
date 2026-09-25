# 🤖 AgentX — Autonomous Claude AI Agent

AgentX est une application d'agent IA autonome alimentée par l'API Claude (via le proxy Anthropic configuré), dotée d'une interface web moderne en **Dark Theme** et d'un mode CLI interactif.

---

## 🚀 Caractéristiques

- **Boucle Autonome ReAct (Reasoning + Acting)** : L'agent réfléchit, planifie, choisit et exécute des outils étape par étape avant de formuler une réponse complète.
- **Recherche Web en direct (`web_search` & `fetch_url`)** : Recherche des informations d'actualité, consulte des articles de presse, synthétise des sources et extrait des citations.
- **Bac à sable JavaScript / Calculs (`run_javascript`)** : Résout des expressions mathématiques et exécute des algorithmes en environnement sécurisé.
- **Exploration du Workspace (`read_file`, `write_file`, `list_files`)** : Accède aux fichiers du projet, lit et écrit des documents.
- **Horloge et Temporel (`get_current_time`)** : Conscience précise de l'heure et du fuseau horaire.
- **Streaming en temps réel (SSE)** : Visualisation du raisonnement interne (*thinking*), des cartes d'exécution d'outils et du rendu Markdown au fur et à mesure.
- **Interface Dark Theme Ultra-Moderne** : Design avec glassmorphism, badges d'état, boutons de copie de code, et panneau de configuration.
- **Mode CLI Terminal** : Exécution rapide de requêtes en ligne de commande.

---

## 🛠️ Configuration

Le fichier `config.json` et le fichier `.env` contiennent votre configuration :

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.justwoker.icu",
    "ANTHROPIC_AUTH_TOKEN": "sk-4oqk40wTjWRc8dIN5s1BjumklytmzBrKOHgND4uljYjoU7me",
    "ANTHROPIC_MODEL": "claude-opus-4-8"
  },
  "fallback_model": "claude-opus-4-8",
  "theme": "dark"
}
```

> **Note sur le modèle** : Votre token d'accès a un accès direct au modèle **`claude-opus-4-8`** (qui inclut la recherche web et le thinking). Le système gère automatiquement le basculement si `claude-opus-5` n'a pas de canal actif sur le proxy.

---

## 🖥️ Utilisation

### 1. Lancer l'Application Web
Dans le dossier du projet `d:\agentx` :
```bash
npm start
```
Ou en mode développement (rechargement automatique) :
```bash
npm run dev
```

Puis ouvrez votre navigateur sur :
👉 **http://localhost:3500**

---

### 2. Mode Ligne de Commande (CLI)
Vous pouvez poser une question directement depuis votre terminal :

```bash
# Exemple de recherche web
node cli.js "cherche sur le web les missions récentes de SpaceX"

# Exemple d'analyse et calcul
node cli.js "calcule 143 * 37 et cherche qui a découvert Pluton"

# Exemple d'exploration de fichiers
node cli.js "liste les fichiers du workspace"
```

---

## 📁 Structure du Projet

```text
d:\agentx/
├── config.json          # Configuration active (URL, Token, Modèle, Thème)
├── .env                 # Variables d'environnement
├── package.json         # Dépendances et scripts
├── server.js            # Serveur Express & streaming SSE
├── cli.js               # Outil CLI pour le terminal
├── src/
│   ├── agent.js         # Moteur de l'agent ReAct autonome
│   ├── claudeClient.js  # Client HTTP Anthropic Messages & fallback
│   ├── config.js        # Gestionnaire de configuration
│   └── tools.js         # Boîte à outils (web_search, fetch_url, js, files)
└── public/
    ├── index.html       # Interface utilisateur Dark Theme
    ├── style.css        # Styles CSS modernes et glassmorphism
    └── app.js           # Client SSE, markdown et animations
```
