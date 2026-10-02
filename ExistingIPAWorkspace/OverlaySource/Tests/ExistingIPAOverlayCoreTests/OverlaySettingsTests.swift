import XCTest
@testable import ExistingIPAOverlayCore

final class OverlaySettingsTests: XCTestCase {
    func testDefaultsAreSafeAndLocal() {
        let value = OverlaySettings.default
        XCTAssertEqual(value.language, .english)
        XCTAssertEqual(value.size, .comfortable)
        XCTAssertEqual(value.panelOpacity, 0.94)
        XCTAssertEqual(value.interfaceScale, 1.0)
    }

    func testInitializerClampsNumericSettings() {
        let value = OverlaySettings(panelOpacity: 4, interfaceScale: 0)
        XCTAssertEqual(value.panelOpacity, 1.0)
        XCTAssertEqual(value.interfaceScale, 0.85)
    }

    func testStoreRoundTripAndReset() throws {
        let memory = MemoryStore()
        let store = OverlaySettingsStore(storage: memory)
        var value = OverlaySettings.default
        value.language = .indonesian
        value.reduceMotion = true
        try store.save(value)
        XCTAssertEqual(store.load(), value)
        store.reset()
        XCTAssertEqual(store.load(), .default)
    }
}

private final class MemoryStore: KeyValueStoring {
    private var values: [String: Any] = [:]
    func data(forKey defaultName: String) -> Data? { values[defaultName] as? Data }
    func set(_ value: Any?, forKey defaultName: String) { values[defaultName] = value }
    func removeObject(forKey defaultName: String) { values.removeValue(forKey: defaultName) }
}
