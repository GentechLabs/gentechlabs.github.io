import { GameState } from './game-state.js';
import { ACTIONS, ENEMIES } from './game-constants.js';

const gameState = new GameState();
gameState.startLevel(1);
gameState.player.ap = 3;
console.log('Player AP:', gameState.player.ap);
console.log('Current enemy:', gameState.currentEnemy);
console.log('ACTIONS.holyStrike:', ACTIONS.holyStrike);
console.log('Current turn:', gameState.getCurrentTurn());

const result = gameState.playerAction('holyStrike');
console.log('Result:', result);
console.log('Enemy HP after holy strike:', gameState.currentEnemy.hp);