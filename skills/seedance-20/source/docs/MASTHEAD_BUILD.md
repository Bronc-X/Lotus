# Masthead build chain

How the outlined display type in `assets/hero-dark.svg` and `assets/hero-light.svg` is produced and verified. The [README design standard](../README.md#design-standard) states the rule; this page keeps the full toolchain description verbatim from the earlier front page. Tokens live in [the frontend design system](../references/frontend-design-system.md); acceptance steps live in [README design acceptance](frontend-redesign.md).

The outlined display type has a separate, build-only toolchain. Before changing
the wordmark or tagline geometry, run `python -I -S -B scripts/build_masthead_outlines.py`
and then `python -I -S -B scripts/build_hero.py`. A writing run first recreates a
dedicated, marker-protected venv outside the checkout. The clear target is rejected when it
is inside the repository, trust directory, Python installation, or a non-temp
home subtree; equals a protected root; or would contain the repository, home
directory, Python prefix, system temp root, or external trust directory. A
dedicated descendant of the system temp directory remains allowed. The installer
then uses pip's `--force-reinstall --require-hashes` against the resolved lock.
The selected wheel artifacts are retained in the build venv; their hashes, pip's install
report, and the sha256 of every locked-distribution file are sealed together,
and the installed import bytes are compared directly with those retained wheel
archives. The venv is created with `--without-pip`, so creation never starts its
runner. The parent then stores and re-verifies a separate trust record outside
the venv that binds the runner, config, trusted base Python, current builder
script, lock, and initialized marker; the runner bytes must match the trusted
stdlib venv launcher. Only then can the verified runner bootstrap bundled pip and
perform the hash-locked installation. After sealing, the parent promotes that
record only if those inputs are unchanged and binds the sealed marker too. A
no-site `python -I -S -B` child verifies the package seal before adding the dedicated
site-packages path or importing FontTools and uharfbuzz.
Inherited loader, Python, pip, and virtualenv hooks are removed from child
environments. The generator records the exact lock digest plus the FontTools,
uharfbuzz, and HarfBuzz versions in
`assets/masthead-outlines.json`. The current lock pins `uharfbuzz==0.55.0`, the
latest stable release shown by [official PyPI metadata](https://pypi.org/project/uharfbuzz/0.55.0/)
when the lock was reviewed on 2026-08-02; the newer 0.56 line was prerelease-only.
Its six hashes are the published CPython abi3 wheels for Windows x86-64, Linux
glibc/musl on x86-64 and ARM64, and macOS universal2. Before either SVG is
written, `build_hero.py` independently requires the exact lock path, lock-byte
digest, install policy, and builder-version map recorded in the outline asset,
then renders both themes in memory so a second-theme failure cannot leave a
half-updated pair.
To prepare a later read-only check without regenerating, run
`python -I -S -B scripts/build_masthead_outlines.py --install-build-deps` once and then
use `python -I -S -B scripts/build_masthead_outlines.py --check` offline. Both commands
resolve the same checkout-specific temp venv by default; CI passes an explicit
run-attempt-specific `--build-env` under `/tmp`, because the hosted Linux
`$RUNNER_TEMP` is below `$HOME` and the clear guard deliberately rejects home
descendants. The wheelhouse remains under `$RUNNER_TEMP`; it is read, not cleared.
A changed distribution file, retained wheel, install report, lock, runner, venv
config, builder script, marker, startup hook, external trust record, or structured
child result makes the offline check fail closed and requires a fresh install.
