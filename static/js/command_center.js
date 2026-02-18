/**
 * Command Center Manager
 * Handles UI state for the high-fidelity command bar and panel.
 */

const CommandCenter = {
    isExpanded: false,
    currentTab: 'markets',

    init() {
        console.log("Command Center initialized.");
        this.bindEvents();
        this.startTime();
    },

    bindEvents() {
        // Toggling the panel
        document.body.addEventListener('click', (e) => {
            const expandBtn = e.target.closest('#cmd-expand-btn');
            if (expandBtn) {
                this.togglePanel();
            }

            const closeBtn = e.target.closest('#cmd-panel-close');
            if (closeBtn) {
                this.togglePanel(false);
            }

            // Tab switching
            const tabBtn = e.target.closest('.tab-btn');
            if (tabBtn) {
                const target = tabBtn.dataset.tab;
                this.switchTab(target);
            }
        });
    },

    togglePanel(force) {
        this.isExpanded = force !== undefined ? force : !this.isExpanded;
        const panel = document.getElementById('command-panel');
        const icon = document.querySelector('#cmd-expand-btn svg');

        if (this.isExpanded) {
            panel.classList.remove('hidden');
            if (icon) icon.style.transform = 'rotate(180deg)';
        } else {
            panel.classList.add('hidden');
            if (icon) icon.style.transform = 'rotate(0deg)';
        }
    },

    switchTab(tabId) {
        this.currentTab = tabId;

        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });

        // Update content screens
        document.querySelectorAll('.tab-screen').forEach(screen => {
            screen.classList.toggle('hidden', screen.id !== `screen-${tabId}`);
        });
    },

    startTime() {
        const istEl = document.getElementById('clk-ist');
        const utcEl = document.getElementById('clk-utc');

        if (!istEl || !utcEl) return;

        const update = () => {
            const now = new Date();

            // IST (UTC + 5.5)
            const ist = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (5.5 * 3600000));
            istEl.textContent = `${ist.getHours().toString().padStart(2, '0')}:${ist.getMinutes().toString().padStart(2, '0')} IST`;

            // UTC
            utcEl.textContent = `${now.getUTCHours().toString().padStart(2, '0')}:${now.getUTCMinutes().toString().padStart(2, '0')} UTC`;
        };

        update();
        setInterval(update, 60000);
    }
};

window.addEventListener('DOMContentLoaded', () => CommandCenter.init());
