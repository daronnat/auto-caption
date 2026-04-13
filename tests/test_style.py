from core.style import apply_style, STYLE_NAMES, STYLE_INSTRUCTIONS


class TestApplyStyle:
    def test_snake_case(self):
        assert apply_style("My Beautiful Photo", "snake_case") == "my_beautiful_photo"

    def test_camel_case(self):
        assert apply_style("My Beautiful Photo", "camelCase") == "myBeautifulPhoto"

    def test_kebab_case(self):
        assert apply_style("My Beautiful Photo", "kebab-case") == "my-beautiful-photo"

    def test_title_case(self):
        assert apply_style("my beautiful photo", "Title Case") == "My Beautiful Photo"

    def test_empty_input(self):
        assert apply_style("", "snake_case") == "untitled"

    def test_whitespace_only(self):
        assert apply_style("   ", "snake_case") == "untitled"

    def test_single_word(self):
        assert apply_style("hello", "camelCase") == "hello"

    def test_mixed_separators(self):
        assert apply_style("hello-world_foo bar", "snake_case") == "hello_world_foo_bar"

    def test_leading_trailing_spaces(self):
        assert apply_style("  hello world  ", "kebab-case") == "hello-world"

    def test_unknown_style_defaults_to_snake(self):
        assert apply_style("Hello World", "unknown") == "hello_world"


class TestStyleConstants:
    def test_style_names_not_empty(self):
        assert len(STYLE_NAMES) >= 4

    def test_instructions_match_names(self):
        for name in STYLE_NAMES:
            assert name in STYLE_INSTRUCTIONS
