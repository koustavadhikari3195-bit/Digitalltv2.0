/**
 * DIGITALLY — AI Sales Director
 * Stateful chat with CSRF-protected backend calls.
 */
(function () {
    'use strict';

    let history = [];
    let isOpen = false;

    window.toggleChat = function () {
        const win = document.getElementById('chat-window');
        const iconOpen = document.getElementById('chat-icon-open');
        const iconClose = document.getElementById('chat-icon-close');
        isOpen = !isOpen;
        win.classList.toggle('hidden', !isOpen);
        iconOpen.classList.toggle('hidden', isOpen);
        iconClose.classList.toggle('hidden', !isOpen);
    };

    window.sendMessage = async function () {
        const input = document.getElementById('chat-input');
        const messages = document.getElementById('chat-messages');
        const text = input.value.trim();
        if (!text) return;

        // Add user bubble
        appendBubble(messages, 'user', text);
        input.value = '';

        // Typing indicator
        const typingId = appendTyping(messages);

        history.push({ role: 'user', content: text });

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
                || getCookie('csrftoken');
            const res = await fetch('/ai/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ message: text, history: history.slice(-10) }),
            });

            const data = await res.json();
            removeTyping(typingId);

            if (res.ok) {
                history.push({ role: 'assistant', content: data.reply });
                appendBubble(messages, 'agent', data.reply);
            } else {
                appendBubble(messages, 'agent', data.error || 'Something went wrong. Try again.');
            }
        } catch {
            removeTyping(typingId);
            appendBubble(messages, 'agent', 'Connection error. Please refresh and try again.');
        }
    };

    // Send on Enter key
    document.getElementById('chat-input')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); window.sendMessage(); }
    });

    function appendBubble(container, role, text) {
        const isAgent = role === 'agent';
        const wrapper = document.createElement('div');
        wrapper.className = `flex gap-2.5 ${isAgent ? '' : 'justify-end'}`;
        wrapper.innerHTML = isAgent
            ? `<div class="w-7 h-7 rounded-full bg-[#FF6B00] flex-shrink-0 flex items-center justify-center text-black font-black text-xs mt-0.5">D</div>
         <div class="bg-[#141414] rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-[#E0E0E0] max-w-[80%] leading-relaxed">${escapeHtml(text)}</div>`
            : `<div class="bg-[#FF6B00]/10 border border-[#FF6B00]/20 rounded-2xl rounded-tr-sm px-4 py-3 text-sm text-white max-w-[80%] leading-relaxed">${escapeHtml(text)}</div>`;
        container.appendChild(wrapper);
        container.scrollTop = container.scrollHeight;
    }

    function appendTyping(container) {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'flex gap-2.5';
        div.innerHTML = `<div class="w-7 h-7 rounded-full bg-[#FF6B00] flex-shrink-0 flex items-center justify-center text-black font-black text-xs">D</div>
      <div class="bg-[#141414] rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1 items-center">
        <span class="w-1.5 h-1.5 bg-[#A0A0A0] rounded-full animate-bounce" style="animation-delay:0ms"></span>
        <span class="w-1.5 h-1.5 bg-[#A0A0A0] rounded-full animate-bounce" style="animation-delay:150ms"></span>
        <span class="w-1.5 h-1.5 bg-[#A0A0A0] rounded-full animate-bounce" style="animation-delay:300ms"></span>
      </div>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        return id;
    }

    function removeTyping(id) {
        document.getElementById(id)?.remove();
    }

    function escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function getCookie(name) {
        return document.cookie.split(';').map(c => c.trim())
            .find(c => c.startsWith(name + '='))?.split('=')[1] ?? '';
    }
})();
