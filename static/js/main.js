/* ============================================================
   main.js — Praveen K Portfolio · Full-Stack JS Layer
   ============================================================ */

'use strict';

/* ──────────────── LOADING SCREEN ──────────────── */
window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    const loader = document.getElementById('loader');
    if (loader) loader.classList.add('hidden');
    setTimeout(() => { if (loader) loader.remove(); }, 700);
  }, 1800);
});

/* ──────────────── THEME MANAGEMENT ──────────────── */
const savedTheme = localStorage.getItem('portfolio-theme') || 'dark';
document.body.setAttribute('data-theme', savedTheme);
updateThemeButtons(savedTheme);

function setTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem('portfolio-theme', theme);
  updateThemeButtons(theme);
  initCanvasParticles();
  trackEvent('theme_change', { theme });
}

function updateThemeButtons(theme) {
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.theme === theme);
  });
}

document.querySelectorAll('.theme-btn').forEach(btn => {
  btn.addEventListener('click', () => setTheme(btn.dataset.theme));
});

/* ──────────────── PAGE PROGRESS BAR ──────────────── */
const progressBar = document.getElementById('pageProgress');
window.addEventListener('scroll', () => {
  if (!progressBar) return;
  const scrolled = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
  progressBar.style.width = Math.min(scrolled, 100) + '%';
}, { passive: true });

/* ──────────────── CUSTOM CURSOR ──────────────── */
const cursorDot  = document.getElementById('cursorDot');
const cursorRing = document.getElementById('cursorRing');
let mouseX = 0, mouseY = 0, ringX = 0, ringY = 0;

document.addEventListener('mousemove', e => {
  mouseX = e.clientX; mouseY = e.clientY;
  if (cursorDot) { cursorDot.style.left = mouseX + 'px'; cursorDot.style.top = mouseY + 'px'; }
});

function animateCursor() {
  ringX += (mouseX - ringX) * 0.15;
  ringY += (mouseY - ringY) * 0.15;
  if (cursorRing) { cursorRing.style.left = ringX + 'px'; cursorRing.style.top = ringY + 'px'; }
  requestAnimationFrame(animateCursor);
}
animateCursor();

document.querySelectorAll('a, button, .btn, .project-card, .stat-card, .skill-chip, .contact-card, .theme-btn, input, textarea').forEach(el => {
  el.addEventListener('mouseenter', () => cursorRing?.classList.add('hover'));
  el.addEventListener('mouseleave', () => cursorRing?.classList.remove('hover'));
});

/* ──────────────── NAVBAR ──────────────── */
const navbar     = document.getElementById('navbar');
const hamburger  = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const sections   = document.querySelectorAll('section[id]');

window.addEventListener('scroll', () => {
  navbar?.classList.toggle('scrolled', window.scrollY > 50);
  let current = '';
  sections.forEach(s => { if (window.scrollY >= s.offsetTop - 200) current = s.id; });
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === '#' + current);
  });
}, { passive: true });

hamburger?.addEventListener('click', () => {
  hamburger.classList.toggle('active');
  mobileMenu?.classList.toggle('active');
});

mobileMenu?.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    hamburger?.classList.remove('active');
    mobileMenu.classList.remove('active');
  });
});

