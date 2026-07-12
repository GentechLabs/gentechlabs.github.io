import { CLASSES, CLASS_ICONS, CLASS_COLORS } from './classes.js';
import { GameState } from './game-state.js';
import { GestureController } from './gesture-controller.js';
import { TouchController } from './touch-controller.js';
import { CHARACTERS } from './characters.js';

class MetaFighterApp {
  constructor() {
    this.gameState = new GameState();
    this.gestureController = new GestureController((action) => this.handleAction(action));
    this.touchController = new TouchController((action) => this.handleAction(action));
    this.selectedMemberIndex = 0;
    this.currentTab = 'abilities';

    this.ui = {
      level: document.getElementById('level'),
      turnIndicator: document.getElementById('turn-indicator'),
      combatLog: document.getElementById('combat-log'),
      enemyName: document.getElementById('enemy-name'),
      attackingCharacter: document.getElementById('attacking-character'),
      effectContainer: document.getElementById('effect-container'),
      abilitiesContainer: document.getElementById('abilities-container'),
      itemsContainer: document.getElementById('items-container'),
      abilitiesPanel: document.getElementById('abilities-panel'),
      itemsPanel: document.getElementById('items-panel'),
      abilitiesTab: document.getElementById('abilities-tab'),
      itemsTab: document.getElementById('items-tab'),
      partyContainer: document.getElementById('party-container'),
      gameOver: document.getElementById('game-over'),
      gameWon: document.getElementById('game-won'),
      restartBtnOver: document.getElementById('restart-btn-over'),
      restartBtnWon: document.getElementById('restart-btn-won'),
      heroSlots: [
        document.getElementById('hero-slot-1'),
        document.getElementById('hero-slot-2'),
        document.getElementById('hero-slot-3')
      ],
      heroSlotChars: [
        document.getElementById('hero-1'),
        document.getElementById('hero-2'),
        document.getElementById('hero-3')
      ],
      heroSlotHPs: [
        document.getElementById('hero-1-hp'),
        document.getElementById('hero-2-hp'),
        document.getElementById('hero-3-hp')
      ],
      enemySlot: document.getElementById('enemy-slot'),
      enemySlotChar: document.getElementById('enemy-1'),
      enemySlotHP: document.getElementById('enemy-1-hp')
    };

    this.init();
  }

  init() {
    this.ui.restartBtnOver.addEventListener('click', () => this.restartGame());
    this.ui.restartBtnWon.addEventListener('click', () => this.restartGame());
    
    // Tab switching
    this.ui.abilitiesTab.addEventListener('click', () => this.switchTab('abilities'));
    this.ui.itemsTab.addEventListener('click', () => this.switchTab('items'));
    
    this.startGame();
  }

  switchTab(tab) {
    this.currentTab = tab;
    if (tab === 'abilities') {
      this.ui.abilitiesPanel.classList.add('active');
      this.ui.abilitiesPanel.style.display = 'flex';
      this.ui.itemsPanel.classList.remove('active');
      this.ui.itemsPanel.style.display = 'none';
      this.ui.abilitiesTab.classList.add('active');
      this.ui.itemsTab.classList.remove('active');
    } else {
      this.ui.itemsPanel.classList.add('active');
      this.ui.itemsPanel.style.display = 'flex';
      this.ui.abilitiesPanel.classList.remove('active');
      this.ui.abilitiesPanel.style.display = 'none';
      this.ui.itemsTab.classList.add('active');
      this.ui.abilitiesTab.classList.remove('active');
    }
  }

  startGame() {
    this.gameState.reset();
    this.gameState.initParty(['warrior', 'hunter', 'mage']);
    this.gameState.startLevel(1);
    this.isGameActive = true;
    this.gestureController.start();
    this.touchController.start();
    this.selectedMemberIndex = 0;
    this.renderCombatSlots();
    this.renderAbilities();
    this.renderItems();
    this.updateUI();
    this.processTurn();
  }

  restartGame() {
    document.body.classList.remove('dying');
    this.ui.gameOver.classList.add('hidden');
    this.ui.gameOver.style.display = 'none';
    this.ui.gameWon.classList.add('hidden');
    this.ui.gameWon.style.display = 'none';
    this.startGame();
  }

