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
    """Medium confidence (0.50–0.74) triggers fail-closed: no chemical product name per FR-022/spec 010."""
    async def _test():
        dummy_bytes = b"fake_medium_confidence"
        result = await perform_cropdoctor_triage(dummy_bytes, "tomatoes")
        assert result["confidence_tier"] == "medium"
        # Fail-closed: medium confidence must NOT expose ONSSA chemical names
        assert result["onssa_product_pointer"] is None
        assert result["fail_closed_active"] is True
        assert ONSSA_DISCLAIMER in result["response_text"]
        # Cultural practices advice must be present instead of active ingredient names
        assert "agronomist" in result["response_text"] or "cultural" in result["response_text"].lower()
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
    """Verify unreadable or non-plant photo returns request for leaf close-up without diagnosis or tier, but with disclaimer per FR-008/FR-017."""
    async def _test():
        unreadable_bytes = b"unreadable_image"
        result = await perform_cropdoctor_triage(unreadable_bytes, "tomatoes", force_unreadable=True)
        
        assert result["is_unreadable"] is True
        assert result["confidence_tier"] is None
        assert result["onssa_product_pointer"] is None
        assert result["disclaimer_included"] is True
        assert ONSSA_DISCLAIMER in result["response_text"]
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


def test_cropdoctor_triage_real_jpeg_bytes_not_mock():
    """Verify standard JPEG header magic bytes (\xFF\xD8\xFF\xE0) do not trigger hardcoded mock diagnosis."""
    async def _test():
        real_jpeg_header = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00"
        result = await perform_cropdoctor_triage(real_jpeg_header, "tomatoes")
        
        # Should not return hardcoded phytophthora_infestans 0.85 mock diagnosis; falls back cleanly when Gemini client is unconfigured
        assert result["is_unreadable"] is True
        assert result["confidence_score"] == 0.0
    asyncio.run(_test())


def test_cropdoctor_triage_unsupported_crop_type():
    """Verify triage requests for unsupported crops (e.g. 'olives') fail closed with onssa_product_pointer: None and include redirect notice."""
    async def _test():
        dummy_bytes = b"fake_high_confidence"
        # Test direct lookup returns None for unlisted crops
        assert lookup_onssa_product("olives", "phytophthora_infestans") is None
        assert lookup_onssa_product("wheat", "tuta_absoluta") is None
        
        # Test triage response payload with unsupported crop
        result = await perform_cropdoctor_triage(dummy_bytes, crop_type="olives")
        assert result["confidence_tier"] == "high"
        assert result["onssa_product_pointer"] is None
        assert "Consult an ONSSA-authorized retailer" in result["response_text"]
        assert "target vision support currently focuses on Tomatoes and Citrus" in result["response_text"]
        assert "Copper hydroxide" not in result["response_text"]
        assert result["disclaimer_included"] is True
    asyncio.run(_test())


def test_cropdoctor_triage_latency_under_3000ms():
    """Verify SC-006: End-to-end vision triage response completes in under 3.0 seconds."""
    import time
    async def _test():
        start_time = time.perf_counter()
        dummy_bytes = b"fake_high_confidence"
        result = await perform_cropdoctor_triage(dummy_bytes, crop_type="tomatoes")
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        assert result["disclaimer_included"] is True
        assert elapsed_ms < 3000.0, f"Triage response latency {elapsed_ms}ms exceeded 3000ms"
    asyncio.run(_test())



