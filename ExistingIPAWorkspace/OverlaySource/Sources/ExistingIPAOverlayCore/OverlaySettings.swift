import Foundation

public enum OverlaySection: String, CaseIterable, Codable, Sendable {
    case overview
    case appearance
    case preferences
    case language
    case about
}

public enum OverlayLanguage: String, CaseIterable, Codable, Sendable {
    case english = "en"
    case indonesian = "id"
}

public enum OverlaySize: String, CaseIterable, Codable, Sendable {
    case compact
    case comfortable
    case large
}

/// Settings for the clean UI shell only. This model intentionally contains no
/// gameplay, automation, account, advertising, licensing, or capture-evasion state.
public struct OverlaySettings: Codable, Equatable, Sendable {
    public var language: OverlayLanguage
    public var size: OverlaySize
    public var panelOpacity: Double
    public var interfaceScale: Double
    public var showStatusBadge: Bool
    public var hapticsEnabled: Bool
    public var reduceMotion: Bool
    public var rememberPosition: Bool

    public init(
        language: OverlayLanguage = .english,
        size: OverlaySize = .comfortable,
        panelOpacity: Double = 0.94,
        interfaceScale: Double = 1.0,
        showStatusBadge: Bool = true,
        hapticsEnabled: Bool = true,
        reduceMotion: Bool = false,
        rememberPosition: Bool = true
    ) {
        self.language = language
        self.size = size
        self.panelOpacity = Self.clamp(panelOpacity, to: 0.70...1.0)
        self.interfaceScale = Self.clamp(interfaceScale, to: 0.85...1.20)
        self.showStatusBadge = showStatusBadge
        self.hapticsEnabled = hapticsEnabled
        self.reduceMotion = reduceMotion
        self.rememberPosition = rememberPosition
    }

    public static let `default` = OverlaySettings()

    public mutating func normalize() {
        panelOpacity = Self.clamp(panelOpacity, to: 0.70...1.0)
        interfaceScale = Self.clamp(interfaceScale, to: 0.85...1.20)
    }

    private static func clamp(_ value: Double, to range: ClosedRange<Double>) -> Double {
        min(max(value, range.lowerBound), range.upperBound)
    }
}
