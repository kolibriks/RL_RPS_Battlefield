import streamlit as st
import numpy as np
from PIL import Image
from scipy.spatial import KDTree


# size of the board
WIDTH, HEIGHT = 700, 700
# number of every object on the board
NUM_OBJECTS = 10
# object size
OBJECT_SIZE = 20
# symbols for the objects
symbols = ['rock', 'paper', 'scissor']
# interaction dictionary
interaction_dict = {'rock': 'scissor', 'scissor': 'paper', 'paper': 'rock'}
# Preload images
image_dict = {symbol: Image.open(f'images/{symbol}.png').resize((OBJECT_SIZE, OBJECT_SIZE)) for symbol in symbols}


class GameObject:
    def __init__(self, x, y, symbol):
        self.x = x
        self.y = y
        self.type = symbol
        self.image = image_dict[symbol]

    def move(self, dx, dy):
        self.x = max(OBJECT_SIZE, min(WIDTH - OBJECT_SIZE, self.x + dx))
        self.y = max(OBJECT_SIZE, min(HEIGHT - OBJECT_SIZE, self.y + dy))


    def iou(self, other):
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x + OBJECT_SIZE, other.x + OBJECT_SIZE)
        y2 = min(self.y + OBJECT_SIZE, other.y + OBJECT_SIZE)

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        union = 2 * OBJECT_SIZE ** 2 - intersection

        return intersection / union if union > 0 else 0


    def interact_with(self, other):
        if interaction_dict[self.type] == other.type:  # Use dictionary to determine interaction
            return other
        return None  # No interaction


def create_objects():
    """Create a board with random objects."""
    objects = []
    for obj in symbols:
        for i in range(NUM_OBJECTS):
            x, y = np.random.randint(0 + OBJECT_SIZE, WIDTH - OBJECT_SIZE), \
                np.random.randint(0 + OBJECT_SIZE, HEIGHT - OBJECT_SIZE)
            objects.append(GameObject(x, y, obj))
    return objects


def draw_objects(objects):
    image = Image.new('RGB', (WIDTH, HEIGHT), 'black')

    for obj in objects:
        image.paste(obj.image, (obj.x, obj.y), mask=obj.image.convert('RGBA').getchannel('A'))

    return image


def simulate_game():
    objects = create_objects()
    image_container = st.empty()

    session_state = st.session_state
    session_state.running = False
    movement_mode = st.radio("Select Movement Mode:", ("Random Mode", "Hunter Mode", "Advanced Hunter Mode"))
    transform_mode = st.checkbox("Object changes class when it loses", value=True)

    if st.button("Start"):
        session_state.running = True

    if st.button("Stop"):
        session_state.running = False

    while session_state.running:
        objects_to_remove = {}
        for obj1 in objects:
            if movement_mode == "Random Mode":
                obj1.move(np.random.randint(-1, 2), np.random.randint(-1, 2))
            elif movement_mode == "Hunter Mode":
                targets = [obj for obj in objects if obj.type == interaction_dict[obj1.type]]
                if targets:
                    target_coords = [(obj.x, obj.y) for obj in targets]
                    kd_tree = KDTree(target_coords)  # Rebuild KD-tree

                    dist, index = kd_tree.query((obj1.x, obj1.y))  # Find nearest target
                    closest_target = targets[index]
                    dy = np.sign(closest_target.y - obj1.y)
                    dx = np.sign(closest_target.x - obj1.x)
                    obj1.move(dx, dy)
            elif movement_mode == "Advanced Hunter Mode":
                target_coords = [(obj.x, obj.y) for obj in objects]
                kd_tree = KDTree(target_coords)  # Build KD-tree for all objects

                dists, indices = kd_tree.query((obj1.x, obj1.y), k=len(objects))  # Find distances to all objects
                dist_kill, dist_avoid = np.inf, np.inf
                closest_target_to_kill = None
                closest_target_to_avoid = None

                for dist, index in zip(dists, indices):
                    obj2 = objects[index]
                    if obj2 != obj1:
                        if obj2.type == interaction_dict[obj1.type] and dist < dist_kill:
                            dist_kill = dist
                            closest_target_to_kill = obj2
                        elif interaction_dict[obj2.type] == obj1.type and dist < dist_avoid:
                            dist_avoid = dist
                            closest_target_to_avoid = obj2

                if dist_kill < dist_avoid or (dist_kill == dist_avoid and dist_kill < np.inf):
                    dy = np.sign(closest_target_to_kill.y - obj1.y)
                    dx = np.sign(closest_target_to_kill.x - obj1.x)
                elif dist_avoid < np.inf:
                    dy = -np.sign(closest_target_to_avoid.y - obj1.y)
                    dx = -np.sign(closest_target_to_avoid.x - obj1.x)
                else:
                    dx, dy = 0, 0

                # Check if the object would move into a wall, and if so, try to move in a different direction
                new_x = obj1.x + dx
                new_y = obj1.y + dy

                if new_x < OBJECT_SIZE or new_x > WIDTH - OBJECT_SIZE:
                    dx = 0
                    dy = np.sign(dy) if dy != 0 else np.random.choice([-1, 1])

                if new_y < OBJECT_SIZE or new_y > HEIGHT - OBJECT_SIZE:
                    dy = 0
                    dx = np.sign(dx) if dx != 0 else np.random.choice([-1, 1])
                obj1.move(dx, dy)

            # check if objects are close enough to interact
            for obj2 in objects:
                if obj1 != obj2 and obj1.iou(obj2) > 0.3:
                    eaten_obj = obj1.interact_with(obj2)
                    if eaten_obj:
                        objects_to_remove[eaten_obj] = obj1.type
        for obj in objects_to_remove.keys():
            if transform_mode:
                obj.type = objects_to_remove[obj]
                obj.image = Image.open(f'images/{obj.type}.png').resize((OBJECT_SIZE, OBJECT_SIZE))
            else:
                objects.remove(obj)
        image = draw_objects(objects)
        image_container.image(image, channels="BGR", use_column_width=True)


def game():
    st.title("Rock, Paper, Scissors")
    simulate_game()


if __name__ == "__main__":
    game()