  renderCombatSlots() {
    // Render heroes
    this.gameState.party.forEach((member, index) => {
      const slot = this.ui.heroSlots[index];
      const charEl = this.ui.heroSlotChars[index];
      const hpEl = this.ui.heroSlotHPs[index];
      
      if (!member.isAlive) {
        slot.classList.add('dead');
      } else {
        slot.classList.remove('dead');
      }
      
      // Get character SVG
      const character = CHARACTERS[member.classKey];
      if (character) {
        charEl.innerHTML = character.svg;
      }
      
      // Update HP bar
      const hpPercent = (member.hp / member.maxHp) * 100;
      hpEl.style.width = `${hpPercent}%`;
    });

    // Render enemy
    const enemy = this.gameState.currentEnemy;
    if (enemy) {
      let enemyName = enemy.name.toLowerCase();
      if (enemyName === 'death knight') enemyName = 'deathKnight';
      const enemyCharacter = CHARACTERS[enemyName];
      if (enemyCharacter) {
        this.ui.enemySlotChar.innerHTML = enemyCharacter.svg;
      }
      
      this.ui.enemyName.textContent = enemy.name;
      
      const hpPercent = (enemy.hp / enemy.maxHp) * 100;
      this.ui.enemySlotHP.style.width = `${hpPercent}%`;
    }
  }

  renderAbilities() {
    const currentTurn = this.gameState.getCurrentTurn();
    if (!currentTurn || currentTurn.type !== 'player') {
      this.ui.abilitiesContainer.innerHTML = '<div class="no-selection">Wait for your turn...</div>';
      return;
    }

    const member = this.gameState.party.find(m => m.name === currentTurn.name);
    if (!member || !member.isAlive) {
      this.ui.abilitiesContainer.innerHTML = '<div class="no-selection">Character is dead!</div>';
      return;
    }

    this.ui.abilitiesContainer.innerHTML = '';

    Object.entries(member.abilities).forEach(([key, ability]) => {
      const abilityEl = document.createElement('div');
      abilityEl.className = `ability-card ${ability.apCost > member.ap ? 'disabled' : ''}`;
      abilityEl.style.borderLeftColor = member.color;
      
      abilityEl.innerHTML = `
        <div class="ability-name">${ability.name}</div>
        <div class="ability-desc">${ability.desc}</div>
        <div class="ability-cost">Cost: ${ability.apCost} AP</div>
      `;
      
      if (ability.apCost <= member.ap && member.isAlive) {
        abilityEl.addEventListener('click', () => {
          this.handleAbility(key);
        });
      }
      
      this.ui.abilitiesContainer.appendChild(abilityEl);
    });
  }

  renderItems() {
    const potionCount = this.gameState.potions;
    
    this.ui.itemsContainer.innerHTML = `
      <div class="item-card ${potionCount <= 0 ? 'disabled' : ''}" id="potion-item">
        <div class="item-icon">🧪</div>
        <div class="item-info">
          <div class="item-name">Health Potion</div>
          <div class="item-desc">Restore 30 HP to lowest ally</div>
        </div>
        <div class="item-count">x${potionCount}</div>
      </div>
    `;
    
    if (potionCount > 0) {
      document.getElementById('potion-item').addEventListener('click', () => {
        this.usePotion();
      });
    }
  }

  updateUI() {
    const { level, combatLog } = this.gameState;

    this.ui.level.textContent = level;
    
    // Update turn indicator
    const currentTurn = this.gameState.getCurrentTurn();
    if (currentTurn) {
      if (currentTurn.type === 'player') {
        this.ui.turnIndicator.textContent = `${currentTurn.name}'s turn`;
        this.ui.turnIndicator.className = 'turn-indicator player-turn';
      } else {
        this.ui.turnIndicator.textContent = 'Enemy turn';
        this.ui.turnIndicator.className = 'turn-indicator enemy-turn';
      }
    }

    // Highlight current character slot
    this.ui.heroSlots.forEach((slot, i) => {
      if (currentTurn && currentTurn.type === 'player') {
        const member = this.gameState.party[i];
        if (member && member.name === currentTurn.name) {
          slot.classList.add('current-turn');
        } else {
          slot.classList.remove('current-turn');
        }
      } else {
        slot.classList.remove('current-turn');
      }
    });

    // Update combat log
    this.ui.combatLog.innerHTML = '';
    combatLog.slice(-8).forEach(log => {
      const logEl = document.createElement('div');
      logEl.className = 'log-entry';
      logEl.textContent = log;
      this.ui.combatLog.appendChild(logEl);
    });
    this.ui.combatLog.scrollTop = this.ui.combatLog.scrollHeight;
  }

