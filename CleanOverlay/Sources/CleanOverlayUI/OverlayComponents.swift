#if canImport(SwiftUI)
import SwiftUI

struct ModuleCard<Content: View>: View {
    let title: String
    let content: Content

    init(title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title.uppercased())
                .font(.caption.weight(.bold))
                .foregroundStyle(OverlayTheme.muted)
            content
        }
        .padding(14)
        .background(OverlayTheme.raised, in: RoundedRectangle(cornerRadius: OverlayTheme.cornerRadius))
        .overlay(RoundedRectangle(cornerRadius: OverlayTheme.cornerRadius).stroke(OverlayTheme.border))
    }
}

struct FeatureTile: View {
    let symbol: String
    let title: String
    let detail: String
    let selected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 8) {
                Image(systemName: symbol).font(.title3.weight(.semibold))
                Text(title).font(.subheadline.weight(.semibold))
                Text(detail).font(.caption).foregroundStyle(OverlayTheme.muted).lineLimit(2)
            }
            .frame(maxWidth: .infinity, minHeight: 90, alignment: .leading)
            .padding(12)
            .background(selected ? OverlayTheme.primary.opacity(0.18) : OverlayTheme.panel,
                        in: RoundedRectangle(cornerRadius: 13))
            .overlay(RoundedRectangle(cornerRadius: 13)
                .stroke(selected ? OverlayTheme.primary : OverlayTheme.border))
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(selected ? .isSelected : [])
    }
}

struct ToggleRow: View {
    let symbol: String
    let title: String
    let detail: String?
    @Binding var value: Bool

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: symbol).frame(width: 24).foregroundStyle(OverlayTheme.primary)
            VStack(alignment: .leading, spacing: 2) {
                Text(title).font(.subheadline.weight(.medium))
                if let detail { Text(detail).font(.caption).foregroundStyle(OverlayTheme.muted) }
            }
            Spacer(minLength: 8)
            Toggle("", isOn: $value).labelsHidden().tint(OverlayTheme.primary)
        }
        .frame(minHeight: OverlayTheme.rowHeight)
    }
}

struct MeterRow: View {
    let title: String
    let formattedValue: String
    let range: ClosedRange<Double>
    @Binding var value: Double

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack { Text(title).font(.subheadline.weight(.medium)); Spacer(); Text(formattedValue).foregroundStyle(OverlayTheme.muted) }
            Slider(value: $value, in: range).tint(OverlayTheme.primary)
        }
        .padding(.vertical, 5)
    }
}

struct SegmentedRow<Value: Hashable>: View {
    let title: String
    let options: [(Value, String)]
    @Binding var selection: Value

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title).font(.subheadline.weight(.medium))
            Picker(title, selection: $selection) {
                ForEach(options, id: \.0) { value, label in Text(label).tag(value) }
            }
            .pickerStyle(.segmented)
            .labelsHidden()
        }
    }
}

struct KeyValueRow: View {
    let key: String
    let value: String
    var body: some View {
        HStack { Text(key).foregroundStyle(OverlayTheme.muted); Spacer(); Text(value).fontWeight(.medium) }
            .font(.subheadline).frame(minHeight: 34)
    }
}
#endif
