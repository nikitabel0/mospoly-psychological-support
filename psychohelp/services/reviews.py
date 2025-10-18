from psychohelp.repositories.reviews import UUID, get_review


def get_review_by_id(appointment_id: UUID):
    return get_review(appointment_id)
