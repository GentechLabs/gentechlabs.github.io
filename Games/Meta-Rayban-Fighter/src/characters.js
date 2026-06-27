// Character SVG models for Meta Ray-Ban Fighter

export const CHARACTERS = {
  skeleton: {
    name: 'Skeleton',
    svg: `
      <svg viewBox="0 0 80 120" class="skeleton-sprite">
        <!-- Skull -->
        <ellipse cx="40" cy="20" rx="15" ry="18" fill="#f5f5dc" stroke="#d3d3d3" stroke-width="2"/>
        <!-- Eye sockets -->
        <ellipse cx="33" cy="18" rx="4" ry="5" fill="#1a1a1a"/>
        <ellipse cx="47" cy="18" rx="4" ry="5" fill="#1a1a1a"/>
        <!-- Nose hole -->
        <path d="M40 22 L38 28 L42 28 Z" fill="#1a1a1a"/>
        <!-- Teeth -->
        <line x1="33" y1="32" x2="47" y2="32" stroke="#1a1a1a" stroke-width="1"/>
        <!-- Ribs -->
        <line x1="25" y1="45" x2="55" y2="45" stroke="#f5f5dc" stroke-width="3"/>
        <line x1="25" y1="52" x2="55" y2="52" stroke="#f5f5dc" stroke-width="3"/>
        <line x1="25" y1="59" x2="55" y2="59" stroke="#f5f5dc" stroke-width="3"/>
        <!-- Spine -->
        <line x1="40" y1="40" x2="40" y2="70" stroke="#f5f5dc" stroke-width="3"/>
        <!-- Arms -->
        <line x1="25" y1="45" x2="10" y2="70" stroke="#f5f5dc" stroke-width="2"/>
        <line x1="55" y1="45" x2="70" y2="70" stroke="#f5f5dc" stroke-width="2"/>
        <!-- Legs -->
        <line x1="35" y1="70" x2="30" y2="110" stroke="#f5f5dc" stroke-width="2"/>
        <line x1="45" y1="70" x2="50" y2="110" stroke="#f5f5dc" stroke-width="2"/>
      </svg>
    `
  },
  zombie: {
    name: 'Zombie',
    svg: `
      <svg viewBox="0 0 80 120" class="zombie-sprite">
        <!-- Head -->
        <ellipse cx="40" cy="20" rx="16" ry="19" fill="#6b8e23" stroke="#4a6a1a" stroke-width="2"/>
        <!-- Eye (one missing) -->
        <ellipse cx="33" cy="18" rx="5" ry="6" fill="#2d4a0c"/>
        <ellipse cx="48" cy="18" rx="5" ry="6" fill="#1a1a1a"/>
        <!-- Stitched mouth -->
        <path d="M32 32 L48 32" stroke="#1a1a1a" stroke-width="2"/>
        <path d="M35 30 L35 34" stroke="#1a1a1a" stroke-width="1"/>
        <path d="M42 30 L42 34" stroke="#1a1a1a" stroke-width="1"/>
        <path d="M45 30 L45 34" stroke="#1a1a1a" stroke-width="1"/>
        <!-- Body -->
        <rect x="28" y="40" width="24" height="35" fill="#4a6a1a" stroke="#2d4a0c" stroke-width="1"/>
        <!-- Ripped clothes -->
        <path d="M30 42 L35 45 L32 48 L36 51 L30 54" fill="none" stroke="#3a5a1a" stroke-width="2"/>
        <path d="M50 42 L45 45 L48 48 L44 51 L50 54" fill="none" stroke="#3a5a1a" stroke-width="2"/>
        <!-- Arms -->
        <rect x="15" y="42" width="12" height="30" fill="#6b8e23" stroke="#4a6a1a" stroke-width="1"/>
        <rect x="53" y="42" width="12" height="30" fill="#6b8e23" stroke="#4a6a1a" stroke-width="1"/>
        <!-- Legs -->
        <rect x="30" y="75" width="10" height="35" fill="#6b8e23" stroke="#4a6a1a" stroke-width="1"/>
        <rect x="40" y="75" width="10" height="35" fill="#6b8e23" stroke="#4a6a1a" stroke-width="1"/>
      </svg>
    `
  },
  ghost: {
    name: 'Ghost',
    svg: `
      <svg viewBox="0 0 80 120" class="ghost-sprite">
        <!-- Ghost body -->
        <path d="M20 10 Q40 0 60 10 Q70 20 70 40 Q70 60 65 75 Q60 90 55 80 Q50 70 45 80 Q40 90 35 80 Q30 70 25 80 Q20 90 15 75 Q10 60 10 40 Q10 20 20 10" fill="#b0c4de" stroke="#778899" stroke-width="2"/>
        <!-- Eyes -->
        <ellipse cx="32" cy="35" rx="6" ry="8" fill="#1a1a1a"/>
        <ellipse cx="48" cy="35" rx="6" ry="8" fill="#1a1a1a"/>
        <!-- Eye glow -->
        <circle cx="34" cy="33" r="2" fill="#4169e1"/>
        <circle cx="50" cy="33" r="2" fill="#4169e1"/>
        <!-- Mouth -->
        <path d="M35 50 Q40 55 45 50" stroke="#1a1a1a" stroke-width="2" fill="none"/>
        <!-- Eerie glow effect -->
        <ellipse cx="40" cy="50" rx="30" ry="40" fill="none" stroke="#b0c4de" stroke-width="1" opacity="0.3"/>
      </svg>
    `
  },
  deathKnight: {
    name: 'Death Knight',
    svg: `
      <svg viewBox="0 0 80 120" class="death-knight-sprite">
        <!-- Helmet -->
        <rect x="28" y="5" width="24" height="25" fill="#2f2f2f" stroke="#4a4a4a" stroke-width="2"/>
        <!-- Visor -->
        <rect x="30" y="12" width="20" height="8" fill="#1a1a1a"/>
        <!-- Glowing eyes -->
        <rect x="32" y="14" width="4" height="4" fill="#ff0000"/>
        <rect x="44" y="14" width="4" height="4" fill="#ff0000"/>
        <!-- Plume -->
        <path d="M40 5 Q50 -5 55 5 Q60 0 55 10" fill="#8b0000" stroke="#5a0000" stroke-width="1"/>
        <!-- Armor body -->
        <rect x="25" y="30" width="30" height="45" fill="#2f2f2f" stroke="#4a4a4a" stroke-width="2"/>
        <!-- Armor details -->
        <rect x="32" y="35" width="16" height="20" fill="#3a3a3a" stroke="#4a4a4a" stroke-width="1"/>
        <!-- Sword (right arm) -->
        <rect x="55" y="35" width="5" height="40" fill="#c0c0c0" stroke="#a0a0a0" stroke-width="1"/>
        <rect x="53" y="30" width="9" height="8" fill="#8b4513" stroke="#5a2d0a" stroke-width="1"/>
        <!-- Shield (left arm) -->
        <rect x="10" y="35" width="12" height="35" fill="#2f2f2f" stroke="#4a4a4a" stroke-width="2"/>
        <circle cx="16" cy="52" r="6" fill="#8b0000" stroke="#5a0000" stroke-width="1"/>
        <!-- Legs -->
        <rect x="30" y="75" width="10" height="40" fill="#2f2f2f" stroke="#4a4a4a" stroke-width="1"/>
        <rect x="40" y="75" width="10" height="40" fill="#2f2f2f" stroke="#4a4a4a" stroke-width="1"/>
        <!-- Aura -->
        <ellipse cx="40" cy="60" rx="35" ry="50" fill="none" stroke="#8b0000" stroke-width="1" opacity="0.4"/>
      </svg>
    `
  }
};