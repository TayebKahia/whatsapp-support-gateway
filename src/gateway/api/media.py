from fastapi import APIRouter, HTTPException, Response, status

from gateway.repository.order import InMemoryOrderRepository, OrderRepository
from gateway.services.pdf_generator import generate_return_label_pdf


def create_media_router(order_repo: OrderRepository | None = None) -> APIRouter:
    router = APIRouter(prefix="/media", tags=["Media"])
    repo = order_repo or InMemoryOrderRepository()

    @router.get("/return-labels/{order_id}.pdf")
    async def get_return_label_pdf(order_id: str) -> Response:
        order = repo.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found",
            )

        rma_code = (
            f"RET-{order.order_id.replace('ORD-', '').replace('#', '')}-{order.order_id[-4:]}99"
        )
        pdf_bytes = generate_return_label_pdf(
            order_id=order.order_id,
            customer_phone=order.customer_phone,
            items=order.items,
            rma_code=rma_code,
            carrier="FedEx Return Service",
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=return_label_{order.order_id}.pdf",
                "Cache-Control": "public, max-age=3600",
            },
        )

    return router
