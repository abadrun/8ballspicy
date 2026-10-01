import SwiftUI

// ================================================================
// MR. SPICY — Overlay (SpicyOverlayView.swift)
// The complete floating-overlay component and its state machine:
//
//     SpicyOverlayState.closed | minimized | expanded
//     SpicySection     home | tools | settings | account | about
//     SpicyModal       none | language | signIn | reset
//
// This is a NEUTRAL reference implementation for legitimate host
// applications (settings panels, developer tools, accessibility
// panels). It contains no gameplay, automation, or entitlement
// functionality by construction.
// ================================================================

enum SpicyOverlayState {
    case closed
    case minimized
    case expanded
}

enum SpicySection: String, CaseIterable, Identifiable {
    case home, tools, settings, account, about
    var id: String { rawValue }
}

enum SpicyModal: String, Identifiable {
    case none
    case language
    case signIn
    case reset
    var id: String { rawValue }
}

struct SpicySettings {
    var language: SpicyLanguage = .english
    var panelOpacity: Double = 0.95
    var textScale: Double = 1.0
    var pureBlack: Bool = false
    var reduceMotionOverride: Bool = false
    var reduceTransparency: Bool = false
    var localProfileName: String? = nil

    static let defaults = SpicySettings()
}

struct SpicyOverlayView: View {
    @Environment(\.accessibilityReduceMotion) private var systemReduceMotion

    @State private var settings = SpicySettings.defaults
    @State private var overlayState: SpicyOverlayState = .closed
    @State private var section: SpicySection = .home
    @State private var modal: SpicyModal = .none
    @State private var toast: String? = nil
    @State private var signInName = ""

    private var reduceMotion: Bool { systemReduceMotion || settings.reduceMotionOverride }

    var body: some View {
        ZStack {
            demoBackdrop
                .ignoresSafeArea()

            overlayRoot
        }
        .preferredColorScheme(.dark)
        .environment(\.layoutDirection, settings.language.layoutDirection)
        // Text-size preference is expressed through Dynamic Type emulation:
        .environment(\.dynamicTypeSize, dynamicTypeSize)
    }

    // MARK: - Overlay root (state machine)

    @ViewBuilder
    private var overlayRoot: some View {
        ZStack(alignment: .bottomTrailing) {
            switch overlayState {
            case .closed:
                fab

            case .minimized:
                pill

            case .expanded:
                panel
            }
        }
        .padding(16)
        .animation(reduceMotion ? nil : .spring(response: 0.32, dampingFraction: 0.86),
                   value: overlayState)
    }

    // MARK: - Closed: floating bubble

