# Installer internals: durability, recovery and trust boundaries

This page holds the detailed guarantees of `scripts/install_codex_skill.py`. The [README](../README.md#install) keeps the short version: the installer stages and validates the repository, promotes it atomically to `<dest>/seedance-20`, serializes concurrent installers on one destination, and replaces a complete existing install only with `--force`. Everything below is the fine print behind those four sentences, kept verbatim from earlier front-page revisions so the contract does not drift.

## Recovery and retry

Automatic retry is limited to states for which every
authority record required by the phase reached is present, has flushed file
contents and, on POSIX, a flushed containing-directory publication, and still
validates. Each payload file is first written under a transaction-derived
sibling name, bounded by the recorded size, synced, checked against the recorded
digest, atomically published at its final stage pathname, and followed by a
containing-directory sync on POSIX. A crash therefore leaves that final pathname
absent or complete, never truncated. The copy-sibling basename is capped at 34
ASCII bytes, shorter than the provenance marker already created before copying;
on POSIX it shortens further if the stage reports a smaller component limit.
Shortened names retain a transaction-and-path digest, and any namespace
collision makes staging fail closed before payload copying begins. This bound
applies only to copy siblings: the installer still requires the filesystem to
represent its longer stage and authority names, so it makes no end-to-end claim
for unusually small component limits. Recoverable states include an
exact empty stage before provenance publication; after complete provenance
publication, source-identical final payload files plus the one exact transaction-
bound in-progress sibling; an exact torn prefix of the installer's expected
provenance or completion record; and a deletion workspace bound by its external
transaction journal (plus the exact empty terminal workspace left if that
journal was already removed). Malformed, swapped, or otherwise untrusted records
and late or unexpected bytes are preserved for inspection. A truncated file at
an expected final payload pathname and an unbound temp-like file are likewise
never claimed for automatic cleanup.
So are the deliberately fail-closed hard-death windows after a quarantine is
renamed but before its authority marker is published, or after a private
deletion workspace is created but before its external journal is published.
During replacement, the previous copy remains available for rollback until the
validated stage is promoted. Restart your client afterwards so `seedance-20`
appears in its skill list.

On Windows, authority and deletion handles share reads only and remain open
through their consuming action; a pre-existing or newly requested writable or
deletion handle therefore makes the installer fail closed. On POSIX, verified
objects are moved into a journal-bound mode-`0700` workspace before unlink,
which excludes other OS accounts and narrows the deletion namespace. POSIX
`flock` and owner-only directory permissions are not mandatory isolation from a
hostile process running as the same account. Such a process may retain or open
writable descriptors and mutate either the workspace or its containing skills
directory; all of those capabilities are outside the portable guarantee. The
installer preserves mismatches it observes, but makes no stronger exclusion
claim against that same-account adversary.

On POSIX, authority records are flushed before their containing directory, and
transaction namespace renames and removals are followed by directory `fsync`.
Each copied payload file is individually `fsync`ed before its atomic rename, and
that file's containing stage directory is `fsync`ed after the rename. The
transaction does not recursively flush the supplied skills-directory ancestry;
that ancestry is assumed to have the durability expected by the caller.

Only manifest-declared files and their implied directories are created. Source
permissions are not inherited: POSIX stage/live directories are normalized to
`0700` and files to `0600`. Named streams, extended attributes, and resource
forks on the source root, declared files, or implied directories are refused
before transaction authority is published, because the portable install
contract cannot represent them.

See also [manual transfer and verification](MANUAL_INSTALL.md), [install scopes](INSTALL_SCOPES.md), [the read-only doctor](INSTALL_DOCTOR.md) and [migration from older layouts](INSTALL_MIGRATION.md).
