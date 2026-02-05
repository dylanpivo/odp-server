import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp.api.lib.auth import Authorize
from odp.api.lib.nextcloud import upload_file_to_nextcloud, delete_folder_from_nextcloud
from odp.api.lib.paging import Paginator
from odp.api.models import SubmissionModelIn, SubmissionListItemModel
from odp.const import ODPScope
from odp.const.db import SubmissionStatus
from odp.db import Session
from odp.db.models import Submission

router = APIRouter()


def submission_list_item_model(submission: Submission) -> SubmissionListItemModel:
    return SubmissionListItemModel(
        id=submission.id,
        title=submission.data.get('title'),
        status=submission.status
    )


@router.post(
    '/',
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def create_submission(
        submission_in: SubmissionModelIn,
):
    submission = Submission(
        data=submission_in.data,
        user_id=submission_in.user_id,
        status=SubmissionStatus.editing
    )

    submission.save()

    return submission


@router.put(
    '/{submission_id}/upload',
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def dataset_upload(
        submission_id: int,
        file: UploadFile = File(...)
):
    if not (submission := Session.get(Submission, submission_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    temp_dir = Path(f'temp_uploads/{submission_id}')

    if not temp_dir.exists():
        temp_dir.mkdir(parents=True, exist_ok=True)

    local_path_to_file = temp_dir / file.filename

    try:
        with open(local_path_to_file, "wb") as f:
            f.write(file.file.read())

        upload_file_to_nextcloud(local_path_to_file, submission_id, file.filename)

        submission.dataset_file_name = file.filename
        submission.save()
    finally:
        if os.path.exists(local_path_to_file):
            os.remove(local_path_to_file)

        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

        await file.close()


@router.put(
    '/{submission_id}',
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))]
)
async def update_submission(
        submission_id: int,
        submission_data: dict[str, Any],
        user_id: str,
):
    statement = select(Submission).where(
        Submission.id == submission_id,
        Submission.user_id == user_id
    )

    result = Session.execute(statement)
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found or unauthorized"
        )

    submission.data = submission_data

    submission.save()

    return submission


@router.post(
    '/submit/{submission_id}',
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def submit_submission(
        submission_id: int,
):
    if not (submission := Session.get(Submission, submission_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    submission.status = SubmissionStatus.submitted

    submission.save()

    return submission


@router.get(
    '/',
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def list_submissions(
        paginator: Paginator = Depends(),
        status: str = 'all'
):
    stmt = (select(Submission))

    if not status == 'all' and status in [s.value for s in SubmissionStatus]:
        stmt = stmt.where(Submission.status == status)

    return paginator.paginate(
        stmt,
        lambda row: submission_list_item_model(row.Submission),
        sort='submission.id'
    )


@router.get(
    '/user_submissions',
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def list_user_submissions(
        user_id: str,
        paginator: Paginator = Depends(),
):
    stmt = (select(Submission).where(Submission.user_id == user_id))

    return paginator.paginate(
        stmt,
        lambda row: submission_list_item_model(row.Submission),
        sort='submission.id'
    )


@router.get(
    '/{submission_id}',
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def get_submission(
        submission_id: int,
        user_id: str,
):
    stmt = select(Submission).where(
        Submission.id == submission_id,
        Submission.user_id == user_id
    )

    result = Session.execute(stmt)
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


@router.get(
    '/admin/{submission_id}',
    dependencies=[Depends(Authorize(ODPScope.RECORD_READ))],
)
async def get_submission(
        submission_id: int
):
    if not (submission := Session.get(Submission, submission_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


@router.delete(
    '/{submission_id}',
    dependencies=[Depends(Authorize(ODPScope.CATALOG_READ))],
)
async def delete_submission(
        submission_id: int,
):
    if not (submission := Session.get(Submission, submission_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    delete_folder_from_nextcloud(submission_id)

    submission.delete()
