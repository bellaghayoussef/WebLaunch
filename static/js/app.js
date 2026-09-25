/**
 * LeadHunter Dashboard Application Logic
 */

let activeLeadOutreach = null;
let currentOutreachData = null;

document.addEventListener('DOMContentLoaded', () => {
  const searchForm = document.getElementById('search-form');
  const searchLoading = document.getElementById('search-loading');
  const searchBtn = document.getElementById('search-btn');
  const tableSearch = document.getElementById('table-search');

  // Search Form Submit
  if (searchForm) {
    searchForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const country = document.getElementById('country-select').value;
      const city = document.getElementById('city-input').value.trim();
      const category = document.getElementById('category-select').value;
      const onlyNoWebsite = document.getElementById('no-website-only').checked;
      const limit = document.getElementById('limit-select').value;

      searchLoading.style.display = 'block';
      searchBtn.disabled = true;
      searchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Prospection en cours...';

      try {
        const res = await fetch('/api/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            country,
            city,
            category,
            only_no_website: onlyNoWebsite,
            limit: parseInt(limit, 10)
          })
        });

        const data = await res.json();
        if (!data.success) {
          throw new Error(data.error || 'Erreur lors de la recherche');
        }

        showToast(`✅ ${data.count} prospects trouvés et enregistrés!`);
        // Refresh page or reload table
        window.location.reload();

      } catch (err) {
        showToast(`❌ Erreur: ${err.message}`);
      } finally {
        searchLoading.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Lancer la recherche';
      }
    });
  }

  // Live filter in leads table
  if (tableSearch) {
    tableSearch.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      const rows = document.querySelectorAll('#leads-body tr');
      rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        if (text.includes(q)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }
});

// Toast notification helper
function showToast(message) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

let currentMockupLead = { id: '', name: '', mockupUrl: '', demoUrl: '' };

