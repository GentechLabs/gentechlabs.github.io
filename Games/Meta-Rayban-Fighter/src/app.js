import { ENEMIES, ACTIONS, KEYBOARD_MAP } from './game-constants.js';
import { GameState } from './game-state.js';
import { GestureController } from './gesture-controller.js';
import { TouchController } from './touch-controller.js';
import { getCharacterSVG } from './characters.js';

class MetaFighterApp {
  constructor() {
    this.gameState = new GameState();
    this.gestureController = new GestureController(this.handleGesture.bind(this));
    this.touchController = new TouchController(this.handleAction.bind(this));
    this.isGameActive = false;

    this.ui = {
      playerHp: document.getElementById('player-hp'),
      enemyHp: document.getElementById('enemy-hp'),
      playerAp: document.getElementById('player-ap'),
      potions: document.getElementById('potions'),
      turnIndicator: document.getElementById('turn-indicator'),
      combatLog: document.getElementById('combat-log'),
      level: document.getElementById('level'),
      enemyName: document.getElementById('enemy-name'),
      playerSpriteContainer: document.getElementById('player-sprite-container'),
      enemySpriteContainer: document.getElementById('enemy-sprite-container'),
      gameOver: document.getElementById('game-over'),
      gameWon: document.getElementById('game-won'),
      restartBtn: document.getElementById('restart-btn')
    };

    this.init();
  }

  init() {
    this.ui.restartBtn.addEventListener('click', () => this.restartGame());
    this.startGame();
  }

  startGame() {
    this.gameState.reset();
    this.gameState.startLevel(1);
    this.isGameActive = true;
    this.gestureController.start();
    this.touchController.start();
    this.renderCharacters();
    this.updateUI();
    this.processTurn();
  }

  restartGame() {
    document.body.classList.remove('dying');
    this.ui.gameOver.classList.add('hidden');
    this.ui.gameWon.classList.add('hidden');
    this.startGame();
  }

  renderCharacters() {
    // Render player knight SVG
    this.ui.playerSpriteContainer.innerHTML = getCharacterSVG('player');
    
    // Render enemy based on current enemy
    if (this.gameState.currentEnemy) {
      const enemyKey = this.gameState.currentEnemy.name.toLowerCase();
      this.ui.enemySpriteContainer.innerHTML = getCharacterSVG(enemyKey);
    }
  }

  handleAction(actionKey) {
    if (!this.isGameActive) return;

    const currentTurn = this.gameState.getCurrentTurn();
    if (currentTurn.type !== 'player') {
      console.log('Not your turn!');
      return;
    }

    const result = this.gameState.playerAction(actionKey);
    if (result.success) {
      this.playActionAnimation(actionKey, result.data);
      this.updateUI();

      // Check if enemy was killed
      if (result.data?.killed) {
        this.showKillMessage(result.data.enemyName);
        
        // Check for boss victory
        const victoryCheck = this.gameState.checkVictory();
        if (victoryCheck?.won) {
          setTimeout(() => {
            this.isGameActive = false;
            this.ui.gameWon.classList.remove('hidden');
          }, 3000);
          return;
        }

        // Proceed to next level
        setTimeout(() => {
          const nextLevel = this.gameState.level + 1;
          this.showLevelTransitionMessage(nextLevel);
          setTimeout(() => {
            this.gameState.startLevel(nextLevel);
            this.renderCharacters();
            this.updateUI();
            this.processTurn();
          }, 2000);
        }, 3000);
        return;
      }

      this.processTurn();
    } else {
      console.log(result.message);
    }
  }

  handleGesture(gestureName) {
    this.handleAction(gestureName);
  }

  playActionAnimation(actionKey, data) {
    const playerSprite = this.ui.playerSpriteContainer.querySelector('svg');
    const enemySprite = this.ui.enemySpriteContainer.querySelector('svg');

    if (!playerSprite || !enemySprite) return;

    // Clear previous animations
    playerSprite.classList.remove('knight-attack-walk', 'knight-damage');
    enemySprite.classList.remove('skeleton-attack-walk', 'skeleton-damage', 
                              'zombie-attack-walk', 'zombie-damage',
                              'ghost-attack-walk', 'ghost-damage');

    if (actionKey === 'attack') {
      playerSprite.classList.add('knight-attack-walk');
      if (data?.damage) {
        this.showDamageNumber(data.damage, this.ui.enemySpriteContainer);
      }
    } else if (actionKey === 'holyStrike' || actionKey === 'smite') {
      playerSprite.classList.add('knight-attack-walk');
      if (data?.damage) {
        this.showDamageNumber(data.damage, this.ui.enemySpriteContainer, true);
      }
    } else if (actionKey === 'potion') {
      this.showHealNumber(data?.healed || 0, this.ui.playerSpriteContainer);
    }

    if (data?.damage && data.damage > 0) {
      const enemyClass = this.getEnemyAnimationClass();
      enemySprite.classList.add(`${enemyClass}-damage`);
      setTimeout(() => enemySprite.classList.remove(`${enemyClass}-damage`), 400);
    }

    setTimeout(() => {
      playerSprite.classList.remove('knight-attack-walk');
    }, 800);
  }

