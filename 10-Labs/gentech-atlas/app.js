/* GenTech Atlas — Meta Ray-Ban Display App */
(function() {
  'use strict';

  // ── Config ──
  var CONFIG = {
    appName: 'GenTech Atlas',
    storageKey: 'gentech_atlas',
    cityUrl: 'cities/tokyo.json',
  };

  // ── State ──
  var state = {
    currentScreen: 'home',
    screenHistory: [],
    city: null,
    stamps: 0,
    visited: {},
    foodTried: {},
    packed: 0,
    packingSlots: [],
    packingItems: [],
  };

  var screens = {};
  var cityData = null;

  // ── Screen Collection ──
  function collectScreens() {
    document.querySelectorAll('.screen').forEach(function(s) {
      if (s.id) screens[s.id] = s;
    });
  }

  // ── Navigation ──
  function navigateTo(screenId, options) {
    options = options || {};
    var addToHistory = options.addToHistory !== false;
    if (addToHistory && state.currentScreen) {
      state.screenHistory.push(state.currentScreen);
    }
    Object.keys(screens).forEach(function(id) {
      screens[id].classList.add('hidden');
    });
    if (screens[screenId]) {
      screens[screenId].classList.remove('hidden');
      state.currentScreen = screenId;
      onScreenEnter(screenId);
      focusFirst(screens[screenId]);
    }
  }

  function navigateBack() {
    if (state.screenHistory.length > 0) {
      navigateTo(state.screenHistory.pop(), { addToHistory: false });
    }
  }

  // ── Focus Management (D-pad) ──
  function focusFirst(container) {
    var el = container.querySelector('.focusable:not([disabled]):not(.hidden)');
    if (el) el.focus();
  }

  function moveFocus(direction) {
    var container = screens[state.currentScreen];
    if (!container) return;
    var focusables = Array.from(
      container.querySelectorAll('.focusable:not([disabled]):not(.hidden)')
    );
    if (focusables.length === 0) return;
    var current = document.activeElement;
    var idx = focusables.indexOf(current);
    if (idx === -1) { focusFirst(container); return; }
    var nextIdx;
    if (direction === 'up' || direction === 'left') {
      nextIdx = idx > 0 ? idx - 1 : focusables.length - 1;
    } else {
      nextIdx = idx < focusables.length - 1 ? idx + 1 : 0;
    }
    focusables[nextIdx].focus();
    var scrollParent = focusables[nextIdx].closest('.content');
    if (scrollParent) {
      focusables[nextIdx].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }

  // ── Toast ──
  function showToast(message, type) {
    var toast = document.getElementById('toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast';
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = 'toast' + (type ? ' ' + type : '');
    toast.offsetHeight;
    toast.classList.add('visible');
    setTimeout(function() { toast.classList.remove('visible'); }, 2500);
  }

  // ── Load City Data ──
  function loadCity() {
    var content = document.querySelector('#home .content');
    content.innerHTML = '<div class="loading-container"><div class="loading-spinner"></div><div class="loading-text">Loading Tokyo...</div></div>';

    fetch(CONFIG.cityUrl)
      .then(function(r) { return r.json(); })
      .then(function(data) {
        cityData = data;
        state.city = data.city;
        state.visited = {};
        state.foodTried = {};
        state.packed = 0;
        state.packingSlots = new Array(12).fill(null);
        state.packingItems = JSON.parse(JSON.stringify(data.packing));
        state.stamps = 0;
        renderHome();
      })
      .catch(function(err) {
        content.innerHTML = '<div class="loading-container"><div class="error-icon">⚠️</div><div class="loading-text">Failed to load: ' + err.message + '</div></div>';
      });
  }

  // ── Render Home ──
  function renderHome() {
    var content = document.querySelector('#home .content');
    content.innerHTML =
      '<div class="card focusable" data-action="explore" tabindex="0">' +
        '<div class="card-title">🗺️ Explore Tokyo</div>' +
        '<div class="card-subtitle">' + cityData.districts.length + ' districts to discover</div>' +
      '</div>' +
      '<div class="card focusable" data-action="food" tabindex="0">' +
        '<div class="card-title">🍜 Food Finder</div>' +
        '<div class="card-subtitle">' + cityData.food.length + ' must-try dishes</div>' +
      '</div>' +
      '<div class="card focusable" data-action="phrases" tabindex="0">' +
        '<div class="card-title">💬 Phrase Helper</div>' +
        '<div class="card-subtitle">' + cityData.phrases.length + ' essential phrases</div>' +
      '</div>' +
      '<div class="card focusable" data-action="packing" tabindex="0">' +
        '<div class="card-title">🎒 Packing List</div>' +
        '<div class="card-subtitle">' + cityData.packing.length + ' items to pack</div>' +
      '</div>';
  }

  // ── Explorer ──
  function renderExplorer() {
    var list = document.getElementById('district-list');
    list.innerHTML = '';
    cityData.districts.forEach(function(d, i) {
      var visited = state.visited[d.id];
      var item = document.createElement('div');
      item.className = 'list-item focusable';
      item.tabIndex = 0;
      item.dataset.index = i;
      item.innerHTML =
        '<span class="list-item-icon">' + d.emoji + '</span>' +
        '<div class="list-item-content">' +
          '<div class="list-item-title">' + d.name + '</div>' +
          '<div class="list-item-meta">' + d.budget + '</div>' +
        '</div>' +
        '<span class="list-item-badge ' + (visited ? 'badge-visited' : 'badge-new') + '">' + (visited ? '✅' : 'NEW') + '</span>';
      item.addEventListener('click', function() { showDistrict(i); });
      item.addEventListener('focus', function() { showDistrict(i); });
      list.appendChild(item);
    });
    document.getElementById('stamps-count').textContent = state.stamps + '/' + cityData.districts.length;
  }

  function showDistrict(i) {
    var d = cityData.districts[i];
    if (!state.visited[d.id]) {
      state.visited[d.id] = true;
      state.stamps++;
      document.getElementById('stamps-count').textContent = state.stamps + '/' + cityData.districts.length;
      renderExplorer();
    }
    var detail = document.getElementById('district-detail');
    detail.innerHTML =
      '<div class="card-title">' + d.emoji + ' ' + d.name + '</div>' +
      '<div class="card-detail">' + d.fact + '</div>' +
      '<div class="card-budget">💰 ' + d.budget + '</div>' +
      '<div class="card-tips">💡 ' + d.tips + '</div>' +
      (state.visited[d.id] ? '<div class="card-stamp">✅ Stamp collected!</div>' : '');
  }

  // ── Food ──
  function renderFood() {
    var list = document.getElementById('food-list');
    list.innerHTML = '';
    cityData.food.forEach(function(f, i) {
      var tried = state.foodTried[i];
      var item = document.createElement('div');
      item.className = 'list-item focusable';
      item.tabIndex = 0;
      item.dataset.index = i;
      item.innerHTML =
        '<span class="list-item-icon">' + f.emoji + '</span>' +
        '<div class="list-item-content">' +
          '<div class="list-item-title">' + f.name + '</div>' +
          '<div class="list-item-meta">' + f.price + '</div>' +
        '</div>' +
        '<span class="list-item-badge ' + (tried ? 'badge-visited' : 'badge-new') + '">' + (tried ? '✅' : 'TRY') + '</span>';
      item.addEventListener('click', function() { showFood(i); });
      item.addEventListener('focus', function() { showFood(i); });
      list.appendChild(item);
    });
    var triedCount = Object.keys(state.foodTried).length;
    document.getElementById('food-count').textContent = triedCount + '/' + cityData.food.length;
  }

  function showFood(i) {
    var f = cityData.food[i];
    state.foodTried[i] = true;
    var triedCount = Object.keys(state.foodTried).length;
    document.getElementById('food-count').textContent = triedCount + '/' + cityData.food.length;
    renderFood();
    var detail = document.getElementById('food-detail');
    detail.innerHTML =
      '<div class="card-title">' + f.emoji + ' ' + f.name + '</div>' +
      '<div class="card-detail">' + f.description + '</div>' +
      '<div class="card-budget">💰 ' + f.price + '</div>' +
      '<div class="card-stamp">✅ Added to your food list!</div>';
  }

  // ── Phrases ──
  function renderPhrases() {
    var list = document.getElementById('phrase-list');
    list.innerHTML = '';
    cityData.phrases.forEach(function(p, i) {
      var item = document.createElement('div');
      item.className = 'list-item focusable';
      item.tabIndex = 0;
      item.dataset.index = i;
      item.innerHTML =
        '<span class="list-item-icon">💬</span>' +
        '<div class="list-item-content">' +
          '<div class="list-item-title">' + p.situation + '</div>' +
        '</div>';
      item.addEventListener('click', function() { showPhrase(i); });
      item.addEventListener('focus', function() { showPhrase(i); });
      list.appendChild(item);
    });
  }

  function showPhrase(i) {
    var p = cityData.phrases[i];
    var detail = document.getElementById('phrase-detail');
    detail.innerHTML =
      '<div class="card-title">' + p.situation + '</div>' +
      '<div class="card-phrase">' + p.phrase + '</div>' +
      '<div class="card-detail">' + p.meaning + '</div>';
  }

  // ── Packing ──
  function renderPacking() {
    state.packed = 0;
    state.packingSlots = new Array(12).fill(null);
    state.packingItems = JSON.parse(JSON.stringify(cityData.packing));

    var grid = document.getElementById('packing-grid');
    grid.innerHTML = '';
    state.packingItems.forEach(function(item, i) {
      var div = document.createElement('div');
      div.className = 'grid-item focusable';
      div.tabIndex = 0;
      div.dataset.index = i;
      div.innerHTML = '<span class="emoji">' + item.emoji + '</span><span class="label">' + item.name + '</span>';
      div.addEventListener('click', function() { packItem(i); });
      div.addEventListener('focus', function() { packItem(i); });
      grid.appendChild(div);
    });
    document.getElementById('packed-count').textContent = '0/' + state.packingItems.length;
    document.getElementById('packing-progress').style.width = '0%';
  }

  function packItem(index) {
    var item = state.packingItems[index];
    if (!item || item.packed) return;
    item.packed = true;
    state.packed++;

    var items = document.querySelectorAll('.grid-item');
    if (items[index]) items[index].classList.add('packed');

    document.getElementById('packed-count').textContent = state.packed + '/' + state.packingItems.length;
    document.getElementById('packing-progress').style.width = (state.packed / state.packingItems.length * 100) + '%';

    if (state.packed >= state.packingItems.length) {
      showToast('🧳 All packed for Tokyo! 🇯🇵', 'success');
    }
  }

  // ── Screen Enter ──
  function onScreenEnter(screenId) {
    if (screenId === 'explore' && cityData) renderExplorer();
    else if (screenId === 'food' && cityData) renderFood();
    else if (screenId === 'phrases' && cityData) renderPhrases();
    else if (screenId === 'packing' && cityData) renderPacking();
  }

  // ── Action Handler ──
  function handleAction(action, element) {
    switch (action) {
      case 'back': navigateBack(); break;
      case 'explore': navigateTo('explore'); break;
      case 'food': navigateTo('food'); break;
      case 'phrases': navigateTo('phrases'); break;
      case 'packing': navigateTo('packing'); break;
      default: break;
    }
  }

  // ── Events ──
  function setupEvents() {
    document.addEventListener('click', function(e) {
      var actionEl = e.target.closest('[data-action]');
      if (actionEl) handleAction(actionEl.dataset.action, actionEl);
    });

    document.addEventListener('keydown', function(e) {
      var isInput = document.activeElement &&
        (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA');
      if (isInput && !['Escape', 'Enter'].includes(e.key)) return;

      switch (e.key) {
        case 'ArrowUp': moveFocus('up'); e.preventDefault(); break;
        case 'ArrowDown': moveFocus('down'); e.preventDefault(); break;
        case 'ArrowLeft': moveFocus('left'); e.preventDefault(); break;
        case 'ArrowRight': moveFocus('right'); e.preventDefault(); break;
        case 'Enter':
          if (document.activeElement && document.activeElement.classList.contains('focusable')) {
            document.activeElement.click();
          }
          e.preventDefault();
          break;
        case 'Escape': navigateBack(); e.preventDefault(); break;
      }
    });
  }

  // ── Init ──
  function init() {
    collectScreens();
    setupEvents();
    loadCity();
    setTimeout(function() {
      navigateTo('home', { addToHistory: false });
    }, 100);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
