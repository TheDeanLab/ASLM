import random
import tkinter as tk

import pytest


@pytest.fixture
def tk_root():
    root = tk.Tk()
    yield root
    root.destroy()


@pytest.fixture
def entry(tk_root):
    from aslm.view.custom_widgets.validation import ValidatedEntry

    entry = ValidatedEntry(tk_root, textvariable=tk.DoubleVar())

    yield entry


def test_add_history(entry):
    # TODO: Why does this not work with textvariable=tk.StringVar()??
    entry.set("42")
    entry.add_history(0)
    assert entry.undo_history.pop() == "42"


def test_undo(entry):
    # base case
    entry.set("42")
    entry.add_history(0)
    entry.undo(0)
    assert entry.get() == "42"

    # regular undo
    entry.set("42")
    entry.add_history(0)
    entry.set("43")
    entry.add_history(0)
    entry.undo(0)
    assert entry.get() == "42"
    assert entry.redo_history.pop() == "43"


def test_redo(entry):
    entry.set("42")
    entry.add_history(0)
    entry.set("43")
    entry.add_history(0)
    entry.undo(0)
    assert entry.get() == "42"
    entry.redo(0)
    assert entry.get() == "43"
    assert entry.undo_history == ["42", "43"]


def test_undo_redo(entry):
    # Random number of entries
    vals = [str(random.randint(1, 100)) for _ in range(random.randint(3, 5))]
    for val in vals:
        entry.set(val)
        entry.add_history(0)

    n_tries = random.randint(1, 10)
    for _ in range(n_tries):
        entry.undo(0)
        assert entry.redo_history == [vals[-1]]
        assert entry.get() == vals[-2]
        assert entry.undo_history == [vals[-3]]
        entry.redo(0)
        assert entry.get() == vals[-1]
        assert entry.undo_history == vals[-3:]
        assert entry.redo_history == []
