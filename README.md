# Road signs annotation
This python script enables convenient segmentation and annotation of polish road signs photos.

User can select part of the image with the road sign and label it. Selected area is saved as separate image in a
 directory corresponding to one of 5 classes:
 - `A` - waring sign,
 - `B` - prohibition sign,
 - `C` - mandatory sign,
 - `D` - information sign,
 - `X` - image with none of the above.
 
 Also there is a separate directory for photos that has been used to avoid
 processing the same image multiple times.
## Manual
Mouse:
- press `RMB` and move the mouse to draw square on the image,
- press `LMB` and move the mouse to move drawn square.

Keyboard:
- press `A`, `B`, `C`, `D` or `X` to save selected area to corresponding directory,
- press `>` to get next image and mark current image as used (move to separate directory),
- press `esc` to stop the script.

requirements (pip install ...): 
- `python3`,
- `opencv`,
- `numpy`.

running the script in cmd (path to directory containing raw images is required):

`python <path_to_main.py> <path_to_dir_with_imgs>`

example (windows):

`python .\main.py C:\Users\Filip\Downloads\dataset`

