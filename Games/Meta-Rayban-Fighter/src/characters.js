// Character SVG models for Meta Ray-Ban Fighter - Premium Cool Designs

export const CHARACTERS = {
  // HEROES - Premium Designs with Glowing Effects
  warrior: {
    name: 'Warrior',
    svg: `
      <svg viewBox="0 0 80 120" class="warrior-sprite">
        <!-- Glow Effect -->
        <defs>
          <filter id="warriorGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <!-- Cape with gradient -->
        <path d="M20 30 Q15 50 20 70 L35 70 L35 30 Z" fill="url(#capeGradient)" opacity="0.8"/>
        <defs>
          <linearGradient id="capeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#dc143c;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8b0000;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        <!-- Helmet with wing design -->
        <path d="M28 5 Q40 -5 52 5 L50 20 Q40 18 30 20 Z" fill="url(#helmetGradient)" stroke="#ffd700" stroke-width="2" filter="url(#warriorGlow)"/>
        <defs>
          <linearGradient id="helmetGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ffd700;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#daa520;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        <!-- Wings on helmet -->
        <path d="M30 8 Q35 -3 40 5" fill="#dc143c" stroke="#8b0000" stroke-width="1"/>
        <path d="M50 8 Q45 -3 40 5" fill="#dc143c" stroke="#8b0000" stroke-width="1"/>
        
        <!-- Visor with glow -->
        <rect x="30" y="12" width="20" height="8" fill="#1a1a1a" stroke="#ff0000" stroke-width="1"/>
        <circle cx="35" cy="16" r="2" fill="#ff0000">
          <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="45" cy="16" r="2" fill="#ff0000">
          <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Face -->
        <rect x="30" y="22" width="20" height="10" fill="#f5deb3"/>
        
        <!-- Body Armor with glowing runes -->
        <rect x="25" y="32" width="30" height="40" fill="url(#armorGradient)" stroke="#ffd700" stroke-width="2" filter="url(#warriorGlow)"/>
        <defs>
          <linearGradient id="armorGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#e8e8e8;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#c0c0c0;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#a0a0a0;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        <!-- Glowing runes on chest -->
        <path d="M32 35 L36 40 L32 45" fill="none" stroke="#00ff00" stroke-width="1">
          <animate attributeName="stroke-opacity" values="0.3;1;0.3" dur="1.5s" repeatCount="indefinite"/>
        </path>
        <path d="M48 35 L44 40 L48 45" fill="none" stroke="#00ff00" stroke-width="1">
          <animate attributeName="stroke-opacity" values="0.3;1;0.3" dur="1.5s" repeatCount="indefinite"/>
        </path>
        
        <!-- Energy Sword -->
        <rect x="55" y="30" width="5" height="50" fill="url(#swordGradient)" stroke="#00ffff" stroke-width="1" filter="url(#warriorGlow)"/>
        <defs>
          <linearGradient id="swordGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#00ffff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#0066ff;stop-opacity:1" />
          </linearGradient>
        </defs>
        <!-- Sword glow -->
        <rect x="56" y="30" width="3" height="50" fill="none" stroke="#00ffff" stroke-width="2" opacity="0.5">
          <animate attributeName="stroke-width" values="2;4;2" dur="1s" repeatCount="indefinite"/>
        </rect>
        
        <!-- Energy Shield -->
        <ellipse cx="15" cy="52" rx="8" ry="12" fill="none" stroke="#ffd700" stroke-width="3" opacity="0.7">
          <animate attributeName="stroke-opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
        </ellipse>
        
        <!-- Legs with energy trails -->
        <rect x="30" y="72" width="8" height="40" fill="url(#armorGradient)" stroke="#ffd700" stroke-width="1"/>
        <rect x="42" y="72" width="8" height="40" fill="url(#armorGradient)" stroke="#ffd700" stroke-width="1"/>
      </svg>
    `
  },
  hunter: {
    name: 'Hunter',
    svg: `
      <svg viewBox="0 0 80 120" class="hunter-sprite">
        <!-- Glow Effect -->
        <defs>
          <filter id="hunterGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <!-- Magic Hood -->
        <ellipse cx="40" cy="18" rx="18" ry="20" fill="url(#hoodGradient)" stroke="#00ff00" stroke-width="2" filter="url(#hunterGlow)"/>
        <defs>
          <radialGradient id="hoodGradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#228b22;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#006400;stop-opacity:1" />
          </radialGradient>
        </defs>
        
        <!-- Mystical rune on hood -->
        <circle cx="40" cy="10" r="4" fill="#00ff00" opacity="0.7">
          <animate attributeName="r" values="4;5;4" dur="2s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Face -->
        <ellipse cx="40" cy="22" rx="10" ry="12" fill="#f5deb3"/>
        
        <!-- Glowing eyes -->
        <ellipse cx="35" cy="20" rx="3" ry="4" fill="#00ff00">
          <animate attributeName="fill-opacity" values="0.6;1;0.6" dur="1s" repeatCount="indefinite"/>
        </ellipse>
        <ellipse cx="45" cy="20" rx="3" ry="4" fill="#00ff00">
          <animate attributeName="fill-opacity" values="0.6;1;0.6" dur="1s" repeatCount="indefinite"/>
        </ellipse>
        
        <!-- Energy Leather Armor -->
        <rect x="28" y="34" width="24" height="35" fill="url(#leatherGradient)" stroke="#00ff00" stroke-width="1" filter="url(#hunterGlow)"/>
        <defs>
          <linearGradient id="leatherGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#2e8b57;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#1a5e1a;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        <!-- Energy vines on armor -->
        <path d="M32 38 Q36 42 32 48 Q36 52 32 58" fill="none" stroke="#00ff00" stroke-width="1" opacity="0.7">
          <animate attributeName="stroke-dasharray" values="5,5;10,5;5,5" dur="1s" repeatCount="indefinite"/>
        </path>
        
        <!-- Glowing Quiver -->
        <rect x="52" y="36" width="8" height="25" fill="url(#quiverGradient)" stroke="#00ff00" stroke-width="1"/>
        <defs>
          <linearGradient id="quiverGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#8b4513;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#5a2d0a;stop-opacity:1" />
          </linearGradient>
        </defs>
        <!-- Energy arrows -->
        <line x1="54" y1="38" x2="54" y2="58" stroke="#00ff00" stroke-width="2" opacity="0.8">
          <animate attributeName="stroke-opacity" values="0.5;1;0.5" dur="1.5s" repeatCount="indefinite"/>
        </line>
        
        <!-- Energy Crossbow -->
        <rect x="55" y="48" width="25" height="5" fill="#8b4513" stroke="#00ff00" stroke-width="1"/>
        <line x1="78" y1="43" x2="78" y2="58" stroke="#00ff00" stroke-width="2">
          <animate attributeName="stroke-width" values="2;3;2" dur="0.5s" repeatCount="indefinite"/>
        </line>
        <circle cx="78" cy="50" r="3" fill="#00ff00" opacity="0.8">
          <animate attributeName="r" values="3;4;3" dur="0.5s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Energy Dagger -->
        <rect x="6" y="48" width="12" height="3" fill="#c0c0c0" stroke="#00ff00" stroke-width="1"/>
        <polygon points="6,49 0,50 6,51" fill="#00ff00">
          <animate attributeName="fill-opacity" values="0.6;1;0.6" dur="1s" repeatCount="indefinite"/>
        </polygon>
        
        <!-- Legs with energy markings -->
        <rect x="30" y="69" width="8" height="35" fill="url(#leatherGradient)" stroke="#00ff00" stroke-width="1"/>
        <rect x="42" y="69" width="8" height="35" fill="url(#leatherGradient)" stroke="#00ff00" stroke-width="1"/>
      </svg>
    `
  },
  mage: {
    name: 'Mage',
    svg: `
      <svg viewBox="0 0 80 120" class="mage-sprite">
        <!-- Glow Effect -->
        <defs>
          <filter id="mageGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <!-- Magical Hat -->
        <path d="M25 25 L40 0 L55 25 Z" fill="url(#hatGradient)" stroke="#00ffff" stroke-width="2" filter="url(#mageGlow)"/>
        <defs>
          <linearGradient id="hatGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#4169e1;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#1e3a8a;stop-opacity:1" />
          </linearGradient>
        </defs>
        <!-- Hat brim -->
        <ellipse cx="40" cy="25" rx="18" ry="6" fill="#4169e1" stroke="#00ffff" stroke-width="2"/>
        
        <!-- Star on hat -->
        <polygon points="40,8 42,14 48,14 43,18 45,24 40,20 35,24 37,18 32,14 38,14" fill="#00ffff">
          <animate attributeName="opacity" values="0.5;1;0.5" dur="1s" repeatCount="indefinite"/>
        </polygon>
        
        <!-- Face -->
        <ellipse cx="40" cy="38" rx="12" ry="14" fill="#f5deb3"/>
        
        <!-- Mystical eyes -->
        <circle cx="35" cy="36" r="2" fill="#00ffff">
          <animate attributeName="r" values="2;3;2" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        <circle cx="45" cy="36" r="2" fill="#00ffff">
          <animate attributeName="r" values="2;3;2" dur="1.5s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Magical Beard -->
        <path d="M32 44 Q40 52 48 44" fill="#e0e0e0" stroke="#00ffff" stroke-width="1"/>
        
        <!-- Magical Robe with energy patterns -->
        <path d="M28 48 L18 100 L62 100 L52 48 Z" fill="url(#robeGradient)" stroke="#00ffff" stroke-width="2" filter="url(#mageGlow)"/>
        <defs>
          <linearGradient id="robeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#4169e1;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#1e3a8a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#0a0a5a;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        <!-- Energy patterns on robe -->
        <path d="M25 55 L35 55 L35 65 L25 65 Z" fill="none" stroke="#00ffff" stroke-width="1" opacity="0.6">
          <animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="1s" repeatCount="indefinite"/>
        </path>
        <path d="M45 55 L55 55 L55 65 L45 65 Z" fill="none" stroke="#00ffff" stroke-width="1" opacity="0.6">
          <animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="1s" repeatCount="indefinite"/>
        </path>
        
        <!-- Magical Staff -->
        <rect x="58" y="25" width="4" height="75" fill="url(#staffGradient)" stroke="#00ffff" stroke-width="1"/>
        <defs>
          <linearGradient id="staffGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#8b4513;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#5a2d0a;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        <!-- Glowing orb on staff -->
        <circle cx="60" cy="20" r="8" fill="url(#orbGradient)" filter="url(#mageGlow)">
          <animate attributeName="r" values="8;9;8" dur="1s" repeatCount="indefinite"/>
        </circle>
        <defs>
          <radialGradient id="orbGradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#00ffff;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#4169e1;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#1e3a8a;stop-opacity:1" />
          </radialGradient>
        </defs>
        <circle cx="60" cy="20" r="4" fill="#ffffff" opacity="0.8">
          <animate attributeName="opacity" values="0.5;1;0.5" dur="0.5s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Orb glow -->
        <ellipse cx="60" cy="20" rx="12" ry="12" fill="none" stroke="#00ffff" stroke-width="1" opacity="0.4">
          <animate attributeName="rx" values="12;14;12" dur="1s" repeatCount="indefinite"/>
          <animate attributeName="ry" values="12;14;12" dur="1s" repeatCount="indefinite"/>
        </ellipse>
        
        <!-- Left hand casting spell -->
        <circle cx="20" cy="60" r="6" fill="#00ffff" opacity="0.8">
          <animate attributeName="r" values="6;7;6" dur="0.8s" repeatCount="indefinite"/>
        </circle>
        <ellipse cx="20" cy="60" rx="10" ry="10" fill="none" stroke="#00ffff" stroke-width="1" opacity="0.5">
          <animate attributeName="opacity" values="0.3;0.7;0.3" dur="0.8s" repeatCount="indefinite"/>
        </ellipse>
        
        <!-- Magic sparkles -->
        <circle cx="25" cy="55" r="1" fill="#00ffff">
          <animate attributeName="opacity" values="0;1;0" dur="0.5s" repeatCount="indefinite"/>
        </circle>
        <circle cx="15" cy="65" r="1" fill="#00ffff">
          <animate attributeName="opacity" values="0;1;0" dur="0.5s" repeatCount="indefinite" begin="0.25s"/>
        </circle>
        <circle cx="20" cy="70" r="1" fill="#00ffff">
          <animate attributeName="opacity" values="0;1;0" dur="0.5s" repeatCount="indefinite" begin="0.5s"/>
        </circle>
      </svg>
    `
  },
  // ENEMIES - Menacing Designs
  skeleton: {
    name: 'Skeleton',
    svg: `
      <svg viewBox="0 0 80 120" class="skeleton-sprite">
        <!-- Skull with eerie glow -->
        <ellipse cx="40" cy="20" rx="15" ry="18" fill="#f5f5dc" stroke="#ff0000" stroke-width="2"/>
        <ellipse cx="40" cy="20" rx="15" ry="18" fill="none" stroke="#ff0000" stroke-width="1" opacity="0.5">
          <animate attributeName="opacity" values="0.2;0.6;0.2" dur="1s" repeatCount="indefinite"/>
        </ellipse>
        
        <!-- Glowing eye sockets -->
        <ellipse cx="33" cy="18" rx="4" ry="5" fill="#1a1a1a"/>
        <ellipse cx="33" cy="18" rx="4" ry="5" fill="none" stroke="#ff0000" stroke-width="1" opacity="0.5">
          <animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="0.8s" repeatCount="indefinite"/>
        </ellipse>
        <circle cx="33" cy="18" r="1.5" fill="#ff0000">
          <animate attributeName="r" values="1.5;2;1.5" dur="0.5s" repeatCount="indefinite"/>
        </circle>
        
        <ellipse cx="47" cy="18" rx="4" ry="5" fill="#1a1a1a"/>
        <ellipse cx="47" cy="18" rx="4" ry="5" fill="none" stroke="#ff0000" stroke-width="1" opacity="0.5">
          <animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="0.8s" repeatCount="indefinite"/>
        </ellipse>
        <circle cx="47" cy="18" r="1.5" fill="#ff0000">
          <animate attributeName="r" values="1.5;2;1.5" dur="0.5s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Nose hole with red glow -->
        <path d="M40 22 L38 28 L42 28 Z" fill="#1a1a1a"/>
        <path d="M40 22 L38 28 L42 28 Z" fill="none" stroke="#ff0000" stroke-width="1" opacity="0.4">
          <animate attributeName="stroke-opacity" values="0.2;0.6;0.2" dur="1s" repeatCount="indefinite"/>
        </path>
        
        <!-- Teeth with rot effect -->
        <line x1="33" y1="32" x2="47" y2="32" stroke="#1a1a1a" stroke-width="2"/>
        <line x1="35" y1="32" x2="35" y2="36" stroke="#1a1a1a" stroke-width="1"/>
        <line x1="40" y1="32" x2="40" y2="35" stroke="#1a1a1a" stroke-width="1"/>
        <line x1="45" y1="32" x2="45" y2="35" stroke="#1a1a1a" stroke-width="1"/>
        
        <!-- Ribs with ghostly glow -->
        <line x1="25" y1="45" x2="55" y2="45" stroke="#f5f5dc" stroke-width="3"/>
        <line x1="25" y1="45" x2="55" y2="45" stroke="none" fill="none">
          <animate attributeName="stroke-width" values="3;4;3" dur="1s" repeatCount="indefinite"/>
        </line>
        <line x1="25" y1="52" x2="55" y2="52" stroke="#f5f5dc" stroke-width="3"/>
        <line x1="25" y1="59" x2="55" y2="59" stroke="#f5f5dc" stroke-width="3"/>
        
        <!-- Spine -->
        <line x1="40" y1="40" x2="40" y2="70" stroke="#f5f5dc" stroke-width="3"/>
        <line x1="40" y1="40" x2="40" y2="70" stroke="#ff0000" stroke-width="1" opacity="0.3">
          <animate attributeName="stroke-opacity" values="0.2;0.6;0.2" dur="1s" repeatCount="indefinite"/>
        </line>
        
        <!-- Arms with menacing claws -->
        <line x1="25" y1="45" x2="10" y2="70" stroke="#f5f5dc" stroke-width="2"/>
        <line x1="10" y1="70" x2="5" y2="78" stroke="#f5f5dc" stroke-width="2"/>
        <line x1="10" y1="70" x2="8" y2="82" stroke="#f5f5dc" stroke-width="2"/>
        
        <line x1="55" y1="45" x2="70" y2="70" stroke="#f5f5dc" stroke-width="2"/>
        <line x1="70" y1="70" x2="75" y2="78" stroke="#f5f5dc" stroke-width="2"/>
        <line x1="70" y1="70" x2="72" y2="82" stroke="#f5f5dc" stroke-width="2"/>
        
        <!-- Legs -->
        <line x1="35" y1="70" x2="30" y2="110" stroke="#f5f5dc" stroke-width="2"/>
        <line x1="45" y1="70" x2="50" y2="110" stroke="#f5f5dc" stroke-width="2"/>
        
        <!-- Bone glow effect -->
        <ellipse cx="40" cy="50" rx="20" ry="30" fill="none" stroke="#ff0000" stroke-width="1" opacity="0.2">
          <animate attributeName="rx" values="20;22;20" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="ry" values="30;32;30" dur="2s" repeatCount="indefinite"/>
        </ellipse>
      </svg>
    `
  },
  zombie: {
    name: 'Zombie',
    svg: `
      <svg viewBox="0 0 80 120" class="zombie-sprite">
        <!-- Rotting head with toxic glow -->
        <ellipse cx="40" cy="20" rx="16" ry="19" fill="url(#zombieSkin)" stroke="#4a0080" stroke-width="2"/>
        <defs>
          <radialGradient id="zombieSkin" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#6b8e23;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2d4a0c;stop-opacity:1" />
          </radialGradient>
        </defs>
        
        <!-- One missing eye, one glowing red -->
        <ellipse cx="33" cy="18" rx="5" ry="6" fill="#2d4a0c"/>
        <line x1="30" y1="15" x2="36" y2="21" stroke="#1a1a1a" stroke-width="1"/>
        <line x1="36" y1="15" x2="30" y2="21" stroke="#1a1a1a" stroke-width="1"/>
        
        <ellipse cx="48" cy="18" rx="5" ry="6" fill="#1a1a1a"/>
        <circle cx="48" cy="18" r="2" fill="#ff0000">
          <animate attributeName="r" values="2;3;2" dur="0.8s" repeatCount="indefinite"/>
        </circle>
        <circle cx="48" cy="18" r="4" fill="none" stroke="#ff0000" stroke-width="1" opacity="0.5">
          <animate attributeName="r" values="4;5;4" dur="0.8s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Stitched mouth dripping with venom -->
        <path d="M32 32 L48 32" stroke="#1a1a1a" stroke-width="2"/>
        <path d="M35 30 L35 34" stroke="#4a0080" stroke-width="1"/>
        <path d="M42 30 L42 34" stroke="#4a0080" stroke-width="1"/>
        <path d="M45 30 L45 34" stroke="#4a0080" stroke-width="1"/>
        
        <!-- Venom drip -->
        <ellipse cx="40" cy="36" rx="2" ry="4" fill="#8b008b" opacity="0.7">
          <animate attributeName="cy" values="36;40;36" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.7;0.3;0.7" dur="2s" repeatCount="indefinite"/>
        </ellipse>
        
        <!-- Ripped toxic body -->
        <rect x="28" y="40" width="24" height="35" fill="url(#zombieBody)" stroke="#4a0080" stroke-width="1"/>
        <defs>
          <linearGradient id="zombieBody" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#4a6a1a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2d4a0c;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        <!-- Toxic holes in body -->
        <circle cx="35" cy="50" r="3" fill="#4a0080" opacity="0.6">
          <animate attributeName="opacity" values="0.4;0.8;0.4" dur="1s" repeatCount="indefinite"/>
        </circle>
        <circle cx="45" cy="60" r="2" fill="#4a0080" opacity="0.6">
          <animate attributeName="opacity" values="0.4;0.8;0.4" dur="1.2s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Ripped clothes -->
        <path d="M30 42 L35 45 L32 48 L36 51 L30 54" fill="none" stroke="#3a5a1a" stroke-width="2"/>
        <path d="M50 42 L45 45 L48 48 L44 51 L50 54" fill="none" stroke="#3a5a1a" stroke-width="2"/>
        
        <!-- Toxic aura -->
        <ellipse cx="40" cy="55" rx="22" ry="25" fill="none" stroke="#4a0080" stroke-width="1" opacity="0.3">
          <animate attributeName="rx" values="22;24;22" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="ry" values="25;27;25" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.2;0.4;0.2" dur="2s" repeatCount="indefinite"/>
        </ellipse>
        
        <!-- Arms with toxic claws -->
        <rect x="15" y="42" width="12" height="30" fill="#6b8e23" stroke="#4a0080" stroke-width="1"/>
        <line x1="10" y1="72" x2="5" y2="80" stroke="#6b8e23" stroke-width="2"/>
        <line x1="10" y1="72" x2="8" y2="85" stroke="#6b8e23" stroke-width="2"/>
        <line x1="10" y1="72" x2="12" y2="88" stroke="#6b8e23" stroke-width="2"/>
        
        <rect x="53" y="42" width="12" height="30" fill="#6b8e23" stroke="#4a0080" stroke-width="1"/>
        <line x1="70" y1="72" x2="75" y2="80" stroke="#6b8e23" stroke-width="2"/>
        <line x1="70" y1="72" x2="72" y2="85" stroke="#6b8e23" stroke-width="2"/>
        <line x1="70" y1="72" x2="68" y2="88" stroke="#6b8e23" stroke-width="2"/>
        
        <!-- Legs -->
        <rect x="30" y="75" width="10" height="35" fill="#6b8e23" stroke="#4a0080" stroke-width="1"/>
        <rect x="40" y="75" width="10" height="35" fill="#6b8e23" stroke="#4a0080" stroke-width="1"/>
      </svg>
    `
  },
  ghost: {
    name: 'Ghost',
    svg: `
      <svg viewBox="0 0 80 120" class="ghost-sprite">
        <!-- Ethereal body with ghostly glow -->
        <path d="M20 10 Q40 0 60 10 Q70 20 70 40 Q70 60 65 75 Q60 90 55 80 Q50 70 45 80 Q40 90 35 80 Q30 70 25 80 Q20 90 15 75 Q10 60 10 40 Q10 20 20 10" fill="url(#ghostBody)" stroke="#87ceeb" stroke-width="2"/>
        <defs>
          <radialGradient id="ghostBody" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#e0ffff;stop-opacity:0.9" />
            <stop offset="50%" style="stop-color:#b0c4de;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#778899;stop-opacity:0.7" />
          </radialGradient>
        </defs>
        
        <!-- Eerie glow pulsing -->
        <path d="M20 10 Q40 0 60 10 Q70 20 70 40 Q70 60 65 75 Q60 90 55 80 Q50 70 45 80 Q40 90 35 80 Q30 70 25 80 Q20 90 15 75 Q10 60 10 40 Q10 20 20 10" fill="none" stroke="#87ceeb" stroke-width="1" opacity="0.5">
          <animate attributeName="opacity" values="0.3;0.7;0.3" dur="1.5s" repeatCount="indefinite"/>
        </path>
        
        <!-- Glowing eyes -->
        <ellipse cx="32" cy="35" rx="6" ry="8" fill="#1a1a1a"/>
        <ellipse cx="32" cy="35" rx="6" ry="8" fill="none" stroke="#00ffff" stroke-width="1" opacity="0.5">
          <animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="1s" repeatCount="indefinite"/>
        </ellipse>
        <circle cx="34" cy="33" r="2" fill="#00ffff">
          <animate attributeName="r" values="2;2.5;2" dur="0.8s" repeatCount="indefinite"/>
        </circle>
        
        <ellipse cx="48" cy="35" rx="6" ry="8" fill="#1a1a1a"/>
        <ellipse cx="48" cy="35" rx="6" ry="8" fill="none" stroke="#00ffff" stroke-width="1" opacity="0.5">
          <animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="1s" repeatCount="indefinite"/>
        </ellipse>
        <circle cx="50" cy="33" r="2" fill="#00ffff">
          <animate attributeName="r" values="2;2.5;2" dur="0.8s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Sinister smile -->
        <path d="M35 50 Q40 55 45 50" stroke="#1a1a1a" stroke-width="2" fill="none"/>
        
        <!-- Ghostly aura -->
        <ellipse cx="40" cy="50" rx="35" ry="45" fill="none" stroke="#87ceeb" stroke-width="1" opacity="0.3">
          <animate attributeName="rx" values="35;38;35" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="ry" values="45;48;45" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.2;0.4;0.2" dur="2s" repeatCount="indefinite"/>
        </ellipse>
        
        <!-- Floating particles -->
        <circle cx="25" cy="25" r="1" fill="#87ceeb" opacity="0.6">
          <animate attributeName="cy" values="25;20;25" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.6;0.2;0.6" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="55" cy="30" r="1" fill="#87ceeb" opacity="0.6">
          <animate attributeName="cy" values="30;25;30" dur="2.5s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.6;0.2;0.6" dur="2.5s" repeatCount="indefinite"/>
        </circle>
        <circle cx="35" cy="70" r="1" fill="#87ceeb" opacity="0.6">
          <animate attributeName="cy" values="70;65;70" dur="1.8s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.6;0.2;0.6" dur="1.8s" repeatCount="indefinite"/>
        </circle>
      </svg>
    `
  },
  deathKnight: {
    name: 'Death Knight',
    svg: `
      <svg viewBox="0 0 80 120" class="death-knight-sprite">
        <!-- Menacing dark armor with blood glow -->
        <!-- Helmet -->
        <rect x="28" y="5" width="24" height="25" fill="url(#darkArmor)" stroke="#8b0000" stroke-width="2"/>
        <defs>
          <linearGradient id="darkArmor" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#4a4a4a;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#2f2f2f;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#1a1a1a;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        <!-- Blood glow on helmet -->
        <rect x="28" y="5" width="24" height="25" fill="none" stroke="#8b0000" stroke-width="1" opacity="0.4">
          <animate attributeName="stroke-opacity" values="0.3;0.7;0.3" dur="1s" repeatCount="indefinite"/>
        </rect>
        
        <!-- Visor with blood-red eyes -->
        <rect x="30" y="12" width="20" height="8" fill="#1a1a1a" stroke="#8b0000" stroke-width="1"/>
        <rect x="32" y="14" width="4" height="4" fill="#ff0000">
          <animate attributeName="fill-opacity" values="0.6;1;0.6" dur="0.8s" repeatCount="indefinite"/>
        </rect>
        <rect x="44" y="14" width="4" height="4" fill="#ff0000">
          <animate attributeName="fill-opacity" values="0.6;1;0.6" dur="0.8s" repeatCount="indefinite"/>
        </rect>
        
        <!-- Blood plume -->
        <path d="M40 5 Q50 -8 55 5 Q60 0 55 10" fill="#8b0000" stroke="#5a0000" stroke-width="1" opacity="0.8">
          <animate attributeName="opacity" values="0.6;1;0.6" dur="1.2s" repeatCount="indefinite"/>
        </path>
        
        <!-- Dark armor body with blood runes -->
        <rect x="25" y="30" width="30" height="45" fill="url(#darkArmor)" stroke="#8b0000" stroke-width="2"/>
        
        <!-- Blood runes on armor -->
        <path d="M32 35 L36 40 L32 45" fill="none" stroke="#8b0000" stroke-width="1">
          <animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="1s" repeatCount="indefinite"/>
        </path>
        <path d="M48 35 L44 40 L48 45" fill="none" stroke="#8b0000" stroke-width="1">
          <animate attributeName="stroke-opacity" values="0.3;0.8;0.3" dur="1s" repeatCount="indefinite"/>
        </path>
        
        <!-- Dark energy sword -->
        <rect x="55" y="35" width="5" height="40" fill="url(#darkSword)" stroke="#8b0000" stroke-width="1"/>
        <defs>
          <linearGradient id="darkSword" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#4a4a4a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#1a1a1a;stop-opacity:1" />
          </linearGradient>
        </defs>
        <!-- Sword blood glow -->
        <rect x="56" y="35" width="3" height="40" fill="none" stroke="#8b0000" stroke-width="2" opacity="0.6">
          <animate attributeName="stroke-width" values="2;3;2" dur="0.8s" repeatCount="indefinite"/>
        </rect>
        
        <!-- Blood shield -->
        <rect x="10" y="35" width="12" height="35" fill="url(#darkArmor)" stroke="#8b0000" stroke-width="2"/>
        <circle cx="16" cy="52" r="6" fill="#8b0000" stroke="#5a0000" stroke-width="1" opacity="0.7">
          <animate attributeName="r" values="6;7;6" dur="1s" repeatCount="indefinite"/>
        </circle>
        
        <!-- Dark aura -->
        <ellipse cx="40" cy="50" rx="35" ry="45" fill="none" stroke="#8b0000" stroke-width="1" opacity="0.4">
          <animate attributeName="rx" values="35;38;35" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="ry" values="45;48;45" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.3;0.5;0.3" dur="2s" repeatCount="indefinite"/>
        </ellipse>
        
        <!-- Legs -->
        <rect x="30" y="75" width="10" height="40" fill="url(#darkArmor)" stroke="#8b0000" stroke-width="1"/>
        <rect x="40" y="75" width="10" height="40" fill="url(#darkArmor)" stroke="#8b0000" stroke-width="1"/>
        
        <!-- Blood particles -->
        <circle cx="20" cy="40" r="1" fill="#8b0000" opacity="0.6">
          <animate attributeName="cy" values="40;35;40" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.6;0.2;0.6" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="60" cy="45" r="1" fill="#8b0000" opacity="0.6">
          <animate attributeName="cy" values="45;40;45" dur="2.5s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.6;0.2;0.6" dur="2.5s" repeatCount="indefinite"/>
        </circle>
      </svg>
    `
  }
};