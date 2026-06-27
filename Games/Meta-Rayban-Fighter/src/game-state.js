import { CLASSES, CLASS_COLORS } from './classes.js';
import { ENEMIES } from './game-constants.js';

export class PartyMember {
  constructor(classKey, name) {
    const classData = CLASSES[classKey];
    this.classKey = classKey;
    this.name = name || classData.name;
    this.role = classData.role;
    this.position = classData.position;
    this.abilities = classData.abilities;
    this.color = CLASS_COLORS[classKey];
    
    this.maxHp = classData.baseStats.maxHp;
    this.hp = classData.baseStats.maxHp;
    this.maxAp = 2;
    this.ap = 2;
    this.damage = classData.baseStats.damage;
    this.speed = classData.baseStats.speed;
    this.dodge = classData.baseStats.dodge;
    this.protection = classData.baseStats.protection;
    
    this.isAlive = true;
    this.buffs = [];
  }

  takeDamage(damage, isPhysical = true) {
    if (!this.isAlive) return 0;

    let actualDamage = damage;
    
    if (isPhysical && this.protection > 0) {
      actualDamage = Math.max(0, damage - this.protection);
      console.log(`${this.name} blocked ${damage - actualDamage} damage`);
    }

    this.hp = Math.max(0, this.hp - actualDamage);
    
    if (this.hp <= 0) {
      this.isAlive = false;
      this.hp = 0;
    }

    return actualDamage;
  }

  heal(amount) {
    if (!this.isAlive) return 0;
    this.hp = Math.min(this.maxHp, this.hp + amount);
    return amount;
  }

  useAbility(abilityKey) {
    const ability = this.abilities[abilityKey];
    if (!ability) {
      console.error(`Ability ${abilityKey} not found for ${this.name}`);
      return null;
    }

    if (this.ap < ability.cost) {
      console.error(`Not enough AP for ${ability.name}`);
      return null;
    }

    this.ap -= ability.cost;
    return { ...ability, classKey: this.classKey, userName: this.name };
  }

  resetAp() {
    this.ap = this.maxAp;
  }
}

export class GameState {
  constructor() {
    this.party = [];
    this.currentEnemy = null;
    this.level = 1;
    this.maxLevel = 3;
    this.gameOver = false;
    this.combatLog = [];
    this.potions = 3;
    this.turnOrder = [];
    this.currentTurnIndex = 0;
    this.enemyBuffs = [];
  }

  initParty(members = ['warrior', 'hunter', 'mage']) {
    this.party = members.map((classKey, index) => {
      const names = ['Sir Galahad', 'Aria Swiftarrow', 'Elara Moonweaver'];
      return new PartyMember(classKey, names[index]);
    });
    this.log(`Party formed: ${this.party.map(m => m.name).join(', ')}`);
  }

  reset() {
    this.party = [];
    this.currentEnemy = null;
    this.level = 1;
    this.gameOver = false;
    this.combatLog = [];
    this.potions = 3;
    this.turnOrder = [];
    this.currentTurnIndex = 0;
    this.enemyBuffs = [];
  }

  log(message) {
    this.combatLog.push(message);
    console.log(message);
  }

  startLevel(levelNum) {
    this.level = levelNum;
    this.enemyBuffs = [];

    const enemyKeys = ['skeleton', 'zombie', 'ghost', 'deathKnight'];
    const enemyKey = levelNum <= 3 ? enemyKeys[levelNum - 1] : 'deathKnight';
    const baseEnemy = ENEMIES[enemyKey] || ENEMIES.skeleton;

    this.currentEnemy = {
      ...baseEnemy,
      hp: baseEnemy.hp + (levelNum - 1) * 10,
      maxHp: baseEnemy.maxHp + (levelNum - 1) * 10,
      damage: baseEnemy.damage + (levelNum - 1) * 3,
      stunned: 0,
      forcedTarget: null,
      damageTakenBonus: 0
    };

    this.turnOrder = this.buildTurnOrder();
    this.currentTurnIndex = 0;
    this.log(`Level ${levelNum}: ${this.currentEnemy.name} appears!`);
    this.log(`HP: ${this.currentEnemy.hp} | Damage: ${this.currentEnemy.damage}`);
  }

  buildTurnOrder() {
    const livingParty = this.party.filter(m => m.isAlive);
    const turns = [];

    livingParty.forEach(member => {
      turns.push({
        type: 'player',
        member: member,
        speed: member.speed,
        name: member.name
      });
    });

    if (this.currentEnemy && this.currentEnemy.hp > 0 && this.currentEnemy.stunned <= 0) {
      turns.push({
        type: 'enemy',
        speed: this.currentEnemy.speed,
        name: this.currentEnemy.name
      });
    }

    return turns.sort((a, b) => b.speed - a.speed);
  }

  getCurrentTurn() {
    return this.turnOrder[this.currentTurnIndex];
  }

  isPartyAlive() {
    return this.party.some(m => m.isAlive);
  }

