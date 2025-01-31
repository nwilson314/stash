# stash - personal content queue

## 📌 overview
**stash** is a lightweight system for **capturing, organizing, and consuming** links (articles, podcasts, videos) with ai-assisted summaries.  
it integrates with **mobile shortcuts**, a **cli**, **obsidian**, and a simple **web ui** (using sveltekit + tailwind) to keep content accessible and ephemeral.

---

## 🔹 features

### 1️⃣ capturing links (input)
- **mobile**  
  - ios shortcut → share menu sends links to `post https://stash-link.fly.dev/save`
- **cli**  
  - planned: bash script (fzf) for quick saving
- **web ui**  
  - minimal sveltekit + tailwind deployment at [stash-peach.vercel.app](https://stash-peach.vercel.app)  
  - tabbed interface separating **unread** vs. **read** links  
  - inline form to add new links (url + optional note)  
  - mark read & delete links quickly
- **future**  
  - browser extension (one-click saves)  
  - email forwarding (stash@mydomain.com)  

---

## 2️⃣ api - storage & retrieval

### current api endpoints
- `post /save` → save a link  
- `get /links` → retrieve all saved links  
- `patch /links/{id}/read` → mark a link as read  
- `delete /links/{id}` → remove a link  

### planned api endpoints
- `post /summarize` → ai-generated summary of a link  

### database model
postgres on fly.io with a `Link` table featuring `id`, `url`, `note`, `timestamp`, plus a `read` boolean for read-tracking.

### orm & migration
- using **sqlmodel**  
- managing schema updates with **alembic**  

---

## 3️⃣ retrieving & using links

- **obsidian sync**: python script fetches `get /links` and writes to `saved_links.md`  
- **web ui**: sveltekit + tailwind at stash-peach.vercel.app (includes inline add form + tabs)  
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
- minimal web ui with sveltekit (tabs for unread/read)  
- user auth (registration/login) for sharing  
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

to share stash with friends, we introduce a simple registration/login flow:
- **user accounts**: store username, hashed password, etc.  
- **login/registration**: minimal forms or invite-based.  
- **token-based auth**: generate a token (jwt or similar) on login.  
- **private stash**: each user sees only their own links.  

---

## 8️⃣ next steps

1. finalize user auth in the backend and integrate in the web ui.  
2. build a barebones browser extension (one-click `/save`).  
3. experiment with ai summarization (maybe `post /summarize`).  
4. keep refining the tabbed sveltekit ui & read-tracking.  

that’s it. ephemeral & frictionless.  
