import { ENEMIES, ACTIONS, GESTURE_MAP, KEYBOARD_MAP } from './game-constants.js';

export class GameState {
  constructor() {
    this.reset();
  }

  reset() {
    this.level = 1;
    this.player = {
      hp: 100,
      maxHp: 100,
      ap: 2,
      maxAp: 3,
      potions: 3,
      isGuarding: false,
      isCountering: false,
      speed: 55
    };
    this.currentEnemy = null;
    this.turnOrder = [];
    this.currentTurnIndex = 0;
    this.combatLog = [];
    this.gameOver = false;
    this.won = false;
    this.actionQueue = [];
  }

  // Character sprites
  getEnemySprite(enemyName) {
    const sprites = {
      'Skeleton': { emoji: '💀', class: 'skeleton-sprite' },
      'Zombie': { emoji: '🧟', class: 'zombie-sprite' },
      'Ghost': { emoji: '👻', class: 'ghost-sprite' },
      'Death Knight': { emoji: '💀', class: 'skeleton-sprite' }
    };
    return sprites[enemyName] || { emoji: '👾', class: '' };
  }

  getPlayerSprite() {
    return { emoji: '⚔️', class: 'knight-sprite' };
  }

  log(message) {
    this.combatLog.push({ message, time: Date.now() });
    if (this.combatLog.length > 20) {
      this.combatLog.shift();
    }
  }

  startLevel(levelNum) {
    this.level = levelNum;
    this.actionQueue = [];

    if (levelNum === 1) {
      this.currentEnemy = { ...ENEMIES.skeleton };
    } else if (levelNum === 2) {
      this.currentEnemy = { ...ENEMIES.zombie };
    } else if (levelNum === 3) {
      this.currentEnemy = { ...ENEMIES.ghost };
    }

    // Partial heal between levels (20%)
    if (levelNum > 1) {
      const healAmount = Math.floor(this.player.maxHp * 0.2);
      this.player.hp = Math.min(this.player.maxHp, this.player.hp + healAmount);
      this.log(`Recovered ${healAmount} HP between levels.`);
    }

    this.calculateTurnOrder();
    this.log(`Level ${levelNum}: ${this.currentEnemy.name} appears!`);
  }

  calculateTurnOrder() {
    this.turnOrder = [
      { type: 'player', speed: this.player.speed },
      { type: 'enemy', speed: this.currentEnemy.speed }
    ].sort((a, b) => b.speed - a.speed);
    this.currentTurnIndex = 0;
  }

  getCurrentTurn() {
    return this.turnOrder[this.currentTurnIndex];
  }

  advanceTurn() {
    this.currentTurnIndex = (this.currentTurnIndex + 1) % this.turnOrder.length;

    // Reset player guard at start of their next turn
    if (this.getCurrentTurn().type === 'player') {
      if (this.player.isCountering && !this.player.isGuarding) {
        this.player.isCountering = false;
      }
    }
  }

  playerAction(actionKey) {
    const action = ACTIONS[actionKey];
    if (!action) return { success: false, message: 'Invalid action' };

    if (actionKey === 'potion') {
      if (this.player.potions <= 0) {
        return { success: false, message: 'No potions left!' };
      }
      this.player.potions--;
      const healAmount = Math.floor(this.player.maxHp * 0.5);
      this.player.hp = Math.min(this.player.maxHp, this.player.hp + healAmount);
      this.log(`Used Potion. Recovered ${healAmount} HP.`);
      this.advanceTurn();
      return { success: true, message: 'Healed!', data: { healAmount } };
    }

    if (this.player.ap < action.cost) {
      return { success: false, message: `Need ${action.cost} AP!` };
    }

    if (actionKey === 'guard') {
      this.player.isGuarding = true;
      this.player.isCountering = false;
      this.log('You raise your guard.');
      this.advanceTurn();
      return { success: true, message: 'Guard up' };
    }

    if (actionKey === 'counter') {
      this.player.isCountering = true;
      this.player.ap -= action.cost;
      this.log('You prepare to counter.');
      this.advanceTurn();
      return { success: true, message: 'Counter ready' };
    }

    // Attack actions
    this.player.ap -= action.cost;
    let damage = action.damage;

    // Holy Strike bonus vs undead
    if (action.type === 'holy') {
      damage *= 2;
      this.log('Holy energy blasts through!');
    }

    this.currentEnemy.hp -= damage;
    this.log(`You ${actionKey.replace(/([A-Z])/g, ' $1').toLowerCase().trim()} for ${damage} damage!`);

    if (this.currentEnemy.hp <= 0) {
      this.currentEnemy.hp = 0;
      this.log(`${this.currentEnemy.name} defeated!`);
      return this.checkLevelComplete();
    }

    this.advanceTurn();
    return { success: true, message: `Dealt ${damage} damage`, data: { damage, enemyHp: this.currentEnemy.hp } };
  }

  enemyTurn() {
    if (this.currentEnemy.hp <= 0) return;

    const enemy = this.currentEnemy;
    let damage = enemy.damage;

    // Check if player is countering
    if (this.player.isCountering) {
      damage *= 0.5;
      this.log(`Counter! Reduced incoming damage to ${damage}.`);
      this.player.isCountering = false;
    }

    // Guard reduction
    if (this.player.isGuarding) {
      damage *= 0.4;
      this.log(`Guard absorbs attack. Reduced to ${damage}.`);
    }

    // Ghost phase through guard
    if (enemy.special === 'phase' && this.player.isGuarding && Math.random() < 0.5) {
      damage = enemy.damage;
      this.log('Ghost phases through your guard!');
    }

    // Zombie poison
    if (enemy.special === 'poison' && Math.random() < 0.3) {
      this.player.hp -= 5;
      this.log('Poison! -5 HP over time.');
    }

    this.player.hp -= damage;
    this.log(`${enemy.name} attacks for ${damage} damage!`);

    if (this.player.hp <= 0) {
      this.player.hp = 0;
      this.gameOver = true;
      this.log('You died... Permadeath.');
      return { gameOver: true, message: 'GAME OVER' };
    }

    this.player.isGuarding = false;
    this.advanceTurn();
  }

  checkLevelComplete() {
    if (this.currentEnemy.hp <= 0) {
      if (this.level < 3) {
        const nextLevel = this.level + 1;
        return { levelComplete: true, nextLevel, message: `Level ${this.level} clear!` };
      } else {
        // Spawn Death Knight boss
        this.currentEnemy = { ...ENEMIES.deathKnight };
        this.calculateTurnOrder();
        this.log('Death Knight appears! (Boss)');
        return { message: 'Death Knight boss fight!' };
      }
    }
    return { message: 'Continue fighting' };
  }

  checkVictory() {
    if (this.currentEnemy && this.currentEnemy.name === 'Death Knight' && this.currentEnemy.hp <= 0) {
      this.won = true;
      this.gameOver = true;
      return { won: true, message: 'DEMO COMPLETE! You conquered the dungeon!' };
    }
    return null;
  }
}