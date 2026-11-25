#!/usr/bin/env python3
"""
QQS-Pro web page animations (data/*.gif), all 428 x 174 (2 x the printer's 214 x 87 animation box).

  print.gif  printing: she paints the flower (8 s), holds it (2 s); arm swings, nozzle dot blinks, "!" blinks
  heat.gif   M109 / M190: she holds still, "!" blinks, steam moves, empty canvas
  pause.gif  paused: still, flower half done, steam moves
  idle.gif   George's sleeping picture (tools/art/idle_sleep.png), the three Z's float up one after another

print / heat / pause are rendered from the firmware's own animation data (qqs_anim_data.cpp) with the same rules
as qqs::anim_draw() (via sim/animsim.py's helpers), so the page matches the printer.
Run: python3 tools/gen_web_anim.py   (needs ~/qqsp/fw and ~/qqsp/sim)
"""
import os, sys, math
import numpy as np, cv2
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data')
sys.path.insert(0, os.path.expanduser('~/qqsp/sim'))
import animsim as A

BG = (34, 34, 34)          # the page's card colour (#222)
OR = (255, 140, 40)        # #ff8c28
A.BG = BG
W, H = A.W, A.H            # 214 x 87
LOOP_DRAW, LOOP_HOLD, TICK_MS = 32, 8, 250


def fw_frame(tick, loop_pos, running, waiting):
    """qqs::anim_draw(full=true) on the host."""
    D = A.D
    p8 = 254 if loop_pos >= LOOP_DRAW else loop_pos * 254 // LOOP_DRAW
    img = Image.new('RGB', (W, H), BG)
    lv, b = A.B('qqs_anim_bg'); A.draw(img, 0, 0, lv, b, OR, BG)
    if (running or waiting) and tick % 12 >= 10:
        lv, b = A.B('qqs_anim_bang_mask'); A.draw(img, int(D['BANG_X']), int(D['BANG_Y']), lv, b, BG, BG)
    fl = np.where(A.ford <= p8, A.flv, 0); A.draw(img, int(D['FLOWER_X']), int(D['FLOWER_Y']), fl, 4, BG, OR)
    if 0 < p8 < 254 and (not running or not (tick & 1)):
        i = -1
        for k, (x, y, o) in enumerate(A.noz):
            if o <= p8: i = k
        if i >= 0:
            x, y, _ = A.noz[i]; A.fill(img, x - 2, y - 1, 5, 3, BG); A.fill(img, x - 1, y - 2, 3, 5, BG); A.fill(img, x, y, 1, 1, OR)
    for j in range(2):
        x0 = D['STEAM_X1'] if j else D['STEAM_X0']
        for y in range(int(D['STEAM_Y0']), int(D['STEAM_Y1'])):
            x = x0 + D['STEAM_AMP'] * math.sin(y / D['STEAM_PERIOD'] + tick * 1.3 + j * 0.8)
            A.fill(img, int(x) - 1, y, 2, 1, OR)
    f = [0, 1, 2, 1][tick & 3] if running else 0
    lv, b = A.B('qqs_anim_arm%d_mask' % f); A.draw(img, int(D['ARM_X']), int(D['ARM_Y']), lv, b, BG, BG)
    lv, b = A.B('qqs_anim_arm%d' % f); A.draw(img, int(D['ARM_X']), int(D['ARM_Y']), lv, b, OR, BG)
    return img


def up2(f):
    f = f if isinstance(f, Image.Image) else Image.fromarray(f)
    return f.resize((f.width * 2, f.height * 2), Image.NEAREST) if f.width == W else f


def save_gif(name, frames, ms):
    pal = [up2(f).convert('P', palette=Image.ADAPTIVE, colors=32) for f in frames]
    pal[0].save(os.path.join(OUT, name), save_all=True, append_images=pal[1:], duration=ms, loop=0, optimize=True, disposal=1)
    return os.path.getsize(os.path.join(OUT, name))


