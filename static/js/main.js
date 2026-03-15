document.addEventListener('DOMContentLoaded', () => {
    initNav();
    initMobile();
    initReveal();
    initMenuTabs();
    initQuotes();
    initForms();
    initLang();
});

/* ── Nav scroll ──────────────────────────────────────────────── */
function initNav() {
    const nav = document.querySelector('.nav');
    if (!nav) return;
    const check = () => nav.classList.toggle('scrolled', window.scrollY > 50);
    window.addEventListener('scroll', check, { passive: true });
    check();
}

/* ── Mobile menu ─────────────────────────────────────────────── */
function initMobile() {
    const btn = document.querySelector('.hamburger');
    const menu = document.querySelector('.mobile-menu');
    if (!btn || !menu) return;

    btn.addEventListener('click', () => {
        btn.classList.toggle('active');
        menu.classList.toggle('open');
        document.body.style.overflow = menu.classList.contains('open') ? 'hidden' : '';
    });
    menu.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            btn.classList.remove('active');
            menu.classList.remove('open');
            document.body.style.overflow = '';
        });
    });
}

/* ── Scroll reveal ───────────────────────────────────────────── */
function initReveal() {
    const els = document.querySelectorAll('.reveal');
    if (!els.length) return;
    const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -30px 0px' });
    els.forEach(el => obs.observe(el));
}

/* ── Menu tabs ───────────────────────────────────────────────── */
function initMenuTabs() {
    const tabs = document.querySelectorAll('.menu-tab');
    const cats = document.querySelectorAll('.menu-cat');
    if (!tabs.length) return;
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const t = tab.dataset.cat;
            tabs.forEach(x => x.classList.remove('active'));
            tab.classList.add('active');
            cats.forEach(c => c.classList.toggle('active', c.dataset.cat === t));
        });
    });
}

/* ── Testimonial quotes ──────────────────────────────────────── */
function initQuotes() {
    const items = document.querySelectorAll('.quote-item');
    const dots = document.querySelectorAll('.dots button');
    if (!items.length) return;
    let cur = 0, iv;
    function show(i) {
        items.forEach(x => x.classList.remove('active'));
        dots.forEach(x => x.classList.remove('active'));
        items[i].classList.add('active');
        if (dots[i]) dots[i].classList.add('active');
        cur = i;
    }
    function next() { show((cur + 1) % items.length); }
    dots.forEach((d, i) => d.addEventListener('click', () => { show(i); clearInterval(iv); iv = setInterval(next, 5000); }));
    iv = setInterval(next, 5000);
}

/* ── Forms AJAX ──────────────────────────────────────────────── */
function initForms() {
    bind('reservation-form', '/rezervacija');
    bind('contact-form', '/kontakt');
}
function bind(id, url) {
    const form = document.getElementById(id);
    if (!form) return;
    form.addEventListener('submit', async e => {
        e.preventDefault();
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(Object.fromEntries(new FormData(form)))
            });
            const j = await res.json();
            showToast(j.message, 'success');
            form.reset();
        } catch { showToast('Greška. Pokušajte ponovo.', 'error'); }
    });
}

function showToast(msg, type = 'success') {
    const old = document.querySelector('.toast');
    if (old) old.remove();
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.textContent = msg;
    document.body.appendChild(t);
    requestAnimationFrame(() => t.classList.add('show'));
    setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 400); }, 3500);
}

/* ── Language Toggle ─────────────────────────────────────────── */
function initLang() {
    const saved = localStorage.getItem('tc-lang') || 'sr';
    setLang(saved);

    document.querySelectorAll('.lang-toggle button').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.dataset.lang;
            localStorage.setItem('tc-lang', lang);
            setLang(lang);
        });
    });
}

function setLang(lang) {
    document.querySelectorAll('.lang-toggle button').forEach(b => {
        b.classList.toggle('active', b.dataset.lang === lang);
    });
    document.querySelectorAll('[data-sr]').forEach(el => {
        el.textContent = lang === 'sr' ? el.dataset.sr : el.dataset.en;
    });
    document.querySelectorAll('[data-sr-placeholder]').forEach(el => {
        el.placeholder = lang === 'sr' ? el.dataset.srPlaceholder : el.dataset.enPlaceholder;
    });
}

