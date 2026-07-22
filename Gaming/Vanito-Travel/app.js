/* === Vanito's Travel Companion — Japan Explorer === */
(function() {
  'use strict';

  const CITIES = ['tokyo', 'osaka'];
  let CITY_DATA = null;
  let currentCity = 'tokyo';

  const state = {
    currentScreen: 'title',
    explorer: { stamps: 0, locations: [] },
    food: { tried: new Set() },
    packing: { packed: 0, slots: new Array(12).fill(null), items: [] }
  };

  // ── Load city data ──
  async function loadCity(city) {
    currentCity = city || currentCity;
    try {
      const resp = await fetch('cities/' + currentCity + '.json');
      CITY_DATA = await resp.json();
      state.explorer.locations = JSON.parse(JSON.stringify(CITY_DATA.districts));
      state.explorer.stamps = 0;
      state.food.tried = new Set();
      state.packing.items = JSON.parse(JSON.stringify(CITY_DATA.packing));
      state.packing.packed = 0;
      state.packing.slots = new Array(12).fill(null);
      document.getElementById('city-name').textContent = CITY_DATA.emoji + ' ' + CITY_DATA.city;
      renderExplorer();
      renderFood();
      renderPhrases();
      renderPacking();
      showScreen('title');
    } catch (e) {
      document.getElementById('screen-title').innerHTML =
        '<div class="title-content">' +
        '<div class="logo">🗼</div>' +
        '<h1>Vanito\'s Travel Companion</h1>' +
        '<p class="subtitle" style="color:#e8652a">⚠️ Could not load ' + currentCity + ' data</p>' +
        '<p style="color:#6a5a4a;font-size:12px">' + e.message + '</p></div>';
    }
  }

  // ── Navigation ──
  function showScreen(id) {
    document.querySelectorAll('.screen').forEach(function(s) { s.classList.remove('active'); });
    var el = document.getElementById('screen-' + id);
    if (el) el.classList.add('active');
    state.currentScreen = id;
  }

  // ── Explorer ──
  function renderExplorer() {
    if (!CITY_DATA) return;
    var grid = document.getElementById('map-grid');
    grid.innerHTML = '';
    state.explorer.locations.forEach(function(loc) {
      var div = document.createElement('div');
      div.className = 'map-location' + (loc.visited ? ' visited' : '');
      div.innerHTML = '<span class="emoji">' + loc.emoji + '</span><span class="name">' + loc.name + '</span>' + (loc.visited ? '<span class="stamp">✅</span>' : '');
      div.addEventListener('click', function() { visitLocation(loc.id); });
      grid.appendChild(div);
    });
    document.getElementById('stamps-count').textContent = state.explorer.stamps;
  }

  function visitLocation(id) {
    var loc = state.explorer.locations.find(function(l) { return l.id === id; });
    if (!loc) return;
    if (!loc.visited) {
      loc.visited = true;
      state.explorer.stamps++;
      document.getElementById('stamps-count').textContent = state.explorer.stamps;
    }
    var info = document.getElementById('location-info');
    info.innerHTML =
      '<div class="info-title">' + loc.emoji + ' ' + loc.name + '</div>' +
      '<div class="info-fact">' + loc.fact + '</div>' +
      '<div class="info-budget">💰 ' + loc.budget + '</div>' +
      '<div class="info-tips">💡 ' + loc.tips + '</div>' +
      (loc.visited ? '<div class="info-stamp">✅ Stamp collected!</div>' : '');
    info.classList.remove('fade-in');
    void info.offsetWidth;
    info.classList.add('fade-in');
    renderExplorer();
  }

  // ── Food Finder ──
  function renderFood() {
    if (!CITY_DATA) return;
    var list = document.getElementById('food-list');
    list.innerHTML = '';
    CITY_DATA.food.forEach(function(item, i) {
      var div = document.createElement('div');
      div.className = 'food-card';
      div.innerHTML = '<span class="food-emoji">' + item.emoji + '</span><span class="food-name">' + item.name + '</span><span class="food-price">' + item.price + '</span>';
      div.addEventListener('click', function() { showFoodDetail(i); });
      list.appendChild(div);
    });
  }

  function showFoodDetail(i) {
    var item = CITY_DATA.food[i];
    state.food.tried.add(i);
    document.getElementById('food-count').textContent = state.food.tried.size;
    var detail = document.getElementById('food-detail');
    detail.innerHTML =
      '<div class="info-title">' + item.emoji + ' ' + item.name + '</div>' +
      '<div class="info-fact">' + item.description + '</div>' +
      '<div class="info-budget">💰 ' + item.price + '</div>' +
      '<div class="info-stamp">✅ Added to your food list!</div>';
    detail.classList.remove('fade-in');
    void detail.offsetWidth;
    detail.classList.add('fade-in');
  }

  // ── Phrase Helper ──
  function renderPhrases() {
    if (!CITY_DATA) return;
    var grid = document.getElementById('phrase-grid');
    grid.innerHTML = '';
    CITY_DATA.phrases.forEach(function(p, i) {
      var div = document.createElement('div');
      div.className = 'phrase-btn';
      div.textContent = p.situation;
      div.addEventListener('click', function() { showPhrase(i); });
      grid.appendChild(div);
    });
  }

  function showPhrase(i) {
    var p = CITY_DATA.phrases[i];
    var display = document.getElementById('phrase-display');
    display.innerHTML =
      '<div class="info-title">' + p.situation + '</div>' +
      '<div class="phrase-jp">' + p.phrase + '</div>' +
      '<div class="info-fact">' + p.meaning + '</div>';
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

    var grid = document.getElementById('suitcase-grid');
    grid.innerHTML = '';
    for (var i = 0; i < 12; i++) {
      var slot = document.createElement('div');
      slot.className = 'suitcase-slot';
      slot.dataset.index = i;
      grid.appendChild(slot);
    }

    var pool = document.getElementById('items-pool');
    pool.innerHTML = '';
    state.packing.items.forEach(function(item, i) {
      var div = document.createElement('div');
      div.className = 'pool-item';
      div.dataset.index = i;
      div.innerHTML = '<span class="emoji">' + item.emoji + '</span>' + item.name;
      div.addEventListener('click', function() { packItem(i); });
      pool.appendChild(div);
    });
    document.getElementById('packed-count').textContent = '0';
  }

  function packItem(index) {
    var item = state.packing.items[index];
    if (!item || item.placed) return;
    var emptyIdx = state.packing.slots.indexOf(null);
    if (emptyIdx === -1) return;

    state.packing.slots[emptyIdx] = item;
    item.placed = true;
    state.packing.packed++;

    var slots = document.querySelectorAll('.suitcase-slot');
    if (slots[emptyIdx]) {
      slots[emptyIdx].textContent = item.emoji;
      slots[emptyIdx].classList.add('filled');
    }
    var poolItems = document.querySelectorAll('.pool-item');
    if (poolItems[index]) poolItems[index].classList.add('placed');
    document.getElementById('packed-count').textContent = state.packing.packed;

    if (state.packing.packed >= 12) {
      setTimeout(function() {
        document.getElementById('packing-area').innerHTML =
          '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:12px">' +
          '<div style="font-size:64px">🧳</div>' +
          '<div style="font-size:20px;color:#d4a017;font-weight:600">All Packed!</div>' +
          '<div style="font-size:13px;color:#c0b0a0">Ready for ' + CITY_DATA.city + '! 🇯🇵</div>' +
          '<button class="btn btn-primary" onclick="location.reload()" style="margin-top:12px">Start Over</button></div>';
      }, 500);
    }
  }

  // ── Swipe Detection ──
  var touchStartX = 0;
  document.addEventListener('touchstart', function(e) { touchStartX = e.touches[0].clientX; }, { passive: true });
  document.addEventListener('touchend', function(e) {
    var dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 50) {
      var screens = ['title', 'explorer', 'food', 'phrases', 'packing'];
      var idx = screens.indexOf(state.currentScreen);
      if (dx < 0 && idx < screens.length - 1) showScreen(screens[idx + 1]);
      else if (dx > 0 && idx > 0) showScreen(screens[idx - 1]);
    }
  }, { passive: true });

  // ── Event Binding ──
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('[data-screen]');
    if (btn) showScreen(btn.dataset.screen);
    var cityBtn = e.target.closest('[data-city]');
    if (cityBtn) loadCity(cityBtn.dataset.city);
  });
  document.querySelectorAll('.btn[data-mode]').forEach(function(btn) {
    btn.addEventListener('click', function() { showScreen(btn.dataset.mode); });
  });

  // Keyboard nav
  document.addEventListener('keydown', function(e) {
    var screens = ['title', 'explorer', 'food', 'phrases', 'packing'];
    var idx = screens.indexOf(state.currentScreen);
    if (e.key === 'ArrowLeft' && idx > 0) showScreen(screens[idx - 1]);
    if (e.key === 'ArrowRight' && idx < screens.length - 1) showScreen(screens[idx + 1]);
  });

  // ── Init ──
  loadCity('tokyo');
})();
