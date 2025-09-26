#!/usr/bin/env bash
set -euo pipefail
cd geofence_prover
nargo compile
srs_downloader -c ./target/geofence_prover.json -o ./target/geofence_prover.srs
cd ..
cp geofence_prover/target/geofence_prover.json mopro-example-app/ios/MoproApp/
cp geofence_prover/target/geofence_prover.srs  mopro-example-app/ios/MoproApp/
echo "✅ synced ACIR+SRS to iOS app"
