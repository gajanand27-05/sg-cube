import os

css_path = r"c:\SG\frontend\style.css"
js_path = r"c:\SG\frontend\app.js"

css_content = """
/* ============================================================
   INFO SCREEN AND LOGIN SCREEN
   ============================================================ */
/* Info Content */
.info-content {
    overflow-x: hidden;
}
.cards-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 100%;
    max-width: 440px;
}
.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border-dim);
    border-radius: var(--radius-lg);
    padding: 24px 20px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
    animation: fadeInUp 0.6s ease-out both;
}
.feature-card:nth-child(1) { animation-delay: 0.1s; }
.feature-card:nth-child(2) { animation-delay: 0.2s; }
.feature-card:nth-child(3) { animation-delay: 0.3s; }
.feature-card:nth-child(4) { animation-delay: 0.4s; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.feature-card:hover { border-color: var(--cyan); box-shadow: 0 5px 20px rgba(0, 240, 255, 0.1); }
.card-content { position: relative; z-index: 1; }
.card-icon { font-size: 2rem; color: var(--cyan); margin-bottom: 12px; text-shadow: 0 0 10px var(--cyan-glow); }
.card-title { font-family: var(--font-display); font-size: 1.1rem; color: var(--text-primary); margin-bottom: 8px; letter-spacing: 1px; }
.card-desc { font-family: var(--font-body); font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5; }

/* Tech Stack Marquee */
.tech-stack { width: 100vw; overflow: hidden; position: relative; margin-top: 40px; margin-bottom: 20px; left: -20px; }
.tech-title { text-align: center; font-family: var(--font-mono); color: var(--text-dim); font-size: 0.75rem; letter-spacing: 4px; margin-bottom: 15px; }
.marquee { display: flex; gap: 20px; width: max-content; animation: scrollMarquee 20s linear infinite; padding-left: 20px; }
.tech-item { display: inline-flex; align-items: center; gap: 6px; color: var(--text-secondary); font-size: 0.95rem; background: rgba(0, 240, 255, 0.04); padding: 8px 14px; border-radius: 16px; border: 1px solid var(--border-glow); }
.tech-item i { color: var(--cyan); }

@keyframes scrollMarquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

/* Login Screen */
.login-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 0 20px;
    z-index: 5;
    position: relative;
}
.auth-container {
    width: 100%;
    max-width: 340px;
    background: var(--bg-card);
    border: 1px solid var(--border-glow);
    border-radius: var(--radius-lg);
    padding: 24px 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 15px rgba(0, 240, 255, 0.05);
    backdrop-filter: blur(10px);
    animation: fadeInUp 0.8s ease-out 0.2s both;
}
.auth-form {
    display: none;
    flex-direction: column;
    gap: 16px;
}
.auth-form.active {
    display: flex;
    animation: fadeIn 0.4s ease-out;
}
.input-group {
    position: relative;
    width: 100%;
}
.input-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--cyan-dim);
    font-size: 0.9rem;
}
.input-group input {
    width: 100%;
    background: var(--bg-input);
    border: 1px solid var(--border-dim);
    color: var(--text-primary);
    padding: 12px 14px 12px 40px;
    border-radius: var(--radius-sm);
    font-family: var(--font-body);
    font-size: 0.95rem;
    outline: none;
    transition: all 0.3s ease;
}
.input-group input:focus {
    border-color: var(--cyan);
    box-shadow: 0 0 12px var(--cyan-glow);
}
.auth-btn {
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(0, 128, 255, 0.1));
    border: 1px solid var(--cyan);
    color: var(--cyan);
    padding: 12px;
    border-radius: var(--radius-sm);
    font-family: var(--font-display);
    font-size: 0.9rem;
    letter-spacing: 2px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 8px;
    text-transform: uppercase;
}
.auth-btn:hover {
    background: var(--cyan);
    color: var(--bg-primary);
    box-shadow: 0 0 20px var(--cyan-glow);
}
.auth-switch {
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 5px;
}
.auth-switch a {
    color: var(--cyan);
    text-decoration: none;
    margin-left: 5px;
    transition: color 0.3s, text-shadow 0.3s;
}
.auth-switch a:hover {
    color: #fff;
    text-shadow: 0 0 8px var(--cyan-glow);
}
"""

