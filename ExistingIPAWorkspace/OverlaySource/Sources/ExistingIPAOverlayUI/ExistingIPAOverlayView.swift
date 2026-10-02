#if canImport(SwiftUI)
import SwiftUI
import ExistingIPAOverlayCore

@MainActor
public struct ExistingIPAOverlayView: View {
    @StateObject private var model: OverlayViewModel

    public init(model: @autoclosure @escaping () -> OverlayViewModel = OverlayViewModel()) {
        _model = StateObject(wrappedValue: model())
    }

    public var body: some View {
        ZStack(alignment: .topTrailing) {
            if model.isExpanded {
                panel
                    .transition(.scale(scale: 0.92, anchor: .topTrailing).combined(with: .opacity))
            } else {
                Button { model.setExpanded(true) } label: {
                    Image(systemName: "slider.horizontal.3")
                        .font(.title3.weight(.bold)).foregroundStyle(.white)
                        .frame(width: 52, height: 52)
                        .background(LinearGradient(colors: [OverlayTheme.primary, OverlayTheme.secondary],
                                                   startPoint: .topLeading, endPoint: .bottomTrailing),
                                    in: Circle())
                        .shadow(color: .black.opacity(0.35), radius: 12, y: 6)
                }
                .accessibilityLabel(t("accessibility.open"))
            }
        }
        .preferredColorScheme(.dark)
        .environment(\.locale, Locale(identifier: model.settings.language.rawValue))
        .onChange(of: model.settings) { _ in model.persist() }
    }

    private var panel: some View {
        VStack(spacing: 0) {
            header
            Divider().overlay(OverlayTheme.border)
            HStack(spacing: 0) {
                sidebar
                Divider().overlay(OverlayTheme.border)
                ScrollView { content.padding(16).frame(maxWidth: .infinity, alignment: .topLeading) }
            }
        }
        .frame(width: 700, height: 520)
        .scaleEffect(model.settings.interfaceScale, anchor: .topTrailing)
        .background(OverlayTheme.background.opacity(model.settings.panelOpacity), in: RoundedRectangle(cornerRadius: 20))
        .overlay(RoundedRectangle(cornerRadius: 20).stroke(OverlayTheme.border))
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .shadow(color: .black.opacity(0.45), radius: 24, y: 12)
    }

    private var header: some View {
        HStack(spacing: 12) {
            Image(systemName: "square.grid.2x2.fill")
                .foregroundStyle(OverlayTheme.primary).font(.title3)
            VStack(alignment: .leading, spacing: 1) {
                Text(t("app.title")).font(.headline)
                Text(t("app.subtitle")).font(.caption).foregroundStyle(OverlayTheme.muted)
            }
            Spacer()
            if model.settings.showStatusBadge {
                Label(t("status.ready"), systemImage: "checkmark.circle.fill")
                    .font(.caption.weight(.semibold)).foregroundStyle(OverlayTheme.positive)
            }
            Button { model.setExpanded(false) } label: {
                Image(systemName: "xmark").frame(width: 32, height: 32)
            }
            .buttonStyle(.plain).accessibilityLabel(t("accessibility.close"))
        }
        .padding(.horizontal, 16).frame(height: 62)
    }

    private var sidebar: some View {
        VStack(spacing: 6) {
            ForEach(OverlaySection.allCases, id: \.self) { section in
                Button { model.selectedSection = section } label: {
                    HStack(spacing: 9) {
                        Image(systemName: icon(for: section)).frame(width: 20)
                        Text(t("section.\(section.rawValue)"))
                        Spacer()
                    }
                    .font(.subheadline.weight(.medium)).padding(.horizontal, 10).frame(height: 42)
                    .background(model.selectedSection == section ? OverlayTheme.primary.opacity(0.18) : .clear,
                                in: RoundedRectangle(cornerRadius: 10))
                    .foregroundStyle(model.selectedSection == section ? OverlayTheme.text : OverlayTheme.muted)
                }
                .buttonStyle(.plain)
            }
            Spacer()
            Text("v1.0").font(.caption2).foregroundStyle(OverlayTheme.muted)
        }
        .padding(12).frame(width: 160)
    }

    @ViewBuilder private var content: some View {
        switch model.selectedSection {
        case .overview: OverviewScreen(select: { model.selectedSection = $0 }, t: t)
        case .appearance: AppearanceScreen(settings: $model.settings, t: t)
        case .preferences: PreferencesScreen(settings: $model.settings, t: t)
        case .language: LanguageScreen(settings: $model.settings, t: t)
        case .about: AboutScreen(reset: model.reset, t: t)
        }
    }

    private func t(_ key: String) -> String { OverlayLocalization.text(key, language: model.settings.language) }
    private func icon(for section: OverlaySection) -> String {
        switch section {
        case .overview: "rectangle.grid.2x2"
        case .appearance: "paintbrush"
        case .preferences: "switch.2"
        case .language: "globe"
        case .about: "info.circle"
        }
    }
}
#endif
