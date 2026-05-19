from __future__ import annotations

import unittest
from commands import Command, command
from workbench import ModernWorkbench, CommandManager

class TestCommands(unittest.TestCase):
    def test_command_matching(self):
        cmd = Command(
            name="test",
            label="Test Command",
            description="A test command",
            handler=lambda x, y: None,
            aliases=("t", "testing")
        )
        
        self.assertTrue(cmd.matches("test"))
        self.assertTrue(cmd.matches("TEST"))
        self.assertTrue(cmd.matches("t"))
        self.assertTrue(cmd.matches("testing"))
        self.assertFalse(cmd.matches("other"))

    def test_command_decorator(self):
        @command(name="decorated", label="Deco", description="Desc")
        async def mock_handler(wb, argv):
            pass
            
        self.assertTrue(hasattr(mock_handler, "_command_metadata"))
        self.assertEqual(mock_handler._command_metadata["name"], "decorated")

class TestCommandManager(unittest.TestCase):
    def setUp(self):
        self.workbench = ModernWorkbench()
        self.manager = self.workbench.command_manager

    def test_find_command(self):
        cmd = self.manager.find_command("help")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "help")

    def test_find_command_by_prefix(self):
        cmd = self.manager.find_command_by_prefix("he")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "help")

    def test_suggest_commands(self):
        suggestions = self.manager.suggest_commands("hlp")
        self.assertIn("help", suggestions)

if __name__ == "__main__":
    unittest.main()
