/* Beemo landing — particles + launch sequence */
(() => {
  'use strict';

  /* ---------- Particles ---------- */
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d', { alpha: true });
  const DPR = Math.min(window.devicePixelRatio || 1, 1.5);
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  let w = 0, h = 0;
  let count = reduceMotion ? 0 : 55;
  let speedY = 0;
  const parts = [];

  function sizeCanvas() {
    w = canvas.width = innerWidth * DPR;
    h = canvas.height = innerHeight * DPR;
    canvas.style.width = innerWidth + 'px';
    canvas.style.height = innerHeight + 'px';
  }
  function resetPart(p, randomY = false) {
    p.x = Math.random() * w;
    p.y = randomY ? Math.random() * h : -10;
    p.r = (Math.random() * 1.4 + 0.3) * DPR;
    p.vx = (Math.random() - 0.5) * 0.15 * DPR;
    p.vy = (-Math.random() * 0.35 - 0.05) * DPR;
    p.a = Math.random() * 0.5 + 0.2;
  }
  function initParts(n) {
    parts.length = 0;
    for (let i = 0; i < n; i++) {
      const p = {};
      resetPart(p, true);
      parts.push(p);
    }
  }
  sizeCanvas();
  initParts(count);

  let resizeTimer;
  addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => { sizeCanvas(); initParts(count); }, 120);
  });

  // Cache accent color (read once, refresh occasionally)
  let accent = '#a78bff';
  let accentHex = '60';
  function refreshAccent() {
    const v = getComputedStyle(document.body).getPropertyValue('--accent-a').trim();
    if (v) accent = v;
  }
  refreshAccent();
  setInterval(refreshAccent, 500);

  let running = true;
  document.addEventListener('visibilitychange', () => { running = !document.hidden; if (running) requestAnimationFrame(tick); });

  function tick() {
    if (!running) return;
    ctx.clearRect(0, 0, w, h);
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i];
      p.x += p.vx;
      p.y += p.vy + speedY;
      if (p.y < -10 || p.y > h + 20 || p.x < -10 || p.x > w + 10) resetPart(p, speedY < 1);
      ctx.beginPath();
      ctx.fillStyle = `rgba(255,255,255,${p.a * 0.7})`;
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.fillStyle = accent + accentHex;
      ctx.arc(p.x, p.y, p.r * 3, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  /* ---------- Launch sequence ---------- */
  const useBeemo = document.getElementById('useBeemo');
  const navLaunch = document.getElementById('navLaunch');
  const warp = document.getElementById('warp');
  const countdown = document.getElementById('countdown');

  // Build warp streaks lazily on first launch instead of upfront
  let streaksBuilt = false;
  function buildStreaks() {
    if (streaksBuilt) return;
    streaksBuilt = true;
    const frag = document.createDocumentFragment();
    const N = 60;
    for (let i = 0; i < N; i++) {
      const s = document.createElement('div');
      s.className = 'streak';
      const ang = Math.random() * 360;
      const dist = 40 + Math.random() * 60;
      const x = Math.cos(ang * Math.PI / 180) * dist;
      const y = Math.sin(ang * Math.PI / 180) * dist;
      s.style.left = `calc(50% + ${x}vw)`;
      s.style.top = `calc(50% + ${y}vh)`;
      s.style.animationDelay = (Math.random() * 0.6) + 's';
      if (i % 5 === 0) s.style.background = 'linear-gradient(to bottom, transparent, var(--accent-a))';
      frag.appendChild(s);
    }
    warp.appendChild(frag);
  }

  let launching = false;
  function launch() {
    if (launching) return;
    launching = true;
    buildStreaks();
    document.body.classList.add('launching');
    speedY = 14 * DPR;

    const seq = ['T – 03', 'T – 02', 'T – 01', 'IGNITION'];
    let i = 0;
    countdown.textContent = seq[0];
    const ticker = setInterval(() => {
      i++;
      if (i < seq.length) countdown.textContent = seq[i];
      else clearInterval(ticker);
    }, 280);

    setTimeout(() => {
      sessionStorage.setItem('beemo:arriving', '1');
      location.href = 'Beemo App.html';
    }, 2100);
  }

  useBeemo.addEventListener('click', launch);
  navLaunch.addEventListener('click', e => { e.preventDefault(); launch(); });
  addEventListener('keydown', e => {
    if (e.key === 'Enter' && !launching && document.activeElement === document.body) launch();
  });
})();
