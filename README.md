# 🔐 PromptGuard  
An AI-powered prompt safety firewall that detects jailbreak attempts, illegal intent, harmful queries, and unsafe semantic patterns using rule-based + semantic-level analysis.

---

## 🌟 Features  

- 🚧 **Rule-Based Firewall** (expanded illegal detection, jailbreak patterns, self-harm, hate-speech)  
- 🧠 **Semantic Analyzer** using MiniLM embeddings (detects meaning-level dangerous intent)  
- 🔎 **Sanitizer Engine** to rewrite unsafe prompts safely  
- 🖥️ **React Frontend** with dark/light mode, status indicators, and animated UI  
- ⚡ **Real-time API Health Monitoring**  
- 📊 **Detailed Result Panel** (semantic score bar, reasons, sanitized prompt, raw JSON)

---

## 📁 Project Structure  

```
PromptGuard/
│
├── backend/
│   ├── api.py
│   ├── detectors/
│   │   ├── analyzer.py
│   │   ├── rules.py
│   │   ├── semantic.py
│   │   ├── sanitizer.py
│   │   ├── logger.py
│   └── tests/
│
├── frontend/
│   ├── src/App.jsx
│   ├── components/ResultPanel.jsx
│   ├── App.css
│   └── ResultPanel.css
│
├── README.md
└── .gitignore
```

---

# 🛠️ Installation & Setup

> **Prerequisites**
- Python 3.10+
- Node.js 18+
- Git installed

---

### **1️⃣ Clone the Repository**

```bash
git clone https://github.com/archoudhury19/PromptGuard.git
cd PromptGuard
```

---

### **2️⃣ Backend Setup (FastAPI)**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --reload --port 9000
```

Backend runs at:

```
http://127.0.0.1:9000
```

---

### **3️⃣ Frontend Setup (React + Vite)**

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

# 🚀 Deployment Guide (Step-by-Step)

You can deploy PromptGuard in 2 ways:

---

## **A. Deploy Backend on Render (Free Tier)**

1. Push your project to GitHub  
2. Go to **https://render.com**  
3. Click **New Web Service**  
4. Select repo → choose `backend/` folder  
5. Set:
   - Runtime: **Python**
   - Start Command:  
     ```bash
     uvicorn api:app --host 0.0.0.0 --port 10000
     ```
6. Deploy  
7. Copy Render backend URL (example):  
   ```
   https://promptguard-backend.onrender.com
   ```

---

## **B. Deploy Frontend on Vercel**

1. Go to **https://vercel.com**  
2. "Add New Project" → Select your repo  
3. Select `frontend/` folder  
4. Build Command:
   ```
   npm install
   npm run build
   ```
5. Add environment variable:

   ```
   VITE_BACKEND_URL=https://promptguard-backend.onrender.com
   ```

6. Deploy 🎉

---

# 👨‍💻 Author

**Ankur Ray Choudhury**  
Developer • AI & Security Enthusiast  
India  

GitHub: https://github.com/archoudhury19  

---

# 🤝 Contribution

Contributions are welcome!

If you want to submit improvements:

1. Fork this repo  
2. Create a new branch  
3. Commit changes  
4. Open a Pull Request  

---

# 💬 Feedback  

If you want to suggest improvements, open an **Issue** or contact:

📧 Email: *your email here*  
🐙 GitHub Issues: https://github.com/archoudhury19/PromptGuard/issues

---

# 🙏 Acknowledgements  

- **SentenceTransformers** for embedding models  
- **FastAPI** for backend  
- **React + Vite** for frontend  
- **Google GDG FIEM** for hosting the Hack-to-Hire Ideathon  
- Special thanks to mentors & friends who inspired and reviewed the project  

---