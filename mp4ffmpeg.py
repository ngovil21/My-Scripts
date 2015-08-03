import os
import sys
import re
import shutil
import subprocess

__author__ = 'Nikhil'


outmode = 'mp4'
remover = True
accept_ext = 'mp4 mkv avi divx m4v mpeg mpg wmv'

ffmpeg_exe = "C:\\Users\\Nikhil\\local64\\bin-video\\ffmpeg.exe"
ffprobe_exe = "C:\\Users\\Nikhil\\local64\\bin-video\\ffprobe.exe"
mkvextract_exe = "C:\\Users\\Nikhil\\local64\\bin-video\\mkvextract.exe"
video_codec = 'libx264'
video_type = 'h264'
audio_codec = 'libfdk_aac'
audio_type = 'aac'
crf = "18"
vbr = ''
extract_subtitle = True
subtitle_languages = "en eng english"
threads = 0
additional_ffmpeg = '-preset veryfast -movflags +faststart'

outformat = 'mp4'
if outmode == 'mp4':
    outformat = 'mp4'
elif outmode == 'mkv':
    outformat = 'matroska'


def ffmpeg(*args, **kwargs):
    largs = [ffmpeg_exe, ]
    largs.extend(args)
    return subprocess.check_output(largs, **kwargs).decode('utf-8')


formats = ""
if subprocess.getoutput(ffmpeg_exe + ' -formats'):
    formats = subprocess.getoutput(ffmpeg_exe + ' -formats 2')
else:
    exit(1)

if ('E mp4' in formats) and ('E matroska' in formats):
    print("You have the suitable formats")
else:
    print("You do not have both the mkv and mp4 formats...Exiting!")
    exit(1)

codecs = subprocess.getoutput(ffmpeg_exe + ' -codecs 2')

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

print("Your FFMpeg is OK\nEntering File Processing\n")


def processFile(path, file):
    extension = os.path.splitext(file)[1].replace(".", "")
    filename = os.path.splitext(file)[0]

    if extension in accept_ext:
        print(file + " is an acceptable extension. Checking file...")
    else:
        print(file + " is not an acceptable extension. Skipping...")
        return

    if ffprobe_exe:
        file_info = subprocess.getoutput('"' + ffprobe_exe + '"' + " " + '"' + os.path.join(path, file) + '"')
    else:
        file_info = ffmpeg("-i", os.path.join(path, file), stderr=subprocess.DEVNULL)

    if 'Invalid data found' in file_info:
        print("File " + file + " is NOT A VIDEO FILE cannot be converted!")
        return

    encode_crf = []
    if file_info.find("Video: " + video_type) != -1:
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
        "Using video codec: " + vcodec + " audio codec: " + acodec + " and Container format " + outformat + " for\nFile: " + file + "\nStarting Conversion...\n")

    filename = filename.replace("XVID", video_type)
    filename = filename.replace("xvid", video_type)

    try:
        args = ['-i', os.path.join(path, file), '-y', '-f', outformat, '-acodec', acodec]
        if encode_vbr:
            args.extend(encode_vbr)
        args.extend(['-vcodec', vcodec])
        if encode_crf:
            args.extend(encode_crf)
        if additional_ffmpeg:
            args.extend(additional_ffmpeg.split(" "))
        if threads:
            args.extend(['-threads', str(threads)])
        args.append(os.path.join(path, filename + '.temp'))
        ffmpeg(*args)
        print("")
    except Exception as e:
        print("Error: %s" % e)
        print("Removing temp file and skipping file")
        if os.path.isfile(os.path.join(path, filename + '.temp')):
            os.remove(os.path.join(path, filename + '.temp'))
        return

    if extract_subtitle and (file_info.find("Subtitle:") != -1):
        print("Extracting First Subtitle")
        matches = re.finditer("Stream #(\d+):(\d+)\((\w+)\): Subtitle: (.*)", file_info)
        for m in matches:
            if m.group(3) not in subtitle_languages.split(" "):
                continue
            try:
                if 'subrip' in m.group(4):
                    sub_format = 'copy'
                    sub_ext = '.srt'
                if 'hdmv_pgs' in m.group(4):
                    subprocess.check_output([mkvextract_exe, 'tracks', os.path.join(path, file),
                                             m.group(2) + ':' + os.path.join(path, filename + '.' + m.group(
                                                 3) + '.' + m.group(2) + '.sup')])
                    continue
                else:
                    sub_format = '.srt'
                    sub_ext = '.srt'
                ffmpeg("-i", os.path.join(path, file), '-y', '-map', m.group(1) + ':' + m.group(2), '-c:s:0',
                       sub_format,
                       os.path.join(path, filename + '.' + m.group(3) + '.' + m.group(2) + sub_ext))
                print("")
            except Exception as e:
                print("Error: %s" % e)
                print("Deleting subtitle.")
                if os.path.isfile(os.path.join(path, filename + '.' + m.group(3) + '.' + m.group(2) + sub_ext)):
                    os.remove(os.path.join(path, filename + '.' + m.group(3) + '.' + m.group(2) + sub_ext))

    if remover:
        print("Deleting original file: " + file)
        os.remove(os.path.join(path, file))

    if outmode == extension:
        shutil.move(os.path.join(path, filename + ".temp"), os.path.join(path, filename + ".enc." + outmode))
        filename += ".enc"
    else:
        shutil.move(os.path.join(path, filename + ".temp"), os.path.join(path, filename + "." + outmode))


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
