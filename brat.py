#!/usr/bin/env python3
import os, sys, json, subprocess, tempfile, shutil, tarfile, zipfile
from datetime import datetime
import urllib.request

BRATOS_VERSION = "1.3.2"
BRATOS_HOME = os.path.expanduser("~/.bratos")
BRATOS_INDEX = os.path.join(BRATOS_HOME, "index.json")
BRATOS_STATE = os.path.join(BRATOS_HOME, "state.json")
BRATOS_INDEX_URL = "https://raw.githubusercontent.com/gulbalamesiyev/bratos-tools/main/index.json"
PREFIX = "/data/data/com.termux/files/usr"
TOOLS_DIR = os.path.join(BRATOS_HOME, "tools")

# ═══════════════ CORE ═══════════════
def load_state():
    if os.path.exists(BRATOS_STATE):
        with open(BRATOS_STATE) as f: return json.load(f)
    return {"installed": {}}

def save_state(s):
    with open(BRATOS_STATE, 'w') as f: json.dump(s, f, indent=2)

def load_index():
    if os.path.exists(BRATOS_INDEX):
        with open(BRATOS_INDEX) as f: return json.load(f)
    return {"packages": {}}

def get_token():
    c = os.path.join(BRATOS_HOME, "config")
    if os.path.exists(c):
        for l in open(c):
            if l.startswith("GITHUB_TOKEN="): return l.strip().split("=",1)[1]
    return None

def is_installed(name, state=None):
    if state is None: state = load_state()
    return name in state.get("installed", {})

# ═══════════════ DOCTOR ═══════════════
def doctor():
    state = load_state(); idx = load_index()
    
    # Rəng kodları
    G = "\033[1;32m"  # Yaşıl
    R = "\033[1;31m"  # Qırmızı
    C = "\033[1;36m"  # Cyan
    W = "\033[1;37m"  # Ağ
    X = "\033[0m"     # Reset
    
    print(f"{R}┌─────────────────────────────────────────┐{X}")
    print(f"{R}│{X}  {G}BRATOS {BRATOS_VERSION} CORE{X}                     {R}│{X}")
    print(f"{R}│{X}─────────────────────────────────────────{R}│{X}")
    print(f"{R}│{X}  {W}Device  :{X} {subprocess.getoutput('getprop ro.product.model 2>/dev/null') or '?'}")
    print(f"{R}│{X}  {W}Android :{X} {subprocess.getoutput('getprop ro.build.version.release 2>/dev/null') or '?'}")
    print(f"{R}│{X}  {W}Arch    :{X} {os.uname().machine}")
    root = f"{G}🟢 Yes{X}" if "uid=0" in subprocess.getoutput("su -c id 2>/dev/null") else f"{R}🔴 No{X}"
    print(f"{R}│{X}  {W}Root    :{X} {root}")
    net = f"{G}🟢 Online{X}" if os.system("ping -c1 -W1 google.com >/dev/null 2>&1")==0 else f"{R}🔴 Offline{X}"
    print(f"{R}│{X}  {W}Network :{X} {net}")
    print(f"{R}│{X}─────────────────────────────────────────{R}│{X}")
    print(f"{R}│{X}  {C}Tools   :{X} {len(state.get('installed',{}))} installed / {len(idx.get('packages',{}))} available")
    print(f"{R}│{X}  {C}Developer:{X} Masiyev Gülbala")
    print(f"{R}└─────────────────────────────────────────┘{X}")
# ═══════════════ UPDATE ═══════════════
def update_index():
    print("Updating package index...")
    try:
        with urllib.request.urlopen(BRATOS_INDEX_URL) as r:
            with open(BRATOS_INDEX,'w') as f: f.write(r.read().decode())
        print("Index updated successfully.")
    except Exception as e: print(f"Update failed: {e}")

# ═══════════════ SEARCH ═══════════════
def search_pkg(query):
    idx = load_index()
    if not idx.get("packages"): print("Run 'brat update' first."); return
    q = query.lower().strip(); found = 0
    for name, info in idx["packages"].items():
        desc = info.get('description','').lower()
        cat = info.get('category','').lower()
        if q in name.lower() or q in desc or q in cat:
            m = info.get('install_method','binary')
            tag = f" [{m}]" if m != 'binary' else ""
            print(f"  - {name}{tag} ({info.get('category','?')}): {info.get('description','')}")
            found += 1
    if not found: print(f"No packages matching '{query}'.")

