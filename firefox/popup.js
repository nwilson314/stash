document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const saveUi = document.getElementById('save-ui');
    const loginBtn = document.getElementById('login-btn');
    const saveBtn = document.getElementById('save-btn');
    const logoutBtn = document.getElementById('logout-btn');
  
    // check login state from extension storage
    chrome.storage.local.get('loggedIn', (result) => {
      if (result.loggedIn) {
        loginForm.style.display = 'none';
        saveUi.style.display = 'block';
      } else {
        loginForm.style.display = 'block';
        saveUi.style.display = 'none';
      }
    });
  
    loginBtn.addEventListener('click', () => {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        fetch('https://stash-link.fly.dev/users/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        })
          .then(res => {
            if (!res.ok) throw new Error('login failed');
            return res.json();
          })
          .then(data => {
            // store the token for later use
            chrome.storage.local.set({ accessToken: data.access_token, loggedIn: true }, () => {
              loginForm.style.display = 'none';
              saveUi.style.display = 'block';
            });
          })
          .catch(err => alert(err.message));
      });
  
    logoutBtn.addEventListener('click', () => {
      // simple logout; ideally, hit a logout endpoint too
      chrome.storage.local.remove('loggedIn', () => {
        loginForm.style.display = 'block';
        saveUi.style.display = 'none';
      });
    });
  
    saveBtn.addEventListener('click', () => {
      // tell background.js to save the current page
      chrome.runtime.sendMessage({ action: 'saveCurrentPage' });
    });
  });
  