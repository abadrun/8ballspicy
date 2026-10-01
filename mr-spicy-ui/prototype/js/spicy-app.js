/* ================================================================
   MR. SPICY — Overlay application logic (spicy-app.js)
   State model: overlay ∈ {closed, minimized, expanded};
   screen ∈ {home, tools, settings, account, about}; language ∈ {en, ar}.
   UI strings come exclusively from SpicyI18n. No network requests,
   no storage: state lives in memory for the session.
   ================================================================ */
"use strict";

(() => {
  const DEFAULTS = {
    lang: "en",
    overlay: "closed",
    screen: "home",
    opacity: 95,          // %
    textSize: 100,        // %
    pureBlack: false,
    reduceMotion: false,
    reduceTransparency: false,
    frameMeter: true,
    cpu: 18,
    logLevel: "info",
    user: null
  };

  const state = { ...DEFAULTS, device: "regular" };

  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const el = {
    html: document.documentElement,
    overlay: $("#overlay"),
    fab: $("#fab"),
    pill: $("#pill"),
    panel: $("#panel"),
    panelContent: $("#panel-content"),
    circles: $$(".circle"),
    sections: $$(".section"),
    screen: $("#screen"),
    device: $(".device"),
    toast: $("#toast"),
    log: $("#log"),
    cpuFill: $("#cpu-fill"),
    cpuValue: $("#cpu-value"),
    accountName: $("#account-name"),
    accountStatus: $("#account-status"),
    accountChip: $("#account-chip"),
    btnSignIn: $("#btn-signin"),
    btnSignOut: $("#btn-signout"),
    settingsLangValue: $("#settings-lang-value"),
    quickLang: $("#btn-quick-lang"),
    rgOpacity: $("#rg-opacity"),
    outOpacity: $("#out-opacity"),
    rgTextSize: $("#rg-textsize"),
    outTextSize: $("#out-textsize")
  };

  const t = (key) => SpicyI18n.t(key, state.lang);

  /* ---------------- localization ---------------- */

  function applyI18n() {
    el.html.lang = state.lang;
    el.html.dir = SpicyI18n.dir(state.lang);
    $$("[data-i18n]").forEach((node) => {
      node.textContent = t(node.dataset.i18n);
    });
    $$("[data-i18n-aria]").forEach((node) => {
      node.setAttribute("aria-label", t(node.dataset.i18nAria));
    });
    $$("[data-i18n-ph]").forEach((node) => {
      node.setAttribute("placeholder", t(node.dataset.i18nPh));
    });
    renderDynamic();
  }

  /* Values that depend on runtime state (not plain static strings) */
  function renderDynamic() {
    // Feature circles: active section marker
    el.circles.forEach((c) => {
      if (c.dataset.nav === "language") return; // action button, never "current"
      if (c.dataset.nav === state.screen) c.setAttribute("aria-current", "true");
      else c.removeAttribute("aria-current");
    });

    // Settings / quick actions
    el.settingsLangValue.textContent = t("settings.languageValue");
    el.quickLang.textContent = t("home.goLangLabel");

    // Toolbar radios
    $$("[data-lang]").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.lang === state.lang)));
    $$("[data-device]").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.device === state.device)));

    // Sliders
    el.outOpacity.textContent = `${state.opacity}%`;
    el.outTextSize.textContent = `${state.textSize}%`;

    // Account
    if (state.user) {
      el.accountName.textContent = state.user.name;
      el.accountStatus.textContent = t("account.signedInAs").replace("{name}", state.user.name);
      el.btnSignIn.hidden = true;
      el.btnSignOut.hidden = false;
    } else {
      el.accountName.textContent = t("account.guest");
      el.accountStatus.textContent = t("account.signedOut");
      el.btnSignIn.hidden = false;
      el.btnSignOut.hidden = true;
    }

    renderLog();
    renderCpu();
    renderLangModalSelection();
  }

  function renderLog() {
    const lines = t(`logs.${state.logLevel}`);
    el.log.innerHTML = "";
    lines.forEach((line) => {
      const div = document.createElement("div");
      const isErr = line.startsWith("[error]");
      const isOk = line.startsWith("[ok]");
      if (isErr) div.className = "t-err";
      if (isOk) div.className = "t-ok";
      const tag = line.slice(0, line.indexOf("]") + 1);
      const rest = line.slice(line.indexOf("]") + 1);
      const tagSpan = document.createElement("span");
      tagSpan.className = "lvl";
      tagSpan.textContent = tag;
      div.appendChild(tagSpan);
      div.appendChild(document.createTextNode(rest));
      el.log.appendChild(div);
    });
  }

  function renderCpu() {
    el.cpuFill.style.width = `${state.cpu}%`;
    el.cpuValue.textContent = `${state.cpu}%`;
  }

  function renderLangModalSelection() {
    $$("#scrim-language [data-choose-lang]").forEach((b) => {
      const selected = b.dataset.chooseLang === state.lang;
      b.classList.toggle("selected", selected);
      b.setAttribute("aria-pressed", String(selected));
    });
  }

  /* ---------------- overlay state machine ---------------- */

  function setOverlay(next) {
    const prev = state.overlay;
    state.overlay = next;
    el.overlay.dataset.state = next;
    // Focus management
    if (next === "expanded") {
      const first = $(".circle[aria-current='true']") || $(".circle");
      if (prev === "closed") first.focus({ preventScroll: true });
    } else if (next === "closed" && prev !== "closed") {
      el.fab.focus({ preventScroll: true });
    } else if (next === "minimized") {
      el.pill.focus({ preventScroll: true });
    }
  }

  function navigate(screen, focusTarget = true) {
    state.screen = screen;
    el.sections.forEach((s) => { s.hidden = s.dataset.screen !== screen; });
    el.panelContent.scrollTop = 0;
    renderDynamic();
    if (focusTarget) {
      const active = $(`.section[data-screen="${screen}"]`);
      if (active) {
        active.setAttribute("tabindex", "-1");
        active.focus({ preventScroll: true });
      }
    }
  }

  /* ---------------- modals ---------------- */

  let activeScrim = null;
  let lastFocused = null;

  function openModal(id) {
    if (activeScrim) closeModal();
    const scrim = $(`#${id}`);
    lastFocused = document.activeElement;
    scrim.hidden = false;
    activeScrim = scrim;
    const first = scrim.querySelector("input, button:not(.modal-close)") || scrim.querySelector("button");
    if (first) first.focus({ preventScroll: true });
  }

  function closeModal() {
    if (!activeScrim) return;
    activeScrim.hidden = true;
    activeScrim = null;
    if (lastFocused && lastFocused.focus) lastFocused.focus({ preventScroll: true });
    lastFocused = null;
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (activeScrim) { closeModal(); return; }
      if (state.overlay === "expanded") { setOverlay("closed"); return; }
    }
    if (e.key === "Tab" && activeScrim) {
      // Focus trap
      const focusables = Array.from(activeScrim.querySelectorAll(
        "button, input, select, [tabindex]:not([tabindex='-1'])"
      )).filter((n) => !n.disabled && n.offsetParent !== null);
      if (!focusables.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  /* ---------------- toast ---------------- */

  let toastTimer = null;
  function showToast(messageKey) {
    el.toast.textContent = t(messageKey);
    el.toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.toast.hidden = true; }, 2200);
  }

  /* ---------------- settings application ---------------- */

  function applyAppearance() {
    el.html.classList.toggle("pure-black", state.pureBlack);
    el.html.classList.toggle("reduce-motion", state.reduceMotion);
    el.html.classList.toggle("reduce-transparency", state.reduceTransparency);
    el.html.style.setProperty("--text-scale", String(state.textSize / 100));
    const alpha = state.reduceTransparency ? 1 : state.opacity / 100;
    el.panel.style.setProperty("--panel-alpha", String(alpha));
    el.rgOpacity.value = String(state.opacity);
    el.rgTextSize.value = String(state.textSize);
    $("#sw-black").setAttribute("aria-checked", String(state.pureBlack));
    $("#sw-motion").setAttribute("aria-checked", String(state.reduceMotion));
    $("#sw-transparency").setAttribute("aria-checked", String(state.reduceTransparency));
    $("#sw-frame").setAttribute("aria-checked", String(state.frameMeter));
  }

  function setSwitch(id, value, cb) {
    $(`#${id}`).setAttribute("aria-checked", String(value));
    if (cb) cb(value);
  }

  /* ---------------- tools simulation ---------------- */

  let cpuTimer = null;
  function syncCpuTimer() {
    const shouldRun = state.frameMeter && state.screen === "tools" && state.overlay === "expanded";
    if (shouldRun && !cpuTimer) {
      cpuTimer = setInterval(() => {
        const drift = (Math.random() * 14) - 7;
        state.cpu = Math.max(8, Math.min(46, Math.round(state.cpu + drift)));
        renderCpu();
      }, 900);
    } else if (!shouldRun && cpuTimer) {
      clearInterval(cpuTimer);
      cpuTimer = null;
    }
  }

  /* ---------------- language & device ---------------- */

  function setLang(lang) {
    state.lang = lang;
    applyI18n();
  }

  function setDevice(device) {
    state.device = device;
    el.device.dataset.device = device;
    renderDynamic();
  }

  /* ---------------- reset ---------------- */

  function resetSettings() {
    const keep = { device: state.device, overlay: state.overlay, screen: state.screen };
    Object.assign(state, DEFAULTS, keep);
    applyAppearance();
    applyI18n();
    syncCpuTimer();
    showToast("toast.reset");
  }

  /* ---------------- event wiring ---------------- */

  function wire() {
    // Overlay states
    el.fab.addEventListener("click", () => setOverlay("expanded"));
    el.pill.addEventListener("click", () => setOverlay("expanded"));
    $("#btn-minimize").addEventListener("click", () => setOverlay("minimized"));
    $("#btn-close").addEventListener("click", () => setOverlay("closed"));
    $("#btn-header-settings").addEventListener("click", () => { navigate("settings"); syncCpuTimer(); });

    // Circles
    el.circles.forEach((c) => {
      c.addEventListener("click", () => {
        const target = c.dataset.nav;
        if (target === "language") { openModal("scrim-language"); return; }
        navigate(target);
        syncCpuTimer();
      });
    });

    // Generic action buttons
    $$("[data-action]").forEach((b) => {
      b.addEventListener("click", () => {
        if (b.dataset.action === "go-settings") navigate("settings");
        if (b.dataset.action === "go-about") navigate("about");
        if (b.dataset.action === "toggle-lang") setLang(state.lang === "en" ? "ar" : "en");
      });
    });

    // Toolbar
    $$("[data-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));
    $$("[data-device]").forEach((b) => b.addEventListener("click", () => setDevice(b.dataset.device)));

    // Switches
    $("#sw-frame").addEventListener("click", () => {
      state.frameMeter = !state.frameMeter;
      setSwitch("sw-frame", state.frameMeter);
      syncCpuTimer();
    });
    $("#sw-black").addEventListener("click", () => {
      state.pureBlack = !state.pureBlack;
      applyAppearance();
    });
    $("#sw-motion").addEventListener("click", () => {
      state.reduceMotion = !state.reduceMotion;
      applyAppearance();
    });
    $("#sw-transparency").addEventListener("click", () => {
      state.reduceTransparency = !state.reduceTransparency;
      applyAppearance();
    });

    // Sliders
    el.rgOpacity.addEventListener("input", () => {
      state.opacity = Number(el.rgOpacity.value);
      el.outOpacity.textContent = `${state.opacity}%`;
      el.panel.style.setProperty("--panel-alpha", String(state.reduceTransparency ? 1 : state.opacity / 100));
    });
    el.rgTextSize.addEventListener("input", () => {
      state.textSize = Number(el.rgTextSize.value);
      el.outTextSize.textContent = `${state.textSize}%`;
      el.html.style.setProperty("--text-scale", String(state.textSize / 100));
    });

    // Log level segmented control
    $$("[data-loglevel]").forEach((b) => {
      b.addEventListener("click", () => {
        state.logLevel = b.dataset.loglevel;
        $$("[data-loglevel]").forEach((x) => x.setAttribute("aria-checked", String(x === b)));
        renderLog();
      });
    });

    // Language modal
    $$("#scrim-language [data-choose-lang]").forEach((b) => {
      b.addEventListener("click", () => { setLang(b.dataset.chooseLang); closeModal(); });
    });
    $("#row-language").addEventListener("click", () => openModal("scrim-language"));

    // Sign-in modal
    $("#btn-signin").addEventListener("click", () => {
      const input = $("#signin-name");
      input.value = state.user ? state.user.name : "";
      openModal("scrim-signin");
    });
    $("#btn-do-signin").addEventListener("click", () => {
      const name = $("#signin-name").value.trim() || "spicy.guest";
      state.user = { name };
      closeModal();
      renderDynamic();
      showToast("toast.signedIn");
    });
    $("#signin-name").addEventListener("keydown", (e) => {
      if (e.key === "Enter") $("#btn-do-signin").click();
    });
    el.btnSignOut.addEventListener("click", () => {
      state.user = null;
      renderDynamic();
      showToast("toast.signedOut");
    });

    // Reset modal
    $("#row-reset").addEventListener("click", () => openModal("scrim-reset"));
    $("#btn-do-reset").addEventListener("click", () => {
      resetSettings();
      closeModal();
    });

    // Generic modal close buttons + scrim click
    $$("[data-close]").forEach((b) => b.addEventListener("click", closeModal));
    $$(".scrim").forEach((scrim) => {
      scrim.addEventListener("pointerdown", (e) => { if (e.target === scrim) closeModal(); });
    });
  }

  /* ---------------- init ---------------- */

  function init() {
    wire();
    applyAppearance();
    applyI18n();
    navigate("home", false);
    setOverlay("closed");
  }

  // Robust boot: DOMContentLoaded may already have fired (e.g. dynamic script
  // injection). init must run exactly once — no idempotency is assumed.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
