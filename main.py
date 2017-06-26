import pygame

from setgame import launcher


pygame.init()
launcher.load()

app = launcher.spawn_app()
fps_clock = pygame.time.Clock()
pygame.mixer.quit()

app.open()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        app.handle_event(event)

    app.step()
    fps_clock.tick(30)
