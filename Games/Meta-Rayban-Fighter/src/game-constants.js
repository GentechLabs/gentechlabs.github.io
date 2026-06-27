export const ENEMIES = {
  skeleton: {
    name: 'Skeleton',
    hp: 30,
    maxHp: 30,
    speed: 50,
    damage: 8,
    special: null
  },
  zombie: {
    name: 'Zombie',
    hp: 50,
    maxHp: 50,
    speed: 30,
    damage: 10,
    special: 'poison'
  },
  ghost: {
    name: 'Ghost',
    hp: 40,
    maxHp: 40,
    speed: 70,
    damage: 12,
    special: 'phase'
  },
  deathKnight: {
    name: 'Death Knight',
    hp: 80,
    maxHp: 80,
    speed: 60,
    damage: 15,
    special: 'undead'
  }
};

export const LEVELS = [1, 2, 3];

export const ACTIONS = {
  attack: { name: 'Attack', cost: 0, damage: 10, type: 'physical' },
  guard: { name: 'Guard', cost: 0, damage: 0, type: 'defense' },
  counter: { name: 'Counter', cost: 1, damage: 15, type: 'counter' },
  holyStrike: { name: 'Holy Strike', cost: 2, damage: 20, type: 'holy' },
  smite: { name: 'Smite', cost: 2, damage: 18, type: 'holy' },
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
  'p': 'potion'
};