/* ──────────────── SMOOTH SCROLL ──────────────── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(a.getAttribute('href'));
    if (target) window.scrollTo({ top: target.offsetTop - 80, behavior: 'smooth' });
  });
});

/* ──────────────── RIPPLE EFFECT ──────────────── */
function createRipple(e) {
  const btn  = e.currentTarget;
  const ripple = document.createElement('span');
  const rect = btn.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  ripple.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - rect.left - size/2}px;top:${e.clientY - rect.top - size/2}px`;
  ripple.classList.add('ripple');
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 600);
}

/* ──────────────── SCROLL REVEAL ──────────────── */
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 80);
      revealObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .timeline-item').forEach(el => revealObs.observe(el));

/* ──────────────── SECTION VIEW TRACKING ──────────────── */
const sectionObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) trackEvent('section_view', { section: entry.target.id });
  });
}, { threshold: 0.4 });
sections.forEach(s => sectionObs.observe(s));

/* ──────────────── ANIMATED COUNTERS ──────────────── */
const counterObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const el = entry.target;
    const target = parseInt(el.dataset.count);
    let current  = 0;
    const step   = Math.max(1, Math.floor(target / 40));
    const timer  = setInterval(() => {
      current += step;
      if (current >= target) { current = target; clearInterval(timer); }
      el.textContent = current + '+';
    }, 40);
    counterObs.unobserve(el);
  });
}, { threshold: 0.5 });
document.querySelectorAll('.stat-number[data-count]').forEach(el => counterObs.observe(el));

/* ──────────────── SKILL BARS ──────────────── */
const skillObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.style.width = entry.target.dataset.width + '%';
    skillObs.unobserve(entry.target);
  });
}, { threshold: 0.3 });
document.querySelectorAll('.skill-fill').forEach(el => skillObs.observe(el));

/* ──────────────── 3D CARD TILT ──────────────── */
document.querySelectorAll('.stat-card, .project-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const r = card.getBoundingClientRect();
    const x = e.clientX - r.left, y = e.clientY - r.top;
    const cx = r.width / 2,       cy = r.height / 2;
    const rx = (y - cy) / cy * -5, ry = (x - cx) / cx * 5;
    card.style.transform = `perspective(1000px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-5px)`;
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
  });
});

/* ──────────────── PARALLAX MOUSE ──────────────── */
document.addEventListener('mousemove', e => {
  const mx = (e.clientX / window.innerWidth - 0.5) * 2;
  const my = (e.clientY / window.innerHeight - 0.5) * 2;
  document.querySelectorAll('.floating-shape').forEach((el, i) => {
    const spd = (i + 1) * 8;
    el.style.transform = `translate(${mx * spd}px, ${my * spd}px) rotate(${mx * 20}deg)`;
  });
});

/* ──────────────── PROJECTS HORIZONTAL SCROLL ──────────────── */
const projectsGrid = document.getElementById('projectsGrid');
const projProgress = document.getElementById('projectsProgress');
const projectCards = projectsGrid ? projectsGrid.querySelectorAll('.project-card') : [];

function updateProjectCards() {
  if (!projectsGrid) return;
  const sl = projectsGrid.scrollLeft;
  const sw = projectsGrid.scrollWidth - projectsGrid.clientWidth;
  if (projProgress) projProgress.style.width = (sw > 0 ? sl / sw * 100 : 0) + '%';
  const cr = projectsGrid.getBoundingClientRect();
  const cc = cr.left + cr.width / 2;
  projectCards.forEach(card => {
    const cardRect   = card.getBoundingClientRect();
    const cardCenter = cardRect.left + cardRect.width / 2;
    const dist       = cardCenter - cc;
    const maxDist    = cr.width * 0.7;
    const ratio      = Math.max(-1, Math.min(1, dist / maxDist));
    const rotY  = ratio * 25, rotX = Math.abs(ratio) * -3;
    const transZ = -Math.abs(ratio) * 60;
    const scale = 1 - Math.abs(ratio) * 0.12;
    const opacity = 1 - Math.abs(ratio) * 0.35;
    card.style.transform = `perspective(1200px) rotateY(${rotY}deg) rotateX(${rotX}deg) translateZ(${transZ}px) scale(${scale})`;
    card.style.opacity = Math.max(0.4, opacity);
  });
}

if (projectsGrid) {
  projectsGrid.addEventListener('scroll', updateProjectCards, { passive: true });
  setTimeout(updateProjectCards, 200);
  window.addEventListener('resize', updateProjectCards);
  projectsGrid.addEventListener('wheel', e => {
    if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
      e.preventDefault();
      projectsGrid.scrollBy({ left: e.deltaY * 2, behavior: 'auto' });
    }
  }, { passive: false });
}

/* ──────────────── PARTICLE CANVAS ──────────────── */
const bgCanvas = document.getElementById('bgCanvas');
const bgCtx    = bgCanvas?.getContext('2d');
let particles  = [];

function resizeCanvas() {
  if (!bgCanvas) return;
  bgCanvas.width  = window.innerWidth;
  bgCanvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas, { passive: true });

function getThemeColors() {
  const s = getComputedStyle(document.body);
  return {
    orb1: s.getPropertyValue('--orb1').trim(),
    orb2: s.getPropertyValue('--orb2').trim(),
    orb3: s.getPropertyValue('--orb3').trim(),
  };
}

function initCanvasParticles() {
  particles = [];
  const colors  = getThemeColors();
  const colorArr = [colors.orb1, colors.orb2, colors.orb3];
  for (let i = 0; i < 60; i++) {
    particles.push({
      x: Math.random() * (bgCanvas?.width || 1920),
      y: Math.random() * (bgCanvas?.height || 1080),
      size:   Math.random() * 2 + 0.5,
      speedX: (Math.random() - 0.5) * 0.4,
      speedY: (Math.random() - 0.5) * 0.4,
      color:  colorArr[Math.floor(Math.random() * 3)],
      opacity: Math.random() * 0.4 + 0.1,
    });
  }
}
initCanvasParticles();

function drawParticles() {
  if (!bgCtx || !bgCanvas) return;
  bgCtx.clearRect(0, 0, bgCanvas.width, bgCanvas.height);
  particles.forEach(p => {
    bgCtx.beginPath();
    bgCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    bgCtx.fillStyle = p.color;
    bgCtx.globalAlpha = p.opacity;
    bgCtx.fill();
    p.x += p.speedX; p.y += p.speedY;
    if (p.x < 0) p.x = bgCanvas.width;
    if (p.x > bgCanvas.width)  p.x = 0;
    if (p.y < 0) p.y = bgCanvas.height;
    if (p.y > bgCanvas.height) p.y = 0;
  });
  bgCtx.globalAlpha = 1;
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const d  = Math.sqrt(dx * dx + dy * dy);
      if (d < 120) {
        bgCtx.beginPath();
        bgCtx.moveTo(particles[i].x, particles[i].y);
        bgCtx.lineTo(particles[j].x, particles[j].y);
        bgCtx.strokeStyle = particles[i].color;
        bgCtx.globalAlpha = (1 - d / 120) * 0.08;
        bgCtx.lineWidth = 0.5;
        bgCtx.stroke();
      }
    }
  }
  bgCtx.globalAlpha = 1;
  requestAnimationFrame(drawParticles);
}
drawParticles();

/* ──────────────── 3D FLOATING CHARTS CANVAS ──────────────── */
const canvas3D = document.getElementById('bgCanvas3D');
const ctx3D    = canvas3D?.getContext('2d');
let floatingCharts = [];

function resize3D() {
  if (!canvas3D) return;
  canvas3D.width  = window.innerWidth;
  canvas3D.height = window.innerHeight;
}
resize3D();
window.addEventListener('resize', resize3D, { passive: true });

function getChartColors() {
  const s = getComputedStyle(document.body);
  return {
    accent: s.getPropertyValue('--accent').trim(),
    accent2: s.getPropertyValue('--accent2').trim(),
    orb1:   s.getPropertyValue('--orb1').trim(),
    orb2:   s.getPropertyValue('--orb2').trim(),
    orb3:   s.getPropertyValue('--orb3').trim(),
    text:   s.getPropertyValue('--text-muted').trim(),
    border: s.getPropertyValue('--glass-border').trim(),
  };
}

function initFloatingCharts() {
  floatingCharts = [];
  const types = ['bar','pie','line','scatter','radar','donut','area','histogram','candlestick','gauge'];
  const count = Math.min(12, Math.max(7, Math.floor(window.innerWidth / 160)));
  for (let i = 0; i < count; i++) {
    const sz = Math.random() * 40 + 45;
    floatingCharts.push({
      x: Math.random() * (canvas3D?.width || 1920),
      y: Math.random() * (canvas3D?.height || 1080),
      size: sz, type: types[i % types.length],
      rotation: Math.random() * Math.PI * 2, rotSpeed: (Math.random() - 0.5) * 0.004,
      tilt: Math.random() * 0.4 + 0.6, speedX: (Math.random() - 0.5) * 0.25, speedY: (Math.random() - 0.5) * 0.25,
      opacity: Math.random() * 0.12 + 0.06, phase: Math.random() * Math.PI * 2,
      data: Array.from({length: Math.floor(Math.random()*4)+4}, () => Math.random()*0.8+0.2),
      bobSpeed: Math.random() * 0.008 + 0.004, bobAmp: Math.random() * 8 + 4, time: 0,
    });
  }
}
initFloatingCharts();

function drawChart(ctx, c, colors) {
  switch(c.type) {
    case 'bar':         drawBar(ctx, c, colors); break;
    case 'pie':         drawPie(ctx, c, colors); break;
    case 'donut':       drawDonut(ctx, c, colors); break;
    case 'line':        drawLine(ctx, c, colors); break;
    case 'area':        drawArea(ctx, c, colors); break;
    case 'scatter':     drawScatter(ctx, c, colors); break;
    case 'radar':       drawRadar(ctx, c, colors); break;
    case 'histogram':   drawHistogram(ctx, c, colors); break;
    case 'candlestick': drawCandlestick(ctx, c, colors); break;
    case 'gauge':       drawGauge(ctx, c, colors); break;
  }
}

function drawBar(ctx, c, colors) {
  const s = c.size, bars = c.data.length, bw = (s*1.6)/bars*0.65, gap = (s*1.6)/bars*0.35;
  const depth = 6*c.tilt, cols = [colors.accent,colors.accent2,colors.orb2,colors.orb3,colors.orb1];
  ctx.strokeStyle = colors.border; ctx.lineWidth = 0.8;
  ctx.beginPath(); ctx.moveTo(-s*0.8,s*0.5); ctx.lineTo(s*0.8,s*0.5); ctx.moveTo(-s*0.8,-s*0.5); ctx.lineTo(-s*0.8,s*0.5); ctx.stroke();
  c.data.forEach((v,i) => {
    const x = -s*0.8+i*(bw+gap)+gap/2, h = v*s*0.9, col = cols[i%cols.length];
    ctx.fillStyle=col; ctx.globalAlpha=c.opacity*0.5;
    ctx.beginPath(); ctx.moveTo(x+bw,s*0.5-h); ctx.lineTo(x+bw+depth,s*0.5-h-depth*0.6); ctx.lineTo(x+bw+depth,s*0.5-depth*0.6); ctx.lineTo(x+bw,s*0.5); ctx.fill();
    ctx.globalAlpha=c.opacity*0.7;
    ctx.beginPath(); ctx.moveTo(x,s*0.5-h); ctx.lineTo(x+depth,s*0.5-h-depth*0.6); ctx.lineTo(x+bw+depth,s*0.5-h-depth*0.6); ctx.lineTo(x+bw,s*0.5-h); ctx.fill();
    ctx.globalAlpha=c.opacity; ctx.fillRect(x,s*0.5-h,bw,h);
    ctx.strokeStyle=col; ctx.lineWidth=0.5; ctx.strokeRect(x,s*0.5-h,bw,h);
  });
}
function drawPie(ctx, c, colors) {
  const s=c.size*0.6, cols=[colors.accent,colors.accent2,colors.orb2,colors.orb3,colors.orb1];
  const total=c.data.reduce((a,b)=>a+b,0); let angle=-Math.PI/2; const dh=8*c.tilt;
  c.data.forEach((v,i) => { const sl=(v/total)*Math.PI*2; ctx.fillStyle=cols[i%cols.length]; ctx.globalAlpha=c.opacity*0.4; ctx.beginPath(); ctx.moveTo(0,dh); ctx.arc(0,dh,s,angle,angle+sl); ctx.fill(); angle+=sl; });
  angle=-Math.PI/2;
  c.data.forEach((v,i) => { const sl=(v/total)*Math.PI*2; ctx.fillStyle=cols[i%cols.length]; ctx.globalAlpha=c.opacity; ctx.beginPath(); ctx.moveTo(0,0); ctx.arc(0,0,s,angle,angle+sl); ctx.closePath(); ctx.fill(); ctx.strokeStyle=colors.border; ctx.lineWidth=0.5; ctx.stroke(); angle+=sl; });
}
function drawDonut(ctx, c, colors) {
  const outer=c.size*0.6, inner=c.size*0.32, cols=[colors.accent,colors.accent2,colors.orb2,colors.orb3,colors.orb1];
  const total=c.data.reduce((a,b)=>a+b,0); let angle=-Math.PI/2+c.time*0.3;
  c.data.forEach((v,i) => { const sl=(v/total)*Math.PI*2; ctx.fillStyle=cols[i%cols.length]; ctx.globalAlpha=c.opacity; ctx.beginPath(); ctx.arc(0,0,outer,angle,angle+sl); ctx.arc(0,0,inner,angle+sl,angle,true); ctx.closePath(); ctx.fill(); ctx.strokeStyle=colors.border; ctx.lineWidth=0.4; ctx.stroke(); angle+=sl; });
}
function drawLine(ctx, c, colors) {
  const s=c.size, pts=c.data, w=s*1.6, h=s;
  ctx.strokeStyle=colors.border; ctx.lineWidth=0.6;
  ctx.beginPath(); ctx.moveTo(-w/2,h/2); ctx.lineTo(w/2,h/2); ctx.moveTo(-w/2,-h/2); ctx.lineTo(-w/2,h/2); ctx.stroke();
  ctx.globalAlpha=c.opacity*0.3; ctx.fillStyle=colors.accent;
  ctx.beginPath(); ctx.moveTo(-w/2,h/2);
  pts.forEach((v,i) => { const px=-w/2+(i/(pts.length-1))*w; ctx.lineTo(px,h/2-v*h); });
  ctx.lineTo(w/2,h/2); ctx.closePath(); ctx.fill();
  ctx.globalAlpha=c.opacity; ctx.strokeStyle=colors.accent; ctx.lineWidth=1.5; ctx.lineJoin='round';
  ctx.beginPath();
  pts.forEach((v,i) => { const px=-w/2+(i/(pts.length-1))*w; const py=h/2-v*h; i===0?ctx.moveTo(px,py):ctx.lineTo(px,py); });
  ctx.stroke();
  pts.forEach((v,i) => { const px=-w/2+(i/(pts.length-1))*w; const py=h/2-v*h; ctx.fillStyle=colors.accent2; ctx.beginPath(); ctx.arc(px,py,2.5,0,Math.PI*2); ctx.fill(); });
}
function drawArea(ctx, c, colors) {
  const s=c.size, pts=c.data, w=s*1.6, h=s;
  [colors.orb2,colors.accent].forEach((col,li) => {
    ctx.globalAlpha=c.opacity*0.25; ctx.fillStyle=col;
    ctx.beginPath(); ctx.moveTo(-w/2,h/2);
    pts.forEach((v,i) => { const off=li*0.15; const px=-w/2+(i/(pts.length-1))*w; ctx.lineTo(px,h/2-(v-off)*h*0.85); });
    ctx.lineTo(w/2,h/2); ctx.closePath(); ctx.fill();
    ctx.globalAlpha=c.opacity*0.8; ctx.strokeStyle=col; ctx.lineWidth=1;
    ctx.beginPath();
    pts.forEach((v,i) => { const off=li*0.15; const px=-w/2+(i/(pts.length-1))*w; const py=h/2-(v-off)*h*0.85; i===0?ctx.moveTo(px,py):ctx.lineTo(px,py); });
    ctx.stroke();
  });
}
function drawScatter(ctx, c, colors) {
  const s=c.size, w=s*1.5, h=s, cols=[colors.accent,colors.accent2,colors.orb2];
  ctx.strokeStyle=colors.border; ctx.lineWidth=0.6; ctx.globalAlpha=c.opacity*0.5;
  ctx.beginPath(); ctx.moveTo(-w/2,h/2); ctx.lineTo(w/2,h/2); ctx.moveTo(-w/2,-h/2); ctx.lineTo(-w/2,h/2); ctx.stroke();
  for(let i=0;i<14;i++){
    const px=-w/2+Math.sin(i*3.7+c.phase)*0.5*w+w/2; const py=h/2-Math.abs(Math.cos(i*2.3+c.phase))*h*0.85;
    ctx.fillStyle=cols[i%3]; ctx.globalAlpha=c.opacity*0.9;
    ctx.beginPath(); ctx.arc(px,py,2+Math.random(),0,Math.PI*2); ctx.fill();
  }
}
function drawRadar(ctx, c, colors) {
  const s=c.size*0.55, sides=c.data.length;
  ctx.strokeStyle=colors.border; ctx.lineWidth=0.4; ctx.globalAlpha=c.opacity*0.4;
  for(let ring=1;ring<=3;ring++){
    ctx.beginPath();
    for(let i=0;i<=sides;i++){ const a=(i*2*Math.PI/sides)-Math.PI/2; const r=s*ring/3; i===0?ctx.moveTo(Math.cos(a)*r,Math.sin(a)*r):ctx.lineTo(Math.cos(a)*r,Math.sin(a)*r); }
    ctx.closePath(); ctx.stroke();
  }
  for(let i=0;i<sides;i++){ const a=(i*2*Math.PI/sides)-Math.PI/2; ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(Math.cos(a)*s,Math.sin(a)*s); ctx.stroke(); }
  ctx.fillStyle=colors.accent; ctx.globalAlpha=c.opacity*0.3;
  ctx.beginPath();
  c.data.forEach((v,i) => { const a=(i*2*Math.PI/sides)-Math.PI/2; const r=v*s; i===0?ctx.moveTo(Math.cos(a)*r,Math.sin(a)*r):ctx.lineTo(Math.cos(a)*r,Math.sin(a)*r); });
  ctx.closePath(); ctx.fill(); ctx.strokeStyle=colors.accent; ctx.lineWidth=1.2; ctx.globalAlpha=c.opacity; ctx.stroke();
}
function drawHistogram(ctx, c, colors) {
  const s=c.size, bars=c.data.length, w=s*1.6, bw=w/bars;
  ctx.strokeStyle=colors.border; ctx.lineWidth=0.6; ctx.globalAlpha=c.opacity*0.5;
  ctx.beginPath(); ctx.moveTo(-w/2,s*0.5); ctx.lineTo(w/2,s*0.5); ctx.moveTo(-w/2,-s*0.5); ctx.lineTo(-w/2,s*0.5); ctx.stroke();
  c.data.forEach((v,i) => { const x=-w/2+i*bw; const h=v*s*0.9; ctx.fillStyle=i%2===0?colors.accent:colors.orb2; ctx.globalAlpha=c.opacity*0.8; ctx.fillRect(x+1,s*0.5-h,bw-2,h); ctx.strokeStyle=colors.border; ctx.lineWidth=0.3; ctx.strokeRect(x+1,s*0.5-h,bw-2,h); });
}
function drawCandlestick(ctx, c, colors) {
  const s=c.size, n=c.data.length, w=s*1.6, bw=w/n*0.5;
  ctx.strokeStyle=colors.border; ctx.lineWidth=0.5; ctx.globalAlpha=c.opacity*0.4;
  ctx.beginPath(); ctx.moveTo(-w/2,s*0.5); ctx.lineTo(w/2,s*0.5); ctx.stroke();
  c.data.forEach((v,i) => {
    const x=-w/2+(i+0.5)*(w/n); const open=v*s*0.6; const close=(v+(Math.sin(i*1.5+c.phase)>0?0.15:-0.15))*s*0.6;
    const high=Math.max(open,close)+6; const low=Math.min(open,close)-6; const bull=close>open;
    ctx.strokeStyle=bull?colors.accent:colors.orb3; ctx.lineWidth=0.8; ctx.globalAlpha=c.opacity;
    ctx.beginPath(); ctx.moveTo(x,s*0.5-high); ctx.lineTo(x,s*0.5-low); ctx.stroke();
    ctx.fillStyle=bull?colors.accent:colors.orb3; ctx.globalAlpha=c.opacity*0.8;
    ctx.fillRect(x-bw/2,s*0.5-Math.max(open,close),bw,Math.abs(close-open)||4);
  });
}
function drawGauge(ctx, c, colors) {
  const s=c.size*0.55; const val=c.data[0];
  ctx.strokeStyle=colors.border; ctx.lineWidth=6; ctx.globalAlpha=c.opacity*0.3; ctx.lineCap='round';
  ctx.beginPath(); ctx.arc(0,0,s,Math.PI*0.8,Math.PI*2.2); ctx.stroke();
  ctx.strokeStyle=colors.accent; ctx.lineWidth=6; ctx.globalAlpha=c.opacity;
  ctx.beginPath(); ctx.arc(0,0,s,Math.PI*0.8,Math.PI*0.8+val*Math.PI*1.4); ctx.stroke();
  const na=Math.PI*0.8+val*Math.PI*1.4;
  ctx.strokeStyle=colors.accent2; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(Math.cos(na)*s*0.7,Math.sin(na)*s*0.7); ctx.stroke();
  ctx.fillStyle=colors.accent; ctx.beginPath(); ctx.arc(0,0,3,0,Math.PI*2); ctx.fill();
}

function drawFloatingCharts() {
  if (!ctx3D || !canvas3D) return;
  ctx3D.clearRect(0, 0, canvas3D.width, canvas3D.height);
  const colors = getChartColors();
  floatingCharts.forEach(c => {
    c.time += 0.016;
    const bobY = Math.sin(c.time * c.bobSpeed * 60 + c.phase) * c.bobAmp;
    ctx3D.save();
    ctx3D.translate(c.x, c.y + bobY);
    ctx3D.rotate(c.rotation);
    ctx3D.scale(1, c.tilt);
    ctx3D.globalAlpha = c.opacity;
    drawChart(ctx3D, c, colors);
    ctx3D.restore();
    c.rotation += c.rotSpeed; c.x += c.speedX; c.y += c.speedY;
    if (c.x < -c.size*2) c.x = canvas3D.width + c.size*2;
    if (c.x > canvas3D.width + c.size*2) c.x = -c.size*2;
    if (c.y < -c.size*2) c.y = canvas3D.height + c.size*2;
    if (c.y > canvas3D.height + c.size*2) c.y = -c.size*2;
  });
  requestAnimationFrame(drawFloatingCharts);
}
drawFloatingCharts();

/* ──────────────── TOAST NOTIFICATION ──────────────── */
function showToast(message, type = 'success') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✓' : '✕'}</span> ${message}`;
  document.body.appendChild(toast);
  requestAnimationFrame(() => { requestAnimationFrame(() => toast.classList.add('show')); });
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

