from fastapi import APIRouter

from api.customers import customer_operation_router


router = APIRouter()
router.include_router(customer_operation_router)