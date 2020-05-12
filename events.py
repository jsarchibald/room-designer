import pygame

# General UI events
ui_type = pygame.USEREVENT + 1
capture_space_event = pygame.event.Event(ui_type, method="capture_space")
error_listening_event = pygame.event.Event(ui_type, method="done_listening", message="I couldn't understand that.")
done_listening_event = pygame.event.Event(ui_type, method="done_listening", message=None)

error_type = pygame.USEREVENT + 2
error_event = pygame.event.Event(error_type)

# Room design events
design_type = pygame.USEREVENT + 3

# File I/O events
file_type = pygame.USEREVENT + 5
file_new = pygame.event.Event(file_type, method="new")
file_open = pygame.event.Event(file_type, method="open")
file_save = pygame.event.Event(file_type, method="save")
file_export = pygame.event.Event(file_type, method="export")
