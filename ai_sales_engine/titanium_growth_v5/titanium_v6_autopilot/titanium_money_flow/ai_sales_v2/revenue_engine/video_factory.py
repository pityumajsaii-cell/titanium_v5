import os
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip

def create_short(text, output_name):
    # Egyszerű, de profi üzleti Shorts (1080x1920)
    bg = ColorClip(size=(1080, 1920), color=(0, 0, 50), duration=15)
    txt_clip = TextClip(text, fontsize=70, color='white', font='Arial', method='caption', size=(900, None))
    txt_clip = txt_clip.set_position('center').set_duration(15)
    
    video = CompositeVideoClip([bg, txt_clip])
    video.write_videofile(output_name, fps=24, codec="libx264")

# AI által generált téma (példa)
create_short("Hogyan spórol a Svájci vállalkozás AI-val? \n\n 1. Automata ügyfélszolgálat \n 2. 0-24 Lead generálás \n\n Kattints a linkre a profilban!", "shorts_v8.mp4")
