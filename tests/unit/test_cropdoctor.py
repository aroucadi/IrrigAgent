import asyncio
from app.cropdoctor import lookup_onssa_product, perform_cropdoctor_triage, ONSSA_DISCLAIMER


def test_static_onssa_lookup():
    product = lookup_onssa_product("tomatoes", "tuta_absoluta")
    assert product is not None
    assert "Spinosad" in product


def test_static_onssa_lookup_unknown():
    product = lookup_onssa_product("tomatoes", "unknown_fungus")
    assert product is None


def test_cropdoctor_triage_high_confidence():
    async def _test():
        dummy_bytes = b"fake_image_data"
        result = await perform_cropdoctor_triage(dummy_bytes, "tomatoes")
        assert result["disclaimer_included"] is True
        assert ONSSA_DISCLAIMER in result["response_text"]
        assert "CropDoctor Diagnosis" in result["response_text"]
    
    asyncio.run(_test())
