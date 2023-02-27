from src.utility.proc import run_proc


exitcode, out, err = run_proc(['./derdeutschlehrer', 'Halllo, das hier ist erin Tets!'])
print(f'output: "{out}"')
