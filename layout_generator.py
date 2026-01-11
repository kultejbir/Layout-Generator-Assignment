import random
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from matplotlib.patches import Patch


# ------------------------
# SITE & BUILDING CONFIG
# ------------------------

SITE_WIDTH = 200
SITE_HEIGHT = 140

PLAZA_SIZE = 40
PLAZA_X = (SITE_WIDTH - PLAZA_SIZE) / 2
PLAZA_Y = (SITE_HEIGHT - PLAZA_SIZE) / 2

TOWER_A = {"type": "A", "w": 30, "h": 20}
TOWER_B = {"type": "B", "w": 20, "h": 20}

MIN_BUILDING_DIST = 15
MIN_BOUNDARY_DIST = 10
NEIGHBOUR_RADIUS = 60


# ------------------------
# GEOMETRY HELPERS
# ------------------------

def rectangle(x, y, w, h):
    return Polygon([
        (x, y),
        (x + w, y),
        (x + w, y + h),
        (x, y + h)
    ])


def distance_between(b1, b2):
    r1 = rectangle(b1["x"], b1["y"], b1["w"], b1["h"])
    r2 = rectangle(b2["x"], b2["y"], b2["w"], b2["h"])
    return r1.distance(r2)


# ------------------------
# RULE CHECKING FUNCTIONS
# ------------------------

def inside_site(b):
    return (
        b["x"] >= MIN_BOUNDARY_DIST and
        b["y"] >= MIN_BOUNDARY_DIST and
        b["x"] + b["w"] <= SITE_WIDTH - MIN_BOUNDARY_DIST and
        b["y"] + b["h"] <= SITE_HEIGHT - MIN_BOUNDARY_DIST
    )


def no_plaza_overlap(b):
    plaza = rectangle(PLAZA_X, PLAZA_Y, PLAZA_SIZE, PLAZA_SIZE)
    building = rectangle(b["x"], b["y"], b["w"], b["h"])
    return not building.intersects(plaza)


def distance_ok(b, others):
    for o in others:
        if distance_between(b, o) < MIN_BUILDING_DIST:
            return False
    return True


def neighbour_mix(buildings):
    for b in buildings:
        if b["type"] == "A":
            has_b_nearby = False
            for o in buildings:
                if o["type"] == "B":
                    if distance_between(b, o) <= NEIGHBOUR_RADIUS:
                        has_b_nearby = True
                        break
            if not has_b_nearby:
                return False
    return True


def check_all_rules(buildings):
    rules = {}

    # Rule 1 & 3: Inside site + boundary distance
    rules["Boundary Distance Rule"] = all(inside_site(b) for b in buildings)

    # Rule 2: Inter-building distance
    rules["Inter-building Distance Rule"] = True
    for i in range(len(buildings)):
        for j in range(i + 1, len(buildings)):
            if distance_between(buildings[i], buildings[j]) < MIN_BUILDING_DIST:
                rules["Inter-building Distance Rule"] = False

    # Rule 4: Neighbour mix
    rules["Neighbour Mix Rule"] = neighbour_mix(buildings)

    # Rule 5: Plaza
    rules["Central Plaza Rule"] = all(no_plaza_overlap(b) for b in buildings)

    return rules



# ------------------------
# LAYOUT GENERATION
# ------------------------

def random_building(building_type):
    x = random.uniform(0, SITE_WIDTH)
    y = random.uniform(0, SITE_HEIGHT)
    return {
        "type": building_type["type"],
        "w": building_type["w"],
        "h": building_type["h"],
        "x": x,
        "y": y
    }


def generate_layout(max_attempts=500):
    buildings = []

    for _ in range(max_attempts):
        btype = random.choice([TOWER_A, TOWER_B])
        b = random_building(btype)

        if not inside_site(b):
            continue
        if not no_plaza_overlap(b):
            continue
        if not distance_ok(b, buildings):
            continue

        buildings.append(b)

    return buildings


# ------------------------
# VISUALISATION
# ------------------------


def draw_layout(buildings, title):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Site
    ax.add_patch(
        plt.Rectangle((0, 0), SITE_WIDTH, SITE_HEIGHT,
                      fill=False, linewidth=2)
    )

    # Plaza
    ax.add_patch(
        plt.Rectangle((PLAZA_X, PLAZA_Y),
                      PLAZA_SIZE, PLAZA_SIZE,
                      color="lightgray")
    )

    # Buildings
    for b in buildings:
        color = "red" if b["type"] == "A" else "blue"
        ax.add_patch(
            plt.Rectangle((b["x"], b["y"]),
                          b["w"], b["h"],
                          color=color)
        )

    legend_elements = [
        Patch(facecolor='red', label='Tower A'),
        Patch(facecolor='blue', label='Tower B'),
        Patch(facecolor='lightgray', label='Central Plaza')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    ax.set_xlim(0, SITE_WIDTH)
    ax.set_ylim(0, SITE_HEIGHT)
    ax.set_title(title)
    ax.set_aspect("equal")

    plt.show()




# ------------------------
# STATS
# ------------------------

def print_stats(buildings):
    count_a = sum(1 for b in buildings if b["type"] == "A")
    count_b = sum(1 for b in buildings if b["type"] == "B")
    area = sum(b["w"] * b["h"] for b in buildings)

    print("Tower A:", count_a)
    print("Tower B:", count_b)
    print("Total Built Area:", area, "sqm")

    rules = check_all_rules(buildings)
    for rule, status in rules.items():
        print(f"{rule}: {'OK' if status else 'VIOLATED'}")

    print("-" * 40)





# ------------------------
# MAIN
# ------------------------


if __name__ == "__main__":
    try:
        n = int(input("Enter the number of Layouts you want to generate: "))
        for i in range(n):
            layout = generate_layout()
            print(f"Layout {i + 1}")
            print_stats(layout)
            draw_layout(layout, f"Layout {i + 1}")
    except ValueError:
        print("Please enter a valid integer.")
