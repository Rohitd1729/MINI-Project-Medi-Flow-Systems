# 🚀 Quick Start Guide - Medi-Flow Systems

## Step-by-Step Instructions

### Step 1: Install Backend Dependencies

Open terminal in the backend folder and run:

```bash
cd backend
pip install -r requirements.txt
```

**This installs:**
- Flask (web framework)
- PostgreSQL adapter
- NLP libraries (spaCy, FuzzyWuzzy)
- ML libraries (scikit-learn)
- And more...

**Time:** 2-5 minutes

---

### Step 2: Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

**Time:** 1-2 minutes

---

### Step 3: Setup PostgreSQL Database

1. **Open PostgreSQL** (pgAdmin or psql)

2. **Create Database:**
   ```sql
   CREATE DATABASE msms_db;
   ```

3. **Update config.py** (if needed):
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:YOUR_PASSWORD@localhost/msms_db'
   ```
   Replace `YOUR_PASSWORD` with your PostgreSQL password.

---

### Step 4: Initialize Database

```bash
python init_db.py
```

**This creates all tables:**
- users, roles
- medicines, companies
- sales, purchases
- chatbot_kb, chatbot_logs
- audit_log

---

### Step 5: Load Chatbot Knowledge Base

```bash
python chatbot/loader.py
```

**This loads 25 medications** into the chatbot database.

**Expected output:**
```
Successfully loaded 25 drugs into the database
```

---

### Step 6: Start Backend Server

```bash
python app.py
```

**Expected output:**
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

**Keep this terminal open!**

---

### Step 7: Install Frontend Dependencies

Open a **NEW terminal** and run:

```bash
cd frontend
npm install
```

**Time:** 2-3 minutes

---

### Step 8: Start Frontend Server

```bash
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view the app in the browser.
Local: http://localhost:3000
```

**Browser will open automatically!**

---

## 🎯 Test the System

### 1. Login
- **URL:** http://localhost:3000
- **Username:** admin
- **Password:** admin123

### 2. Test Chatbot
Look for the chat widget (usually bottom-right corner)

**Try these queries:**
```
✅ "What is the dosage of Paracetamol?"
✅ "Side effects of Ibuprofen"
✅ "Alternatives to Aspirin"
✅ "What is Omeprazole used for?"
```

**Test typo handling:**
```
✅ "What is paracetmol used for?"
✅ "Side effects of ibuprofn"
```

**Test context awareness:**
```
User: "Tell me about Paracetamol"
Bot: [Response]
User: "What are the side effects?"  ← No need to repeat drug name!
Bot: [Side effects of Paracetamol]
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"
**Solution:** Make sure you're in the correct directory
```bash
cd backend  # For backend commands
cd frontend # For frontend commands
```

### Issue: "Database connection error"
**Solution:** 
1. Check PostgreSQL is running
2. Verify database name: `msms_db`
3. Check password in `config.py`

### Issue: "Port 5000 already in use"
**Solution:** 
```bash
# Find and kill the process
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

### Issue: "spaCy model not found"
**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: Frontend won't start
**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────┐
│   Frontend (React)                  │
│   http://localhost:3000             │
└──────────────┬──────────────────────┘
               │ REST API
               ▼
┌─────────────────────────────────────┐
│   Backend (Flask)                   │
│   http://localhost:5000             │
│                                     │
│   ├─ NLP Engine                     │
│   ├─ Inference Engine               │
│   └─ Training System                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   PostgreSQL Database               │
│   msms_db                           │
└─────────────────────────────────────┘
```

---

## ✅ Success Checklist

- [ ] Backend dependencies installed
- [ ] spaCy model downloaded
- [ ] PostgreSQL database created
- [ ] Database initialized
- [ ] Chatbot knowledge base loaded
- [ ] Backend server running (port 5000)
- [ ] Frontend dependencies installed
- [ ] Frontend server running (port 3000)
- [ ] Can login with admin/admin123
- [ ] Chatbot responds to queries
- [ ] Typo handling works
- [ ] Context awareness works

---

## 🎓 API Endpoints

Once backend is running, test these:

### Health Check
```bash
curl http://localhost:5000/
```
**Expected:** `{"message": "Medi-Flow Systems API - Smart Management. Better Health."}`

### Chatbot Query
```bash
curl -X POST http://localhost:5000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the dosage of Paracetamol?", "user_id": 1}'
```

### Submit Feedback
```bash
curl -X POST http://localhost:5000/api/chat/training/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "log_id": 1,
    "feedback_type": "rating",
    "feedback_data": {"rating": 5}
  }'
```

---

## 🎉 You're All Set!

Your **Medi-Flow Systems** is now running!

**Next Steps:**
1. Explore the dashboard
2. Test all chatbot features
3. Try the inventory management
4. Check the reports section
5. Practice your demo presentation

---

**Need Help?** Check the documentation:
- README.md - Project overview
- AI_DOCUMENTATION.md - AI component details
- CHATBOT_FEATURES.md - Chatbot capabilities
- PROJECT_REVIEW.md - Code review
- FIXES_APPLIED.md - Recent fixes

---

**Medi-Flow Systems** - Smart Management. Better Health. 🏥
