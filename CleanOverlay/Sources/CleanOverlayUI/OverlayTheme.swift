#if canImport(SwiftUI)
import SwiftUI

public enum OverlayTheme {
    public static let background = Color(red: 0.045, green: 0.052, blue: 0.070)
    public static let panel = Color(red: 0.075, green: 0.085, blue: 0.112)
    public static let raised = Color(red: 0.105, green: 0.118, blue: 0.154)
    public static let border = Color.white.opacity(0.10)
    public static let primary = Color("OverlayAccent", bundle: .module)
    public static let secondary = Color(red: 0.62, green: 0.43, blue: 0.98)
    public static let positive = Color(red: 0.25, green: 0.82, blue: 0.58)
    public static let text = Color.white.opacity(0.94)
    public static let muted = Color.white.opacity(0.62)
    public static let cornerRadius: CGFloat = 16
    public static let rowHeight: CGFloat = 48
}
#endif
