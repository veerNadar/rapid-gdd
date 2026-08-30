import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import ReviewCreate, ReviewSectionFeedbackUpdate

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/")
def list_reviews(project_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/")
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{review_id}")
def get_review(review_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{review_id}/feedback")
def list_review_feedback(review_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.patch("/feedback/{feedback_id}")
def update_review_feedback(
    feedback_id: uuid.UUID,
    payload: ReviewSectionFeedbackUpdate,
    db: Session = Depends(get_db),
):
    raise NotImplementedError
