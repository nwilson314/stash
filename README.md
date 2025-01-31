# stash - personal content queue

## 📌 overview
**stash** is a lightweight system for **capturing, organizing, and consuming** links (articles, podcasts, videos) with ai-assisted summaries.  
it integrates with **mobile shortcuts**, a **cli**, **obsidian**, and a simple **web ui** (using *sveltekit* + tailwind) to keep content accessible and ephemeral.

---

## 🔹 features

### **1️⃣ capturing links (input)**
- **mobile**  
  - ios shortcut → share menu sends links to `post https://stash-link.fly.dev/save`
- **cli**  
  - planned: bash script (fzf) for quick saving
- **web ui**  
  - minimal sveltekit + tailwind deployment at [stash-peach.vercel.app](https://stash-peach.vercel.app)  
  - view and manage links, mark read, delete
- **future**  
  - browser extension (one-click saves)  
  - email forwarding (stash@mydomain.com)  

---

## **2️⃣ api - storage & retrieval**

### **current api endpoints**  
- `post /save` → save a link  
- `get /links` → retrieve all saved links  
- `patch /links/{id}/read` → mark link as read  
- `delete /links/{id}` → remove a link  

### **planned api endpoints**  
- `post /summarize` → ai-generated summary of a link  

### **database model**  
postgres on fly.io with a `Link` table featuring `id`, `url`, `note`, `timestamp`, and now a `read` boolean for read-tracking.

### **orm & migration**  
- using **sqlmodel**  
- managing schema updates with **alembic**  

---

## **3️⃣ retrieving & using links**

- **obsidian sync**: python script fetches `get /links` and writes to `saved_links.md`  
- **web ui**: sveltekit + tailwind at stash-peach.vercel.app  
- **cli picker**: (planned) open links interactively using fzf  
- **future**:  
  - ai summarization  
  - category tagging  

---

## 4️⃣ roadmap

**phase 1** (complete-ish):  
- backend on fly.io (save and retrieve links)  
- ios shortcut capture  
- basic db model with read column

**phase 2** (ongoing):  
- minimal web ui with sveltekit  
- read tracking & delete endpoints  
- browser extension for quick saves

**phase 3** (future):  
- ai summarization (gpt-4 / llamaindex)  
- auto-categorization & tagging  

---

## 5️⃣ deployment

- **backend**: fastapi + postgres on fly.io  
- **frontend**: sveltekit on vercel (stash-peach.vercel.app)  
- **cli**: local scripts

---

## 6️⃣ general development rules (for ais)

1. check the top-level readme for an overview.  
2. prioritize speed and simplicity, no bloat.  
3. keep workflow low-friction—saving/retrieving is instant.  
4. minimal aesthetics. no trashy interfaces.  
5. avoid feature creep.  
6. no heavy deps unless necessary.  
7. frontend is snappy & minimalistic, no over-engineering.  
8. keep it personal, avoid corporate “enterprise” style.  
9. all changes must improve the experience: faster saves, easier retrieval, more useful content.  
10. if in doubt, ask, “would i actually use this daily?” if no, it’s not worth it.

---

## 7️⃣ user auth

to share stash with friends, we’ll introduce a basic registration/login flow. keep it lightweight:

- **user accounts**:  
  - new table storing user info (username, hashed password, etc)  
- **login/registration**:  
  - minimal forms for sign up & sign in (or just do an invite code approach if you’re lazy)  
- **token-based auth**:  
  - upon login, generate a token (jwt or similar).  
  - all subsequent requests include that token in headers.  
- **private stash**:  
  - each user has their own link storage, so friends can’t rummage around your stash, and vice versa.  

---

## 8️⃣ next steps
1. implement user auth (db, login, registration, token handling).  
2. create a basic browser extension to post links to `/save`.  
3. experiment with ai summarization via `post /summarize`.  
4. keep refining the sveltekit ui & read-tracking.  

*that’s it. ephemeral & frictionless.*  
