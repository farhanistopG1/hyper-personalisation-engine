"""
💀 MESSAGE GENERATOR 💀

High-converting, emotionally-connected WhatsApp message generation.

Based on proven 10,000+ customer re-engagement format.

Tone: Warm friend who genuinely misses you and wants to reconnect.
NOT a salesperson trying to steal money.
"""

import random
from typing import List

# Support both direct and module imports
try:
    from .schemas import CustomerInput, AIRecommendation, MessageTemplate
except ImportError:
    from schemas import CustomerInput, AIRecommendation, MessageTemplate


class MessageGenerator:
    """
    💀 HIGH-CONVERTING MESSAGE GENERATOR 💀

    Generates emotionally-connected WhatsApp messages for customer re-engagement.

    Proven Structure:
    1. Personal greeting with name
    2. Nostalgia trigger (specific last order)
    3. Emotional connection ("It makes us smile...")
    4. New recommendations (AI-powered)
    5. Reassurance ("Your favorite's still on top")
    6. Concrete CTA with incentives

    Tone: Friend missing you, NOT salesperson
    """

    def __init__(
        self,
        client_name: str = "Pizza Express",
        reservation_link: str = "https://bit.ly/pizzaai-reserve",
        promo_code: str = "Pizza AI",
        discount: str = "10% off",
        free_item: str = "4 free dough balls"
    ):
        self.client_name = client_name
        self.reservation_link = reservation_link
        self.promo_code = promo_code
        self.discount = discount
        self.free_item = free_item

    def generate_message(
        self,
        customer: CustomerInput,
        recommendation: AIRecommendation
    ) -> str:
        """
        Generate high-converting personalized WhatsApp message

        Args:
            customer: Customer data with last order history
            recommendation: AI recommendation with new items

        Returns:
            Full WhatsApp message text (optimized for conversions)
        """
        # Build message sections
        greeting = self._build_greeting(customer)
        nostalgia = self._build_nostalgia_trigger(customer)
        emotional = self._build_emotional_connection()
        recommendations = self._build_new_recommendations(recommendation.recommended_items)
        reassurance = self._build_reassurance()
        cta = self._build_concrete_cta()

        # Combine with proper spacing
        full_message = f"{greeting}\n\n{nostalgia}\n\n{emotional}\n\n{recommendations}\n\n{reassurance}\n\n{cta}"

        return full_message

    def _build_greeting(self, customer: CustomerInput) -> str:
        """Build personal greeting with customer name"""

        if customer.name:
            greetings = [
                f"Hey {customer.name}!",
                f"Hi {customer.name}!",
                f"{customer.name}!",
            ]
            return random.choice(greetings)
        else:
            return "Hey there!"

    def _build_nostalgia_trigger(self, customer: CustomerInput) -> str:
        """
        Build nostalgia trigger using SPECIFIC last order item

        This is the KEY conversion element - specific memory recall
        """
        if customer.last_order_items and len(customer.last_order_items) > 0:
            # Use the first (most recent) item from last order
            last_item = customer.last_order_items[0]

            nostalgia_templates = [
                f"Remember that delicious {last_item} you had last time? 😋",
                f"We still remember your {last_item} order! 🍽️",
                f"That {last_item} you loved last time? We haven't forgotten 💭",
                f"Your {last_item} order is still fresh in our memory! 😊",
            ]

            return random.choice(nostalgia_templates)
        else:
            # Fallback if no last order data
            return "We've been thinking about your last visit! 💭"

    def _build_emotional_connection(self) -> str:
        """Build emotional connection line (friend missing you)"""

        emotional_lines = [
            "It makes us smile just thinking about it! 💚",
            "We miss having you around! 😊",
            "It brings back good memories! ✨",
            "We've been hoping you'd come back! 💭",
            "You're one of our favorites! ❤️",
        ]

        return random.choice(emotional_lines)

    def _build_new_recommendations(self, items: List[str]) -> str:
        """
        Build NEW recommendations section

        Frame as NEW options to try, not replacements
        """
        if not items or len(items) == 0:
            return "We've got some NEW dishes we think you'd love! 🌟"

        # Format recommendations based on count
        if len(items) == 1:
            rec_text = f"We've got a NEW dish we think you'd love – maybe try our {items[0]}? 🍝"
        elif len(items) == 2:
            rec_text = f"We've got some NEW dishes we think you'd love – maybe try our {items[0]}, or our {items[1]}? 🍝"
        else:  # 3+ items
            rec_text = f"We've got some NEW dishes we think you'd love – maybe try our {items[0]}, {items[1]}, or our {items[2]}? 🍝"

        # Add quality statement
        quality_statements = [
            "\n\nThey're both amazing.",
            "\n\nYou're going to love them.",
            "\n\nThey're absolutely delicious.",
            "\n\nThey're getting rave reviews!",
        ]

        return rec_text + random.choice(quality_statements)

    def _build_reassurance(self) -> str:
        """
        Build reassurance section

        Critical: Reassure that their favorite is still available
        """
        reassurance_templates = [
            "Your favorite's still on top. ✨\n\nWe're here. So is your fave.",
            "Don't worry – your favorite's still here waiting for you! 💚",
            "Your go-to dish? Still on the menu and still amazing! 🌟",
            "We're here. Your favorite's here. All that's missing is you! 😊",
        ]

        return random.choice(reassurance_templates)

    def _build_concrete_cta(self) -> str:
        """
        Build concrete CTA with stacked incentives

        This is where conversion happens:
        - Clear action (Reserve table)
        - Concrete incentive (10% off)
        - Clickable link
        - Bonus incentive (free dough balls)
        - Exclusivity code (mention promo)
        """
        cta = f"Reserve your table + {self.discount} → {self.reservation_link}\n\n"
        cta += f"Mention \"{self.promo_code}\" when you visit. Get {self.free_item} 🎉"

        return cta

    def generate_batch_messages(
        self,
        customers: List[CustomerInput],
        recommendations: dict
    ) -> dict:
        """
        Generate messages for multiple customers

        Args:
            customers: List of customers
            recommendations: Dict mapping customer_id to AIRecommendation

        Returns:
            Dict mapping customer_id to generated message
        """
        messages = {}

        for customer in customers:
            recommendation = recommendations.get(customer.customer_id)

            if not recommendation:
                # Fallback message without AI recommendations
                messages[customer.customer_id] = self._generate_fallback_message(customer)
            else:
                messages[customer.customer_id] = self.generate_message(customer, recommendation)

        return messages

    def _generate_fallback_message(self, customer: CustomerInput) -> str:
        """
        Generate fallback message when no AI recommendation available

        Still maintains high-converting structure
        """
        greeting = self._build_greeting(customer)
        nostalgia = self._build_nostalgia_trigger(customer)
        emotional = self._build_emotional_connection()

        # Generic new dishes mention
        new_dishes = "We've got some amazing NEW dishes we think you'd love! 🌟"

        reassurance = self._build_reassurance()
        cta = self._build_concrete_cta()

        return f"{greeting}\n\n{nostalgia}\n\n{emotional}\n\n{new_dishes}\n\n{reassurance}\n\n{cta}"


