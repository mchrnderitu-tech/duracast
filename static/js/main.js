/* =====================================================================
   BuildCorp — main.js
   Loaded with `defer` BEFORE Alpine, so Alpine.data()/store() calls below
   are registered before Alpine boots the tree.
   ===================================================================== */

(function () {
  'use strict';

  /* ------------------------------------------------------------------
     1. AOS — scroll-triggered animations
     ------------------------------------------------------------------ */
  function initAOS() {
    if (typeof AOS === 'undefined') return;
    AOS.init({
      duration: 700,
      easing: 'ease-out-cubic',
      once: true,
      offset: 80,
      disable: function () {
        // Respect the OS "reduce motion" preference.
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      }
    });
    // Recalculate after images/fonts settle.
    window.addEventListener('load', function () { AOS.refresh(); });
  }

  /* ------------------------------------------------------------------
     2. Smooth in-page anchors that respect the fixed header
     ------------------------------------------------------------------ */
  function initSmoothAnchors() {
    document.addEventListener('click', function (event) {
      const link = event.target.closest('a[href^="#"]');
      if (!link) return;
      const id = link.getAttribute('href');
      if (!id || id === '#' || id.length < 2) return;
      const target = document.querySelector(id);
      if (!target) return;
      event.preventDefault();
      const header = document.getElementById('site-header');
      const offset = (header ? header.offsetHeight : 72) + 12;
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: Math.max(top, 0), behavior: 'smooth' });
      history.replaceState(null, '', id);
    });
  }

  /* ------------------------------------------------------------------
     3. Lazy video autoplay guard (mobile data savers, autoplay policy)
     ------------------------------------------------------------------ */
  function initHeroVideo() {
    const video = document.querySelector('section video[autoplay]');
    if (!video) return;
    const attempt = video.play();
    if (attempt && typeof attempt.catch === 'function') {
      attempt.catch(function () {
        // Autoplay blocked — show the poster frame instead.
        video.removeAttribute('autoplay');
        video.setAttribute('controls', 'controls');
      });
    }
  }

  /* ------------------------------------------------------------------
     4. Alpine components
     ------------------------------------------------------------------ */
  document.addEventListener('alpine:init', function () {

    /* --- Projects gallery: filter + modal --------------------------- */
    Alpine.data('projectsGallery', function () {
      return {
        filter: 'all',
        active: null,
        projects: [],

        init() {
          const node = document.getElementById('projects-data');
          try {
            this.projects = node ? JSON.parse(node.textContent) : [];
          } catch (error) {
            console.warn('Could not parse project data:', error);
            this.projects = [];
          }
          // Lock body scroll while the modal is open.
          this.$watch('active', (value) => {
            document.body.classList.toggle('overflow-hidden', Boolean(value));
          });
        },

        get visible() {
          if (this.filter === 'all') return this.projects;
          return this.projects.filter((project) => project.category === this.filter);
        },

        open(project) { this.active = project; },
        close() { this.active = null; }
      };
    });

    /* --- Quote form: progressive client-side validation ------------- */
    Alpine.data('quoteForm', function () {
      return {
        loading: false,
        touched: {},
        fields: { full_name: '', email: '', phone: '', project_type: '', details: '' },

        touch(field) { this.touched[field] = true; },

        get errors() {
          const out = {};
          if (!this.fields.full_name || this.fields.full_name.trim().length < 2) {
            out.full_name = 'Please enter your full name.';
          }
          const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
          if (!emailPattern.test(this.fields.email || '')) {
            out.email = 'Please enter a valid email address.';
          }
          if (!this.fields.project_type) {
            out.project_type = 'Please choose a project type.';
          }
          if (!this.fields.details || this.fields.details.trim().length < 10) {
            out.details = 'Please give us at least a sentence about your project.';
          }
          return out;
        },

        errorFor(field) {
          return this.touched[field] ? (this.errors[field] || '') : '';
        },

        submit(event) {
          // Mark everything touched so any remaining problems become visible.
          Object.keys(this.fields).forEach((key) => { this.touched[key] = true; });
          if (Object.keys(this.errors).length > 0) {
            event.preventDefault();
            const firstInvalid = event.target.querySelector('input, select, textarea');
            if (firstInvalid) firstInvalid.focus();
            return;
          }
          // Valid → let the browser POST to Django (server-side validation still runs).
          this.loading = true;
        }
      };
    });

    /* --- Dashboard shell: mobile sidebar ---------------------------- */
    Alpine.data('dashboardShell', function () {
      return { open: false };
    });
  });

  /* ------------------------------------------------------------------
     6. Count-up animation for stats (data-counter attributes)
     ------------------------------------------------------------------ */
  function initCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    if (!counters.length) return;

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const animate = function (el) {
      const target = parseFloat(el.dataset.counter) || 0;
      const suffix = el.dataset.counterSuffix || '';
      const duration = 1600;
      const start = performance.now();

      function step(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        el.textContent = Math.floor(eased * target) + suffix;
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = target + suffix;
      }
      requestAnimationFrame(step);
    };

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting && !entry.target.dataset.counted) {
          entry.target.dataset.counted = 'true';
          animate(entry.target);
        }
      });
    }, { threshold: 0.4 });

    counters.forEach(function (el) { observer.observe(el); });
  }

  /* ------------------------------------------------------------------
     7. Pause Spline rendering when off-screen (WebGL perf)
     ------------------------------------------------------------------ */
  function initSplinePause() {
    const spline = document.querySelector('spline-viewer');
    if (!spline || !('IntersectionObserver' in window)) return;

    const obs = new IntersectionObserver(function (entries) {
      const entry = entries[0];
      if (entry.isIntersecting) spline.removeAttribute('hidden');
      else spline.setAttribute('hidden', '');
    }, { threshold: 0 });
    obs.observe(spline);
  }

  /* ------------------------------------------------------------------
     Boot
     ------------------------------------------------------------------ */
  function boot() {
    document.documentElement.classList.remove('no-js');
    initAOS();
    initSmoothAnchors();
    initHeroVideo();
    initCounters();
    initSplinePause();
  }

  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();