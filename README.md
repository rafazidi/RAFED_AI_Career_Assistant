# RAFED IA — Personal Career Assistant

Portfolio bilingue (FR/EN) avec chatbot RAG destiné à présenter le parcours professionnel de Rafed Zidi aux recruteurs.

## Ce que contient cette version

- `backend/` : API FastAPI, moteur de recherche documentaire ChromaDB, embeddings Sentence Transformers et génération via API compatible OpenAI.
- `frontend/` : portfolio React + TypeScript avec une interface de chat intégrée.
- `knowledge_base/` : documents de profil de départ à vérifier et compléter.
- `docs/` : architecture et guide de personnalisation.
- `.env.example` : configuration locale sans clé secrète.

> Cette archive est une base de projet complète et exécutable pour démarrer le développement. Pour obtenir des réponses générées par un LLM, il faudra configurer un fournisseur compatible OpenAI dans le fichier `.env`. Sans clé API, le backend peut tout de même rechercher les documents et signaler que la génération n'est pas configurée.

## Prérequis

- Windows 10/11
- Python 3.11
- Node.js LTS (Node 26 peut fonctionner, mais une version LTS est généralement préférable pour un environnement de développement)
- npm
- Git (facultatif au premier lancement)

## 1. Ouvrir le projet

Décompresse `RAFED_IA.zip` dans :

`C:\Users\bmahj\Desktop\rafed\`

Le dossier final doit être :

`C:\Users\bmahj\Desktop\rafed\RAFED IA`

Si Windows ajoute `RAFED_IA` au nom du dossier extrait, renomme-le en `RAFED IA`.

## 2. Démarrer le backend (PowerShell)

Ouvre un premier terminal PowerShell :

```powershell
cd "C:\Users\bmahj\Desktop\rafed\RAFED IA"

py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r backend\requirements.txt

Copy-Item .env.example .env
```

Puis lance l'API :

```powershell
uvicorn app.main:app --app-dir backend --reload
```

API : http://127.0.0.1:8000  
Documentation interactive : http://127.0.0.1:8000/docs  
Vérification : http://127.0.0.1:8000/health

Le premier chargement du modèle d'embeddings peut télécharger un modèle Hugging Face et prendre un peu de temps.

## 3. Démarrer le frontend

Ouvre un deuxième terminal PowerShell :

```powershell
cd "C:\Users\bmahj\Desktop\rafed\RAFED IA\frontend"
npm install
npm run dev
```

Ouvre l'adresse affichée par Vite, généralement http://localhost:5173.

## 4. Activer la génération IA

Ouvre le fichier `.env` à la racine et renseigne les paramètres de ton fournisseur LLM compatible avec l'API OpenAI :

```env
LLM_API_KEY=ta_cle_api
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=nom-du-modele-disponible
```

Utilise le nom exact d'un modèle disponible chez le fournisseur choisi. Ne partage jamais ta clé API et ne la place jamais dans le frontend.

Redémarre le backend après toute modification du `.env`.

## 5. Synchroniser automatiquement les projets GitHub

Le portfolio affiche automatiquement les dépôts **publics, non forkés** du compte GitHub configuré qui portent le topic `portfolio`. Pour ajouter un projet :

1. Ouvre le dépôt souhaité sur GitHub.
2. Dans la section **About**, ajoute le topic `portfolio`.
3. Renseigne une description claire et vérifiée et ajoute un README présentant le projet.

À l’ouverture du portfolio, le backend récupère ces dépôts, affiche leurs descriptions et liens, puis indexe leurs README pour que l’assistant puisse répondre aux questions sur les projets. La liste GitHub est mise en cache pendant 5 minutes. Aucun jeton GitHub n’est requis pour les dépôts publics.

Le compte et le topic peuvent être configurés dans `.env` avec `GITHUB_OWNER` et `GITHUB_TOPIC`. Les informations personnelles qui ne figurent pas dans les dépôts restent gérées dans les documents Markdown de `knowledge_base/`.

Après modification de ces documents locaux, reconstruis l’index avec :

```powershell
python do_ingest.py
```

À exécuter depuis la racine du projet avec `.venv` activé.

## 6. Sécurité et limites

- Le fichier `.env` et les secrets ne doivent jamais être commités sur GitHub.
- Le chatbot est informatif : il ne doit pas inventer de diplômes, d'expériences, de compétences ou de résultats.
- Les informations de la base documentaire doivent être vérifiées avant publication.
- Avant un déploiement public, ajouter une limitation de débit, une politique de confidentialité, une validation renforcée des entrées et une protection contre les abus.
- Ne mets pas de données personnelles sensibles dans la base documentaire.

## 7. Hébergement gratuit recommandé

Un déploiement gratuit simple consiste à servir le frontend sur GitHub Pages et l'API sur Hugging Face Spaces.

### API FastAPI sur Hugging Face Spaces

1. Crée un Hugging Face Space avec le SDK **Docker**.
2. Pousse ce dépôt dans le dépôt du Space.
3. Ajoute dans **Settings > Variables and secrets** :
   - `FRONTEND_ORIGIN=https://rafazidi.github.io`
   - `GITHUB_OWNER=rafazidi`
   - `GITHUB_TOPIC=portfolio`
   - `LLM_API_KEY=<ta clé>`
   - `LLM_BASE_URL=<l'URL OpenAI-compatible>`
   - `LLM_MODEL=<le nom du modèle>`
4. Le `Dockerfile` reconstruit automatiquement l'index depuis `knowledge_base/` puis démarre l'API sur le port `7860`.
5. Après le démarrage, vérifie `https://<utilisateur>-<nom-du-space>.hf.space/health`.

Hugging Face peut mettre le Space en veille après une période d'inactivité. Le premier démarrage après veille peut prendre plusieurs minutes à cause du chargement du modèle d'embeddings.

### Frontend sur GitHub Pages

1. Ouvre **Settings > Pages** du dépôt GitHub.
2. Sélectionne **GitHub Actions** comme source.
3. Dans **Settings > Secrets and variables > Actions > Variables**, ajoute `VITE_API_URL` avec l'URL publique du Space, sans `/` final.
4. Pousse les modifications sur la branche `main`.
5. Le workflow [deploy-pages.yml](.github/workflows/deploy-pages.yml) construit et publie automatiquement le frontend.
6. L'adresse sera `https://rafazidi.github.io/RAFED_AI_Career_Assistant/`.

Remarque : les offres gratuites peuvent changer de quota ou de modèle d'utilisation. Vérifie les conditions du fournisseur choisi avant une publication.

## Structure

```text
RAFED IA/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   │   ├── llm.py
│   │   │   └── rag.py
│   │   └── ingest.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── knowledge_base/
├── docs/
├── .env.example
├── .gitignore
└── README.md
```
