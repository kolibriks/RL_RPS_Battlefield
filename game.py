import streamlit as st
import numpy as np
from PIL import Image


# size of the board
WIDTH, HEIGHT = 700, 700
# number of every object on the board
NUM_OBJECTS = 10
# object size
OBJECT_SIZE = 20
# symbols for the objects
symbols = ['rock', 'paper', 'scissor']


class GameObject:
    def __init__(self, x, y, symbol):
        self.x = x
        self.y = y
        self.type = symbol
        self.image = self.image = Image.open(f'images/{symbol}.png').resize((OBJECT_SIZE, OBJECT_SIZE))

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
        if self.type == 'rock' and other.type == 'scissor':
            return other
        if self.type == 'scissor' and other.type == 'paper':
            return other
        if self.type == 'paper' and other.type == 'rock':
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
    movement_mode = st.radio("Select Movement Mode:", ("Random Mode", "Hunter Mode"))
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
                closest_target = None
                min_dist = np.inf
                for obj2 in objects:
                    if obj1 != obj2 and obj1.interact_with(obj2):
                        dist = (obj1.x - obj2.x) ** 2 + (obj1.y - obj2.y) ** 2
                        if dist < min_dist:
                            min_dist = dist
                            closest_target = obj2
                if closest_target:
                    dy = np.sign(closest_target.y - obj1.y)
                    dx = np.sign(closest_target.x - obj1.x)
                    obj1.move(dx, dy)
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
