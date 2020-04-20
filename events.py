import pygame

capture_space_type = pygame.USEREVENT + 1
capture_space_event = pygame.event.Event(capture_space_type)

what_space_type = pygame.USEREVENT + 2
what_space_event = pygame.event.Event(what_space_type)