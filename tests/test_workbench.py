from __future__ import annotations

import unittest
import asyncio
from workbench import ModernWorkbench

class TestModernWorkbench(unittest.TestCase):
    def setUp(self):
        self.workbench = ModernWorkbench()

    def test_initialization(self):
        self.assertEqual(self.workbench.VERSION, "1.2.0")
        self.assertGreater(len(self.workbench.commands), 0)
        self.assertEqual(self.workbench.history, [])

    def test_find_command(self):
        cmd = self.workbench.find_command("help")
        self.assertIsNotNone(cmd)

    def test_suggest_commands(self):
        suggestions = self.workbench.suggest_commands("hlp")
        self.assertIn("help", suggestions)

if __name__ == "__main__":
    unittest.main()
