ballot_provenance: software to provide evidence for the provenance of paper ballots by publishing hashes of images of the ballots during scanning

To help secure the chain-of-custody of paper ballots in elections,
this software helps election administrators to obtain and publish
"fingerprints" (sha256 cryptographic hashes) of each of their ballot
images, and publish that while scanning ballots in an election.

When the paper ballots are audited, perhaps weeks later, those images
can be compared with the paper ballot, and their hashes can be compared
with the originally published and timestamped hashes, to help ensure
that nothing was changed along the way.

Supported: Dominion project backup zip files.
