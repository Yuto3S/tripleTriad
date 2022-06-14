MAX_ASCEND = 10
MIN_DESCEND = 1


class Card:
    top: int
    left: int
    right: int
    bottom: int
    card_id: int
    card_type: int
    game_id: str

    def __init__(self, top, left, right, bottom, card_id, card_type, game_id=None):
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        self.card_id = card_id
        self.card_type = card_type
        self.game_id = game_id

    @classmethod
    def from_card(cls, existing_card):
        return cls(
            existing_card.top,
            existing_card.left,
            existing_card.right,
            existing_card.bottom,
            existing_card.card_id,
            existing_card.card_type,
            existing_card.game_id,
        )

    def update_game_id(self, color):
        if self.game_id:
            return

        self.game_id = f"{self.card_id}{color}"

    def ascend(self):
        self.top = min(MAX_ASCEND, self.top + 1)
        self.bottom = min(MAX_ASCEND, self.bottom + 1)
        self.left = min(MAX_ASCEND, self.left + 1)
        self.right = min(MAX_ASCEND, self.right + 1)

    def descend(self):
        self.top = max(MIN_DESCEND, self.top - 1)
        self.bottom = max(MIN_DESCEND, self.bottom - 1)
        self.left = max(MIN_DESCEND, self.left - 1)
        self.right = max(MIN_DESCEND, self.right - 1)

    #  TODO: Update direction values to Enum
    def get_direction(self, direction):
        match direction:
            case "top":
                return self.top
            case "bottom":
                return self.bottom
            case "left":
                return self.left
            case "right":
                return self.right

        raise Exception(f"Could not match '{direction}' to any direction")

    def get_opposite_direction(self, direction):
        match direction:
            case "top":
                return self.bottom
            case "bottom":
                return self.top
            case "left":
                return self.right
            case "right":
                return self.left

        raise Exception(f"Could not match '{direction}' to any direction")
