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
        dummy_bytes = b"fake_high_confidence"
        result = await perform_cropdoctor_triage(dummy_bytes, "tomatoes")
        assert result["disclaimer_included"] is True
        assert ONSSA_DISCLAIMER in result["response_text"]
        assert "CropDoctor Diagnosis" in result["response_text"]
    asyncio.run(_test())


def test_cropdoctor_triage_medium_confidence():
    async def _test():
        dummy_bytes = b"fake_medium_confidence"
        result = await perform_cropdoctor_triage(dummy_bytes, "tomatoes")
        assert result["confidence_tier"] == "medium"
        assert result["onssa_product_pointer"] is not None
        assert ONSSA_DISCLAIMER in result["response_text"]
    asyncio.run(_test())


def test_cropdoctor_triage_low_confidence_multi_leaf_or_low_light():
    """Verify multi-leaf or low-light image inputs force Low confidence (<50%) omitting chemical product pointers per FR-022."""
    async def _test():
        dummy_bytes = b"fake_low_confidence"
        result = await perform_cropdoctor_triage(dummy_bytes, "tomatoes")
        
        assert result["confidence_tier"] == "low"
        assert result["onssa_product_pointer"] is None
        assert "Suggested treatment class" not in result["response_text"]
        assert "Please reply with a clearer, close-up photograph" in result["response_text"]
        assert result["disclaimer_included"] is True
        assert ONSSA_DISCLAIMER in result["response_text"]
    asyncio.run(_test())


def test_cropdoctor_triage_unreadable_or_non_plant_photo():
    """Verify unreadable or non-plant photo returns request for leaf close-up without diagnosis, tier, or disclaimer per FR-017."""
    async def _test():
        unreadable_bytes = b"unreadable_image"
        result = await perform_cropdoctor_triage(unreadable_bytes, "tomatoes", force_unreadable=True)
        
        assert result["is_unreadable"] is True
        assert result["confidence_tier"] is None
        assert result["onssa_product_pointer"] is None
        assert result["disclaimer_included"] is False
        assert ONSSA_DISCLAIMER not in result["response_text"]
        assert "No plant leaf identified in the photo" in result["response_text"]
    asyncio.run(_test())


def test_cropdoctor_triage_exception_fallback():
    """Verify exceptions during Gemini vision execution safely fallback to unreadable state per FR-023."""
    async def _test():
        invalid_bytes = b"random_corrupted_image_bytes"
        result = await perform_cropdoctor_triage(invalid_bytes, "tomatoes")
        
        assert result["is_unreadable"] is True
        assert result["confidence_score"] == 0.0
        assert result["onssa_product_pointer"] is None
        assert "No plant leaf identified in the photo" in result["response_text"]
    asyncio.run(_test())
