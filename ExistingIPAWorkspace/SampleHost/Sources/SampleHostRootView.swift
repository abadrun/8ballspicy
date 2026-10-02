import ExistingIPAOverlayUI
import SwiftUI

struct SampleHostRootView: View {
    var body: some View {
        ZStack(alignment: .topTrailing) {
            LinearGradient(
                colors: [Color(red: 0.03, green: 0.05, blue: 0.08), Color(red: 0.08, green: 0.12, blue: 0.18)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 8) {
                Image(systemName: "checkmark.seal.fill")
                    .font(.largeTitle)
                    .foregroundStyle(.green)
                Text("Authorized Sample Host")
                    .font(.headline)
                Text("The local Swift package is linked at source level.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .padding()
            .accessibilityIdentifier("sample-host-content")

            ExistingIPAOverlayView()
                .padding(18)
                .accessibilityIdentifier("existing-ipa-overlay")
        }
        .preferredColorScheme(.dark)
    }
}
