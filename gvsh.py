#!/usr/bin/env python3
"""Robust remote shell for GhostVector dropbear (auth 'none', user=instance id)."""
import sys, time, paramiko

HOST = "instances.ctfcup.online"
USER = "lnt2um3q8qpgk11r"
PROMPT = "$ "  # ash default when no PS1? observed prompt is '$'

class Shell:
    def __init__(self):
        self.t = paramiko.Transport((HOST, 22))
        self.t.connect()
        self.t.auth_none(USER)
        self.ch = self.t.open_session()
        self.ch.get_pty(term="vt100", width=4096, height=100)
        self.ch.invoke_shell()
        self.ch.settimeout(5)
        time.sleep(1.0)
        self.drain()
        self.send("export PS1='XGVXx9q '\n")
        time.sleep(0.7)
        self.drain()

    def drain(self, until_idle=1.0, max_wait=60):
        buf = b""
        last = time.time()
        end = time.time() + max_wait
        while time.time() < end:
            try:
                d = self.ch.recv(131072)
            except Exception:
                d = b""
            if d:
                buf += d
                last = time.time()
                if buf.count(b"XGVXx9q") >= 1 and time.time() - last > 0.25:
                    # got a prompt; small extra wait then break
                    try:
                        self.ch.settimeout(0.5)
                        more = self.ch.recv(131072)
                        while more:
                            buf += more
                            more = self.ch.recv(131072)
                    except Exception:
                        pass
                    break
            else:
                if time.time() - last > until_idle:
                    break
        return buf.decode(errors="replace")

    def send(self, s):
        self.ch.sendall(s.encode(errors="replace"))

    def run(self, cmd, timeout=60):
        self.send(cmd + "\n")
        out = self.drain(max_wait=timeout)
        return out

def main():
    sh = Shell()
    cmds = sys.argv[1:]
    for c in cmds:
        print("=== " + c)
        print(sh.run(c))
    sh.ch.close(); sh.t.close()

if __name__ == "__main__":
    main()
