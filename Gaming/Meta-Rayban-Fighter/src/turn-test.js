// Quick test to verify turn system
import { GameState } from './game-state.js';
import { ENEMIES } from './game-constants.js';

const gameState = new GameState();
gameState.startLevel(1);

console.log('=== Turn System Test ===\n');
console.log('Initial state:');
console.log(`- Player HP: ${gameState.player.hp}`);
console.log(`- Enemy: ${gameState.currentEnemy.name} (${gameState.currentEnemy.hp} HP)`);
console.log(`- Turn: ${gameState.getCurrentTurn().type}\n`);

// Player attacks
console.log('Player attacks...');
const attackResult = gameState.playerAction('attack');
console.log(`- Result: ${JSON.stringify(attackResult)}`);
console.log(`- Player HP: ${gameState.player.hp}`);
console.log(`- Enemy HP: ${gameState.currentEnemy.hp}`);
console.log(`- Turn: ${gameState.getCurrentTurn().type}\n`);

// Enemy should attack automatically now
console.log('Enemy turn (should be automatic)...');
gameState.enemyTurn();
console.log(`- Player HP: ${gameState.player.hp}`);
console.log(`- Enemy HP: ${gameState.currentEnemy.hp}`);
console.log(`- Turn: ${gameState.getCurrentTurn().type}\n`);

// Player attacks again
console.log('Player attacks again...');
gameState.playerAction('attack');
console.log(`- Player HP: ${gameState.player.hp}`);
console.log(`- Enemy HP: ${gameState.currentEnemy.hp}`);
console.log(`- Turn: ${gameState.getCurrentTurn().type}\n`);

console.log('=== Test Complete ===');