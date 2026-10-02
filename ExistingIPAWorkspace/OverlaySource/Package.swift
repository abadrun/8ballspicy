// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "ExistingIPAOverlay",
    defaultLocalization: "en",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .library(name: "ExistingIPAOverlay", targets: ["ExistingIPAOverlayUI"]),
        .library(name: "ExistingIPAOverlayCore", targets: ["ExistingIPAOverlayCore"])
    ],
    targets: [
        .target(name: "ExistingIPAOverlayCore"),
        .target(
            name: "ExistingIPAOverlayUI",
            dependencies: ["ExistingIPAOverlayCore"],
            resources: [.process("Resources")]
        ),
        .testTarget(name: "ExistingIPAOverlayCoreTests", dependencies: ["ExistingIPAOverlayCore"]),
        .testTarget(
            name: "ExistingIPAOverlayUITests",
            dependencies: ["ExistingIPAOverlayUI", "ExistingIPAOverlayCore"]
        )
    ]
)