# ═══════════════ GITHUB API ═══════════════
def get_github_arm64_url(repo):
    api = f"https://api.github.com/repos/{repo}/releases/latest"
    h = {"User-Agent": "BratOS"}; t = get_token()
    if t: h["Authorization"] = f"Bearer {t}"
    try:
        req = urllib.request.Request(api, headers=h)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        tag = data["tag_name"]
        for a in data.get("assets", []):
            n = a["name"].lower()
            if any(k in n for k in ["arm64","aarch64","android"]) and "darwin" not in n:
                return a["browser_download_url"], tag
        for a in data.get("assets", []):
            if "linux" in a["name"].lower() and "darwin" not in a["name"].lower():
                return a["browser_download_url"], tag
    except: pass
    return None, None

def download_and_extract(url, name, tmp):
    arch = os.path.join(tmp, "dl")
    urllib.request.urlretrieve(url, arch)
    if tarfile.is_tarfile(arch):
        with tarfile.open(arch, 'r:*') as tf: tf.extractall(tmp)
    elif zipfile.is_zipfile(arch):
        with zipfile.ZipFile(arch) as zf: zf.extractall(tmp)
    else:
        dest = os.path.join(tmp, name); shutil.copy(arch, dest)
        os.chmod(dest, 0o755); return dest
    for r, _, fs in os.walk(tmp):
        for f in fs:
            if f == name or name in f:
                p = os.path.join(r, f); os.chmod(p, 0o755); return p
    return None

# ═══════════════ INSTALL ═══════════════
def git_install(name, url, reqs=False, post=None):
    os.makedirs(TOOLS_DIR, exist_ok=True)
    dest = os.path.join(TOOLS_DIR, name)
    if os.path.exists(dest): shutil.rmtree(dest)
    print(f"  -> Cloning {url}...")
    if os.system(f"git clone --depth 1 {url} {dest} 2>&1") != 0:
        print("  ❌ Clone failed!"); return None
    if reqs:
        rf = os.path.join(dest, "requirements.txt")
        if os.path.exists(rf):
            print("  -> pip install -r requirements.txt...")
            os.system(f"cd {dest} && pip install -r requirements.txt 2>&1 | tail -3")
    if post:
        print(f"  -> {post}")
        os.system(f"cd {dest} && {post} 2>&1 | tail -5")
    # simlink
    bin_dir = f"{PREFIX}/bin"; os.makedirs(bin_dir, exist_ok=True)
    slink = f"{bin_dir}/{name}"
    if os.path.islink(slink) or os.path.exists(slink): os.remove(slink)
    # Geniş axtarış
    candidates = [
        f"{dest}/{name}.py", f"{dest}/{name}.sh", f"{dest}/{name}.rb",
        f"{dest}/{name}.pl", f"{dest}/{name}",
        f"{dest}/main.py", f"{dest}/run.py",
        f"{dest}/bin/{name}", f"{dest}/bin/{name}.sh", f"{dest}/bin/{name}.py",
        f"{dest}/src/{name}.py", f"{dest}/src/{name}.sh",
    ]
    for c in candidates:
        if os.path.isfile(c):
            os.symlink(c, slink); print(f"  -> {slink}"); return slink
    print(f"  ⚠️ Source: {dest}")
    return dest

