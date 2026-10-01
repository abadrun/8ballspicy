import SwiftUI

// ================================================================
// MR. SPICY — Modal (SpicyModalView.swift)
// Consistent modal presentation: scrim + card, title/subtitle/body,
// optional actions, close control, Escape-equivalent (the scrim tap),
// focus semantics via accessibility, and Reduce Motion awareness.
// ================================================================

struct SpicyModalAction {
    let title: String
    var role: Role = .primary
    let action: () -> Void

    enum Role { case primary, secondary, danger }
}

struct SpicyModalView<Content: View>: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    let title: String
    var subtitle: String? = nil
    @ViewBuilder var content: Content
    var primaryAction: SpicyModalAction? = nil
    var secondaryAction: SpicyModalAction? = nil
    var isPresented: Bool
    let onClose: () -> Void

    var body: some View {
        ZStack {
            if isPresented {
                Color.black
                    .opacity(0.55)
                    .ignoresSafeArea()
                    .onTapGesture(perform: onClose)
                    .transition(.opacity)
                    .accessibilityLabel("Close")
                    .accessibilityAddTraits(.isButton)

                card
                    .padding(.horizontal, SpicyTheme.Spacing.x4)
                    .transition(reduceMotion ? .opacity : .opacity.combined(with: .move(edge: .bottom).combined(with: .scale(scale: 0.97))))
            }
        }
        .animation(reduceMotion ? .easeIn(duration: 0.01) : .easeOut(duration: SpicyTheme.Motion.medium),
                   value: isPresented)
    }

    private var card: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Head
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(SpicyTheme.Typography.title)
                        .foregroundColor(SpicyTheme.Ink.primary)
                    if let subtitle {
                        Text(subtitle)
                            .font(SpicyTheme.Typography.caption)
                            .foregroundColor(SpicyTheme.Ink.tertiary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                Spacer(minLength: SpicyTheme.Spacing.x2)
                Button(action: onClose) {
                    Image(systemName: "xmark")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(SpicyTheme.Ink.secondary)
                        .frame(width: 36, height: 36)
                        .contentShape(Rectangle())
                }
                .buttonStyle(SpicyPressableStyle())
                .accessibilityLabel("Close")
            }
            .padding(.top, SpicyTheme.Spacing.x5)
            .padding(.horizontal, SpicyTheme.Spacing.x4)

            // Body
            content
                .padding(.top, SpicyTheme.Spacing.x2)
                .padding(.horizontal, SpicyTheme.Spacing.x4)

            // Actions
            if primaryAction != nil || secondaryAction != nil {
                HStack(spacing: SpicyTheme.Spacing.x2) {
                    if let secondary = secondaryAction {
                        Button(secondary.title, action: secondary.action)
                            .buttonStyle(SpicySecondaryButtonStyle())
                    }
                    if let primary = primaryAction {
                        Button(primary.title, action: primary.action)
                            .buttonStyle(primary.role == .danger ? SpicyDangerButtonStyle() : SpicyPrimaryButtonStyle())
                    }
                }
                .padding(.top, SpicyTheme.Spacing.x3)
                .padding(.bottom, SpicyTheme.Spacing.x4)
                .padding(.horizontal, SpicyTheme.Spacing.x4)
            } else {
                Spacer(minLength: SpicyTheme.Spacing.x4)
                    .padding(.bottom, SpicyTheme.Spacing.x4)
            }
        }
        .frame(maxWidth: 340, alignment: .leading)
        .spicyPanel()
        .accessibilityElement(children: .contain)
        .accessibilityLabel(title)
    }
}
