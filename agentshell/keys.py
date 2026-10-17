"""
Interactive API key setup.
Reads providers from settings.py, asks for keys, saves to ~/.agentshell/.env.
Runs without any LLM — pure Python + getpass.
"""
import os
import getpass

from dotenv import load_dotenv, set_key

from settings import LLM_PROVIDERS, GLOBAL_DIR, ENV_FILE



def run_setup_keys() -> None:
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
    ENV_FILE.touch(mode=0o600, exist_ok=True)
    load_dotenv(ENV_FILE, override=True)

    print("=" * 50)
    print(" Agent Shell — API Key Setup")
    print("=" * 50)
    print("Press Enter to skip a provider.\n")

    changed = False

    for p in LLM_PROVIDERS:
        name, env_var, url = p["name"], p["env_var"], p["url"]
        current = os.getenv(env_var)

        if current:
            print(f"[{name}] key already set (...{current[-4:]})")
            ans = input("  overwrite? (y/N): ").strip().lower()
            if ans != "y":
                continue

        print(f"[{name}] get your key here: {url}")
        key = getpass.getpass(f"  enter {env_var} (hidden): ").strip()

        if not key:
            print("  skipped.\n")
            continue

        set_key(str(ENV_FILE), env_var, key)
        os.environ[env_var] = key
        print("  saved.\n")
        changed = True

    if changed:
        os.chmod(ENV_FILE, 0o600)
        print(f"Keys saved to: {ENV_FILE}")

    has_any = any(os.getenv(p["env_var"]) for p in LLM_PROVIDERS)
    if not has_any:
        print("\nNo API keys configured.")
        print("You can add them later with: agentsh setup-keys")
    else:
        print("Done. You can now run `agentsh`.")