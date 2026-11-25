// ── Navbar scroll effect ─────────────────────────────────────
window.addEventListener('scroll', () => {
  const nav = document.querySelector('.navbar');
  if (nav) nav.classList.toggle('scrolled', window.scrollY > 50);
});

// ── Hamburger menu ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.getElementById('hamburger');
  const navLinks  = document.querySelector('.nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('mobile-open');
      hamburger.classList.toggle('open');
    });
  }

  // Auto-close flash messages
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      alert.style.transition = 'all 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });

  // Close buttons on alerts
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
      }
    });
  });

  // ── Dropdown toggle ─────────────────────────────────────────
  document.querySelectorAll('[data-dropdown]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const target = document.querySelector(trigger.dataset.dropdown);
      if (target) target.classList.toggle('show');
    });
  });
  document.addEventListener('click', () => {
    document.querySelectorAll('.dropdown-menu.show').forEach(m => m.classList.remove('show'));
  });

  // ── Counter animation ────────────────────────────────────────
  const counters = document.querySelectorAll('[data-count]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(c => observer.observe(c));

  // ── Animate on scroll ────────────────────────────────────────
  const animEls = document.querySelectorAll('.animate-fade-up');
  const animObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });
  animEls.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    animObs.observe(el);
  });

  // ── Property Type Filter ─────────────────────────────────────
  document.querySelectorAll('.type-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // ── Star Rating ──────────────────────────────────────────────
  document.querySelectorAll('.star-rating').forEach(container => {
    const stars = container.querySelectorAll('.star-input');
    stars.forEach((star, idx) => {
      star.addEventListener('mouseover', () => highlightStars(stars, idx));
      star.addEventListener('click', () => setStars(stars, idx));
      container.addEventListener('mouseleave', () => restoreStars(stars));
    });
  });

  // ── Image preview ────────────────────────────────────────────
  const imgInput = document.getElementById('imageInput');
  if (imgInput) {
    imgInput.addEventListener('change', (e) => {
      const preview = document.getElementById('imagePreview');
      if (!preview) return;
      preview.innerHTML = '';
      Array.from(e.target.files).forEach(file => {
        const reader = new FileReader();
        reader.onload = ev => {
          const div = document.createElement('div');
          div.className = 'preview-thumb';
          div.innerHTML = `<img src="${ev.target.result}" alt="Preview" style="width:100px;height:80px;object-fit:cover;border-radius:8px;">`;
          preview.appendChild(div);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  // ── Confirm delete ───────────────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm || 'Are you sure?')) e.preventDefault();
    });
  });

  // ── File upload drag & drop ──────────────────────────────────
  const uploadAreas = document.querySelectorAll('.file-upload-area');
  uploadAreas.forEach(area => {
    area.addEventListener('dragover', e => { e.preventDefault(); area.classList.add('dragover'); });
    area.addEventListener('dragleave', () => area.classList.remove('dragover'));
    area.addEventListener('drop', e => {
      e.preventDefault(); area.classList.remove('dragover');
      const input = area.querySelector('input[type="file"]');
      if (input) { input.files = e.dataTransfer.files; input.dispatchEvent(new Event('change')); }
    });
    area.addEventListener('click', () => area.querySelector('input[type="file"]')?.click());
  });

  // ── Chart defaults ───────────────────────────────────────────
  if (window.Chart) {
    Chart.defaults.color = '#9ea3b0';
    Chart.defaults.font.family = "'Outfit', sans-serif";
    Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';
  }
});

// ── Helper: counter animation ────────────────────────────────
function animateCounter(el) {
  const target = parseInt(el.dataset.count, 10);
  const duration = 1800;
  const start = performance.now();
  const update = (now) => {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(eased * target).toLocaleString() + (el.dataset.suffix || '');
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

// ── Helper: star rating ──────────────────────────────────────
function highlightStars(stars, idx) {
  stars.forEach((s, i) => s.classList.toggle('hovered', i <= idx));
}
function setStars(stars, idx) {
  stars.forEach((s, i) => { s.classList.toggle('selected', i <= idx); s.dataset.selected = i <= idx; });
  const container = stars[0].closest('.star-rating');
  const input = container?.querySelector('input[type="hidden"]');
  if (input) input.value = idx + 1;
}
function restoreStars(stars) {
  stars.forEach(s => s.classList.remove('hovered'));
}

// ── Format currency (PKR) ────────────────────────────────────
function formatPKR(amount) {
  if (amount >= 10000000) return (amount / 10000000).toFixed(1) + ' Cr';
  if (amount >= 100000)   return (amount / 100000).toFixed(1) + ' Lac';
  return amount.toLocaleString('en-PK');
}

// ── Active nav link ───────────────────────────────────────────
document.querySelectorAll('.dash-nav-item').forEach(item => {
  if (item.href && window.location.pathname.startsWith(new URL(item.href, location).pathname)) {
    item.classList.add('active');
  }
});


/* ═══════════════════════════════════════════════════════════
   UI ENHANCEMENTS (visual/UX only — no data or logic changes)
═══════════════════════════════════════════════════════════ */
(function () {
  document.documentElement.classList.add('js-ready');

  function onReady(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  onReady(function () {
    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ── Scroll progress bar + back-to-top ──────────────────────
    var bar = document.createElement('div');
    bar.className = 'scroll-progress';
    document.body.appendChild(bar);

    var btt = document.createElement('button');
    btt.type = 'button';
    btt.className = 'back-to-top';
    btt.setAttribute('aria-label', 'Back to top');
    btt.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
    btt.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
    document.body.appendChild(btt);

    var ticking = false;
    function onScroll() {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
      btt.classList.toggle('show', h.scrollTop > 600);
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
    }, { passive: true });
    onScroll();

    // ── Staggered scroll-reveal for cards ──────────────────────
    var selector = '.prop-card,.agent-card,.testimonial-card,.blog-card,.type-card,.stat-card,.stats-item,.sidebar-widget,.chart-card';
    var items = Array.prototype.slice.call(document.querySelectorAll(selector)).filter(function (el) {
      return !el.classList.contains('animate-fade-up') && !el.closest('.animate-fade-up');
    });
    if ('IntersectionObserver' in window && !reduceMotion) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var el = e.target;
          el.classList.add('in-view');
          io.unobserve(el);
          var delay = parseInt(el.getAttribute('data-reveal-delay'), 10) || 0;
          // Remove helper classes after the animation so normal hover effects work again
          setTimeout(function () { el.classList.remove('reveal', 'in-view'); }, 900 + delay);
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
      items.forEach(function (el) {
        var idx = el.parentNode ? Array.prototype.indexOf.call(el.parentNode.children, el) : 0;
        var delay = (idx % 4) * 70;
        el.setAttribute('data-reveal-delay', delay);
        el.style.setProperty('--reveal-delay', delay + 'ms');
        el.classList.add('reveal');
        io.observe(el);
      });
    }

    // ── Images: lazy-load + graceful fallback if a photo is missing ──
    var FALLBACK = 'data:image/svg+xml;utf8,' + encodeURIComponent(
      "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 260'>" +
      "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>" +
      "<stop offset='0' stop-color='#1a1e28'/><stop offset='1' stop-color='#0d0f14'/></linearGradient></defs>" +
      "<rect width='400' height='260' fill='url(#g)'/>" +
      "<g fill='none' stroke='#c9a84c' stroke-width='3' stroke-linejoin='round' opacity='.65'>" +
      "<path d='M150 140 L200 100 L250 140 V185 H150 Z'/><path d='M185 185 V155 H215 V185'/></g></svg>"
    );
    function applyFallback(img) {
      if (img.dataset.fallback) return;
      img.dataset.fallback = '1';
      img.classList.add('img-fallback');
      img.src = FALLBACK;
    }
    document.addEventListener('error', function (e) {
      var t = e.target;
      if (t && t.tagName === 'IMG') applyFallback(t);
    }, true);
    Array.prototype.forEach.call(document.querySelectorAll('img'), function (img) {
      if (!img.hasAttribute('loading')) img.loading = 'lazy';
      img.decoding = 'async';
      if (img.complete && img.naturalWidth === 0 && img.getAttribute('src')) applyFallback(img);
    });

    // ── Form submit: loading state to prevent double-clicks ────
    function resetLoading() {
      Array.prototype.forEach.call(document.querySelectorAll('[data-loading]'), function (b) {
        b.disabled = false;
        b.innerHTML = b.dataset.label;
        b.classList.remove('is-loading');
        delete b.dataset.loading;
      });
    }
    Array.prototype.forEach.call(document.querySelectorAll('form'), function (f) {
      f.addEventListener('submit', function () {
        if (f.target === '_blank') return;
        var btn = f.querySelector('button[type="submit"]:not([name]), button:not([type]):not([name])');
        if (!btn || btn.dataset.loading) return;
        setTimeout(function () {
          btn.dataset.loading = '1';
          btn.dataset.label = btn.innerHTML;
          btn.classList.add('is-loading');
          btn.innerHTML = '<span class="spinner"></span> Please wait…';
          btn.disabled = true;
          setTimeout(resetLoading, 10000);   // safety net
        }, 0);
      });
    });
    window.addEventListener('pageshow', function (e) { if (e.persisted) resetLoading(); });

    // ── Navbar: highlight current page, close mobile menu nicely ──
    var path = location.pathname.replace(/\/$/, '') || '/';
    var navLinks = document.querySelector('.nav-links');
    Array.prototype.forEach.call(document.querySelectorAll('.nav-links a[href]'), function (a) {
      try {
        var p = new URL(a.href, location.href).pathname.replace(/\/$/, '') || '/';
        if (p === path || (p !== '/' && path.indexOf(p + '/') === 0)) a.classList.add('active');
      } catch (err) { /* ignore bad hrefs */ }
      a.addEventListener('click', function () {
        var hb = document.getElementById('hamburger');
        if (navLinks) navLinks.classList.remove('mobile-open');
        if (hb) hb.classList.remove('open');
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var hb = document.getElementById('hamburger');
      if (navLinks) navLinks.classList.remove('mobile-open');
      if (hb) hb.classList.remove('open');
    });
  });
})();
