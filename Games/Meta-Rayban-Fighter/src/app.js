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
      heroSpriteContainer: document.getElementById('hero-sprite-container'),
      partyContainer: document.getElementById('party-container'),
      abilitiesContainer: document.getElementById('abilities-container'),
      gameOver: document.getElementById('game-over'),
      gameWon: document.getElementById('game-won'),
      restartBtnOver: document.getElementById('restart-btn-over'),
      restartBtnWon: document.getElementById('restart-btn-won'),
      potionBtn: document.getElementById('potion-btn'),
      effectContainer: document.getElementById('effect-container')
    };

    this.init();
  }

  init() {
    this.ui.restartBtnOver.addEventListener('click', () => this.restartGame());
    this.ui.restartBtnWon.addEventListener('click', () => this.restartGame());
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
    this.ui.gameOver.style.display = 'none';
    this.ui.gameWon.classList.add('hidden');
    this.ui.gameWon.style.display = 'none';
    this.startGame();
  }

  renderParty() {
    this.ui.partyContainer.innerHTML = '';
    
    this.gameState.party.forEach((member, index) => {
      const currentTurn = this.gameState.getCurrentTurn();
      const isCurrentTurn = currentTurn && currentTurn.type === 'player' && currentTurn.name === member.name;
      
      const memberEl = document.createElement('div');
      memberEl.className = `party-member ${!member.isAlive ? 'dead' : ''}`;
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
          <span class="def-stat">DEF: ${member.def}</span>
        </div>
        ${isCurrentTurn ? '<div class="current-turn-indicator">⬆️ CURRENT TURN</div>' : ''}
      `;
      
      this.ui.partyContainer.appendChild(memberEl);
    });
  }

  renderCharacters() {
    // Render current hero
    const currentTurn = this.gameState.getCurrentTurn();
    let heroName = 'warrior';
    if (currentTurn && currentTurn.type === 'player') {
      const currentMember = this.gameState.party.find(m => m.name === currentTurn.name);
      if (currentMember) {
        heroName = currentMember.classKey;
      }
    }
    
    const heroCharacter = CHARACTERS[heroName];
    if (heroCharacter && this.ui.heroSpriteContainer) {
      this.ui.heroSpriteContainer.innerHTML = heroCharacter.svg;
    }
    
    // Render enemy
    const enemy = this.gameState.currentEnemy;
    if (enemy && this.ui.enemySpriteContainer) {
      let enemyName = enemy.name.toLowerCase();
      if (enemyName === 'death knight') enemyName = 'deathKnight';
      const enemyCharacter = CHARACTERS[enemyName];
      if (enemyCharacter) {
        this.ui.enemySpriteContainer.innerHTML = enemyCharacter.svg;
      }
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
    
    // Character title
    const titleEl = document.createElement('div');
    titleEl.className = 'current-character-title';
    titleEl.innerHTML = `<span class="character-title-icon">${CLASS_ICONS[member.classKey]}</span> ${member.name}'s Abilities`;
    this.ui.abilitiesContainer.appendChild(titleEl);

    // Render abilities
    Object.entries(member.abilities).forEach(([key, ability]) => {
      const abilityEl = document.createElement('div');
      abilityEl.className = `ability-card ${ability.apCost > member.ap ? 'disabled' : ''}`;
      abilityEl.style.borderLeftColor = member.color;
      
      abilityEl.innerHTML = `
        <div class="ability-name">${ability.name}</div>
        <div class="ability-desc">${ability.desc}</div>
        <div class="ability-cost">Cost: ${ability.apCost} AP</div>
        <div class="ability-type">${ability.type}</div>
      `;
      
      if (ability.apCost <= member.ap && member.isAlive) {
        abilityEl.addEventListener('click', () => {
          this.selectedMemberIndex = this.gameState.party.indexOf(member);
          this.handleAbility(key);
        });
      }
      
      this.ui.abilitiesContainer.appendChild(abilityEl);
    });
  }

  updateUI() {
    const { party, currentEnemy, level, combatLog, potions } = this.gameState;

    this.ui.level.textContent = level;
    this.ui.enemyName.textContent = currentEnemy?.name || '';
    
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

    // Update combat log
    this.ui.combatLog.innerHTML = '';
    combatLog.slice(-15).forEach(log => {
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
      this.selectedMemberIndex = this.gameState.party.findIndex(m => m.name === currentTurn.name);
      this.renderParty();
      this.renderCharacters();
      this.renderAbilities();
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

    const member = this.gameState.party.find(m => m.name === currentTurn.name);
    if (!member || !member.isAlive) {
      console.log('Character is dead!');
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
        this.ui.gameWon.style.display = 'flex';
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

    const member = this.gameState.party.find(m => m.name === currentTurn.name);
    if (!member || !member.isAlive) return;

    const abilityKey = action;
    if (member.abilities[abilityKey]) {
      this.handleAbility(abilityKey);
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

    // Heal lowest HP party member
    const lowestMember = livingParty.reduce((lowest, current) => 
      current.hp < lowest.hp ? current : lowest
    );

    const healAmount = 30;
    lowestMember.hp = Math.min(lowestMember.maxHp, lowestMember.hp + healAmount);
    this.gameState.potions--;
    
    this.gameState.log(`${lowestMember.name} used potion: +${healAmount} HP`);
    this.updateUI();
    this.renderParty();
    
    this.showHealAnimation(lowestMember, healAmount);
  }

  showEnemyAttack(damageData) {
    const { totalDamage, effectType } = damageData;
    
    // Trigger visual effect based on enemy ability
    if (effectType) {
      this.playVisualEffect(effectType, 'enemy');
    }
    
    const enemySprite = this.ui.enemySpriteContainer.querySelector('svg');
    if (enemySprite) {
      enemySprite.classList.add('enemy-attacking');
      setTimeout(() => enemySprite.classList.remove('enemy-attacking'), 500);
    }
    
    // Show damage text
    if (totalDamage > 0) {
      this.showDamageText(totalDamage, 'enemy');
    }
  }
  
  showAbilityAnimation(member, abilityKey, result) {
    const ability = member.abilities[abilityKey];
    if (!ability) return;
    
    // Map ability types to visual effects
    const effectMap = {
      'magical': 'fireballEffect',
      'lightning': 'lightningEffect',
      'heal': 'healEffect',
      'defense': 'shieldEffect',
      'cc': 'frostNovaEffect',
      'debuff': 'tauntEffect',
      'physical': 'slashEffect'
    };
    
    const effectType = effectMap[ability.type] || 'slashEffect';
    this.playVisualEffect(effectType, 'player');
    
    // Show damage or heal text
    if (result.damage > 0) {
      this.showDamageText(result.damage, 'player');
    } else if (result.healAmount > 0) {
      this.showHealText(result.healAmount, 'player');
    }
  }
  
  playVisualEffect(effectType, source) {
    const effectClass = `${effectType}-effect` || 'slash-effect';
    const effectEl = document.createElement('div');
    effectEl.className = `ability-effect ${effectClass}`;
    
    // Position effect based on source
    if (source === 'player') {
      effectEl.style.left = '30%';
    } else {
      effectEl.style.left = '70%';
    }
    
    this.ui.effectContainer.appendChild(effectEl);
    
    // Remove effect after animation
    setTimeout(() => {
      effectEl.remove();
    }, 1000);
  }
  
  showDamageText(damage, source) {
    const textEl = document.createElement('div');
    textEl.className = 'damage-text';
    textEl.textContent = `-${damage}`;
    
    if (source === 'player') {
      textEl.style.left = '70%';
    } else {
      textEl.style.left = '30%';
    }
    textEl.style.top = '40%';
    
    this.ui.effectContainer.appendChild(textEl);
    
    setTimeout(() => {
      textEl.remove();
    }, 1000);
  }
  
  showHealText(healAmount, source) {
    const textEl = document.createElement('div');
    textEl.className = 'heal-text';
    textEl.textContent = `+${healAmount}`;
    
    if (source === 'player') {
      textEl.style.left = '30%';
    } else {
      textEl.style.left = '70%';
    }
    textEl.style.top = '40%';
    
    this.ui.effectContainer.appendChild(textEl);
    
    setTimeout(() => {
      textEl.remove();
    }, 1000);
  }

  showHealAnimation(member, healAmount) {
    const memberElements = this.ui.partyContainer.querySelectorAll('.party-member');
    const memberIndex = this.gameState.party.indexOf(member);
    if (memberElements[memberIndex]) {
      memberElements[memberIndex].classList.add('healing');
      setTimeout(() => memberElements[memberIndex].classList.remove('healing'), 500);
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
      this.ui.gameOver.style.display = 'flex';
    }, 2000);
  }
}

// Start the game when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new MetaFighterApp();
});