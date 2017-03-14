import pygame

import setgame


pygame.init()
setgame.manager.load()

app = setgame.manager.launch()
fps_clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        app.handle_event(event)

    app.tick()
    fps_clock.tick(30)
