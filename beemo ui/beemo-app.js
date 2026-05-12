/* Beemo App — particles, state, tweaks, parallax, clock, arrival */
(() => {
  'use strict';

  /* ---------- Particles ---------- */
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d', { alpha: true });
  const DPR = Math.min(window.devicePixelRatio || 1, 1.5);
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  let w = 0, h = 0;
  let count = reduceMotion ? 0 : 55;
  const parts = [];

  function sizeCanvas() {
    w = canvas.width = innerWidth * DPR;
    h = canvas.height = innerHeight * DPR;
    canvas.style.width = innerWidth + 'px';
    canvas.style.height = innerHeight + 'px';
  }
  function resetPart(p, randomY = false) {
    p.x = Math.random() * w;
    p.y = randomY ? Math.random() * h : h + 10;
    p.r = (Math.random() * 1.4 + 0.3) * DPR;
    p.vx = (Math.random() - 0.5) * 0.15 * DPR;
    p.vy = (-Math.random() * 0.35 - 0.05) * DPR;
    p.a = Math.random() * 0.5 + 0.2;
    p.life = Math.random() * 200 + 200;
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

  let accent = '#a78bff';
  function refreshAccent() {
    const v = getComputedStyle(document.body).getPropertyValue('--accent-a').trim();
    if (v) accent = v;
  }
  refreshAccent();
  setInterval(refreshAccent, 500);

  let running = true;
  document.addEventListener('visibilitychange', () => {
    running = !document.hidden;
    if (running) requestAnimationFrame(tick);
  });

  function tick() {
    if (!running) return;
    ctx.clearRect(0, 0, w, h);
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i];
      p.x += p.vx; p.y += p.vy; p.life--;
      if (p.life <= 0 || p.y < -10 || p.x < -10 || p.x > w + 10) resetPart(p);
      ctx.beginPath();
      ctx.fillStyle = `rgba(255,255,255,${p.a * 0.6})`;
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.fillStyle = accent + '60';
      ctx.arc(p.x, p.y, p.r * 3, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  window.__setParticles = n => {
    count = Math.max(0, Math.min(200, n | 0));
    initParts(count);
  };

  /* ---------- State management ---------- */
  const body = document.body;
  const stage = document.getElementById('stage');
  const chips = document.querySelectorAll('.chip');
  const railState = document.getElementById('railState');
  const transcript = document.getElementById('transcript');
  const chatLog = document.getElementById('chat-log');
  const mic = document.getElementById('mic');
  const dock = document.getElementById('dock');
  const promptInput = document.getElementById('prompt');

  let activeBody = null; // body element of the current active Beemo message

  function createMsg(roleText, html, withViz) {
    const div = document.createElement('div');
    div.className = 'msg msg-' + roleText.toLowerCase();
    const roleEl = document.createElement('div');
    roleEl.className = 'msg-role';
    roleEl.textContent = roleText;
    if (withViz) {
      const v = document.createElement('span');
      v.className = 'viz';
      v.innerHTML = '<i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>';
      roleEl.appendChild(v);
    }
    const bodyEl = document.createElement('div');
    bodyEl.className = 'msg-body';
    if (html) bodyEl.innerHTML = html;
    div.appendChild(roleEl);
    div.appendChild(bodyEl);
    chatLog.appendChild(div);
    transcript.scrollTop = transcript.scrollHeight;
    return bodyEl;
  }

  const stateNames = {
    idle: 'Idle · standby',
    listening: 'Listening · live',
    replying: 'Replying · streaming'
  };
  let replyTimer = null, typeTimer = null, transitionTimer = null;
  let recognition = null, recognizing = false;

  function setState(s) {
    const prev = body.dataset.state;
    if (prev && prev !== s && s !== 'white') {
      clearTimeout(transitionTimer);
      body.dataset.state = 'white';
      body.classList.add('flash');
      transitionTimer = setTimeout(() => {
        body.classList.remove('flash');
        applyState(s);
      }, 360);
      chips.forEach(c => c.classList.toggle('active', c.dataset.state === s));
      railState.textContent = stateNames[s] || '';
      return;
    }
    applyState(s);
  }

  function applyState(s) {
    body.dataset.state = s;
    stage.classList.remove('idle', 'listening', 'replying');
    stage.classList.add(s);
    chips.forEach(c => c.classList.toggle('active', c.dataset.state === s));
    railState.textContent = stateNames[s];
    mic.classList.toggle('active', s === 'listening');
    if (s === 'listening') {
      transcript.hidden = false;
      transcript.classList.remove('empty');
    } else if (s === 'replying') {
      transcript.hidden = false;
      transcript.classList.remove('empty');
      activeBody = createMsg('Beemo', '<span class="cursor"></span>');
    } else {
      clearTimeout(replyTimer);
      clearTimeout(typeTimer);
      if (chatLog.children.length === 0) {
        transcript.hidden = true;
        transcript.classList.add('empty');
      }
    }
  }

  function startTyping(text, extras) {
    clearTimeout(typeTimer);
    activeBody.innerHTML = '';
    let i = 0;
    function step() {
      if (i <= text.length) {
        activeBody.innerHTML = text.slice(0, i) + '<span class="cursor"></span>';
        i++;
        transcript.scrollTop = transcript.scrollHeight;
        typeTimer = setTimeout(step, 18 + Math.random() * 22);
      } else {
        activeBody.innerHTML = text;
        if (extras) {
          const el = document.createElement('div');
          el.className = 'reply-extras';
          el.innerHTML = extras;
          activeBody.appendChild(el);
        }
        transcript.scrollTop = transcript.scrollHeight;
        replyTimer = setTimeout(() => setState('idle'), extras ? 7000 : 4200);
      }
    }
    step();
  }

  function sendChat(text) {
    return fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    }).then(r => r.ok ? r.json() : Promise.reject(new Error('Server error')));
  }

  function startReply(result) {
    const text = result.response || "I couldn't process that, try again.";
    let extras = null;
    if (result.intent === 'weather' && result.weather) {
      const w = result.weather;
      extras = `<div class="weather-card">
        <span class="weather-city">${w.city}</span>
        <span class="weather-temp">${Math.round(w.temp)}°C</span>
        <span class="weather-cond">${w.condition} · ${w.humidity}% humidity</span>
      </div>`;
    } else if (result.intent === 'news' && result.headlines && result.headlines.length) {
      const items = result.headlines
        .map((h, i) => `<li><span class="n">${i + 1}</span>${h}</li>`)
        .join('');
      extras = `<ul class="news-list">${items}</ul>`;
    } else if (result.intent === 'search' && result.search_results && result.search_results.length) {
      const items = result.search_results.map(r => `
        <li>
          <a class="sr-title" href="${r.url}" target="_blank" rel="noopener">${r.title}</a>
          <span class="sr-snippet">${r.snippet}</span>
        </li>`).join('');
      extras = `<ul class="search-list">${items}</ul>`;
    }
    startTyping(text, extras);
  }

  // State chips are view-only indicators — no click handlers.
  chips.forEach(c => { c.style.cursor = 'default'; c.setAttribute('tabindex', '-1'); c.setAttribute('aria-disabled', 'true'); });

  // Track whether the user is mid-typing so we can return to idle when they stop / clear input.
  let typingIdleTimer = null;
  function onTypingActivity() {
    if (body.dataset.state === 'replying') return; // don't interrupt a reply
    const hasText = promptInput.value.trim().length > 0;
    if (hasText) {
      if (body.dataset.state !== 'listening') setState('listening');
    } else if (body.dataset.state === 'listening') {
      // input was cleared — go back to idle
      setState('idle');
    }
    clearTimeout(typingIdleTimer);
    // if user pauses typing for a while with empty input, ensure idle
    typingIdleTimer = setTimeout(() => {
      if (!promptInput.value.trim() && body.dataset.state === 'listening' && chatLog.children.length === 0) setState('idle');
    }, 1800);
  }
  promptInput.addEventListener('input', onTypingActivity);

  mic.addEventListener('click', () => {
    if (body.dataset.state === 'replying') return;
    clearTimeout(typingIdleTimer);

    // Stop if already listening
    if (recognizing && recognition) {
      recognition.stop();
      return;
    }
    if (body.dataset.state === 'listening') {
      setState('idle');
      return;
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      // Browser doesn't support speech recognition — toggle state visually only
      setState('listening');
      return;
    }

    recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => { recognizing = true; };

    // Show listening indicator immediately
    transcript.hidden = false;
    transcript.classList.remove('empty');
    const listeningBody = createMsg('You', '<span class="cursor"></span> listening…', true);

    recognition.onstart = () => { recognizing = true; };

    recognition.onresult = async e => {
      const text = e.results[0][0].transcript.trim();
      if (!text) {
        listeningBody.closest('.msg').remove();
        setState('idle');
        return;
      }
      listeningBody.textContent = text;

      const t0 = Date.now();
      setState('replying');
      try {
        const result = await sendChat(text);
        const wait = Math.max(0, 820 - (Date.now() - t0));
        setTimeout(() => startReply(result), wait);
      } catch {
        setTimeout(() => startTyping("Beemo is offline — start the server first."), Math.max(0, 820 - (Date.now() - t0)));
      }
    };

    recognition.onerror = () => {
      recognizing = false;
      listeningBody.closest('.msg').remove();
      if (chatLog.children.length === 0) { transcript.hidden = true; transcript.classList.add('empty'); }
      setState('idle');
    };
    recognition.onend = () => {
      recognizing = false;
      if (body.dataset.state === 'listening') {
        listeningBody.closest('.msg').remove();
        setState('idle');
      }
    };

    setState('listening');
    recognition.start();
  });

  dock.addEventListener('submit', async e => {
    e.preventDefault();
    const v = promptInput.value.trim();
    if (!v) return;

    // Show user message
    transcript.hidden = false;
    transcript.classList.remove('empty');
    createMsg('You', v);
    promptInput.value = '';

    // Start fetch immediately while the user sees their message
    const fetchPromise = sendChat(v);

    // After 450ms, animate into replying state
    await new Promise(r => setTimeout(r, 450));
    setState('replying'); // white flash (~360ms) then applyState

    try {
      const [result] = await Promise.all([
        fetchPromise,
        new Promise(r => setTimeout(r, 400)), // let state transition finish
      ]);
      startReply(result);
    } catch {
      startTyping("Beemo is offline — start the server first.");
    }
  });

  promptInput.addEventListener('focus', () => dock.classList.add('dock-focus'));
  promptInput.addEventListener('blur', () => {
    dock.classList.remove('dock-focus');
    if (!promptInput.value.trim() && body.dataset.state === 'listening' && chatLog.children.length === 0) setState('idle');
  });

  document.querySelectorAll('.suggest button').forEach(b => {
    b.addEventListener('click', () => {
      promptInput.value = b.textContent;
      promptInput.focus();
    });
  });

  /* ---------- Tweaks ---------- */
  const tGlow = document.getElementById('tGlow');
  const tMotion = document.getElementById('tMotion');
  const tParticles = document.getElementById('tParticles');
  tGlow && tGlow.addEventListener('input', e => {
    document.documentElement.style.setProperty('--glow-mult', e.target.value / 60);
    const halo = document.querySelector('.halo');
    if (halo) halo.style.opacity = 0.25 + (e.target.value / 100) * 0.7;
  });
  tMotion && tMotion.addEventListener('input', e => {
    document.documentElement.style.setProperty('--motion-mult', 0.4 + (e.target.value / 100) * 1.6);
  });
  tParticles && tParticles.addEventListener('input', e => {
    window.__setParticles(parseInt(e.target.value, 10));
  });
  document.querySelectorAll('.tweaks .swatches button').forEach(b => {
    b.addEventListener('click', () => setState(b.dataset.theme));
  });

  /* ---------- Parallax (rAF-throttled) ---------- */
  const cards = document.querySelectorAll('.card');
  const orb = document.querySelector('.orb');
  let mx = 0, my = 0, parallaxRAF = 0, parallaxPending = false;
  function applyParallax() {
    parallaxPending = false;
    for (let i = 0; i < cards.length; i++) {
      const f = (i % 2 === 0 ? 1 : -1) * (8 + i * 2);
      cards[i].style.transform = `translate3d(${mx * f}px, ${my * f}px, 0)`;
    }
    if (orb) orb.style.transform = `translate3d(${mx * -14}px, ${my * -14}px, 0)`;
  }
  addEventListener('mousemove', e => {
    mx = e.clientX / innerWidth - 0.5;
    my = e.clientY / innerHeight - 0.5;
    if (!parallaxPending) {
      parallaxPending = true;
      parallaxRAF = requestAnimationFrame(applyParallax);
    }
  }, { passive: true });

  /* ---------- Clock ---------- */
  const clock = document.getElementById('clock');
  function tickClock() {
    if (!clock) return;
    clock.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  tickClock();
  setInterval(tickClock, 30000);

  /* ---------- Arrival animation ---------- */
  if (sessionStorage.getItem('beemo:arriving') === '1') {
    sessionStorage.removeItem('beemo:arriving');
    document.body.classList.add('arriving');
    setTimeout(() => document.body.classList.remove('arriving'), 2400);
  }
})();
