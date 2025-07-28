"""
Localized help generation service for the Telegram bot.

Provides localized help text generation that respects user language preferences.
"""

from typing import Optional, List, Dict, Any
from aiogram.types import User

from core.handlers.registry import get_registry
from core.handlers.types import HandlerCategory, HandlerType
from core.utils.logger import get_logger
from business.services.localization import t, get_localization_service

logger = get_logger()


class LocalizedHelpService:
    """
    Service for generating localized help text from registered handlers.
    
    Features:
    - Generates help text in user's preferred language
    - Uses localization keys for descriptions instead of hardcoded metadata
    - Supports category filtering
    - Maintains consistent formatting across languages
    """
    
    def __init__(self):
        """Initialize the localized help service."""
        self.registry = get_registry()
        self.localization_service = get_localization_service()
    
    def generate_help_text(
        self, 
        user: User, 
        category: Optional[HandlerCategory] = None
    ) -> str:
        """
        Generate localized help text for a user.
        
        Args:
            user: Telegram user for language detection
            category: Optional category to filter by
            
        Returns:
            Localized help text in HTML format
        """
        try:
            # Get handlers to include
            if category:
                handlers = self.registry.get_handlers_by_category(category)
                title = self._get_category_title(user, category)
            else:
                handlers = [h for h in self.registry.get_all_handlers() if not h.metadata.hidden]
                title = t("commands.help.header", user=user)
            
            if not handlers:
                return title + "\n\n" + t("commands.help.no_commands", user=user)
            
            # Group handlers by category
            by_category = self._group_by_category(handlers)
            
            # Build help text
            help_sections = [f"<b>{title}</b>\n"]
            
            for cat in HandlerCategory:
                cat_handlers = by_category.get(cat, [])
                if not cat_handlers:
                    continue
                
                # Add category header
                category_name = self._get_category_name(user, cat)
                help_sections.append(f"<b>{category_name}</b>")
                
                # Add commands in this category
                for handler in sorted(cat_handlers, key=lambda h: h.metadata.command or ""):
                    if handler.metadata.handler_type == HandlerType.COMMAND:
                        command_help = self._format_command_help(user, handler)
                        help_sections.append(command_help)
                
                help_sections.append("")  # Empty line between categories
            
            return "\n".join(help_sections).strip()
            
        except Exception as e:
            logger.error(f"Error generating localized help: {e}")
            # Fallback to error message
            return t("errors.help_generation_failed", user=user)
    
    def _group_by_category(self, handlers) -> Dict[HandlerCategory, List[Any]]:
        """Group handlers by category."""
        by_category = {}
        for cat in HandlerCategory:
            by_category[cat] = []
        
        for handler in handlers:
            if handler.metadata.handler_type == HandlerType.COMMAND:
                by_category[handler.metadata.category].append(handler)
        
        return by_category
    
    def _get_category_title(self, user: User, category: HandlerCategory) -> str:
        """Get localized category title for filtered help."""
        category_name = self._get_category_name(user, category)
        return t("commands.help.category_header", user=user, category=category_name)
    
    def _get_category_name(self, user: User, category: HandlerCategory) -> str:
        """Get localized category name."""
        category_key = f"commands.help.category_{category.value.lower()}"
        return t(category_key, user=user)
    
    def _format_command_help(self, user: User, handler) -> str:
        """Format help text for a single command."""
        cmd = handler.metadata.command
        
        # Get localized description using command-specific key
        desc_key = f"commands.{cmd}.description"
        description = t(desc_key, user=user)
        
        # Build command help line
        help_line = f"  /{cmd} - {description}"
        
        # Add usage if different from basic command
        usage = handler.metadata.usage
        if usage and usage != f"/{cmd}":
            usage_label = t("commands.help.usage_label", user=user)
            help_line += f"\n    {usage_label} {usage}"
        
        # Add examples if available
        if handler.metadata.examples:
            examples_label = t("commands.help.examples_label", user=user)
            examples = ", ".join(handler.metadata.examples)
            help_line += f"\n    {examples_label} {examples}"
        
        return help_line
    
    def get_command_help(self, user: User, command: str) -> Optional[str]:
        """
        Get detailed help for a specific command.
        
        Args:
            user: Telegram user for language detection
            command: Command name (without /)
            
        Returns:
            Detailed help text for the command, or None if not found
        """
        try:
            handlers = self.registry.get_all_handlers()
            
            for handler in handlers:
                if (handler.metadata.command == command or 
                    command in handler.metadata.aliases):
                    
                    # Get localized description
                    desc_key = f"commands.{handler.metadata.command}.description"
                    description = t(desc_key, user=user)
                    
                    help_text = [f"<b>/{command}</b> - {description}"]
                    
                    # Add usage
                    if handler.metadata.usage:
                        usage_label = t("commands.help.usage_label", user=user)
                        help_text.append(f"{usage_label} {handler.metadata.usage}")
                    
                    # Add examples
                    if handler.metadata.examples:
                        examples_label = t("commands.help.examples_label", user=user)
                        examples = "\n".join([f"  {ex}" for ex in handler.metadata.examples])
                        help_text.append(f"{examples_label}\n{examples}")
                    
                    # Add aliases
                    if handler.metadata.aliases:
                        aliases_text = ", ".join([f"/{alias}" for alias in handler.metadata.aliases])
                        help_text.append(f"Aliases: {aliases_text}")
                    
                    return "\n\n".join(help_text)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting command help for '{command}': {e}")
            return None


# Global service instance
_help_service: Optional[LocalizedHelpService] = None


def get_help_service() -> LocalizedHelpService:
    """Get the global localized help service instance."""
    global _help_service
    if _help_service is None:
        _help_service = LocalizedHelpService()
    return _help_service


def generate_localized_help(
    user: User, 
    category: Optional[HandlerCategory] = None
) -> str:
    """
    Convenience function for generating localized help.
    
    Args:
        user: Telegram user for language detection
        category: Optional category to filter by
        
    Returns:
        Localized help text
    """
    return get_help_service().generate_help_text(user, category) 