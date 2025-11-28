// Profile JS for file preview and validation
(() => {
  const input = document.getElementById('photoInput');
  const preview = document.getElementById('photoPreview');
  const info = document.getElementById('fileInfo');
  if (!input) return;

  const allowedExtsAttr = input.dataset.allowedExts || "";
  const allowedExts = allowedExtsAttr ? allowedExtsAttr.split(',').map(e => e.trim().toLowerCase()) : null;
  const maxBytes = input.dataset.maxBytes ? parseInt(input.dataset.maxBytes, 10) : null;

  input.addEventListener('change', (ev) => {
    const file = ev.target.files && ev.target.files[0];
    if (!file) {
      preview.style.display = 'none';
      info.style.display = 'none';
      preview.src = '';
      return;
    }

    const filename = file.name;
    const sizeKB = Math.round(file.size / 1024);
    const ext = filename.split('.').pop().toLowerCase();

    if (allowedExts) {
      if (!allowedExts.includes(ext)) {
        info.textContent = `❌ Extension ".${ext}" not allowed. Allowed: ${allowedExts.join(', ')}.`;
        info.style.color = '#b91c1c';
        preview.style.display = 'none';
        return;
      }
      if (maxBytes && file.size > maxBytes) {
        info.textContent = `❌ File too large (${sizeKB} KB). Max ${(maxBytes/1024/1024).toFixed(1)} MB.`;
        info.style.color = '#b91c1c';
        preview.style.display = 'none';
        return;
      }
      info.textContent = `✅ ${filename} — ${sizeKB} KB`;
      info.style.color = '#065f46';
    } else {
      info.textContent = `⚠️ Vulnerable mode: no validation. File = ${filename} (${sizeKB} KB)`;
      info.style.color = '#92400e';
    }

    info.style.display = 'block';

    const reader = new FileReader();
    reader.onload = function(e) {
      preview.src = e.target.result;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  });
})();