/* ──────────────── ANALYTICS TRACKING ──────────────── */
const _tracked = new Set();
function trackEvent(event, meta = {}) {
  const key = event + JSON.stringify(meta);
  if (_tracked.has(key)) return;
  _tracked.add(key);
  fetch('/api/analytics/track', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ event, meta }),
  }).catch(() => {});
}

// Track page view on load
trackEvent('page_view', { path: window.location.pathname });

/* ──────────────── CONTACT FORM ──────────────── */
const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name    = document.getElementById('formName').value.trim();
    const email   = document.getElementById('formEmail').value.trim();
    const message = document.getElementById('formMsg').value.trim();
    const submitBtn = contactForm.querySelector('button[type="submit"]');

    // Client-side validation
    let valid = true;
    [
      { id: 'formName',  val: name,    min: 2,   msg: 'Name must be at least 2 characters' },
      { id: 'formEmail', val: email,   min: 0,   msg: 'Please enter a valid email', email: true },
      { id: 'formMsg',   val: message, min: 10,  msg: 'Message must be at least 10 characters' },
    ].forEach(({ id, val, min, msg, email: isEmail }) => {
      const group = document.getElementById(id)?.closest('.form-group');
      const errEl = group?.querySelector('.form-error');
      const emailOk = isEmail ? /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(val) : true;
      const ok = val.length >= min && emailOk;
      group?.classList.toggle('error', !ok);
      if (errEl) errEl.textContent = msg;
      if (!ok) valid = false;
    });

    if (!valid) return;

    submitBtn.disabled    = true;
    submitBtn.textContent = 'Sending…';

    try {
      const res  = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, message }),
      });
      const data = await res.json();
      if (res.ok && data.success) {
        showToast(data.message || 'Message sent! I\'ll get back to you soon 🚀', 'success');
        contactForm.reset();
        trackEvent('contact_submit');
      } else {
        showToast(data.errors?.[0] || 'Something went wrong. Please try again.', 'error');
      }
    } catch {
      showToast('Network error. Please check your connection.', 'error');
    } finally {
      submitBtn.disabled    = false;
      submitBtn.textContent = 'Send Message →';
    }
  });
}

