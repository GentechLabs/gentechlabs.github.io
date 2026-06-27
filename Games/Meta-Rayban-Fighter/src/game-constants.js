export const ENEMIES = {
  skeleton: {
    name: 'Skeleton',
    hp: 40,
    maxHp: 40,
    speed: 50,
    damage: 12,
    special: null
  },
  zombie: {
    name: 'Zombie',
    hp: 70,
    maxHp: 70,
    speed: 30,
    damage: 15,
    special: 'poison'
  },
  ghost: {
    name: 'Ghost',
    hp: 55,
    maxHp: 55,
    speed: 80,
    damage: 18,
    special: 'phase'
  },
  deathKnight: {
    name: 'Death Knight',
    hp: 120,
    maxHp: 120,
    speed: 65,
    damage: 22,
    special: 'undead'
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