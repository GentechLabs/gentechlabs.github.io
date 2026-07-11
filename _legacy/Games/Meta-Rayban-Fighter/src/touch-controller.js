export class TouchController {
  constructor(onAction) {
    this.onAction = onAction;
    this.isListening = false;
    this.touchZones = [];
  }

  start() {
    if (this.isListening) return;
    this.isListening = true;

    document.querySelectorAll('.touch-zone').forEach(zone => {
      this.touchZones.push(zone);
      zone.addEventListener('click', (e) => {
        e.preventDefault();
        const action = zone.getAttribute('data-action');
        if (action && this.onAction) {
          this.onAction(action);
          this.visualFeedback(zone);
        }
      });

      zone.addEventListener('touchstart', (e) => {
        e.preventDefault();
        zone.style.transform = 'scale(0.95)';
      }, { passive: false });

      zone.addEventListener('touchend', (e) => {
        e.preventDefault();
        zone.style.transform = 'scale(1)';
        const action = zone.getAttribute('data-action');
        if (action && this.onAction) {
          this.onAction(action);
        }
      });
    });

    console.log('Touch controller started. Tap action buttons to play.');
  }

  stop() {
    this.isListening = false;
    this.touchZones.forEach(zone => {
      zone.removeEventListener('click', () => {});
      zone.removeEventListener('touchstart', () => {});
      zone.removeEventListener('touchend', () => {});
    });
  }

  visualFeedback(zone) {
    zone.classList.add('active');
    setTimeout(() => zone.classList.remove('active'), 200);
  }
}