  playerAction(member, abilityKey) {
    const ability = member.useAbility(abilityKey);
    if (!ability) {
      return { success: false, message: 'Cannot use ability' };
    }

    const enemy = this.currentEnemy;
    let result = { damage: 0, heal: 0, message: '', effects: [] };

    if (ability.type === 'heal' && ability.target === 'ally') {
      const lowestHpMember = this.party
        .filter(m => m.isAlive)
        .sort((a, b) => (a.hp / a.maxHp) - (b.hp / b.maxHp))[0];
      
      if (lowestHpMember) {
        const healAmount = lowestHpMember.heal(ability.heal);
        result.heal = healAmount;
        result.message = `${member.name} healed ${lowestHpMember.name} for ${healAmount} HP`;
        this.log(result.message);
      }
    } else if (ability.type === 'buff' && ability.target === 'ally') {
      const lowestHpMember = this.party
        .filter(m => m.isAlive)
        .sort((a, b) => (a.hp / a.maxHp) - (b.hp / b.maxHp))[0];
      
      if (lowestHpMember && ability.effect) {
        lowestHpMember.protection += ability.effect.protection;
        lowestHpMember.buffs.push({
          name: ability.name,
          effect: ability.effect,
          duration: ability.effect.duration
        });
        result.message = `${member.name} shielded ${lowestHpMember.name}`;
        this.log(result.message);
      }
    } else if (ability.type === 'cc' && ability.effect?.stun) {
      this.currentEnemy.stunned = ability.effect.stun;
      result.message = `${member.name} stunned the enemy!`;
      this.log(result.message);
      result.effects.push({ type: 'stun', duration: ability.effect.stun });
    } else if (ability.type === 'debuff') {
      if (ability.effect?.forcedTarget) {
        this.currentEnemy.forcedTarget = member;
        result.message = `${member.name} taunted the enemy!`;
        this.log(result.message);
      }
      if (ability.effect?.damageTaken) {
        this.currentEnemy.damageTakenBonus = ability.effect.damageTaken;
        result.message = `${member.name} marked the enemy!`;
        this.log(result.message);
      }
      if (ability.effect?.stun) {
        this.currentEnemy.stunned = ability.effect.stun;
        result.message = `${member.name} trapped the enemy!`;
        this.log(result.message);
      }
    } else {
      let damage = ability.damage || member.damage;
      if (ability.hits) {
        damage *= ability.hits;
      }
      
      if (ability.type === 'magical' || member.classKey === 'mage') {
        damage *= 2;
      }

      if (ability.critBonus) {
        const critRoll = Math.random() * 100;
        if (critRoll < ability.critBonus + member.dodge) {
          damage *= 2;
          result.message = `CRITICAL HIT! ${member.name}'s ${ability.name} dealt ${damage} damage!`;
        } else {
          result.message = `${member.name} used ${ability.name}: ${damage} damage`;
        }
      } else {
        result.message = `${member.name} used ${ability.name}: ${damage} damage`;
      }

      if (this.currentEnemy.damageTakenBonus > 0) {
        damage = Math.floor(damage * (1 + this.currentEnemy.damageTakenBonus / 100));
        result.message += ` (marked: +${this.currentEnemy.damageTakenBonus}%)`;
      }

      this.currentEnemy.hp -= damage;
      result.damage = damage;
      this.log(result.message);

      if (this.currentEnemy.hp <= 0) {
        this.log(`${this.currentEnemy.name} has been defeated!`);
      }
    }

    return { success: true, ...result };
  }

  usePotion(targetMember) {
    if (this.potions <= 0) {
      return { success: false, message: 'No potions left' };
    }

    if (!targetMember || !targetMember.isAlive) {
      return { success: false, message: 'Invalid target' };
    }

    const healAmount = Math.floor(targetMember.maxHp * 0.5);
    targetMember.heal(healAmount);
    this.potions--;
    this.log(`${targetMember.name} used potion: +${healAmount} HP`);
    this.log(`Potions remaining: ${this.potions}`);

    return { success: true, heal: healAmount, target: targetMember.name };
  }

  enemyTurn() {
    if (!this.currentEnemy || this.currentEnemy.hp <= 0) return 0;

    const enemy = this.currentEnemy;
    let damage = enemy.damage;

    const livingParty = this.party.filter(m => m.isAlive);
    if (livingParty.length === 0) return 0;

    let target = enemy.forcedTarget;
    if (!target || !target.isAlive) {
      target = livingParty[Math.floor(Math.random() * livingParty.length)];
    }

    const actualDamage = target.takeDamage(damage);
    this.log(`${enemy.name} attacked ${target.name}: ${actualDamage} damage`);

    if (!this.isPartyAlive()) {
      this.gameOver = true;
      this.log('💀 GAME OVER - Your party has fallen!');
    }

    return actualDamage;
  }

  advanceTurn() {
    this.currentTurnIndex = (this.currentTurnIndex + 1) % this.turnOrder.length;

    const currentTurn = this.getCurrentTurn();
    if (currentTurn.type === 'player') {
      currentTurn.member.resetAp();
    }

    if (this.currentEnemy) {
      if (this.currentEnemy.stunned > 0) {
        this.currentEnemy.stunned--;
        this.log(`${this.currentEnemy.name} is stunned!`);
      }
      if (this.currentEnemy.forcedTarget) {
        this.currentEnemy.forcedTarget = null;
      }
      if (this.currentEnemy.damageTakenBonus > 0) {
        this.currentEnemy.damageTakenBonus = 0;
      }
    }

    this.party.forEach(member => {
      member.buffs = member.buffs.filter(buff => {
        buff.duration--;
        if (buff.duration <= 0) {
          if (buff.effect.protection) {
            member.protection -= buff.effect.protection;
          }
          return false;
        }
        return true;
      });
    });
  }

  checkVictory() {
    if (this.currentEnemy.hp <= 0) {
      if (this.level < this.maxLevel) {
        const nextLevel = this.level + 1;
        return {
          won: false,
          nextLevel,
          message: `Victory! Continue to Level ${nextLevel}`
        };
      } else {
        return { won: true, message: '🏆 Victory! You conquered the dungeon!' };
      }
    }
    return null;
  }

  checkGameOver() {
    if (!this.isPartyAlive()) {
      return { gameOver: true, message: '💀 Your party has fallen!' };
    }
    return null;
  }
}