# ============================================================================
# MESSAGE QUALITY VALIDATION
# ============================================================================

class MessageValidator:
    """
    💀 MESSAGE QUALITY VALIDATOR 💀

    Ensures messages meet quality standards before sending.
    Updated for high-converting format.
    """

    @staticmethod
    def validate_tone(message: str) -> tuple[bool, str]:
        """
        Validate message tone is appropriate

        Returns:
            (is_valid, reason)
        """
        # Forbidden words/phrases (Andrew Tate / aggressive sales tone)
        forbidden = [
            "warrior", "beast mode", "grind", "hustle",
            "alpha", "sigma", "dominate", "conquer",
            "listen up", "wake up", "real talk",
            "limited time", "act now", "hurry", "expires"  # Aggressive sales tactics
        ]

        message_lower = message.lower()

        for word in forbidden:
            if word in message_lower:
                return False, f"Contains forbidden word: '{word}' (too aggressive)"

        # Must contain friendly elements (emojis)
        friendly_indicators = ["😊", "❤️", "💚", "🍕", "😍", "🌟", "✨", "👋", "💭", "🎉", "😋", "🍝", "🍽️"]
        has_emoji = any(indicator in message for indicator in friendly_indicators)

        if not has_emoji:
            return False, "Message lacks friendly emojis"

        return True, "Tone is appropriate"

    @staticmethod
    def validate_length(message: str) -> tuple[bool, str]:
        """
        Validate message length is appropriate for WhatsApp

        Returns:
            (is_valid, reason)
        """
        # Updated for longer high-converting format
        length = len(message)

        if length < 100:
            return False, f"Message too short ({length} chars, min 100)"

        if length > 1500:
            return False, f"Message too long ({length} chars, max 1500)"

        return True, f"Length appropriate ({length} chars)"

    @staticmethod
    def validate_structure(message: str) -> tuple[bool, str]:
        """
        Validate message has proper high-converting structure

        Returns:
            (is_valid, reason)
        """
        # Must have sections (greeting, nostalgia, recommendations, CTA)
        lines = [line.strip() for line in message.split("\n") if line.strip()]

        if len(lines) < 5:
            return False, "Message needs all sections (greeting, nostalgia, emotion, recommendations, reassurance, CTA)"

        # Must have CTA with link
        if "https://" not in message and "http://" not in message:
            return False, "Message must include reservation link"

        # Must mention incentive
        if "free" not in message.lower() and "off" not in message.lower():
            return False, "Message must include concrete incentive (discount or free item)"

        return True, "Structure is valid"

    @staticmethod
    def validate_personalization(message: str, customer: CustomerInput) -> tuple[bool, str]:
        """
        Validate message is properly personalized

        Returns:
            (is_valid, reason)
        """
        # Must include customer name (if available)
        if customer.name and customer.name not in message:
            return False, f"Message missing customer name ({customer.name})"

        # Should reference last order if available
        if customer.last_order_items and len(customer.last_order_items) > 0:
            # Check if any last order item is mentioned
            has_last_order_ref = any(
                item.lower() in message.lower()
                for item in customer.last_order_items
            )
            if not has_last_order_ref:
                return False, "Message missing last order reference (nostalgia trigger)"

        return True, "Personalization is valid"

    @classmethod
    def validate_message(cls, message: str, customer: CustomerInput = None) -> tuple[bool, List[str]]:
        """
        Run all validations

        Args:
            message: Generated message
            customer: Customer data (for personalization check)

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Run standard checks
        checks = [
            cls.validate_tone,
            cls.validate_length,
            cls.validate_structure
        ]

        for check in checks:
            is_valid, reason = check(message)
            if not is_valid:
                errors.append(reason)

        # Run personalization check if customer provided
        if customer:
            is_valid, reason = cls.validate_personalization(message, customer)
            if not is_valid:
                errors.append(reason)

        return (len(errors) == 0, errors)
