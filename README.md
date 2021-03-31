# Road signs annotation
## Description
This python script has been written to enable convenient segmentation and annotation of polish road signs photos.

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
- press `LMB` and move the mouse to draw square on the image,
- press `RMB` and move the mouse to move drawn square.

Keyboard:
- `A`, `B`, `C`, `D` or `X` - save selected area to the corresponding directory,
- `>` - get next image and mark current image as used (move it to the separate directory),
- `Space` - zoom in to the selected area (only "one level" of zoom works),
- `Backspace` - zoom out to the original image,
- `Esc` - stop the script.

Requirements: 
- `python3`,
- `opencv`,
- `numpy`.

Running the script in cmd (path to the directory containing raw images is required):

`python <path_to_main.py> <path_to_dir_with_imgs>`

Example (windows):

`python .\main.py C:\Users\Filip\Downloads\dataset`

