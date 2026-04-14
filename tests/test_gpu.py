from core.gpu import MODEL_VRAM_ESTIMATES, check_vram_sufficient, detect_gpu, get_vram_usage


class TestDetectGpu:
    def test_returns_dict_with_required_keys(self):
        info = detect_gpu()
        assert "device" in info
        assert "device_name" in info
        assert "vram_total_mb" in info
        assert "vram_free_mb" in info
        assert "backend_hint" in info

    def test_device_is_string(self):
        info = detect_gpu()
        assert isinstance(info["device"], str)

    def test_device_name_is_string(self):
        info = detect_gpu()
        assert isinstance(info["device_name"], str)

    def test_vram_values_are_non_negative(self):
        info = detect_gpu()
        assert info["vram_total_mb"] >= 0
        assert info["vram_free_mb"] >= 0


class TestGetVramUsage:
    def test_returns_tuple_of_two_ints(self):
        used, total = get_vram_usage()
        assert isinstance(used, int)
        assert isinstance(total, int)
        assert used >= 0
        assert total >= 0


class TestCheckVramSufficient:
    def test_unknown_model_returns_ok(self):
        ok, msg = check_vram_sufficient("unknown/model", {"vram_total_mb": 8000})
        assert ok is True
        assert msg == ""

    def test_sufficient_vram(self):
        ok, msg = check_vram_sufficient(
            "Qwen/Qwen3.5-0.8B", {"vram_total_mb": 8000}
        )
        assert ok is True

    def test_insufficient_vram(self):
        ok, msg = check_vram_sufficient(
            "Qwen/Qwen3.5-0.8B", {"vram_total_mb": 500}
        )
        assert ok is False
        assert "500" in msg

    def test_tight_fit_warning(self):
        estimated = MODEL_VRAM_ESTIMATES["Qwen/Qwen3.5-0.8B"]
        # Give just barely enough (between 80% and 100%)
        tight_vram = int(estimated * 1.1)
        ok, msg = check_vram_sufficient(
            "Qwen/Qwen3.5-0.8B", {"vram_total_mb": tight_vram}
        )
        assert ok is True
        assert "tight" in msg

    def test_zero_vram_skips_check(self):
        ok, msg = check_vram_sufficient("Qwen/Qwen3.5-0.8B", {"vram_total_mb": 0})
        assert ok is True


class TestModelVramEstimates:
    def test_known_model_has_estimate(self):
        assert "Qwen/Qwen3.5-0.8B" in MODEL_VRAM_ESTIMATES
        assert MODEL_VRAM_ESTIMATES["Qwen/Qwen3.5-0.8B"] > 0
