import subprocess
import signal
import os
from typing import Tuple

def run_proc(cmd: list[str]) -> Tuple[int, str, str]:
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        out = p.communicate()[0].decode("utf-8")
        err = p.communicate()[1].decode("utf-8")

        """ capture pdflatex output """
        #pdflatex_output: list[str] = []
        #for line in p.stdout:
        #    print(line)
        #    pdflatex_output.append(line)

        """ wait for pdflatex to finish """
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print(f'pdflatex timed out.')
        print(out)
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)

    exitcode: int = p.returncode

    return exitcode, out, err