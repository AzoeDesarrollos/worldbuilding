import sys
from cx_Freeze import setup, Executable
import os
from datetime import datetime

now = ''.join([char for char in str(datetime.now()) if char not in [' ', '.', ':', '-']])

build_exe_options = {"packages": ["pygame", "pint"],
                     "excludes": ["tkinter", "http", "errno", "getop", "gettext", "glob", "http.client", "http.server",
                                  "imp", "io", "lib2to3", "multiprocessing", "zipimport", "xml.parsers",
                                  "pkg_resources", "pydoc", "pprint", "quopri", "runpy", "select", "selectors",
                                  "socket", "stringprep", "subprocess", "tarfile", "unittest", "xml",
                                  "importlib_metadata",

                                  "pygame.camera", "pygame.joystick", "pygame.mixer", "pygame.music", "pygame.cdrom",
                                  "pygame.examples", "pygame.scrap", "pygame.tests", "pygame.touch", "pygame.midi",
                                  "pygame.sndarray","pygame.surfarray","pygame.pixelcopy"

                                  ],
                     "include_files": [('data/favicon.png',) * 2],
                     "optimize": 2,
                     "build_exe": os.path.join(os.getcwd(), 'build', now)
                     }

base = None
if sys.platform == "win32":
    base = "Win32GUI"
icono = os.path.join(os.getcwd(), 'data', 'favicon.ico')
setup(
    name="Worldbuilding",
    version="1.0",
    description="An app for worldbuilders",
    options={"build_exe": build_exe_options},
    executables=[Executable(script="main.py", base=base, target_name="Worldbuilding", icon=icono)]
)
