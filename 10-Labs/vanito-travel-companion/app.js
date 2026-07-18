/* === Vanito's Travel Companion — Tokyo Explorer === */
(function() {
  'use strict';

  let CITY_DATA = null;
  const state = {
    currentScreen: 'title',
    explorer: { stamps: 0, locations: [] },
    food: { tried: new Set() },
    packing: { packed: 0, slots: new Array(12).fill(null), items: [] }
  };

  // ── Load city data ──
  async function loadCity() {
    try {
      const resp = await fetch('cities/tokyo.json');
      CITY_DATA = await resp.json();
      state.explorer.locations = JSON.parse(JSON.stringify(CITY_DATA.districts));
      state.packing.items = JSON.parse(JSON.stringify(CITY_DATA.packing));
      renderExplorer();
      renderFood();
      renderPhrases();
      renderPacking();
    } catch (e) {
      document.getElementById('screen-title').innerHTML = `
        <div class="title-content">
          <div class="logo">🗼</div>
          <h1>Vanito's Travel Companion</h1>
          <p class="subtitle" style="color:#e8652a">⚠️ Could not load Tokyo data</p>
          <p style="color:#6a5a4a;font-size:12px">${e.message}</p>
        </div>`;
    }
  }

  // ── Navigation ──
  function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const el = document.getElementById('screen-' + id);
    if (el) el.classList.add('active');
    state.currentScreen = id;
  }

  // ── Explorer ──
  function renderExplorer() {
    if (!CITY_DATA) return;
    const grid = document.getElementById('map-grid');
    grid.innerHTML = '';
    state.explorer.locations.forEach(loc => {
      const div = document.createElement('div');
      div.className = 'map-location' + (loc.visited ? ' visited' : '');
      div.innerHTML = `<span class="emoji">${loc.emoji}</span><span class="name">${loc.name}</span>${loc.visited ? '<span class="stamp">✅</span>' : ''}`;
      div.addEventListener('click', () => visitLocation(loc.id));
      grid.appendChild(div);
    });
    document.getElementById('stamps-count').textContent = state.explorer.stamps;
  }

  function visitLocation(id) {
    const loc = state.explorer.locations.find(l => l.id === id);
    if (!loc) return;
    if (!loc.visited) {
      loc.visited = true;
      state.explorer.stamps++;
      document.getElementById('stamps-count').textContent = state.explorer.stamps;
    }
    const info = document.getElementById('location-info');
    info.innerHTML = `
      <div class="info-title">${loc.emoji} ${loc.name}</div>
      <div class="info-fact">${loc.fact}</div>
      <div class="info-budget">💰 ${loc.budget}</div>
      <div class="info-tips">💡 ${loc.tips}</div>
      ${loc.visited ? '<div class="info-stamp">✅ Stamp collected!</div>' : ''}
    `;
    info.classList.remove('fade-in');
    void info.offsetWidth;
    info.classList.add('fade-in');
    renderExplorer();
  }

  // ── Food Finder ──
  function renderFood() {
    if (!CITY_DATA) return;
    const list = document.getElementById('food-list');
    list.innerHTML = '';
    CITY_DATA.food.forEach((item, i) => {
      const div = document.createElement('div');
      div.className = 'food-card';
      div.innerHTML = `
        <span class="food-emoji">${item.emoji}</span>
        <span class="food-name">${item.name}</span>
        <span class="food-price">${item.price}</span>
      `;
      div.addEventListener('click', () => showFoodDetail(i));
      list.appendChild(div);
    });
  }

  function showFoodDetail(i) {
    const item = CITY_DATA.food[i];
    state.food.tried.add(i);
    document.getElementById('food-count').textContent = state.food.tried.size;
    const detail = document.getElementById('food-detail');
    detail.innerHTML = `
      <div class="info-title">${item.emoji} ${item.name}</div>
      <div class="info-fact">${item.description}</div>
      <div class="info-budget">💰 ${item.price}</div>
      <div class="info-stamp">✅ Added to your food list!</div>
    `;
    detail.classList.remove('fade-in');
    void detail.offsetWidth;
    detail.classList.add('fade-in');
  }

  // ── Phrase Helper ──
  function renderPhrases() {
    if (!CITY_DATA) return;
    const grid = document.getElementById('phrase-grid');
    grid.innerHTML = '';
    CITY_DATA.phrases.forEach((p, i) => {
      const div = document.createElement('div');
      div.className = 'phrase-btn';
      div.textContent = p.situation;
      div.addEventListener('click', () => showPhrase(i));
      grid.appendChild(div);
    });
  }

  function showPhrase(i) {
    const p = CITY_DATA.phrases[i];
    const display = document.getElementById('phrase-display');
    display.innerHTML = `
      <div class="info-title">${p.situation}</div>
      <div class="phrase-jp">${p.phrase}</div>
      <div class="info-fact">${p.meaning}</div>
    `;
    display.classList.remove('fade-in');
    void display.offsetWidth;
    display.classList.add('fade-in');
  }

  // ── Packing List ──
  function renderPacking() {
    if (!CITY_DATA) return;
    state.packing.packed = 0;
    state.packing.slots = new Array(12).fill(null);
    state.packing.items = JSON.parse(JSON.stringify(CITY_DATA.packing));

    const grid = document.getElementById('suitcase-grid');
    grid.innerHTML = '';
    for (let i = 0; i < 12; i++) {
      const slot = document.createElement('div');
      slot.className = 'suitcase-slot';
      slot.dataset.index = i;
      grid.appendChild(slot);
    }

    const pool = document.getElementById('items-pool');
    pool.innerHTML = '';
    state.packing.items.forEach((item, i) => {
      const div = document.createElement('div');
      div.className = 'pool-item';
      div.dataset.index = i;
      div.innerHTML = `<span class="emoji">${item.emoji}</span>${item.name}`;
      div.addEventListener('click', () => packItem(i));
      pool.appendChild(div);
    });
    document.getElementById('packed-count').textContent = '0';
  }

  function packItem(index) {
    const item = state.packing.items[index];
    if (!item || item.placed) return;
    const emptyIdx = state.packing.slots.indexOf(null);
    if (emptyIdx === -1) return;

    state.packing.slots[emptyIdx] = item;
    item.placed = true;
    state.packing.packed++;

    const slots = document.querySelectorAll('.suitcase-slot');
    if (slots[emptyIdx]) {
      slots[emptyIdx].textContent = item.emoji;
      slots[emptyIdx].classList.add('filled');
    }
    const poolItems = document.querySelectorAll('.pool-item');
    if (poolItems[index]) poolItems[index].classList.add('placed');
    document.getElementById('packed-count').textContent = state.packing.packed;

    if (state.packing.packed >= 12) {
      setTimeout(() => {
        document.getElementById('packing-area').innerHTML = `
          <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:12px">
            <div style="font-size:64px">🧳</div>
            <div style="font-size:20px;color:#d4a017;font-weight:600">All Packed!</div>
            <div style="font-size:13px;color:#c0b0a0">Ready for Tokyo! 🇯🇵</div>
            <button class="btn btn-primary" onclick="location.reload()" style="margin-top:12px">Start Over</button>
          </div>`;
      }, 500);
    }
  }

  // ── Swipe Detection ──
  let touchStartX = 0;
  document.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
  document.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 50) {
      const screens = ['title', 'explorer', 'food', 'phrases', 'packing'];
      const idx = screens.indexOf(state.currentScreen);
      if (dx < 0 && idx < screens.length - 1) showScreen(screens[idx + 1]);
      else if (dx > 0 && idx > 0) showScreen(screens[idx - 1]);
    }
  }, { passive: true });

  // ── Event Binding ──
  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-screen]');
    if (btn) showScreen(btn.dataset.screen);
  });
  document.querySelectorAll('.btn[data-mode]').forEach(btn => {
    btn.addEventListener('click', () => showScreen(btn.dataset.mode));
  });

  // Keyboard nav
  document.addEventListener('keydown', e => {
    const screens = ['title', 'explorer', 'food', 'phrases', 'packing'];
    const idx = screens.indexOf(state.currentScreen);
    if (e.key === 'ArrowLeft' && idx > 0) showScreen(screens[idx - 1]);
    if (e.key === 'ArrowRight' && idx < screens.length - 1) showScreen(screens[idx + 1]);
  });

  // ── Init ──
  loadCity();
})();
