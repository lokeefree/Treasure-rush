
import asyncio
import random
import pygame

# -----------------------------
# TREASURE RUSH - VERSION 1
# -----------------------------

pygame.init()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Treasure Rush")

CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 30)
BIG_FONT = pygame.font.Font(None, 64)

# Colors
GRASS = (104, 160, 83)
DARK_GREEN = (47, 100, 54)
WHITE = (255, 255, 255)
GOLD = (255, 207, 55)
BROWN = (130, 79, 43)
BLUE = (55, 125, 230)
RED = (220, 65, 65)
BLACK = (30, 35, 30)
STONE = (115, 120, 120)

PLAYER_SIZE = 28
PLAYER_SPEED = 230
GAME_DURATION = 90


def random_position(size=20):
    return pygame.Rect(
        random.randint(40, WIDTH - 40 - size),
        random.randint(100, HEIGHT - 40 - size),
        size,
        size,
    )


def new_game():
    player = pygame.Rect(70, 120, PLAYER_SIZE, PLAYER_SIZE)

    coins = [random_position(16) for _ in range(15)]
    chests = [random_position(25) for _ in range(4)]

    slimes = []
    for _ in range(3):
        rect = random_position(25)
        slimes.append({
            "rect": rect,
            "speed": random.choice([-110, 110]),
        })

    return player, coins, chests, slimes


def draw_text(text, x, y, color=WHITE, font=FONT):
    image = font.render(text, True, color)
    SCREEN.blit(image, (x, y))


def draw_game(player, coins, chests, slimes,
              score, time_left, hit_cooldown, game_over):

    SCREEN.fill(GRASS)

    # Decorative grass patches
    for x in range(20, WIDTH, 80):
        for y in range(100, HEIGHT, 85):
            pygame.draw.circle(
                SCREEN, DARK_GREEN, (x, y), 3
            )

    # HUD
    pygame.draw.rect(SCREEN, BLACK, (0, 0, WIDTH, 85))
    draw_text("TREASURE RUSH", 20, 12, GOLD)
    draw_text(f"Score: {score}", 20, 48)
    draw_text(f"Coins: {len(coins)}", 210, 48)
    draw_text(f"Time: {max(0, int(time_left))}", 350, 48)

    # Coins
    for coin in coins:
        pygame.draw.circle(
            SCREEN, GOLD, coin.center, 9
        )
        pygame.draw.circle(
            SCREEN, (255, 239, 130), coin.center, 4
        )

    # Treasure chests
    for chest in chests:
        pygame.draw.rect(SCREEN, BROWN, chest)
        pygame.draw.rect(
            SCREEN, GOLD,
            (chest.x, chest.y + 7, chest.width, 6)
        )
        pygame.draw.rect(
            SCREEN, BLACK,
            (chest.centerx - 2, chest.y + 9, 4, 4)
        )

    # Slimes
    for slime in slimes:
        rect = slime["rect"]
        pygame.draw.ellipse(SCREEN, RED, rect)
        pygame.draw.circle(
            SCREEN, WHITE, (rect.x + 8, rect.y + 9), 4
        )
        pygame.draw.circle(
            SCREEN, WHITE, (rect.x + 18, rect.y + 9), 4
        )
        pygame.draw.circle(
            SCREEN, BLACK, (rect.x + 8, rect.y + 9), 2
        )
        pygame.draw.circle(
            SCREEN, BLACK, (rect.x + 18, rect.y + 9), 2
        )

    # Player
    player_color = (
        WHITE if hit_cooldown > 0 else BLUE
    )
    pygame.draw.rect(SCREEN, player_color, player)
    pygame.draw.rect(
        SCREEN, WHITE, player, 2
    )

    draw_text(
        "WASD / Arrow Keys: Move",
        15, HEIGHT - 32, WHITE
    )

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(190)
        overlay.fill(BLACK)
        SCREEN.blit(overlay, (0, 0))

        draw_text(
            "TIME'S UP!", 255, 220, GOLD, BIG_FONT
        )
        draw_text(
            f"Final Score: {score}",
            290, 300, WHITE
        )
        draw_text(
            "Press R to play again",
            270, 355, WHITE
        )


async def main():
    player, coins, chests, slimes = new_game()

    score = 0
    time_left = GAME_DURATION
    hit_cooldown = 0
    game_over = False
    running = True

    while running:
        dt = min(CLOCK.tick(60) / 1000, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_r and game_over:
                    (
                        player, coins, chests, slimes
                    ) = new_game()

                    score = 0
                    time_left = GAME_DURATION
                    hit_cooldown = 0
                    game_over = False

        if not game_over:
            time_left -= dt
            hit_cooldown = max(0, hit_cooldown - dt)

            keys = pygame.key.get_pressed()

            dx = 0
            dy = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1

            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071

            player.x += round(dx * PLAYER_SPEED * dt)
            player.y += round(dy * PLAYER_SPEED * dt)

            # Keep the player inside the map
            player.left = max(0, player.left)
            player.right = min(WIDTH, player.right)
            player.top = max(85, player.top)
            player.bottom = min(HEIGHT, player.bottom)

            # Collect coins
            for coin in coins[:]:
                if player.colliderect(coin):
                    coins.remove(coin)
                    score += 10

            # Open treasure chests
            for chest in chests[:]:
                if player.colliderect(chest):
                    chests.remove(chest)
                    score += 50

            # Move slimes horizontally
            for slime in slimes:
                rect = slime["rect"]
                rect.x += round(slime["speed"] * dt)

                if rect.left <= 0:
                    rect.left = 0
                    slime["speed"] = abs(slime["speed"])

                if rect.right >= WIDTH:
                    rect.right = WIDTH
                    slime["speed"] = -abs(slime["speed"])

                # Slime collision: lose 5 seconds
                if (
                    player.colliderect(rect)
                    and hit_cooldown <= 0
                ):
                    time_left -= 5
                    hit_cooldown = 1.0

            if time_left <= 0:
                time_left = 0
                game_over = True

        draw_game(
            player, coins, chests, slimes,
            score, time_left, hit_cooldown, game_over
        )

        pygame.display.flip()

        # Lets browser-based Pygbag process input and rendering
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