js_content = """
// ============================================================
//  Auth & Info Routing Extensions
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    // Info Screen Routing
    const btnOpenInfo = document.getElementById('btn-open-info');
    const btnCloseInfo = document.getElementById('btn-close-info');
    const screenInfo = document.getElementById('screen-info');
    const screenSettings = document.getElementById('screen-settings');

    if (btnOpenInfo) {
        btnOpenInfo.addEventListener('click', () => {
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            screenInfo.classList.add('active');
        });
    }

    if (btnCloseInfo) {
        btnCloseInfo.addEventListener('click', () => {
            screenInfo.classList.remove('active');
            screenSettings.classList.add('active');
        });
    }

    // Login logic
    const screenLogin = document.getElementById('screen-login');
    const screenHome = document.getElementById('screen-home');
    const bottomNav = document.getElementById('bottom-nav');
    
    // Auth Forms switches
    const formLogin = document.getElementById('form-login');
    const formSignup = document.getElementById('form-signup');
    const formVerify = document.getElementById('form-verify');
    
    document.getElementById('switch-to-signup')?.addEventListener('click', (e) => {
        e.preventDefault();
        formLogin.classList.remove('active');
        formSignup.classList.add('active');
    });
    
    document.getElementById('switch-to-login')?.addEventListener('click', (e) => {
        e.preventDefault();
        formSignup.classList.remove('active');
        formLogin.classList.add('active');
    });

    document.getElementById('verify-back')?.addEventListener('click', (e) => {
        e.preventDefault();
        formVerify.classList.remove('active');
        formLogin.classList.add('active');
    });

    let currentSignupEmail = '';

    // Handle Signup
    formSignup?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const btn = formSignup.querySelector('.auth-btn');
        btn.textContent = 'Processing...';

        try {
            const res = await fetch('/api/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();

            if (data.success) {
                currentSignupEmail = email;
                formSignup.classList.remove('active');
                formVerify.classList.add('active');
                showToast('fa-envelope', 'Verification code sent!');
            } else {
                showToast('fa-exclamation-triangle', data.message || 'Signup failed');
            }
        } catch (err) {
            showToast('fa-wifi', 'Server error');
        } finally {
            btn.textContent = 'Request Access';
        }
    });

    // Handle Verification
    formVerify?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const code = document.getElementById('verify-code').value;
        const btn = formVerify.querySelector('.auth-btn');
        btn.textContent = 'Verifying...';

        try {
            const res = await fetch('/api/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: currentSignupEmail, code })
            });
            const data = await res.json();

            if (data.success) {
                showToast('fa-check', 'Verified successfully!');
                setTimeout(() => { doLoginTransition(); }, 500);
            } else {
                showToast('fa-times', data.message || 'Invalid code');
            }
        } catch (err) {
            showToast('fa-wifi', 'Server error');
        } finally {
            btn.textContent = 'Verify Code';
        }
    });

    // Handle Login
    formLogin?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const btn = formLogin.querySelector('.auth-btn');
        btn.textContent = 'Authenticating...';

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();

            if (data.success) {
                showToast('fa-unlock', 'Access Granted');
                setTimeout(() => { doLoginTransition(); }, 500);
            } else {
                showToast('fa-lock', data.message || 'Invalid credentials');
            }
        } catch (err) {
            showToast('fa-wifi', 'Server error');
        } finally {
            btn.textContent = 'Access System';
        }
    });

    function doLoginTransition() {
        screenLogin.classList.remove('active');
        screenHome.classList.add('active');
        bottomNav.style.display = 'flex';
        // Reset navigation to point to home
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.querySelector('.nav-item[data-target="screen-home"]').classList.add('active');
        activeScreen = 'screen-home';
    }
});
"""

with open(css_path, "a", encoding="utf-8") as f:
    f.write(css_content)

with open(js_path, "a", encoding="utf-8") as f:
    f.write(js_content)
