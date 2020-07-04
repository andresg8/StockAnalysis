from modulefinder import ModuleFinder

finder = ModuleFinder()

finder.run_script("main.py")
mfound = []
for key, value in finder.modules.items():
    sw = key.split(".")[0]
    if sw not in mfound:
        mfound.append(sw)
    if (key.startswith("kivy") or key.startswith("yfinance") or
        key.startswith("openpyxl") or key.startswith("pandas") or
        key.startswith("urllib3") or key.startswith("matplotlib") or
        key.startswith("numpy")):
        continue
    else:
        print(key, value)