    private var fab: some View {
        Button {
            overlayState = .expanded
        } label: {
            Image("SpicyLogo")
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 56, height: 56)
                .clipShape(Circle())
                .padding(4)
                .background(Circle().fill(SpicyTheme.Surface.elevated))
                .overlay(Circle().strokeBorder(SpicyTheme.Line.border, lineWidth: 1))
                .shadow(color: .black.opacity(0.5), radius: 18, y: 10)
        }
        .buttonStyle(SpicyPressableStyle())
        .accessibilityLabel(localized("a11y.open", settings.language))
    }

    // MARK: - Minimized: pill

    private var pill: some View {
        Button {
            overlayState = .expanded
        } label: {
            HStack(spacing: SpicyTheme.Spacing.x2) {
                Image("SpicyLogo")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 26, height: 26)
                    .clipShape(Circle())
                Text("MR. SPICY")
                    .font(SpicyTheme.Typography.sub.weight(.bold))
                    .tracking(0.8)
                Image(systemName: "chevron.up")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(SpicyTheme.Ink.secondary)
            }
            .padding(.horizontal, SpicyTheme.Spacing.x4)
            .padding(.vertical, SpicyTheme.Spacing.x2)
            .background(Capsule().fill(pillSurface))
            .overlay(Capsule().strokeBorder(SpicyTheme.Line.border, lineWidth: 1))
            .shadow(color: .black.opacity(0.5), radius: 18, y: 10)
        }
        .buttonStyle(SpicyPressableStyle())
        .accessibilityLabel(localized("a11y.expand", settings.language))
    }

    private var pillSurface: Color {
        settings.reduceTransparency ? SpicyTheme.Surface.solid : Color(hex: 0x1A151B).opacity(settings.panelOpacity)
    }

    // MARK: - Expanded: panel

    private var panel: some View {
        VStack(spacing: 0) {
            SpicyHeaderView(
                subtitle: localized("app.subtitle", settings.language),
                onSettings: { switchTo(.settings) },
                onMinimize: { overlayState = .minimized },
                onClose: { overlayState = .closed }
            )

            SpicyCirclesRow(items: circleItems, activeID: activeCircleID)
                .padding(.horizontal, SpicyTheme.Spacing.x3)
                .padding(.top, SpicyTheme.Spacing.x4)

            ScrollView {
                sectionContent
                    .padding(.horizontal, SpicyTheme.Spacing.x4)
                    .padding(.top, SpicyTheme.Spacing.x3)
                    .padding(.bottom, SpicyTheme.Spacing.x5)
            }

            HStack(spacing: SpicyTheme.Spacing.x2) {
                Circle().fill(SpicyTheme.Feedback.success).frame(width: 6, height: 6)
                Text(localized("footer.caption", settings.language))
                    .font(SpicyTheme.Typography.micro)
                    .foregroundColor(SpicyTheme.Ink.tertiary)
            }
            .padding(.vertical, SpicyTheme.Spacing.x2)
            .frame(maxWidth: .infinity)
            .overlay(alignment: .top) { SpicyRowDivider() }
        }
        .frame(width: min(SpicyTheme.Metrics.panelWidth + 20, panelMaxWidth))
        .frame(maxHeight: 560)
        .spicyPanel()
        .opacity(settings.reduceTransparency ? 1 : settings.panelOpacity)
        .accessibilityElement(children: .contain)
        .accessibilityLabel(localized("a11y.panel", settings.language))
    }

    private var panelMaxWidth: CGFloat {
        // Compact-width devices keep a safe margin.
        UIScreen.main.bounds.width - 24
    }

    // MARK: - Feature circles

    private var circleItems: [SpicyCirclesRow.Item] {
        [
            .init(id: "home", label: localized("nav.home", settings.language),
                  systemImage: "house.fill", action: { switchTo(.home) }),
            .init(id: "tools", label: localized("nav.tools", settings.language),
                  systemImage: "slider.horizontal.3", action: { switchTo(.tools) }),
            .init(id: "settings", label: localized("nav.settings", settings.language),
                  systemImage: "gearshape.fill", action: { switchTo(.settings) }),
            .init(id: "language", label: localized("nav.language", settings.language),
                  systemImage: "globe", action: { modal = .language }),
            .init(id: "account", label: localized("nav.account", settings.language),
                  systemImage: "person.crop.circle.fill", action: { switchTo(.account) }),
            .init(id: "about", label: localized("nav.about", settings.language),
                  systemImage: "info.circle.fill", action: { switchTo(.about) })
        ]
    }

    private var activeCircleID: String? {
        // The language circle is an action, never a destination.
        modal == .none ? section.rawValue : nil
    }

    private func switchTo(_ target: SpicySection) {
        section = target
    }

    // MARK: - Section content

    @ViewBuilder
    private var sectionContent: some View {
        switch section {
        case .home:
            SpicyHomeView(
                language: settings.language,
                onOpenSettings: { switchTo(.settings) },
                onToggleLanguage: {
                    settings.language = settings.language == .english ? .arabic : .english
                }
            )
        case .tools:
            SpicyToolsView(language: settings.language)
        case .settings:
            SpicySettingsView(
                language: settings.language,
                panelOpacity: $settings.panelOpacity,
                textScale: $settings.textScale,
                pureBlack: $settings.pureBlack,
                reduceMotionOverride: $settings.reduceMotionOverride,
                reduceTransparency: $settings.reduceTransparency,
                onOpenLanguage: { modal = .language },
                onOpenAbout: { switchTo(.about) },
                onReset: { modal = .reset }
            )
        case .account:
            SpicyAccountView(language: settings.language,
                             localProfileName: $settings.localProfileName,
                             onSignIn: { modal = .signIn },
                             onSignOut: {
                                 settings.localProfileName = nil
                                 showToast("toast.signedOut")
                             })
        case .about:
            SpicyAboutView(language: settings.language)
        }
    }

    // MARK: - Modal layer

    @ViewBuilder
    private var modalLayer: some View {
        switch modal {
        case .none:
            EmptyView()

        case .language:
            SpicyModalView(
                title: localized("modal.languageTitle", settings.language),
                subtitle: localized("modal.languageSub", settings.language),
                content: {
                    SpicyGroup {
                        ForEach(SpicyLanguage.allCases) { lang in
                            SpicyNavigationRow(title: lang.label,
                                               value: lang.directionLabel) {
                                settings.language = lang
                                modal = .none
                            }
                            if lang != SpicyLanguage.allCases.last {
                                SpicyRowDivider()
                            }
                        }
                    }
                },
                secondaryAction: SpicyModalAction(title: localized("modal.cancel", settings.language),
                                                  role: .secondary) { modal = .none },
                isPresented: modal == .language,
                onClose: { modal = .none }
            )

        case .signIn:
            SpicyModalView(
                title: localized("modal.signinTitle", settings.language),
                subtitle: localized("modal.signinSub", settings.language),
                content: {
                    TextField(localized("modal.namePh", settings.language), text: $signInName)
                        .textFieldStyle(.roundedBorder)
                        .autocorrectionDisabled()
                        .accessibilityLabel(localized("modal.nameLabel", settings.language))
                },
                primaryAction: SpicyModalAction(title: localized("modal.signinCta", settings.language)) {
                    settings.localProfileName = signInName.trimmingCharacters(in: .whitespaces).isEmpty
                        ? "spicy.guest"
                        : signInName.trimmingCharacters(in: .whitespaces)
                    modal = .none
                    showToast("toast.signedIn")
                },
                secondaryAction: SpicyModalAction(title: localized("modal.cancel", settings.language),
                                                  role: .secondary) { modal = .none },
                isPresented: modal == .signIn,
                onClose: { modal = .none }
            )

        case .reset:
            SpicyModalView(
                title: localized("modal.resetTitle", settings.language),
                subtitle: localized("modal.resetBody", settings.language),
                content: { EmptyView() },
                primaryAction: SpicyModalAction(title: localized("modal.resetCta", settings.language),
                                                role: .danger) {
                    let keep = settings.localProfileName
                    settings = SpicySettings.defaults
                    settings.localProfileName = keep
                    section = .settings
                    modal = .none
                    showToast("toast.reset")
                },
                secondaryAction: SpicyModalAction(title: localized("modal.cancel", settings.language),
                                                  role: .secondary) { modal = .none },
                isPresented: modal == .reset,
                onClose: { modal = .none }
            )
        }
    }

    // MARK: - Toast

    @ViewBuilder
    private var toastLayer: some View {
        if let toast {
            Text(toastKey(toast))
                .font(SpicyTheme.Typography.sub.weight(.semibold))
                .padding(.horizontal, SpicyTheme.Spacing.x5)
                .padding(.vertical, SpicyTheme.Spacing.x2)
                .background(Capsule().fill(SpicyTheme.Surface.elevated))
                .overlay(Capsule().strokeBorder(SpicyTheme.Line.border, lineWidth: 1))
                .shadow(color: .black.opacity(0.5), radius: 14, y: 8)
                .transition(reduceMotion ? .opacity : .opacity.combined(with: .move(edge: .bottom)))
                .onAppear {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2.2) {
                        withAnimation { self.toast = nil }
                    }
                }
                .accessibilityLabel(toastKey(toast))
        }
    }

    private func toastKey(_ key: String) -> String {
        localized(key, settings.language)
    }

    private func showToast(_ key: String) {
        withAnimation { toast = key }
    }

    // MARK: - Dynamic Type emulation for the text-size preference

    private var dynamicTypeSize: DynamicTypeSize {
        switch settings.textScale {
        case ..<0.95:  return .small
        case ..<1.05:  return .large      // default
        case ..<1.10:  return .xLarge
        default:       return .xxLarge
        }
    }

    // MARK: - Demo backdrop (abstract; not any product's artwork)

    private var demoBackdrop: some View {
        ZStack {
            (settings.pureBlack ? Color.black : SpicyTheme.Surface.background)
            RadialGradient(colors: [SpicyTheme.Accent.base.opacity(0.20), .clear],
                           center: UnitPoint(x: 0.85, y: 0.1), startRadius: 10, endRadius: 420)
            RadialGradient(colors: [SpicyTheme.Accent.base.opacity(0.12), .clear],
                           center: UnitPoint(x: 0.1, y: 0.95), startRadius: 10, endRadius: 460)
            Text("MR. SPICY")
                .font(.system(size: 56, weight: .heavy))
                .tracking(10)
                .foregroundColor(Color.white.opacity(0.05))
                .padding(.top, 160)
                .accessibilityHidden(true)
        }
    }
}
