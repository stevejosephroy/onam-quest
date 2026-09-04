# ── Escape Pathalam — Global Configuration ──────────────────────────────────

SCREEN_W = 1024
SCREEN_H = 768
FPS = 60
TITLE = "Escape Pathalam — An Onam Adventure"

# ── Core palette ─────────────────────────────────────────────────────────────
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
GRAY        = (120, 120, 120)
RED         = (220, 30,  30)
DARK_RED    = (139, 0,   0)

# ── Onam festival warmth (Levels 1-4, boot, menu) ───────────────────────────
ONAM_DEEP     = (100, 40,  10)       # deep warm brown
ONAM_BROWN    = (139, 69,  19)       # saddle brown
ONAM_GOLD     = (218, 165, 32)       # warm gold
ONAM_LIGHT    = (255, 223, 120)      # light gold
ONAM_ORANGE   = (255, 140, 0)        # deep orange
ONAM_CREAM    = (255, 248, 230)      # warm cream
ONAM_LEAF     = (34,  120, 15)       # banana leaf green
ONAM_LEAF_DK  = (20,  75,  10)       # dark leaf green

# ── Celebration / petal palette ──────────────────────────────────────────────
GOLD         = (255, 215, 0)
ORANGE       = (255, 140, 0)
KERALA_GREEN = (0,   128, 0)
PETAL_PINK   = (255, 105, 180)
PETAL_YELLOW = (255, 255, 100)
PETAL_ORANGE = (255, 165, 0)
PETAL_RED    = (220, 20,  60)
PETAL_WHITE  = (255, 250, 250)
AMBER        = (255, 191, 0)

# Pookalam ring colors (outermost → innermost)
POOKALAM_COLORS = [
    (220, 40,  40),      # deep red
    (255, 100, 0),       # orange
    (255, 200, 0),       # golden
    (255, 255, 120),     # yellow
    (255, 130, 200),     # pink
    (160, 50,  220),     # violet
    (255, 250, 250),     # white (center)
]

# ── Pathalam underworld (Level 5) ───────────────────────────────────────────
PATH_SKY_TOP   = (15,  5,   30)     # near-black purple
PATH_SKY_BOT   = (40,  8,   8)      # dark blood red
PATH_GROUND    = (50,  30,  20)     # dark earth
PATH_GROUND_LT = (70,  45,  30)     # lighter earth
PATH_LAVA      = (255, 80,  0)      # lava orange
PATH_FIRE_RED  = (255, 30,  10)     # fire
PATH_FIRE_YEL  = (255, 200, 50)     # fire highlight
PATH_ROCK      = (65,  55,  50)     # dark gray rock
PATH_ROCK_LT   = (90,  80,  70)     # lighter rock
PATH_PURPLE    = (80,  20,  60)     # deep purple accent
PATH_SMOKE     = (50,  40,  45)     # smoke gray

# ── Maveli character ─────────────────────────────────────────────────────────
MAVELI_CROWN = (255, 215, 0)        # gold crown
MAVELI_SKIN  = (210, 170, 120)      # skin
MAVELI_DHOTI = (255, 250, 240)      # white cloth

# ── Sadya dish definitions ───────────────────────────────────────────────────
SADYA_DISHES = [
    ("Rice",     (255, 255, 230)),
    ("Sambar",   (200, 100, 20)),
    ("Avial",    (140, 180, 60)),
    ("Papadam",  (230, 200, 120)),
    ("Payasam",  (245, 225, 195)),
    ("Pickle",   (180, 40,  30)),
]

# ── Water / sky (Level 3) ───────────────────────────────────────────────────
SKY_TOP      = (135, 206, 235)      # light sky blue
SKY_BOTTOM   = (70,  130, 180)      # steel blue
WATER_DEEP   = (30,  80,  140)      # deep water
WATER_LIGHT  = (70,  160, 220)      # surface water
BOAT_BROWN   = (139, 90,  43)       # wooden boat
BOAT_GOLD    = (218, 175, 70)       # boat trim

# ── Warm lamp-lit (Level 4) ─────────────────────────────────────────────────
LAMP_BG_TOP  = (60,  20,  10)       # warm dark
LAMP_BG_BOT  = (100, 50,  20)       # warm brown
LAMP_FLAME   = (255, 180, 50)       # flame
LAMP_GLOW    = (255, 200, 100)      # glow
LAMP_BRONZE  = (180, 130, 60)       # bronze metal

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_NAME     = "segoe ui"
FONT_FALLBACK = "arial"
FONT_MONO     = "consolas"
FONT_SM  = 16
FONT_MD  = 22
FONT_LG  = 32
FONT_XL  = 48
FONT_TITLE = 64

# ── Timing ───────────────────────────────────────────────────────────────────
BOOT_LINE_DELAY   = 0.06
TYPEWRITER_SPEED  = 0.03
LEVEL3_BPM        = 120
LEVEL4_BPM        = 110
LEVEL5_TIME       = 60

# ── Level 5 runner ───────────────────────────────────────────────────────────
RUNNER_GROUND_Y   = 580          # ground level for runner
RUNNER_GRAVITY    = 1800         # px/s²
RUNNER_JUMP_VEL   = -620         # initial jump velocity
RUNNER_SPEED      = 320          # base scroll speed px/s
RUNNER_WIN_DIST   = 500         # meters to escape
RUNNER_MAX_HP     = 3
