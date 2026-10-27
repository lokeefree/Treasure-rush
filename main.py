import asyncio
import random
import platform
import pygame

# -----------------------------
# TREASURE RUSH - UPDATE 1
# -----------------------------

pygame.init()

WIDTH, HEIGHT = 800, 600
HUD_HEIGHT = 88
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Treasure Rush")

CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 28)
SMALL_FONT = pygame.font.Font(None, 22)
BIG_FONT = pygame.font.Font(None, 68)
MEDIUM_FONT = pygame.font.Font(None, 38)

# Colors
GRASS = (104, 160, 83)
DARK_GREEN = (47, 100, 54)
LIGHT_GREEN = (130, 185, 95)
WHITE = (255, 255, 255)
GOLD = (255, 207, 55)
PALE_GOLD = (255, 239, 130)
BROWN = (130, 79, 43)
BLUE = (55, 125, 230)
RED = (220, 65, 65)
BLACK = (30, 35, 30)
PANEL = (37, 43, 38)
MUTED = (190, 200, 188)
ORANGE = (245, 151, 55)

PLAYER_SIZE = 28
PLAYER_SPEED = 230
GAME_DURATION = 90
COIN_COUNT = 15
CHEST_COUNT = 4
SLIME_COUNT = 3

# Touch controls are enabled automatically in browsers/devices that report
# touch capability. Keyboard controls remain available on every device.
DPAD_SIZE = 46
DPAD_GAP = 5
DPAD_ORIGIN = (24, HEIGHT - 38 - (DPAD_SIZE * 3 + DPAD_GAP * 2) - 12)


def detect_touch_device():
    """Best-effort detection for touch-capable devices in Pygbag/browser builds."""
    navigator = None
    try:
        browser_window = getattr(platform, "window", None)
        if browser_window is not None:
            navigator = browser_window.navigator
    except Exception:
        pass

    # Some browser Python runtimes expose JavaScript through the `js` module.
    if navigator is None:
        try:
            import js
            navigator = js.navigator
        except Exception:
            pass

    try:
        if navigator is not None:
            touch_points = int(getattr(navigator, "maxTouchPoints", 0) or 0)
            user_agent = str(getattr(navigator, "userAgent", "")).lower()
            mobile_words = ("android", "iphone", "ipad", "ipod", "mobile")
            if touch_points > 0 or any(word in user_agent for word in mobile_words):
                return True
    except Exception:
        # Detection can vary by browser/runtime; touch events still work below.
        pass
    return False


def dpad_buttons():
    """Return the four directional button rectangles."""
    x, y = DPAD_ORIGIN
    center_x = x + DPAD_SIZE + DPAD_GAP
    center_y = y + DPAD_SIZE + DPAD_GAP
    return {
        "up": pygame.Rect(center_x, y, DPAD_SIZE, DPAD_SIZE),
        "left": pygame.Rect(x, center_y, DPAD_SIZE, DPAD_SIZE),
        "right": pygame.Rect(center_x + DPAD_SIZE + DPAD_GAP, center_y, DPAD_SIZE, DPAD_SIZE),
        "down": pygame.Rect(center_x, center_y + DPAD_SIZE + DPAD_GAP, DPAD_SIZE, DPAD_SIZE),
    }


def touch_position_from_event(event):
    """Convert Pygame finger coordinates (0..1) to screen coordinates."""
    return int(event.x * WIDTH), int(event.y * HEIGHT)


def random_position(size=20):
    """Create a random rectangle inside the play area."""
    return pygame.Rect(
        random.randint(40, WIDTH - 40 - size),
        random.randint(HUD_HEIGHT + 15, HEIGHT - 45 - size),
        size,
        size,
    )


def new_game():
    """Create a completely fresh round."""
    player = pygame.Rect(70, HUD_HEIGHT + 35, PLAYER_SIZE, PLAYER_SIZE)

    coins = [random_position(16) for _ in range(COIN_COUNT)]
    chests = [random_position(25) for _ in range(CHEST_COUNT)]

    slimes = []
    for _ in range(SLIME_COUNT):
        rect = random_position(25)
        slimes.append({
            "rect": rect,
            "speed": random.choice([-110, 110]),
        })

    return player, coins, chests, slimes


