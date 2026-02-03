"""Arbiter module for validating and routing AI responses."""

from typing import List, Dict, Optional
from models.message import Message, MessageType
from models.role import Role


class Arbiter:
    """
    GPT Arbiter that validates questions/answers and verifies role assignments.
    Provides quality control through prompt checking.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.validation_rules: List[str] = []
        self.active_roles: List[Role] = []

    def validate_message(self, message: Message) -> bool:
        """
        Validate a message against current rules.

        Args:
            message: Message to validate

        Returns:
            True if message passes validation
        """
        if self.logger:
            self.logger.log(f"Валидация сообщения: {message.content[:50]}...")

        # Check message content is not empty
        if not message.content.strip():
            if self.logger:
                self.logger.log("Валидация провалена: пустое сообщение")
            return False

        # Check against validation rules
        for rule in self.validation_rules:
            if rule.lower() in message.content.lower():
                if self.logger:
                    self.logger.log(f"Валидация провалена: нарушение правила '{rule}'")
                return False

        if self.logger:
            self.logger.log("Валидация успешна ✓")

        return True

    def check_role_assignment(self, role: Role, message: Message) -> Dict[str, any]:
        """
        Check if a role is properly assigned for a message.

        Args:
            role: Role to check
            message: Message context

        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": True,
            "role": role.name,
            "model": role.model,
            "issues": []
        }

        # Check if role necessity matches message context
        # This is a placeholder for actual AI-based validation
        if len(message.content) < 10:
            result["issues"].append("Сообщение слишком короткое для данной роли")
            result["valid"] = False

        if self.logger:
            status = "успешна" if result["valid"] else "провалена"
            self.logger.log(f"Проверка роли '{role.name}': {status}")

        return result

    def arbitrate_responses(self, responses: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Arbitrate between multiple AI responses.

        Args:
            responses: List of responses from different AI models

        Returns:
            Dictionary with arbitration results
        """
        if self.logger:
            self.logger.log(f"Арбитраж {len(responses)} ответов")

        # This is a simulation - in real implementation would use GPT API
        result = {
            "best_response": None,
            "consensus": False,
            "all_responses": responses,
            "issues": []
        }

        if responses:
            # Simple selection - would be replaced with actual AI arbitration
            result["best_response"] = responses[0]
            result["consensus"] = len(responses) == 1

        if self.logger:
            self.logger.log("Арбитраж завершен")

        return result

    def add_validation_rule(self, rule: str) -> None:
        """Add a validation rule."""
        self.validation_rules.append(rule)
        if self.logger:
            self.logger.log(f"Добавлено правило валидации: {rule}")

    def set_active_roles(self, roles: List[Role]) -> None:
        """Set active roles for validation."""
        self.active_roles = roles
        if self.logger:
            self.logger.log(f"Установлено {len(roles)} активных ролей")

    def generate_prompt_check(self, prompt: str, prohibitions: List[str]) -> Dict[str, any]:
        """
        Check a prompt against prohibitions.

        Args:
            prompt: Prompt to check
            prohibitions: List of prohibited content

        Returns:
            Dictionary with check results
        """
        result = {
            "valid": True,
            "violations": [],
            "warnings": []
        }

        for prohibition in prohibitions:
            if prohibition.lower() in prompt.lower():
                result["valid"] = False
                result["violations"].append(prohibition)

        if self.logger:
            status = "принят" if result["valid"] else "отклонен"
            self.logger.log(f"Проверка промпта: {status}")

        return result
