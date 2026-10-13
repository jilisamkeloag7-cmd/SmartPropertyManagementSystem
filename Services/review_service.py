
from Repositories.review_repository import ReviewRepository
from Repositories.property_repository import PropertyRepository
from Repositories.lease_repository import LeaseRepository
from Repositories.user_repository import UserRepository


MANAGER_ROLES = {"Administrator", "Property Manager"}


class ReviewService:
    def __init__(self):
        self.reviews = ReviewRepository()
        self.properties = PropertyRepository()
        self.leases = LeaseRepository()
        self.users = UserRepository()

    # ------------------------------------------------------------------ helpers
    def _enrich(self, r):
        reviewer = self.users.find_by_id(r.reviewer_id)
        # Show only first name + initial for privacy
        name = ""
        if reviewer:
            parts = (reviewer.name or "").split()
            if len(parts) >= 2:
                name = f"{parts[0]} {parts[1][0]}."
            elif parts:
                name = parts[0]
        return {
            "review_id": r.review_id,
            "property_id": r.property_id,
            "reviewer_id": r.reviewer_id,
            "reviewer_name": name or "Anonymous",
            "rating": r.rating,
            "comment": r.comment or "",
            "created_at": r.created_at,
        }

    def _has_lease_history(self, user_id: int, property_id: int) -> bool:
        """Tenant must have (or have had) a lease on the property to review it."""
        leases = self.leases.list_for_tenant(user_id)
        return any(l.property_id == property_id for l in leases)

    # ------------------------------------------------------------------ reads
    def list_for_property(self, property_id: int):
        rows = self.reviews.list_for_property(property_id)
        return [self._enrich(r) for r in rows]

    def average_for_property(self, property_id: int):
        return self.reviews.average_for_property(property_id)

    # ------------------------------------------------------------------ writes
    def create_review(self, property_id: int, rating: int, comment: str,
                       session_user: dict):
        role = session_user.get("role", "")
        uid = session_user.get("user_id")

        if role != "Tenant":
            return False, "Only tenants can leave reviews."

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            return False, "Rating must be a number."

        if rating < 1 or rating > 5:
            return False, "Rating must be between 1 and 5."

        prop = self.properties.find_by_id(property_id)
        if not prop:
            return False, "Property not found."

        if not self._has_lease_history(uid, property_id):
            return False, "You can only review properties you have leased."

        existing = self.reviews.find_by_reviewer_and_property(uid, property_id)
        if existing:
            return False, "You have already reviewed this property."

        comment = (comment or "").strip()
        if len(comment) > 1000:
            return False, "Comment is too long (max 1000 characters)."

        self.reviews.create(property_id, uid, rating, comment or None)
        return True, "Review submitted. Thank you!"

    def delete_review(self, review_id: int, session_user: dict):
        role = session_user.get("role", "")
        if role not in MANAGER_ROLES:
            return False, "Only managers or administrators can remove reviews."

        ok = self.reviews.delete(review_id)
        return (True, "Review removed.") if ok else (False, "Review not found.")