def draw_text(text, x, y, color=WHITE, font=FONT, centered=False):
    image = font.render(str(text), True, color)
    if centered:
        x -= image.get_width() // 2
    SCREEN.blit(image, (x, y))


def draw_coin(coin):
    pygame.draw.circle(SCREEN, (90, 70, 30), (coin.centerx + 1, coin.centery + 2), 9)
    pygame.draw.circle(SCREEN, GOLD, coin.center, 9)
    pygame.draw.circle(SCREEN, PALE_GOLD, coin.center, 4)


def draw_chest(chest):
    pygame.draw.rect(SCREEN, (80, 48, 28), chest, border_radius=4)
    body = pygame.Rect(chest.x, chest.y + 5, chest.width, chest.height - 5)
    pygame.draw.rect(SCREEN, BROWN, body, border_radius=3)
    pygame.draw.rect(SCREEN, GOLD, (chest.x, chest.y + 7, chest.width, 6))
    pygame.draw.rect(
        SCREEN, PALE_GOLD,
        (chest.centerx - 3, chest.y + 8, 6, 8),
        border_radius=1,
    )
    pygame.draw.rect(SCREEN, (75, 44, 25), chest, 2, border_radius=4)


def draw_slime(rect, hit_cooldown):
    color = (245, 130, 130) if hit_cooldown > 0 else RED
    pygame.draw.ellipse(SCREEN, (120, 48, 48), rect.move(0, 3))
    pygame.draw.ellipse(SCREEN, color, rect)
    pygame.draw.circle(SCREEN, WHITE, (rect.x + 8, rect.y + 9), 4)
    pygame.draw.circle(SCREEN, WHITE, (rect.x + 18, rect.y + 9), 4)
    pygame.draw.circle(SCREEN, BLACK, (rect.x + 9, rect.y + 9), 2)
    pygame.draw.circle(SCREEN, BLACK, (rect.x + 19, rect.y + 9), 2)


def draw_player(player, hit_cooldown):
    color = (135, 190, 255) if hit_cooldown > 0 else BLUE
    pygame.draw.rect(SCREEN, (30, 65, 130), player.move(0, 3), border_radius=5)
    pygame.draw.rect(SCREEN, color, player, border_radius=5)
    pygame.draw.rect(SCREEN, WHITE, player, 2, border_radius=5)
    # Simple face so the player is easier to distinguish from objects.
    pygame.draw.circle(SCREEN, WHITE, (player.x + 9, player.y + 9), 3)
    pygame.draw.circle(SCREEN, WHITE, (player.x + 19, player.y + 9), 3)
    pygame.draw.circle(SCREEN, BLACK, (player.x + 9, player.y + 9), 1)
    pygame.draw.circle(SCREEN, BLACK, (player.x + 19, player.y + 9), 1)


