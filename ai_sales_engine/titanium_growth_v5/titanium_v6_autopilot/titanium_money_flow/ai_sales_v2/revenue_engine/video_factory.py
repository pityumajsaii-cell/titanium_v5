import sys
from moviepy import ColorClip, TextClip, CompositeVideoClip

def create_short(text, output_name):
    # Modern Shorts méret (1080x1920)
    bg = ColorClip(size=(1080, 1920), color=(0, 0, 50), duration=10)
    
    # Szöveg klip az új szintaktikával
    txt_clip = TextClip(
        text=text,
        font_size=70,
        color='white',
        method='caption',
        size=(900, None)
    ).with_duration(10).with_position('center')

    video = CompositeVideoClip([bg, txt_clip])
    video.write_videofile(output_name, fps=24, codec="libx264")

if __name__ == "__main__":
    content = sys.argv[1] if len(sys.argv) > 1 else "Titanium V9 Online"
    out = sys.argv[2] if len(sys.argv) > 2 else "output.mp4"
    create_short(content, out)
