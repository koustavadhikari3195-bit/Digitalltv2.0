/**
 * DIGITALLY — Motion System v3
 * Runs AFTER command_center.js (load order: command_center.js → motion.js)
 * Zero external dependencies. Respects prefers-reduced-motion.
 * Respects pointer:coarse (disables cursor on mobile).
 */

(function DIGITALLY_Motion() {
    'use strict';

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const touch = window.matchMedia('(pointer: coarse)').matches;

    /* ── 1. CUSTOM CURSOR ──────────────────────────────── */
    if (!reduced && !touch) {
        const dot = document.getElementById('cursor-dot');
        const ring = document.getElementById('cursor-ring');

        if (dot && ring) {
            let mx = 0, my = 0, rx = 0, ry = 0;

            document.addEventListener('mousemove', e => {
                mx = e.clientX; my = e.clientY;
                dot.style.left = mx + 'px';
                dot.style.top = my + 'px';
            });

            (function lerpRing() {
                rx += (mx - rx) * 0.12;
                ry += (my - ry) * 0.12;
                ring.style.left = rx + 'px';
                ring.style.top = ry + 'px';
                requestAnimationFrame(lerpRing);
            })();

            document.addEventListener('mouseleave', () => {
                dot.style.opacity = '0';
                ring.style.opacity = '0';
            });
            document.addEventListener('mouseenter', () => {
                dot.style.opacity = '1';
                ring.style.opacity = '0.45';
            });
            document.addEventListener('mousedown', () => {
                dot.style.transform = 'translate(-50%,-50%) scale(0.5)';
            });
            document.addEventListener('mouseup', () => {
                dot.style.transform = 'translate(-50%,-50%) scale(1)';
            });
        }
    }

    /* ── 2. MAGNETIC BUTTONS ───────────────────────────── */
    if (!reduced && !touch) {
        document.querySelectorAll('.btn-magnetic').forEach(btn => {
            const strength = parseFloat(btn.dataset.magnetStrength || '0.35');

            btn.addEventListener('mousemove', e => {
                const r = btn.getBoundingClientRect();
                const dx = (e.clientX - (r.left + r.width / 2)) * strength;
                const dy = (e.clientY - (r.top + r.height / 2)) * strength;
                btn.style.transform = `translate(${dx}px,${dy}px)`;
                const inner = btn.querySelector('.btn-inner');
                if (inner) inner.style.transform = `translate(${dx * 0.4}px,${dy * 0.4}px)`;
            });

            btn.addEventListener('mouseleave', () => {
                btn.style.transform = '';
                const inner = btn.querySelector('.btn-inner');
                if (inner) inner.style.transform = '';
            });
        });
    }

    /* ── 3. RIPPLE CLICK ───────────────────────────────── */
    document.querySelectorAll('.btn-ripple').forEach(el => {
        el.addEventListener('click', e => {
            if (reduced) return;
            const r = el.getBoundingClientRect();
            const size = Math.max(r.width, r.height) * 2;
            const span = document.createElement('span');
            span.className = 'ripple';
            span.style.cssText =
                `width:${size}px;height:${size}px;` +
                `left:${e.clientX - r.left - size / 2}px;` +
                `top:${e.clientY - r.top - size / 2}px;`;
            el.appendChild(span);
            span.addEventListener('animationend', () => span.remove());
        });
    });

    /* ── 4. SCROLL REVEALS ─────────────────────────────── */
    // Set stagger indices on children
    document.querySelectorAll('.stagger-children').forEach(parent => {
        Array.from(parent.children).forEach((child, i) => {
            child.style.setProperty('--i', i);
        });
    });

    const revealObs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                revealObs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.reveal, .reveal-left, .section-divider')
        .forEach(el => revealObs.observe(el));

    /* ── 5. STAT COUNTERS ──────────────────────────────── */
    const counterObs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            counterObs.unobserve(entry.target);

            const el = entry.target;
            const target = parseFloat(el.dataset.target);
            const suffix = el.dataset.suffix || '';
            const dur = 1800;
            const start = performance.now();
            const ease = t => 1 - Math.pow(1 - t, 4); // easeOutQuart

            (function tick(now) {
                const p = Math.min((now - start) / dur, 1);
                const val = target * ease(p);
                el.textContent = (Number.isInteger(target)
                    ? Math.round(val).toLocaleString('en-IN')
                    : val.toFixed(1)) + suffix;
                if (p < 1) requestAnimationFrame(tick);
            })(start);
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('[data-counter]').forEach(el => counterObs.observe(el));

    /* ── 6. SMOOTH ANCHOR SCROLL ───────────────────────── */
    // Offset = command bar (48px) + sticky nav (52px) = 100px
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const targetSelector = a.getAttribute('href');
            if (targetSelector === '#') return;
            const target = document.querySelector(targetSelector);
            if (!target) return;
            e.preventDefault();
            const top = target.getBoundingClientRect().top + window.scrollY - 100;
            window.scrollTo({ top, behavior: 'smooth' });
        });
    });

    /* ── 7. CONTACT FORM STEP MANAGER ─────────────────── */
    const form = document.getElementById('contact-form');
    if (form) {
        const steps = Array.from(form.querySelectorAll('.form-step'));
        const dots = Array.from(document.querySelectorAll('.step-dot'));
        const bar = document.getElementById('form-progress-bar');
        let current = 0;

        const goTo = to => {
            // Slide out
            steps[current].style.cssText =
                'transition:opacity 200ms ease,transform 200ms cubic-bezier(0.23,1,0.32,1);' +
                `opacity:0;transform:translateX(${to > current ? '-24px' : '24px'});`;

            setTimeout(() => {
                steps[current].style.display = 'none';
                steps[current].style.cssText = '';
                current = to;

                steps[current].style.cssText =
                    `display:block;opacity:0;transform:translateX(${to > current ? '24px' : '-24px'});`;

                requestAnimationFrame(() => {
                    steps[current].style.cssText =
                        'display:block;transition:opacity 250ms ease,' +
                        'transform 250ms cubic-bezier(0.23,1,0.32,1);opacity:1;transform:translateX(0);';
                });

                // Update step dots
                dots.forEach((d, i) => {
                    d.classList.toggle('active', i === current);
                    d.classList.toggle('done', i < current);
                });

                // Update progress bar
                if (bar) bar.style.width = `${((current + 1) / steps.length) * 100}%`;

                // Scroll form into view on mobile
                if (touch) form.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 210);
        };

        const markInvalid = el => {
            el.style.borderColor = '#ef4444';
            el.style.boxShadow = '0 0 0 3px rgba(239,68,68,0.15)';
            el.addEventListener('input', () => {
                el.style.borderColor = '';
                el.style.boxShadow = '';
            }, { once: true });
        };

        const validateStep = () => {
            let ok = true;
            steps[current].querySelectorAll('[required]').forEach(input => {
                if (input.type === 'radio') {
                    // Check if any radio in group is selected
                    const groupName = input.name;
                    if (!form.querySelector(`[name="${groupName}"]:checked`)) {
                        ok = false;
                        const group = steps[current].querySelector(
                            `[name="${groupName}"]`
                        )?.closest('.form-group');
                        if (group) {
                            group.style.outline = '1px solid #ef4444';
                            group.style.borderRadius = '8px';
                            setTimeout(() => { group.style.outline = ''; }, 2000);
                        }
                    }
                    return;
                }
                if (!input.value.trim()) { ok = false; markInvalid(input); }
            });
            return ok;
        };

        form.querySelectorAll('.btn-next').forEach(btn => {
            btn.addEventListener('click', () => { if (validateStep()) goTo(current + 1); });
        });
        form.querySelectorAll('.btn-back').forEach(btn => {
            btn.addEventListener('click', () => { if (current > 0) goTo(current - 1); });
        });

        // HTMX success → green state
        document.body.addEventListener('htmx:afterRequest', e => {
            if (e.detail.elt.id === 'contact-form' && e.detail.xhr.status === 200) {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('success');
                    submitBtn.style.cssText =
                        'background:#16a34a;box-shadow:0 0 30px rgba(22,163,74,0.35);' +
                        'transition:background 400ms ease,box-shadow 400ms ease;';
                    submitBtn.innerHTML =
                        `<svg width="22" height="22" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2.5"
              style="stroke-dasharray:100;stroke-dashoffset:100;
                     animation:checkDraw 500ms ease 100ms forwards;">
              <polyline points="20 6 9 17 4 12"/>
            </svg>`;
                }
            }
        });
    }

})();
