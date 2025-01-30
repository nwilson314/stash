# Stash - Personal Content Queue  

## 📌 Overview  
**Stash** is a lightweight system for **capturing, organizing, and consuming** links (articles, podcasts, videos) with AI-assisted summaries.  
It integrates with **mobile shortcuts, CLI tools, Obsidian, and a web UI** to keep content accessible and useful.

---

## 🔹 Features  

### **1️⃣ Capturing Links (Input)**  
✅ **Mobile:**  
   - **iOS Shortcut** → Share menu sends links to `POST https://stash-link.fly.dev/save`

✅ **CLI:**  
   - **Bash script (`fzf`)** for quick saving (Planned)  

✅ **Web UI (Planned):**  
   - **Dashboard for viewing & managing links**  
   - **Hosted on Vercel**  

🚀 **Future:**  
   - **Browser extension** for one-click saving  
   - **Email forwarding** (`stash@mydomain.com` auto-saves links)  

---

## **2️⃣ API - Storage & Retrieval**  

### **Current API Endpoints**  
- `POST /save` → Save a link  
- `GET /links` → Retrieve all saved links  

### **Planned API Endpoints**  
- `PATCH /links/{id}/read` → Mark link as read  
- `DELETE /links/{id}` → Remove a link  
- `POST /summarize` → AI-generated summary of a link  

### **Database Model (Postgres on Fly.io)**  
```python
class Link(Base):
    id: UUID
    url: str
    note: str
    timestamp: datetime
```

### ORM and Migration strategy
- **SQLModel** for defining the database schema
- **Alembic** migrations for managing database changes

## 3️⃣ Retrieving & Using Links

✅ **Obsidian Sync**

- Python script fetches links from GET /links
- Writes to saved_links.md for easy access

✅ **CLI Picker** (fzf) (Planned)

- Choose & open links interactively from terminal

✅ **Web UI** (stash.vercel.app) (Planned)

- Simple dashboard for managing links
- Search & filtering

🚀 **Future Features**:

- AI Summarization (GPT-4, LlamaIndex)
- Read Tracking (read: bool)

## 4️⃣ Roadmap

✅ **Phase 1: Core Capture System**

- Backend running on Fly.io (POST /save, GET /links)
- iOS Shortcut for quick saving
- Basic database model (Postgres)

🚀 **Phase 2: Retrieval & UI**

- Build a Basic UI (stash.vercel.app)
- Implement Read Tracking (read: bool)
- CLI Picker (fzf for selecting links)
- Browser Extension for Quick Saves

🚀 **Phase 3: AI & Intelligence**

- AI Summarization (On-demand article summaries)
- Auto-categorization & tagging

## 5️⃣ Deployment

- Backend: Fly.io (FastAPI + Postgres)
- Frontend (Planned): Vercel (SvelteKit)
- CLI & Scripts: Runs locally

## 6️⃣ General Development Rules (for AIs)

these rules ensure that any AI working on stash understands the project’s core philosophy:

1. Check the top-level README for an overview. this is THE README. everything is inside.
2. Prioritize speed and simplicity, no bloat.
3. Keep the workflow low-friction—saving and retrieving links should be instant.
4. For anything aesthetic-related, keep it simple, clean, and elegant. It should not look like trash.
5. Avoid unnecessary features. If a new feature doesn't actively improve usability, it doesn’t belong.
6. Do not add heavy dependencies unless absolutely necessary. Lightweight and efficient is the goal.
7. Frontend should be snappy and minimalistic. No over-engineering, no unnecessary animations, just functional elegance.
8. Avoid corporate/enterprise-style design. This is a personal project—no bloated UIs, dashboards, or complex settings pages.
9. All changes should improve the experience. Every change should either:
    Make saving links faster
    Make retrieving links easier
    Make content more useful (e.g., summaries, categorization)
10. If in doubt, ask: “Would I actually use this daily?” If the answer is no, it’s not worth adding.

## 7️⃣ Next Steps

1️⃣ Build a Basic UI → Display & manage links in a clean interface
2️⃣ Implement Read Tracking (read column in DB)
3️⃣ Develop a Browser Extension for Quick Saves