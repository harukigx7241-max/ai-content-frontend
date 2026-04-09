"""app/routers/cw.py — Tab2: クラウドワークス系エンドポイント"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.cw import CwProposalRequest, CwProfileRequest, CwPricingRequest
from app.prompts.builders.cw import (
    build_cw_proposal_prompt,
    build_cw_profile_prompt,
    build_cw_pricing_prompt,
)

router = APIRouter(prefix="/api/cw", tags=["crowdworks"])


@router.post("/proposal")
def cw_proposal(p: CwProposalRequest):
    return JSONResponse({"prompt": build_cw_proposal_prompt(p)})


@router.post("/profile")
def cw_profile(p: CwProfileRequest):
    return JSONResponse({"prompt": build_cw_profile_prompt(p)})


@router.post("/pricing")
def cw_pricing(p: CwPricingRequest):
    return JSONResponse({"prompt": build_cw_pricing_prompt(p)})
