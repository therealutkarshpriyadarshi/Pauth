"""
OAuth provider definitions and enumerations.
"""

from enum import Enum
from typing import Type

from src.providers.base import BaseProvider
from src.providers.google import GoogleProvider
from src.providers.github import GithubProvider
from src.providers.facebook import FacebookProvider
from src.providers.twitter import TwitterProvider
from src.providers.microsoft import MicrosoftProvider
from src.providers.linkedin import LinkedInProvider
from src.providers.discord import DiscordProvider
from src.providers.apple import AppleProvider


class Providers(Enum):
    """
    Enumeration of supported OAuth providers.

    Each provider enum value maps to its corresponding provider class.
    """

    GOOGLE = "google"
    GITHUB = "github"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    MICROSOFT = "microsoft"
    LINKEDIN = "linkedin"
    DISCORD = "discord"
    APPLE = "apple"

    def get_provider_class(self) -> Type[BaseProvider]:
        """
        Get the provider class for this enum value.

        Returns:
            Type[BaseProvider]: The provider class

        Raises:
            NotImplementedError: If provider is not yet implemented
        """
        provider_map = {
            Providers.GOOGLE: GoogleProvider,
            Providers.GITHUB: GithubProvider,
            Providers.FACEBOOK: FacebookProvider,
            Providers.TWITTER: TwitterProvider,
            Providers.MICROSOFT: MicrosoftProvider,
            Providers.LINKEDIN: LinkedInProvider,
            Providers.DISCORD: DiscordProvider,
            Providers.APPLE: AppleProvider,
        }

        if self not in provider_map:
            raise NotImplementedError(
                f"{self.value} provider is not yet implemented. "
                f"Available providers: {', '.join(p.value for p in provider_map.keys())}"
            )

        return provider_map[self]

    @property
    def display_name(self) -> str:
        """
        Get the display name for this provider.

        Returns:
            str: Display name
        """
        display_names = {
            Providers.GOOGLE: "Google",
            Providers.GITHUB: "GitHub",
            Providers.FACEBOOK: "Facebook",
            Providers.TWITTER: "Twitter (X)",
            Providers.MICROSOFT: "Microsoft",
            Providers.LINKEDIN: "LinkedIn",
            Providers.DISCORD: "Discord",
            Providers.APPLE: "Apple",
        }
        return display_names.get(self, self.value.title())

    @classmethod
    def from_string(cls, provider_name: str) -> 'Providers':
        """
        Get provider enum from string name.

        Args:
            provider_name (str): Provider name (case-insensitive)

        Returns:
            Providers: Provider enum value

        Raises:
            ValueError: If provider name is invalid
        """
        provider_name = provider_name.lower()
        for provider in cls:
            if provider.value == provider_name:
                return provider
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {', '.join(p.value for p in cls)}"
        )