/* ── Admin functions (kept global) ───────────────────────────── */
function openModal(id) { const m = document.getElementById(id); if (m) m.classList.add('show'); }
function closeModal(id) { const m = document.getElementById(id); if (m) m.classList.remove('show'); }
document.addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('show'); });

async function saveMenuItem() {
    const f = document.getElementById('menu-item-form');
    if (!f) return;
    const itemId = f.dataset.itemId;
    const data = {
        category_id: f.querySelector('[name="category_id"]').value,
        name: f.querySelector('[name="name"]').value,
        description: f.querySelector('[name="description"]').value,
        price: parseFloat(f.querySelector('[name="price"]').value),
        available: f.querySelector('[name="available"]').checked,
        sort_order: parseInt(f.querySelector('[name="sort_order"]').value) || 0
    };
    const url = itemId ? `/admin/api/menu/${itemId}` : '/admin/api/menu';
    try {
        const r = await fetch(url, { method: itemId ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        const j = await r.json();
        if (j.success) { showToast(itemId ? 'Ažurirano!' : 'Dodato!', 'success'); setTimeout(() => location.reload(), 700); }
    } catch { showToast('Greška.', 'error'); }
}

function editMenuItem(id, catId, name, desc, price, available, sortOrder) {
    const f = document.getElementById('menu-item-form');
    if (!f) return;
    f.dataset.itemId = id;
    f.querySelector('[name="category_id"]').value = catId;
    f.querySelector('[name="name"]').value = name;
    f.querySelector('[name="description"]').value = desc;
    f.querySelector('[name="price"]').value = price;
    f.querySelector('[name="available"]').checked = available;
    f.querySelector('[name="sort_order"]').value = sortOrder;
    document.querySelector('#menu-modal h3').textContent = 'Izmeni stavku';
    openModal('menu-modal');
}

function openAddMenuItem(catId) {
    const f = document.getElementById('menu-item-form');
    if (!f) return;
    f.dataset.itemId = '';
    f.reset();
    f.querySelector('[name="category_id"]').value = catId;
    f.querySelector('[name="available"]').checked = true;
    document.querySelector('#menu-modal h3').textContent = 'Dodaj stavku';
    openModal('menu-modal');
}

async function deleteMenuItem(id) {
    if (!confirm('Obrisati stavku?')) return;
    try { const r = await fetch(`/admin/api/menu/${id}`, { method: 'DELETE' }); const j = await r.json(); if (j.success) { showToast('Obrisano.', 'success'); setTimeout(() => location.reload(), 700); } } catch { showToast('Greška.', 'error'); }
}

async function addCategory() {
    const name = prompt('Naziv kategorije:');
    if (!name) return;
    try { const r = await fetch('/admin/api/category', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) }); const j = await r.json(); if (j.success) { showToast('Dodato!', 'success'); setTimeout(() => location.reload(), 700); } } catch { showToast('Greška.', 'error'); }
}

async function deleteCategory(id) {
    if (!confirm('Obrisati kategoriju i sve stavke?')) return;
    try { const r = await fetch(`/admin/api/category/${id}`, { method: 'DELETE' }); const j = await r.json(); if (j.success) { showToast('Obrisano.', 'success'); setTimeout(() => location.reload(), 700); } } catch { showToast('Greška.', 'error'); }
}

async function updateReservation(id, status) {
    try { const r = await fetch(`/admin/api/reservation/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }) }); const j = await r.json(); if (j.success) { showToast(`Status: ${status}`, 'success'); setTimeout(() => location.reload(), 700); } } catch { showToast('Greška.', 'error'); }
}

async function deleteReservation(id) {
    if (!confirm('Obrisati rezervaciju?')) return;
    try { const r = await fetch(`/admin/api/reservation/${id}`, { method: 'DELETE' }); const j = await r.json(); if (j.success) { showToast('Obrisano.', 'success'); setTimeout(() => location.reload(), 700); } } catch { showToast('Greška.', 'error'); }
}