/* ──────────────── CHATBOT ──────────────── */
let chatOpen    = false;
let sessionId   = localStorage.getItem('chat_session') || '';
let chatHistory = [];

if (!sessionId) {
  sessionId = 'sess_' + Math.random().toString(36).slice(2);
  localStorage.setItem('chat_session', sessionId);
}

function toggleChatbot() {
  chatOpen = !chatOpen;
  document.getElementById('chatbotWindow')?.classList.toggle('active', chatOpen);
  const btn = document.getElementById('chatbotToggle');
  if (btn) btn.innerHTML = chatOpen ? '✕' : '💬<span class="badge-dot"></span>';
  if (chatOpen) trackEvent('chatbot_open');
}

function sendQuickReply(text) {
  const input = document.getElementById('chatInput');
  if (input) input.value = text;
  sendMessage();
}

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text  = (input?.value || '').trim();
  if (!text) return;
  if (input) input.value = '';

  // Hide quick replies after first message
  document.getElementById('quickReplies')?.style.setProperty('display', 'none');

  addChatMessage(text, 'user');
  showTyping();
  trackEvent('chatbot_message', { session: sessionId });

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });
    const data = await res.json();
    removeTyping();
    addChatMessage(data.reply || 'Sorry, I couldn\'t process that.', 'bot');
  } catch {
    removeTyping();
    addChatMessage('Sorry, I\'m having trouble connecting. Please try again!', 'bot');
  }
}

