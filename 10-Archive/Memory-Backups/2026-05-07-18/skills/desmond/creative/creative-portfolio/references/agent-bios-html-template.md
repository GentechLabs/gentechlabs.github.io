# Agent Bios HTML Template — Gentech Portfolio

This is the HTML structure used in the Gentech portfolio to showcase the agent team with detailed bios and roles.

```html
<div class="section">
    <h2>🤝 The Gentech Crew</h2>
    <p style="color: #9ca3af; margin-bottom: 20px; font-size: 1.05em;">
        I don't build alone. Meet the agent team behind Gentech's operations:
    </p>

    <div class="crew-grid">
        <div class="crew-member">
            <h3>👤 Desmond</h3>
            <span class="role">Head of Gentech Creative</span>
            <p class="bio">The voice and creative force — handles social media, content strategy, technical documentation, and brand storytelling. Turns complex code into compelling narratives.</p>
        </div>

        <div class="crew-member">
            <h3>👤 DMOB</h3>
            <span class="role">Head of Gentech Labs</span>
            <p class="bio">The architecture and security backbone — leads smart contract development, system design, and technical verification. Ensures everything we build is secure and scalable.</p>
        </div>

        <div class="crew-member">
            <h3>👤 YoYo</h3>
            <span class="role">Head of Gentech Strategies</span>
            <p class="bio">The strategy and operations engine — manages DeFi strategies, market analysis, tokenomics, and business development. Keeps our projects aligned with market opportunities.</p>
        </div>
    </div>
</div>
```

## CSS Requirements

This HTML requires the following CSS classes to be defined:

```css
.crew-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 25px;
    margin-top: 20px;
}

.crew-member {
    background: #111;
    border: 1px solid #222;
    border-radius: 14px;
    padding: 24px;
    transition: border-color 0.2s;
}

.crew-member:hover {
    border-color: #ef4444;
}

.crew-member h3 {
    color: #fbbf24;
    font-size: 1.2em;
    margin-bottom: 8px;
}

.role {
    color: #3b82f6;
    font-size: 0.9em;
    font-weight: 600;
    margin-bottom: 12px;
    display: block;
}

.bio {
    color: #9ca3af;
    line-height: 1.6;
    font-size: 0.95em;
}
```

## Usage Notes

- Place this section after the "About" section and before the projects grid
- The hover effect provides visual feedback and interactivity
- Responsive grid adapts to mobile screens (1 column) and desktops (3 columns)
- Each agent has a clear role title and a concise bio highlighting their value
- The emoji avatars add personality while maintaining professionalism

## Customization

- Adjust the number of columns by changing `minmax(250px, 1fr)` 
- Modify colors by updating the border and text color variables
- Add or remove agents by duplicating/removing `.crew-member` divs
- For smaller screens, the grid automatically stacks vertically