import pygame

pygame.init()  # pygame 초기화

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# 화면 설정
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCALE_FACTOR = min(SCREEN_WIDTH / 400, SCREEN_HEIGHT / 600)

# 새(플레이어) 설정
BIRD_SIZE = int(30 * SCALE_FACTOR)
BIRD_X_POS = SCREEN_WIDTH // 3
BIRD_GRAVITY = 0.8 * SCALE_FACTOR
BIRD_LIFT = -15 * SCALE_FACTOR

# 파이프 설정
PIPE_WIDTH = int(50 * SCALE_FACTOR)
PIPE_SPEED = 3 * SCALE_FACTOR
INITIAL_PIPE_GAP = int(400 * SCALE_FACTOR)
MIN_PIPE_GAP = int(150 * SCALE_FACTOR)
MIN_PIPE_SPAWN_DISTANCE = 300 * SCALE_FACTOR

# 코인 설정
COIN_SIZE = int(20 * SCALE_FACTOR)

# 게임 난이도 설정
INITIAL_SPAWN_INTERVAL = 120
MIN_SPAWN_INTERVAL = 90
DIFFICULTY_INCREASE_INTERVAL = 1000
SPEED_INCREASE_RATE = 0.1
GAP_DECREASE_RATE = 15

# 폰트 크기 설정
SCORE_FONT_SIZE = int(36 * SCALE_FACTOR)
GAME_OVER_FONT_SIZE = int(74 * SCALE_FACTOR)
RESTART_FONT_SIZE = int(36 * SCALE_FACTOR)