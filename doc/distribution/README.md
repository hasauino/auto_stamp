# Generating executables

- Used [PyInstaller](https://www.pyinstaller.org/) on windows to generate the `exe` file,  and on Ubuntu to generate the binary file.

#### PyInstaller

```bash
pyinstaller.exe --name AutoStamp --icon=icon.ico gui.py --hidden-import='pkg_resources.py2_warn' --hidden-import='PIL._tkinter_finder'
```



- Tool uses [pdf2image](https://pypi.org/project/pdf2image/) python module. This needs an application on the targeted os which converts pdg to image:
  - Windows users will have to install [poppler for Windows](http://blog.alivate.com.au/poppler-windows/), then add the `bin/` folder to [PATH](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/).
  - Most distros ship with `pdftoppm` and `pdftocairo`. If they are not installed, refer to your package manager to install `poppler-utils`



There is a `nsi` script which packages `poppler` and do the required things, look below.

# Window

- Used [NSIS](https://nsis.sourceforge.io/Main_Page), the `nsi` script is in this directory: [nsis_script.nsi](nsis_script.nsi)
- There is a plug in you need for setting `PATH` environment variable: [EnVar plug-in](https://nsis.sourceforge.io/EnVar_plug-in).
- Download `poppler` and put it in the same directory as the `nsi` script alongside the `AutoStamp.exe` (exe must be renamed).

