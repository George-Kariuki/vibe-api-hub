import random

from fastapi import APIRouter

from app.models.lists import RandomPickRequest, RandomPickResponse

router = APIRouter(prefix="/lists", tags=["List Utilities"])


@router.post(
    "/random-pick",
    response_model=RandomPickResponse,
    summary="Pick N random items from a list",
    description=(
        "Pick multiple random items from a provided list in a single call. \n\n"
        "This solves the common no-code limitation where random pickers only return one item. \n\n"
        "- `allow_duplicates: false` (default): picks are unique. If `count >= len(items)`, "
        "the API returns **all items** in randomized order.\n"
        "- `allow_duplicates: true`: picks may repeat and `count` can exceed the number of items.\n\n"
        "Optional `seed` provides deterministic results for testing/workflows."
    ),
)
async def random_pick(body: RandomPickRequest) -> RandomPickResponse:
    rng = random.Random(body.seed)
    items = body.items

    if body.allow_duplicates:
        picks = rng.choices(items, k=body.count)
    else:
        if body.count >= len(items):
            picks = list(items)
            rng.shuffle(picks)
        else:
            picks = rng.sample(items, k=body.count)

    return RandomPickResponse(
        picks=picks,
        count_requested=body.count,
        count_returned=len(picks),
        input_size=len(items),
        allow_duplicates=body.allow_duplicates,
        seed=body.seed,
    )