def install_pkg(name):
    idx = load_index(); info = idx.get("packages", {}).get(name)
    if not info: print(f"Package '{name}' not found."); return
    m = info.get("install_method", "binary"); path = None; ver = "?"

    if m == "git":
        url = info.get("git_url", "")
        if not url: print("No git_url."); return
        print(f"Installing {name} via git...")
        path = git_install(name, url, info.get("requirements")=="true", info.get("post_install"))
        if not path: return
        ver = "git"
    else:
        repo = info.get("github_repo", "")
        if not repo: print("No github_repo."); return
        print(f"Resolving {name} from {repo}...")
        url, ver = get_github_arm64_url(repo)
        if not url:
            print("  ⚠️  No ARM64 binary. Please install manually")
            git_url = info.get("git_url", f"https://github.com/{repo}.git")
            ans = input("  Try git clone? (y/n): ").strip().lower()
            if ans == 'y':
                path = git_install(name, git_url, info.get("requirements")=="true", info.get("post_install"))
                if path:
                    ver = "git"
                    state = load_state()
                    state["installed"][name] = {
                        "version": ver, "path": path, "method": "git",
                        "date": datetime.now().strftime('%Y-%m-%d %H:%M')
                    }
                    save_state(state)
                    print(f"  ✅ Installed: {path}")
            else:
                print("  Skipped.")
            return
        print(f"  Downloading {name} {ver}...")
        tmp = tempfile.mkdtemp()
        try:
            bin = download_and_extract(url, name, tmp)
            if not bin: print("Binary not found."); shutil.rmtree(tmp); return
            dest = f"{PREFIX}/bin/{name}"
            shutil.copy(bin, dest); os.chmod(dest, 0o755); path = dest
        except Exception as e: print(f"Error: {e}"); shutil.rmtree(tmp); return
        shutil.rmtree(tmp)

    if path:
        state = load_state()
        state["installed"][name] = {
            "version": ver, "path": path, "method": m,
            "date": datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        save_state(state)
        print(f"  ✅ Installed: {path}")

# ═══════════════ RUN ═══════════════
def run_pkg(name, args=None):
    state = load_state()

    # Əgər quraşdırılıbsa, birbaşa işlət
    if is_installed(name, state):
        d = state["installed"][name]
        path = d.get("path", "")
        if path and os.path.exists(path):
            if os.path.isfile(path):
                cmd = [path] + (args if args else ["-h"])
                os.execvp(path, cmd)
            else:
                # Axtarış sırası
                search = [
                    f"{name}.py", f"{name}.sh", f"{name}.rb", f"{name}.pl",
                    "main.py", "run.py",
                    f"bin/{name}", f"bin/{name}.sh", f"bin/{name}.py",
                    f"src/{name}.py", f"src/{name}.sh",
                ]
                for f in search:
                    fp = os.path.join(path, f)
                    if os.path.isfile(fp):
                        if fp.endswith('.py'):
                            cmd = ["python3", fp] + (args if args else ["-h"])
                            os.execvp("python3", cmd)
                        else:
                            os.chmod(fp, 0o755)
                            cmd = [fp] + (args if args else ["-h"])
                            os.execvp(fp, cmd)
                print(f"Cannot find executable in {path}")
                print(f"Try: cd {path} && ls bin/")
            return

    # Quraşdırılmayıbsa – müvəqqəti endir işlət
    idx = load_index()
    info = idx.get("packages", {}).get(name)
    if not info: print(f"Package '{name}' not found."); return

    m = info.get("install_method", "binary")
    if m == "git":
        print(f"  ⚠️  '{name}' requires manual installation (git clone).")
        print(f"  Run: brat install {name}")
        return

    repo = info.get("github_repo", "")
    if not repo: print("No github_repo."); return

    print(f"Resolving {name} for temporary run...")
    url, ver = get_github_arm64_url(repo)
    if not url:
        print(f"  ⚠️  No ARM64 binary. Please install manually.")
        return

    print(f"Downloading {name} {ver}...")
    tmp = tempfile.mkdtemp()
    try:
        bin = download_and_extract(url, name, tmp)
        if bin:
            print(f"Running {name}...\n")
            cmd = [bin] + (args if args else ["-h"])
            os.execv(bin, cmd)
        else:
            print("Binary not found in archive.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        shutil.rmtree(tmp)

# ═══════════════ UNINSTALL ═══════════════
def uninstall_pkg(name):
    state = load_state()
    if not is_installed(name, state): print("Not installed."); return
    d = state["installed"][name]
    bp = f"{PREFIX}/bin/{name}"
    if os.path.islink(bp) or os.path.exists(bp): os.remove(bp); print(f"Removed {bp}")
    gp = f"{TOOLS_DIR}/{name}"
    if os.path.exists(gp): shutil.rmtree(gp); print(f"Removed {gp}")
    del state["installed"][name]
    save_state(state)
    print(f"'{name}' uninstalled.")

# ═══════════════ LIST ═══════════════
def list_pkgs():
    state = load_state()
    if not state.get("installed"): print("No packages installed."); return
    print("Installed packages:")
    for n, d in state["installed"].items():
        print(f"  {n:20} v{d.get('version','?'):10} [{d.get('method','?')}] {d.get('date','')}")

# ═══════════════ BROWSE ═══════════════
def browse():
    idx = load_index(); state = load_state()
    pkgs = idx.get("packages", {})
    if not pkgs: print("Run 'brat update' first."); return
    cats = {}
    for n, i in pkgs.items(): cats.setdefault(i.get("category", "other"), []).append(n)
    cl = sorted(cats)
    while True:
        print("\n" + "═" * 55)
        print("  📂 CATEGORIES")
        print("═" * 55)
        for i, c in enumerate(cl, 1): print(f"  {i:2}) {c:20} ({len(cats[c])} tools)")
        print(f"  {len(cl)+1:2}) 🔙 Exit")
        print("═" * 55)
        try:
            c = input("  Category: ").strip()
            if c in ['q','exit','b','back']: return
            c = int(c)
        except: return
        if c == len(cl)+1: return
        if 1 <= c <= len(cl):
            cat = cl[c-1]; tools = sorted(cats[cat])
            while True:
                print(f"\n  ─── {cat.upper()} ───")
                for i, t in enumerate(tools, 1):
                    inst = is_installed(t, state); st = "✅" if inst else "⬇️"
                    info = pkgs[t]; m = info.get('install_method','binary')
                    tag = " [git]" if m == "git" else ""
                    print(f"  {i:2}) {st} {t}{tag}")
                print(f"  {len(tools)+1:2}) 🔙 Back")
                try:
                    tc = input("  Tool: ").strip()
                    if tc in ['b','back']: break
                    tc = int(tc)
                except: break
                if tc == len(tools)+1: break
                if 1 <= tc <= len(tools):
                    tool = tools[tc-1]; info = pkgs[tool]
                    m = info.get('install_method','binary')
                    inst = is_installed(tool, state)
                    print(f"\n  🔧 {tool} ({m.upper()})")
                    if inst:
                        d = state["installed"][tool]
                        print(f"  ✅ Installed (v{d.get('version','?')})")
                        print(f"  1) Run (-h)  2) Reinstall  3) Uninstall  4) Back")
                        act = input("  Choice: ").strip()
                        if act == '1': run_pkg(tool); input("\n  Press Enter...")
                        elif act == '2': install_pkg(tool); state = load_state(); input("\n  Press Enter...")
                        elif act == '3': uninstall_pkg(tool); state = load_state(); input("\n  Press Enter...")
                    else:
                        print(f"  ⬇️ Not installed")
                        if m == "git":
                            print(f"  1) Install  2) Back")
                            act = input("  Choice: ").strip()
                            if act == '1': install_pkg(tool); state = load_state(); input("\n  Press Enter...")
                        else:
                            print(f"  1) Install  2) Run (temp)  3) Back")
                            act = input("  Choice: ").strip()
                            if act == '1': install_pkg(tool); state = load_state(); input("\n  Press Enter...")
                            elif act == '2': run_pkg(tool); input("\n  Press Enter...")

# ═══════════════ HELP ═══════════════
def help_msg():
    print(f"BratOS {BRATOS_VERSION}")
    print()
    print("Commands:")
    print("  doctor       Show device status")
    print("  update       Update package index from repo")
    print("  search <q>   Search packages (name, description, category)")
    print("  browse       Interactive category/tool browser")
    print("  install <p>  Install a package permanently")
    print("  run <p>      Run a package (installed or temporary)")
    print("  uninstall <p>Remove a package")
    print("  list         List installed packages")
    print("  help         This help")
    print("  version      Show version")

# ═══════════════ MAIN ═══════════════
def main():
    if len(sys.argv) < 2: help_msg(); return
    cmd = sys.argv[1].lower()
    if cmd == "doctor": doctor()
    elif cmd == "update": update_index()
    elif cmd == "search": search_pkg(sys.argv[2] if len(sys.argv)>2 else "")
    elif cmd == "browse": browse()
    elif cmd == "install": install_pkg(sys.argv[2] if len(sys.argv)>2 else "")
    elif cmd == "run": run_pkg(sys.argv[2] if len(sys.argv)>2 else "", sys.argv[3:] if len(sys.argv)>3 else None)
    elif cmd == "uninstall": uninstall_pkg(sys.argv[2] if len(sys.argv)>2 else "")
    elif cmd == "list": list_pkgs()
    elif cmd == "help": help_msg()
    elif cmd == "version": print(f"BratOS {BRATOS_VERSION}")
    else: print(f"Unknown: {cmd}")

if __name__ == "__main__":
    main()
