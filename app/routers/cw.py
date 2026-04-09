"""app/routers/cw.py — Tab2: クラウドワークス系エンドポイント"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.cw import CwProposalRequest, CwProfileRequest, CwPricingRequest
from app.prompts.builders.cw import (
    build_cw_proposal_prompt,
    build_cw_profile_prompt,
    build_cw_pricing_prompt,
)
from app.services.generate_service import dispatch

router = APIRouter(prefix="/api/cw", tags=["crowdworks"])


@router.post("/proposal")
def cw_proposal(p: CwProposalRequest):
    prompt, meta = dispatch(p, build_cw_proposal_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/profile")
def cw_profile(p: CwProfileRequest):
    prompt, meta = dispatch(p, build_cw_profile_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})


@router.post("/pricing")
def cw_pricing(p: CwPricingRequest):
    prompt, meta = dispatch(p, build_cw_pricing_prompt)
    return JSONResponse({"prompt": prompt, "meta": meta})
