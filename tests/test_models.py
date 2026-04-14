from core.models import cache_dir_path, get_downloaded_models, total_cache_size_mb


class TestModels:
    def test_get_downloaded_models_returns_list(self):
        result = get_downloaded_models()
        assert isinstance(result, list)

    def test_total_cache_size_returns_float(self):
        result = total_cache_size_mb()
        assert isinstance(result, float)
        assert result >= 0.0

    def test_cache_dir_path_returns_string(self):
        result = cache_dir_path()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_model_entries_have_expected_fields(self):
        models = get_downloaded_models()
        for m in models:
            assert "repo_id" in m
            assert "size_mb" in m
            assert "nb_files" in m
