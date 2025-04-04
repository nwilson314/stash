# stash - personal content queue

## 📌 overview
**stash** is a lightweight system for **capturing, organizing, and consuming** links (articles, podcasts, videos) with ai-assisted summaries.  
it integrates with **mobile shortcuts**, a **cli**, **obsidian**, a simple **web ui** (using sveltekit + tailwind), and a **firefox extension** for quick saves—ensuring your content stays accessible and ephemeral.

---

## 🔹 features

### 1️⃣ capturing links (input)
- **mobile**  
  - ios shortcut → share menu sends links to `POST /save`
- **cli**  
  - planned: bash script (`fzf`) for quick saving
- **web ui**  
  - minimal sveltekit + tailwind deployment at `link-stash.app`
  - tabbed interface separating **unread** vs. **read** links
  - inline form to add new links (url + optional note)
  - mark read & delete links quickly
  - **link details page** with full information and category management
- **firefox extension**  
  - one-click saving from the toolbar and via a hotkey
  - integrated login that stores the access token for bearer auth
  - built using a non-persistent event page (minimal overhead)
  - submitted to mozilla addons (check for approval & updates)

### 2️⃣ organizing content
- **categories**
  - create custom categories to organize links
  - assign links to categories manually or via ai
  - filter your stash by category
- **ai-powered features**
  - automatic link categorization
  - ai-generated short summaries for quick context
  - weekly digest newsletters of your saved content

---

## 🔹 api - storage & retrieval

### current api endpoints
- `POST /users/register` → user registration  
- `POST /users/login` → user authentication (returns jwt / access token)  
- `POST /links/save` → save a link *(requires authentication)*  
- `GET /links` → retrieve all saved links *(requires authentication)*  
- `PATCH /links/{id}/read` → mark a link as read *(requires authentication)*  
- `DELETE /links/{id}` → remove a link *(requires authentication)*  
- `GET /links/{id}` → get link details *(requires authentication)*
- `GET /categories` → get all categories *(requires authentication)*
- `POST /categories` → create a new category *(requires authentication)*
- `POST /links/{id}/category` → assign a category to a link *(requires authentication)*
- `PATCH /users/newsletter` → update newsletter preferences *(requires authentication)*

### planned api endpoints
- `POST /summarize` → ai-generated summary of a link

### database model
postgres on fly.io with `users`, `links`, and `categories` tables:

- `users` table stores `id`, `email`, `hashed_password`, `api_key` (optional), and ai/newsletter preferences
- `links` table stores `id`, `user_id` (foreign key), `url`, `note`, `timestamp`, `read` status, `title`, `category_id`, and ai-generated data
- `categories` table stores `id`, `user_id` (foreign key), `name`, and `created_at`

### orm & migration
- using **sqlmodel**
- managing schema updates with **alembic**

---

## 🔹 retrieving & using links

- **obsidian sync**: python script fetches `GET /links` and writes to a markdown file
- **web ui**: sveltekit + tailwind at `link-stash.app`
  - filter by category
  - view detailed link information
  - manage categories
- **cli picker**: (planned) open links interactively using `fzf`
- **ai features**:  
  - automatic categorization  
  - short summaries for quick context
  - weekly digest newsletters

---

## 🔹 authentication flow

### token-based authentication
- users log in via `POST /users/login`, which returns an **access token**
- the token is stored in an httpOnly cookie for the web ui, and in the extension's local storage (for the firefox extension)
- backend checks the token for authentication on all protected routes
- users log out by clearing the cookie (or removing the stored token in the extension)

### user auth in sveltekit
- when logging in, the **backend sets the token in a cookie**
- protected routes read the token from cookies (`+page.server.ts`)
- if no valid token, user is redirected to `/users/login`
- logout button clears the cookie and redirects to `/users/login`

---

## 🔹 frontend & ui updates

### landing page
- dark theme, minimal styling
- auto-redirects users to `/stash` if already logged in
- showcases core features and value proposition

### stash ui
- displays **unread & read** links
- uses **server-side load (`+page.server.ts`)** to fetch links securely
- logout button in the top right
- category filtering
- link details page for full information

### documentation
- dedicated page explaining how to use stash
- information about browser extensions
- api documentation

---

## 🔹 roadmap

**phase 1** (complete):  
- backend on fly.io (save and retrieve links)
- ios shortcut capture 
- user authentication & token-based storage
- basic db model with user ownership
- full web ui with sveltekit (tabs for unread/read)
- firefox extension for quick saves (completed & submitted)

**phase 2** (mostly complete): 
- chrome extension for quick saves (planned)
- auto-categorization & tagging (completed)
- ai summarization (completed)
- link details page (completed)
- weekly digest newsletters (completed)

**phase 3** (future):  
- email-based link capture
- some sort of obsidian integration
- audio to text for spotify/youtube podcasts and vids

---

## 🔹 deployment

- **backend**: fastapi + postgres on fly.io
- **frontend**: sveltekit on vercel (link-stash.app)
- **firefox extension**: submitted to mozilla addons (available upon approval)
- **cli**: local scripts

---

## 🔹 development principles

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

---

## 🔹 next steps

1. maintain and iterate on the firefox extension  
   - monitor user feedback and update as needed
2. build the chrome extension (planned)
3. refine ai summarization and categorization
4. improve newsletter generation and delivery
5. keep refining the ui
6. build obsidian integration
7. add cli picker (`fzf`)
8. add email-based link capture
9. audio to text for spotify/youtube podcasts and vids

that's it. ephemeral & frictionless.
