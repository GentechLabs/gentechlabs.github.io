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

    this.ui = {
      level: document.getElementById('level'),
      turnIndicator: document.getElementById('turn-indicator'),
      combatLog: document.getElementById('combat-log'),
      enemyName: document.getElementById('enemy-name'),
      enemySpriteContainer: document.getElementById('enemy-sprite-container'),
      partyContainer: document.getElementById('party-container'),
      abilitiesContainer: document.getElementById('abilities-container'),
      gameOver: document.getElementById('game-over'),
      gameWon: document.getElementById('game-won'),
      restartBtn: document.getElementById('restart-btn'),
      potionBtn: document.getElementById('potion-btn')
    };

    this.init();
  }

  init() {
    this.ui.restartBtn.addEventListener('click', () => this.restartGame());
    this.ui.potionBtn.addEventListener('click', () => this.usePotion());
    this.startGame();
  }

  startGame() {
    this.gameState.reset();
    this.gameState.initParty(['warrior', 'hunter', 'mage']);
    this.gameState.startLevel(1);
    this.isGameActive = true;
    this.gestureController.start();
    this.touchController.start();
    this.selectedMemberIndex = 0;
    this.renderParty();
    this.renderCharacters();
    this.renderAbilities();
    this.updateUI();
    this.processTurn();
  }

  restartGame() {
    document.body.classList.remove('dying');
    this.ui.gameOver.classList.add('hidden');
    this.ui.gameWon.classList.add('hidden');
    this.startGame();
  }

  renderParty() {
    this.ui.partyContainer.innerHTML = '';
    
    this.gameState.party.forEach((member, index) => {
      const memberEl = document.createElement('div');
      memberEl.className = `party-member ${!member.isAlive ? 'dead' : ''} ${index === this.selectedMemberIndex ? 'selected' : ''}`;
      memberEl.style.borderLeft = `3px solid ${member.color}`;
      memberEl.innerHTML = `
        <div class="member-header">
          <span class="member-icon">${CLASS_ICONS[member.classKey]}</span>
          <span class="member-name">${member.name}</span>
          <span class="member-role">${member.role}</span>
        </div>
        <div class="hp-bar-mini">
          <div class="hp-fill-mini" style="width: ${(member.hp / member.maxHp) * 100}%; background: ${member.color}"></div>
          <span class="hp-text-mini">${member.hp}/${member.maxHp}</span>
        </div>
        <div class="stats-mini">
          <span class="ap-stat">AP: ${member.ap}/${member.maxAp}</span>
          <span class="protection-stat">DEF: ${member.protection}</span>
        </div>
      `;
      
      memberEl.addEventListener('click', () => {
        this.selectedMemberIndex = index;
        this.renderParty();
        this.renderAbilities();
      });
      
      this.ui.partyContainer.appendChild(memberEl);
    });
  }

  renderAbilities() {
    const member = this.gameState.party[this.selectedMemberIndex];
    if (!member || !member.isAlive) {
      this.ui.abilitiesContainer.innerHTML = '<div class="no-selection">Select a living party member</div>';
      return;
    }

    this.ui.abilitiesContainer.innerHTML = '';
    
    Object.entries(member.abilities).forEach(([key, ability]) => {
      const abilityEl = document.createElement('div');
      abilityEl.className = `ability-card ${member.ap < ability.cost ? 'disabled' : ''}`;
      abilityEl.setAttribute('data-ability', key);
      abilityEl.style.borderColor = member.color;
      abilityEl.innerHTML = `
        <div class="ability-name">${ability.name}</div>
        <div class="ability-desc">${ability.description}</div>
        <div class="ability-cost">Cost: ${ability.cost} AP</div>
        <div class="ability-type">${ability.type}</div>
      `;
      
      abilityEl.addEventListener('click', () => {
        this.handleAbility(key);
      });
      
      this.ui.abilitiesContainer.appendChild(abilityEl);
    });
  }

  renderCharacters() {
    if (!this.gameState.currentEnemy) return;

    const enemy = this.gameState.currentEnemy;
    const enemyClass = enemy.name.toLowerCase().replace(' ', '');
    const enemySvg = CHARACTERS[enemyClass]?.svg || CHARACTERS.skeleton?.svg;
    
    this.ui.enemySpriteContainer.innerHTML = enemySvg;
    const enemySvgElement = this.ui.enemySpriteContainer.querySelector('svg');
    if (enemySvgElement) {
      enemySvgElement.classList.add(`${enemyClass}-sprite`);
    }

    // Render current hero
    const heroSpriteContainer = document.getElementById('hero-sprite-container');
    if (heroSpriteContainer) {
      const currentTurn = this.gameState.getCurrentTurn();
      if (currentTurn && currentTurn.type === 'player' && currentTurn.member) {
        const heroClass = currentTurn.member.classKey;
        const heroSvg = CHARACTERS[heroClass]?.svg;
        if (heroSvg) {
          heroSpriteContainer.innerHTML = heroSvg;
        }
      }
    }
  }

  updateUI() {
    const { party, currentEnemy, level, combatLog, potions } = this.gameState;

    this.ui.level.textContent = level;
    this.ui.enemyName.textContent = currentEnemy?.name || '';
    
    // Update potions display
    const potionsSpan = document.getElementById('potions');
    if (potionsSpan) {
      potionsSpan.textContent = potions;
    }
    
    if (currentEnemy) {
      const enemyHpFill = document.getElementById('enemy-hp');
      if (enemyHpFill) {
        enemyHpFill.style.width = `${(currentEnemy.hp / currentEnemy.maxHp) * 100}%`;
        enemyHpFill.textContent = `${currentEnemy.hp}/${currentEnemy.maxHp}`;
      }
    }

    this.renderParty();
    this.renderAbilities();
    this.renderCharacters();

    this.ui.combatLog.innerHTML = combatLog.slice(-10).map(entry => 
      `<div class="log-entry">${entry}</div>`
    ).join('');

    this.ui.combatLog.scrollTop = this.ui.combatLog.scrollHeight;
  }

  processTurn() {
    if (!this.isGameActive) return;

    const currentTurn = this.gameState.getCurrentTurn();
    
    if (!currentTurn) {
      this.gameState.turnOrder = this.gameState.buildTurnOrder();
      this.currentTurnIndex = 0;
      this.updateUI();
      return;
    }

    if (currentTurn.type === 'player') {
      this.ui.turnIndicator.textContent = `${currentTurn.name}'s turn`;
      this.ui.turnIndicator.className = 'turn-indicator player-turn';
      this.ui.turnIndicator.style.background = currentTurn.member.color;
      
      const memberIndex = this.gameState.party.findIndex(m => m.name === currentTurn.name);
      if (memberIndex !== -1) {
        this.selectedMemberIndex = memberIndex;
        this.renderParty();
        this.renderAbilities();
      }
    } else if (currentTurn.type === 'enemy') {
      this.ui.turnIndicator.textContent = `Enemy turn`;
      this.ui.turnIndicator.className = 'turn-indicator enemy-turn';
      this.ui.turnIndicator.style.background = '#8b0000';
      
      setTimeout(() => {
        const damage = this.gameState.enemyTurn();
        this.showEnemyAttack(damage);
        this.updateUI();
        
        setTimeout(() => {
          const gameOverCheck = this.gameState.checkGameOver();
          if (gameOverCheck?.gameOver) {
            this.isGameActive = false;
            this.triggerDeathAnimation();
            return;
          }

          this.gameState.advanceTurn();
          this.gameState.turnOrder = this.gameState.buildTurnOrder();
          this.currentTurnIndex = 0;
          this.updateUI();
          this.processTurn();
        }, 1000);
      }, 1000);
    }
  }

  handleAbility(abilityKey) {
    if (!this.isGameActive) return;

    const currentTurn = this.gameState.getCurrentTurn();
    if (!currentTurn || currentTurn.type !== 'player') {
      console.log('Not your turn!');
      return;
    }

    const member = this.gameState.party[this.selectedMemberIndex];
    if (!member || !member.isAlive || member.name !== currentTurn.name) {
      console.log('Select the current turn member');
      return;
    }

    const result = this.gameState.playerAction(member, abilityKey);
    if (!result.success) {
      console.log(result.message);
      return;
    }

    this.updateUI();
    this.showAbilityAnimation(member, abilityKey, result);

    setTimeout(() => {
      const victoryCheck = this.gameState.checkVictory();
      if (victoryCheck?.won) {
        this.isGameActive = false;
        this.ui.gameWon.classList.remove('hidden');
        return;
      }

      if (victoryCheck?.nextLevel) {
        this.showLevelTransition(victoryCheck.nextLevel);
        return;
      }

      this.gameState.advanceTurn();
      this.gameState.turnOrder = this.gameState.buildTurnOrder();
      this.currentTurnIndex = 0;
      this.updateUI();
      this.processTurn();
    }, 1000);
  }

  handleAction(action) {
    const currentTurn = this.gameState.getCurrentTurn();
    if (!currentTurn || currentTurn.type !== 'player') return;

    if (action === 'potion') {
      this.usePotion();
      return;
    }

    const member = this.gameState.party[this.selectedMemberIndex];
    if (member && member.abilities[action]) {
      this.handleAbility(action);
    }
  }

  usePotion() {
    const lowestHpMember = this.gameState.party
      .filter(m => m.isAlive)
      .sort((a, b) => (a.hp / a.maxHp) - (b.hp / b.maxHp))[0];

    if (!lowestHpMember) {
      console.log('No living party members');
      return;
    }

    const result = this.gameState.usePotion(lowestHpMember);
    if (result.success) {
      this.updateUI();
      this.showHealAnimation(lowestHpMember, result.heal);
    }
  }

  showAbilityAnimation(member, abilityKey, result) {
    const memberElement = document.querySelector(`.party-member:nth-child(${this.gameState.party.indexOf(member) + 1})`);
    if (memberElement) {
      memberElement.classList.add('ability-active');
      setTimeout(() => memberElement.classList.remove('ability-active'), 500);
    }

    if (result.damage > 0) {
      const enemySprite = this.ui.enemySpriteContainer.querySelector('svg');
      if (enemySprite) {
        enemySprite.classList.add('taking-damage');
        setTimeout(() => enemySprite.classList.remove('taking-damage'), 500);
      }
    }
  }

  showEnemyAttack(damage) {
    const enemySprite = this.ui.enemySpriteContainer.querySelector('svg');
    if (enemySprite) {
      enemySprite.classList.add('enemy-attacking');
      setTimeout(() => enemySprite.classList.remove('enemy-attacking'), 500);
    }
  }

  showHealAnimation(member, healAmount) {
    const memberElement = document.querySelector(`.party-member:nth-child(${this.gameState.party.indexOf(member) + 1})`);
    if (memberElement) {
      memberElement.classList.add('healing');
      setTimeout(() => memberElement.classList.remove('healing'), 500);
    }
  }

  showLevelTransition(nextLevel) {
    this.ui.turnIndicator.textContent = `Level ${nextLevel} approaching...`;
    this.ui.turnIndicator.className = 'turn-indicator player-turn';
    
    setTimeout(() => {
      this.gameState.startLevel(nextLevel);
      this.gameState.turnOrder = this.gameState.buildTurnOrder();
      this.currentTurnIndex = 0;
      this.renderCharacters();
      this.updateUI();
      this.processTurn();
    }, 2000);
  }

  triggerDeathAnimation() {
    document.body.classList.add('dying');
    
    setTimeout(() => {
      this.ui.gameOver.classList.remove('hidden');
    }, 2000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.gameApp = new MetaFighterApp();
});