#!/usr/bin/env python3
"""Upload a local file to the guest using only ash builtins (printf-based b64 decode)."""
import sys, time, base64
sys.path.insert(0, "/workspace")
from gvsh import Shell

def upload(sh,  bytes, remote: str, chunk=180):
    b64 = base64.b64encode(data).decode()
    sh.run(f"rm -f {remote}.b64 {remote}; : > {remote}.b64")
    for i in range(0, len(b64), chunk):
        part = b64[i:i+chunk]
        cmd = f'echo -n {part} >> {remote}.b64'
        sh.send(cmd + "\n")
        # don't wait for prompt each line; just pace
        time.sleep(0.05)
    # drain echo backlog
    sh.drain(max_wait=90)
    dec = r'''D=/tmp/d.sh
cat > $D <<'EOS'
d='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
tabx=0123456789abcdef
hexval(){ local c=$1 i=0 v=0
  while [ $i -lt 16 ]; do
    if [ "${tabx:$i:1}" = "$c" ]; then v=$((v*16+i)); fi
    i=$((i+1))
  done
  echo $v
}
# build value map via expansion loop over d string
in="$1"; out=""; acc=0; nbits=0
i=0; L=${#in}
while [ $i -lt $L ]; do
  c="${in:$i:1}"
  j=0; val=-1
  while [ $j -lt 64 ]; do
    if [ "${d:$j:1}" = "$c" ]; then val=$j; break; fi
    j=$((j+1))
  done
  if [ $val -ge 0 ]; then
    acc=$((acc*64+val)); nbits=$((nbits+6))
    if [ $nbits -ge 8 ]; then
      nbits=$((nbits-8))
      byte=$(( (acc >> nbits) & 255 ))
      printf '\\\\x%02x' $byte
    fi
  fi
  i=$((i+1))
done
EOS
chmod +x $D'''
    # simpler: write decoder with single-quote-safe heredoc via printf lines
    # We'll instead avoid heredoc: send decoder script as b64 too? chicken-egg.
    # Use ash arithmetic with character lookup done in shell is slow (12KB -> ~16k chars * 64 cmp = ok but slow).
    raise SystemExit("unused")

DECODER_LINES = [
"d='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='",
"in=$(cat \"$1\")",
"out=",
"i=0; L=${#in}",
"while [ $i -lt $L ]; do",
"  c=${in:$i:1}",
"  j=0; v=-1",
"  while [ $j -lt 64 ]; do",
"    if [ \"${d:$j:1}\" = \"$c\" ]; then v=$j; break; fi",
"    j=$((j+1))",
"  done",
"  out=\"$out$v\"",
"  i=$((i+1))",
"done",
"echo \"$out\"",
]

if __name__ == "__main__":
    path, remote = sys.argv[1], sys.argv[2]
    data = open(path, "rb").read()
    sh = Shell()
    b64 = base64.b64encode(data).decode()
    sh.run(f"rm -f {remote}.b64 {remote}; : > {remote}.b64")
    chunk = 200
    total = (len(b64)+chunk-1)//chunk
    for i in range(0, len(b64), chunk):
        sh.send(f"echo -n {b64[i:i+chunk]} >> {remote}.b64\n")
        if (i//chunk) % 25 == 24:
            sh.drain(max_wait=120)
    sh.drain(max_wait=120)
    print("uploaded b64 lines:", total)
    # verify size
    print(sh.run(f"cat {remote}.b64 | wc -c" if False else "wc -c {0}.b64 2>/dev/null || ls -la {0}.b64".format(remote)))
    sh.ch.close(); sh.t.close()
