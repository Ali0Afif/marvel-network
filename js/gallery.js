(function () {
  'use strict';

  const ease = t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;

  /* phase: 0=active, +1=upcoming (below/behind), -1=receded (above/behind) */
  function phaseToStyle(phase) {
    const W = 0.68;
    if (phase >  W) return { scale: 0.80, ty:  130, tz: -260, op: 0 };
    if (phase < -W) return { scale: 1.13, ty:  -95, tz: -190, op: 0 };
    if (phase >= 0) {
      const t = ease(phase / W);
      return { scale: 1 - t * 0.20, ty: t * 130, tz: -t * 260, op: 1 - t };
    }
    const t = ease(-phase / W);
    return { scale: 1 + t * 0.13, ty: -t * 95, tz: -t * 190, op: 1 - t };
  }

  class Gallery {
    constructor(track) {
      this.track    = track;
      this.exhibits = [...track.querySelectorAll('.g-sticky > .g-exhibit')];
      this.N        = this.exhibits.length;
      if (!this.N) return;

      const SCREENS = parseFloat(track.dataset.screens || '1.45');
      track.style.height = `${(this.N - 1) * SCREENS * 100 + 100}vh`;

      /* build progress dots */
      const dotsEl = track.querySelector('.g-dots');
      if (dotsEl) {
        this.exhibits.forEach(() => {
          const d = document.createElement('div');
          d.className = 'g-dot';
          dotsEl.appendChild(d);
        });
        this.dotEls = [...dotsEl.querySelectorAll('.g-dot')];
      }
      this.numEl = track.querySelector('.g-num');

      this._raf  = null;
      this._last = -99;
      window.addEventListener('scroll', () => this._sched(), { passive: true });
      window.addEventListener('resize', () => this._update());
      this._update();
    }

    _sched() {
      if (this._raf) return;
      this._raf = requestAnimationFrame(() => { this._raf = null; this._update(); });
    }

    _update() {
      const rect       = this.track.getBoundingClientRect();
      const scrollable = this.track.offsetHeight - window.innerHeight;
      const p = scrollable > 0
        ? Math.max(0, Math.min(this.N - 1, (-rect.top / scrollable) * (this.N - 1)))
        : 0;
      if (Math.abs(p - this._last) < 0.001) return;
      this._last = p;

      this.exhibits.forEach((el, i) => {
        const s = phaseToStyle(i - p);
        el.style.transform    = `perspective(1400px) translateZ(${s.tz}px) translateY(${s.ty}px) scale(${s.scale})`;
        el.style.opacity      = Math.max(0, s.op).toFixed(3);
        el.style.pointerEvents = s.op > 0.3 ? '' : 'none';
      });

      const active = Math.round(p);
      this.dotEls?.forEach((d, i) => d.classList.toggle('active', i === active));
      if (this.numEl) this.numEl.textContent = String(active + 1).padStart(2, '0');
    }
  }

  function init() {
    document.querySelectorAll('.gallery-track').forEach(el => new Gallery(el));
  }

  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', init)
    : init();
})();
