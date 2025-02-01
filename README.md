# stash - personal content queue

## 📌 overview
**stash** is a lightweight system for **capturing, organizing, and consuming** links (articles, podcasts, videos) with ai-assisted summaries.  
it integrates with **mobile shortcuts**, a **cli**, **obsidian**, and a simple **web ui** (using sveltekit + tailwind) to keep content accessible and ephemeral.

---

## 🔹 features

### 1️⃣ capturing links (input)
- **mobile**  
  - ios shortcut → share menu sends links to `POST /save`  
- **cli**  
  - planned: bash script (`fzf`) for quick saving  
- **web ui**  
  - minimal sveltekit + tailwind deployment at `stash-peach.vercel.app`  
  - tabbed interface separating **unread** vs. **read** links  
  - inline form to add new links (url + optional note)  
  - mark read & delete links quickly
- **docs**
  - web docs detailing how to create the ios shortcut
  - browser extension docs (one-click saves) (planned)
  - obsidian docs (planned)
- **future**  
  - browser extension (one-click saves)  
  - email forwarding (`stash@mydomain.com`)  
  - obsidian sync (python script fetches `GET /links` and writes to a markdown file)
  - obsidian plugin (if feeling wild)

---

## 2️⃣ api - storage & retrieval

### current api endpoints
- `POST /users/register` → user registration  
- `POST /users/login` → user authentication (returns jwt)  
- `POST /links/save` → save a link *(requires authentication)*  
- `GET /links` → retrieve all saved links *(requires authentication)*  
- `PATCH /links/{id}/read` → mark a link as read *(requires authentication)*  
- `DELETE /links/{id}` → remove a link *(requires authentication)*  

### planned api endpoints
- `POST /summarize` → ai-generated summary of a link  

### database model
postgres on fly.io with a `users` table and a `links` table:

- `users` table stores `id`, `email`, `hashed_password`, and an optional `api_key`  
- `links` table stores `id`, `user_id` (foreign key), `url`, `note`, `timestamp`, and `read` status  

### orm & migration
- using **sqlmodel**  
- managing schema updates with **alembic**  

---

## 3️⃣ retrieving & using links

- **obsidian sync**: python script fetches `GET /links` and writes to a markdown file  
- **web ui**: sveltekit + tailwind at `stash-peach.vercel.app`  
- **cli picker**: (planned) open links interactively using `fzf`  
- **future**:  
  - ai summarization  
  - category tagging  

---

## 4️⃣ authentication flow

### token-based authentication
- users log in via `POST /users/login`, which returns a **jwt access token**  
- **token is stored in an httpOnly cookie** for security  
- backend checks the token for authentication on all protected routes  
- users log out by clearing the cookie  

### user auth in sveltekit
- when logging in, the **backend sets the token in a cookie**  
- protected routes read the token from cookies (`+page.server.ts`)  
- if no valid token, user is redirected to `/login`  
- logout button clears the cookie and redirects to `/login`  

---

## 5️⃣ frontend & ui updates

### landing page
- dark theme, minimal styling  
- auto-redirects users to `/stash` if already logged in  

### stash ui
- displays **unread & read** links  
- uses **server-side load (`+page.server.ts`)** to fetch links securely  
- logout button in the top right  

---

## 6️⃣ roadmap

**phase 1** (complete-ish):  
- backend on fly.io (save and retrieve links)  
- ios shortcut capture 
- user authentication & token-based storage  
- basic db model with user ownership
- full web ui with sveltekit (tabs for unread/read)

**phase 2** (ongoing): 
- browser extension for quick saves
- auto-categorization & tagging  
- ai summarization  

**phase 3** (future):  
  
- email-based link capture
- some sort of obsidian integration

---

## 7️⃣ deployment

- **backend**: fastapi + postgres on fly.io  
- **frontend**: sveltekit on vercel (stash-peach.vercel.app)  
- **cli**: local scripts

## 8️⃣ development principles

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
11. **"just keep shipping"** - iterate, don’t stall.  

## 9️⃣ next steps

1. build a barebones browser extension (one-click `/save`).
  a. zen browser (firefox) extension
  b. chrome extension
2. experiment with ai summarization (maybe `post /summarize`).
3. nail down auto categorization, tagging, and title auto-creation. 
3. keep refining the ui.
4. build obsidian integration.
5. add cli picker (`fzf`).
6. add email-based link capture.
7. audio to text for spotify/youtube podcasts and vids.

that's it. ephemeral & frictionless.  