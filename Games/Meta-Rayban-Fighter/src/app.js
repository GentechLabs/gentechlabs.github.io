import { ENEMIES, ACTIONS, KEYBOARD_MAP } from './game-constants.js';
import { GameState } from './game-state.js';
import { GestureController } from './gesture-controller.js';

class MetaFighterApp {
  constructor() {
    this.gameState = new GameState();
    this.gestureController = new GestureController(this.handleGesture.bind(this));
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
    this.updateUI();
    this.processTurn();
  }

  restartGame() {
    this.ui.gameOver.classList.add('hidden');
    this.ui.gameWon.classList.add('hidden');
    this.startGame();
  }

  handleGesture(gestureName) {
    if (!this.isGameActive) return;

    const currentTurn = this.gameState.getCurrentTurn();
    if (currentTurn.type !== 'player') {
      console.log('Not your turn!');
      return;
    }

    // Use the gesture name directly (already matches action keys)
    const result = this.gameState.playerAction(gestureName);
    if (result.success) {
      this.updateUI();

      // Check if enemy defeated
      const victoryCheck = this.gameState.checkVictory();
      if (victoryCheck?.won) {
        this.isGameActive = false;
        this.ui.gameWon.classList.remove('hidden');
        return;
      }

      // Level complete?
      if (result.levelComplete) {
        setTimeout(() => {
          this.gameState.startLevel(result.nextLevel);
          this.updateUI();
          this.processTurn();
        }, 2000);
        return;
      }

      this.processTurn();
    } else {
      console.log(result.message);
    }
  }

  processTurn() {
    if (!this.isGameActive) return;

    const currentTurn = this.gameState.getCurrentTurn();

    if (currentTurn.type === 'enemy') {
      this.ui.turnIndicator.textContent = `${this.gameState.currentEnemy.name}'s turn...`;
      this.ui.turnIndicator.className = 'enemy-turn';

      setTimeout(() => {
        this.gameState.enemyTurn();
        this.updateUI();

        const victoryCheck = this.gameState.checkVictory();
        if (victoryCheck?.won) {
          this.isGameActive = false;
          this.ui.gameWon.classList.remove('hidden');
          return;
        }

        if (this.gameState.gameOver) {
          this.isGameActive = false;
          this.ui.gameOver.classList.remove('hidden');
          return;
        }

        this.ui.turnIndicator.textContent = 'Your turn';
        this.ui.turnIndicator.className = 'player-turn';
        this.processTurn();
      }, 1000);
    } else {
      this.ui.turnIndicator.textContent = 'Your turn';
      this.ui.turnIndicator.className = 'player-turn';
    }
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

    // Update combat log
    this.ui.combatLog.innerHTML = combatLog.map(log =>
      `<div class="log-entry">${log.message}</div>`
    ).join('');

    // Auto-scroll log
    this.ui.combatLog.scrollTop = this.ui.combatLog.scrollHeight;

    // AP regen (1 per turn)
    if (player.ap < player.maxAp && this.gameState.getCurrentTurn().type === 'player') {
      player.ap = Math.min(player.maxAp, player.ap + 1);
    }
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.gameApp = new MetaFighterApp();
});