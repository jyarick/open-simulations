#!/bin/bash
# Convert gitlink/submodule entries to normal tracked directories
# Run from repository root. Preserves all files on disk.

set -e  # Exit on any error

echo "=== Step 1: Inspect gitlink/submodule entries ==="
echo "Mode 160000 = gitlink (submodule). Checking index..."
git ls-files -s simulations/SINDy simulations/energy_demand simulations/flrw-expansion-visualizer simulations/physics_intuition_engine simulations/schrodinger-cat-lab simulations/supernova 2>/dev/null | while read mode hash stage path; do
  if [ "$mode" = "160000" ]; then
    echo "  [GITLINK] $path"
  fi
done

echo ""
echo "=== Step 2: Remove gitlink entries from index (files stay on disk) ==="
# --cached = index only, -r = recursive (for dir), -f = force (required for gitlinks)
git rm --cached simulations/SINDy
git rm --cached simulations/energy_demand
git rm --cached simulations/flrw-expansion-visualizer
git rm --cached simulations/physics_intuition_engine
git rm --cached simulations/schrodinger-cat-lab
git rm --cached simulations/supernova

echo ""
echo "=== Step 3: Re-add as normal tracked directories ==="
git add simulations/SINDy
git add simulations/energy_demand
git add simulations/flrw-expansion-visualizer
git add simulations/physics_intuition_engine
git add simulations/schrodinger-cat-lab
git add simulations/supernova

echo ""
echo "=== Step 4: Commit and push ==="
git commit -m "Convert submodule gitlinks to normal tracked directories"
git push

echo ""
echo "Done. Directories are now normal tracked folders."
