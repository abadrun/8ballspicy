#if canImport(SwiftUI)
import SwiftUI
import ExistingIPAOverlayCore

struct OverviewScreen: View {
    let select: (OverlaySection) -> Void
    let t: (String) -> String
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            screenTitle(t("section.overview"), t("overview.subtitle"))
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                FeatureTile(symbol: "paintbrush", title: t("section.appearance"), detail: t("appearance.subtitle"), selected: false) { select(.appearance) }
                FeatureTile(symbol: "switch.2", title: t("section.preferences"), detail: t("preferences.subtitle"), selected: false) { select(.preferences) }
                FeatureTile(symbol: "globe", title: t("section.language"), detail: t("language.subtitle"), selected: false) { select(.language) }
                FeatureTile(symbol: "info.circle", title: t("section.about"), detail: t("about.subtitle"), selected: false) { select(.about) }
            }
            ModuleCard(title: t("overview.scope")) {
                Label(t("overview.local_only"), systemImage: "iphone")
                Label(t("overview.no_network"), systemImage: "network.slash")
                Label(t("overview.no_gating"), systemImage: "lock.open")
            }
            .font(.subheadline)
        }
    }
}

struct AppearanceScreen: View {
    @Binding var settings: OverlaySettings
    let t: (String) -> String
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            screenTitle(t("section.appearance"), t("appearance.subtitle"))
            ModuleCard(title: t("appearance.layout")) {
                SegmentedRow(title: t("appearance.size"), options: [
                    (.compact, t("size.compact")), (.comfortable, t("size.comfortable")), (.large, t("size.large"))
                ], selection: $settings.size)
                MeterRow(title: t("appearance.opacity"), formattedValue: "\(Int(settings.panelOpacity * 100))%",
                         range: 0.70...1.0, value: $settings.panelOpacity)
                MeterRow(title: t("appearance.scale"), formattedValue: String(format: "%.0f%%", settings.interfaceScale * 100),
                         range: 0.85...1.20, value: $settings.interfaceScale)
            }
        }
    }
}

struct PreferencesScreen: View {
    @Binding var settings: OverlaySettings
    let t: (String) -> String
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            screenTitle(t("section.preferences"), t("preferences.subtitle"))
            ModuleCard(title: t("preferences.interface")) {
                ToggleRow(symbol: "checkmark.circle", title: t("preferences.status"), detail: t("preferences.status.detail"), value: $settings.showStatusBadge)
                Divider().overlay(OverlayTheme.border)
                ToggleRow(symbol: "waveform", title: t("preferences.haptics"), detail: t("preferences.haptics.detail"), value: $settings.hapticsEnabled)
                Divider().overlay(OverlayTheme.border)
                ToggleRow(symbol: "figure.walk.motion", title: t("preferences.reduce_motion"), detail: t("preferences.reduce_motion.detail"), value: $settings.reduceMotion)
                Divider().overlay(OverlayTheme.border)
                ToggleRow(symbol: "mappin.and.ellipse", title: t("preferences.position"), detail: t("preferences.position.detail"), value: $settings.rememberPosition)
            }
        }
    }
}

struct LanguageScreen: View {
    @Binding var settings: OverlaySettings
    let t: (String) -> String
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            screenTitle(t("section.language"), t("language.subtitle"))
            ModuleCard(title: t("language.choose")) {
                SegmentedRow(title: t("section.language"), options: [
                    (.english, "English"), (.indonesian, "Bahasa Indonesia")
                ], selection: $settings.language)
                Text(t("language.note")).font(.caption).foregroundStyle(OverlayTheme.muted)
            }
        }
    }
}

struct AboutScreen: View {
    let reset: () -> Void
    let t: (String) -> String
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            screenTitle(t("section.about"), t("about.subtitle"))
            ModuleCard(title: t("about.details")) {
                KeyValueRow(key: t("about.version"), value: "1.0.0")
                KeyValueRow(key: t("about.implementation"), value: t("about.source_level"))
                KeyValueRow(key: t("about.network"), value: t("about.none"))
            }
            ModuleCard(title: t("about.reset")) {
                Text(t("about.reset.detail")).font(.subheadline).foregroundStyle(OverlayTheme.muted)
                Button(role: .destructive, action: reset) { Label(t("about.reset.button"), systemImage: "arrow.counterclockwise") }
                    .buttonStyle(.bordered)
            }
        }
    }
}

@ViewBuilder private func screenTitle(_ title: String, _ subtitle: String) -> some View {
    VStack(alignment: .leading, spacing: 4) {
        Text(title).font(.title2.weight(.bold))
        Text(subtitle).font(.subheadline).foregroundStyle(OverlayTheme.muted)
    }
}
#endif
