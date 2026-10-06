/* PRIVACY//FIELD GitHub Pages build: all scoring runs in this browser. */
(() => {
  "use strict";

  const state = { framework: null, groups: [], step: 0, responses: {}, assessment: null, reportUrl: null };
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const levelColors = { LOW: "#a4ffd7", MODERATE: "#dcff7a", HIGH: "#ffc876", CRITICAL: "#ff817d" };
  const levelClass = { LOW: "low", MODERATE: "moderate", HIGH: "high", CRITICAL: "critical" };
  const priorityOrder = { IMMEDIATE: 0, IMPORTANT: 1, "GOOD PRACTICE": 2 };

  const escapeHTML = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[char]));

  async function readJSON(relativePath) {
    const response = await fetch(new URL(relativePath, document.baseURI), { cache: "no-store" });
    if (!response.ok) throw new Error(`Could not load ${relativePath} (${response.status})`);
    return response.json();
  }

  let toastTimer;
  function toast(message) {
    const node = $("#toast");
    node.textContent = message;
    node.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => node.classList.remove("show"), 3000);
  }

  function setupReveal() {
    if (!("IntersectionObserver" in window)) {
      $$(".reveal").forEach((node) => node.classList.add("visible"));
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { entry.target.classList.add("visible"); observer.unobserve(entry.target); }
      });
    }, { threshold: 0.08 });
    $$(".reveal").forEach((node) => observer.observe(node));
  }

  function setupSignalCanvas() {
    const canvas = $("#signal-canvas");
    if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    let width = 0, height = 0, frame = 0;
    const particles = [];
    function resize() {
      const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
      width = canvas.clientWidth; height = canvas.clientHeight;
      canvas.width = width * ratio; canvas.height = height * ratio;
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      particles.length = 0;
      const count = Math.min(54, Math.max(22, Math.floor((width * height) / 26000)));
      for (let i = 0; i < count; i += 1) particles.push({
        x: Math.random() * width, y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.18, vy: (Math.random() - 0.5) * 0.18,
        r: Math.random() * 1.35 + 0.45,
      });
    }
    function draw() {
      ctx.clearRect(0, 0, width, height);
      for (let i = 0; i < particles.length; i += 1) {
        const a = particles[i]; a.x += a.vx; a.y += a.vy;
        if (a.x < -4) a.x = width + 4; if (a.x > width + 4) a.x = -4;
        if (a.y < -4) a.y = height + 4; if (a.y > height + 4) a.y = -4;
        ctx.beginPath(); ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(164,255,215,.45)"; ctx.fill();
        for (let j = i + 1; j < particles.length; j += 1) {
          const b = particles[j], distance = Math.hypot(a.x - b.x, a.y - b.y);
          if (distance < 95) {
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
            ctx.strokeStyle = `rgba(116,205,173,${(1 - distance / 95) * 0.11})`;
            ctx.lineWidth = 0.65; ctx.stroke();
          }
        }
      }
      frame = requestAnimationFrame(draw);
    }
    resize(); draw();
    window.addEventListener("resize", resize, { passive: true });
    window.addEventListener("pagehide", () => cancelAnimationFrame(frame), { once: true });
  }

  function initializeResponses() {
    state.responses = {};
    state.groups.forEach((group) => group.questions.forEach((question) => { state.responses[question.id] = "NOT_SURE"; }));
  }

  function renderSteps() {
    const step = state.groups[state.step];
    if (!step) return;
    const index = state.step + 1, total = state.groups.length;
    $("#step-count").textContent = `${String(index).padStart(2, "0")} / ${String(total).padStart(2, "0")}`;
    $("#step-kicker").textContent = `CATEGORY ${String(index).padStart(2, "0")}`;
    $("#progress-fill").style.width = `${(index / total) * 100}%`;
    $("#previous-step").disabled = state.step === 0;
    $("#previous-step").style.opacity = state.step === 0 ? ".4" : "1";
    $("#next-step").hidden = state.step === total - 1;
    $("#submit-assessment").hidden = state.step !== total - 1;
    $("#step-list").innerHTML = state.groups.map((group, i) => `
      <button type="button" class="step-nav ${i === state.step ? "active" : ""} ${i < state.step ? "done" : ""}" data-step="${i}" aria-current="${i === state.step ? "step" : "false"}">
        <span>${String(i + 1).padStart(2, "0")}</span><span>${escapeHTML(group.short)}</span><span class="step-check">✓</span>
      </button>`).join("");
    const firstQuestionIndex = state.groups.slice(0, state.step).reduce((sum, group) => sum + group.questions.length, 0);
    const questionsHTML = step.questions.map((question, questionIndex) => {
      const globalIndex = String(firstQuestionIndex + questionIndex + 1).padStart(2, "0");
      const options = question.options.map((option) => `
        <label class="answer-option"><input type="radio" name="${escapeHTML(question.id)}" value="${escapeHTML(option.value)}" ${state.responses[question.id] === option.value ? "checked" : ""}><span>${escapeHTML(option.label)}</span></label>`).join("");
      return `<article class="question-item"><div class="question-title-row"><span class="q-index">${globalIndex}</span><h3 class="question-title">${escapeHTML(question.prompt)}</h3></div><p class="question-help">${escapeHTML(question.help)}</p><div class="answer-options" role="radiogroup" aria-label="${escapeHTML(question.prompt)}">${options}</div></article>`;
    }).join("");
    $("#question-step").innerHTML = `<h2 class="question-group-title">${escapeHTML(step.label)}</h2><p class="question-group-description">${escapeHTML(step.description)}</p>${questionsHTML}`;
  }

  function openAssessment() {
    const section = $("#assessment"); section.hidden = false;
    section.scrollIntoView({ behavior: "smooth", block: "start" });
    if (!state.groups.length) { toast("The questionnaire is loading. Try again in a moment."); return; }
    renderSteps();
  }

  function validateResponses(responses) {
    const questions = Object.fromEntries(state.groups.flatMap((group) => group.questions.map((question) => [question.id, question])));
    const ids = Object.keys(questions);
    if (!responses || typeof responses !== "object" || Array.isArray(responses)) throw new Error("Answers must be a fixed-choice map.");
    if (Object.keys(responses).length !== ids.length || ids.some((id) => !(id in responses))) throw new Error("Please answer all questionnaire sections.");
    for (const [id, answer] of Object.entries(responses)) {
      if (!questions[id] || typeof answer !== "string" || !(answer in questions[id].risk_by_value)) throw new Error("One or more answers are invalid.");
    }
    return questions;
  }

  function classify(score) {
    if (score <= 20) return "LOW";
    if (score <= 40) return "MODERATE";
    if (score <= 70) return "HIGH";
    return "CRITICAL";
  }

  function calculate(responses) {
    const questions = validateResponses(responses);
    const featureRatios = {}, categoryScores = {};
    for (const group of state.groups) {
      const ratios = group.questions.map((question) => {
        const points = question.risk_by_value[responses[question.id]];
        featureRatios[question.id] = points / question.max_points;
        return featureRatios[question.id];
      });
      const average = ratios.reduce((sum, value) => sum + value, 0) / ratios.length;
      const peak = Math.max(...ratios);
      const score = Math.max(0, Math.min(100, Math.round((0.60 * peak + 0.40 * average) * 100)));
      categoryScores[group.key] = { label: group.label, short: group.short, weight: group.weight, score };
    }
    const weightTotal = state.groups.reduce((sum, group) => sum + group.weight, 0);
    const overall = Math.max(0, Math.min(100, Math.round(state.groups.reduce((sum, group) => sum + categoryScores[group.key].score * group.weight, 0) / weightTotal)));
    const findings = [];
    for (const group of state.groups) for (const question of group.questions) {
      const points = question.risk_by_value[responses[question.id]];
      if (points <= 0) continue;
      findings.push({
        finding_type: question.id, category: group.key, category_label: group.label,
        title: question.finding_title, description: question.help,
        severity: points >= 3 ? "HIGH" : points >= 2 ? "MEDIUM" : "LOW",
        priority: question.priority, risk_points: points, recommendation: question.recommendation,
      });
    }
    findings.sort((a, b) => (priorityOrder[a.priority] - priorityOrder[b.priority]) || (b.risk_points - a.risk_points) || a.category_label.localeCompare(b.category_label));
    const seen = new Set();
    const recommendations = findings.filter((finding) => {
      const key = `${finding.finding_type}|${finding.recommendation}`;
      if (seen.has(key)) return false; seen.add(key); return true;
    }).map((finding) => ({
      finding_type: finding.finding_type, category: finding.category, category_label: finding.category_label,
      risk: finding.title, recommendation: finding.recommendation, priority: finding.priority,
    }));
    const controls = state.groups.flatMap((group) => group.questions).filter((question) =>
      Object.keys(question.risk_by_value).length === 4 && question.risk_by_value.YES === 0 && question.risk_by_value.NO === 4);
    const enabled = controls.filter((question) => responses[question.id] === "YES").length;
    return {
      assessment_id: `LOCAL-${new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14)}`,
      overall_score: overall, risk_level: classify(overall), category_scores: categoryScores,
      findings, recommendations, finding_count: findings.length, recommendation_count: recommendations.length,
      security_controls_enabled: enabled, security_controls_total: controls.length,
      assessed_at: new Date().toISOString(),
      disclaimer: "Educational self-assessment only. Scores reflect selected answers and model assumptions; they are not a prediction or guarantee of compromise or safety.",
    };
  }

  function buildRadar(target, categoryEntries) {
    const data = categoryEntries.map((item) => ({ label: item.short || item.label, score: Math.max(0, Math.min(100, Number(item.score) || 0)) }));
    const width = 340, height = 260, cx = 170, cy = 126, radius = 82, count = data.length;
    const pointAt = (index, level) => { const angle = -Math.PI / 2 + (Math.PI * 2 * index) / count; return [cx + Math.cos(angle) * radius * level, cy + Math.sin(angle) * radius * level]; };
    const polygons = [0.25, 0.5, 0.75, 1].map((level) => `<polygon class="radar-grid" points="${data.map((_, i) => pointAt(i, level).join(",")).join(" ")}"/>`).join("");
    const axes = data.map((item, i) => {
      const [x, y] = pointAt(i, 1), [lx, ly] = pointAt(i, 1.19), anchor = lx < cx - 8 ? "end" : lx > cx + 8 ? "start" : "middle";
      return `<line class="radar-axis" x1="${cx}" y1="${cy}" x2="${x}" y2="${y}"/><text class="radar-label" x="${lx}" y="${ly}" text-anchor="${anchor}" dominant-baseline="middle">${escapeHTML(item.label)}</text>`;
    }).join("");
    const values = data.map((item, i) => pointAt(i, item.score / 100).join(",")).join(" ");
    const dots = data.map((item, i) => { const [x, y] = pointAt(i, item.score / 100); return `<circle class="radar-point" cx="${x}" cy="${y}" r="3"/>`; }).join("");
    target.innerHTML = `<svg viewBox="0 0 ${width} ${height}" aria-hidden="true"><title>Category risk levels, zero to one hundred</title>${polygons}${axes}<polygon class="radar-shape" points="${values}"/>${dots}</svg>`;
  }

  function renderDashboard(data) {
    $("#cohort-size").textContent = Number(data.sample_size || 0).toLocaleString();
    $("#cohort-average").textContent = Number(data.average_score || 0).toFixed(1);
    $("#average-meter").style.width = `${Math.min(100, Number(data.average_score || 0))}%`;
    const distribution = data.risk_distribution || {};
    $("#high-share").textContent = (Number(distribution.HIGH || 0) + Number(distribution.CRITICAL || 0)).toFixed(1);
    const top = (data.top_weaknesses || [])[0];
    $("#top-signal").textContent = top ? top.label : "No elevated signal";
    $("#top-signal-rate").textContent = top ? `${top.rate}% of the fictional cohort` : "No cohort data";
    $("#donut-center").textContent = Number(data.sample_size || 0).toLocaleString();
    const bands = [{ key: "LOW", color: levelColors.LOW }, { key: "MODERATE", color: levelColors.MODERATE }, { key: "HIGH", color: levelColors.HIGH }, { key: "CRITICAL", color: levelColors.CRITICAL }];
    let start = 0;
    const stops = bands.map((band) => { const extent = Number(distribution[band.key] || 0); const stop = `${band.color} ${start}% ${start + extent}%`; start += extent; return stop; });
    $("#risk-donut").style.background = `conic-gradient(${stops.join(",")})`;
    $("#risk-legend").innerHTML = bands.map((band) => `<div><i style="background:${band.color}"></i><span>${band.key}</span><b>${Number(distribution[band.key] || 0).toFixed(1)}%</b></div>`).join("");
    buildRadar($("#cohort-radar"), data.category_averages || []);
    $("#weakness-bars").innerHTML = (data.top_weaknesses || []).slice(0, 5).map((item) => `<div class="weakness-row"><span>${escapeHTML(item.label)}</span><div class="weakness-track"><i style="width:${Math.min(100, Number(item.rate) || 0)}%"></i></div><b>${Number(item.rate).toFixed(0)}%</b></div>`).join("");
    $("#security-controls").innerHTML = (data.security_controls || []).map((item) => `<div class="control-row"><span>${escapeHTML(item.label)}</span><div class="control-track"><i style="width:${Math.min(100, Number(item.enabled_percent) || 0)}%"></i></div><b>${Number(item.enabled_percent).toFixed(0)}%</b></div>`).join("");
  }

  function makeReportHTML(result) {
    const categories = Object.values(result.category_scores).map((item) => `<tr><td>${escapeHTML(item.label)}</td><td>${item.score}/100</td><td>${item.weight}%</td></tr>`).join("");
    const findings = result.findings.slice(0, 12).map((item) => `<li><strong>${escapeHTML(item.title)}</strong> <small>${escapeHTML(item.priority)}</small><br>${escapeHTML(item.recommendation)}</li>`).join("") || "<li>No elevated findings in this educational model.</li>";
    const recommendations = result.recommendations.slice(0, 12).map((item) => `<li><small>${escapeHTML(item.priority)}</small> ${escapeHTML(item.recommendation)}</li>`).join("") || "<li>Maintain current practices and review settings periodically.</li>";
    const checklist = (state.checklist || []).map((item) => `<li>□ ${escapeHTML(item.text)}</li>`).join("");
    return `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Privacy Field Report</title><style>body{margin:0;background:#f3f7f4;color:#172629;font:15px/1.55 system-ui,sans-serif}main{max-width:850px;margin:30px auto;padding:42px;background:white;border:1px solid #d8e4de;border-radius:18px}header{display:flex;justify-content:space-between;gap:20px;border-bottom:1px solid #d8e4de;padding-bottom:20px}.eyebrow{color:#09816a;font-size:11px;letter-spacing:.14em;font-weight:800}h1{font-size:30px;margin:8px 0}h2{font-size:18px;margin:25px 0 8px}.score{font-size:36px;font-weight:850;color:#09816a}small{display:inline-block;color:#176c5d;background:#e8f7f1;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:800;margin:0 5px}table{width:100%;border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #e0e8e4;text-align:left}li{padding:6px 0}.notice{margin-top:24px;padding:15px;border-radius:10px;background:#f0f5f2;color:#526268;font-size:12px}button{position:fixed;top:15px;right:15px;background:#10262a;color:white;border:0;border-radius:99px;padding:12px 16px;font-weight:700;cursor:pointer}@media print{button{display:none}body{background:#fff}main{margin:0 auto;border:0}}@media(max-width:600px){main{margin:10px;padding:20px}header{display:block}}</style><body><button onclick="window.print()">Print / Save as PDF</button><main><header><div><div class="eyebrow">PRIVACY//FIELD · LOCAL-ONLY REPORT</div><h1>Social media privacy assessment</h1><div>Assessment ${escapeHTML(result.assessment_id)}<br>${escapeHTML(new Date(result.assessed_at).toLocaleString())}</div></div><div class="score">${result.overall_score}<small>/100 · ${escapeHTML(result.risk_level)}</small></div></header><h2>Category scores</h2><table><thead><tr><th>Category</th><th>Risk</th><th>Weight</th></tr></thead><tbody>${categories}</tbody></table><h2>Top findings and actions</h2><ol>${findings}</ol><h2>Recommendations</h2><ol>${recommendations}</ol><h2>Privacy checklist</h2><ul>${checklist}</ul><div class="notice"><b>Disclaimer:</b> Higher means higher assessed exposure in this educational model. The score is not a prediction or guarantee of compromise or safety. This local-only report contains no questionnaire answers or sensitive profile data.</div></main></body></html>`;
  }

  function renderResult(result) {
    state.assessment = result;
    const section = $("#results"), score = result.overall_score, color = levelColors[result.risk_level] || levelColors.LOW;
    section.hidden = false;
    $("#overall-score").textContent = score;
    $("#score-gauge").style.background = `conic-gradient(${color} ${score}%, rgba(255,255,255,.08) 0)`;
    $("#risk-badge").textContent = result.risk_level;
    $("#risk-badge").className = `risk-badge ${levelClass[result.risk_level] || ""}`;
    $("#assessment-reference").textContent = result.assessment_id;
    $("#finding-count").textContent = `${result.finding_count} FLAGS`;
    $("#result-date").textContent = new Date(result.assessed_at).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }).toUpperCase();
    if (state.reportUrl) URL.revokeObjectURL(state.reportUrl);
    state.reportUrl = URL.createObjectURL(new Blob([makeReportHTML(result)], { type: "text/html;charset=utf-8" }));
    $("#report-link").href = state.reportUrl;

    const categories = Object.entries(result.category_scores).map(([key, item]) => ({ key, ...item }));
    buildRadar($("#result-radar"), categories);
    $("#category-list").innerHTML = categories.map((item) => `<div class="category-row"><span>${escapeHTML(item.label)}</span><b>${item.score}/100</b><div class="cat-meter"><i style="width:${item.score}%"></i></div></div>`).join("");
    $("#findings-list").innerHTML = result.findings.length ? result.findings.slice(0, 12).map((item) => `<article class="finding-item"><span class="finding-mark">!</span><div><h4>${escapeHTML(item.title)}</h4><p>${escapeHTML(item.recommendation || item.description)}</p><div class="finding-meta">${escapeHTML(item.category_label)} · ${escapeHTML(item.severity)} SEVERITY · ${escapeHTML(item.priority)}</div></div></article>`).join("") : `<p class="empty-state">No elevated findings. Keep reviewing settings periodically.</p>`;
    $("#recommendations-list").innerHTML = result.recommendations.length ? result.recommendations.slice(0, 10).map((item) => {
      const className = item.priority === "IMMEDIATE" ? "" : item.priority === "IMPORTANT" ? "important" : "good-practice";
      return `<article class="recommendation-item"><span class="priority-tag ${className}">${escapeHTML(item.priority)}</span><div><h4>${escapeHTML(item.category_label)}</h4><p>${escapeHTML(item.recommendation)}</p></div></article>`;
    }).join("") : `<p class="empty-state">No priority actions were generated. Review the checklist periodically.</p>`;
    renderImprovements(result);
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderImprovements(result) {
    const findings = new Set(result.findings.map((item) => item.finding_type));
    $("#improvement-options").innerHTML = state.framework.improvements.map((action) => `<label class="improvement-option"><input type="checkbox" value="${escapeHTML(action.id)}" ${findings.has(action.id) ? "checked" : ""}><span><b class="improvement-group">${escapeHTML(action.group)}</b>${escapeHTML(action.label)}</span></label>`).join("");
    $("#simulation-result").innerHTML = `<span class="sim-placeholder">Select one or more improvements to see a simulated score.</span>`;
  }

  function renderSimulation(before, after, changes) {
    const reduction = Math.max(0, before.overall_score - after.overall_score);
    const delta = reduction > 0 ? `↓ ${reduction} POINT${reduction === 1 ? "" : "S"}` : "NO SCORE CHANGE";
    $("#simulation-result").innerHTML = `<div class="simulation-summary"><span>NOW <strong>${before.overall_score}</strong> · ${before.risk_level}</span><span class="delta ${reduction ? "" : "no-change"}">${delta}</span><span>SIMULATED <strong>${after.overall_score}</strong> · ${after.risk_level}</span><small>Framework simulation only; not a guarantee of real-world safety.</small></div>`;
  }

  function setupControls() {
    $$('[data-start-assessment]').forEach((button) => button.addEventListener("click", openAssessment));
    $("#previous-step").addEventListener("click", () => { if (state.step > 0) { state.step -= 1; renderSteps(); } });
    $("#next-step").addEventListener("click", () => { if (state.step < state.groups.length - 1) { state.step += 1; renderSteps(); } });
    $("#step-list").addEventListener("click", (event) => { const button = event.target.closest("[data-step]"); if (button) { state.step = Number(button.dataset.step); renderSteps(); } });
    $("#question-step").addEventListener("change", (event) => { if (event.target.matches('input[type="radio"]')) state.responses[event.target.name] = event.target.value; });
    $("#load-demo").addEventListener("click", () => {
      state.responses = { ...state.demo.responses };
      renderSteps();
      toast("Fictional demo loaded locally. No profile was accessed.");
    });
    $("#submit-assessment").addEventListener("click", (event) => {
      const button = event.currentTarget;
      button.disabled = true; button.textContent = "Scoring in this browser…";
      try { renderResult(calculate(state.responses)); }
      catch (error) { toast(error.message); }
      finally { button.disabled = false; button.innerHTML = 'Generate my readout <span aria-hidden="true">↗</span>'; }
    });
    $("#run-simulation").addEventListener("click", () => {
      const changes = $$("#improvement-options input:checked").map((input) => input.value);
      if (!changes.length) { toast("Choose at least one improvement to simulate."); return; }
      const simulated = { ...state.responses };
      for (const id of changes) {
        if (!(id in state.framework.safe_improvement_values)) { toast("An improvement was not recognized."); return; }
        simulated[id] = state.framework.safe_improvement_values[id];
      }
      renderSimulation(calculate(state.responses), calculate(simulated), changes);
    });
    $("#delete-assessment").addEventListener("click", () => {
      state.assessment = null;
      if (state.reportUrl) { URL.revokeObjectURL(state.reportUrl); state.reportUrl = null; }
      $("#results").hidden = true;
      initializeResponses(); renderSteps();
      $("#assessment").hidden = false; $("#assessment").scrollIntoView({ behavior: "smooth" });
      toast("Local readout cleared. Nothing was stored on a server.");
    });
    $("#checklist-download").addEventListener("click", (event) => {
      event.preventDefault();
      const text = ["SOCIAL MEDIA PRIVACY CHECKLIST", "", ...state.checklist.map((item) => `□ ${item.text}`), "", "Review settings directly in the platform. Educational guidance only."].join("\n");
      const url = URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" }));
      const link = document.createElement("a"); link.href = url; link.download = "social-media-privacy-checklist.txt";
      document.body.appendChild(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000); toast("Checklist downloaded.");
    });
  }

  async function init() {
    setupReveal(); setupSignalCanvas(); setupControls();
    try {
      const [framework, dashboard, demo, checklist] = await Promise.all([
        readJSON("data/framework.json"), readJSON("data/dashboard.json"),
        readJSON("data/demo-profile.json"), readJSON("data/checklist.json"),
      ]);
      state.framework = framework; state.groups = framework.groups; state.demo = demo; state.checklist = checklist.checklist;
      initializeResponses(); renderSteps(); renderDashboard(dashboard);
    } catch (error) {
      toast(`Static site data failed to load: ${error.message}. Serve this folder over HTTP.`);
      console.error(error);
    }
  }

  document.addEventListener("DOMContentLoaded", init, { once: true });
})();
