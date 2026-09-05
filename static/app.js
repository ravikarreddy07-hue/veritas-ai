/**
 * Frontend Controller for Veritas AI Website & Studio.
 */

let currentTone = 'natural';
let currentIntensity = 'balanced';
let samplesCache = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    fetchSamples();
    setTimeout(() => {
        loadSample('ai_essay');
    }, 200);
});

async function fetchSamples() {
    try {
        const res = await fetch('/api/samples');
        if (res.ok) {
            samplesCache = await res.json();
        }
    } catch (err) {
        console.error('Failed to load sample texts:', err);
    }
}

function loadSample(key) {
    if (!samplesCache || !samplesCache[key]) {
        if (key === 'ai_essay') {
            document.getElementById('input-text').value =
                "In today's fast-paced digital world, artificial intelligence plays a crucial role in modern society. " +
                "Furthermore, it is important to note that machine learning algorithms foster innovation across multifaceted industries. " +
                "A rich tapestry of computational tools serves as a testament to human ingenuity. " +
                "Moreover, navigating the complexities of data science requires a holistic approach to succeed.";
        }
    } else {
        document.getElementById('input-text').value = samplesCache[key].text;
    }
    updateWordCount();
    runDetection();
}

function updateWordCount() {
    const text = document.getElementById('input-text').value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    const chars = text.length;
    const readTime = Math.max(1, Math.ceil(words / 200));

    document.getElementById('word-count-badge').textContent = `${words} words`;
    document.getElementById('char-count-badge').textContent = `${chars} characters`;
    document.getElementById('read-time-badge').textContent = `${words > 0 ? readTime : 0} min read`;
}

async function pasteToInput() {
    try {
        const text = await navigator.clipboard.readText();
        if (text) {
            document.getElementById('input-text').value = text;
            updateWordCount();
            runDetection();
            showToast('Pasted from clipboard!');
        }
    } catch (err) {
        showToast('Please paste manually using Ctrl+V');
    }
}

function clearInput() {
    document.getElementById('input-text').value = '';
    updateWordCount();
    document.getElementById('detector-results').classList.add('hidden');
    document.getElementById('humanizer-results').classList.add('hidden');
}

// Tone Selector
function setTone(tone) {
    currentTone = tone;
    document.querySelectorAll('.tone-btn').forEach(btn => {
        btn.classList.remove('bg-purple-600', 'text-white', 'border-purple-500');
        btn.classList.add('bg-slate-800', 'text-slate-300', 'border-slate-700');
    });
    const activeBtn = document.getElementById(`tone-${tone}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-slate-800', 'text-slate-300', 'border-slate-700');
        activeBtn.classList.add('bg-purple-600', 'text-white', 'border-purple-500');
    }
}

// Intensity Selector
function setIntensity(intensity) {
    currentIntensity = intensity;
    document.querySelectorAll('.int-btn').forEach(btn => {
        btn.classList.remove('bg-purple-600', 'text-white', 'border-purple-500');
        btn.classList.add('bg-slate-800', 'text-slate-300', 'border-slate-700');
    });
    const activeBtn = document.getElementById(`int-${intensity}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-slate-800', 'text-slate-300', 'border-slate-700');
        activeBtn.classList.add('bg-purple-600', 'text-white', 'border-purple-500');
    }

    const descEl = document.getElementById('intensity-desc');
    if (intensity === 'mild') {
        descEl.textContent = 'Mild: focuses on replacing obvious AI clichés and buzzwords.';
    } else if (intensity === 'balanced') {
        descEl.textContent = 'Balanced: removes clichés, injects cadence punches, and drops AI score under 20%.';
    } else {
        descEl.textContent = 'Stealth (<10%): deep burstiness restructuring, clause splitting, and authentic human cadence.';
    }
}

function toggleOllama() {
    const check = document.getElementById('use-ollama-check');
    const settings = document.getElementById('ollama-settings');
    if (check.checked) {
        settings.classList.remove('hidden');
        settings.classList.add('flex');
    } else {
        settings.classList.add('hidden');
        settings.classList.remove('flex');
    }
}

// Detection Request
async function runDetection() {
    const text = document.getElementById('input-text').value.trim();
    if (!text) {
        showToast('Please enter text to analyze');
        return;
    }

    const btn = document.getElementById('detect-btn');
    const btnText = document.getElementById('detect-btn-text');
    btn.disabled = true;
    btnText.textContent = 'Analyzing Forensic Signals...';

    try {
        const response = await fetch('/api/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error('Detection failed');
        }

        const data = await response.json();
        renderDetectionResults(data);
    } catch (err) {
        console.error(err);
        showToast('Error during detection: ' + err.message);
    } finally {
        btn.disabled = false;
        btnText.textContent = 'Detect AI Content';
        lucide.createIcons();
    }
}