# ---- idle: George's picture at 214 x 87, Z's animated ----
SRC = os.path.join(HERE, 'art', 'idle_sleep.png')
raw = cv2.imread(SRC)[:, :, 2].astype(np.float32) / 255.0        # orange = red channel high, lines / background black
# The idle picture is rendered at 2 x (428 x 174): at 214 px its ~12 px lines (in 2025 px) wash out and thickening
# them breaks the thin orange strokes. The printer's frames are scaled 2 x with nearest neighbour to match.
LINE_GROW = 0
SCALE = 2
ink = cv2.erode(raw, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * LINE_GROW + 1, 2 * LINE_GROW + 1))) if LINE_GROW else raw
SH, SW = ink.shape
IW, IH = W * SCALE, H * SCALE
scale = min(IW / SW, IH / SH)
DW, DH = int(round(SW * scale)), int(round(SH * scale))
OX, OY = (IW - DW) // 2, (IH - DH) // 2

# the three Z's: orange blobs in the top middle (big, medium, small); found in the source, removed from the base
reg = np.zeros(ink.shape, bool); reg[60:330, 1080:1345] = True
lab, n = ndimage.label((raw > 0.5) & reg)
zs = []
for i, sl in enumerate(ndimage.find_objects(lab)):
    m = lab == i + 1
    if m.sum() > 1000: zs.append((sl[0].start, m))
zs.sort(key=lambda z: -z[0])                                       # lowest (small) first
assert len(zs) == 3, len(zs)
base = ink.copy()
for _, m in zs: base[ndimage.binary_dilation(m, iterations=6)] = 0.0   # with their dark outline


def down(full):
    small = cv2.resize(full, (DW, DH), interpolation=cv2.INTER_AREA)
    c = np.zeros((IH, IW), np.float32); c[OY:OY + DH, OX:OX + DW] = small
    return np.round(c * 15) / 15                                    # 16 levels, like the printer's 4 bpp art


def rgb(lv):
    f = lv[..., None]
    return (np.array(OR) * f + np.array(BG) * (1 - f)).astype(np.uint8)


def idle_frames():
    # 16 frames x 300 ms: Z1 (small) from frame 0, Z2 from 3, Z3 from 6; each rises while shown; all gone by 15
    win = [(0, 12), (3, 13), (6, 14)]
    rise_full = 26                                                   # source px over its whole window (~5 px at 428)
    frames = []
    for t in range(16):
        full = base.copy()
        for (y0, m), (a, b) in zip(zs, win):
            if a <= t < b:
                dy = -int(round(rise_full * (t - a) / max(b - a - 1, 1)))
                mm = np.roll(m, dy, axis=0)
                halo = ndimage.binary_dilation(mm, iterations=6)
                full[halo] = 0.0
                full[mm] = ink[m]
        frames.append(rgb(down(full)))
    return frames


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    sizes = {}
    # printing: loop_pos 0..39 (32 draw + 8 hold), tick runs on
    sizes['print.gif'] = save_gif('print.gif', [fw_frame(t, t % (LOOP_DRAW + LOOP_HOLD), True, False) for t in range(40)], TICK_MS)
    sizes['heat.gif'] = save_gif('heat.gif', [fw_frame(t, 0, False, True) for t in range(24)], TICK_MS)
    sizes['pause.gif'] = save_gif('pause.gif', [fw_frame(t, 20, False, False) for t in range(24)], TICK_MS)
    sizes['idle.gif'] = save_gif('idle.gif', [Image.fromarray(f) for f in idle_frames()], 300)
    for k, v in sizes.items(): print('%-10s %6d bytes' % (k, v))
    # previews x3 for checking
    for k in sizes:
        im = Image.open(os.path.join(OUT, k)); fr = []
        try:
            while True: fr.append(im.convert('RGB')); im.seek(im.tell() + 1)
        except EOFError: pass
        fr[0].save('/tmp/prev_' + k, save_all=True, append_images=fr[1:], duration=im.info.get('duration', 250), loop=0)
