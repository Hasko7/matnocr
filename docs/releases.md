# Release Protection

[Back to the documentation index](README.md)

## Active Repository Settings

Verified on 2026-11-24:

- The `Protect main` ruleset requires a pull request, an up-to-date branch, and
  the successful `CI` check from GitHub Actions. It blocks branch deletion and
  force pushes, with no bypass exceptions.
- The `Protect version tags` ruleset targets `v*` (`refs/tags/v*` in the API).
  It blocks tag updates and deletions, with no bypass exceptions. New version
  tags can still be created by users with the necessary repository permissions.
- GitHub release immutability is enabled for future releases. Once published,
  release assets and the associated tag are locked. Release titles and notes
  can still be edited.

These are GitHub repository settings; cloning the repository does not configure
them. Inspect them under **Settings → Rules → Rulesets** and
**Settings → General → Releases → Enable release immutability**.

## Python Package Publishing Workflows

The repository has separate Python-package workflows:

- `.github/workflows/testpypi.yml` runs manually from `main` and targets
  TestPyPI using the `testpypi` GitHub environment.
- `.github/workflows/release.yml` runs on a new `v*` tag and targets PyPI using
  the `pypi` GitHub environment. It checks that the tag matches the version in
  `pyproject.toml` and that the tagged commit is on `main`.

Both workflows run checks and build the wheel and sdist on Windows before a
separate job publishes them through OIDC. The user confirmed a successful
TestPyPI upload and fresh-environment installation of version `0.1.0`. The user
also confirmed configuration of the `pypi` GitHub environment and pending PyPI
Trusted Publisher. The PyPI project will be created on first publication. The
`pypi` environment can require a reviewer before publication. These workflows
publish Python packages only. Windows binary builds and the complete GitHub
Release pipeline remain planned work in `TODO.md`.

## Publishing Order for a Complete Release

When the full release pipeline is implemented:

1. Select a reviewed commit with successful checks, and verify that the package
   version matches its new version tag, such as `v0.1.0`.
2. Run release validation and build every artifact from that same tagged commit.
3. Create a **draft release** and upload all intended assets, checksums, and
   required third-party license files.
4. Verify the complete draft, then publish it. All assets must be uploaded
   before publication because release immutability locks them afterward.
5. Ship corrections under a new version, such as `v0.1.1`.

Protecting tags prevents later changes; it does not by itself run tests or
guarantee that a newly created tag points to a reviewed commit. The release
workflow must enforce validation before publishing.

GitHub documents [ruleset protections](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
and the [draft-first workflow for immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).
