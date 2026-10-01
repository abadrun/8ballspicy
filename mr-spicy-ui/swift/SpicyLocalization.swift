import SwiftUI

// ================================================================
// MR. SPICY — Localization (SpicyLocalization.swift)
// English + Arabic string tables mirroring spicy-i18n.js, plus
// layout-direction support. In a production app these would live in
// String Catalogs / Localizable.strings; the dictionary keeps this
// reference self-contained and dependency-free.
// ================================================================

enum SpicyLanguage: String, CaseIterable, Identifiable {
    case english = "en"
    case arabic  = "ar"

    var id: String { rawValue }

    var label: String {
        switch self {
        case .english: return "English"
        case .arabic:  return "العربية"
        }
    }

    var directionLabel: String {
        switch self {
        case .english: return localized("modal.ltr")
        case .arabic:  return localized("modal.rtl")
        }
    }

    var layoutDirection: LayoutDirection {
        self == .arabic ? .rightToLeft : .leftToRight
    }
}

enum SpicyLocalization {

    private static let tables: [SpicyLanguage: [String: String]] = [
        .english: [
            "app.subtitle": "Control Panel",

            "nav.home": "Home",
            "nav.tools": "Tools",
            "nav.settings": "Settings",
            "nav.language": "Language",
            "nav.account": "Account",
            "nav.about": "About",

            "a11y.open": "Open MR. SPICY panel",
            "a11y.expand": "Expand panel",
            "a11y.minimize": "Minimize panel",
            "a11y.close": "Close panel",
            "a11y.openSettings": "Open settings",
            "a11y.sections": "Panel sections",

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
            "account.signedInAs": "Signed in as %@ (local)",
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
            "modal.signinSub": "Local demo — the name is stored in this device only and nothing is transmitted.",
            "modal.nameLabel": "Display name",
            "modal.cancel": "Cancel",
            "modal.signinCta": "Sign in",
            "modal.resetTitle": "Reset settings?",
            "modal.resetBody": "Appearance, motion and language return to their defaults.",
            "modal.resetCta": "Reset",

            "toast.signedIn": "Signed in locally",
            "toast.signedOut": "Signed out",
            "toast.reset": "Settings restored to defaults"
        ],

        .arabic: [
            "app.subtitle": "لوحة التحكم",

            "nav.home": "الرئيسية",
            "nav.tools": "الأدوات",
            "nav.settings": "الإعدادات",
            "nav.language": "اللغة",
            "nav.account": "الحساب",
            "nav.about": "حول",

            "a11y.open": "فتح لوحة مستر سبايسي",
            "a11y.expand": "توسيع اللوحة",
            "a11y.minimize": "تصغير اللوحة",
            "a11y.close": "إغلاق اللوحة",
            "a11y.openSettings": "فتح الإعدادات",
            "a11y.sections": "أقسام اللوحة",

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
            "account.signedInAs": "مسجّل الدخول باسم %@ (محليًا)",
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
            "modal.signinSub": "تجريبي محلي — يُحفظ الاسم على هذا الجهاز فقط ولا يُرسَل أي شيء.",
            "modal.nameLabel": "الاسم المعروض",
            "modal.cancel": "إلغاء",
            "modal.signinCta": "تسجيل الدخول",
            "modal.resetTitle": "إعادة تعيين الإعدادات؟",
            "modal.resetBody": "سيعود المظهر والحركة واللغة إلى وضعها الافتراضي.",
            "modal.resetCta": "إعادة تعيين",

            "toast.signedIn": "تم تسجيل الدخول محليًا",
            "toast.signedOut": "تم تسجيل الخروج",
            "toast.reset": "تمت استعادة الإعدادات الافتراضية"
        ]
    ]

    /// Resolve `key` for `language`, falling back to English, then the key.
    static func string(_ key: String, _ language: SpicyLanguage) -> String {
        tables[language]?[key] ?? tables[.english]?[key] ?? key
    }

    /// Resolve with one `%@` substitution (e.g. account.signedInAs).
    static func string(_ key: String, _ language: SpicyLanguage, _ value: String) -> String {
        let template = string(key, language)
        return template.replacingOccurrences(of: "%@", with: value)
    }
}

/// Convenience used across the views.
func localized(_ key: String, _ language: SpicyLanguage) -> String {
    SpicyLocalization.string(key, language)
}
