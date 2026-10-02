// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "CleanOverlay",
    defaultLocalization: "en",
    platforms: [.iOS(.v16)],
    products: [
        .library(name: "CleanOverlay", targets: ["CleanOverlayUI"]),
        .library(name: "CleanOverlayCore", targets: ["CleanOverlayCore"])
    ],
    targets: [
        .target(name: "CleanOverlayCore"),
        .target(
            name: "CleanOverlayUI",
            dependencies: ["CleanOverlayCore"],
            resources: [.process("Resources")]
        ),
        .testTarget(name: "CleanOverlayCoreTests", dependencies: ["CleanOverlayCore"])
    ]
)
