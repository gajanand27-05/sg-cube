/* ============================================================
   SG CUBE — Application Logic
   Navigation, Animations, Waveform, Gauges, Voice Recognition
   ============================================================ */

(function () {
    'use strict';

    // ── DOM References ──
    const screens       = document.querySelectorAll('.screen');
    const navItems      = document.querySelectorAll('.nav-item');
    const micBtn        = document.getElementById('mic-btn');
    const waveCanvas    = document.getElementById('waveform-canvas');
    const waveCtx       = waveCanvas.getContext('2d');
    const clockEl       = document.getElementById('clock');
    const chatInput     = document.getElementById('chat-input');
    const chatSend      = document.getElementById('chat-send');
    const chatContainer = document.getElementById('chat-container');
    const testConnBtn   = document.getElementById('test-connection');
    const connStatus    = document.getElementById('conn-status');
    const particlesDiv  = document.getElementById('particles');
    const voiceCmdEl    = document.getElementById('voice-command');
    const aiRespEl      = document.getElementById('ai-response');

    let isListening     = false;
    let waveAnimId      = null;
    let activeScreen    = 'screen-home';
    let recognition     = null;

    // ── Server Config ──
    function getServerUrl() {
        let ip   = document.getElementById('server-ip')?.value || 'localhost';
        const port = document.getElementById('server-port')?.value || '5000';
        
        // If accessing from local file system, default to localhost instead of a dead placeholder IP
        if (window.location.protocol === 'file:') {
            ip = 'localhost';
        }
        // If hosted on localhost, use localhost
        else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            ip = 'localhost';
        }
        
        return `http://${ip}:${port}`;
    }

    // ── Initialization ──
    function init() {
        updateClock();
        setInterval(updateClock, 1000);
        createParticles();
        setupNavigation();
        setupVoiceRecognition();
        setupMicButton();
        setupChat();
        setupAutomation();
        setupSystemGauges();
        setupSettings();
        drawIdleWave();
        animateEntrance();

        // Clear placeholder text
        voiceCmdEl.textContent = 'Tap the microphone to speak...';
        voiceCmdEl.style.opacity = '0.5';
        aiRespEl.textContent = 'Waiting for your command...';
        aiRespEl.style.opacity = '0.5';
    }

    // ── Clock ──
    function updateClock() {
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        clockEl.textContent = `${h}:${m}`;
    }

    // ── Particles ──
    function createParticles() {
        for (let i = 0; i < 25; i++) {
            const p = document.createElement('div');
            p.classList.add('particle');
            p.style.left = Math.random() * 100 + '%';
            p.style.top  = (80 + Math.random() * 20) + '%';
            p.style.animationDuration = (6 + Math.random() * 10) + 's';
            p.style.animationDelay    = (Math.random() * 8) + 's';
            p.style.width  = (1 + Math.random() * 2) + 'px';
            p.style.height = p.style.width;
            particlesDiv.appendChild(p);
        }
    }

    // ── Navigation ──
    function setupNavigation() {
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const target = item.dataset.target;
                if (target === activeScreen) return;

                navItems.forEach(n => n.classList.remove('active'));
                item.classList.add('active');

                screens.forEach(s => s.classList.remove('active'));
                document.getElementById(target).classList.add('active');
                activeScreen = target;

                if (target === 'screen-system') {
                    setTimeout(animateGauges, 200);
                    fetchSystemInfo();
                }
                if (target === 'screen-chat') {
                    loadChatHistory();
                }
            });
        });
    }

    // ============================================================
    //  WEB SPEECH API — Voice Recognition
    // ============================================================

    function setupVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn('Web Speech API not supported in this browser.');
            showToast('fa-exclamation-triangle', 'Voice recognition not supported. Use Chrome or Edge.');
            return;
        }

        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        // Get language from settings
        const langSelect = document.getElementById('voice-lang');
        recognition.lang = langSelect ? langSelect.value : 'en-US';

        // Update language when settings change
        if (langSelect) {
            langSelect.addEventListener('change', () => {
                recognition.lang = langSelect.value;
            });
        }

        // ── Recognition Events ──

        recognition.onstart = () => {
            console.log('[SG CUBE] Voice recognition started');
            voiceCmdEl.style.opacity = '1';
            voiceCmdEl.textContent = '🎤 Listening...';
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // Show interim results in real-time
            if (interimTranscript) {
                voiceCmdEl.textContent = `🎤 ${interimTranscript}`;
                voiceCmdEl.style.opacity = '1';
            }

            // On final result, send to backend
            if (finalTranscript) {
                voiceCmdEl.textContent = `"${finalTranscript}"`;
                voiceCmdEl.style.opacity = '1';

                // Show processing state
                aiRespEl.textContent = 'Processing...';
                aiRespEl.style.opacity = '0.7';

                // Send to backend
                sendToBackend(finalTranscript);
            }
        };

        recognition.onerror = (event) => {
            console.error('[SG CUBE] Recognition error:', event.error);

            if (event.error === 'no-speech') {
                voiceCmdEl.textContent = 'No speech detected. Try again.';
                showToast('fa-microphone-slash', 'No speech detected');
            } else if (event.error === 'audio-capture') {
                voiceCmdEl.textContent = 'Microphone not found.';
                showToast('fa-exclamation-triangle', 'Microphone not available');
            } else if (event.error === 'not-allowed') {
                voiceCmdEl.textContent = 'Microphone permission denied.';
                showToast('fa-lock', 'Please allow microphone access');
            } else {
                voiceCmdEl.textContent = `Error: ${event.error}`;
                showToast('fa-exclamation-triangle', `Voice error: ${event.error}`);
            }

            stopListening();
        };

        recognition.onend = () => {
            console.log('[SG CUBE] Voice recognition ended');
            // If still in listening mode and recognition auto-stopped, keep UI consistent
            if (isListening) {
                stopListening();
            }
        };
    }

    // ── Start/Stop Listening ──
    function startListening() {
        if (!recognition) {
            showToast('fa-exclamation-triangle', 'Voice recognition not available');
            return;
        }

        isListening = true;
        micBtn.classList.add('listening');
        startWaveform();
        showToast('fa-microphone', 'Listening... Speak your command');

        // Refresh language setting before starting
        const langSelect = document.getElementById('voice-lang');
        if (langSelect) {
            recognition.lang = langSelect.value;
        }

        try {
            recognition.start();
        } catch (e) {
            console.error('[SG CUBE] Failed to start recognition:', e);
            stopListening();
        }
    }

    function stopListening() {
        isListening = false;
        micBtn.classList.remove('listening');
        stopWaveform();

        if (recognition) {
            try {
                recognition.stop();
            } catch (e) {
                // Already stopped
            }
        }
    }

    // ── Mic Button Handler ──
    function setupMicButton() {
        micBtn.addEventListener('click', () => {
            if (isListening) {
                stopListening();
                showToast('fa-check-circle', 'Voice input stopped');
            } else {
                startListening();
            }
        });
    }

    // ============================================================
    //  Backend Communication
    // ============================================================

    async function sendToBackend(text) {
        const url = getServerUrl();

        try {
            const response = await fetch(`${url}/api/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }

            const data = await response.json();

            // Display AI response with typing effect
            typeResponse(data.response || 'Command processed.');

            // Also add to chat history
            addChatBubble('user', text);
            setTimeout(() => {
                addChatBubble('ai', data.response || 'Command processed.');
                // Save to persistent history (fire-and-forget)
                fetch(`${url}/api/chat/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: 'default',
                        user_message: text,
                        ai_message: data.response || 'Command processed.'
                    })
                }).catch(() => {});
            }, 300);

            // Speak the response if TTS is enabled
            const ttsToggle = document.getElementById('tts-toggle');
            if (ttsToggle && ttsToggle.checked && data.response) {
                speakResponse(data.response);
            }

            if (data.action) {
                console.log(`[SG CUBE] Action: ${data.action}`);
            }

        } catch (error) {
            console.error('[SG CUBE] Backend error:', error);
            const errorMsg = 'Could not reach server. Check connection settings.';
            aiRespEl.textContent = errorMsg;
            aiRespEl.style.opacity = '1';
            showToast('fa-exclamation-triangle', 'Server connection failed');
        }
    }

    // ── Type response character by character ──
    function typeResponse(text) {
        aiRespEl.textContent = '';
        aiRespEl.style.opacity = '1';
        let i = 0;
        const speed = Math.max(15, Math.min(40, 800 / text.length));

        function type() {
            if (i < text.length) {
                aiRespEl.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        type();
    }

    // ── Text-to-Speech ──
    function speakResponse(text) {
        if (!('speechSynthesis' in window)) return;

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        const voiceSelect = document.getElementById('tts-voice');
        const voices = window.speechSynthesis.getVoices();
        if (voiceSelect && voiceSelect.value !== '' && voices[voiceSelect.value]) {
            utterance.voice = voices[voiceSelect.value];
        }

        const langSelect = document.getElementById('voice-lang');
        utterance.lang = langSelect ? langSelect.value : 'en-US';

        const rateSlider = document.getElementById('tts-rate');
        const pitchSlider = document.getElementById('tts-pitch');
        utterance.rate = rateSlider ? parseFloat(rateSlider.value) : 1;
        utterance.pitch = pitchSlider ? parseFloat(pitchSlider.value) : 1;

        window.speechSynthesis.speak(utterance);
    }

    // ── Fetch real system info from backend ──
    async function fetchSystemInfo() {
        const url = getServerUrl();
        try {
            const response = await fetch(`${url}/api/system`);
            if (!response.ok) return;
            const data = await response.json();

            if (data.success) {
                // Update gauges with real data
                updateGaugeValue('gauge-cpu', 'gauge-cpu-val', data.cpu);
                updateGaugeValue('gauge-ram', 'gauge-ram-val', data.ram_percent);
                updateGaugeValue('gauge-bat', 'gauge-bat-val', data.battery || 0);

                // Update quick stats on home screen
                const stats = document.querySelectorAll('.quick-stat span');
                if (stats[0]) stats[0].textContent = `CPU ${data.cpu}%`;
                if (stats[1]) stats[1].textContent = `RAM ${data.ram_used}G`;
                if (stats[2]) stats[2].textContent = `${data.battery || '?'}%`;
            }
        } catch (e) {
            console.log('[SG CUBE] Could not fetch system info:', e.message);
        }
    }

    function updateGaugeValue(fillId, textId, value) {
        const circumference = 2 * Math.PI * 52;
        const fill = document.getElementById(fillId);
        const text = document.getElementById(textId);
        if (fill) {
            fill.style.strokeDasharray = circumference;
            fill.style.strokeDashoffset = circumference - (value / 100) * circumference;
        }
        if (text) text.textContent = Math.round(value) + '%';
    }

    // ============================================================
    //  Waveform Animations
    // ============================================================

    function drawIdleWave() {
        const w = waveCanvas.width;
        const h = waveCanvas.height;
        const cx = w / 2;
        const cy = h / 2;
        const radius = 48;
        let t = 0;

        function frame() {
            waveCtx.clearRect(0, 0, w, h);

            waveCtx.beginPath();
            waveCtx.arc(cx, cy, radius, 0, Math.PI * 2);
            waveCtx.strokeStyle = 'rgba(0, 240, 255, 0.06)';
            waveCtx.lineWidth = 1;
            waveCtx.stroke();

            for (let i = 0; i < 3; i++) {
                const angle = t * 0.01 + (i * Math.PI * 2) / 3;
                const x = cx + Math.cos(angle) * radius;
                const y = cy + Math.sin(angle) * radius;

                waveCtx.beginPath();
                waveCtx.arc(x, y, 1.5, 0, Math.PI * 2);
                waveCtx.fillStyle = 'rgba(0, 240, 255, 0.3)';
                waveCtx.fill();
            }

            t++;
            if (!isListening) {
                waveAnimId = requestAnimationFrame(frame);
            }
        }
        frame();
    }

    function startWaveform() {
        if (waveAnimId) cancelAnimationFrame(waveAnimId);

        const w = waveCanvas.width;
        const h = waveCanvas.height;
        const cx = w / 2;
        const cy = h / 2;
        let t = 0;

        function frame() {
            waveCtx.clearRect(0, 0, w, h);

            const layers = [
                { r: 56, amp: 12, freq: 6, color: 'rgba(0, 240, 255, 0.5)', lw: 2 },
                { r: 64, amp: 8,  freq: 8, color: 'rgba(0, 128, 255, 0.3)', lw: 1.5 },
                { r: 72, amp: 6,  freq: 10, color: 'rgba(0, 240, 255, 0.15)', lw: 1 },
            ];

            layers.forEach(layer => {
                waveCtx.beginPath();
                for (let a = 0; a <= 360; a += 2) {
                    const rad = (a * Math.PI) / 180;
                    const waveOffset = Math.sin(rad * layer.freq + t * 0.08) * layer.amp * (0.5 + Math.random() * 0.5);
                    const r = layer.r + waveOffset;
                    const x = cx + Math.cos(rad) * r;
                    const y = cy + Math.sin(rad) * r;
                    a === 0 ? waveCtx.moveTo(x, y) : waveCtx.lineTo(x, y);
                }
                waveCtx.closePath();
                waveCtx.strokeStyle = layer.color;
                waveCtx.lineWidth = layer.lw;
                waveCtx.stroke();
            });

            const grad = waveCtx.createRadialGradient(cx, cy, 0, cx, cy, 40);
            grad.addColorStop(0, 'rgba(0, 255, 136, 0.08)');
            grad.addColorStop(1, 'transparent');
            waveCtx.fillStyle = grad;
            waveCtx.fillRect(0, 0, w, h);

            t++;
            if (isListening) {
                waveAnimId = requestAnimationFrame(frame);
            }
        }
        frame();
    }

    function stopWaveform() {
        if (waveAnimId) cancelAnimationFrame(waveAnimId);
        drawIdleWave();
    }

    // ============================================================
    //  Chat
    // ============================================================

    function setupChat() {
        async function sendMessage() {
            const text = chatInput.value.trim();
            if (!text) return;

            addChatBubble('user', text);
            chatInput.value = '';

            // Send to backend
            const url = getServerUrl();
            try {
                const response = await fetch(`${url}/api/command`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });

                if (!response.ok) throw new Error(`Server ${response.status}`);
                const data = await response.json();
                addChatBubble('ai', data.response || 'Command processed.');

                // Save to persistent history (fire-and-forget)
                fetch(`${url}/api/chat/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: 'default',
                        user_message: text,
                        ai_message: data.response || 'Command processed.'
                    })
                }).catch(() => {});

                // Speak if TTS enabled
                const ttsToggle = document.getElementById('tts-toggle');
                if (ttsToggle && ttsToggle.checked && data.response) {
                    speakResponse(data.response);
                }
            } catch (error) {
                addChatBubble('ai', 'Could not reach server. Please check your connection.');
            }
        }

        chatSend.addEventListener('click', sendMessage);
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // Chat mic button — use voice recognition in chat
        const chatMicBtn = document.querySelector('.chat-mic-btn');
        if (chatMicBtn) {
            chatMicBtn.addEventListener('click', () => {
                if (isListening) {
                    stopListening();
                } else {
                    startListening();
                }
            });
        }
    }

    function addChatBubble(type, text) {
        const now = new Date();
        const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${type}`;

        const avatar = type === 'ai' ? `<div class="chat-avatar"><i class="fas fa-robot"></i></div>` : '';

        // Convert newlines to <br> for display
        const displayText = text.replace(/\n/g, '<br>');

        bubble.innerHTML = `
            ${avatar}
            <div class="chat-content">
                <p>${displayText}</p>
                <span class="chat-time">${time}</span>
            </div>
        `;

        chatContainer.appendChild(bubble);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // ============================================================
    //  Automation
    // ============================================================

    function setupAutomation() {
        document.querySelectorAll('.auto-card').forEach(card => {
            card.addEventListener('click', async () => {
                const label = card.querySelector('.auto-card-label').textContent;
                showToast('fa-wand-magic-sparkles', `Executing: ${label}`);

                card.style.transform = 'scale(0.93)';
                setTimeout(() => { card.style.transform = ''; }, 200);

                // Send automation command to backend
                await sendToBackend(label);
            });
        });

        document.querySelectorAll('.auto-list-item').forEach(item => {
            item.addEventListener('click', async () => {
                const name = item.querySelector('.auto-list-name').textContent;
                showToast('fa-terminal', `Running: ${name}`);
                await sendToBackend(name);
            });
        });
    }

    // ============================================================
    //  System Gauges
    // ============================================================

    function setupSystemGauges() {
        setTimeout(animateGauges, 500);
    }

    function animateGauges() {
        const circumference = 2 * Math.PI * 52;
        const gauges = [
            { id: 'gauge-cpu', value: 23 },
            { id: 'gauge-ram', value: 62 },
            { id: 'gauge-bat', value: 87 },
        ];

        gauges.forEach(g => {
            const el = document.getElementById(g.id);
            if (!el) return;
            const offset = circumference - (g.value / 100) * circumference;
            el.style.strokeDasharray = circumference;
            el.style.strokeDashoffset = circumference;
            void el.getBoundingClientRect();
            el.style.strokeDashoffset = offset;
        });
    }

    // Periodically fetch real system info
    function startGaugeSim() {
        setInterval(() => {
            if (activeScreen !== 'screen-system') return;
            fetchSystemInfo();
        }, 5000);
    }

    // ============================================================
    //  Settings
    // ============================================================

    function setupSettings() {
        // ── Test Connection Button ──
        testConnBtn.addEventListener('click', async () => {
            testConnBtn.classList.add('testing');
            testConnBtn.innerHTML = '<i class="fas fa-spinner"></i> Testing...';
            connStatus.innerHTML = '<i class="fas fa-circle"></i> Testing...';
            connStatus.className = 'setting-status';
            connStatus.style.color = 'var(--orange)';

            const url = getServerUrl();

            try {
                const response = await fetch(`${url}/api/health`, {
                    signal: AbortSignal.timeout(5000)
                });

                if (!response.ok) throw new Error('Bad response');
                const data = await response.json();

                testConnBtn.classList.remove('testing');
                testConnBtn.innerHTML = '<i class="fas fa-satellite-dish"></i> Test';

                if (data.status === 'online') {
                    connStatus.innerHTML = '<i class="fas fa-circle"></i> Connected';
                    connStatus.className = 'setting-status connected';
                    connStatus.style.color = '';
                    showToast('fa-check-circle', `Connected to ${data.name} v${data.version}`);

                    // Update top bar status
                    const statusDot = document.querySelector('.status-dot');
                    const statusLabel = document.querySelector('.status-label');
                    if (statusDot) statusDot.className = 'status-dot online';
                    if (statusLabel) { statusLabel.textContent = 'ONLINE'; statusLabel.style.color = ''; }
                } else {
                    throw new Error('Server not online');
                }
            } catch (error) {
                testConnBtn.classList.remove('testing');
                testConnBtn.innerHTML = '<i class="fas fa-satellite-dish"></i> Test';
                connStatus.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
                connStatus.className = 'setting-status disconnected';
                connStatus.style.color = '';
                showToast('fa-exclamation-triangle', 'Connection failed. Check IP & Port.');

                // Update top bar status
                const statusDot = document.querySelector('.status-dot');
                const statusLabel = document.querySelector('.status-label');
                if (statusDot) statusDot.className = 'status-dot';
                if (statusLabel) { statusLabel.textContent = 'OFFLINE'; statusLabel.style.color = 'var(--red)'; }
            }
        });

        // ── System Quick Action Buttons ──
        document.querySelectorAll('.sys-action-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const action = btn.dataset.action;
                if (!action) return;

                const url = getServerUrl();
                try {
                    const res = await fetch(`${url}/api/system/action`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ action: action })
                    });
                    const data = await res.json();
                    showToast(data.success ? 'fa-check-circle' : 'fa-exclamation-triangle', data.response);
                } catch (e) {
                    showToast('fa-exclamation-triangle', 'Failed to execute action');
                }
            });
        });
    }

    // ============================================================
    //  Toast Notification
    // ============================================================

    let toastTimeout = null;
    function showToast(icon, message) {
        let toast = document.querySelector('.toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.className = 'toast';
            document.body.appendChild(toast);
        }

        toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;
        toast.classList.remove('show');
        void toast.offsetWidth;
        toast.classList.add('show');

        if (toastTimeout) clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {
            toast.classList.remove('show');
        }, 2500);
    }

    // ============================================================
    //  Entrance Animations
    // ============================================================

    function animateEntrance() {
        const items = document.querySelectorAll('.logo-section, .mic-area, .voice-output, .home-quick-stats');
        items.forEach((el, i) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, 200 + i * 150);
        });

        setTimeout(startGaugeSim, 2000);

        // Auto-fetch system info on load
        setTimeout(fetchSystemInfo, 1000);
    }

    // ── Canvas Resize ──
    function resizeCanvas() {
        const micArea = document.querySelector('.mic-area');
        if (micArea) {
            const size = Math.min(micArea.offsetWidth, micArea.offsetHeight);
            waveCanvas.width = size;
            waveCanvas.height = size;
        }
    }

    window.addEventListener('resize', resizeCanvas);

    // ── Start ──
    document.addEventListener('DOMContentLoaded', init);

