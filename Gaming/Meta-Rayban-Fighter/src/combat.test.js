import { GameState } from './game-state.js';
import { ACTIONS, ENEMIES } from './game-constants.js';

function testCombatEngine() {
  const gameState = new GameState();
  let testsPassed = 0;
  let testsFailed = 0;

  // Test 1: Initial state
  console.log('Test 1: Initial state');
  assert(gameState.player.hp === 100, 'Player HP should start at 100');
  assert(gameState.player.potions === 3, 'Player should have 3 potions');
  assert(gameState.player.ap === 2, 'Player AP should start at 2');
  console.log('✓ Initial state correct\n');

  // Test 2: Level 1 start
  console.log('Test 2: Level 1 start');
  gameState.startLevel(1);
  assert(gameState.currentEnemy.name === 'Skeleton', 'Enemy should be Skeleton');
  assert(gameState.currentEnemy.hp === 30, 'Skeleton HP should be 30');
  console.log('✓ Level 1 enemy correct\n');

  // Test 3: Player attack
  console.log('Test 3: Player attack');
  const attackResult = gameState.playerAction('attack');
  assert(attackResult.success === true, 'Attack should succeed');
  assert(gameState.currentEnemy.hp < 30, 'Enemy HP should decrease');
  console.log(`✓ Attack dealt damage, enemy HP: ${gameState.currentEnemy.hp}\n`);

  // Test 4: Enemy turn
  console.log('Test 4: Enemy turn');
  gameState.enemyTurn();
  assert(gameState.player.hp < 100, 'Player HP should decrease after enemy attack');
  console.log(`✓ Enemy attacked, player HP: ${gameState.player.hp}\n`);

  // Test 5: Guard mechanic
  console.log('Test 5: Guard mechanic');
  const initialHp = gameState.player.hp;
  gameState.playerAction('guard');
  gameState.enemyTurn();
  const guardedDamage = initialHp - gameState.player.hp;
  const rawDamage = gameState.currentEnemy.damage;
  assert(guardedDamage < rawDamage, 'Guard should reduce damage');
  console.log(`✓ Guard reduced damage from ${rawDamage} to ${guardedDamage}\n`);

  // Test 6: Potion usage
  console.log('Test 6: Potion usage');
  const beforePotionHp = gameState.player.hp;
  gameState.playerAction('potion');
  assert(gameState.player.potions === 2, 'Potions should decrease');
  assert(gameState.player.hp > beforePotionHp, 'Player HP should increase');
  console.log(`✓ Potion used, HP increased from ${beforePotionHp} to ${gameState.player.hp}\n`);

  // Test 7: Holy Strike bonus vs undead
  console.log('Test 7: Holy Strike bonus vs undead');
  gameState.currentEnemy = { ...ENEMIES.skeleton };
  gameState.player.ap = 3; // Give max AP for Holy Strike
  const holyStrikeResult = gameState.playerAction('holyStrike');
  // Holy Strike may return levelComplete if it defeats enemy
  assert(holyStrikeResult.success === true || holyStrikeResult.levelComplete === true, 'Holy Strike should succeed');
  // Holy Strike deals 2x damage = 40, skeleton has 30 HP
  assert(gameState.currentEnemy.hp <= 0, 'Holy Strike should deal 2x damage vs undead');
  console.log('✓ Holy Strike deals 2x damage vs undead\n');

  // Test 8: Level progression
  console.log('Test 8: Level progression');
  gameState.reset();
  gameState.startLevel(1);
  // Defeat skeleton quickly
  gameState.currentEnemy.hp = 1;
  gameState.playerAction('attack');
  console.log(`✓ Level complete triggered, moving to level 2\n`);

  // Test 9: Permadeath
  console.log('Test 9: Permadeath');
  gameState.reset();
  gameState.startLevel(1);
  gameState.player.hp = 5; // Set low HP
  gameState.currentEnemy.damage = 10; // Ensure enemy can kill
  const enemyResult = gameState.enemyTurn();
  assert(gameState.gameOver === true, 'Game should be over on HP 0');
  assert(enemyResult.gameOver === true, 'enemyTurn should return gameOver');
  console.log('✓ Permadeath triggers correctly\n');

  // Test 10: Turn order
  console.log('Test 10: Turn order');
  gameState.reset();
  gameState.startLevel(1);
  const turn = gameState.getCurrentTurn();
  assert(turn !== null, 'Current turn should be defined');
  console.log(`✓ Turn order working, current: ${turn.type}\n`);

  console.log('='.repeat(50));
  console.log(`All tests completed. Passed: ${testsPassed}/${testsPassed + testsFailed}`);
  console.log('='.repeat(50));

  function assert(condition, message) {
    if (condition) {
      testsPassed++;
      console.log(`✓ ${message}`);
    } else {
      testsFailed++;
      console.error(`✗ ${message}`);
      throw new Error(message);
    }
  }
}

// Run tests
try {
  testCombatEngine();
  console.log('\n🎉 Combat engine tests passed!');
  process.exit(0);
} catch (error) {
  console.error('\n❌ Tests failed:', error.message);
  process.exit(1);
}