import shutil
import glob
import os
src = r'C:\Users\LENOVO\Desktop\Python\Voice\Voice\Images'
dst = r'C:\Users\LENOVO\Desktop\Python\Voice\Voice\static\images'
os.makedirs(dst, exist_ok=True)
files = glob.glob(os.path.join(src, '*.png'))
for f in files:
    shutil.copy(f, dst)
print(f'copied {len(files)} png files')
