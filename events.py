import pygame

capture_space_type = pygame.USEREVENT + 1
capture_space_event = pygame.event.Event(capture_space_type)

done_listening_type = pygame.USEREVENT + 2
done_listening_event = pygame.event.Event(done_listening_type)

error_type = pygame.USEREVENT + 3
error_event = pygame.event.Event(error_type)

create_type = pygame.USEREVENT + 4