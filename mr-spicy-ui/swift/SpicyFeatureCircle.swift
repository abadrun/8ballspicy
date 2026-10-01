import SwiftUI

// ================================================================
// MR. SPICY — Feature circle (SpicyFeatureCircle.swift)
// Consistent circular navigation control with identical geometry for
// every feature: active / inactive / disabled states, ≥44 pt target,
// VoiceOver label, automatic RTL mirroring (pure layout, no flips
// needed).
// ================================================================

struct SpicyFeatureCircle: View {
    enum DisplayState { case active, inactive, disabled }

    let label: String
    let systemImage: String
    var state: DisplayState = .inactive
    let action: () -> Void

    private var faceFill: AnyShapeStyle {
        switch state {
        case .active:   return AnyShapeStyle(SpicyTheme.Accent.gradient)
        case .inactive: return AnyShapeStyle(SpicyTheme.Surface.elevated)
        case .disabled: return AnyShapeStyle(SpicyTheme.Surface.elevated)
        }
    }

    private var iconColor: Color {
        switch state {
        case .active:   return .white
        case .inactive: return SpicyTheme.Ink.secondary
        case .disabled: return SpicyTheme.Ink.tertiary
        }
    }

    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                ZStack {
                    Circle()
                        .fill(faceFill)
                    Circle()
                        .strokeBorder(state == .active ? Color.clear : SpicyTheme.Line.border, lineWidth: 1)
                    Image(systemName: systemImage)
                        .font(.system(size: SpicyTheme.Metrics.iconSize, weight: .medium))
                        .foregroundColor(iconColor)
                }
                .frame(width: SpicyTheme.Metrics.circleDiameter,
                       height: SpicyTheme.Metrics.circleDiameter)
                .shadow(color: state == .active ? SpicyTheme.Accent.base.opacity(0.45) : .clear,
                        radius: 14, y: 6)

                Text(label)
                    .font(SpicyTheme.Typography.micro)
                    .foregroundColor(state == .active ? SpicyTheme.Ink.primary : SpicyTheme.Ink.tertiary)
                    .lineLimit(1)
                    .truncationMode(.tail)
            }
            .frame(minWidth: 48)
            .padding(.vertical, SpicyTheme.Spacing.x1)
        }
        .buttonStyle(SpicyPressableStyle())
        .disabled(state == .disabled)
        .accessibilityLabel(label)
        .accessibilityAddTraits(state == .active ? [.isSelected] : [])
    }
}

// MARK: - Circles row

/// A row of feature circles; the first `activeIndex` circle renders active.
struct SpicyCirclesRow: View {
    struct Item: Identifiable {
        let id: String
        let label: String
        let systemImage: String
        var disabled: Bool = false
        let action: () -> Void
    }

    let items: [Item]
    let activeID: String?

    var body: some View {
        HStack(alignment: .top, spacing: SpicyTheme.Spacing.x1) {
            ForEach(items) { item in
                SpicyFeatureCircle(
                    label: item.label,
                    systemImage: item.systemImage,
                    state: state(for: item),
                    action: item.action
                )
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Panel sections")
    }

    private func state(for item: Item) -> SpicyFeatureCircle.DisplayState {
        if item.disabled { return .disabled }
        return item.id == activeID ? .active : .inactive
    }
}
