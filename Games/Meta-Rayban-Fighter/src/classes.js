// Party classes for Darkest Dungeon-style roguelike

export const CLASSES = {
  warrior: {
    name: 'Warrior',
    role: 'tank',
    position: 'front',
    baseStats: {
      maxHp: 120,
      damage: 15,
      speed: 45,
      dodge: 10,
      protection: 15
    },
    abilities: {
      attack: {
        name: 'Slash',
        description: 'Basic sword attack',
        damage: 15,
        cost: 0,
        range: 'melee',
        type: 'physical'
      },
      defend: {
        name: 'Defend',
        description: 'Increase protection for turn',
        cost: 0,
        range: 'self',
        type: 'buff',
        effect: { protection: 20, duration: 1 }
      },
      taunt: {
        name: 'Taunt',
        description: 'Force enemy to target you',
        cost: 1,
        range: 'melee',
        type: 'debuff',
        effect: { forcedTarget: true, duration: 1 }
      },
      cleave: {
        name: 'Cleave',
        description: 'Hit all enemies',
        damage: 10,
        cost: 2,
        range: 'melee',
        type: 'physical',
        aoe: true
      },
      ironWill: {
        name: 'Iron Will',
        description: 'Heal self + increase protection',
        heal: 30,
        cost: 2,
        range: 'self',
        type: 'heal',
        effect: { protection: 10, duration: 1 }
      }
    }
  },
  hunter: {
    name: 'Hunter',
    role: 'damage',
    position: 'flexible',
    baseStats: {
      maxHp: 80,
      damage: 20,
      speed: 60,
      dodge: 20,
      protection: 5
    },
    abilities: {
      shoot: {
        name: 'Shoot',
        description: 'Quick crossbow shot',
        damage: 20,
        cost: 0,
        range: 'ranged',
        type: 'physical'
      },
      aimedShot: {
        name: 'Aimed Shot',
        description: 'High damage, high accuracy',
        damage: 35,
        cost: 1,
        range: 'ranged',
        type: 'physical',
        critBonus: 20
      },
      trap: {
        name: 'Trap',
        description: 'Setup trap (stun next enemy attack)',
        cost: 1,
        range: 'self',
        type: 'debuff',
        effect: { stun: 1 }
      },
      huntersMark: {
        name: 'Hunter\'s Mark',
        description: 'Increase damage taken by enemy',
        cost: 1,
        range: 'ranged',
        type: 'debuff',
        effect: { damageTaken: 25, duration: 2 }
      },
      rapidFire: {
        name: 'Rapid Fire',
        description: '3 shots, moderate damage each',
        damage: 12,
        cost: 2,
        range: 'ranged',
        type: 'physical',
        hits: 3
      }
    }
  },
  mage: {
    name: 'Mage',
    role: 'crowdControl',
    position: 'back',
    baseStats: {
      maxHp: 60,
      damage: 25,
      speed: 50,
      dodge: 15,
      protection: 0
    },
    abilities: {
      fireball: {
        name: 'Fireball',
        description: 'Magical fire damage',
        damage: 25,
        cost: 0,
        range: 'ranged',
        type: 'magical'
      },
      frostNova: {
        name: 'Frost Nova',
        description: 'Freeze enemy (skip turn)',
        cost: 1,
        range: 'ranged',
        type: 'cc',
        effect: { stun: 1 }
      },
      chainLightning: {
        name: 'Chain Lightning',
        description: 'Bounce lightning to all enemies',
        damage: 18,
        cost: 2,
        range: 'ranged',
        type: 'magical',
        aoe: true
      },
      heal: {
        name: 'Heal',
        description: 'Restore ally HP',
        heal: 40,
        cost: 1,
        range: 'ranged',
        type: 'heal',
        target: 'ally'
      },
      shield: {
        name: 'Shield',
        description: 'Protect ally from damage',
        cost: 1,
        range: 'ranged',
        type: 'buff',
        target: 'ally',
        effect: { protection: 25, duration: 1 }
      }
    }
  }
};

export const CLASS_COLORS = {
  warrior: '#8b4513',
  hunter: '#228b22',
  mage: '#4169e1'
};

export const CLASS_ICONS = {
  warrior: '⚔️',
  hunter: '🏹',
  mage: '🔮'
};