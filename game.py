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
        self.image = self.image = Image.open(f'images/{symbol}.png').resize((OBJECT_SIZE, OBJECT_SIZE))

    def move(self, dx, dy):
        self.x = max(OBJECT_SIZE, min(WIDTH - OBJECT_SIZE, self.x + dx))
        self.y = max(OBJECT_SIZE, min(HEIGHT - OBJECT_SIZE, self.y + dy))


def create_objects():
    """Create a board with random objects."""
    objects = []
    for obj in symbols:
        for i in range(NUM_OBJECTS):
            x, y = np.random.randint(0, WIDTH), np.random.randint(0, HEIGHT)
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
    if st.button("Start"):
        session_state.running = True

    if st.button("Stop"):
        session_state.running = False

    while session_state.running:
        for obj in objects:
            obj.move(np.random.randint(-1, 2), np.random.randint(-1, 2))
        image = draw_objects(objects)
        image_container.image(image, channels="BGR", use_column_width=True)


def game():
    st.title("Rock, Paper, Scissors")
    simulate_game()


if __name__ == "__main__":
    game()
