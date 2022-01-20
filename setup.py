import sys
import subprocess
from pathlib import Path

venv_path = Path(__file__).parent/'venv'
activate_window = venv_path/'Scripts'/'activate_this.py'
activate_linux = venv_path/'bin'/'activate_this.py'
requirements = Path(__file__).parent/'requirements.txt'
usage_msg = "Usage: python setup.py (-nogui) <directory>"


def main():
    nogui = False
    if len(sys.argv) == 1:
        print(usage_msg)
        return
    for i, arg in enumerate(sys.argv):
        if arg == '-nogui':
            del sys.argv[i]
            nogui = True
        elif arg.startswith('-'):
            print(usage_msg)
            return

    run_path = " ".join(sys.argv[1:])
    if not venv_path.exists():
        subprocess.call(['python', '-m', 'pip', 'install', 'virtualenv'])
        subprocess.call(['virtualenv', venv_path])
        if activate_window.exists():
            exec(activate_window.open().read(), dict(__file__=activate_window))
            activate = activate_window
        else:
            exec(activate_linux.open().read(), dict(__file__=activate_linux))
            activate = activate_linux
        subprocess.call(['pip', 'install', '-r', requirements])
    else:
        if activate_window.exists():
            activate = activate_window
        else:
            activate = activate_linux
    with (Path(run_path)/'run.py').open('w+') as file:
        if nogui:
            file.write(f"""exec(open('{activate.as_posix()}').read(), dict(__file__='{activate.as_posix()}')) # noqa
import sys
sys.path.append('{Path(__file__).parent.as_posix()}')  # noqa
from main_nogui import main  # type: ignore
main()""")
        else:
            file.write(f"""exec(open('{activate.as_posix()}').read(), dict(__file__='{activate.as_posix()}')) # noqa
import sys
sys.path.append('{Path(__file__).parent.as_posix()}')  # noqa
from main import main  # type: ignore
main()""")


if __name__ == '__main__':
    main()