  processTurn() {
    const currentTurn = this.gameState.getCurrentTurn();
    if (!currentTurn) return;

    if (currentTurn.type === 'player') {
      this.renderAbilities();
      this.renderItems();
    } else if (currentTurn.type === 'enemy') {
      this.ui.turnIndicator.textContent = 'Enemy turn';
      this.ui.turnIndicator.className = 'turn-indicator enemy-turn';
      
      setTimeout(() => {
        this.performEnemyAttack();
      }, 500);
    }
  }

  performEnemyAttack() {
    const enemy = this.gameState.currentEnemy;
    if (!enemy) return;

    // Get a living hero to attack
    const livingHeroes = this.gameState.party.filter(m => m.isAlive);
    if (livingHeroes.length === 0) return;
    
    const target = livingHeroes[Math.floor(Math.random() * livingHeroes.length)];
    const targetIndex = this.gameState.party.indexOf(target);

    // Animate enemy attacking
    this.ui.enemySlotChar.classList.add('enemy-attacking');
    
    // Show effect on target hero
    setTimeout(() => {
      const slotEl = this.ui.heroSlots[targetIndex];
      const rect = slotEl.getBoundingClientRect();
      const hudRect = this.ui.effectContainer.getBoundingClientRect();
      
      this.showEffectAt(
        rect.left - hudRect.left + rect.width/2,
        rect.top - hudRect.top + rect.height/2,
        'slash-effect'
      );
      
      // Deal damage
      const damage = Math.max(1, enemy.damage - target.def);
      target.hp = Math.max(0, target.hp - damage);
      
      this.showDamageAt(
        rect.left - hudRect.left + rect.width/2,
        rect.top - hudRect.top,
        damage
      );
      
      this.gameState.log(`${enemy.name} attacks ${target.name} for ${damage} damage!`);
      
      setTimeout(() => {
        this.ui.enemySlotChar.classList.remove('enemy-attacking');
        this.renderCombatSlots();
        this.updateUI();
        
        // Check game over
        const gameOverCheck = this.gameState.checkGameOver();
        if (gameOverCheck?.gameOver) {
          this.isGameActive = false;
          this.triggerDeathAnimation();
          return;
        }

        this.gameState.advanceTurn();
        this.renderCombatSlots();
        this.updateUI();
        this.processTurn();
      }, 500);
    }, 400);
  }

  handleAbility(abilityKey) {
    if (!this.isGameActive) return;

    const currentTurn = this.gameState.getCurrentTurn();
    if (!currentTurn || currentTurn.type !== 'player') return;

    const member = this.gameState.party.find(m => m.name === currentTurn.name);
    if (!member || !member.isAlive) return;

    const result = this.gameState.playerAction(member, abilityKey);
    if (!result.success) return;

    // Animate hero attacking
    const memberIndex = this.gameState.party.indexOf(member);
    const slotChar = this.ui.heroSlotChars[memberIndex];
    
    slotChar.classList.add('hero-attacking');
    
    // Show effect on enemy
    setTimeout(() => {
      const enemyRect = this.ui.enemySlot.getBoundingClientRect();
      const hudRect = this.ui.effectContainer.getBoundingClientRect();
      
      const ability = member.abilities[abilityKey];
      let effectType = 'slash-effect';
      if (ability.type === 'magical') effectType = 'fire-effect';
      else if (ability.type === 'heal') effectType = 'heal-effect';
      else if (ability.type === 'cc') effectType = 'frost-effect';
      
      this.showEffectAt(
        enemyRect.left - hudRect.left + enemyRect.width/2,
        enemyRect.top - hudRect.top + enemyRect.height/2,
        effectType
      );
      
      if (result.damage > 0) {
        this.showDamageAt(
          enemyRect.left - hudRect.left + enemyRect.width/2,
          enemyRect.top - hudRect.top,
          result.damage
        );
      }
      
      this.renderCombatSlots();
      this.updateUI();
      
      setTimeout(() => {
        slotChar.classList.remove('hero-attacking');
        
        // Check victory
        const victoryCheck = this.gameState.checkVictory();
        if (victoryCheck?.won) {
          this.isGameActive = false;
          this.ui.gameWon.classList.remove('hidden');
          this.ui.gameWon.style.display = 'flex';
          return;
        }

        if (victoryCheck?.nextLevel) {
          this.showLevelTransition(victoryCheck.nextLevel);
          return;
        }

        this.gameState.advanceTurn();
        this.renderCombatSlots();
        this.renderAbilities();
        this.renderItems();
        this.updateUI();
        this.processTurn();
      }, 500);
    }, 400);
  }

