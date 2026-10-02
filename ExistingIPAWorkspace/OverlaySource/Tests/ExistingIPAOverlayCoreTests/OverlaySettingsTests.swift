import Foundation
import XCTest
@testable import ExistingIPAOverlayCore

final class OverlaySettingsTests: XCTestCase {
    func testDefaultsCoverEveryLocalPreference() {
        let value = OverlaySettings.default
        XCTAssertEqual(value.language, .english)
        XCTAssertEqual(value.size, .comfortable)
        XCTAssertEqual(value.panelOpacity, 0.94)
        XCTAssertEqual(value.interfaceScale, 1.0)
        XCTAssertTrue(value.showStatusBadge)
        XCTAssertTrue(value.hapticsEnabled)
        XCTAssertFalse(value.reduceMotion)
        XCTAssertTrue(value.rememberPosition)
    }

    func testEnumCasesAndRawValuesAreStable() {
        XCTAssertEqual(OverlaySection.allCases, [.overview, .appearance, .preferences, .language, .about])
        XCTAssertEqual(OverlayLanguage.allCases, [.english, .indonesian])
        XCTAssertEqual(OverlayLanguage.english.rawValue, "en")
        XCTAssertEqual(OverlayLanguage.indonesian.rawValue, "id")
        XCTAssertEqual(OverlaySize.allCases, [.compact, .comfortable, .large])
    }

    func testInitializerClampsBothBounds() {
        let upper = OverlaySettings(panelOpacity: 4, interfaceScale: 9)
        XCTAssertEqual(upper.panelOpacity, 1.0)
        XCTAssertEqual(upper.interfaceScale, 1.20)

        let lower = OverlaySettings(panelOpacity: -4, interfaceScale: 0)
        XCTAssertEqual(lower.panelOpacity, 0.70)
        XCTAssertEqual(lower.interfaceScale, 0.85)
    }

    func testNormalizeClampsDecodedOrMutatedValues() {
        var value = OverlaySettings.default
        value.panelOpacity = -1
        value.interfaceScale = 8
        value.normalize()
        XCTAssertEqual(value.panelOpacity, 0.70)
        XCTAssertEqual(value.interfaceScale, 1.20)
    }

    func testCodableRoundTripPreservesEveryField() throws {
        let original = OverlaySettings(
            language: .indonesian,
            size: .large,
            panelOpacity: 0.81,
            interfaceScale: 1.12,
            showStatusBadge: false,
            hapticsEnabled: false,
            reduceMotion: true,
            rememberPosition: false
        )
        let data = try JSONEncoder().encode(original)
        XCTAssertEqual(try JSONDecoder().decode(OverlaySettings.self, from: data), original)
    }

    func testStoreRoundTripUsesOnlyTheComponentStorageKey() throws {
        let memory = RecordingStore()
        let store = OverlaySettingsStore(storage: memory)
        var value = OverlaySettings.default
        value.language = .indonesian
        value.size = .compact
        value.reduceMotion = true

        try store.save(value)

        XCTAssertEqual(memory.setKeys, [OverlaySettingsStore.storageKey])
        XCTAssertEqual(store.load(), value)
        XCTAssertEqual(memory.readKeys, [OverlaySettingsStore.storageKey])
    }

    func testStoreNormalizesPersistedOutOfRangeValues() throws {
        let memory = RecordingStore()
        let raw = """
        {
          "language":"en",
          "size":"comfortable",
          "panelOpacity":-20,
          "interfaceScale":42,
          "showStatusBadge":true,
          "hapticsEnabled":true,
          "reduceMotion":false,
          "rememberPosition":true
        }
        """.data(using: .utf8)!
        memory.values[OverlaySettingsStore.storageKey] = raw

        let value = OverlaySettingsStore(storage: memory).load()

        XCTAssertEqual(value.panelOpacity, 0.70)
        XCTAssertEqual(value.interfaceScale, 1.20)
    }

    func testMalformedOrMissingPersistenceFallsBackToDefaults() {
        let missing = RecordingStore()
        XCTAssertEqual(OverlaySettingsStore(storage: missing).load(), .default)

        let malformed = RecordingStore()
        malformed.values[OverlaySettingsStore.storageKey] = Data("not-json".utf8)
        XCTAssertEqual(OverlaySettingsStore(storage: malformed).load(), .default)
    }

    func testResetRemovesOnlyTheComponentStorageKey() throws {
        let memory = RecordingStore()
        memory.values["unrelated"] = Data("keep".utf8)
        let store = OverlaySettingsStore(storage: memory)
        try store.save(.default)

        store.reset()

        XCTAssertEqual(memory.removedKeys, [OverlaySettingsStore.storageKey])
        XCTAssertNil(memory.values[OverlaySettingsStore.storageKey])
        XCTAssertNotNil(memory.values["unrelated"])
    }

    func testRealUserDefaultsSuitePersistsAcrossStoreInstancesAndResets() throws {
        let suiteName = "ExistingIPAOverlayCoreTests.\(UUID().uuidString)"
        let defaults = try XCTUnwrap(UserDefaults(suiteName: suiteName))
        defer { defaults.removePersistentDomain(forName: suiteName) }
        defaults.removePersistentDomain(forName: suiteName)

        var expected = OverlaySettings.default
        expected.language = .indonesian
        expected.panelOpacity = 0.77
        expected.rememberPosition = false
        try OverlaySettingsStore(storage: defaults).save(expected)

        XCTAssertEqual(OverlaySettingsStore(storage: defaults).load(), expected)
        OverlaySettingsStore(storage: defaults).reset()
        XCTAssertEqual(OverlaySettingsStore(storage: defaults).load(), .default)
    }
}

private final class RecordingStore: KeyValueStoring {
    var values: [String: Any] = [:]
    var readKeys: [String] = []
    var setKeys: [String] = []
    var removedKeys: [String] = []

    func data(forKey defaultName: String) -> Data? {
        readKeys.append(defaultName)
        return values[defaultName] as? Data
    }

    func set(_ value: Any?, forKey defaultName: String) {
        setKeys.append(defaultName)
        values[defaultName] = value
    }

    func removeObject(forKey defaultName: String) {
        removedKeys.append(defaultName)
        values.removeValue(forKey: defaultName)
    }
}
