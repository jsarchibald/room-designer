import pygame

# General UI events
ui_type = pygame.USEREVENT + 1
capture_space_event = pygame.event.Event(ui_type, method="capture_space")
done_listening_event = pygame.event.Event(ui_type, method="done_listening")

error_type = pygame.USEREVENT + 3
error_event = pygame.event.Event(error_type)

# Room design events
create_type = pygame.USEREVENT + 4
delete_type = pygame.USEREVENT + 5

# File I/O events
file_type = pygame.USEREVENT + 6
file_new = pygame.event.Event(file_type, method="new")
file_open = pygame.event.Event(file_type, method="open")
file_save = pygame.event.Event(file_type, method="save")
