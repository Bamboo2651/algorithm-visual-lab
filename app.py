import pygame

WindowWidth = 1100
WindowHeight = 700

backgroundColor = (10, 14, 26) 

def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (WindowWidth, WindowHeight)
    )
    
    pygame.display.set_caption("Algorithm Visual Lab")

    clock = pygame.time.Clock()
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(backgroundColor)

        pygame.display.flip()

        clock.tick(60)

    # Pygameを終了する
    pygame.quit()


if __name__ == "__main__":
    main()