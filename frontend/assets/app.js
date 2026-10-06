/* PRIVACY//FIELD — browser-side UI only. No analytics, cookies, or localStorage. */
(() => {
  "use strict";

  const API = "/api";
  const state = { groups: [], step: 0, responses: {}, assessment: null, actions: [] };
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const levelColors = { LOW: "#a4ffd7", MODERATE: "#dcff7a", HIGH: "#ffc876", CRITICAL: "#ff817d" };
  const levelClass = { LOW: "low", MODERATE: "moderate", HIGH: "high", CRITICAL: "critical" };

  const escapeHTML = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[char]));

  async function api(path, options = {}) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: { ...(options.body ? { "Content-Type": "application/json" } : {}), ...(options.headers || {}) },
    });
    let data = {};
    try { data = await response.json(); } catch (_) { /* A route may return HTML. */ }
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
    return data;
  }

  let toastTimer;
  function toast(message) {
    const node = $("#toast");
    node.textContent = message;
    node.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => node.classList.remove("show"), 3000);
  }

  function showError(message) {
    toast(message || "Something went wrong. Please try again.");
  }

  function setupReveal() {
    if (!("IntersectionObserver" in window)) {
      $$(".reveal").forEach((node) => node.classList.add("visible"));
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    $$(".reveal").forEach((node) => observer.observe(node));
  }

  function setupSignalCanvas() {
    const canvas = $("#signal-canvas");
    if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    let width = 0, height = 0, frame = 0;
    const particles = [];
    function resize() {
      const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = width * ratio;
      canvas.height = height * ratio;
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      particles.length = 0;
      const count = Math.min(54, Math.max(22, Math.floor((width * height) / 26000)));
      for (let i = 0; i < count; i += 1) {
        particles.push({
          x: Math.random() * width, y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.18, vy: (Math.random() - 0.5) * 0.18,
          r: Math.random() * 1.35 + 0.45,
        });
      }
    }
    function draw() {
      context.clearRect(0, 0, width, height);
      for (let i = 0; i < particles.length; i += 1) {
        const a = particles[i];
        a.x += a.vx; a.y += a.vy;
        if (a.x < -4) a.x = width + 4; if (a.x > width + 4) a.x = -4;
        if (a.y < -4) a.y = height + 4; if (a.y > height + 4) a.y = -4;
        context.beginPath(); context.arc(a.x, a.y, a.r, 0, Math.PI * 2);
        context.fillStyle = "rgba(164,255,215,.45)"; context.fill();
        for (let j = i + 1; j < particles.length; j += 1) {
          const b = particles[j];
          const dx = a.x - b.x, dy = a.y - b.y, distance = Math.hypot(dx, dy);
          if (distance < 95) {
            context.beginPath(); context.moveTo(a.x, a.y); context.lineTo(b.x, b.y);
            context.strokeStyle = `rgba(116,205,173,${(1 - distance / 95) * 0.11})`;
            context.lineWidth = 0.65; context.stroke();
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
    state.groups.forEach((group) => group.questions.forEach((question) => {
      state.responses[question.id] = "NOT_SURE";
    }));
  }

  function renderSteps() {
    const step = state.groups[state.step];
    if (!step) return;
    const index = state.step + 1;
    const total = state.groups.length;
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
      const answers = question.options.map((option) => `
        <label class="answer-option">
          <input type="radio" name="${escapeHTML(question.id)}" value="${escapeHTML(option.value)}" ${state.responses[question.id] === option.value ? "checked" : ""}>
          <span>${escapeHTML(option.label)}</span>
        </label>`).join("");
      return `<article class="question-item">
        <div class="question-title-row"><span class="q-index">${globalIndex}</span><h3 class="question-title">${escapeHTML(question.prompt)}</h3></div>
        <p class="question-help">${escapeHTML(question.help)}</p>
        <div class="answer-options" role="radiogroup" aria-label="${escapeHTML(question.prompt)}">${answers}</div>
      </article>`;
    }).join("");
    $("#question-step").innerHTML = `<h2 class="question-group-title">${escapeHTML(step.label)}</h2><p class="question-group-description">${escapeHTML(step.description)}</p>${questionsHTML}`;
  }

  function openAssessment() {
    const section = $("#assessment");
    section.hidden = false;
    section.scrollIntoView({ behavior: "smooth", block: "start" });
    if (!state.groups.length) {
      toast("Questionnaire is loading—try again in a moment.");
      return;
    }
    renderSteps();
  }

  function buildRadar(target, categoryEntries) {
    if (!target) return;
    const data = categoryEntries.map((item) => ({ label: item.label || item.short, score: Math.max(0, Math.min(100, Number(item.score) || 0)) }));
    const width = 340, height = 260, cx = 170, cy = 126, radius = 82, count = data.length;
    const pointAt = (index, level) => {
      const angle = -Math.PI / 2 + (Math.PI * 2 * index) / count;
      return [cx + Math.cos(angle) * radius * level, cy + Math.sin(angle) * radius * level];
    };
    const polygons = [0.25, 0.5, 0.75, 1].map((level) => {
      const points = data.map((_, i) => pointAt(i, level).join(",")).join(" ");
      return `<polygon class="radar-grid" points="${points}"/>`;
    }).join("");
    const axes = data.map((item, i) => {
      const [x, y] = pointAt(i, 1);
      const [lx, ly] = pointAt(i, 1.19);
      const anchor = lx < cx - 8 ? "end" : (lx > cx + 8 ? "start" : "middle");
      return `<line class="radar-axis" x1="${cx}" y1="${cy}" x2="${x}" y2="${y}"/><text class="radar-label" x="${lx}" y="${ly}" text-anchor="${anchor}" dominant-baseline="middle">${escapeHTML(item.label)}</text>`;
    }).join("");
    const valuePoints = data.map((item, i) => pointAt(i, item.score / 100).join(",")).join(" ");
    const dots = data.map((item, i) => {
      const [x, y] = pointAt(i, item.score / 100);
      return `<circle class="radar-point" cx="${x}" cy="${y}" r="3"/>`;
    }).join("");
    target.innerHTML = `<svg viewBox="0 0 ${width} ${height}" aria-hidden="true"><title>Category risk levels, zero to one hundred</title>${polygons}${axes}<polygon class="radar-shape" points="${valuePoints}"/>${dots}</svg>`;
  }

  function renderDashboard(data) {
    $("#cohort-size").textContent = Number(data.sample_size || 0).toLocaleString();
    $("#cohort-average").textContent = Number(data.average_score || 0).toFixed(1);
    $("#average-meter").style.width = `${Math.min(100, Number(data.average_score || 0))}%`;
    const distribution = data.risk_distribution || {};
    const highShare = Number(distribution.HIGH || 0) + Number(distribution.CRITICAL || 0);
    $("#high-share").textContent = highShare.toFixed(1);
    const top = (data.top_weaknesses || [])[0];
    $("#top-signal").textContent = top ? top.label : "No elevated signal";
    $("#top-signal-rate").textContent = top ? `${top.rate}% of the fictional cohort` : "No cohort data";
    $("#donut-center").textContent = Number(data.sample_size || 0).toLocaleString();
    const bands = [
      { key: "LOW", color: levelColors.LOW }, { key: "MODERATE", color: levelColors.MODERATE },
      { key: "HIGH", color: levelColors.HIGH }, { key: "CRITICAL", color: levelColors.CRITICAL },
    ];
    let start = 0;
    const stops = bands.map((band) => {
      const extent = Number(distribution[band.key] || 0);
      const part = `${band.color} ${start}% ${start + extent}%`;
      start += extent;
      return part;
    });
    $("#risk-donut").style.background = `conic-gradient(${stops.join(",")})`;
    $("#risk-legend").innerHTML = bands.map((band) => `
      <div><i style="background:${band.color}"></i><span>${band.key}</span><b>${Number(distribution[band.key] || 0).toFixed(1)}%</b></div>`).join("");
    buildRadar($("#cohort-radar"), (data.category_averages || []).map((item) => ({ label: item.label, score: item.score })));
    $("#weakness-bars").innerHTML = (data.top_weaknesses || []).slice(0, 5).map((item) => `
      <div class="weakness-row"><span>${escapeHTML(item.label)}</span><div class="weakness-track"><i style="width:${Math.min(100, Number(item.rate) || 0)}%"></i></div><b>${Number(item.rate).toFixed(0)}%</b></div>`).join("") || `<p class="empty-state">No synthetic patterns available.</p>`;
    $("#security-controls").innerHTML = (data.security_controls || []).map((item) => `
      <div class="control-row"><span>${escapeHTML(item.label)}</span><div class="control-track"><i style="width:${Math.min(100, Number(item.enabled_percent) || 0)}%"></i></div><b>${Number(item.enabled_percent).toFixed(0)}%</b></div>`).join("") || `<p class="empty-state">No synthetic controls available.</p>`;
  }

  function renderAssessmentResult(result) {
    state.assessment = result;
    const section = $("#results");
    section.hidden = false;
    const score = Number(result.overall_score) || 0;
    const color = levelColors[result.risk_level] || levelColors.LOW;
    $("#overall-score").textContent = score;
    $("#score-gauge").style.background = `conic-gradient(${color} ${score}%, rgba(255,255,255,.08) 0)`;
    $("#risk-badge").textContent = result.risk_level;
    $("#risk-badge").className = `risk-badge ${levelClass[result.risk_level] || ""}`;
    $("#assessment-reference").textContent = `REF ${result.assessment_id || "LOCAL"}`;
    $("#finding-count").textContent = `${result.finding_count || 0} FLAGS`;
    $("#result-date").textContent = new Date(result.assessed_at || Date.now()).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }).toUpperCase();
    $("#report-link").href = `${API}/assessment/${encodeURIComponent(result.assessment_id)}/report`;

    const categories = Object.entries(result.category_scores || {}).map(([key, item]) => ({ key, ...item }));
    buildRadar($("#result-radar"), categories.map((item) => ({ label: item.short, score: item.score })));
    $("#category-list").innerHTML = categories.map((item) => `
      <div class="category-row"><span>${escapeHTML(item.label)}</span><b>${Number(item.score)}/100</b><div class="cat-meter"><i style="width:${Number(item.score)}%"></i></div></div>`).join("");

    const findings = result.findings || [];
    $("#findings-list").innerHTML = findings.length ? findings.slice(0, 12).map((item) => `
      <article class="finding-item"><span class="finding-mark">!</span><div><h4>${escapeHTML(item.title)}</h4><p>${escapeHTML(item.recommendation || item.description)}</p><div class="finding-meta">${escapeHTML(item.category_label)} · ${escapeHTML(item.severity)} SEVERITY · ${escapeHTML(item.priority)}</div></div></article>`).join("") : `<p class="empty-state">No elevated findings in the answers provided. Keep reviewing settings periodically.</p>`;

    const recommendations = result.recommendations || [];
    $("#recommendations-list").innerHTML = recommendations.length ? recommendations.slice(0, 10).map((item) => {
      const className = item.priority === "IMMEDIATE" ? "" : item.priority === "IMPORTANT" ? "important" : "good-practice";
      return `<article class="recommendation-item"><span class="priority-tag ${className}">${escapeHTML(item.priority)}</span><div><h4>${escapeHTML(item.category_label)}</h4><p>${escapeHTML(item.recommendation)}</p></div></article>`;
    }).join("") : `<p class="empty-state">No priority actions were generated. Revisit the checklist in a few months.</p>`;

    renderImprovementOptions(result);
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderImprovementOptions(result) {
    const findings = new Set((result.findings || []).map((item) => item.finding_type));
    $("#improvement-options").innerHTML = state.actions.map((action) => `
      <label class="improvement-option"><input type="checkbox" value="${escapeHTML(action.id)}" ${findings.has(action.id) ? "checked" : ""}>
        <span><b class="improvement-group">${escapeHTML(action.group)}</b>${escapeHTML(action.label)}</span></label>`).join("");
    $("#simulation-result").innerHTML = `<span class="sim-placeholder">Select one or more improvements to see a simulated score.</span>`;
  }

  function renderSimulation(simulation) {
    const reduction = Number(simulation.risk_reduction) || 0;
    const changeText = reduction > 0 ? `↓ ${reduction} POINT${reduction === 1 ? "" : "S"}` : "NO SCORE CHANGE";
    const noChangeClass = reduction > 0 ? "" : "no-change";
    $("#simulation-result").innerHTML = `<div class="simulation-summary"><span>NOW <strong>${simulation.current_score}</strong> · ${escapeHTML(simulation.current_level)}</span><span class="delta ${noChangeClass}">${changeText}</span><span>SIMULATED <strong>${simulation.simulated_score}</strong> · ${escapeHTML(simulation.simulated_level)}</span><small>${escapeHTML(simulation.disclaimer)}</small></div>`;
  }

  async function loadQuestionnaire() {
    const [questionnaire, improvements] = await Promise.all([
      api("/questionnaire"), api("/improvements"),
    ]);
    state.groups = questionnaire.groups || [];
    state.actions = improvements.actions || [];
    initializeResponses();
    renderSteps();
  }

  async function loadDashboard() {
    try {
      const data = await api("/dashboard/stats");
      renderDashboard(data);
    } catch (error) {
      $("#cohort-size").textContent = "—";
      $("#top-signal").textContent = "Demo unavailable";
      $("#top-signal-rate").textContent = "Run the synthetic data generator";
      showError(error.message);
    }
  }

  function setupAssessmentControls() {
    $$('[data-start-assessment]').forEach((button) => button.addEventListener("click", openAssessment));
    $("#previous-step").addEventListener("click", () => {
      if (state.step > 0) { state.step -= 1; renderSteps(); }
    });
    $("#next-step").addEventListener("click", () => {
      if (state.step < state.groups.length - 1) { state.step += 1; renderSteps(); }
    });
    $("#step-list").addEventListener("click", (event) => {
      const button = event.target.closest("[data-step]");
      if (button) { state.step = Number(button.dataset.step); renderSteps(); }
    });
    $("#question-step").addEventListener("change", (event) => {
      if (event.target.matches('input[type="radio"]')) state.responses[event.target.name] = event.target.value;
    });
    $("#load-demo").addEventListener("click", async () => {
      try {
        const demo = await api("/demo-profile");
        state.responses = demo.responses;
        renderSteps();
        toast("Fictional demo loaded. No real profile data.");
      } catch (error) { showError(error.message); }
    });
    $("#submit-assessment").addEventListener("click", async (event) => {
      const button = event.currentTarget;
      button.disabled = true; button.textContent = "Scoring locally…";
      try {
        const result = await api("/assessment", { method: "POST", body: JSON.stringify({ responses: state.responses }) });
        renderAssessmentResult(result);
        loadDashboard();
      } catch (error) { showError(error.message); }
      finally { button.disabled = false; button.innerHTML = 'Generate my readout <span aria-hidden="true">↗</span>'; }
    });
    $("#run-simulation").addEventListener("click", async () => {
      const changes = $$("#improvement-options input:checked").map((input) => input.value);
      if (!changes.length) { toast("Choose at least one improvement to simulate."); return; }
      const button = $("#run-simulation"); button.disabled = true;
      try {
        const result = await api("/assessment/simulate-improvement", {
          method: "POST", body: JSON.stringify({ responses: state.responses, changes }),
        });
        renderSimulation(result);
      } catch (error) { showError(error.message); }
      finally { button.disabled = false; }
    });
    $("#delete-assessment").addEventListener("click", async () => {
      const current = state.assessment;
      if (!current?.assessment_id) return;
      try {
        await api(`/assessment/${encodeURIComponent(current.assessment_id)}`, { method: "DELETE" });
        state.assessment = null;
        $("#results").hidden = true;
        $("#assessment").hidden = false;
        $("#assessment").scrollIntoView({ behavior: "smooth" });
        await loadDashboard();
        toast("Saved derived assessment deleted.");
      } catch (error) { showError(error.message); }
    });
  }

  function setupChecklistDownload() {
    const link = $("#checklist-download");
    link.addEventListener("click", async (event) => {
      event.preventDefault();
      try {
        const data = await api("/privacy-checklist");
        const text = ["SOCIAL MEDIA PRIVACY CHECKLIST", "", ...(data.checklist || []).map((item) => `□ ${item.text}`), "", "Educational reminder: review settings directly with the platform."] .join("\n");
        const objectURL = URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" }));
        const download = document.createElement("a");
        download.href = objectURL; download.download = "social-media-privacy-checklist.txt";
        document.body.appendChild(download); download.click(); download.remove();
        setTimeout(() => URL.revokeObjectURL(objectURL), 1000);
        toast("Checklist downloaded.");
      } catch (error) { showError(error.message); }
    });
  }

  async function init() {
    setupReveal();
    setupSignalCanvas();
    setupAssessmentControls();
    setupChecklistDownload();
    try { await loadQuestionnaire(); }
    catch (error) { showError(`Questionnaire failed to load: ${error.message}`); }
    await loadDashboard();
  }

  document.addEventListener("DOMContentLoaded", init, { once: true });
})();
