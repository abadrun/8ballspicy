#if canImport(SwiftUI)
import SwiftUI
import ExistingIPAOverlayCore

@MainActor
public final class OverlayViewModel: ObservableObject {
    @Published public var isExpanded = false
    @Published public var selectedSection: OverlaySection = .overview
    @Published public var settings: OverlaySettings

    private let store: OverlaySettingsStore

    public init(store: OverlaySettingsStore = OverlaySettingsStore()) {
        self.store = store
        self.settings = store.load()
    }

    public func setExpanded(_ expanded: Bool) {
        if settings.reduceMotion {
            isExpanded = expanded
        } else {
            withAnimation(.spring(response: 0.30, dampingFraction: 0.86)) { isExpanded = expanded }
        }
    }

    public func persist() {
        try? store.save(settings)
    }

    public func reset() {
        store.reset()
        settings = .default
        selectedSection = .overview
    }
}
#endif
