"""Generate uml_final.png — a UML class diagram for pawpal_system.py."""
from PIL import Image, ImageDraw, ImageFont

# ── Colours ──────────────────────────────────────────────────────────────────
BG          = "#FAFAFA"
BOX_FILL    = "#EAF4FB"
BOX_BORDER  = "#2980B9"
HEADER_FILL = "#2980B9"
HEADER_TEXT = "#FFFFFF"
BODY_TEXT   = "#1A1A2E"
LINE_COLOR  = "#555555"
ARROW_COLOR = "#2C3E50"
NOTE_FILL   = "#FFF9C4"
NOTE_BORDER = "#F9A825"

W, H = 1200, 980
img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

try:
    font_head  = ImageFont.truetype("arial.ttf", 15)
    font_body  = ImageFont.truetype("arial.ttf", 13)
    font_small = ImageFont.truetype("arial.ttf", 11)
    font_title = ImageFont.truetype("arialbd.ttf", 20)
except OSError:
    font_head  = ImageFont.load_default()
    font_body  = font_head
    font_small = font_head
    font_title = font_head

# ── Helper: draw a UML class box ─────────────────────────────────────────────
def class_box(x, y, name, attributes, methods, w=310):
    line_h = 20
    attr_h = max(len(attributes), 1) * line_h + 10
    meth_h = max(len(methods), 1)    * line_h + 10
    total_h = 34 + attr_h + meth_h

    # Outer border
    draw.rectangle([x, y, x + w, y + total_h], fill=BOX_FILL, outline=BOX_BORDER, width=2)

    # Header
    draw.rectangle([x, y, x + w, y + 34], fill=HEADER_FILL, outline=BOX_BORDER, width=2)
    draw.text((x + w // 2, y + 9), f"«dataclass»", font=font_small,
              fill="#CCE8F4", anchor="mm")
    draw.text((x + w // 2, y + 24), name, font=font_head,
              fill=HEADER_TEXT, anchor="mm")

    # Attributes section
    ay = y + 34
    draw.line([(x, ay), (x + w, ay)], fill=BOX_BORDER, width=1)
    for i, attr in enumerate(attributes):
        draw.text((x + 8, ay + 5 + i * line_h), attr, font=font_body, fill=BODY_TEXT)

    # Methods section
    my = ay + attr_h
    draw.line([(x, my), (x + w, my)], fill=BOX_BORDER, width=1)
    for i, meth in enumerate(methods):
        draw.text((x + 8, my + 5 + i * line_h), meth, font=font_body, fill="#1A6696")

    return x, y, x + w, y + total_h   # bbox

def mid_bottom(bbox): return ((bbox[0] + bbox[2]) // 2, bbox[3])
def mid_top(bbox):    return ((bbox[0] + bbox[2]) // 2, bbox[1])
def mid_right(bbox):  return (bbox[2], (bbox[1] + bbox[3]) // 2)
def mid_left(bbox):   return (bbox[0], (bbox[1] + bbox[3]) // 2)

def arrow(p1, p2, label=""):
    draw.line([p1, p2], fill=ARROW_COLOR, width=2)
    # arrowhead
    import math
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy) or 1
    ux, uy = dx / length, dy / length
    size = 10
    left  = (int(p2[0] - size * ux + size * 0.5 * uy),
              int(p2[1] - size * uy - size * 0.5 * ux))
    right = (int(p2[0] - size * ux - size * 0.5 * uy),
              int(p2[1] - size * uy + size * 0.5 * ux))
    draw.polygon([p2, left, right], fill=ARROW_COLOR)
    if label:
        mx, my = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
        draw.text((mx + 5, my - 14), label, font=font_small, fill=LINE_COLOR)

def dashed_arrow(p1, p2, label=""):
    import math
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy) or 1
    segments = int(length / 10)
    for i in range(0, segments, 2):
        t1 = i / segments
        t2 = min((i + 1) / segments, 1)
        draw.line(
            [(int(p1[0] + t1 * dx), int(p1[1] + t1 * dy)),
             (int(p1[0] + t2 * dx), int(p1[1] + t2 * dy))],
            fill=LINE_COLOR, width=2
        )
    ux, uy = dx / length, dy / length
    size = 10
    left  = (int(p2[0] - size * ux + size * 0.5 * uy),
              int(p2[1] - size * uy - size * 0.5 * ux))
    right = (int(p2[0] - size * ux - size * 0.5 * uy),
              int(p2[1] - size * uy + size * 0.5 * ux))
    draw.polygon([p2, left, right], fill=LINE_COLOR)
    if label:
        mx, my = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
        draw.text((mx + 5, my - 14), label, font=font_small, fill=LINE_COLOR)

# ── Title ─────────────────────────────────────────────────────────────────────
draw.text((W // 2, 28), "PawPal+ — Final UML Class Diagram", font=font_title,
          fill=BODY_TEXT, anchor="mm")
draw.text((W // 2, 50), "pawpal_system.py", font=font_small,
          fill="#888888", anchor="mm")

# ── Class boxes ───────────────────────────────────────────────────────────────

# Owner  (top-left)
owner_bb = class_box(
    40, 75,
    "Owner",
    ["+ name: str", "+ available_mins: int"],
    [],
)

# Pet  (top-right)
pet_bb = class_box(
    840, 75,
    "Pet",
    ["+ name: str", "+ species: str", "+ age: int"],
    [],
)

# CareTask  (middle)
task_bb = class_box(
    420, 75,
    "CareTask",
    [
        "+ title: str",
        "+ duration_mins: int",
        "+ priority: str",
        "+ preferred_time: str | None",
        "+ start_time: str | None",
        "+ completed: bool = False",
        "+ frequency: str | None",
        "+ pet_name: str | None",
    ],
    ["+ priority_value() -> int"],
    w=340,
)

# Scheduler  (bottom-left / centre)
sched_bb = class_box(
    40, 460,
    "Scheduler",
    ["+ owner: Owner", "+ pet: Pet", "+ tasks: list[CareTask]"],
    [
        "+ add_task(task: CareTask) -> None",
        "+ build_plan() -> DailyPlan",
        "+ sort_by_time() -> list[CareTask]",
        "+ filter_tasks(...) -> list[CareTask]",
        "+ mark_task_complete(task) -> CareTask | None",
        "+ detect_conflicts() -> list[str]",
    ],
    w=400,
)

# DailyPlan  (bottom-right)
plan_bb = class_box(
    700, 460,
    "DailyPlan",
    ["+ scheduled: list[CareTask]", "+ skipped: list[CareTask]"],
    ["+ explain() -> str"],
    w=340,
)

# PRIORITY_MAP note
nx, ny = 860, 300
draw.rectangle([nx, ny, nx + 270, ny + 60], fill=NOTE_FILL, outline=NOTE_BORDER, width=2)
draw.text((nx + 8, ny + 8),  "PRIORITY_MAP (module-level)",   font=font_small, fill="#555")
draw.text((nx + 8, ny + 26), '{"low": 1, "medium": 2, "high": 3}', font=font_small, fill=BODY_TEXT)
draw.text((nx + 8, ny + 44), "used by CareTask.priority_value()",  font=font_small, fill="#888")

# ── Relationships ─────────────────────────────────────────────────────────────

# Scheduler --> Owner  (uses / association)
arrow(mid_left(sched_bb), mid_bottom(owner_bb), "uses")

# Scheduler --> Pet  (uses / association)
p1 = (sched_bb[2], sched_bb[1] + 40)
p2 = (pet_bb[0],   pet_bb[3] - 20)
arrow(p1, p2, "uses")

# Scheduler --> CareTask  (aggregates 0..*)
p1 = ((sched_bb[0] + sched_bb[2]) // 2, sched_bb[1])
p2 = (task_bb[0] + 60, task_bb[3])
arrow(p1, p2, "0..*")

# Scheduler ..> DailyPlan  (creates / dashed)
dashed_arrow(mid_right(sched_bb), mid_left(plan_bb), "creates")

# DailyPlan --> CareTask  (aggregates two lists)
p1 = ((plan_bb[0] + plan_bb[2]) // 2, plan_bb[1])
p2 = (task_bb[2] - 40, task_bb[3])
dashed_arrow(p1, p2, "holds list")

# PRIORITY_MAP --> CareTask
draw.line([(nx, ny + 30), (task_bb[2], task_bb[1] + 120)], fill=NOTE_BORDER, width=1)

# ── Legend ────────────────────────────────────────────────────────────────────
lx, ly = 40, 880
draw.rectangle([lx, ly, lx + 380, ly + 70], fill="#F5F5F5", outline="#BBBBBB", width=1)
draw.text((lx + 8, ly + 6), "Legend", font=font_head, fill=BODY_TEXT)
arrow((lx + 8, ly + 30), (lx + 60, ly + 30))
draw.text((lx + 68, ly + 22), "association / uses", font=font_small, fill=BODY_TEXT)
# dashed line sample
for sx in range(lx + 8, lx + 60, 10):
    draw.line([(sx, ly + 52), (min(sx + 6, lx + 60), ly + 52)], fill=LINE_COLOR, width=2)
draw.polygon([(lx+60,ly+52),(lx+50,ly+47),(lx+50,ly+57)], fill=LINE_COLOR)
draw.text((lx + 68, ly + 45), "creates / holds (dashed)", font=font_small, fill=BODY_TEXT)

img.save("uml_final.png", dpi=(150, 150))
print("Saved uml_final.png")
