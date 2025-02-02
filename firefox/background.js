chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'saveCurrentPage') {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          const url = tabs[0].url;
          chrome.storage.local.get('accessToken', (result) => {
            const token = result.accessToken;
            fetch('https://stash-link.fly.dev/links/save', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'authorization': `bearer ${token}`
              },
              body: JSON.stringify({ url })
            })
              .then(res => {
                if (!res.ok) throw new Error('failed to save link');
                return res.json();
              })
              .then(data => console.log('saved:', data))
              .catch(err => console.error(err));
          });
        }
      });
    }
  });
  
  
  // listen for the keyboard shortcut command
  chrome.commands.onCommand.addListener((command) => {
    if (command === 'save-url') {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          const url = tabs[0].url;
          fetch('https://stash-link.fly.dev/links/save', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
          })
            .then(res => {
              if (!res.ok) throw new Error('failed to save link');
              return res.json();
            })
            .then(data => console.log('saved via hotkey:', data))
            .catch(err => console.error(err));
        }
      });
    }
  });
  