#!/usr/bin/env python3
"""Observe memleak restoring a privately mapped ELF; never execute that ELF."""

import ctypes
import hashlib
import json
import mmap
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time


# Exact Ubuntu libc from the incident, checked offline against its build ID.
LIBC_SHA256 = "de259f5276c4a991f78bf87225d6b40e56edbffe0dcbc0ffca36ec7fe30f3f77"
MMAP_OFFSET = 0x1252F0
ORIGINAL = bytes.fromhex("f3 0f 1e fa 41 f7 c1 ff 0f 00 00 75 33 55 48 89")
HOOK = bytes.fromhex("e9 8b 44 7b fe")


def check_libc(data):
    if hashlib.sha256(data).hexdigest() != LIBC_SHA256:
        raise RuntimeError("Different libc build; stop and report its SHA256.")
    if data[MMAP_OFFSET:MMAP_OFFSET + len(ORIGINAL)] != ORIGINAL:
        raise RuntimeError("Unexpected mmap entry; no probes installed.")


def stop_child(child):
    for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGKILL):
        if child.poll() is not None:
            return
        child.send_signal(signum)
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            continue
        return
    raise RuntimeError("Test memleak child did not exit; inspect its PID.")


def main():
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise RuntimeError("Run inside the original Linux x86_64 container.")
    tool = sys.argv[1] if len(sys.argv) == 2 else shutil.which("memleak-bpfcc")
    if not tool or len(sys.argv) > 2:
        raise RuntimeError("Usage: python3 verify-uprobe-restore.py /usr/sbin/memleak")
    tool = str(Path(tool).resolve(strict=True))
    source = Path("/usr/lib/x86_64-linux-gnu/libc.so.6")
    data = source.read_bytes()
    print("libc SHA256:", hashlib.sha256(data).hexdigest(), flush=True)
    check_libc(data)

    # Some libbpf-tools releases truncate -O to 31 bytes.
    directory = Path(tempfile.mkdtemp(prefix="ur-", dir="/tmp"))
    private = directory / "c.so"
    if len(os.fsencode(private)) > 31:
        raise RuntimeError("Private ELF path exceeds memleak's 31-byte limit.")
    shutil.copyfile(source, private)
    source_id = (source.stat().st_dev, source.stat().st_ino)
    private_id = (private.stat().st_dev, private.stat().st_ino)
    if source_id == private_id:
        raise RuntimeError("Copy shares the source inode; refusing to proceed.")
    check_libc(private.read_bytes())
    print("Evidence directory:", directory, flush=True)
    print("Source/copy device+inode:", source_id, private_id, flush=True)

    # These two mappings are data specimens. Neither is loaded or executed.
    with private.open("rb") as stream:
        control = mmap.mmap(stream.fileno(), 0, flags=mmap.MAP_PRIVATE,
                            prot=mmap.PROT_READ | mmap.PROT_EXEC)
        patched = mmap.mmap(stream.fileno(), 0, flags=mmap.MAP_PRIVATE,
                            prot=mmap.PROT_READ | mmap.PROT_WRITE)
    patched[MMAP_OFFSET:MMAP_OFFSET + len(HOOK)] = HOOK
    address = ctypes.addressof(ctypes.c_char.from_buffer(patched))
    mprotect = ctypes.CDLL(None, use_errno=True).mprotect
    mprotect.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
    mprotect.restype = ctypes.c_int
    if mprotect(address, len(patched), mmap.PROT_READ | mmap.PROT_EXEC):
        raise OSError(ctypes.get_errno(), "mprotect(RX) failed")

    maps = [line for line in Path("/proc/self/maps").read_text().splitlines()
            if str(private) in line]
    if len(maps) != 2 or any(line.split()[1] != "r-xp" for line in maps):
        raise RuntimeError("Expected two private RX mappings; no probes installed.")
    (directory / "maps.txt").write_text("\n".join(maps) + "\n")
    command = [tool, "-p", str(os.getpid()), "-O", str(private), "1", "2"]
    report = {"kernel": platform.release(), "pid": os.getpid(),
              "source_inode": source_id, "copy_inode": private_id,
              "argv": command, "observations": []}
    print("Command:", " ".join(command), flush=True)

    def read_entries():
        end = MMAP_OFFSET + len(ORIGINAL)
        return bytes(control[MMAP_OFFSET:end]), bytes(patched[MMAP_OFFSET:end])

    def record(label, entries):
        observation = {"phase": label, "time": time.time(),
                       "control": entries[0].hex(" "),
                       "patched": entries[1].hex(" ")}
        report["observations"].append(observation)
        print(f"{label:6} control: {observation['control']}", flush=True)
        print(f"{label:6} patched: {observation['patched']}", flush=True)

    previous = read_entries()
    record("before", previous)
    seen_cc = False
    timed_out = False
    with (directory / "memleak.log").open("w") as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 60
            while child.poll() is None:
                current = read_entries()
                if current != previous:
                    record("during", current)
                    previous = current
                seen_cc |= current[1] == b"\xcc" + HOOK[1:] + ORIGINAL[5:]
                if time.monotonic() >= deadline:
                    timed_out = True
                    break
                time.sleep(0.02)
        finally:
            stop_child(child)
    after = read_entries()
    record("after", after)
    disk_unchanged = private.read_bytes() == data
    expected_damage = ORIGINAL[:1] + HOOK[1:] + ORIGINAL[5:]
    reproduced = (seen_cc and not timed_out and child.returncode == 0
                  and disk_unchanged and after == (ORIGINAL, expected_damage))
    report.update(exit_code=child.returncode, timed_out=timed_out,
                  observed_cc=seen_cc, disk_unchanged=disk_unchanged,
                  result="REPRODUCED" if reproduced else "INCONCLUSIVE")
    (directory / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Result:", report["result"], flush=True)
    print("Memleak log:", directory / "memleak.log", flush=True)
    print("This tests the restore mechanism, not the historical incident.", flush=True)
    control.close()
    patched.close()
    return 0 if reproduced else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError) as error:
        sys.exit(str(error))
