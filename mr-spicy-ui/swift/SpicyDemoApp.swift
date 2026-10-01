import SwiftUI

// ================================================================
// MR. SPICY — Demo host app (SpicyDemoApp.swift)
// Minimal host that presents the neutral overlay reference on an
// abstract backdrop. Replace this scene with any legitimate
// authorized host application.
//
// Setup: add the files in this folder to an iOS 16+ app target and
// add the derived circular logo asset (generated from the supplied
// logo.png — see mr-spicy-ui/prototype/assets/logo-circle-*.png)
// to Assets.xcassets as an image set named "SpicyLogo".
// ================================================================

@main
struct SpicyDemoApp: App {
    var body: some Scene {
        WindowGroup {
            SpicyOverlayView()
        }
    }
}