function addChatMessage(text, type) {
  const container = document.getElementById('chatMessages');
  if (!container) return;
  const msg = document.createElement('div');
  msg.className = 'chat-msg ' + type;
  msg.textContent = text;
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;
  chatHistory.push({ role: type === 'user' ? 'user' : 'model', content: text });
}

function showTyping() {
  const container = document.getElementById('chatMessages');
  if (!container) return;
  const el = document.createElement('div');
  el.className = 'typing-indicator'; el.id = 'typingIndicator';
  el.innerHTML = '<span></span><span></span><span></span>';
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
}

function removeTyping() {
  document.getElementById('typingIndicator')?.remove();
}

function exportChatHistory() {
  if (!chatHistory.length) { showToast('No chat history to export', 'error'); return; }
  const lines = chatHistory.map(m => `[${m.role.toUpperCase()}]: ${m.content}`).join('\n\n');
  const blob  = new Blob([`Praveen K — AI Assistant Chat History\n${'='.repeat(40)}\n\n${lines}`], { type: 'text/plain' });
  const link  = document.createElement('a');
  link.href   = URL.createObjectURL(blob);
  link.download = `chat_export_${new Date().toISOString().slice(0,10)}.txt`;
  link.click();
  showToast('Chat history downloaded!', 'success');
}

// Chatbot keyboard shortcut
document.getElementById('chatInput')?.addEventListener('keypress', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

/* ──────────────── RESUME DOWNLOAD + ANALYTICS ──────────────── */
function downloadResumePDF() {
  trackEvent('resume_download');

  // Create a hidden anchor pointing to the real PDF and trigger a download
  const link    = document.createElement('a');
  link.href     = '/static/resume/Praveen_K_resume.pdf';
  link.download = 'Praveen_K_Resume.pdf';
  link.style.display = 'none';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast('Resume downloaded successfully! 📄', 'success');
}
