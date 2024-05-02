from django.apps import AppConfig


class BulletinBoardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bulletin_board'

    def ready(self):
        import bulletin_board.signals

