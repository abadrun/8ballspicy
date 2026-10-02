#if canImport(SwiftUI)
import Foundation
import ExistingIPAOverlayCore

public enum OverlayLocalization {
    public static func text(_ key: String, language: OverlayLanguage) -> String {
        guard let path = Bundle.module.path(forResource: language.rawValue, ofType: "lproj"),
              let bundle = Bundle(path: path) else {
            return key
        }
        return NSLocalizedString(key, bundle: bundle, value: key, comment: "")
    }
}
#endif
