/* Beemo Auth — mode switching, validation, providers */
(() => {
  'use strict';

  const body = document.body;
  const title = document.getElementById('title');
  const lede = document.getElementById('lede');
  const tabs = document.querySelectorAll('.tabs button');
  const form = document.getElementById('authForm');
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  const name = document.getElementById('name');
  const emailHint = document.getElementById('emailHint');
  const strength = document.getElementById('strength');
  const submitBtn = document.getElementById('submitBtn');
  const togglePw = document.getElementById('togglePw');

  const COPY = {
    login: { title: 'Welcome back.', lede: "Sign in to your Beemo. We'll have everything just as you left it." },
    signup: { title: 'Begin orbiting.', lede: 'Create a Beemo account — your ambient companion, calibrated to you.' }
  };

  function setMode(mode) {
    body.dataset.mode = mode;
    tabs.forEach(t => t.classList.toggle('active', t.dataset.mode === mode));
    title.textContent = COPY[mode].title;
    lede.textContent = COPY[mode].lede;
    document.querySelectorAll('[data-login-text]').forEach(el => el.style.display = mode === 'login' ? '' : 'none');
    document.querySelectorAll('[data-signup-text]').forEach(el => el.style.display = mode === 'signup' ? '' : 'none');
    document.querySelectorAll('[data-login-only]').forEach(el => el.style.display = mode === 'login' ? '' : 'none');
    password.autocomplete = mode === 'login' ? 'current-password' : 'new-password';
    // keep URL in sync without reload
    const u = new URL(location.href);
    u.searchParams.set('m', mode);
    history.replaceState(null, '', u);
  }

  // initial mode from query
  const initial = new URLSearchParams(location.search).get('m') === 'signup' ? 'signup' : 'login';
  setMode(initial);

  tabs.forEach(t => t.addEventListener('click', () => setMode(t.dataset.mode)));
  document.querySelectorAll('[data-go]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); setMode(a.dataset.go); }));

  // password show/hide
  togglePw.addEventListener('click', () => {
    const isPw = password.type === 'password';
    password.type = isPw ? 'text' : 'password';
    togglePw.setAttribute('aria-label', isPw ? 'Hide password' : 'Show password');
  });

  // email hint
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  email.addEventListener('input', () => {
    const v = email.value.trim();
    email.parentElement.classList.remove('error');
    if (!v) { emailHint.textContent = ''; emailHint.className = 'hint'; return; }
    if (emailRe.test(v)) { emailHint.textContent = 'Looks valid'; emailHint.className = 'hint ok'; }
    else { emailHint.textContent = 'Use a full email address'; emailHint.className = 'hint bad'; }
  });

  // strength meter
  function score(pw) {
    let s = 0;
    if (pw.length >= 8) s++;
    if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) s++;
    if (/\d/.test(pw)) s++;
    if (/[^A-Za-z0-9]/.test(pw)) s++;
    return s;
  }
  password.addEventListener('input', () => {
    if (body.dataset.mode !== 'signup') return;
    const s = score(password.value);
    strength.className = 'strength s' + s;
  });

  // submit
  form.addEventListener('submit', e => {
    e.preventDefault();
    const v = email.value.trim();
    let ok = true;
    if (!emailRe.test(v)) { email.parentElement.classList.add('error'); ok = false; }
    else email.parentElement.classList.remove('error');
    if (password.value.length < 8) { password.parentElement.classList.add('error'); ok = false; }
    else password.parentElement.classList.remove('error');
    if (body.dataset.mode === 'signup' && !name.value.trim()) {
      name.parentElement.classList.add('error'); ok = false;
    } else if (name) name.parentElement.classList.remove('error');
    if (!ok) return;

    submitBtn.disabled = true;
    // mock "auth" — replace with real call. Routes to the app with the same arrival animation.
    setTimeout(() => {
      sessionStorage.setItem('beemo:arriving', '1');
      sessionStorage.setItem('beemo:user', JSON.stringify({ email: v, name: name?.value || '' }));
      location.href = 'Beemo App.html';
    }, 900);
  });

  // providers — placeholder OAuth handoff (each would normally redirect to its IdP)
  document.querySelectorAll('.provider').forEach(p => {
    p.addEventListener('click', () => {
      const prov = p.dataset.prov;
      p.style.pointerEvents = 'none';
      p.style.opacity = '.6';
      // In production: window.location = '/oauth/' + prov;
      setTimeout(() => {
        sessionStorage.setItem('beemo:arriving', '1');
        sessionStorage.setItem('beemo:user', JSON.stringify({ provider: prov }));
        location.href = 'Beemo App.html';
      }, 700);
    });
  });
})();
