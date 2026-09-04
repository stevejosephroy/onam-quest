import pygame
import os

_CACHE = {}
_SOUND_CACHE = {}

def get_sound(filename):
    path = os.path.join("assets", filename)
    if path in _SOUND_CACHE:
        return _SOUND_CACHE[path]
    try:
        snd = pygame.mixer.Sound(path)
        _SOUND_CACHE[path] = snd
        return snd
    except Exception as e:
        print(f"Error loading sound {path}: {e}")
        class DummySound:
            def play(self): pass
        return DummySound()

def get_image(filename, scale=None, colorkey=(0, 0, 0)):
    path = os.path.join("assets", filename)
    key = (path, scale)
    if key in _CACHE:
        return _CACHE[key]
    
    try:
        img = pygame.image.load(path).convert_alpha()
        
        if colorkey is not None:
            bg_color = img.get_at((0, 0))
            with pygame.PixelArray(img) as px:
                px.replace(bg_color, (0,0,0,0), distance=0.12)
                
        if scale is not None:
            img = pygame.transform.smoothscale(img, scale)
        _CACHE[key] = img
        return img
    except Exception as e:
        print(f"Error loading {path}: {e}")
        s = pygame.Surface(scale if scale else (50, 50), pygame.SRCALPHA)
        s.fill((255, 0, 255, 128))
        return s

def get_spritesheet(filename, frames_x, frames_y, scale_each=None, colorkey=(0, 0, 0)):
    sheet = get_image(filename, colorkey=colorkey)
    if sheet.get_size() == (50, 50): # Fallback hit
        return [sheet] * (frames_x * frames_y)

    w, h = sheet.get_size()
    cell_w = w // frames_x
    cell_h = h // frames_y
    
    frames = []
    for y in range(frames_y):
        for x in range(frames_x):
            # 1. Extract the mathematical cell
            cell_rect = pygame.Rect(x * cell_w, y * cell_h, cell_w, cell_h)
            cell = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA).convert_alpha()
            cell.blit(sheet, (0, 0), cell_rect)
            
            # 2. Find bounding box of non-black pixels in this cell
            min_x, max_x = cell_w, 0
            min_y, max_y = cell_h, 0
            has_content = False
            
            for cx in range(cell_w):
                for cy in range(cell_h):
                    r, g, b, _ = cell.get_at((cx, cy))
                    if r > 15 or g > 15 or b > 15:
                        has_content = True
                        if cx < min_x: min_x = cx
                        if cx > max_x: max_x = cx
                        if cy < min_y: min_y = cy
                        if cy > max_y: max_y = cy
                        
            if has_content and max_x > min_x and max_y > min_y:
                # 3. Crop tightly
                crop_w = max_x - min_x + 1
                crop_h = max_y - min_y + 1
                crop_rect = pygame.Rect(min_x, min_y, crop_w, crop_h)
                frame = pygame.Surface((crop_w, crop_h), pygame.SRCALPHA).convert_alpha()
                frame.blit(cell, (0, 0), crop_rect)
            else:
                frame = pygame.Surface(cell.get_size(), pygame.SRCALPHA).convert_alpha()
                frame.blit(cell, (0, 0))
                
            if colorkey is not None and sum(colorkey) >= 20:
                frame.set_colorkey(colorkey)
                
            if scale_each is not None:
                frame = pygame.transform.smoothscale(frame, scale_each)
            frames.append(frame)
            
    return frames
