"""Headless acceptance checks for the redesigned UI shell."""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_registry():
    from src.ui.tool_registry import TOOLS, get_tool, pdf_tools, tools_for_section

    assert len(TOOLS) == 12
    assert [s for s in ("Tools", "Converter", "Security", "Automation", "Library")
            if tools_for_section(s)] == ["Tools", "Converter", "Security", "Automation", "Library"]
    assert get_tool("merge").input_mode == "multi_pdf"
    assert get_tool("images to pdf").input_mode == "multi_image"
    assert get_tool("batch").panel_key is None
    assert all(t.key in {p.key for p in pdf_tools()} for t in (get_tool("merge"), get_tool("compress")))
    assert get_tool("does-not-exist") is None


def test_session_rules():
    from src.core.models import PdfFile
    from src.ui.tool_registry import get_tool
    from src.ui.widgets.tool_session import ToolSession

    def pdf(name):
        return PdfFile(path=Path(name), name=name, page_count=3)

    single = ToolSession(get_tool("compress"))
    assert single.add_pdfs([pdf("a.pdf"), pdf("b.pdf")]) == [single.files[0]]
    assert len(single.files) == 1
    assert single.add_pdfs([pdf("c.pdf")]) == []

    multi = ToolSession(get_tool("merge"))
    assert len(multi.add_pdfs([pdf("a.pdf"), pdf("b.pdf"), pdf("c.pdf")])) == 3
    multi.move(2, -1)
    assert [p.name for p in multi.files] == ["a.pdf", "c.pdf", "b.pdf"]
    multi.remove_at(0)
    assert [p.name for p in multi.files] == ["c.pdf", "b.pdf"]

    images = ToolSession(get_tool("images to pdf"))
    assert images.add_pdfs([pdf("a.pdf")]) == []
    assert images.add_images([Path("x.png"), Path("bad.txt")]) == [Path("x.png")]


def main():
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    failures = []
    for name, fn in tests:
        try:
            fn()
            print(f"  [PASS] {name}")
        except Exception as exc:  # noqa: BLE001 - test runner reports all failures
            failures.append((name, exc))
            print(f"  [FAIL] {name}: {exc}")
    print()
    if failures:
        print(f"RESULT: {len(failures)}/{len(tests)} redesign checks failed")
        return False
    print(f"RESULT: all {len(tests)} redesign checks passed")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
