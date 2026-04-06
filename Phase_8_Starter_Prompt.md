# 🚀 SG CUBE — Phase 8: Voice TTS Improvements

## Context
You are working on the SG CUBE project (`d:\sg\`). Phases 1–7 are complete. The frontend uses the **browser's built-in Web Speech API** for both STT (Speech-to-Text via `SpeechRecognition`) and TTS (Text-to-Speech via `speechSynthesis`).

**Current limitations:**
- TTS uses whatever default voice the browser picks — no voice selection
- Speech rate is hardcoded to `1` and pitch to `1` — no user control
- No way to preview voices before selecting one
- The `speakResponse()` function is basic (4 lines)

This phase adds user-configurable voice controls to the Settings screen.

## Reference Files (READ THESE FIRST)
- `d:\sg\frontend\app.js` — Read full file. Focus on:
  - Lines 343-356: `speakResponse()` — the current basic TTS function
  - Lines 118-211: `setupVoiceRecognition()` — STT setup using Web Speech API
  - Lines 330-341: `typeResponse()` — the typing effect on the home screen
- `d:\sg\frontend\index.html` — Read lines 452-487 for the existing "VOICE ASSISTANT" settings group. This is where you'll add new controls.
- `d:\sg\frontend\style.css` — Read for design tokens. Important: `--font-body`, `--font-mono`, `--bg-input`, `--border-glow`, `--cyan`, `--text-primary`, `--text-secondary`.

**No backend changes needed for this phase.** This is 100% frontend.

## Goal
Add voice selection dropdown, speech rate slider, and pitch slider to the Settings screen, and use them in the TTS function.

## What to do

### 1. Modify `d:\sg\frontend\index.html`
Inside the "VOICE ASSISTANT" settings group (lines 452-487), add these new items AFTER the Language selector (after line 486, before the closing `</div>` of the group):

```html
<div class="setting-item">
    <label class="setting-label" for="tts-voice">Voice</label>
    <select class="setting-select" id="tts-voice">
        <option value="">Loading voices...</option>
    </select>
</div>
<div class="setting-item">
    <label class="setting-label" for="tts-rate">Speech Rate</label>
    <div class="slider-row">
        <input type="range" class="setting-slider" id="tts-rate" min="0.5" max="2" step="0.1" value="1">
        <span class="slider-value" id="tts-rate-val">1.0x</span>
    </div>
</div>
<div class="setting-item">
    <label class="setting-label" for="tts-pitch">Pitch</label>
    <div class="slider-row">
        <input type="range" class="setting-slider" id="tts-pitch" min="0.5" max="2" step="0.1" value="1">
        <span class="slider-value" id="tts-pitch-val">1.0</span>
    </div>
</div>
<div class="setting-item row">
    <div>
        <span class="setting-label">Test Voice</span>
        <span class="setting-desc">Preview current voice settings</span>
    </div>
    <button class="setting-test-btn" id="btn-test-voice">
        <i class="fas fa-volume-high"></i> Test
    </button>
</div>
```

### 2. Modify `d:\sg\frontend\style.css`
Add styles for the slider at the END of the file:

```css
/* Voice Settings Sliders */
.slider-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 6px;
}

.setting-slider {
    flex: 1;
    -webkit-appearance: none;
    appearance: none;
    height: 4px;
    background: var(--border-glow);
    border-radius: 2px;
    outline: none;
}

.setting-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--cyan);
    cursor: pointer;
    box-shadow: 0 0 8px var(--cyan-glow);
}

.slider-value {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--cyan);
    min-width: 35px;
    text-align: right;
}
```

### 3. Modify `d:\sg\frontend\app.js`

**A. Add voice population function (add near the top of the IIFE, or in `init()`):**
```javascript
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

// Voices load asynchronously in some browsers
if ('speechSynthesis' in window) {
    speechSynthesis.onvoiceschanged = populateVoices;
    populateVoices(); // Try immediately too
}
```

**B. Add slider value display handlers:**
```javascript
document.getElementById('tts-rate')?.addEventListener('input', (e) => {
    document.getElementById('tts-rate-val').textContent = parseFloat(e.target.value).toFixed(1) + 'x';
});

document.getElementById('tts-pitch')?.addEventListener('input', (e) => {
    document.getElementById('tts-pitch-val').textContent = parseFloat(e.target.value).toFixed(1);
});
```

**C. Replace the existing `speakResponse()` function with an enhanced version:**
```javascript
function speakResponse(text) {
    if (!('speechSynthesis' in window)) return;
    
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Get user-selected voice
    const voiceSelect = document.getElementById('tts-voice');
    const voices = window.speechSynthesis.getVoices();
    if (voiceSelect && voiceSelect.value !== '' && voices[voiceSelect.value]) {
        utterance.voice = voices[voiceSelect.value];
    }
    
    // Get language from settings
    const langSelect = document.getElementById('voice-lang');
    utterance.lang = langSelect ? langSelect.value : 'en-US';
    
    // Get rate and pitch from sliders
    const rateSlider = document.getElementById('tts-rate');
    const pitchSlider = document.getElementById('tts-pitch');
    utterance.rate = rateSlider ? parseFloat(rateSlider.value) : 1;
    utterance.pitch = pitchSlider ? parseFloat(pitchSlider.value) : 1;
    
    window.speechSynthesis.speak(utterance);
}
```

**D. Add test voice button handler:**
```javascript
document.getElementById('btn-test-voice')?.addEventListener('click', () => {
    speakResponse('Hello! I am SG CUBE, your AI assistant. This is how I sound with the current voice settings.');
});
```

**E. Call `populateVoices()` in `init()` or when navigating to Settings:**
Add to the navigation handler where `screen-settings` becomes active:
```javascript
if (target === 'screen-settings') {
    populateVoices();
    checkOllamaStatus(); // already exists
}
```

## Critical Rules
- NO backend changes in this phase
- DO NOT break the existing `setupVoiceRecognition()` STT logic
- DO NOT change the `sendToBackend()` or `setupChat()` functions
- The voice dropdown must auto-populate from `speechSynthesis.getVoices()` — NOT hardcoded
- Sliders must show their current value as the user drags them
- The "Test" button must use the currently selected voice, rate, and pitch

## Verify
1. Open the frontend, go to Settings → VOICE ASSISTANT section
2. Voice dropdown shows all available browser voices (Chrome typically has 20+ voices)
3. Drag the Speech Rate slider → value label updates in real-time (e.g. "1.5x")
4. Drag the Pitch slider → value label updates
5. Click "Test" → hear the selected voice with current rate/pitch settings
6. Go to Home screen, say a voice command → AI response is spoken with the selected voice settings
7. Go to Chat screen, type a message with TTS enabled → response spoken with selected voice
8. All existing functionality unchanged
