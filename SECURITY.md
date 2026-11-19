# Security Policy

## Supported Versions

MatnOCR is currently a development preview. Reports against the current `main`
branch are welcome. No released-version support window or backport policy has
been established yet. A version in package metadata does not imply a public
release or a security maintenance guarantee.

## Report a Vulnerability

Please do not publish exploit details, sensitive PDFs, or personal data in
public issues or pull requests.

On the project's GitHub repository, use **Report a vulnerability** in the
security area when private vulnerability reporting is enabled. This sends the
report privately to repository maintainers. Creating this policy file does not
enable that GitHub setting.

If the private reporting option is unavailable, open a minimal issue asking
for a private security contact. Include no exploit steps, payloads, or affected
private documents. Wait for a private channel before sharing those details.
No dedicated security email address is published by this project at present.

See [GitHub's private reporting instructions](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately).

## What to Include Privately

- Affected commit or version, Windows build, Python version, and installation method.
- A description of the impact and the conditions required to trigger it.
- Minimal reproduction steps and an original or shareable sample, if needed.
- Relevant diagnostics, dependency versions, and any proposed mitigation.

Potential issues include unsafe PDF handling, unintended file access or data
loss, unsafe command construction, or incorrect privilege handling in language
pack management. Ordinary recognition errors belong in an OCR quality report,
unless they demonstrate a security impact.

If the problem appears to originate in PDFium, PyWinRT, or another dependency,
identify the dependency and version. Maintainers can coordinate with its
upstream project; please avoid disclosing an unfixed vulnerability publicly.

## Handling Reports

Maintainers will assess reports and coordinate any fix and disclosure with the
reporter. Response and remediation times depend on maintainer availability;
there is no guaranteed response deadline or bug bounty program. Please allow
time to investigate before publishing details.
