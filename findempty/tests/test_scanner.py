import findempty.testhelpers.fs as fs
import findempty.testhelpers.tree as tree
import findempty.cli as cli
import findempty.config as config

import shutil
import sys


WORK_PATH = "test-tree-findempty"


LAYOUT = """
x simple_empty/
x recursively_empty/
x     empty_child_1/
x     empty_child_2/
x         empty_grandchild_2/
x     empty_child_3/
x         empty_grandchild_3/
x contains_ignorable/
x     thumbs.db
x     desktop.ini
x recursively_ignorable/
x     thumbs.db
x     ignorable_child_1/
x         desktop.ini
x     ignorable_child_2/
x         thumbs.db
x         ignorable_grandchild_2/
x             thumbs.db
  simple_not_empty/
      file.txt
  simple_not_empty_with_ignorables/
      file.txt
      thumbs.db
  preserve_empty.app/
  preserve_empty_with_ignorables.app/
      thumbs.db
  recursively_not_empty/
      nonempty_child_1/
          thumbs.db
          nonempty_grandchild_1/
              file.txt
  mixed/
x     simple_empty/
x     recursively_empty/
x         empty_child_1/
x         empty_child_2/
x             empty_grandchild_2/
x         empty_child_3/
x             empty_grandchild_3/
x     contains_ignorable/
x         thumbs.db
x         desktop.ini
x     recursively_ignorable/
x         thumbs.db
x         ignorable_child_1/
x             desktop.ini
x         ignorable_child_2/
x             thumbs.db
x             ignorable_grandchild_2/
x                 thumbs.db
      simple_not_empty/
          file.txt
      simple_not_empty_with_ignorables/
          file.txt
          thumbs.db
      recursively_not_empty/
          nonempty_child_1/
              thumbs.db
              nonempty_grandchild_1/
                  file.txt
      prune/
          kept_1/
              kept_2/
                  force_keep.txt
x                 prune_3/
x                     prune_4/
"""


def parse_layout(string, input_tree, expect_tree):
    layout_lines = string.split("\n")
    tree.parse_build(input_tree, (line[2:] for line in layout_lines))
    tree.parse_build(expect_tree, (
        line[2:]
        for line in layout_lines
        if line[:2] == "  "
    ))


def run(path):
    ignore_func, preserve_func = config.load_default()
    cli.scan(
        (path,),
        ignore_func,
        preserve_func,
        delete=True,
        verbose=2,
        debug=True
    )


def test_deletion():
    input_tree = fs.Mock()
    expect_tree = fs.Mock()
    parse_layout(LAYOUT, input_tree, expect_tree)

    fails = 0

    live_tree = fs.Live(WORK_PATH)
    tree.copy(input_tree, live_tree)

    for mismatch in tree.compare(input_tree, live_tree):
        print(str(mismatch))
        fails += 1
    if fails > 0:
        print("FAIL: sanity check failed")
        return 1

    run(WORK_PATH)

    for mismatch in tree.compare(expect_tree, live_tree):
        print(str(mismatch))
        fails += 1

    if fails == 0:
        print("PASS")
        shutil.rmtree(WORK_PATH)
        return 0
    else:
        print("FAIL")
        return 2
