import os
import subprocess
from django.shortcuts import render, redirect
from .forms import VideoForm
from .models import Video
from django.conf import settings

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            video_path = os.path.join(settings.MEDIA_ROOT, str(video.video_file))
            subtitle_path = os.path.join(settings.MEDIA_ROOT, f'{video.title}.srt')

            # Run FFmpeg command to extract subtitles
            command = f"ffmpeg -i {video_path} -map 0:s:0 {subtitle_path}"
            subprocess.run(command, shell=True)

            # Read the extracted subtitle file
            if os.path.exists(subtitle_path):
                with open(subtitle_path, 'r') as subtitle_file:
                    video.subtitle_file = subtitle_file.read()
                    video.save()

            return redirect('video_list')

    else:
        form = VideoForm()
    return render(request, 'video/upload.html', {'form': form})



def search_video(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        videos = Video.objects.all()
        for video in videos:
            if query.lower() in video.subtitle_file.lower():
                results.append({
                    'video': video,
                    'timestamp': get_timestamp(video.subtitle_file, query),
                })
    return render(request, 'video/search.html', {'results': results, 'query': query})

def get_timestamp(subtitle_text, query):
    subtitles_blocks = subtitle_text.strip().split('\n\n')
    for block in subtitles_blocks:
        lines = block.split('\n')
        if len(lines) < 3:
            continue

        time_range = lines[1]
        subtitle_content = " ".join(lines[2:])

        if query.lower() in subtitle_content.lower():
            start_time = time_range.split(' --> ')[0]
            return start_time.split(',')[0]  # Return only hh:mm:ss
    return None


def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video/list.html', {'videos': videos})


def video_detail(request, pk):
    video = Video.objects.get(pk=pk)
    return render(request, 'video/detail.html', {'video': video})
