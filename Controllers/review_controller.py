
from Services.review_service import ReviewService


class ReviewController:
    def __init__(self):
        self.service = ReviewService()

    def list_for_property(self, property_id: int):
        return self.service.list_for_property(property_id)

    def average_for_property(self, property_id: int):
        return self.service.average_for_property(property_id)

    def create(self, property_id: int, rating: int, comment: str,
               session_user: dict):
        return self.service.create_review(property_id, rating, comment, session_user)

    def delete(self, review_id: int, session_user: dict):
        return self.service.delete_review(review_id, session_user)
