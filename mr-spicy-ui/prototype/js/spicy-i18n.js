/* ================================================================
   MR. SPICY — Localization (spicy-i18n.js)
   English + Arabic string tables. Keys are namespaced; the UI reads
   strings only through these tables (no hard-coded UI strings in JS).
   `home.goLangLabel` shows the *target* language name, so each table
   stores the other language's name.
   ================================================================ */
"use strict";

const SpicyI18n = (() => {
  const tables = {
    en: {
      "toolbar.sub": "UI reference · interactive prototype",
      "toolbar.langAria": "Prototype language",
      "toolbar.deviceAria": "Device width",
      "toolbar.compact": "Compact",
      "toolbar.regular": "Regular",
      "toolbar.note": "Tip: the overlay supports closed → minimized → expanded states, EN/AR with RTL mirroring, and keyboard navigation (Tab / Esc).",

      "a11y.open": "Open MR. SPICY panel",
      "a11y.expand": "Expand panel",
      "a11y.panel": "MR. SPICY panel",
      "a11y.openSettings": "Open settings",
      "a11y.minimize": "Minimize panel",
      "a11y.close": "Close panel",
      "a11y.sections": "Panel sections",

      "app.subtitle": "Control Panel",

      "nav.home": "Home",
      "nav.tools": "Tools",
      "nav.settings": "Settings",
      "nav.language": "Language",
      "nav.account": "Account",
      "nav.about": "About",
      "nav.homeAria": "Go to Home",
      "nav.toolsAria": "Go to Developer tools",
      "nav.settingsAria": "Go to Settings",
      "nav.languageAria": "Change language",
      "nav.accountAria": "Go to Account",
      "nav.aboutAria": "Go to About",

      "home.badge": "Demo mode",
      "home.demoNotice": "This is a neutral UI reference. It contains no gameplay features and connects to no services.",
      "home.statsTitle": "Design system at a glance",
      "home.statTokens": "Design tokens",
      "home.statLangs": "Languages",
      "home.statComponents": "Components",
      "home.statStates": "Overlay states",
      "home.quickActions": "Quick actions",
      "home.goSettings": "Open settings",
      "home.goLangLabel": "العربية",

      "tools.title": "Developer tools",
      "tools.subtitle": "Neutral demonstration of the row components.",
      "tools.frameMeter": "Frame meter",
      "tools.frameMeterDesc": "Simulated. No real measurement is performed.",
      "tools.cpu": "CPU load (simulated)",
      "tools.logLevel": "Log level",
      "tools.build": "Build",
      "tools.renderer": "Renderer",
      "tools.logsTitle": "Log preview",
      "log.info": "Info",
      "log.debug": "Debug",
      "log.error": "Errors",

      "settings.title": "Settings",
      "settings.subtitle": "Appearance, motion and general preferences.",
      "settings.appearance": "Appearance",
      "settings.opacity": "Overlay opacity",
      "settings.textSize": "Text size",
      "settings.pureBlack": "Pure black background",
      "settings.pureBlackDesc": "AMOLED-friendly deep black.",
      "settings.motion": "Motion",
      "settings.reduceMotion": "Reduce motion",
      "settings.reduceMotionDesc": "Removes non-essential animations.",
      "settings.reduceTransparency": "Reduce transparency",
      "settings.reduceTransparencyDesc": "Uses solid surfaces and full opacity.",
      "settings.general": "General",
      "settings.languageRow": "Language",
      "settings.languageValue": "English",
      "settings.aboutRow": "About MR. SPICY",
      "settings.reset": "Reset all settings",

      "account.title": "Account",
      "account.guest": "Guest",
      "account.localProfile": "Local demo profile",
      "account.planName": "Free demo",
      "account.planTitle": "Plan",
      "account.planNote": "This reference grants no entitlements and performs no purchases or verification.",
      "account.status": "Status",
      "account.signedOut": "Not signed in",
      "account.signedInAs": "Signed in as {name} (local)",
      "account.sync": "Sync",
      "account.syncOff": "Disabled (demo)",
      "account.signIn": "Sign in (demo)",
      "account.signOut": "Sign out",

      "about.title": "About",
      "about.what": "MR. SPICY is a neutral, premium control-panel UI reference: design system, EN/AR localization, RTL and accessibility. It is a standalone demonstration intended for legitimate software such as settings, developer or accessibility panels. It is not affiliated with, endorsed by, or connected to any game, and contains no gameplay or automation functionality.",
      "about.version": "Version",
      "about.asset": "Branding asset",
      "about.repo": "Repository",
      "about.footnote": "Original branding asset preserved unmodified at the repository root.",

      "footer.caption": "Neutral UI reference — no gameplay features",

      "modal.languageTitle": "Language",
      "modal.languageSub": "Interface language and direction.",
      "modal.ltr": "Left to right",
      "modal.rtl": "Right to left",
      "modal.signinTitle": "Sign in",
      "modal.signinSub": "Local demo — the name is stored in this page only and nothing is transmitted.",
      "modal.nameLabel": "Display name",
      "modal.namePh": "e.g. spicy.guest",
      "modal.cancel": "Cancel",
      "modal.signinCta": "Sign in",
      "modal.resetTitle": "Reset settings?",
      "modal.resetBody": "Appearance, motion and language return to their defaults.",
      "modal.resetCta": "Reset",

      "toast.signedIn": "Signed in locally",
      "toast.signedOut": "Signed out",
      "toast.reset": "Settings restored to defaults",

      "logs.info": [
        "[info] panel initialized · 12 ms",
        "[info] localization loaded · en",
        "[info] state → expanded"
      ],
      "logs.debug": [
        "[debug] tokens resolved · 42",
        "[debug] layout pass · 3.1 ms",
        "[debug] focus order verified"
      ],
      "logs.error": [
        "[error] no services configured",
        "[error] sync disabled (demo)",
        "[ok] nothing to report"
      ]
    },

    ar: {
      "toolbar.sub": "مرجع واجهة · نموذج تفاعلي",
      "toolbar.langAria": "لغة النموذج",
      "toolbar.deviceAria": "عرض الجهاز",
      "toolbar.compact": "مضغوط",
      "toolbar.regular": "قياسي",
      "toolbar.note": "تلميح: تدعم اللوحة العائمة الحالات: مغلقة ← مصغّرة ← موسّعة، واللغتين الإنجليزية والعربية مع انعكاس الاتجاه، والتنقّل بلوحة المفاتيح (Tab / Esc).",

      "a11y.open": "فتح لوحة مستر سبايسي",
      "a11y.expand": "توسيع اللوحة",
      "a11y.panel": "لوحة مستر سبايسي",
      "a11y.openSettings": "فتح الإعدادات",
      "a11y.minimize": "تصغير اللوحة",
      "a11y.close": "إغلاق اللوحة",
      "a11y.sections": "أقسام اللوحة",

      "app.subtitle": "لوحة التحكم",

      "nav.home": "الرئيسية",
      "nav.tools": "الأدوات",
      "nav.settings": "الإعدادات",
      "nav.language": "اللغة",
      "nav.account": "الحساب",
      "nav.about": "حول",
      "nav.homeAria": "الانتقال إلى الرئيسية",
      "nav.toolsAria": "الانتقال إلى أدوات المطوّر",
      "nav.settingsAria": "الانتقال إلى الإعدادات",
      "nav.languageAria": "تغيير اللغة",
      "nav.accountAria": "الانتقال إلى الحساب",
      "nav.aboutAria": "الانتقال إلى حول",

      "home.badge": "وضع تجريبي",
      "home.demoNotice": "هذه واجهة مرجعية محايدة. لا تتضمن أي ميزات لعب ولا تتصل بأي خدمات.",
      "home.statsTitle": "نظرة سريعة على نظام التصميم",
      "home.statTokens": "رموز التصميم",
      "home.statLangs": "اللغات",
      "home.statComponents": "المكوّنات",
      "home.statStates": "حالات اللوحة",
      "home.quickActions": "إجراءات سريعة",
      "home.goSettings": "فتح الإعدادات",
      "home.goLangLabel": "English",

      "tools.title": "أدوات المطوّر",
      "tools.subtitle": "عرض محايد لمكوّنات الصفوف.",
      "tools.frameMeter": "عداد الإطارات",
      "tools.frameMeterDesc": "محاكاة فقط؛ لا يتم أي قياس حقيقي.",
      "tools.cpu": "حمل المعالج (محاكاة)",
      "tools.logLevel": "مستوى السجل",
      "tools.build": "الإصدار",
      "tools.renderer": "العارض",
      "tools.logsTitle": "معاينة السجل",
      "log.info": "معلومات",
      "log.debug": "تفصيلي",
      "log.error": "أخطاء",

      "settings.title": "الإعدادات",
      "settings.subtitle": "المظهر والحركة والتفضيلات العامة.",
      "settings.appearance": "المظهر",
      "settings.opacity": "عتامة اللوحة",
      "settings.textSize": "حجم النص",
      "settings.pureBlack": "خلفية سوداء تمامًا",
      "settings.pureBlackDesc": "أسود عميق يناسب شاشات AMOLED.",
      "settings.motion": "الحركة",
      "settings.reduceMotion": "تقليل الحركة",
      "settings.reduceMotionDesc": "إزالة الرسوم المتحركة غير الأساسية.",
      "settings.reduceTransparency": "تقليل الشفافية",
      "settings.reduceTransparencyDesc": "استخدام أسطح مصمتة وعتامة كاملة.",
      "settings.general": "عام",
      "settings.languageRow": "اللغة",
      "settings.languageValue": "العربية",
      "settings.aboutRow": "عن مستر سبايسي",
      "settings.reset": "إعادة تعيين كل الإعدادات",

      "account.title": "الحساب",
      "account.guest": "زائر",
      "account.localProfile": "ملف تجريبي محلي",
      "account.planName": "تجريبي مجاني",
      "account.planTitle": "الخطة",
      "account.planNote": "لا تمنح هذه الواجهة أي صلاحيات ولا تجري أي عمليات شراء أو تحقّق.",
      "account.status": "الحالة",
      "account.signedOut": "غير مسجّل الدخول",
      "account.signedInAs": "مسجّل الدخول باسم {name} (محليًا)",
      "account.sync": "المزامنة",
      "account.syncOff": "معطّلة (تجريبي)",
      "account.signIn": "تسجيل الدخول (تجريبي)",
      "account.signOut": "تسجيل الخروج",

      "about.title": "حول",
      "about.what": "مستر سبايسي واجهة مرجعية محايدة فاخرة للوحات التحكم: نظام تصميم، وترجمة بين الإنجليزية والعربية، ودعم الاتجاه من اليمين إلى اليسار، وإمكانية الوصول. وهي نموذج مستقل مخصّص للبرمجيات المشروعة مثل لوحات الإعدادات وأدوات المطوّرين ولوحات إمكانية الوصول، ولا تنتمي إلى أي لعبة أو ترتبط بها، ولا تتضمّن أي وظائف لعب أو أتمتة.",
      "about.version": "الإصدار",
      "about.asset": "أصل العلامة",
      "about.repo": "المستودع",
      "about.footnote": "الأصل الأصلي للعلامة محفوظ دون تعديل في جذر المستودع.",

      "footer.caption": "واجهة مرجعية محايدة — بلا أي ميزات لعب",

      "modal.languageTitle": "اللغة",
      "modal.languageSub": "لغة الواجهة واتجاهها.",
      "modal.ltr": "من اليسار إلى اليمين",
      "modal.rtl": "من اليمين إلى اليسار",
      "modal.signinTitle": "تسجيل الدخول",
      "modal.signinSub": "تجريبي محلي — يُحفظ الاسم في هذه الصفحة فقط ولا يُرسَل أي شيء.",
      "modal.nameLabel": "الاسم المعروض",
      "modal.namePh": "مثال: spicy.guest",
      "modal.cancel": "إلغاء",
      "modal.signinCta": "تسجيل الدخول",
      "modal.resetTitle": "إعادة تعيين الإعدادات؟",
      "modal.resetBody": "سيعود المظهر والحركة واللغة إلى وضعها الافتراضي.",
      "modal.resetCta": "إعادة تعيين",

      "toast.signedIn": "تم تسجيل الدخول محليًا",
      "toast.signedOut": "تم تسجيل الخروج",
      "toast.reset": "تمت استعادة الإعدادات الافتراضية",

      "logs.info": [
        "[info] تم تهيئة اللوحة · 12 ms",
        "[info] تم تحميل الترجمة · ar",
        "[info] الحالة ← موسّعة"
      ],
      "logs.debug": [
        "[debug] تم تحليل الرموز · 42",
        "[debug] دورة التخطيط · 3.1 ms",
        "[debug] تم التحقق من ترتيب التركيز"
      ],
      "logs.error": [
        "[error] لا توجد خدمات مهيّأة",
        "[error] المزامنة معطّلة (تجريبي)",
        "[ok] لا يوجد ما يُبلَّغ عنه"
      ]
    }
  };

  const directions = { en: "ltr", ar: "rtl" };

  return {
    languages: [
      { code: "en", label: "English", dir: "ltr" },
      { code: "ar", label: "العربية", dir: "rtl" }
    ],
    dir(lang) { return directions[lang] || "ltr"; },
    table(lang) { return tables[lang] || tables.en; },
    t(key, lang) {
      const tbl = this.table(lang);
      return Object.prototype.hasOwnProperty.call(tbl, key) ? tbl[key] : key;
    }
  };
})();