function renderDetectionResults(data) {
    const container = document.getElementById('detector-results');
    container.classList.remove('hidden');

    const score = data.ai_percentage;
    const scoreCircle = document.getElementById('score-circle');
    const scorePercentage = document.getElementById('score-percentage');
    const verdictTitle = document.getElementById('verdict-title');
    const verdictDesc = document.getElementById('verdict-desc');

    scorePercentage.textContent = `${score}%`;
    scoreCircle.setAttribute('stroke-dasharray', `${score}, 100`);

    if (score >= 65) {
        scoreCircle.setAttribute('class', 'text-red-500 transition-all duration-700 ease-out');
        verdictTitle.className = 'text-xl font-bold text-red-400 mt-0.5';
    } else if (score >= 40) {
        scoreCircle.setAttribute('class', 'text-yellow-500 transition-all duration-700 ease-out');
        verdictTitle.className = 'text-xl font-bold text-yellow-400 mt-0.5';
    } else {
        scoreCircle.setAttribute('class', 'text-emerald-400 transition-all duration-700 ease-out');
        verdictTitle.className = 'text-xl font-bold text-emerald-400 mt-0.5';
    }

    verdictTitle.textContent = data.verdict;
    verdictDesc.textContent = data.explanation;

    // Metrics
    document.getElementById('metric-burstiness').textContent = data.metrics.burstiness_index;
    document.getElementById('metric-ttr').textContent = `${data.metrics.vocabulary_ttr}%`;
    document.getElementById('metric-cliches').textContent = data.metrics.cliche_count;
    document.getElementById('metric-grade').textContent = `Gr. ${data.metrics.flesch_kincaid_grade}`;

    // Sentence Heatmap
    renderSentenceHeatmap(data.sentences);
}

function renderSentenceHeatmap(sentences) {
    const heatmapEl = document.getElementById('heatmap-container');
    heatmapEl.innerHTML = '';

    if (!sentences || sentences.length === 0) {
        heatmapEl.innerHTML = '<span class="text-slate-500">No sentences parsed.</span>';
        return;
    }

    sentences.forEach((s) => {
        const span = document.createElement('span');
        let badgeClass = 'heatmap-human';
        if (s.classification === 'Likely AI') badgeClass = 'heatmap-ai';
        else if (s.classification === 'Mixed') badgeClass = 'heatmap-mixed';

        span.className = `heatmap-sentence ${badgeClass}`;
        span.textContent = s.text + ' ';

        span.addEventListener('mouseenter', (e) => showSentenceTooltip(e, s));
        span.addEventListener('mousemove', (e) => moveSentenceTooltip(e));
        span.addEventListener('mouseleave', hideSentenceTooltip);

        heatmapEl.appendChild(span);
    });
}

// Tooltip helpers
const tooltip = document.getElementById('sentence-tooltip');

function showSentenceTooltip(e, sent) {
    const sentNumEl = document.getElementById('tooltip-sent-num');
    const sentScoreEl = document.getElementById('tooltip-sent-score');
    const sentWordsEl = document.getElementById('tooltip-sent-words');
    const sentReasonsEl = document.getElementById('tooltip-sent-reasons');

    sentNumEl.textContent = `Sentence #${sent.id}`;
    sentScoreEl.textContent = `AI Prob: ${sent.score}%`;
    sentWordsEl.textContent = `${sent.words} words`;

    if (sent.score >= 65) {
        sentScoreEl.className = 'font-semibold px-2 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 border border-red-500/30';
    } else if (sent.score >= 40) {
        sentScoreEl.className = 'font-semibold px-2 py-0.5 rounded text-[10px] bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
    } else {
        sentScoreEl.className = 'font-semibold px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
    }

    sentReasonsEl.innerHTML = '';
    sent.reasons.forEach(r => {
        const li = document.createElement('li');
        li.textContent = r;
        sentReasonsEl.appendChild(li);
    });

    moveSentenceTooltip(e);
    tooltip.classList.remove('opacity-0');
}

function moveSentenceTooltip(e) {
    if (window.innerWidth < 640) {
        return; // Handled by CSS bottom docking on mobile
    }
    const x = e.clientX + 15;
    const y = e.clientY + 15;
    tooltip.style.left = `${Math.min(window.innerWidth - 290, Math.max(10, x))}px`;
    tooltip.style.top = `${Math.min(window.innerHeight - 180, Math.max(10, y))}px`;
}

function hideSentenceTooltip() {
    tooltip.classList.add('opacity-0');
}

// Humanizer Request
async function runHumanizer() {
    const text = document.getElementById('input-text').value.trim();
    if (!text) {
        showToast('Please enter text to humanize');
        return;
    }

    const btn = document.getElementById('humanize-btn');
    const btnText = document.getElementById('humanize-btn-text');
    btn.disabled = true;
    btnText.textContent = 'Humanizing Text...';

    const useOllama = document.getElementById('use-ollama-check').checked;
    const ollamaModel = document.getElementById('ollama-model-input').value.trim() || 'llama3';

    try {
        const response = await fetch('/api/humanize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text,
                tone: currentTone,
                intensity: currentIntensity,
                use_ollama: useOllama,
                ollama_model: ollamaModel
            })
        });

        if (!response.ok) {
            throw new Error('Humanization failed');
        }

        const data = await response.json();
        renderHumanizerResults(data);
    } catch (err) {
        console.error(err);
        showToast('Error during humanization: ' + err.message);
    } finally {
        btn.disabled = false;
        btnText.textContent = 'Humanize Text Now';
        lucide.createIcons();
    }
}

