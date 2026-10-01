import { JSDOM } from "jsdom";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

// prototype/ lives next to validation/
const root = join(dirname(fileURLToPath(import.meta.url)), "..", "prototype");
const html = readFileSync(`${root}/index.html`, "utf-8");

const errors = [];
const vc = new (class extends (await import("jsdom")).VirtualConsole {
})(/* suppress noise */);
const { VirtualConsole } = await import("jsdom");
const vconsole = new VirtualConsole();
vconsole.on("jsdomError", (e) => errors.push("jsdomError: " + e.message));
vconsole.on("error", (...a) => errors.push("console.error: " + a.join(" ")));

const dom = new JSDOM(html, {
  url: "http://localhost/index.html",
  runScripts: "outside-only",
  pretendToBeVisual: true,
  virtualConsole: vconsole,
});
const { window } = dom;
// load i18n + app scripts manually
const i18nSrc = readFileSync(`${root}/js/spicy-i18n.js`, "utf-8");
const appSrc  = readFileSync(`${root}/js/spicy-app.js`, "utf-8");
window.eval(i18nSrc + "\n;\n" + appSrc);
// wait for jsdom's REAL DOMContentLoaded (init runs exactly once)
if (window.document.readyState === "loading") {
  await new Promise(r => window.document.addEventListener("DOMContentLoaded", r, { once: true }));
}
await new Promise(r => setTimeout(r, 30));

const $ = (s) => window.document.querySelector(s);
const $$ = (s) => [...window.document.querySelectorAll(s)];
const results = [];
const check = (name, cond) => results.push([cond ? "PASS" : "FAIL", name]);
const click = (el) => el.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));

await new Promise(r => setTimeout(r, 50));

// 1. Boot state
check("boots without JS errors", errors.length === 0);
check("overlay starts closed", $("#overlay").dataset.state === "closed");
check("default lang/dir = en/ltr", window.document.documentElement.lang === "en" && window.document.documentElement.dir === "ltr");
check("i18n applied to static node", $("[data-i18n='app.subtitle']").textContent === "Control Panel");
check("home section visible, others hidden", !$(".section[data-screen='home']").hidden && $$(".section[hidden]").length === 4);

// 2. Overlay state machine
click($("#fab"));
check("fab → expanded", $("#overlay").dataset.state === "expanded");
check("panel in a11y tree & circles focusable", $$(".circle").length === 6);
click($("#btn-minimize"));
check("minimize → minimized", $("#overlay").dataset.state === "minimized");
click($("#pill"));
check("pill → expanded", $("#overlay").dataset.state === "expanded");
click($("#btn-close"));
check("close → closed", $("#overlay").dataset.state === "closed");
click($("#fab"));

// 3. Section navigation
click($("[data-nav='tools']"));
check("tools circle navigates", !$(".section[data-screen='tools']").hidden);
check("aria-current moves to tools", $("[data-nav='tools']").getAttribute("aria-current") === "true");
check("home hidden after nav", $(".section[data-screen='home']").hidden);
click($("[data-nav='settings']"));
check("settings circle navigates", !$(".section[data-screen='settings']").hidden);

// 4. Settings interactions
const swBlack = $("#sw-black");
click(swBlack);
check("pure-black switch toggles aria", swBlack.getAttribute("aria-checked") === "true");
check("pure-black class applied", window.document.documentElement.classList.contains("pure-black"));
const rg = $("#rg-opacity");
rg.value = "75";
rg.dispatchEvent(new window.Event("input", { bubbles: true }));
check("opacity slider updates output", $("#out-opacity").textContent === "75%");
const swMotion = $("#sw-motion");
click(swMotion);
check("reduce-motion switch toggles", swMotion.getAttribute("aria-checked") === "true" && window.document.documentElement.classList.contains("reduce-motion"));

// 5. Modals
click($("#row-language"));
check("language modal opens", !$("#scrim-language").hidden);
click($("[data-choose-lang='ar']"));
check("choose AR closes modal", $("#scrim-language").hidden);
check("lang/dir switch to ar/rtl", window.document.documentElement.lang === "ar" && window.document.documentElement.dir === "rtl");
check("AR strings applied", $("[data-i18n='app.subtitle']").textContent === "لوحة التحكم");
check("AR circle label applied", $("[data-nav='home'] .circle-label").textContent === "الرئيسية");
check("settings language value = العربية", $("#settings-lang-value").textContent === "العربية");

// sign-in flow
click($("[data-nav='account']"));
click($("#btn-signin"));
check("sign-in modal opens", !$("#scrim-signin").hidden);
$("#signin-name").value = "tester";
click($("#btn-do-signin"));
check("sign-in closes modal", $("#scrim-signin").hidden);
check("account name updates", $("#account-name").textContent === "tester");
check("status shows signed-in (AR)", $("#account-status").textContent.includes("tester"));
check("sign-out button visible", !$("#btn-signout").hidden);
click($("#btn-signout"));
check("sign-out restores guest (AR)", $("#account-name").textContent === "زائر");

// 6. Reset flow
click($("#row-reset"));
check("reset modal opens", !$("#scrim-reset").hidden);
click($("#btn-do-reset"));
check("reset restores EN/LTR", window.document.documentElement.lang === "en" && window.document.documentElement.dir === "ltr");
check("reset clears pure-black", !window.document.documentElement.classList.contains("pure-black"));
check("reset restores opacity default", $("#out-opacity").textContent === "95%");
check("reset shows toast", !$("#toast").hidden);

// 7. Tools logic
click($("[data-nav='tools']"));
click($("[data-loglevel='debug']"));
check("log level switch renders debug lines", $("#log").textContent.includes("[debug]"));
click($("[data-loglevel='error']"));
check("log level switch renders error lines", $("#log").textContent.includes("[error]"));
const swFrame = $("#sw-frame");
click(swFrame);
check("frame meter switch toggles off", swFrame.getAttribute("aria-checked") === "false");

// 8. Escape key behavior
click($("#btn-header-settings"));
window.document.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
check("Escape collapses expanded panel", $("#overlay").dataset.state === "closed");

// 9. Accessibility invariants
check("all switches have role=switch", $$(".switch").every(s => s.getAttribute("role") === "switch"));
check("all circles have aria-labels", $$(".circle").every(c => (c.getAttribute("aria-label") || "").length > 0));
check("modals are aria-modal dialogs", $$(".modal").every(m => m.getAttribute("role") === "dialog" && m.getAttribute("aria-modal") === "true"));
check("log has aria-live", $("#log").getAttribute("aria-live") === "polite");
check("panel is a labeled dialog", $("#panel").getAttribute("role") === "dialog" && !!$("#panel").getAttribute("aria-label"));

await new Promise(r => setTimeout(r, 100));
check("no JS errors during entire run", errors.length === 0);
if (errors.length) console.log("ERRORS:", errors.slice(0, 5));

const fails = results.filter(r => r[0] === "FAIL");
for (const [s, n] of results) console.log(`${s === "PASS" ? "✓" : "✗ FAIL"}  ${n}`);
console.log(`\n${results.length - fails.length}/${results.length} checks passed`);
process.exit(fails.length ? 1 : 0);
