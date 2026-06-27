// Character SVG models for Meta Ray-Ban Fighter

export const CHARACTERS = {
  player: {
    name: 'Knight',
    svg: `
      <svg viewBox="0 0 80 120" class="knight-sprite">
        <!-- Helmet -->
        <ellipse cx="40" cy="20" rx="12" ry="14" fill="#2c2c2c" stroke="#ffd700" stroke-width="2"/>
        <!-- Visor -->
        <rect x="32" y="18" width="16" height="6" fill="#1a1a1a"/>
        <!-- Torso Armor -->
        <rect x="28" y="35" width="24" height="35" fill="#4a4a4a" stroke="#ffd700" stroke-width="2"/>
        <!-- Shoulders -->
        <circle cx="20" cy="40" r="8" fill="#3a3a3a" stroke="#ffd700" stroke-width="2"/>
        <circle cx="60" cy="40" r="8" fill="#3a3a3a" stroke="#ffd700" stroke-width="2"/>
        <!-- Arms -->
        <rect x="8" y="48" width="12" height="40" fill="#4a4a4a" stroke="#ffd700" stroke-width="1"/>
        <rect x="60" y="48" width="12" height="40" fill="#4a4a4a" stroke="#ffd700" stroke-width="1"/>
        <!-- Sword -->
        <rect x="65" y="45" width="3" height="35" fill="#c0c0c0"/>
        <rect x="63" y="80" width="7" height="12" fill="#8b4513"/>
        <!-- Legs -->
        <rect x="30" y="70" width="8" height="30" fill="#3a3a3a" stroke="#ffd700" stroke-width="1"/>
        <rect x="42" y="70" width="8" height="30" fill="#3a3a3a" stroke="#ffd700" stroke-width="1"/>
        <!-- Shield -->
        <ellipse cx="14" cy="70" rx="10" ry="15" fill="#4a4a4a" stroke="#ffd700" stroke-width="2"/>
        <line x1="14" y1="55" x2="14" y2="85" stroke="#ffd700" stroke-width="1"/>
        <line x1="4" y1="70" x2="24" y2="70" stroke="#ffd700" stroke-width="1"/>
        <!-- Cape -->
        <path d="M28 35 Q15 60 10 100 L50 100 Q45 60 32 35" fill="#8b0000" opacity="0.8"/>
      </svg>
    `
  },
  skeleton: {
    name: 'Skeleton',
    svg: `
      <svg viewBox="0 0 80 120" class="skeleton-sprite">
        <!-- Skull -->
        <ellipse cx="40" cy="18" rx="10" ry="12" fill="#e8e8e8" stroke="#c0c0c0" stroke-width="1"/>
        <!-- Eye sockets -->
        <ellipse cx="35" cy="16" rx="3" ry="4" fill="#1a1a1a"/>
        <ellipse cx="45" cy="16" rx="3" ry="4" fill="#1a1a1a"/>
        <!-- Nose -->
        <path d="M40 18 L38 22 L42 22 Z" fill="#c0c0c0"/>
        <!-- Teeth -->
        <line x1="35" y1="25" x2="45" y2="25" stroke="#1a1a1a" stroke-width="1"/>
        <line x1="38" y1="27" x2="42" y2="27" stroke="#1a1a1a" stroke-width="1"/>
        <!-- Spine -->
        <line x1="40" y1="30" x2="40" y2="75" stroke="#e8e8e8" stroke-width="3"/>
        <!-- Ribcage -->
        <line x1="25" y1="35" x2="55" y2="35" stroke="#e8e8e8" stroke-width="2"/>
        <line x1="23" y1="40" x2="57" y2="40" stroke="#e8e8e8" stroke-width="2"/>
        <line x1="25" y1="45" x2="55" y2="45" stroke="#e8e8e8" stroke-width="2"/>
        <line x1="27" y1="50" x2="53" y2="50" stroke="#e8e8e8" stroke-width="2"/>
        <line x1="29" y1="55" x2="51" y2="55" stroke="#e8e8e8" stroke-width="2"/>
        <!-- Arms -->
        <line x1="25" y1="35" x2="10" y2="65" stroke="#e8e8e8" stroke-width="2"/>
        <line x1="55" y1="35" x2="70" y2="65" stroke="#e8e8e8" stroke-width="2"/>
        <!-- Hands -->
        <circle cx="10" cy="68" r="4" fill="#e8e8e8"/>
        <circle cx="70" cy="68" r="4" fill="#e8e8e8"/>
        <!-- Legs -->
        <line x1="35" y1="75" x2="30" y2="115" stroke="#e8e8e8" stroke-width="2"/>
        <line x1="45" y1="75" x2="50" y2="115" stroke="#e8e8e8" stroke-width="2"/>
        <!-- Feet -->
        <ellipse cx="30" cy="118" rx="5" ry="3" fill="#e8e8e8"/>
        <ellipse cx="50" cy="118" rx="5" ry="3" fill="#e8e8e8"/>
      </svg>
    `
  },
  zombie: {
    name: 'Zombie',
    svg: `
      <svg viewBox="0 0 80 120" class="zombie-sprite">
        <!-- Head -->
        <ellipse cx="40" cy="20" rx="11" ry="13" fill="#5a6a5a" stroke="#3a4a3a" stroke-width="2"/>
        <!-- Eye (one) -->
        <ellipse cx="45" cy="18" rx="4" ry="3" fill="#ff0000"/>
        <!-- Missing eye socket -->
        <ellipse cx="35" cy="18" rx="4" ry="3" fill="#2a2a2a"/>
        <!-- Nose -->
        <path d="M40 22 L37 26 L43 26 Z" fill="#4a5a4a"/>
        <!-- Mouth (open) -->
        <ellipse cx="40" cy="28" rx="5" ry="3" fill="#1a1a1a"/>
        <!-- Teeth -->
        <line x1="36" y1="28" x2="38" y2="31" stroke="#e8e8e8" stroke-width="1"/>
        <line x1="40" y1="28" x2="40" y2="31" stroke="#e8e8e8" stroke-width="1"/>
        <line x1="44" y1="28" x2="42" y2="31" stroke="#e8e8e8" stroke-width="1"/>
        <!-- Body (tattered) -->
        <path d="M28 35 L24 80 L30 85 L32 50 L40 50 L48 50 L50 85 L56 80 L52 35 Z" fill="#4a4a4a" stroke="#2a2a2a" stroke-width="1"/>
        <!-- Arms (ragged) -->
        <path d="M28 40 L15 70 L20 75 L30 55" fill="#5a6a5a" stroke="#3a4a3a" stroke-width="1"/>
        <path d="M52 40 L65 70 L60 75 L50 55" fill="#5a6a5a" stroke="#3a4a3a" stroke-width="1"/>
        <!-- Hands -->
        <ellipse cx="17" cy="73" rx="5" ry="4" fill="#5a6a5a"/>
        <ellipse cx="63" cy="73" rx="5" ry="4" fill="#5a6a5a"/>
        <!-- Legs -->
        <rect x="30" y="80" width="8" height="35" fill="#4a4a4a" stroke="#2a2a2a" stroke-width="1"/>
        <rect x="42" y="80" width="8" height="35" fill="#4a4a4a" stroke="#2a2a2a" stroke-width="1"/>
        <!-- Tattered clothes -->
        <path d="M28 45 Q20 60 18 75 L30 70 Z" fill="#3a3a3a" opacity="0.7"/>
        <path d="M52 45 Q60 60 62 75 L50 70 Z" fill="#3a3a3a" opacity="0.7"/>
      </svg>
    `
  },
  ghost: {
    name: 'Ghost',
    svg: `
      <svg viewBox="0 0 80 120" class="ghost-sprite">
        <!-- Head -->
        <ellipse cx="40" cy="25" rx="15" ry="18" fill="#e8e8ff" stroke="#c0c0ff" stroke-width="2" opacity="0.8"/>
        <!-- Eyes -->
        <ellipse cx="34" cy="22" rx="4" ry="5" fill="#1a1a2e"/>
        <ellipse cx="46" cy="22" rx="4" ry="5" fill="#1a1a2e"/>
        <!-- Mouth -->
        <ellipse cx="40" cy="32" rx="5" ry="3" fill="#1a1a2e"/>
        <!-- Body (flowing) -->
        <path d="M25 40 Q15 70 20 100 L30 95 Q25 70 30 50 L40 50 L50 50 Q55 70 50 95 L60 100 Q65 70 55 40 Z" fill="#e8e8ff" stroke="#c0c0ff" stroke-width="1" opacity="0.7"/>
        <!-- Arms (ethereal) -->
        <path d="M28 50 Q15 60 12 80 Q18 75 28 65" fill="#e8e8ff" stroke="#c0c0ff" stroke-width="1" opacity="0.5"/>
        <path d="M52 50 Q65 60 68 80 Q62 75 52 65" fill="#e8e8ff" stroke="#c0c0ff" stroke-width="1" opacity="0.5"/>
        <!-- Hands -->
        <ellipse cx="14" cy="82" rx="5" ry="3" fill="#e8e8ff" opacity="0.6"/>
        <ellipse cx="66" cy="82" rx="5" ry="3" fill="#e8e8ff" opacity="0.6"/>
        <!-- Tail effect -->
        <path d="M20 100 Q18 110 25 115 L55 115 Q62 110 60 100" fill="none" stroke="#e8e8ff" stroke-width="2" opacity="0.5"/>
      </svg>
    `
  }
};

export function getCharacterSVG(characterKey) {
  return CHARACTERS[characterKey]?.svg || '';
}