  handleAction(action) {
    const currentTurn = this.gameState.getCurrentTurn();
    if (!currentTurn || currentTurn.type !== 'player') return;

    const member = this.gameState.party.find(m => m.name === currentTurn.name);
    if (!member || !member.isAlive) return;

    if (member.abilities[action]) {
      this.handleAbility(action);
    }
  }

  usePotion() {
    if (!this.isGameActive) return;
    if (this.gameState.potions <= 0) {
      this.gameState.log('No potions left!');
      return;
    }

    const livingParty = this.gameState.party.filter(m => m.isAlive);
    if (livingParty.length === 0) return;

    const lowestMember = livingParty.reduce((lowest, current) => 
      current.hp < lowest.hp ? current : lowest
    );

    const healAmount = 30;
    lowestMember.hp = Math.min(lowestMember.maxHp, lowestMember.hp + healAmount);
    this.gameState.potions--;
    
    this.gameState.log(`${lowestMember.name} used potion: +${healAmount} HP`);
    
    // Show heal effect
    const memberIndex = this.gameState.party.indexOf(lowestMember);
    const slotEl = this.ui.heroSlots[memberIndex];
    const rect = slotEl.getBoundingClientRect();
    const hudRect = this.ui.effectContainer.getBoundingClientRect();
    
    this.showEffectAt(
      rect.left - hudRect.left + rect.width/2,
      rect.top - hudRect.top + rect.height/2,
      'heal-effect'
    );
    
    this.showHealAt(
      rect.left - hudRect.left + rect.width/2,
      rect.top - hudRect.top,
      healAmount
    );
    
    this.renderCombatSlots();
    this.renderItems();
    this.updateUI();
  }

  showEffectAt(x, y, effectType) {
    const effectEl = document.createElement('div');
    effectEl.className = `ability-effect ${effectType}`;
    effectEl.style.left = `${x - 40}px`;
    effectEl.style.top = `${y - 40}px`;
    
    this.ui.effectContainer.appendChild(effectEl);
    setTimeout(() => effectEl.remove(), 600);
  }

  showDamageAt(x, y, damage) {
    const textEl = document.createElement('div');
    textEl.className = 'damage-text';
    textEl.textContent = `-${damage}`;
    textEl.style.left = `${x - 15}px`;
    textEl.style.top = `${y}px`;
    
    this.ui.effectContainer.appendChild(textEl);
    setTimeout(() => textEl.remove(), 1000);
  }

  showHealAt(x, y, amount) {
    const textEl = document.createElement('div');
    textEl.className = 'heal-text';
    textEl.textContent = `+${amount}`;
    textEl.style.left = `${x - 15}px`;
    textEl.style.top = `${y}px`;
    
    this.ui.effectContainer.appendChild(textEl);
    setTimeout(() => textEl.remove(), 1000);
  }

  showLevelTransition(nextLevel) {
    this.ui.turnIndicator.textContent = `Level ${nextLevel} approaching...`;
    
    setTimeout(() => {
      this.gameState.startLevel(nextLevel);
      this.renderCombatSlots();
      this.renderAbilities();
      this.renderItems();
      this.updateUI();
      this.processTurn();
    }, 1500);
  }

  triggerDeathAnimation() {
    document.body.classList.add('dying');
    
    setTimeout(() => {
      this.ui.gameOver.classList.remove('hidden');
      this.ui.gameOver.style.display = 'flex';
    }, 1500);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new MetaFighterApp();
});