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
      slash: {
        name: 'Slash',
        desc: 'Basic sword attack',
        damage: 15,
        apCost: 0,
        type: 'physical'
      },
      defend: {
        name: 'Defend',
        desc: 'Increase protection for turn',
        apCost: 0,
        type: 'defense'
      },
      taunt: {
        name: 'Taunt',
        desc: 'Force enemy to target you',
        apCost: 1,
        type: 'debuff'
      },
      cleave: {
        name: 'Cleave',
        desc: 'Hit all enemies',
        damage: 10,
        apCost: 2,
        type: 'physical'
      },
      ironWill: {
        name: 'Iron Will',
        desc: 'Heal self + increase protection',
        healAmount: 30,
        apCost: 2,
        type: 'heal'
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
        desc: 'Quick crossbow shot',
        damage: 20,
        apCost: 0,
        type: 'physical'
      },
      aimedShot: {
        name: 'Aimed Shot',
        desc: 'High damage, high accuracy',
        damage: 35,
        apCost: 1,
        type: 'physical'
      },
      trap: {
        name: 'Trap',
        desc: 'Setup trap (stun next enemy attack)',
        apCost: 1,
        type: 'debuff'
      },
      huntersMark: {
        name: 'Hunter\'s Mark',
        desc: 'Increase damage taken by enemy',
        apCost: 1,
        type: 'debuff'
      },
      rapidFire: {
        name: 'Rapid Fire',
        desc: '3 shots, moderate damage each',
        damage: 12,
        apCost: 2,
        type: 'physical'
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
        desc: 'Magical fire damage',
        damage: 25,
        apCost: 0,
        type: 'magical'
      },
      frostNova: {
        name: 'Frost Nova',
        desc: 'Freeze enemy (skip turn)',
        apCost: 1,
        type: 'cc'
      },
      chainLightning: {
        name: 'Chain Lightning',
        desc: 'Bounce lightning to all enemies',
        damage: 18,
        apCost: 2,
        type: 'magical'
      },
      heal: {
        name: 'Heal',
        desc: 'Restore ally HP',
        healAmount: 40,
        apCost: 1,
        type: 'heal'
      },
      shield: {
        name: 'Shield',
        desc: 'Protect ally from damage',
        apCost: 1,
        type: 'defense'
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