// ============================================================
//  Auth, Admin Panel & Routing
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    const screenLogin = document.getElementById('screen-login');
    const screenHome = document.getElementById('screen-home');
    const screenAdmin = document.getElementById('screen-admin');
    const bottomNav = document.getElementById('bottom-nav');
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');

    let selectedRole = 'user';
    let currentUser = null;

    // ── Role Selector ──
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedRole = btn.dataset.role;
        });
    });

    // ── Switch Forms ──
    document.getElementById('switch-to-register')?.addEventListener('click', (e) => {
        e.preventDefault();
        formLogin.classList.remove('active');
        formRegister.classList.add('active');
    });
    document.getElementById('switch-to-login')?.addEventListener('click', (e) => {
        e.preventDefault();
        formRegister.classList.remove('active');
        formLogin.classList.add('active');
    });

    // ── Register ──
    formRegister?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value.trim();
        const email = document.getElementById('reg-email').value.trim();
        const password = document.getElementById('reg-password').value;
        const confirm = document.getElementById('reg-confirm').value;
        const btn = document.getElementById('reg-submit-btn');

        if (password !== confirm) {
            showToast('fa-exclamation-triangle', 'Passwords do not match');
            return;
        }

        btn.textContent = 'Creating...';
        const url = getServerUrl();

        try {
            const res = await fetch(`${url}/api/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, role: selectedRole })
            });
            const data = await res.json();
            if (data.success) {
                showToast('fa-check', 'Account created! Logging in...');
                currentUser = { username, role: data.role };
                setTimeout(() => routeAfterLogin(data.role), 500);
            } else {
                showToast('fa-times', data.message || 'Registration failed');
            }
        } catch (err) {
            showToast('fa-wifi', 'Server error');
        } finally {
            btn.textContent = 'Create Account';
        }
    });

    // ── Login ──
    formLogin?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        const btn = document.getElementById('login-submit-btn');
        btn.textContent = 'Authenticating...';
        const url = getServerUrl();

        try {
            const res = await fetch(`${url}/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (data.success) {
                showToast('fa-unlock', `Welcome, ${data.username}!`);
                currentUser = { username: data.username, role: data.role };
                setTimeout(() => routeAfterLogin(data.role), 500);
            } else {
                showToast('fa-lock', data.message || 'Invalid credentials');
            }
        } catch (err) {
            showToast('fa-wifi', 'Server error');
        } finally {
            btn.textContent = 'Access System';
        }
    });

    // ── Route after login ──
    function routeAfterLogin(role) {
        screenLogin.classList.remove('active');
        if (role === 'admin') {
            screenAdmin.classList.add('active');
            loadAdminDashboard();
        } else {
            screenHome.classList.add('active');
            bottomNav.style.display = 'flex';
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.querySelector('.nav-item[data-target="screen-home"]').classList.add('active');
            activeScreen = 'screen-home';
        }
    }

    // ── Admin Logout ──
    document.getElementById('admin-logout-btn')?.addEventListener('click', () => {
        screenAdmin.classList.remove('active');
        screenLogin.classList.add('active');
        currentUser = null;
        showToast('fa-right-from-bracket', 'Logged out');
    });

    // ============================
    //  Admin Panel Logic
    // ============================

    // ── Tabs ──
    document.querySelectorAll('.admin-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.admin-tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const target = document.getElementById(tab.dataset.tab);
            if (target) target.classList.add('active');

            // Auto-load data for specific tabs
            if (tab.dataset.tab === 'tab-users') loadAdminUsers();
            if (tab.dataset.tab === 'tab-logs') loadAdminLogs();
            if (tab.dataset.tab === 'tab-dashboard') loadAdminDashboard();
        });
    });

    // ── Dashboard Stats ──
    async function loadAdminDashboard() {
        const url = getServerUrl();
        try {
            const [statsRes, sysRes] = await Promise.all([
                fetch(`${url}/api/admin/stats`),
                fetch(`${url}/api/system`)
            ]);
            const stats = await statsRes.json();
            const sys = await sysRes.json();

            if (stats.success) {
                document.getElementById('stat-total-users').textContent = stats.total_users;
                document.getElementById('stat-total-admins').textContent = stats.total_admins;
                document.getElementById('stat-total-requests').textContent = stats.total_requests;
                document.getElementById('stat-total-errors').textContent = stats.total_errors;
            }
            if (sys.success) {
                document.getElementById('admin-platform').textContent = sys.platform || '—';
                document.getElementById('admin-cpu').textContent = `${sys.cpu}%`;
                document.getElementById('admin-ram').textContent = `${sys.ram_used}G / ${sys.ram_total}G (${sys.ram_percent}%)`;
                document.getElementById('admin-battery').textContent = sys.battery ? `${sys.battery}%` : 'N/A';
            }
        } catch (e) {
            console.log('Admin dashboard fetch error:', e);
        }
    }

    // ── User Management ──
    async function loadAdminUsers() {
        const url = getServerUrl();
        try {
            const res = await fetch(`${url}/api/admin/users`);
            const data = await res.json();
            const tbody = document.getElementById('admin-users-tbody');
            tbody.innerHTML = '';

            if (data.success) {
                data.users.forEach(u => {
                    const tr = document.createElement('tr');
                    const statusClass = u.is_active ? 'active-status' : 'blocked-status';
                    const statusText = u.is_active ? 'Active' : 'Blocked';
                    const btnText = u.is_active ? 'Block' : 'Unblock';
                    const btnClass = u.is_active ? 'block-btn' : 'unblock-btn';
                    const isAdmin = u.username === 'admin';
                    tr.innerHTML = `
                        <td>${u.id}</td>
                        <td>${u.username}</td>
                        <td>${u.email}</td>
                        <td><span class="role-badge ${u.role}">${u.role}</span></td>
                        <td><span class="${statusClass}">${statusText}</span></td>
                        <td>${isAdmin ? '—' : `<button class="admin-action-btn ${btnClass}" data-uid="${u.id}">${btnText}</button>`}</td>
                    `;
                    tbody.appendChild(tr);
                });

                // Attach toggle handlers
                tbody.querySelectorAll('.admin-action-btn').forEach(btn => {
                    btn.addEventListener('click', async () => {
                        const uid = btn.dataset.uid;
                        try {
                            const res = await fetch(`${url}/api/admin/toggle-user`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ user_id: parseInt(uid) })
                            });
                            const data = await res.json();
                            if (data.success) {
                                showToast('fa-check', `User ${data.is_active ? 'unblocked' : 'blocked'}`);
                                loadAdminUsers();
                            } else {
                                showToast('fa-times', data.message);
                            }
                        } catch (e) {
                            showToast('fa-wifi', 'Server error');
                        }
                    });
                });
            }
        } catch (e) {
            console.log('Load users error:', e);
        }
    }

    // ── Logs ──
    async function loadAdminLogs() {
        const url = getServerUrl();
        try {
            const res = await fetch(`${url}/api/admin/logs`);
            const data = await res.json();
            const tbody = document.getElementById('admin-logs-tbody');
            tbody.innerHTML = '';

            if (data.success) {
                data.logs.forEach(l => {
                    const tr = document.createElement('tr');
                    const statusClass = l.status >= 400 ? 'error-status' : 'ok-status';
                    tr.innerHTML = `
                        <td>${l.endpoint}</td>
                        <td>${l.method}</td>
                        <td><span class="${statusClass}">${l.status}</span></td>
                        <td>${l.ip}</td>
                        <td>${l.timestamp || '—'}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        } catch (e) {
            console.log('Load logs error:', e);
        }
    }

    document.getElementById('refresh-logs-btn')?.addEventListener('click', () => loadAdminLogs());

    // ── Model Sliders ──
    const tempSlider = document.getElementById('model-temp');
    const lengthSlider = document.getElementById('model-length');
    if (tempSlider) {
        tempSlider.addEventListener('input', () => {
            document.getElementById('model-temp-val').textContent = (tempSlider.value / 100).toFixed(1);
        });
    }
    if (lengthSlider) {
        lengthSlider.addEventListener('input', () => {
            document.getElementById('model-length-val').textContent = lengthSlider.value;
        });
    }

    // ── Model Toggle Buttons ──
    document.querySelectorAll('.model-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.model-toggle-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            showToast('fa-brain', `Model mode: ${btn.dataset.mode}`);
        });
    });

    // ── Tool Cards ──
    const toolModal = document.getElementById('tool-modal');
    const toolModalTitle = document.getElementById('tool-modal-title');
    const toolModalClose = document.getElementById('tool-modal-close');
    const toolModalInput = document.getElementById('tool-modal-input');
    const toolModalFileArea = document.getElementById('tool-modal-file-area');
    const toolModalFile = document.getElementById('tool-modal-file');
    const toolFileName = document.getElementById('tool-file-name');
    const toolModalPrompt = document.getElementById('tool-modal-prompt');
    const toolModalSubmit = document.getElementById('tool-modal-submit');
    const toolModalResult = document.getElementById('tool-modal-result');
    const toolResultText = document.getElementById('tool-result-text');

    let currentTool = null;

    const toolNames = {
        codegen: 'Code Generator',
        summarizer: 'Summarizer',
        resume: 'Resume Builder',
        notes: 'Notes Organizer',
        vision: 'Vision AI',
    };

    function openToolModal(tool) {
        currentTool = tool;
        toolModalTitle.textContent = toolNames[tool] || tool;
        toolModalInput.value = '';
        toolFileName.textContent = '';
        toolModalFile.value = '';
        toolModalPrompt.value = '';
        toolModalResult.style.display = 'none';
        toolResultText.textContent = '';
        toolResultText.classList.remove('error');
        toolModalSubmit.disabled = false;
        toolModalSubmit.classList.remove('loading');
        toolModalSubmit.innerHTML = '<i class="fas fa-bolt"></i> Generate';

        if (tool === 'vision') {
            toolModalInput.style.display = 'none';
            toolModalFileArea.style.display = 'flex';
            toolModalPrompt.style.display = 'block';
        } else {
            toolModalInput.style.display = 'block';
            toolModalFileArea.style.display = 'none';
            toolModalPrompt.style.display = 'none';
        }

        toolModal.style.display = 'flex';
    }

    function closeToolModal() {
        toolModal.style.display = 'none';
        currentTool = null;
    }

    toolModalClose.addEventListener('click', closeToolModal);

    toolModal.addEventListener('click', (e) => {
        if (e.target === toolModal) closeToolModal();
    });

    toolModalFile.addEventListener('change', () => {
        if (toolModalFile.files.length > 0) {
            toolFileName.textContent = toolModalFile.files[0].name;
        } else {
            toolFileName.textContent = '';
        }
    });

    toolModalSubmit.addEventListener('click', async () => {
        if (!currentTool) return;
        const url = getServerUrl();

        toolModalSubmit.disabled = true;
        toolModalSubmit.classList.add('loading');
        toolModalSubmit.innerHTML = '<i class="fas fa-spinner"></i> Processing...';
        toolModalResult.style.display = 'block';
        toolResultText.textContent = 'Analyzing...';
        toolResultText.classList.remove('error');

        try {
            let data;
            if (currentTool === 'vision') {
                if (!toolModalFile.files.length) {
                    throw new Error('Please select an image file.');
                }
                const formData = new FormData();
                formData.append('file', toolModalFile.files[0]);
                const promptVal = toolModalPrompt.value.trim();
                const q = promptVal ? `?prompt=${encodeURIComponent(promptVal)}` : '';
                const resp = await fetch(`${url}/api/vision${q}`, {
                    method: 'POST',
                    body: formData,
                });
                if (!resp.ok) {
                    const err = await resp.json().catch(() => ({ detail: 'Server error' }));
                    throw new Error(err.detail || `Server returned ${resp.status}`);
                }
                data = await resp.json();
                toolResultText.textContent = data.description || 'No description returned.';
            } else {
                const inputVal = toolModalInput.value.trim();
                if (!inputVal) {
                    throw new Error('Please enter some text.');
                }
                const resp = await fetch(`${url}/api/tools/${currentTool}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input_data: inputVal }),
                });
                if (!resp.ok) {
                    const err = await resp.json().catch(() => ({ detail: 'Server error' }));
                    throw new Error(err.detail || `Server returned ${resp.status}`);
                }
                data = await resp.json();
                toolResultText.textContent = data.result || 'No result returned.';
            }
        } catch (error) {
            toolResultText.textContent = `Error: ${error.message}`;
            toolResultText.classList.add('error');
        } finally {
            toolModalSubmit.disabled = false;
            toolModalSubmit.classList.remove('loading');
            toolModalSubmit.innerHTML = '<i class="fas fa-bolt"></i> Generate';
        }
    });

    document.querySelectorAll('.tool-card').forEach(card => {
        card.addEventListener('click', () => {
            const tool = card.dataset.tool;
            if (tool === 'chatbot') {
                document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
                document.getElementById('screen-chat').classList.add('active');
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                document.querySelector('.nav-item[data-target="screen-chat"]')?.classList.add('active');
                activeScreen = 'screen-chat';
            } else {
                openToolModal(tool);
            }
            card.style.transform = 'scale(0.95)';
            setTimeout(() => { card.style.transform = ''; }, 200);
        });
    });

    // ============================
    //  Chat History Persistence
    // ============================

    async function loadChatHistory() {
        const url = getServerUrl();
        try {
            const res = await fetch(`${url}/api/chat/history?user_id=default&limit=50`);
            const data = await res.json();
            if (data.success && data.messages.length > 0) {
                const container = document.getElementById('chat-container');
                const divider = container.querySelector('.chat-date-divider');
                container.innerHTML = '';
                if (divider) container.appendChild(divider);

                data.messages.forEach(msg => {
                    addChatBubble(msg.role === 'user' ? 'user' : 'ai', msg.message);
                });
            }
        } catch(e) {
            console.log('Could not load chat history:', e);
        }
    }

    document.getElementById('btn-clear-chat')?.addEventListener('click', async () => {
        const url = getServerUrl();
        await fetch(`${url}/api/chat/history?user_id=default`, { method: 'DELETE' });
        const container = document.getElementById('chat-container');
        container.innerHTML = '<div class="chat-date-divider"><span>Today</span></div>';
        showToast('fa-trash-alt', 'Chat history cleared');
    });

    // ============================
    //  Voice TTS Controls
    // ============================

    function populateVoices() {
        const voiceSelect = document.getElementById('tts-voice');
        if (!voiceSelect) return;

        const voices = window.speechSynthesis.getVoices();
        voiceSelect.innerHTML = '';

        voices.forEach((voice, index) => {
            const opt = document.createElement('option');
            opt.value = index;
            opt.textContent = `${voice.name} (${voice.lang})`;
            voiceSelect.appendChild(opt);
        });

        if (voices.length === 0) {
            voiceSelect.innerHTML = '<option value="">No voices available</option>';
        }
    }

    if ('speechSynthesis' in window) {
        speechSynthesis.onvoiceschanged = populateVoices;
        populateVoices();
    }

    document.getElementById('tts-rate')?.addEventListener('input', (e) => {
        document.getElementById('tts-rate-val').textContent = parseFloat(e.target.value).toFixed(1) + 'x';
    });

    document.getElementById('tts-pitch')?.addEventListener('input', (e) => {
        document.getElementById('tts-pitch-val').textContent = parseFloat(e.target.value).toFixed(1);
    });

    document.getElementById('btn-test-voice')?.addEventListener('click', () => {
        speakResponse('Hello! I am SG CUBE, your AI assistant. This is how I sound with the current voice settings.');
    });

    // ============================
    //  Ollama Status & Model Selector
    // ============================

    async function checkOllamaStatus() {
        const url = getServerUrl();
        try {
            const res = await fetch(`${url}/api/ollama/status`);
            const data = await res.json();
            const statusDot = document.getElementById('ollama-status-dot');
            const statusText = document.getElementById('ollama-status-text');
            const modelSelect = document.getElementById('ollama-model-select');

            if (data.online) {
                statusDot.innerHTML = '<i class="fas fa-circle"></i> Online';
                statusDot.className = 'setting-status connected';
                statusText.textContent = `${data.models.length} model(s) available`;

                modelSelect.innerHTML = '';
                data.models.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m;
                    opt.textContent = m;
                    if (m === data.current_model) opt.selected = true;
                    modelSelect.appendChild(opt);
                });
            } else {
                statusDot.innerHTML = '<i class="fas fa-circle"></i> Offline';
                statusDot.className = 'setting-status';
                statusText.textContent = 'Ollama not running — using Gemini online';
                modelSelect.innerHTML = '<option value="">Ollama offline</option>';
            }
        } catch (e) {
            console.error('Ollama status check failed:', e);
        }
    }

    document.getElementById('ollama-model-select')?.addEventListener('change', async (e) => {
        const model = e.target.value;
        if (!model) return;
        const url = getServerUrl();
        await fetch(`${url}/api/ollama/model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: model })
        });
        showToast('fa-brain', `Model switched to ${model}`);
    });

    checkOllamaStatus();
});

})();
