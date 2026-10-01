import SwiftUI

// ================================================================
// MR. SPICY — Settings section (SpicySettingsView.swift)
// Appearance / Motion / General groups. Every control drives a real
// preference consumed by the overlay (opacity, text size, surfaces,
// motion, language). Nothing here enables gameplay behavior.
// ================================================================

struct SpicySettingsView: View {

    let language: SpicyLanguage

    @Binding var panelOpacity: Double      // 0.6...1.0
    @Binding var textScale: Double         // 0.9...1.15
    @Binding var pureBlack: Bool
    @Binding var reduceMotionOverride: Bool
    @Binding var reduceTransparency: Bool

    let onOpenLanguage: () -> Void
    let onOpenAbout: () -> Void
    let onReset: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            VStack(alignment: .leading, spacing: 4) {
                Text(localized("settings.title", language)).font(SpicyTheme.Typography.title)
                Text(localized("settings.subtitle", language))
                    .font(SpicyTheme.Typography.sub)
                    .foregroundColor(SpicyTheme.Ink.secondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            group(localized("settings.appearance", language)) {
                SpicySliderRow(title: localized("settings.opacity", language),
                               value: $panelOpacity,
                               range: 0.6...1.0, step: 0.05) { "\(Int((panelOpacity * 100).rounded()))%" }
                SpicyRowDivider()
                SpicySliderRow(title: localized("settings.textSize", language),
                               value: $textScale,
                               range: 0.9...1.15, step: 0.05) { "\(Int((textScale * 100).rounded()))%" }
                SpicyRowDivider()
                SpicyToggleRow(title: localized("settings.pureBlack", language),
                               subtitle: localized("settings.pureBlackDesc", language),
                               isOn: $pureBlack)
            }

            group(localized("settings.motion", language)) {
                SpicyToggleRow(title: localized("settings.reduceMotion", language),
                               subtitle: localized("settings.reduceMotionDesc", language),
                               isOn: $reduceMotionOverride)
                SpicyRowDivider()
                SpicyToggleRow(title: localized("settings.reduceTransparency", language),
                               subtitle: localized("settings.reduceTransparencyDesc", language),
                               isOn: $reduceTransparency)
            }

            group(localized("settings.general", language)) {
                SpicyNavigationRow(title: localized("settings.languageRow", language),
                                   value: language.label,
                                   action: onOpenLanguage)
                SpicyRowDivider()
                SpicyNavigationRow(title: localized("settings.aboutRow", language),
                                   action: onOpenAbout)
                SpicyRowDivider()
                SpicyNavigationRow(title: localized("settings.reset", language),
                                   destructive: true,
                                   action: onReset)
            }
        }
    }

    private func group<Content: View>(_ label: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(spacing: SpicyTheme.Spacing.x2) {
            SpicyGroupLabel(text: label)
            SpicyGroup(content: content)
        }
        .padding(.top, SpicyTheme.Spacing.x4)
    }
}
