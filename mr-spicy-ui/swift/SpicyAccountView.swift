import SwiftUI

// ================================================================
// MR. SPICY — Account & About sections (SpicyAccountView.swift)
// Account: honest local-demo presentation. It NEVER claims an
// entitlement: no fabricated PRO status, no key activation, no
// purchase or verification flows. The only "plan" shown is the
// literal, truthful "Free demo".
// ================================================================

struct SpicyAccountView: View {
    let language: SpicyLanguage

    /// Local demo profile. `nil` = signed out. Nothing is persisted or transmitted.
    @Binding var localProfileName: String?

    let onSignIn: () -> Void
    let onSignOut: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            Text(localized("account.title", language))
                .font(SpicyTheme.Typography.title)
                .frame(maxWidth: .infinity, alignment: .leading)

            // Identity card
            HStack(spacing: SpicyTheme.Spacing.x3) {
                Image("SpicyLogo")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 52, height: 52)
                    .clipShape(Circle())
                    .overlay(Circle().stroke(SpicyTheme.Accent.soft, lineWidth: 3))
                    .accessibilityHidden(true)

                VStack(alignment: .leading, spacing: 2) {
                    Text(localProfileName ?? localized("account.guest", language))
                        .font(SpicyTheme.Typography.bodyEmph)
                        .lineLimit(1)
                    Text(localized("account.localProfile", language))
                        .font(SpicyTheme.Typography.caption)
                        .foregroundColor(SpicyTheme.Ink.tertiary)
                }
                Spacer(minLength: SpicyTheme.Spacing.x2)
                SpicyChip(text: localized("account.planName", language))
            }
            .padding(SpicyTheme.Spacing.x4)
            .background(SpicyTheme.Surface.elevated)
            .clipShape(RoundedRectangle(cornerRadius: SpicyTheme.Radius.large, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: SpicyTheme.Radius.large, style: .continuous)
                    .strokeBorder(SpicyTheme.Line.divider, lineWidth: 1)
            )
            .padding(.top, SpicyTheme.Spacing.x3)

            // Honest plan note
            VStack(alignment: .leading, spacing: SpicyTheme.Spacing.x1) {
                Text(localized("account.planTitle", language))
                    .font(SpicyTheme.Typography.bodyEmph)
                Text(localized("account.planNote", language))
                    .font(SpicyTheme.Typography.caption)
                    .foregroundColor(SpicyTheme.Ink.tertiary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(SpicyTheme.Spacing.x4)
            .background(SpicyTheme.Surface.elevated)
            .clipShape(RoundedRectangle(cornerRadius: SpicyTheme.Radius.large, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: SpicyTheme.Radius.large, style: .continuous)
                    .strokeBorder(SpicyTheme.Line.divider, lineWidth: 1)
            )
            .padding(.top, SpicyTheme.Spacing.x3)

            // Status rows
            SpicyGroup {
                SpicyKeyValueRow(title: localized("account.status", language),
                                 value: statusText)
                SpicyRowDivider()
                SpicyKeyValueRow(title: localized("account.sync", language),
                                 value: localized("account.syncOff", language))
            }
            .padding(.top, SpicyTheme.Spacing.x4)

            HStack(spacing: SpicyTheme.Spacing.x2) {
                if localProfileName == nil {
                    Button(localized("account.signIn", language), action: onSignIn)
                        .buttonStyle(SpicyPrimaryButtonStyle())
                } else {
                    Button(localized("account.signOut", language), action: onSignOut)
                        .buttonStyle(SpicySecondaryButtonStyle())
                }
            }
            .padding(.top, SpicyTheme.Spacing.x4)
            .padding(.bottom, SpicyTheme.Spacing.x6)
        }
    }

    private var statusText: String {
        if let name = localProfileName {
            return SpicyLocalization.string("account.signedInAs", language, name)
        }
        return localized("account.signedOut", language)
    }
}

// ================================================================
// About — factual information about the reference implementation.
// ================================================================

struct SpicyAboutView: View {
    let language: SpicyLanguage

    var body: some View {
        VStack(spacing: 0) {
            Text(localized("about.title", language))
                .font(SpicyTheme.Typography.title)
                .frame(maxWidth: .infinity, alignment: .leading)

            Text(localized("about.what", language))
                .font(SpicyTheme.Typography.sub)
                .foregroundColor(SpicyTheme.Ink.secondary)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.top, SpicyTheme.Spacing.x2)

            SpicyGroup {
                SpicyKeyValueRow(title: localized("about.version", language), value: "1.0.0 · reference")
                SpicyRowDivider()
                SpicyKeyValueRow(title: localized("about.asset", language), value: "logo.png")
                SpicyRowDivider()
                SpicyKeyValueRow(title: localized("about.repo", language), value: "8ballspicy")
            }
            .padding(.top, SpicyTheme.Spacing.x4)

            Text(localized("about.footnote", language))
                .font(SpicyTheme.Typography.caption)
                .foregroundColor(SpicyTheme.Ink.tertiary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.top, SpicyTheme.Spacing.x3)
                .padding(.bottom, SpicyTheme.Spacing.x6)
        }
    }
}
