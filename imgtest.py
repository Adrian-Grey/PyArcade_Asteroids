import os, sys
from PIL import Image

print(f"{os.getcwd()}")

for infile in sys.argv[1:]:
    if os.path.exists(infile):
        print("File exists")
    else: 
        print("File does not exist")
    a, b = os.path.split(infile)
    f, e = os.path.splitext(b)
    print(f"split filepath into {f} and {e}")
    outfile = f + ".jpg"
    print(f"outfile name is {outfile}")
    if infile != outfile:
        try:
            with Image.open(infile) as im:
                print("Image opened successfully")
                im.save(outfile)
        except OSError:
            print("cannot convert", infile)