def draw_hud(score, coins_left, chests_left, time_left):
    pygame.draw.rect(SCREEN, PANEL, (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(SCREEN, GOLD, (0, HUD_HEIGHT - 2), (WIDTH, HUD_HEIGHT - 2), 2)

    draw_text("TREASURE", 18, 10, GOLD, MEDIUM_FONT)
    draw_text("RUSH", 18, 43, WHITE, MEDIUM_FONT)

    # Score panel
    pygame.draw.rect(SCREEN, (53, 61, 54), (205, 15, 145, 58), border_radius=8)
    draw_text("SCORE", 218, 20, MUTED, SMALL_FONT)
    draw_text(score, 218, 42, WHITE, FONT)

    # Treasure remaining panel
    pygame.draw.rect(SCREEN, (53, 61, 54), (365, 15, 175, 58), border_radius=8)
    draw_text("TREASURE LEFT", 378, 20, MUTED, SMALL_FONT)
    draw_text(f"Coins {coins_left}   Chests {chests_left}", 378, 44, GOLD, SMALL_FONT)

    # Timer panel changes color when time is running low.
    timer_color = RED if time_left <= 15 else GOLD
    pygame.draw.rect(SCREEN, (53, 61, 54), (555, 15, 225, 58), border_radius=8)
    draw_text("TIME LEFT", 570, 20, MUTED, SMALL_FONT)
    draw_text(f"{max(0, int(time_left)):02d}s", 570, 41, timer_color, MEDIUM_FONT)

    # Timer bar
    bar_x, bar_y, bar_w, bar_h = 650, 47, 112, 12
    pygame.draw.rect(SCREEN, (22, 27, 23), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
    fill_w = int(bar_w * max(0, min(1, time_left / GAME_DURATION)))
    if fill_w > 0:
        pygame.draw.rect(SCREEN, timer_color, (bar_x, bar_y, fill_w, bar_h), border_radius=5)


def draw_game(player, coins, chests, slimes, score, time_left, hit_cooldown, game_over):
    SCREEN.fill(GRASS)

    # Subtle grass pattern
    for x in range(20, WIDTH, 80):
        for y in range(HUD_HEIGHT + 20, HEIGHT, 85):
            pygame.draw.circle(SCREEN, DARK_GREEN, (x, y), 3)
            pygame.draw.circle(SCREEN, LIGHT_GREEN, (x + 24, y + 30), 2)

    # A light border around the play area
    pygame.draw.rect(SCREEN, DARK_GREEN, (4, HUD_HEIGHT + 3, WIDTH - 8, HEIGHT - HUD_HEIGHT - 7), 2)

    for coin in coins:
        draw_coin(coin)

    for chest in chests:
        draw_chest(chest)

    for slime in slimes:
        draw_slime(slime["rect"], hit_cooldown)

    draw_player(player, hit_cooldown)

    # Bottom instruction strip
    pygame.draw.rect(SCREEN, PANEL, (0, HEIGHT - 38, WIDTH, 38))
    draw_text("MOVE: WASD / ARROW KEYS", 15, HEIGHT - 29, WHITE, SMALL_FONT)
    draw_text("AVOID SLIMES: each hit costs 5 seconds", WIDTH - 15, HEIGHT - 29, MUTED, SMALL_FONT)
    # Right-align the second hint.
    hint = SMALL_FONT.render("AVOID SLIMES: each hit costs 5 seconds", True, MUTED)
    SCREEN.blit(hint, (WIDTH - hint.get_width() - 15, HEIGHT - 29))

    draw_hud(score, len(coins), len(chests), time_left)

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((16, 20, 17, 205))
        SCREEN.blit(overlay, (0, 0))

        panel = pygame.Rect(165, 170, 470, 280)
        pygame.draw.rect(SCREEN, PANEL, panel, border_radius=18)
        pygame.draw.rect(SCREEN, GOLD, panel, 3, border_radius=18)

        draw_text("TIME'S UP!", WIDTH // 2, 205, GOLD, BIG_FONT, centered=True)
        draw_text(f"FINAL SCORE: {score}", WIDTH // 2, 285, WHITE, MEDIUM_FONT, centered=True)
        draw_text("Press R to play again", WIDTH // 2, 345, PALE_GOLD, FONT, centered=True)
        draw_text("Press ESC to quit", WIDTH // 2, 383, MUTED, SMALL_FONT, centered=True)



def draw_touch_controls(pressed_directions):
    """Draw a compact D-pad for touch devices."""
    labels = {"up": "▲", "down": "▼", "left": "◀", "right": "▶"}
    for direction, rect in dpad_buttons().items():
        is_pressed = direction in pressed_directions
        fill = (91, 111, 87) if is_pressed else (37, 43, 38)
        edge = PALE_GOLD if is_pressed else WHITE
        pygame.draw.rect(SCREEN, fill, rect, border_radius=9)
        pygame.draw.rect(SCREEN, edge, rect, 2, border_radius=9)
        image = SMALL_FONT.render(labels[direction], True, WHITE)
        SCREEN.blit(image, image.get_rect(center=rect.center))


def draw_mobile_restart_button():
    """Give touch players a restart button after the round ends."""
    button = pygame.Rect(WIDTH // 2 - 115, 405, 230, 48)
    pygame.draw.rect(SCREEN, (72, 103, 58), button, border_radius=10)
    pygame.draw.rect(SCREEN, PALE_GOLD, button, 2, border_radius=10)
    draw_text("TAP TO PLAY AGAIN", button.centerx, button.y + 13, WHITE, SMALL_FONT, centered=True)
    return button


def reset_round():
    """Return all round state in one place to avoid partial resets."""
    player, coins, chests, slimes = new_game()
    return {
        "player": player,
        "coins": coins,
        "chests": chests,
        "slimes": slimes,
        "score": 0,
        "time_left": float(GAME_DURATION),
        "hit_cooldown": 0.0,
        "game_over": False,
    }


async def main():
    state = reset_round()
    running = True
    # Always show the on-screen controls on both desktop and mobile.
    touch_controls = True
    active_touch_directions = set()
    touch_fingers = {}
    mouse_directions = set()
    restart_button = pygame.Rect(WIDTH // 2 - 115, 405, 230, 48)

    while running:
        dt = min(CLOCK.tick(60) / 1000, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
                px, py = touch_position_from_event(event)
                if state["game_over"]:
                    if event.type == pygame.FINGERDOWN and restart_button.collidepoint(px, py):
                        state = reset_round()
                        touch_fingers.clear()
                        active_touch_directions.clear()
                    continue
                touch_fingers[event.finger_id] = (px, py)

            elif event.type == pygame.FINGERUP:
                touch_fingers.pop(event.finger_id, None)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                px, py = event.pos
                if state["game_over"] and touch_controls and restart_button.collidepoint(px, py):
                    state = reset_round()
                    active_touch_directions.clear()
                elif touch_controls and not state["game_over"]:
                    for direction, rect in dpad_buttons().items():
                        if rect.collidepoint(px, py):
                            mouse_directions.add(direction)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_directions.clear()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r and state["game_over"]:
                    # Rebuild the entire round in one operation.
                    state = reset_round()
                    # Avoid carrying a held key across the reset.
                    pygame.event.clear(pygame.KEYDOWN)

        if not running:
            break

        if not state["game_over"]:
            state["time_left"] -= dt
            state["hit_cooldown"] = max(0.0, state["hit_cooldown"] - dt)

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

            # Combine keyboard and touchscreen input, so either can be used.
            active_touch_directions = set()
            for finger_x, finger_y in touch_fingers.values():
                for direction, rect in dpad_buttons().items():
                    if rect.collidepoint(finger_x, finger_y):
                        active_touch_directions.add(direction)
            pressed_directions = active_touch_directions | mouse_directions
            if "left" in pressed_directions:
                dx -= 1
            if "right" in pressed_directions:
                dx += 1
            if "up" in pressed_directions:
                dy -= 1
            if "down" in pressed_directions:
                dy += 1

            # Normalize diagonal movement.
            if dx and dy:
                dx *= 0.7071
                dy *= 0.7071

            player = state["player"]
            player.x += round(dx * PLAYER_SPEED * dt)
            player.y += round(dy * PLAYER_SPEED * dt)

            # Keep the player inside the play area.
            player.left = max(0, player.left)
            player.right = min(WIDTH, player.right)
            player.top = max(HUD_HEIGHT, player.top)
            player.bottom = min(HEIGHT - 38, player.bottom)

            # Collect coins.
            for coin in state["coins"][:]:
                if player.colliderect(coin):
                    state["coins"].remove(coin)
                    state["score"] += 10

            # Open treasure chests.
            for chest in state["chests"][:]:
                if player.colliderect(chest):
                    state["chests"].remove(chest)
                    state["score"] += 50

            # Move slimes and handle collisions.
            for slime in state["slimes"]:
                rect = slime["rect"]
                rect.x += round(slime["speed"] * dt)

                if rect.left <= 0:
                    rect.left = 0
                    slime["speed"] = abs(slime["speed"])
                elif rect.right >= WIDTH:
                    rect.right = WIDTH
                    slime["speed"] = -abs(slime["speed"])

                if player.colliderect(rect) and state["hit_cooldown"] <= 0:
                    state["time_left"] -= 5
                    state["hit_cooldown"] = 1.0

            if state["time_left"] <= 0:
                state["time_left"] = 0
                state["game_over"] = True

        draw_game(
            state["player"],
            state["coins"],
            state["chests"],
            state["slimes"],
            state["score"],
            state["time_left"],
            state["hit_cooldown"],
            state["game_over"],
        )

        if touch_controls and not state["game_over"]:
            draw_touch_controls(active_touch_directions | mouse_directions)
        elif touch_controls and state["game_over"]:
            restart_button = draw_mobile_restart_button()
        else:
            restart_button = pygame.Rect(WIDTH // 2 - 115, 405, 230, 48)

        pygame.display.flip()

        # Keep this yield for browser-based Pygbag input/rendering.
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
