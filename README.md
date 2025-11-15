# 🔐 **PromptGuard**

*An AI-powered prompt-safety firewall that detects jailbreaks, illegal intent, harmful queries, and unsafe semantic behavior — using hybrid rule-based + semantic analysis.*

---

## 🌟 **Features**

* 🚧 **Rule-Based Firewall** (illegal intent, jailbreak detection, violence, self-harm, hate-speech, hacking, drug orders)
* 🧠 **Semantic Analyzer**

  * Cloud mode → MiniLM (lightweight)
  * Local mode → MPNet (high accuracy)
* 🔄 **Auto-switching semantic engine** depending on environment
* 🔎 **Sanitizer Engine** to rewrite unsafe prompts
* 🎨 **Modern React Frontend** with animations & dark/light mode
* ⚡ **Real-time API health monitoring**
* 📊 **Detailed Analysis Output** (score, reasons, sanitized text, raw JSON)

---

## 📁 **Project Structure**

```
PromptGuard/
│
├── backend/
│   ├── api.py
│   ├── detectors/
│   │   ├── analyzer.py
│   │   ├── rules.py
│   │   ├── semantic_light.py
│   │   ├── semantic_heavy.py
│   │   ├── sanitizer.py
│   │   ├── logger.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/App.jsx
│   ├── components/ResultPanel.jsx
│   ├── components/HistoryPanel.jsx
│   ├── App.css
│
├── README.md
└── .gitignore
```

---

# 🛠️ **Local Installation**

## **1️⃣ Clone Repository**

```bash
git clone https://github.com/archoudhury19/PromptGuard.git
cd PromptGuard
```

---

# **2️⃣ Backend Setup (FastAPI)**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn api:app --reload --port 9000
```

Backend runs at:

```
http://127.0.0.1:9000
```

---

# **3️⃣ Frontend Setup (React + Vite)**

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://127.0.0.1:5173
```

---

# 🚀 **Deployment Guide**

You can deploy PromptGuard using **free services**.

---

# ⚙️ **A. Backend Deployment (Railway)**

1. Push project to GitHub
2. Go to: [https://railway.app](https://railway.app)
3. Create **New Service → Deploy from Repo**
4. Set **Build Root** to:

```
backend
```

5. Railway auto-detects Python
6. Ensure your **Procfile** exists:

```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

7. Add environment variable:

```
GEMINI_API_KEY=your-key
```

8. Deploy
9. Copy backend URL, example:

```
https://promptguard-production.up.railway.app
```

---

# 🌐 **B. Frontend Deployment (Netlify)**

1. Visit [https://app.netlify.com](https://app.netlify.com)
2. “Add New Site” → “Import from GitHub”
3. Set **Base directory**:

```
frontend
```

4. Build command:

```
npm run build
```

5. Publish directory:

```
dist
```

6. Add Env Variable:

```
VITE_API_URL=https://promptguard-production.up.railway.app
```

7. Deploy 🎉

---

# 👨‍💻 **Author**

**Ankur Ray Choudhury**
AI & Security Enthusiast — India

GitHub:
[https://github.com/archoudhury19](https://github.com/archoudhury19)

---

# 🤝 **Contributing**

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Open a Pull Request

---

# 💬 **Feedback**

Have suggestions?

📌 GitHub Issues:
[https://github.com/archoudhury19/PromptGuard/issues](https://github.com/archoudhury19/PromptGuard/issues)

---

# 🙏 **Acknowledgements**

* SentenceTransformers
* FastAPI
* React + Vite
* Google GDG FIEM — Hack-to-Hire Ideathon

---