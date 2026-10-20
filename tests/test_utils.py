import unittest
from utils import is_potentially_dangerous, copy_to_clipboard


class TestUtils(unittest.TestCase):

    def test_dangerous_patterns_detection(self):
        dangerous_commands = [
            "rm -rf /",
            "rm -rf /*",
            "format C:",
            "format d:",
            "del /f /s /q c:",
            "rd /s /q c:",
            "mkfs /dev/sda",
            "dd if=/dev/zero of=/dev/sda",
            "> /dev/sda",
            ":(){ :|:& };:",
            "chmod -R 777 /",
        ]
        for cmd in dangerous_commands:
            with self.subTest(cmd=cmd):
                self.assertTrue(
                    is_potentially_dangerous(cmd),
                    f"Se esperaba que '{cmd}' fuera detectado como peligroso."
                )

    def test_safe_commands_allowed(self):
        safe_commands = [
            "ls -la",
            "git status",
            "nmap -sS -p 80,443 192.168.1.1",
            "docker ps -a",
            "python -m venv .venv",
            "Get-Process | Where-Object { $_.CPU -gt 10 }",
            "cat /var/log/syslog | grep error",
            "curl -I https://example.com",
            "tar -czvf backup.tar.gz ./src",
        ]
        for cmd in safe_commands:
            with self.subTest(cmd=cmd):
                self.assertFalse(
                    is_potentially_dangerous(cmd),
                    f"'{cmd}' no debería ser marcado como peligroso."
                )

    def test_copy_empty_string_returns_false(self):
        self.assertFalse(copy_to_clipboard(""))
        self.assertFalse(copy_to_clipboard("   \n\t  "))


if __name__ == "__main__":
    unittest.main()
