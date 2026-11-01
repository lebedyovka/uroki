#!/usr/bin/env python3
"""Interactive-ish remote runner for the GhostVector dropbear instance.
Auth: 'none' method works with username = instance id."""
import sys, time, paramiko

HOST = "instances.ctfcup.online"
USER = "lnt2um3q8qpgk11r"

def run(cmds, wait=2.0, total=120):
    t = paramiko.Transport((HOST, 22))
    t.connect()
    t.auth_none(USER)
    ch = t.open_session()
    ch.get_pty(term="vt100", width=200, height=50)
    ch.invoke_shell()
    ch.settimeout(10)
    def drain():
        buf = b""
        end = time.time() + 2
        while time.time() < end:
            try:
                d = ch.recv(65536)
            except Exception:
                break
            if not d:
                break
            buf += d
        return buf
    time.sleep(1.0); drain()
    outputs = []
    if isinstance(cmds, str):
        cmds = [cmds]
    for c in cmds:
        ch.sendall((c + "\n").encode())
        time.sleep(wait)
        outputs.append("=== " + c + "\n" + drain().decode(errors="replace"))
    ch.close(); t.close()
    return "\n".join(outputs)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--wait", type=float, default=2.0)
    ap.add_argument("cmds", nargs="+")
    a = ap.parse_args()
    print(run(a.cmds, wait=a.wait))