function renderHumanizerResults(data) {
    const resultsContainer = document.getElementById('humanizer-results');
    resultsContainer.classList.remove('hidden');

    const originalAi = data.original_analysis.ai_percentage;
    const newAi = data.humanized_analysis.ai_percentage;
    const delta = data.score_delta;

    // Delta Banner
    document.getElementById('delta-banner-text').textContent =
        `AI likelihood reduced from ${originalAi}% to ${newAi}% (${data.humanized_analysis.verdict})`;
    
    const deltaBadge = document.getElementById('delta-badge');
    if (delta > 0) {
        deltaBadge.textContent = `-${delta}% Drop`;
        deltaBadge.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40';
    } else {
        deltaBadge.textContent = 'Optimized';
        deltaBadge.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-400 border border-purple-500/40';
    }

    // Output Textarea
    const outputEl = document.getElementById('output-text');
    outputEl.value = data.humanization.humanized_text;

    // Applied transformations
    const changesList = document.getElementById('applied-changes-list');
    changesList.innerHTML = '';
    const changes = data.humanization.changes_applied;
    if (changes && changes.length > 0) {
        changes.forEach(c => {
            const li = document.createElement('li');
            li.textContent = c;
            changesList.appendChild(li);
        });
    } else {
        changesList.innerHTML = '<li>Cadence adjusted for natural human flow</li>';
    }

    // Generate Diff View
    generateDiffView(data.humanization.original_text, data.humanization.humanized_text);

    setOutputTab('clean');
}

function generateDiffView(original, humanized) {
    const diffContainer = document.getElementById('output-diff-view');
    const origWords = original.split(/\s+/);
    const newWords = humanized.split(/\s+/);

    let html = '';
    let i = 0, j = 0;

    while (i < origWords.length || j < newWords.length) {
        if (i < origWords.length && j < newWords.length && origWords[i].toLowerCase() === newWords[j].toLowerCase()) {
            html += `${newWords[j]} `;
            i++;
            j++;
        } else {
            if (i < origWords.length) {
                html += `<del>${origWords[i]}</del> `;
                i++;
            }
            if (j < newWords.length) {
                html += `<ins>${newWords[j]}</ins> `;
                j++;
            }
        }
    }

    diffContainer.innerHTML = html.trim();
}

function setOutputTab(tab) {
    const cleanView = document.getElementById('output-clean-view');
    const diffView = document.getElementById('output-diff-view');
    const tabClean = document.getElementById('tab-clean');
    const tabDiff = document.getElementById('tab-diff');

    if (tab === 'clean') {
        cleanView.classList.remove('hidden');
        diffView.classList.add('hidden');
        tabClean.className = 'font-semibold text-white border-b-2 border-purple-500 pb-1 flex items-center gap-1';
        tabDiff.className = 'font-medium text-slate-400 hover:text-slate-200 pb-1 flex items-center gap-1';
    } else {
        cleanView.classList.add('hidden');
        diffView.classList.remove('hidden');
        tabDiff.className = 'font-semibold text-white border-b-2 border-purple-500 pb-1 flex items-center gap-1';
        tabClean.className = 'font-medium text-slate-400 hover:text-slate-200 pb-1 flex items-center gap-1';
    }
    lucide.createIcons();
}

async function copyOutput() {
    const text = document.getElementById('output-text').value;
    if (!text) return;
    try {
        await navigator.clipboard.writeText(text);
        showToast('Humanized text copied to clipboard!');
    } catch (err) {
        showToast('Failed to copy. Please select and copy manually.');
    }
}

function downloadText() {
    const text = document.getElementById('output-text').value;
    if (!text) {
        showToast('No humanized text to download');
        return;
    }
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `veritas-humanized-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Downloaded text file!');
}

function sendToDetector() {
    const text = document.getElementById('output-text').value;
    if (!text) return;
    document.getElementById('input-text').value = text;
    updateWordCount();
    runDetection();
    showToast('Sent to detector for re-scanning!');
}

// FAQ Accordion Toggle
function toggleFaq(id) {
    const content = document.getElementById(`faq-content-${id}`);
    const icon = document.getElementById(`faq-icon-${id}`);
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        icon.classList.add('rotate-180');
    } else {
        content.classList.add('hidden');
        icon.classList.remove('rotate-180');
    }
}

function showToast(msg) {
    const toast = document.getElementById('toast');
    const toastText = document.getElementById('toast-text');
    toastText.textContent = msg;

    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');

    setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
        toast.classList.remove('translate-y-0', 'opacity-100');
    }, 2800);
}
