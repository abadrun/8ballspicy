import Foundation

public protocol KeyValueStoring: AnyObject {
    func data(forKey defaultName: String) -> Data?
    func set(_ value: Any?, forKey defaultName: String)
    func removeObject(forKey defaultName: String)
}

extension UserDefaults: KeyValueStoring {}

/// Local-only persistence. No identifiers, network calls, subscriptions, ads,
/// activation keys, or host-application state are read or written.
public final class OverlaySettingsStore {
    public static let storageKey = "CleanOverlay.settings.v1"
    private let storage: KeyValueStoring
    private let encoder: JSONEncoder
    private let decoder: JSONDecoder

    public init(storage: KeyValueStoring = UserDefaults.standard) {
        self.storage = storage
        self.encoder = JSONEncoder()
        self.decoder = JSONDecoder()
    }

    public func load() -> OverlaySettings {
        guard let data = storage.data(forKey: Self.storageKey),
              var value = try? decoder.decode(OverlaySettings.self, from: data) else {
            return .default
        }
        value.normalize()
        return value
    }

    public func save(_ settings: OverlaySettings) throws {
        var normalized = settings
        normalized.normalize()
        storage.set(try encoder.encode(normalized), forKey: Self.storageKey)
    }

    public func reset() {
        storage.removeObject(forKey: Self.storageKey)
    }
}
