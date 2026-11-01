#!/usr/bin/env python3
"""Helper: run commands over an SSH shell channel (dropbear w/o exec support)."""
import sys, time, paramiko

HOST = "instances.ctfcup.online"
USER = sys.argv[1]
CMDS = sys.argv[2] if len(sys.argv) > 2 else "id; uname -a"

def main():
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(HOST, username=USER, password="", timeout=30,
                allow_agent=False, look_for_keys=False)
    ch = cli.invoke_shell(width=200, height=100)
    ch.settimeout(30)
    time.sleep(1.5)
    try:
        while True:
            ch.recv(65536)
    except Exception:
        pass
    marker = b"__GVDONE__"
    ch.sendall(CMDS.encode() + b"\necho __GVDONE__$?\n")
    buf = b""
    t0 = time.time()
    while time.time() - t0 < 180:
        try:
            data = ch.recv(65536)
        except Exception:
            continue
        if not 
            break
        buf += data
        if marker in buf:
            time.sleep(0.4)
            try:
                rest = ch.recv(65536)
                buf += rest
            except Exception:
                pass
            break
    out = buf.decode(errors="replace")
    print(out)
    cli.close()

if __name__ == "__main__":
    main()
