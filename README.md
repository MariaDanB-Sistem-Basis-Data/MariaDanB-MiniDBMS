# MariaDanB-MiniDBMS
Mini DBMS for IF3140 Database Systems.

# How to Install

```bash
git clone --recurse-submodules https://github.com/MariaDanB-Sistem-Basis-Data/MariaDanB-MiniDBMS.git
```

- update 
```bash
  git submodule update --init --recursive
```

Manual milestone integration (buat maintainer)
```bash
  git submodule foreach --recursive 'git fetch --all'
  git submodule update --init --remote --recursive
  git add .
  git commit -m "chore(integration): update submodules to latest upstream (milestone X.Y)"
  git push origin main
```