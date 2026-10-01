import SwiftUI

// ================================================================
// MR. SPICY — Reusable row primitives (SpicyComponents.swift)
// Group containers, rows, chips, meters — the neutral equivalents of
// the row patterns found in the supplied overlay's UI taxonomy
// (toggle row, meter row, segmented row, key-value row), re-specified
// for legitimate settings/developer-tool use.
// ================================================================

// MARK: - Group (inset list container)

struct SpicyGroup<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        VStack(spacing: 0) { content }
            .background(SpicyTheme.Surface.elevated)
            .clipShape(RoundedRectangle(cornerRadius: SpicyTheme.Radius.medium, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: SpicyTheme.Radius.medium, style: .continuous)
                    .strokeBorder(SpicyTheme.Line.divider, lineWidth: 1)
            )
    }
}

/// Section label above a group.
struct SpicyGroupLabel: View {
    let text: String
    var body: some View {
        Text(text)
            .font(SpicyTheme.Typography.caption)
            .fontWeight(.bold)
            .tracking(0.6)
            .foregroundColor(SpicyTheme.Ink.tertiary)
            .frame(maxWidth: .infinity, alignment: .leading)
            .accessibilityAddTraits(.isHeader)
    }
}

// MARK: - Divider between rows

struct SpicyRowDivider: View {
    var body: some View {
        Rectangle()
            .fill(SpicyTheme.Line.divider)
            .frame(height: 1)
    }
}

// MARK: - Key-value row

struct SpicyKeyValueRow: View {
    let title: String
    let value: String

    var body: some View {
        HStack {
            Text(title).font(SpicyTheme.Typography.bodyEmph)
            Spacer()
            Text(value).font(SpicyTheme.Typography.sub).foregroundColor(SpicyTheme.Ink.secondary)
        }
        .padding(.horizontal, SpicyTheme.Spacing.x4)
        .padding(.vertical, SpicyTheme.Spacing.x3)
        .frame(minHeight: SpicyTheme.Metrics.minTouchTarget)
        .accessibilityElement(children: .combine)
    }
}

// MARK: - Toggle row

struct SpicyToggleRow: View {
    let title: String
    var subtitle: String? = nil
    @Binding var isOn: Bool

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text(title).font(SpicyTheme.Typography.bodyEmph)
                if let subtitle {
                    Text(subtitle)
                        .font(SpicyTheme.Typography.caption)
                        .foregroundColor(SpicyTheme.Ink.tertiary)
                        .multilineTextAlignment(.leading)
                }
            }
            Spacer(minLength: SpicyTheme.Spacing.x3)
            Toggle("", isOn: $isOn)
                .labelsHidden()
                .tint(SpicyTheme.Accent.base)
        }
        .padding(.horizontal, SpicyTheme.Spacing.x4)
        .padding(.vertical, SpicyTheme.Spacing.x3)
        .frame(minHeight: SpicyTheme.Metrics.minTouchTarget)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(title)
        .accessibilityValue(isOn ? "On" : "Off")
    }
}

// MARK: - Slider row

struct SpicySliderRow: View {
    let title: String
    @Binding var value: Double
    var range: ClosedRange<Double> = 0.6...1.0
    var step: Double = 0.05
    var formatter: (Double) -> String

    var body: some View {
        VStack(alignment: .leading, spacing: SpicyTheme.Spacing.x2) {
            HStack {
                Text(title).font(SpicyTheme.Typography.bodyEmph)
                Spacer()
                Text(formatter(value))
                    .font(SpicyTheme.Typography.sub)
                    .foregroundColor(SpicyTheme.Ink.secondary)
                    .monospacedDigit()
            }
            Slider(value: $value, in: range, step: step)
                .tint(SpicyTheme.Accent.base)
        }
        .padding(.horizontal, SpicyTheme.Spacing.x4)
        .padding(.vertical, SpicyTheme.Spacing.x3)
        .accessibilityElement(children: .contain)
        .accessibilityLabel(title)
        .accessibilityValue(formatter(value))
    }
}

// MARK: - Navigation row (chevron)

