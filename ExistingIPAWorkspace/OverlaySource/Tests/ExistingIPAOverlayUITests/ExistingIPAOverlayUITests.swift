import Foundation
import SwiftUI
import XCTest
import ExistingIPAOverlayCore
@testable import ExistingIPAOverlayUI

#if canImport(UIKit)
import UIKit
#elseif canImport(AppKit)
import AppKit
#endif

final class ExistingIPAOverlayUITests: XCTestCase {
    private let localizationKeys = [
        "app.title", "app.subtitle", "status.ready",
        "accessibility.open", "accessibility.close",
        "section.overview", "section.appearance", "section.preferences", "section.language", "section.about",
        "overview.subtitle", "overview.scope", "overview.local_only", "overview.no_network", "overview.no_gating",
        "appearance.subtitle", "appearance.layout", "appearance.size", "appearance.opacity", "appearance.scale",
        "size.compact", "size.comfortable", "size.large",
        "preferences.subtitle", "preferences.interface", "preferences.status", "preferences.status.detail",
        "preferences.haptics", "preferences.haptics.detail", "preferences.reduce_motion",
        "preferences.reduce_motion.detail", "preferences.position", "preferences.position.detail",
        "language.subtitle", "language.choose", "language.note",
        "about.subtitle", "about.details", "about.version", "about.implementation", "about.source_level",
        "about.network", "about.none", "about.reset", "about.reset.detail", "about.reset.button"
    ]

    func testEveryLocalizationKeyLoadsForEverySupportedLanguage() {
        for language in OverlayLanguage.allCases {
            for key in localizationKeys {
                let value = OverlayLocalization.text(key, language: language)
                XCTAssertFalse(value.isEmpty, "Empty localization for \(language.rawValue):\(key)")
                XCTAssertNotEqual(value, key, "Missing localization for \(language.rawValue):\(key)")
            }
        }
    }

    func testUnknownLocalizationKeyFallsBackToTheKey() {
        let key = "missing.test.key"
        XCTAssertEqual(OverlayLocalization.text(key, language: .english), key)
        XCTAssertEqual(OverlayLocalization.text(key, language: .indonesian), key)
    }

    func testResourceBackedAccentColorCanBeResolved() {
        _ = OverlayTheme.primary
        _ = OverlayTheme.secondary
    }

    @MainActor
    func testViewModelLoadsPersistsAndResetsLocalState() throws {
        let memory = MemoryStore()
        var seeded = OverlaySettings.default
        seeded.language = .indonesian
        seeded.size = .large
        try OverlaySettingsStore(storage: memory).save(seeded)

        let model = OverlayViewModel(store: OverlaySettingsStore(storage: memory))
        XCTAssertEqual(model.settings, seeded)
        XCTAssertEqual(model.selectedSection, .overview)
        XCTAssertFalse(model.isExpanded)

        model.settings.panelOpacity = 0.73
        model.selectedSection = .appearance
        model.persist()
        let reloaded = OverlaySettingsStore(storage: memory).load()
        XCTAssertEqual(reloaded.panelOpacity, 0.73)

        model.reset()
        XCTAssertEqual(model.settings, .default)
        XCTAssertEqual(model.selectedSection, .overview)
        XCTAssertEqual(OverlaySettingsStore(storage: memory).load(), .default)
    }

    @MainActor
    func testExpansionLifecycleWithAndWithoutMotion() {
        let model = OverlayViewModel(store: OverlaySettingsStore(storage: MemoryStore()))

        model.settings.reduceMotion = true
        model.setExpanded(true)
        XCTAssertTrue(model.isExpanded)
        model.setExpanded(false)
        XCTAssertFalse(model.isExpanded)

        model.settings.reduceMotion = false
        model.setExpanded(true)
        XCTAssertTrue(model.isExpanded)
        model.setExpanded(false)
        XCTAssertFalse(model.isExpanded)
    }

    @MainActor
    func testSwiftUIViewBodyEvaluatesInCollapsedAndExpandedStates() {
        let model = OverlayViewModel(store: OverlaySettingsStore(storage: MemoryStore()))
        let collapsed = ExistingIPAOverlayView(model: model)
        _ = collapsed.body

        model.settings.reduceMotion = true
        model.setExpanded(true)
        model.selectedSection = .language
        let expanded = ExistingIPAOverlayView(model: model)
        _ = expanded.body
    }

    @MainActor
    func testHostingControllerAppearanceLifecycle() {
        let model = OverlayViewModel(store: OverlaySettingsStore(storage: MemoryStore()))
        let root = ExistingIPAOverlayView(model: model)

        #if canImport(UIKit)
        let host = UIHostingController(rootView: root)
        let window = UIWindow(frame: CGRect(x: 0, y: 0, width: 844, height: 390))
        window.rootViewController = host
        window.makeKeyAndVisible()
        host.loadViewIfNeeded()
        host.beginAppearanceTransition(true, animated: false)
        host.endAppearanceTransition()
        XCTAssertTrue(host.isViewLoaded)
        XCTAssertNotNil(host.view.window)

        model.settings.reduceMotion = true
        model.setExpanded(true)
        host.rootView = ExistingIPAOverlayView(model: model)
        RunLoop.main.run(until: Date().addingTimeInterval(0.05))
        XCTAssertTrue(model.isExpanded)

        host.beginAppearanceTransition(false, animated: false)
        host.endAppearanceTransition()
        window.rootViewController = nil
        #elseif canImport(AppKit)
        let host = NSHostingController(rootView: root)
        let window = NSWindow(contentViewController: host)
        window.setContentSize(NSSize(width: 844, height: 520))
        window.makeKeyAndOrderFront(nil)
        XCTAssertNotNil(host.view.window)
        model.settings.reduceMotion = true
        model.setExpanded(true)
        host.rootView = ExistingIPAOverlayView(model: model)
        XCTAssertTrue(model.isExpanded)
        window.close()
        #else
        _ = root.body
        #endif
    }
}

private final class MemoryStore: KeyValueStoring {
    private var values: [String: Any] = [:]

    func data(forKey defaultName: String) -> Data? {
        values[defaultName] as? Data
    }

    func set(_ value: Any?, forKey defaultName: String) {
        values[defaultName] = value
    }

    func removeObject(forKey defaultName: String) {
        values.removeValue(forKey: defaultName)
    }
}
