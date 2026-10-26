"""Run localtunnel with automatic reconnection on disconnect."""

import subprocess
import time
import sys

def main() -> None:
    port = sys.argv[1] if len(sys.argv) > 1 else "8000"
    cmd = f"npx --yes localtunnel --port {port} --subdomain biotrace-demo"
    print(f"Menjalankan tunnel port {port}...", flush=True)
    while True:
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            if proc.stdout:
                for line in proc.stdout:
                    print(line, end="", flush=True)
            proc.wait()
        except KeyboardInterrupt:
            print("\nTunnel dihentikan.")
            break
        except Exception as e:
            print(f"Error ({e}), reconnecting...", flush=True)
        print("Tunnel terputus. Menghubungkan ulang dalam 2 detik...", flush=True)
        time.sleep(2)

if __name__ == "__main__":
    main()
