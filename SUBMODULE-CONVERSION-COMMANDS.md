# Convert Gitlink/Submodule Entries to Normal Directories

These commands convert the six affected directories from gitlinks (mode 160000) to normal tracked folders while preserving all files on disk.

---

## Step 1: Inspect (verify they are gitlinks)

```bash
git ls-files -s simulations/SINDy simulations/energy_demand simulations/flrw-expansion-visualizer simulations/physics_intuition_engine simulations/schrodinger-cat-lab simulations/supernova
```

**Expected:** Each line shows `160000` as the mode (gitlink). Normal files show `100644` or `100755`.

---

## Step 2: Remove from index only (files stay on disk)

```bash
git rm --cached simulations/SINDy
git rm --cached simulations/energy_demand
git rm --cached simulations/flrw-expansion-visualizer
git rm --cached simulations/physics_intuition_engine
git rm --cached simulations/schrodinger-cat-lab
git rm --cached simulations/supernova
```

- `--cached` = remove from Git index only, do NOT touch working tree
- Files in these directories remain on disk

---

## Step 3: Re-add as normal directories

```bash
git add simulations/SINDy
git add simulations/energy_demand
git add simulations/flrw-expansion-visualizer
git add simulations/physics_intuition_engine
git add simulations/schrodinger-cat-lab
git add simulations/supernova
```

This stages all files inside each directory as regular tracked files.

---

## Step 4: Commit and push

```bash
git commit -m "Convert submodule gitlinks to normal tracked directories"
git push
```

---

## Optional: Remove .gitmodules (if it exists)

If you have a `.gitmodules` file with these submodule entries, remove them or delete the file:

```bash
# Check if it exists
cat .gitmodules

# If it only references these six, you can remove the file
git rm .gitmodules
git add .gitmodules  # stages the deletion
```

---

## Safety notes

- Root `.git` is never touched
- No `rm -rf` or destructive commands
- `git rm --cached` only affects the index, not the filesystem
