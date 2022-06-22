# Orders videos from manim per sequence.toml to make the final presentation

import toml
import os
import shutil
  
seq = toml.load("sequence.toml")
print(seq)

target_folder = seq['configs']['target_folder']
if not os.path.exists(target_folder):
    os.makedirs(target_folder)

scene_number = 0
for chapter in seq['chapters']:
    for k, v in chapter.items():
        video_path = os.path.join(seq['configs']['base_dir'], k, "480p15")
        
        src = [os.path.join(video_path, x + ".mp4") 
               for x in chapter[k]['scene_order']]
        
        dest = chapter[k]['scene_order']
        num_scenes = len(dest)     
        
        if seq['configs']['prepend_basename']:
            dest = [(chapter[k]['basename'] + x) for x in dest]
        
        filenums = [scene_number + x for x in range(num_scenes)]
        dest = [os.path.join(target_folder, f'{x:02}_{y}.mp4') 
                for x, y in zip(filenums, dest)]
        
        scene_number += num_scenes
        
        for x, y in zip(src, dest):
            if (os.path.exists(x)):
                shutil.copyfile(x, y)
        
        # print(src, dest)
