// Character SVG models for Meta Ray-Ban Fighter

export const CHARACTERS = {
  // Heroes
  warrior: {
    name: 'Warrior',
    svg: `
      <svg viewBox="0 0 80 120" class="warrior-sprite">
        <!-- Helmet -->
        <rect x="28" y="5" width="24" height="20" fill="#ffd700" stroke="#d4af37" stroke-width="2"/>
        <!-- Plume -->
        <path d="M40 5 Q50 -8 55 5" fill="#dc143c" stroke="#8b0000" stroke-width="1"/>
        <!-- Face -->
        <rect x="30" y="12" width="20" height="10" fill="#f5deb3"/>
        <!-- Eyes -->
        <circle cx="35" cy="17" r="2" fill="#4169e1"/>
        <circle cx="45" cy="17" r="2" fill="#4169e1"/>
        <!-- Body armor -->
        <rect x="25" y="28" width="30" height="40" fill="#c0c0c0" stroke="#a0a0a0" stroke-width="2"/>
        <!-- Armor details -->
        <rect x="32" y="32" width="16" height="15" fill="#d4d4d4" stroke="#b0b0b0" stroke-width="1"/>
        <!-- Sword (right hand) -->
        <rect x="55" y="35" width="4" height="45" fill="#c0c0c0" stroke="#a0a0a0" stroke-width="1"/>
        <rect x="53" y="30" width="8" height="8" fill="#8b4513" stroke="#5a2d0a" stroke-width="1"/>
        <polygon points="57,75 52,85 62,85" fill="#c0c0c0"/>
        <!-- Shield (left hand) -->
        <rect x="10" y="35" width="10" height="35" fill="#c0c0c0" stroke="#a0a0a0" stroke-width="2"/>
        <circle cx="15" cy="52" r="4" fill="#dc143c" stroke="#8b0000" stroke-width="1"/>
        <!-- Legs -->
        <rect x="30" y="68" width="8" height="40" fill="#c0c0c0" stroke="#a0a0a0" stroke-width="1"/>
        <rect x="42" y="68" width="8" height="40" fill="#c0c0c0" stroke="#a0a0a0" stroke-width="1"/>
        <!-- Cape -->
        <path d="M25 28 Q20 50 25 70 L30 70 L30 28 Z" fill="#dc143c" opacity="0.7"/>
      </svg>
    `
  },
  hunter: {
    name: 'Hunter',
    svg: `
      <svg viewBox="0 0 80 120" class="hunter-sprite">
        <!-- Hood -->
        <ellipse cx="40" cy="18" rx="18" ry="20" fill="#2e8b57" stroke="#228b22" stroke-width="2"/>
        <!-- Face opening -->
        <ellipse cx="40" cy="22" rx="10" ry="12" fill="#f5deb3"/>
        <!-- Eyes -->
        <circle cx="35" cy="20" r="2" fill="#228b22"/>
        <circle cx="45" cy="20" r="2" fill="#228b22"/>
        <!-- Body (leather armor) -->
        <rect x="28" y="38" width="24" height="35" fill="#8b4513" stroke="#5a2d0a" stroke-width="1"/>
        <!-- Quiver -->
        <rect x="52" y="40" width="8" height="25" fill="#8b4513" stroke="#5a2d0a" stroke-width="1"/>
        <line x1="54" y1="42" x2="54" y2="62" stroke="#deb887" stroke-width="1"/>
        <line x1="56" y1="42" x2="56" y2="62" stroke="#deb887" stroke-width="1"/>
        <line x1="58" y1="42" x2="58" y2="62" stroke="#deb887" stroke-width="1"/>
        <!-- Crossbow (right hand) -->
        <rect x="55" y="50" width="25" height="5" fill="#8b4513" stroke="#5a2d0a" stroke-width="1"/>
        <line x1="78" y1="45" x2="78" y2="60" stroke="#deb887" stroke-width="2"/>
        <!-- Dagger (left hand) -->
        <rect x="8" y="50" width="12" height="3" fill="#c0c0c0" stroke="#a0a0a0" stroke-width="1"/>
        <polygon points="8,51 2,52 8,53" fill="#c0c0c0"/>
        <!-- Legs -->
        <rect x="30" y="73" width="8" height="35" fill="#8b4513" stroke="#5a2d0a" stroke-width="1"/>
        <rect x="42" y="73" width="8" height="35" fill="#8b4513" stroke="#5a2d0a" stroke-width="1"/>
        <!-- Boots -->
        <rect x="28" y="100" width="12" height="8" fill="#5a2d0a"/>
        <rect x="40" y="100" width="12" height="8" fill="#5a2d0a"/>
      </svg>
    `
  },
  mage: {
    name: 'Mage',
    svg: `
      <svg viewBox="0 0 80 120" class="mage-sprite">
        <!-- Hat -->
        <path d="M25 25 L40 5 L55 25 Z" fill="#4169e1" stroke="#1e3a8a" stroke-width="2"/>
        <ellipse cx="40" cy="25" rx="18" ry="6" fill="#4169e1" stroke="#1e3a8a" stroke-width="2"/>
        <!-- Face -->
        <ellipse cx="40" cy="35" rx="12" ry="14" fill="#f5deb3"/>
        <!-- Eyes -->
        <circle cx="35" cy="33" r="2" fill="#4169e1"/>
        <circle cx="45" cy="33" r="2" fill="#4169e1"/>
        <!-- Beard -->
        <path d="M32 42 Q40 50 48 42" fill="#e0e0e0" stroke="#c0c0c0" stroke-width="1"/>
        <!-- Robe -->
        <path d="M28 48 L20 100 L60 100 L52 48 Z" fill="#4169e1" stroke="#1e3a8a" stroke-width="2"/>
        <!-- Robe details -->
        <line x1="40" y1="48" x2="40" y2="100" stroke="#1e3a8a" stroke-width="1"/>
        <!-- Staff (right hand) -->
        <rect x="58" y="30" width="4" height="70" fill="#8b4513" stroke="#5a2d0a" stroke-width="1"/>
        <circle cx="60" cy="25" r="6" fill="#4169e1" stroke="#1e3a8a" stroke-width="1"/>
        <circle cx="60" cy="25" r="3" fill="#87ceeb"/>
        <!-- Magic orb glow -->
        <ellipse cx="60" cy="25" rx="10" ry="10" fill="none" stroke="#87ceeb" stroke-width="1" opacity="0.5"/>
        <!-- Left hand with spell -->
        <circle cx="20" cy="60" r="5" fill="#87ceeb" opacity="0.8"/>
        <ellipse cx="20" cy="60" rx="8" ry="8" fill="none" stroke="#87ceeb" stroke-width="1" opacity="0.5"/>
      </svg>
    `
  },
  // Enemies
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