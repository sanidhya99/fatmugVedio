import os
import subprocess
from django.shortcuts import render, redirect
from .forms import VideoForm
from .models import Video
from django.conf import settings

def upload_video(request):
    error_message = None  # Initialize error_message for both GET and POST requests
    
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()

            # Paths to video and subtitle files
            video_path = os.path.join(settings.MEDIA_ROOT, str(video.video_file))
            print(f'videofile: {video_path}')
            subtitle_path = os.path.join(settings.MEDIA_ROOT, f'{video.title}.srt')

            # Ensure the directory for the subtitles exists
            os.makedirs(os.path.dirname(subtitle_path), exist_ok=True)

            # Convert video to .webm if needed
            if not video_path.endswith('.webm'):
                webm_video_path = os.path.join(settings.MEDIA_ROOT,f'{video.title}.webm')

                # Correct FFmpeg command to convert video to .webm
                convert_command = f"ffmpeg -i {video_path} -c:v libvpx-vp9 -c:a libopus {webm_video_path}"

                try:
                    # Run the conversion command
                    print("FFmpeg Conversion started..........")
                    result = subprocess.run(convert_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    if os.path.exists(webm_video_path):
                        print(f"Conversion successful: {webm_video_path}")
                        video_path = webm_video_path  # Update video_path for subtitle extraction
                    else:
                        print(f"Conversion failed, file not created: {webm_video_path}")
                        error_message = "Video conversion failed"
                except Exception as e:
                    print(f"An error occurred while converting to .webm: {e}")
                    error_message = "An error occurred during video conversion"

            # FFmpeg command to extract subtitles
            command = f"ffmpeg -i {video_path} -map 0:s:0 {subtitle_path}"

            try:
                # Run the FFmpeg command to extract subtitles
                print("Subtitle extracting started.........")
                result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if result.returncode == 0 and os.path.exists(subtitle_path):
                    # Read the extracted subtitle file
                    print("Subtitles writing started.........")
                    with open(subtitle_path, 'r') as subtitle_file:
                        video.subtitle_file = subtitle_file.read()
                        video.save()
                else:
                    print(f"Error extracting subtitles: {result.stderr.decode('utf-8')}")
            except Exception as e:
                print(f"An error occurred while extracting subtitles: {e}")
                error_message = "Subtitle extraction failed"

            if error_message:
                return render(request, 'video/upload.html', {'form': form, 'error_message': error_message})

            return redirect('video_list')

    else:
        form = VideoForm()

    return render(request, 'video/upload.html', {'form': form, 'error_message': error_message})



from django.shortcuts import redirect

def search_video(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        videos = Video.objects.all()
        for video in videos:
            if query.lower() in video.subtitle_file.lower():
                timestamp, subtitle_snippet = get_timestamp_and_subtitle(video.subtitle_file, query)
                
                if timestamp:
                    results.append({
                        'video': video,
                        'timestamp': timestamp
                    })
    
    return render(request, 'video/search.html', {'query': query, 'results': results})



def get_timestamp_and_subtitle(subtitle_text, query):
    subtitles_blocks = subtitle_text.strip().split('\n\n')
    for block in subtitles_blocks:
        lines = block.split('\n')
        if len(lines) < 3:
            continue

        time_range = lines[1]
        subtitle_content = " ".join(lines[2:])

        if query.lower() in subtitle_content.lower():
            start_time = time_range.split(' --> ')[0]
            return start_time.split(',')[0], subtitle_content
    return None, None



def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video/list.html', {'videos': videos})


def video_detail(request, pk):
    video = Video.objects.get(pk=pk).title
    timestamp = request.GET.get('timestamp', '00:00:00')  # Default timestamp to 00:00:00 if not provided
    return render(request, 'video/detail.html', {'video': f'http://127.0.0.1:9000/{video}.webm', 'timestamp': timestamp})