struct SpicyNavigationRow: View {
    let title: String
    var value: String? = nil
    var destructive: Bool = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Text(title)
                    .font(SpicyTheme.Typography.bodyEmph)
                    .foregroundColor(destructive ? SpicyTheme.Feedback.danger : SpicyTheme.Ink.primary)
                Spacer()
                if let value {
                    Text(value).font(SpicyTheme.Typography.sub).foregroundColor(SpicyTheme.Ink.secondary)
                }
                Image(systemName: "chevron.forward")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(SpicyTheme.Ink.tertiary)
                    // SwiftUI mirrors chevrons automatically in RTL.
            }
            .padding(.horizontal, SpicyTheme.Spacing.x4)
            .padding(.vertical, SpicyTheme.Spacing.x3)
            .frame(minHeight: SpicyTheme.Metrics.minTouchTarget)
            .contentShape(Rectangle())
        }
        .buttonStyle(SpicyPressableStyle())
        .accessibilityHint(value ?? title)
    }
}

// MARK: - Segmented choice row

enum SpicySegment: Identifiable, Hashable {
    case info, debug, error
    var id: Self { self }
}

struct SpicySegmentedRow: View {
    let title: String
    let options: [(id: SpicySegment, label: String)]
    @Binding var selection: SpicySegment

    var body: some View {
        VStack(alignment: .leading, spacing: SpicyTheme.Spacing.x2) {
            Text(title).font(SpicyTheme.Typography.bodyEmph)
            HStack(spacing: SpicyTheme.Spacing.x1) {
                ForEach(options, id: \.id) { option in
                    Button {
                        selection = option.id
                    } label: {
                        Text(option.label)
                            .font(SpicyTheme.Typography.caption)
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity, minHeight: 30)
                            .background(
                                selection == option.id
                                    ? AnyShapeStyle(SpicyTheme.Accent.base)
                                    : AnyShapeStyle(SpicyTheme.Surface.elevated2)
                            )
                            .foregroundColor(selection == option.id ? .white : SpicyTheme.Ink.secondary)
                            .clipShape(RoundedRectangle(cornerRadius: 11, style: .continuous))
                    }
                    .buttonStyle(SpicyPressableStyle())
                    .accessibilityAddTraits(selection == option.id ? .isSelected : [])
                }
            }
        }
        .padding(.horizontal, SpicyTheme.Spacing.x4)
        .padding(.vertical, SpicyTheme.Spacing.x3)
    }
}

// MARK: - Meter row (simulated progress)

struct SpicyMeterRow: View {
    let title: String
    let value: Double // 0...1
    var valueText: String

    var body: some View {
        VStack(alignment: .leading, spacing: SpicyTheme.Spacing.x2) {
            HStack {
                Text(title).font(SpicyTheme.Typography.bodyEmph)
                Spacer()
                Text(valueText)
                    .font(SpicyTheme.Typography.sub)
                    .foregroundColor(SpicyTheme.Ink.secondary)
                    .monospacedDigit()
            }
            GeometryReader { proxy in
                ZStack(alignment: .leading) {
                    Capsule().fill(SpicyTheme.Surface.elevated2)
                    Capsule()
                        .fill(SpicyTheme.Accent.gradient)
                        .frame(width: max(8, proxy.size.width * value))
                }
            }
            .frame(height: 10)
        }
        .padding(.horizontal, SpicyTheme.Spacing.x4)
        .padding(.vertical, SpicyTheme.Spacing.x3)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(title)
        .accessibilityValue(valueText)
    }
}

// MARK: - Chip

struct SpicyChip: View {
    enum Kind { case neutral, accent }
    let text: String
    var kind: Kind = .neutral

    var body: some View {
        Text(text)
            .font(SpicyTheme.Typography.micro)
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(kind == .accent ? SpicyTheme.Accent.soft : SpicyTheme.Surface.elevated2)
            .foregroundColor(kind == .accent ? SpicyTheme.Accent.bright : SpicyTheme.Ink.secondary)
            .clipShape(Capsule())
            .overlay(Capsule().strokeBorder(kind == .accent ? SpicyTheme.Accent.bright.opacity(0.25) : SpicyTheme.Line.border, lineWidth: 1))
    }
}
