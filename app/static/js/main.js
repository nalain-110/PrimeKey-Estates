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
