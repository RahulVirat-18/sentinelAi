// Simple in-system modal and toast utility
(function(){
    // Inject basic styles once
    const css = `
    .sai-modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:2000}
    .sai-modal{background:#0f1526;color:#fff;border-radius:8px;padding:20px;max-width:520px;width:90%;box-shadow:0 8px 30px rgba(0,0,0,0.6);font-family:Segoe UI,Arial,sans-serif}
    .sai-modal h3{margin:0 0 10px;font-size:1.1rem}
    .sai-modal p{margin:0 0 15px;color:#cfcfcf}
    .sai-modal .sai-buttons{display:flex;gap:10px;justify-content:flex-end}
    .sai-btn{padding:8px 12px;border-radius:6px;border:0;cursor:pointer;font-weight:600}
    .sai-btn.confirm{background:#e94560;color:white}
    .sai-btn.cancel{background:#2c3e50;color:#cfcfcf}

    .sai-toast{position:fixed;right:20px;top:20px;z-index:3000;background:#333;color:white;padding:12px 18px;border-radius:6px;box-shadow:0 6px 20px rgba(0,0,0,0.4);font-weight:600}
    .sai-toast.success{background:linear-gradient(45deg,#4caf50,#2e7d32)}
    .sai-toast.error{background:linear-gradient(45deg,#e94560,#c62828)}
    `;
    const style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);

    // Helpers
    window.showAlert = function(message, type='info', timeout=4000){
        const t = document.createElement('div');
        t.className = 'sai-toast ' + (type === 'success'? 'success' : (type === 'error' ? 'error' : ''));
        t.innerText = message;
        document.body.appendChild(t);
        setTimeout(()=>{ t.style.opacity = '0'; t.addEventListener('transitionend', ()=> t.remove()); }, timeout);
        // provide slight fade via CSS (not defined) fallback: remove after timeout
        setTimeout(()=>{ if(t.parentElement) t.remove(); }, timeout+600);
    }

    window.showConfirm = function(message, onConfirm, onCancel){
        // Create overlay
        const overlay = document.createElement('div'); overlay.className = 'sai-modal-overlay';
        const modal = document.createElement('div'); modal.className = 'sai-modal';
        modal.innerHTML = `<h3>Confirmation</h3><p>${message}</p>`;
        const btnBar = document.createElement('div'); btnBar.className = 'sai-buttons';

        const cancelBtn = document.createElement('button'); cancelBtn.className = 'sai-btn cancel'; cancelBtn.innerText = 'Cancel';
        const confirmBtn = document.createElement('button'); confirmBtn.className = 'sai-btn confirm'; confirmBtn.innerText = 'Confirm';

        btnBar.appendChild(cancelBtn); btnBar.appendChild(confirmBtn);
        modal.appendChild(btnBar); overlay.appendChild(modal);
        document.body.appendChild(overlay);

        function cleanup(){ if(overlay.parentElement) overlay.remove(); }
        cancelBtn.onclick = function(){ cleanup(); if(typeof onCancel === 'function') onCancel(); }
        confirmBtn.onclick = function(){ cleanup(); if(typeof onConfirm === 'function') onConfirm(); }

        // Close on Escape
        const escHandler = (e)=>{ if(e.key === 'Escape'){ cleanup(); window.removeEventListener('keydown', escHandler); if(typeof onCancel === 'function') onCancel(); } }
        window.addEventListener('keydown', escHandler);
    }
})();
