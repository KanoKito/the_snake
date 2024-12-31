from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет  отравленного яблока
POISON_COLOR = (0, 0, 255)

# Цвет камня
ROCK_COLOR = (125, 125, 125)

# Скорость движения змейки:
SPEED = 20

# Инициализация PyGame.
pygame.init()

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self, body_color=None):
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = body_color

    def draw(self):
        """Пустая заготовка метода для отрисовки объекта на игровом поле."""

    def randomize_position(self, positions) -> None:
        """Устанавливаем случайное положение объекта."""
        if positions is None:
            positions = list()
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in positions:
                break


class Snake(GameObject):
    """Класс игровых объектов Змейка."""

    def __init__(self, body_color=None) -> None:
        super().__init__(body_color)

        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction: tuple = RIGHT
        self.last = None

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляем позицию змейки  добавляя новую голову в начало списка
        positions и удаляя последний элемент, если
        длина змейки не увеличилась.
        """
        self.position = (
            (self.position[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (self.position[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )

        past_length: int = len(self.positions)
        self.positions.insert(0, self.position)
        if self.length == past_length:
            self.last = self.positions.pop()
        elif self.length < past_length:
            self.last = self.positions.pop()
            self.draw()
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Рисуем змейку"""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple:
        """Возвращаем позицию головы змейки - первый элемент в списке
        positions.
        """
        return self.positions[0]

    def reset(self) -> None:
        """Cбрасываем змейку в начальное состояние после столкновения с
        собой.
        """
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.length = len(self.positions)
        self.direction = RIGHT


class Apple(GameObject):
    """Класс игровых объектов Яблоко."""

    def __init__(self, busy=None, body_color=None) -> None:
        super().__init__(body_color)
        self.randomize_position(busy)

    def draw(self):
        """Рисуем яблоко"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            game_object.update_direction()


def draw(*args):
    """Отрисовка объектов"""
    for game_object in args:
        game_object.draw()


def main():
    """Запуск игры"""
    snake = Snake(SNAKE_COLOR)
    apple = Apple(snake.positions, APPLE_COLOR)
    poison_apple = Apple(snake.positions, POISON_COLOR)
    rock = Apple(snake.positions, ROCK_COLOR)
    running = True

    while running:
        clock.tick(SPEED)
        handle_keys(snake)
        clock.tick(SPEED)
        draw(apple, snake, rock, poison_apple)
        snake.move()

        # Змейка съела яблоко
        if apple.position == snake.get_head_position():
            snake.length += 1
            apple.randomize_position(snake.positions)

        # Змейка укусила себя
        if snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Змейка съела плохое яблоко
        if poison_apple.position == snake.get_head_position():
            snake.length = max(1, snake.length - 1)
            poison_apple.randomize_position(snake.positions)

        # Змейка врезалась в камень
        if rock.position == snake.get_head_position():
            snake.reset()
            rock.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        pygame.display.set_caption(f'Змейка Счет: {snake.length - 1}')
        pygame.display.update()


if __name__ == '__main__':
    main()
