import os
import shutil
import sys

__author__ = 'Nikhil'

import subprocess

outmode = 'mp4'
remover = False
accept_ext = 'mp4 mkv avi divx m4v mpeg mpg wmv'

ffmpeg_exe = "C:\\Users\\Nikhil\\local64\\bin-video\\ffmpeg.exe"
ffprobe_exe = "C:\\Users\\Nikhil\\local64\\bin-video\\ffprobe.exe"
video_codec = 'libx264'
video_type = 'h264'
audio_codec = 'libfdk_aac'
audio_type = 'aac'
crf = "18"
vbr = ''
threads = 1
additional_ffmpeg = '-preset veryfast -movflags +faststart'

outformat = 'mp4'
if outmode == 'mp4':
    outformat = 'mp4'
elif outmode == 'mkv':
    outformat = 'matroska'


def ffmpeg(*args, **kwargs):
    largs = [ffmpeg_exe, ]
    largs.extend(args)
    print(largs)
    return subprocess.check_output(largs, **kwargs).decode('utf-8')


formats = ""
if subprocess.check_output([ffmpeg_exe, '-formats'], stderr=subprocess.DEVNULL):
    formats = subprocess.check_output(([ffmpeg_exe, '-formats', '2'])).decode('utf-8')
else:
    exit(1)

if ('E mp4' in formats) and ('E matroska' in formats):
    print("You have the suitable formats")
else:
    print("You do not have both the mkv and mp4 formats...Exiting!")
    exit(1)

codecs = ffmpeg('-codecs', '2')

if video_codec in codecs:
    print("Check " + video_codec + " Audio Encoder ... OK")
else:
    print("Check " + video_codec + " Audio Encoder ... NOK")
    exit(1)

if audio_codec in codecs:
    print("Check " + audio_codec + " Audio Encoder ... OK")
else:
    print("Check " + audio_codec + " Audio Encoder ... NOK")
    exit(1)

print("Your FFMpeg is OK\nEntering File Processing")


def processFile(path, file):
    extension = os.path.splitext(file)[1].replace(".", "")
    filename = os.path.splitext(file)[0]

    if extension in accept_ext:
        print(file + " is an acceptable extension. Checking file...")
    else:
        print(extension)
        print(file + " is not an acceptable extension. Skipping...")
        return

    if ffprobe_exe:
        file_info = subprocess.check_output([ffprobe_exe, '-i', os.path.join(path, file)]).decode('utf-8')
    else:
        file_info = ffmpeg("-i", os.path.join(path, file), stderr=subprocess.DEVNULL)

    if 'Invalid data found' in file_info:
        print("File " + file + " is NOT A VIDEO FILE cannot be converted!")
        return

    encode_crf = []
    if "Video: " + video_type in file_info:
        vcodec = 'copy'
        print("Video is " + video_type + ", remuxing....")
    else:
        vcodec = video_codec
        if crf:
            encode_crf = ["-crf", "" + crf]
        print("Video is not " + video_type + ", converting...")

    encode_vbr = []
    if "Audio: " + audio_type in file_info:
        acodec = 'copy'
        print("Audio is " + audio_type + ", remuxing....")
    else:
        acodec = audio_codec
        if vbr:
            encode_vbr = ["-vbr", "" + vbr]
        print("Audio is not " + audio_type + ", converting...")

    if extension == outmode and vcodec == 'copy' and acodec == 'copy':
        print(file + " is already " + outmode + " and no conversion needed. Skipping...")
        return

    print(
        "Using video codec: " + vcodec + " audio codec: " + acodec + " and Container format " + outformat + " for\nFile: " + file + "\nStarting Conversion...")

    filename = filename.replace("XVID", video_type)
    filename = filename.replace("xvid", video_type)

    args = ['-i',os.path.join(path,file), '-y', '-f', outformat, '-acodec', acodec]
    if encode_vbr:
        args.extend(encode_vbr)
    args.extend(['-vcodec', vcodec])
    if encode_crf:
        args.extend(encode_crf)
    if additional_ffmpeg:
        args.extend(additional_ffmpeg.split(" "))
    if threads:
        args.extend(['-threads', str(threads)])
    args.append(os.path.join(path,filename + '.temp'))
    ffmpeg(*args)

    if remover:
        print("Deleting original file: " + file)
        os.remove(os.path.join(path, file))

    if outmode == extension:
        shutil.move(os.path.join(path,filename + ".temp"), os.path.join(path,filename + ".enc." + outmode))
        filename += ".enc"
    else:
        shutil.move(filename + ".temp", filename + "." + outmode)


def processDirectory(path):
    if os.path.isfile(os.path.join(path, ".noconvert")):
        return
    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        if os.path.isdir(filepath):
            processDirectory(filepath)
        elif os.path.isfile(filepath):
            processFile(path, file)


for arg in sys.argv[1:]:
    if os.path.isdir(arg):
        processDirectory(arg)
    elif os.path.isfile(arg):
        processFile(os.path.dirname(arg), os.path.basename(arg))