  playEnemyAttackAnimation(damage) {
    const playerSprite = this.ui.playerSpriteContainer.querySelector('svg');
    const enemySprite = this.ui.enemySpriteContainer.querySelector('svg');

    if (!playerSprite || !enemySprite) return;

    // Clear previous animations
    enemySprite.classList.remove('skeleton-attack-walk', 'skeleton-damage', 
                              'zombie-attack-walk', 'zombie-damage',
                              'ghost-attack-walk', 'ghost-damage');
    playerSprite.classList.remove('knight-attack-walk', 'knight-damage');

    // Enemy walks forward to attack
    const enemyClass = this.getEnemyAnimationClass();
    enemySprite.classList.add(`${enemyClass}-attack-walk`);

    setTimeout(() => {
      // Player takes damage
      playerSprite.classList.add('knight-damage');
      this.showDamageNumber(damage, this.ui.playerSpriteContainer);
      
      setTimeout(() => {
        playerSprite.classList.remove('knight-damage');
      }, 400);
    }, 400);

    setTimeout(() => {
      enemySprite.classList.remove(`${enemyClass}-attack-walk`);
    }, 1000);
  }

  getEnemyAnimationClass() {
    const enemyName = this.gameState.currentEnemy?.name?.toLowerCase() || '';
    if (enemyName.includes('skeleton') || enemyName.includes('death knight')) return 'skeleton';
    if (enemyName.includes('zombie')) return 'zombie';
    if (enemyName.includes('ghost')) return 'ghost';
    return 'skeleton'; // default
  }

  showDamageNumber(damage, target, isCrit = false) {
    const damageNumber = document.createElement('div');
    damageNumber.className = `damage-number ${isCrit ? 'damage-crit' : ''}`;
    damageNumber.textContent = `-${damage}`;
    damageNumber.style.left = '50%';
    damageNumber.style.top = '20px';
    damageNumber.style.transform = 'translateX(-50%)';
    target.appendChild(damageNumber);

    setTimeout(() => damageNumber.remove(), 800);
  }

  showHealNumber(healed, target) {
    const healNumber = document.createElement('div');
    healNumber.className = 'damage-number heal-number';
    healNumber.textContent = `+${healed}`;
    healNumber.style.left = '50%';
    healNumber.style.top = '20px';
    healNumber.style.transform = 'translateX(-50%)';
    target.appendChild(healNumber);

    setTimeout(() => healNumber.remove(), 800);
  }

  processTurn() {
    if (!this.isGameActive) return;

    const currentTurn = this.gameState.getCurrentTurn();

    if (currentTurn.type === 'enemy') {
      this.ui.turnIndicator.textContent = `${this.gameState.currentEnemy.name}'s turn...`;
      this.ui.turnIndicator.className = 'turn-indicator enemy-turn';

      setTimeout(() => {
        const enemyDamage = this.gameState.enemyTurn();
        this.playEnemyAttackAnimation(enemyDamage);
        this.updateUI();

        const victoryCheck = this.gameState.checkVictory();
        if (victoryCheck?.won) {
          this.isGameActive = false;
          this.ui.gameWon.classList.remove('hidden');
          return;
        }

        if (this.gameState.gameOver) {
          this.isGameActive = false;
          this.triggerDeathAnimation();
          return;
        }

        this.ui.turnIndicator.textContent = 'Your turn';
        this.ui.turnIndicator.className = 'turn-indicator player-turn';
        this.processTurn();
      }, 1500);
    } else {
      this.ui.turnIndicator.textContent = 'Your turn';
      this.ui.turnIndicator.className = 'turn-indicator player-turn';
    }
  }

  showKillMessage(enemyName) {
    this.ui.turnIndicator.textContent = `You slayed ${enemyName}!`;
    this.ui.turnIndicator.className = 'turn-indicator player-turn';
    
    // Flash enemy red then fade out
    const enemySprite = this.ui.enemySpriteContainer.querySelector('svg');
    if (enemySprite) {
      enemySprite.style.transition = 'opacity 0.5s, filter 0.5s';
      enemySprite.style.filter = 'brightness(2) hue-rotate(340deg)';
      setTimeout(() => {
        enemySprite.style.opacity = '0.3';
        enemySprite.style.filter = 'brightness(0.5) grayscale(1)';
      }, 300);
    }
  }

  showLevelTransitionMessage(nextLevel) {
    const nextEnemy = nextLevel === 2 ? 'Zombie' : (nextLevel === 3 ? 'Ghost' : 'Death Knight (Boss)');
    this.ui.turnIndicator.textContent = `Continue to Level ${nextLevel}: ${nextEnemy} awaits...`;
    this.ui.turnIndicator.className = 'turn-indicator player-turn';
  }

  updateUI() {
    const { player, currentEnemy, level, combatLog } = this.gameState;

    this.ui.playerHp.textContent = `${player.hp}/${player.maxHp}`;
    this.ui.playerHp.style.width = `${(player.hp / player.maxHp) * 100}%`;

    if (currentEnemy) {
      this.ui.enemyHp.textContent = `${currentEnemy.hp}/${currentEnemy.maxHp}`;
      this.ui.enemyHp.style.width = `${(currentEnemy.hp / currentEnemy.maxHp) * 100}%`;
      this.ui.enemyName.textContent = currentEnemy.name;
    }

    this.ui.playerAp.textContent = `${player.ap}/${player.maxAp}`;
    this.ui.potions.textContent = player.potions;
    this.ui.level.textContent = level;

    this.ui.combatLog.innerHTML = combatLog.map(log =>
      `<div class="log-entry">${log.message}</div>`
    ).join('');

    this.ui.combatLog.scrollTop = this.ui.combatLog.scrollHeight;

    if (player.ap < player.maxAp && this.gameState.getCurrentTurn().type === 'player') {
      player.ap = Math.min(player.maxAp, player.ap + 1);
    }
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