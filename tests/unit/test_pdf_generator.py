from gateway.services.pdf_generator import generate_return_label_pdf


def test_generate_return_label_pdf_valid_header_and_bytes() -> None:
    pdf_bytes = generate_return_label_pdf(
        order_id="ORD-1003",
        customer_phone="15551112233",
        items=["USB-C Multiport Hub", "Braided Charging Cable"],
        rma_code="RET-1003-987654",
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # Standard PDF magic header
    assert pdf_bytes.startswith(b"%PDF-")
    # PDF should contain the trailer
    assert b"%%EOF" in pdf_bytes
