"""
Interactive UI components: sliders, buttons, checkboxes.
Used for changing simulation parameters mid-run.
"""

import pygame
from typing import Callable


# UI colors
COLOR_PANEL_BG = (18, 18, 28)
COLOR_PANEL_BORDER = (50, 50, 70)
COLOR_SLIDER_TRACK = (40, 40, 55)
COLOR_SLIDER_FILL = (80, 100, 140)
COLOR_SLIDER_THUMB = (120, 150, 200)
COLOR_BUTTON = (60, 80, 120)
COLOR_BUTTON_HOVER = (80, 100, 150)
COLOR_BUTTON_TEXT = (220, 220, 240)
COLOR_LABEL = (180, 190, 210)
COLOR_CHECK_ON = (100, 180, 120)
COLOR_CHECK_OFF = (60, 60, 80)


def get_font(size: int = 20):
    """Get UI font."""
    try:
        return pygame.font.Font(None, size)
    except OSError:
        return pygame.font.SysFont("sans", size - 2)


class Slider:
    """Horizontal slider for numeric values."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        value: float,
        min_val: float,
        max_val: float,
        label: str = "",
        decimals: int = 2,
    ):
        self.rect = pygame.Rect(x, y, width, 28)
        self.value = max(min_val, min(max_val, value))
        self.min_val = min_val
        self.max_val = max_val
        self.label = label
        self.decimals = decimals
        self._dragging = False
        self._thumb_width = 14

    def _value_to_x(self, val: float) -> int:
        t = (val - self.min_val) / (self.max_val - self.min_val) if self.max_val != self.min_val else 0
        return self.rect.x + 4 + int(t * (self.rect.width - 8 - self._thumb_width))

    def _x_to_value(self, px: int) -> float:
        rel = px - self.rect.x - 4
        span = self.rect.width - 8 - self._thumb_width
        if span <= 0:
            return self.min_val
        t = max(0, min(1, rel / span))
        return self.min_val + t * (self.max_val - self.min_val)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._dragging = True
                self.value = self._x_to_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging:
                self._dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            self.value = self._x_to_value(event.pos[0])
            return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        font = get_font(18)
        # Label
        if self.label:
            text = font.render(self.label, True, COLOR_LABEL)
            screen.blit(text, (self.rect.x, self.rect.y - 16))
        # Track
        track_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 10, self.rect.width - 8, 8)
        pygame.draw.rect(screen, COLOR_SLIDER_TRACK, track_rect)
        # Filled portion
        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * track_rect.width) if self.max_val != self.min_val else 0
        if fill_width > 0:
            pygame.draw.rect(screen, COLOR_SLIDER_FILL, (track_rect.x, track_rect.y, fill_width, track_rect.height))
        # Thumb
        thumb_x = self._value_to_x(self.value) - self._thumb_width // 2
        thumb_rect = pygame.Rect(thumb_x, self.rect.y + 4, self._thumb_width, 20)
        pygame.draw.rect(screen, COLOR_SLIDER_THUMB, thumb_rect)
        pygame.draw.rect(screen, (150, 180, 220), thumb_rect, 1)
        # Value text
        val_str = f"{self.value:.{self.decimals}f}"
        val_text = font.render(val_str, True, COLOR_LABEL)
        screen.blit(val_text, (self.rect.x + self.rect.width - 45, self.rect.y + 4))


class Button:
    """Clickable button."""

    def __init__(self, x: int, y: int, width: int, height: int, label: str, on_click: Callable[[], None] | None = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.on_click = on_click
        self._hover = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(event.pos)
        return False

    def draw(self, screen: pygame.Surface) -> None:
        color = COLOR_BUTTON_HOVER if self._hover else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, self.rect, 1)
        font = get_font(18)
        text = font.render(self.label, True, COLOR_BUTTON_TEXT)
        tw, th = text.get_size()
        screen.blit(text, (self.rect.x + (self.rect.width - tw) // 2, self.rect.y + (self.rect.height - th) // 2 - 1))


class Checkbox:
    """Toggle checkbox."""

    def __init__(self, x: int, y: int, label: str, checked: bool = True, on_toggle: Callable[[bool], None] | None = None):
        self.rect = pygame.Rect(x, y, 18, 18)
        self.label = label
        self.checked = checked
        self.on_toggle = on_toggle

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_toggle:
                    self.on_toggle(self.checked)
                return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        color = COLOR_CHECK_ON if self.checked else COLOR_CHECK_OFF
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, self.rect, 1)
        font = get_font(18)
        text = font.render(self.label, True, COLOR_LABEL)
        screen.blit(text, (self.rect.x + 24, self.rect.y - 1))


class ControlPanel:
    """Panel containing all interactive controls."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.sliders: list[Slider] = []
        self.buttons: list[Button] = []
        self.checkboxes: list[Checkbox] = []
        self._slider_dragging: Slider | None = None

    def add_slider(self, slider: Slider) -> None:
        self.sliders.append(slider)

    def add_button(self, button: Button) -> None:
        self.buttons.append(button)

    def add_checkbox(self, checkbox: Checkbox) -> None:
        self.checkboxes.append(checkbox)

    def handle_event(self, event: pygame.event.Event) -> bool:
        for slider in self.sliders:
            if slider.handle_event(event):
                return True
        for button in self.buttons:
            if button.handle_event(event):
                return True
        for checkbox in self.checkboxes:
            if checkbox.handle_event(event):
                return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        # Panel background
        pygame.draw.rect(screen, COLOR_PANEL_BG, self.rect)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, self.rect, 1)
        # Title
        font = get_font(22)
        title = font.render("Controls", True, COLOR_LABEL)
        screen.blit(title, (self.rect.x + 12, self.rect.y + 10))
        # Components draw themselves (they're positioned relative to panel)
