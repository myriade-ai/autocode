from pathlib import Path

from autocode.export import collect_files_content

tests_dir = Path(__file__).parent
package_lock = tests_dir / "package-lock.test.json"


def test_collect_files_content_compiles_long_files():
    # display the content of the file
    files = collect_files_content(tests_dir, set([package_lock]))
    assert files[0][1] == "compiled - 2198 lines"
