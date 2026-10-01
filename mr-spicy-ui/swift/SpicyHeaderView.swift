import SwiftUI

// ================================================================
// MR. SPICY — Panel header (SpicyHeaderView.swift)
// Logo mark, wordmark, subtitle and trailing controls. The HStack
// mirrors automatically for RTL; 44 pt targets; VoiceOver labels
// on every control.
// ================================================================

struct SpicyHeaderView: View {
    let subtitle: String
    let onSettings: () -> Void
    let onMinimize: () -> Void
    let onClose: () -> Void

    /// Derived circular asset generated from the supplied logo.png
    /// (see mr-spicy-ui/prototype/assets/logo-circle-*.png). Add it to
    /// the app's asset catalog as "SpicyLogo".
    private var logo: some View {
        Image("SpicyLogo")
            .resizable()
            .aspectRatio(contentMode: .fit)
            .frame(width: 34, height: 34)
            .clipShape(Circle())
            .overlay(Circle().stroke(SpicyTheme.Accent.soft, lineWidth: 3))
            .accessibilityHidden(true)
    }

    var body: some View {
        HStack(spacing: SpicyTheme.Spacing.x3) {
            logo

            VStack(alignment: .leading, spacing: 2) {
                Text("MR. SPICY")
                    .font(SpicyTheme.Typography.display)
                    .tracking(1.2)
                    .foregroundColor(SpicyTheme.Ink.primary)
                Text(subtitle)
                    .font(SpicyTheme.Typography.caption)
                    .foregroundColor(SpicyTheme.Ink.tertiary)
            }
            Spacer(minLength: SpicyTheme.Spacing.x2)

            HStack(spacing: 2) {
                headerIcon(systemImage: "gearshape", label: "Open settings", action: onSettings)
                headerIcon(systemImage: "chevron.down", label: "Minimize panel", action: onMinimize)
                headerIcon(systemImage: "xmark", label: "Close panel", action: onClose)
            }
        }
        .padding(.horizontal, SpicyTheme.Spacing.x4)
        .padding(.vertical, SpicyTheme.Spacing.x3)
        .overlay(alignment: .bottom) { SpicyRowDivider() }
    }

    private func headerIcon(systemImage: String, label: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: systemImage)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(SpicyTheme.Ink.secondary)
                .frame(width: SpicyTheme.Metrics.minTouchTarget,
                       height: SpicyTheme.Metrics.minTouchTarget)
                .contentShape(Rectangle())
        }
        .buttonStyle(SpicyPressableStyle())
        .accessibilityLabel(label)
    }
}
