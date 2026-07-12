export const ENEMIES = {
  skeleton: {
    name: 'Skeleton',
    hp: 40,
    maxHp: 40,
    speed: 50,
    damage: 12,
    special: 'boneShard',
    abilities: {
      boneShard: {
        name: 'Bone Shard',
        description: 'Throws sharp bones at target',
        damage: 12,
        type: 'physical',
        cooldown: 0,
        effect: 'boneShardEffect'
      },
      skeletalSwipe: {
        name: 'Skeletal Swipe',
        description: 'A slow but deadly claw attack',
        damage: 18,
        type: 'physical',
        cooldown: 2,
        effect: 'swipeEffect'
      }
    }
  },
  zombie: {
    name: 'Zombie',
    hp: 70,
    maxHp: 70,
    speed: 30,
    damage: 15,
    special: 'poison',
    abilities: {
      zombieBite: {
        name: 'Zombie Bite',
        description: 'Bites target, may poison',
        damage: 15,
        type: 'physical',
        cooldown: 0,
        effect: 'biteEffect'
      },
      poisonSpit: {
        name: 'Poison Spit',
        description: 'Spits toxic bile, poisons target',
        damage: 10,
        type: 'poison',
        cooldown: 3,
        effect: 'poisonEffect',
        poisonDamage: 7,
        poisonChance: 0.4
      }
    }
  },
  ghost: {
    name: 'Ghost',
    hp: 55,
    maxHp: 55,
    speed: 80,
    damage: 18,
    special: 'phase',
    abilities: {
      ghostlyTouch: {
        name: 'Ghostly Touch',
        description: 'Cold touch bypasses armor',
        damage: 18,
        type: 'magical',
        cooldown: 0,
        effect: 'touchEffect',
        bypassesArmor: true
      },
      soulDrain: {
        name: 'Soul Drain',
        description: 'Drains HP to heal itself',
        damage: 20,
        type: 'magical',
        cooldown: 2,
        effect: 'drainEffect',
        healPercent: 0.3
      }
    }
  },
  deathKnight: {
    name: 'Death Knight',
    hp: 120,
    maxHp: 120,
    speed: 65,
    damage: 22,
    special: 'undead',
    abilities: {
      deathStrike: {
        name: 'Death Strike',
        description: 'Powerful blade attack with dark magic',
        damage: 22,
        type: 'physical',
        cooldown: 0,
        effect: 'deathStrikeEffect'
      },
      darkBlast: {
        name: 'Dark Blast',
        description: 'Unleashes dark energy, AOE damage',
        damage: 18,
        type: 'magical',
        cooldown: 2,
        effect: 'darkBlastEffect',
        isAOE: true
      },
      raiseDead: {
        name: 'Raise Dead',
        description: 'Summons skeletal reinforcements',
        damage: 0,
        type: 'summon',
        cooldown: 4,
        effect: 'raiseDeadEffect',
        summonDamage: 10
      }
    }
  }
};

export const LEVELS = [1, 2, 3];

export const ACTIONS = {
  attack: { name: 'Attack', cost: 0, damage: 12, type: 'physical' },
  guard: { name: 'Guard', cost: 0, damage: 0, type: 'defense' },
  counter: { name: 'Counter', cost: 1, damage: 18, type: 'counter' },
  holyStrike: { name: 'Holy Strike', cost: 2, damage: 25, type: 'holy' },
  smite: { name: 'Smite', cost: 2, damage: 22, type: 'holy' },
  heavyStrike: { name: 'Heavy Strike', cost: 2, damage: 28, type: 'physical' },
  quickStrike: { name: 'Quick Strike', cost: 1, damage: 15, type: 'physical' },
  taunt: { name: 'Taunt', cost: 1, damage: 5, type: 'mental' },
  potion: { name: 'Potion', cost: 0, damage: 0, type: 'heal' }
};

export const GESTURE_MAP = {
  attack: 'fist_clench',
  guard: 'palm_open_wrist_rotate',
  counter: 'pinch_upward_flick',
  holyStrike: 'double_tap_forward',
  smite: 'double_tap_backward',
  potion: 'peace_sign'
};

export const KEYBOARD_MAP = {
  'a': 'attack',
  'g': 'guard',
  'c': 'counter',
  'h': 'holyStrike',
  's': 'smite',
  'e': 'heavyStrike',
  'q': 'quickStrike',
  't': 'taunt',
  'p': 'potion'
};