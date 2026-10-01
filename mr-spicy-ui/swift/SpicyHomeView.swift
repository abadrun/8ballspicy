import SwiftUI

// ================================================================
// MR. SPICY — Home & Tools sections (SpicyHomeView.swift)
// Home: honest demo status + design-system overview.
// Tools: NEUTRAL developer-tool demonstration of the row components
// (toggle / meter / segmented / key-value). Everything is simulated —
// no measurement of anything occurs.
// ================================================================

struct SpicyHomeView: View {
    let language: SpicyLanguage
    let onOpenSettings: () -> Void
    let onToggleLanguage: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            // Honest demo banner
            VStack(alignment: .leading, spacing: SpicyTheme.Spacing.x2) {
                SpicyChip(text: localized("home.badge", language), kind: .accent)
                Text(localized("home.demoNotice", language))
                    .font(SpicyTheme.Typography.sub)
                    .foregroundColor(SpicyTheme.Ink.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(SpicyTheme.Spacing.x4)
            .background(SpicyTheme.Surface.elevated)
            .clipShape(RoundedRectangle(cornerRadius: SpicyTheme.Radius.large, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: SpicyTheme.Radius.large, style: .continuous)
                    .strokeBorder(SpicyTheme.Line.divider, lineWidth: 1)
            )
            .overlay(alignment: .leading) {
                // accent edge on the leading side (mirrors in RTL)
                RoundedRectangle(cornerRadius: 1.5)
                    .fill(SpicyTheme.Accent.base)
                    .frame(width: 3)
                    .padding(.vertical, SpicyTheme.Spacing.x2)
                    .accessibilityHidden(true)
            }

            sectionTitle(localized("home.statsTitle", language))
            SpicyGroup {
                SpicyKeyValueRow(title: localized("home.statTokens", language), value: "40+")
                SpicyRowDivider()
                SpicyKeyValueRow(title: localized("home.statLangs", language), value: "2 · EN / AR")
                SpicyRowDivider()
                SpicyKeyValueRow(title: localized("home.statComponents", language), value: "12")
                SpicyRowDivider()
                SpicyKeyValueRow(title: localized("home.statStates", language), value: "3")
            }

            sectionTitle(localized("home.quickActions", language))
            HStack(spacing: SpicyTheme.Spacing.x2) {
                Button(localized("home.goSettings", language), action: onOpenSettings)
                    .buttonStyle(SpicySecondaryButtonStyle())
                Button(localized("home.goLangLabel", language), action: onToggleLanguage)
                    .buttonStyle(SpicySecondaryButtonStyle())
            }
        }
    }

    private func sectionTitle(_ text: String) -> some View {
        Text(text)
            .font(SpicyTheme.Typography.title)
            .foregroundColor(SpicyTheme.Ink.primary)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.top, SpicyTheme.Spacing.x5)
            .padding(.bottom, SpicyTheme.Spacing.x2)
            .accessibilityAddTraits(.isHeader)
    }
}

// MARK: - Tools (neutral developer-tool demo)

struct SpicyToolsView: View {
    let language: SpicyLanguage
    @State private var frameMeterOn = true
    @State private var cpu: Double = 0.18
    @State private var logLevel: SpicySegment = .info
    private let timer = Timer.publish(every: 0.9, on: .main, in: .common).autoconnect()

    var body: some View {
        VStack(spacing: 0) {
            sectionHeader(localized("tools.title", language),
                          subtitle: localized("tools.subtitle", language))

            SpicyGroup {
                SpicyToggleRow(title: localized("tools.frameMeter", language),
                               subtitle: localized("tools.frameMeterDesc", language),
                               isOn: $frameMeterOn)
                SpicyRowDivider()
                SpicyMeterRow(title: localized("tools.cpu", language),
                              value: cpu,
                              valueText: "\(Int((cpu * 100).rounded()))%")
                SpicyRowDivider()
                SpicySegmentedRow(
                    title: localized("tools.logLevel", language),
                    options: [
                        (.info,  localized("log.info", language)),
                        (.debug, localized("log.debug", language)),
                        (.error, localized("log.error", language))
                    ],
                    selection: $logLevel
                )
            }

            SpicyGroupLabel(text: localized("tools.build", language)).padding(.bottom, SpicyTheme.Spacing.x2)
            SpicyGroup {
                SpicyKeyValueRow(title: localized("tools.build", language), value: "1.0.0 · demo")
                SpicyRowDivider()
                SpicyKeyValueRow(title: localized("tools.renderer", language), value: "SwiftUI")
            }

            sectionTitle(localized("tools.logsTitle", language))
            Text(logPreview)
                .font(.system(size: 11.5, design: .monospaced))
                .foregroundColor(SpicyTheme.Ink.secondary)
                .frame(maxWidth: .infinity, minHeight: 84, alignment: .topLeading)
                .padding(SpicyTheme.Spacing.x3)
                .background(Color(hex: 0x0A080C))
                .clipShape(RoundedRectangle(cornerRadius: SpicyTheme.Radius.medium, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: SpicyTheme.Radius.medium, style: .continuous)
                        .strokeBorder(SpicyTheme.Line.divider, lineWidth: 1)
                )
                .accessibilityLabel(localized("tools.logsTitle", language))
        }
        .onReceive(timer) { _ in
            guard frameMeterOn else { return }
            // Simulated drift — purely cosmetic UI demonstration.
            withAnimation(.easeOut(duration: SpicyTheme.Motion.slow)) {
                cpu = min(0.46, max(0.08, cpu + Double.random(in: -0.07...0.07)))
            }
        }
    }

    private var logPreview: String {
        let lines: [String]
        switch logLevel {
        case .info:
            lines = ["[info] panel initialized · 12 ms",
                     "[info] localization loaded · \(language.rawValue)",
                     "[info] state → expanded"]
        case .debug:
            lines = ["[debug] tokens resolved · 42",
                     "[debug] layout pass · 3.1 ms",
                     "[debug] focus order verified"]
        case .error:
            lines = ["[error] no services configured",
                     "[error] sync disabled (demo)",
                     "[ok] nothing to report"]
        }
        return lines.joined(separator: "\n")
    }

    private func sectionHeader(_ text: String, subtitle: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(text).font(SpicyTheme.Typography.title)
            Text(subtitle)
                .font(SpicyTheme.Typography.sub)
                .foregroundColor(SpicyTheme.Ink.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityElement(children: .combine)
    }

    private func sectionTitle(_ text: String) -> some View {
        Text(text)
            .font(SpicyTheme.Typography.title)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.top, SpicyTheme.Spacing.x5)
            .padding(.bottom, SpicyTheme.Spacing.x2)
            .accessibilityAddTraits(.isHeader)
    }
}
