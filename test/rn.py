import glob
import os


def get_files_in_path(path: str, extensions: [str] = ["*.*"]):
    return sorted([f for ext in extensions for f in glob.glob(os.path.join(path, ext))])

p = "../temp/sequence"
files = get_files_in_path(p)

for file in files:
    old_name = os.path.splitext(os.path.basename(file))[0]
    new_name = "%s.obj" % old_name.split("_")[1]

    print(new_name)
    os.rename(file, os.path.join(p, new_name))