// Generate Mockup for a Lead
async function generateMockupForLead(leadId) {
  const row = document.getElementById(`row-${leadId}`);
  const btnGen = row ? row.querySelector('.btn-mockup-generate') : null;
  const btnRegen = row ? row.querySelector('.btn-mockup-regenerate') : null;
  const activeBtn = btnGen || btnRegen;

  if (activeBtn) {
    activeBtn.disabled = true;
    activeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> IA en cours...';
  }

  try {
    const res = await fetch(`/api/generate-mockup/${leadId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || 'Erreur');

    showToast('✨ Nouvelle maquette IA générée avec succès !');

    const leadName = row ? row.getAttribute('data-name') : (currentMockupLead.name || 'Restaurant');
    const demoUrl = data.demo_url || `/demo/${leadId}`;

    // Update row cell with both View and Regenerate buttons
    if (row) {
      const mockupCol = row.querySelector('.col-mockup');
      if (mockupCol) {
        mockupCol.innerHTML = `
          <div style="display:flex;gap:6px;align-items:center;">
            <button class="btn-mockup-view" onclick="openMockupModal('${leadName}', '${data.mockup_url}', '${demoUrl}', '${leadId}')" title="Voir la maquette">
              <i class="fa-solid fa-image"></i> Voir
            </button>
            <button class="btn-mockup-regenerate" onclick="generateMockupForLead('${leadId}')" title="Régénérer une nouvelle version IA">
              <i class="fa-solid fa-arrows-rotate"></i> Régénérer
            </button>
          </div>
        `;
      }
    }

    // Update stats counter
    const statDemos = document.getElementById('stat-demos');
    if (statDemos && btnGen) {
      statDemos.textContent = parseInt(statDemos.textContent || '0', 10) + 1;
    }

    // Refresh or open modal
    openMockupModal(leadName, data.mockup_url, demoUrl, leadId);

  } catch (err) {
    showToast(`❌ Erreur: ${err.message}`);
    if (activeBtn) {
      activeBtn.disabled = false;
      activeBtn.innerHTML = btnRegen 
        ? '<i class="fa-solid fa-arrows-rotate"></i> Régénérer' 
        : '<i class="fa-solid fa-wand-magic-sparkles"></i> Générer Maquette';
    }
  }
}

// Open Mockup Preview Modal
function openMockupModal(name, mockupUrl, demoUrl, leadId) {
  const modal = document.getElementById('mockup-modal');
  const title = document.getElementById('mockup-modal-title');
  const img = document.getElementById('mockup-modal-img');
  const iframe = document.getElementById('mockup-modal-iframe');
  const downloadLink = document.getElementById('mockup-download-link');
  const openLiveBtn = document.getElementById('mockup-open-live-btn');
  const regenBtn = document.getElementById('mockup-modal-regen-btn');

  const resolvedDemoUrl = demoUrl || mockupUrl.replace('/static/mockups/', '/demo/').replace('.png', '');
  const resolvedLeadId = leadId || (resolvedDemoUrl.split('/').pop());

  currentMockupLead = {
    id: resolvedLeadId,
    name: name,
    mockupUrl: mockupUrl,
    demoUrl: resolvedDemoUrl
  };

  title.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Maquette Professionnelle — <strong>${name}</strong>`;
  img.src = mockupUrl + '?t=' + Date.now();
  downloadLink.href = mockupUrl;

  if (iframe) iframe.src = resolvedDemoUrl;
  if (openLiveBtn) openLiveBtn.href = resolvedDemoUrl;
  if (regenBtn) {
    regenBtn.disabled = false;
    regenBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Régénérer avec l\'IA';
  }

  switchMockupView('img');
  modal.style.display = 'flex';
}

// Regenerate from inside the modal
async function regenerateCurrentModalLead() {
  if (!currentMockupLead.id) {
    showToast('❌ Identifiant du prospect introuvable.');
    return;
  }

  const regenBtn = document.getElementById('mockup-modal-regen-btn');
  if (regenBtn) {
    regenBtn.disabled = true;
    regenBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Régénération IA...';
  }

  await generateMockupForLead(currentMockupLead.id);

  if (regenBtn) {
    regenBtn.disabled = false;
    regenBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Régénérer avec l\'IA';
  }
}

function switchMockupView(viewType) {
  const viewImg = document.getElementById('mockup-view-img');
  const viewLive = document.getElementById('mockup-view-live');
  const tabImg = document.getElementById('tab-mockup-img');
  const tabLive = document.getElementById('tab-mockup-live');

  if (viewType === 'live') {
    if (viewImg) viewImg.style.display = 'none';
    if (viewLive) viewLive.style.display = 'block';
    if (tabImg) tabImg.classList.remove('active');
    if (tabLive) tabLive.classList.add('active');
  } else {
    if (viewImg) viewImg.style.display = 'block';
    if (viewLive) viewLive.style.display = 'none';
    if (tabImg) tabImg.classList.add('active');
    if (tabLive) tabLive.classList.remove('active');
  }
}

function closeMockupModal() {
  const modal = document.getElementById('mockup-modal');
  const iframe = document.getElementById('mockup-modal-iframe');
  if (iframe) iframe.src = '';
  if (modal) modal.style.display = 'none';
}

// Open Outreach Modal (WhatsApp & Email Pitch)
async function openOutreachModal(leadId) {
  activeLeadOutreach = leadId;
  const modal = document.getElementById('outreach-modal');
  
  try {
    const res = await fetch(`/api/outreach/${leadId}`);
    const data = await res.json();
    if (!data.success) throw new Error(data.error || 'Erreur');

    currentOutreachData = data.messages;
    const lead = data.lead;

    // Fill fields with default lang (ar for Qatar/Gulf, else fr)
    const initialLang = (lead.default_lang || 'ar').startsWith('ar') ? 'ar' : 'fr';
    switchOutreachTab(initialLang);

    // Fill email input if available
    const emailTo = document.getElementById('outreach-email-to');
    if (emailTo) emailTo.value = lead.email || '';

    modal.style.display = 'flex';
  } catch (err) {
    showToast(`❌ Erreur: ${err.message}`);
  }
}

function closeOutreachModal() {
  const modal = document.getElementById('outreach-modal');
  if (modal) modal.style.display = 'none';
}

// Switch language tab in outreach modal
function switchOutreachTab(lang) {
  if (!currentOutreachData) return;

  // Update tab buttons
  document.querySelectorAll('.tabs-header .tab-btn').forEach(btn => {
    if (btn.getAttribute('data-lang') === lang) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  const langPack = currentOutreachData[lang] || currentOutreachData['primary'];

  // Fill WhatsApp
  const waBox = document.getElementById('outreach-wa-text');
  const waSendBtn = document.getElementById('outreach-wa-send-btn');
  if (waBox) waBox.value = langPack.whatsapp;
  if (waSendBtn) {
    if (langPack.wa_url) {
      waSendBtn.href = langPack.wa_url;
      waSendBtn.classList.remove('disabled');
    } else {
      waSendBtn.removeAttribute('href');
      waSendBtn.classList.add('disabled');
    }
  }

  // Fill Email
  const emailSubj = document.getElementById('outreach-email-subject');
  const emailBody = document.getElementById('outreach-email-body');
  if (emailSubj) emailSubj.value = langPack.email_subject;
  if (emailBody) emailBody.value = langPack.email_body;
}

// Copy WhatsApp text to clipboard
function copyWaText() {
  const text = document.getElementById('outreach-wa-text').value;
  navigator.clipboard.writeText(text).then(() => {
    showToast('📋 Message WhatsApp copié dans le presse-papier !');
  });
}

// Mark contacted on WhatsApp click
function markContactedWA() {
  if (activeLeadOutreach) {
    updateLeadStatus(activeLeadOutreach, 'Contacted (WA)');
  }
}

// Send cold email with mockup via SMTP
async function sendOutreachEmail() {
  if (!activeLeadOutreach) return;
  const toEmail = document.getElementById('outreach-email-to').value.trim();
  const subject = document.getElementById('outreach-email-subject').value.trim();
  const body = document.getElementById('outreach-email-body').value.trim();
  const sendBtn = document.getElementById('send-email-btn');

  if (!toEmail) {
    alert('Veuillez renseigner l\'adresse email du destinataire.');
    return;
  }

  sendBtn.disabled = true;
  sendBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Envoi en cours...';

  try {
    const res = await fetch('/api/send-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lead_id: activeLeadOutreach,
        to_email: toEmail,
        subject,
        body
      })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    showToast(`📧 ${data.message}`);
    updateLeadStatus(activeLeadOutreach, 'Contacted (Email)');
    closeOutreachModal();

  } catch (err) {
    showToast(`❌ ${err.message}`);
  } finally {
    sendBtn.disabled = false;
    sendBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Envoyer l\'Email maintenant';
  }
}

// Update lead outreach status in DB
async function updateLeadStatus(leadId, status) {
  try {
    const res = await fetch('/api/leads/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: leadId, outreach_status: status })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`✔ Statut mis à jour : ${status}`);
    }
  } catch (err) {
    console.error('Update error:', err);
  }
}

// Delete a lead
async function deleteLead(leadId) {
  if (!confirm('Supprimer ce prospect ?')) return;

  try {
    const res = await fetch(`/api/leads/${leadId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      const row = document.getElementById(`row-${leadId}`);
      if (row) row.remove();
      showToast('Prospect supprimé.');
      const countBadge = document.getElementById('table-count');
      if (countBadge) countBadge.textContent = data.count;
    }
  } catch (err) {
    showToast(`❌ Erreur: ${err.message}`);
  }
}
