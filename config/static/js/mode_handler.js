// Mode handling JS (simple & effective)
(function () {
  const bannerRoot = document.getElementById('mode-banner-root');
  const vulnLabel = document.getElementById('vuln-label');
  const toggleBtn = document.getElementById('toggle-mode-btn');

  let sessionMode = INITIAL_SESSION_MODE;
  let globalVuln = false;

  function getCookie(name) {
    if (!document.cookie) return null;
    const pairs = document.cookie.split(';').map(c => c.trim());
    for (const p of pairs) {
      if (p.startsWith(name + '=')) return decodeURIComponent(p.substring(name.length + 1));
    }
    return null;
  }

  function renderBanner() {
    bannerRoot.innerHTML = '';
    const isVuln = globalVuln && sessionMode === 'vulnerable';
    if (isVuln) {
      const div = document.createElement('div');
      div.className = 'mode-banner-vuln';
      div.innerHTML = '⚠️ <strong>VULNERABLE LAB MODE ACTIVE</strong>';
      bannerRoot.appendChild(div);
      vulnLabel.textContent = '⚠ VULNERABLE LAB';
      toggleBtn.textContent = 'Vulnerable Mode';
      toggleBtn.setAttribute('aria-pressed', 'true');
      toggleBtn.style.backgroundColor = '#dc3545';
      toggleBtn.style.color = '#fff';
    } else {
      const div = document.createElement('div');
      div.className = 'mode-banner-secure';
      div.textContent = '✔ Secure Mode — vulnerabilities disabled (or session not toggled).';
      bannerRoot.appendChild(div);
      vulnLabel.textContent = '✔ SECURE';
      toggleBtn.textContent = 'Secure Mode';
      toggleBtn.setAttribute('aria-pressed', 'false');
      toggleBtn.style.backgroundColor = '#4CAF50';
      toggleBtn.style.color = '#fff';
    }
  }

  async function fetchModeStatus() {
    try {
      const r = await fetch('/mode-status/', { credentials: 'same-origin' });
      if (!r.ok) throw new Error('status ' + r.status);
      const json = await r.json();
      globalVuln = Boolean(json.global_vulnerable_mode);
      sessionMode = json.session_mode || sessionMode;
      renderBanner();
    } catch (e) {
      // still render something
      console.warn('mode-status fetch error', e);
      globalVuln = false;
      renderBanner();
    }
  }

  async function toggleMode() {
    // ask every time
    if (!confirm('⚠️ Are you sure you want to switch lab mode?')) return;

    try {
      const csrf = getCookie('csrftoken');
      const headers = { 'Content-Type': 'application/json' };
      if (csrf) headers['X-CSRFToken'] = csrf;

      const r = await fetch('/accounts/toggle_mode/', {
        method: 'POST',
        credentials: 'same-origin',
        headers,
        body: JSON.stringify({})
      });

      if (!r.ok) {
        const text = await r.text().catch(() => '');
        throw new Error('HTTP ' + r.status + ' ' + text);
      }

      const json = await r.json();
      if (json.mode) {
        sessionMode = json.mode;
        alert('✅ Mode changed to: ' + json.mode.toUpperCase()); // confirmation every time
        renderBanner();
        // reload so templates/context reflect new mode
        window.location.reload();
      } else if (json.error) {
        throw new Error('Server error: ' + json.error);
      }
    } catch (err) {
      console.error('toggleMode error', err);
      alert('❌ Could not change mode — check console for details.');
    }
  }

  // attach handler
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function (ev) {
      ev.preventDefault();
      toggleMode();
    });
  }

  // initial render & poll
  renderBanner();
  fetchModeStatus();
  setInterval(fetchModeStatus, 5000);
})();
