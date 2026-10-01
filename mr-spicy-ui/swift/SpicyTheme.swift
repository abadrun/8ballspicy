import SwiftUI

// ================================================================
// MR. SPICY — Design tokens (SpicyTheme.swift)
// Single source of truth for the visual language. Mirrors
// mr-spicy-ui/prototype/css/spicy.css 1:1 so the web reference and
// the SwiftUI reference stay visually consistent.
// ================================================================

enum SpicyTheme {

    // MARK: - Surfaces

    enum Surface {
        static let background  = Color(hex: 0x0B090D)   // page / backdrop base
        static let solid       = Color(hex: 0x1A151B)   // panel surface
        static let elevated    = Color(hex: 0x251E27)   // inset lists, cards
        static let elevated2   = Color(hex: 0x2C242E)   // wells, pressed states
        static let pureBlack   = Color.black            // AMOLED variant
    }

    // MARK: - Brand (derived from the supplied logo.png mark #D20D0F)

    enum Accent {
        static let base   = Color(hex: 0xD20D0F)
        static let bright = Color(hex: 0xF0483C)
        static let soft   = Color(hex: 0xD20D0F).opacity(0.16)

        static let gradient = LinearGradient(
            colors: [Color(hex: 0xFF6A4D), Color(hex: 0xE5322B), Color(hex: 0xB00B0D)],
            startPoint: .topLeading, endPoint: .bottomTrailing
        )
    }

    // MARK: - Ink (text)

    enum Ink {
        static let primary   = Color(hex: 0xF4EFF2)
        static let secondary = Color(hex: 0xB9AFB8)
        static let tertiary  = Color(hex: 0x8E8390)
    }

    // MARK: - Lines & feedback

    enum Line {
        static let border  = Color.white.opacity(0.11)
        static let divider = Color.white.opacity(0.06)
    }

    enum Feedback {
        static let danger  = Color(hex: 0xFF5147)
        static let success = Color(hex: 0x3DD68C)
    }

    // MARK: - Spacing scale (4 pt grid)

    enum Spacing {
        static let x1: CGFloat = 4
        static let x2: CGFloat = 8
        static let x3: CGFloat = 12
        static let x4: CGFloat = 16
        static let x5: CGFloat = 20
        static let x6: CGFloat = 24
        static let x7: CGFloat = 28
        static let x8: CGFloat = 32
    }

    // MARK: - Corner radius

    enum Radius {
        static let small:  CGFloat = 10
        static let medium: CGFloat = 14
        static let large:  CGFloat = 20
        static let xlarge: CGFloat = 26
    }

    // MARK: - Typography

    enum Typography {
        static let display    = Font.system(size: 21,   weight: .heavy)
        static let title      = Font.system(size: 16,   weight: .bold)
        static let body       = Font.system(size: 14.5, weight: .regular)
        static let bodyEmph   = Font.system(size: 14.5, weight: .semibold)
        static let sub        = Font.system(size: 12.5, weight: .regular)
        static let caption    = Font.system(size: 11.5, weight: .medium)
        static let micro      = Font.system(size: 10.5, weight: .semibold)
    }

    // MARK: - Control metrics

    enum Metrics {
        static let minTouchTarget: CGFloat = 44
        static let circleDiameter:  CGFloat = 58
        static let iconSize:        CGFloat = 20
        static let panelWidth:      CGFloat = 340
    }

    // MARK: - Motion

    enum Motion {
        static let fast:   TimeInterval = 0.14
        static let medium: TimeInterval = 0.22
        static let slow:   TimeInterval = 0.32
    }
}

// MARK: - Color(hex:)

extension Color {
    init(hex: UInt32) {
        self.init(
            red:   Double((hex >> 16) & 0xFF) / 255.0,
            green: Double((hex >>  8) & 0xFF) / 255.0,
            blue:  Double( hex        & 0xFF) / 255.0
        )
    }
}

// MARK: - Panel chrome

/// Rounded, bordered, elevated surface used by the overlay panel and modals.
struct SpicyPanelModifier: ViewModifier {
    var cornerRadius: CGFloat = SpicyTheme.Radius.xlarge

    func body(content: Content) -> some View {
        content
            .background(SpicyTheme.Surface.solid)
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .strokeBorder(SpicyTheme.Line.border, lineWidth: 1)
            )
            .shadow(color: .black.opacity(0.55), radius: 24, x: 0, y: 18)
            .shadow(color: .black.opacity(0.40), radius: 14, x: 0, y: 4)
    }
}

extension View {
    func spicyPanel(cornerRadius: CGFloat = SpicyTheme.Radius.xlarge) -> some View {
        modifier(SpicyPanelModifier(cornerRadius: cornerRadius))
    }
}

// MARK: - Button styles

/// Subtle press feedback that respects Reduce Motion.
struct SpicyPressableStyle: ButtonStyle {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed && !reduceMotion ? 0.94 : 1)
            .opacity(configuration.isPressed ? 0.9 : 1)
            .animation(reduceMotion ? nil : .easeOut(duration: SpicyTheme.Motion.fast),
                       value: configuration.isPressed)
    }
}

/// Brand-gradient primary button.
struct SpicyPrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(SpicyTheme.Typography.sub.weight(.bold))
            .foregroundColor(.white)
            .frame(maxWidth: .infinity, minHeight: SpicyTheme.Metrics.minTouchTarget)
            .background(SpicyTheme.Accent.gradient)
            .clipShape(RoundedRectangle(cornerRadius: SpicyTheme.Radius.medium, style: .continuous))
            .opacity(configuration.isPressed ? 0.85 : 1)
    }
}

/// Quiet secondary button on an elevated surface.
struct SpicySecondaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(SpicyTheme.Typography.sub.weight(.bold))
            .foregroundColor(SpicyTheme.Ink.primary)
            .frame(maxWidth: .infinity, minHeight: SpicyTheme.Metrics.minTouchTarget)
            .background(SpicyTheme.Surface.elevated2)
            .clipShape(RoundedRectangle(cornerRadius: SpicyTheme.Radius.medium, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: SpicyTheme.Radius.medium, style: .continuous)
                    .strokeBorder(SpicyTheme.Line.border, lineWidth: 1)
            )
            .opacity(configuration.isPressed ? 0.8 : 1)
    }
}

/// Destructive button (e.g. "Reset").
struct SpicyDangerButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(SpicyTheme.Typography.sub.weight(.bold))
            .foregroundColor(SpicyTheme.Feedback.danger)
            .frame(maxWidth: .infinity, minHeight: SpicyTheme.Metrics.minTouchTarget)
            .background(SpicyTheme.Feedback.danger.opacity(0.14))
            .clipShape(RoundedRectangle(cornerRadius: SpicyTheme.Radius.medium, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: SpicyTheme.Radius.medium, style: .continuous)
                    .strokeBorder(SpicyTheme.Feedback.danger.opacity(0.3), lineWidth: 1)
            )
            .opacity(configuration.isPressed ? 0.8 : 1)
    }
}
