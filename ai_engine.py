"""
💀 AI RECOMMENDATION ENGINE 💀

DeepSeek-powered dish recommendations for customer re-engagement.

Responsibilities:
- Analyze customer order history
- Match preferences with available menu
- Generate personalized dish recommendations
- Provide reasoning for recommendations
"""

import os
import httpx
from typing import List, Dict, Any

# Support both direct and module imports
try:
    from .schemas import CustomerInput, MenuItem, AIRecommendation
except ImportError:
    from schemas import CustomerInput, MenuItem, AIRecommendation


class AIRecommendationEngine:
    """
    💀 AI RECOMMENDATION ENGINE 💀

    Uses DeepSeek to generate personalized dish recommendations.

    Features:
    - Customer history analysis
    - Preference-based matching (VEG/NON-VEG)
    - Context-aware recommendations
    - Reasoning and confidence scoring
    """

    def __init__(self, api_key: str = None):
        """
        Initialize AI engine

        Args:
            api_key: DeepSeek API key (reads from env if not provided)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY must be set in environment or passed to constructor")

        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"

    async def recommend_dishes(
        self,
        customer: CustomerInput,
        menu: List[MenuItem],
        client_name: str = "Pizza Express"
    ) -> AIRecommendation:
        """
        Generate AI-powered dish recommendations

        Args:
            customer: Customer data with history
            menu: Available menu items
            client_name: Restaurant name

        Returns:
            AIRecommendation with items + reasoning
        """
        # Filter menu by customer preference
        filtered_menu = [
            item for item in menu
            if item.category == customer.preference and item.is_available
        ]

        if not filtered_menu:
            # Fallback: use all available items
            filtered_menu = [item for item in menu if item.is_available]

        # Build AI prompt
        prompt = self._build_recommendation_prompt(customer, filtered_menu, client_name)

        # Call DeepSeek API
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a friendly food recommendation expert. Analyze customer history and suggest dishes they'll love."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                response.raise_for_status()
                result = response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"DeepSeek API error: {e}")

        # Parse AI response
        ai_text = result["choices"][0]["message"]["content"].strip()
        recommendation = self._parse_ai_response(ai_text, filtered_menu, customer.customer_id)

        return recommendation

    def _build_recommendation_prompt(
        self,
        customer: CustomerInput,
        menu: List[MenuItem],
        client_name: str
    ) -> str:
        """Build the AI prompt for recommendations"""

        # Format menu items
        menu_text = "\n".join([
            f"- {item.name}" + (f" ({item.description})" if item.description else "")
            for item in menu
        ])

        # Format previous orders
        previous_orders = ", ".join(customer.last_order_items) if customer.last_order_items else "Unknown"

        prompt = f"""You are recommending dishes for {client_name}.

CUSTOMER PROFILE:
- Name: {customer.name}
- Preference: {customer.preference}
- Last Order: {customer.last_order_date} ({customer.days_inactive} days ago)
- Previously Ordered: {previous_orders}
- Total Orders: {customer.total_orders}

AVAILABLE MENU ({customer.preference} items):
{menu_text}

TASK:
Based on their previous order and preferences, recommend 2-3 dishes they would love to try.

RULES:
1. Only recommend items from the menu above
2. Consider what they ordered before
3. Suggest variety (don't repeat exact same items)
4. Match their {customer.preference} preference
5. Keep it exciting and appetizing

REQUIRED FORMAT:
RECOMMENDATIONS: [Dish 1], [Dish 2], [Dish 3]
REASONING: [Brief explanation why these dishes suit this customer]
CONFIDENCE: [low/medium/high]

Example:
RECOMMENDATIONS: Margherita Pizza, Pesto Pasta, Tiramisu
REASONING: Customer loves classic Italian flavors. Margherita is similar to their favorite Pepperoni but vegetarian. Pesto Pasta offers a fresh alternative. Tiramisu is a perfect sweet ending.
CONFIDENCE: high

Now recommend for this customer:"""

        return prompt

    def _parse_ai_response(
        self,
        ai_text: str,
        menu: List[MenuItem],
        customer_id: str
    ) -> AIRecommendation:
        """
        Parse AI response into structured recommendation

        Args:
            ai_text: Raw AI response
            menu: Menu items to validate against
            customer_id: Customer ID

        Returns:
            Structured AIRecommendation
        """
        # Extract sections
        recommendations_text = ""
        reasoning_text = ""
        confidence_text = "medium"

        for line in ai_text.split("\n"):
            line = line.strip()
            if line.startswith("RECOMMENDATIONS:"):
                recommendations_text = line.replace("RECOMMENDATIONS:", "").strip()
            elif line.startswith("REASONING:"):
                reasoning_text = line.replace("REASONING:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                confidence_text = line.replace("CONFIDENCE:", "").strip().lower()

        # Parse recommended items
        recommended_items = []
        if recommendations_text:
            # Split by comma and clean
            items = [item.strip() for item in recommendations_text.split(",")]

            # Validate against menu
            menu_names = {item.name.lower(): item.name for item in menu}

            for item in items:
                # Try exact match first
                if item in [m.name for m in menu]:
                    recommended_items.append(item)
                # Try case-insensitive match
                elif item.lower() in menu_names:
                    recommended_items.append(menu_names[item.lower()])

        # Fallback: if parsing failed, pick top 2 from menu
        if not recommended_items:
            recommended_items = [item.name for item in menu[:2]]
            reasoning_text = "Selected popular items from menu"
            confidence_text = "low"

        # Ensure confidence is valid
        if confidence_text not in ["low", "medium", "high"]:
            confidence_text = "medium"

        return AIRecommendation(
            customer_id=customer_id,
            recommended_items=recommended_items[:3],  # Max 3 items
            reasoning=reasoning_text or "AI-powered recommendation based on customer history",
            confidence=confidence_text
        )

    async def batch_recommend(
        self,
        customers: List[CustomerInput],
        menu: List[MenuItem],
        client_name: str = "Pizza Express",
        max_concurrent: int = 10
    ) -> Dict[str, AIRecommendation]:
        """
        Generate recommendations for multiple customers (CONCURRENT with rate limiting)

        Args:
            customers: List of customers
            menu: Available menu
            client_name: Restaurant name
            max_concurrent: Max concurrent API calls (default 10 to avoid overwhelming DeepSeek)

        Returns:
            Dict mapping customer_id to AIRecommendation

        Processing Strategy:
            - Processes customers in PARALLEL (not one-at-a-time)
            - Uses semaphore to limit concurrent DeepSeek API calls
            - Default limit: 10 concurrent calls (safe for DeepSeek API)
            - Higher = faster but risks rate limits
            - Lower = slower but safer
        """
        import asyncio

        # Semaphore to control concurrent API calls (prevents overwhelming DeepSeek)
        semaphore = asyncio.Semaphore(max_concurrent)

        async def recommend_with_limit(customer: CustomerInput) -> tuple:
            """
            Recommend for one customer with concurrency limiting

            Returns:
                (customer_id, AIRecommendation or Exception)
            """
            async with semaphore:  # Wait if max concurrent calls reached
                try:
                    rec = await self.recommend_dishes(customer, menu, client_name)
                    return (customer.customer_id, rec)
                except Exception as e:
                    return (customer.customer_id, e)

        # Create all tasks at once (parallel processing)
        print(f"   🚀 Processing {len(customers)} customers with max {max_concurrent} concurrent API calls...")
        tasks = [recommend_with_limit(customer) for customer in customers]

        # Execute all tasks concurrently (asyncio.gather runs them in parallel)
        results = await asyncio.gather(*tasks)

        # Process results
        recommendations = {}
        for customer_id, result in results:
            if isinstance(result, Exception):
                # API call failed - create fallback
                print(f"   ⚠️  Failed to recommend for {customer_id}: {result}")

                # Find customer object for fallback
                customer = next((c for c in customers if c.customer_id == customer_id), None)

                if customer:
                    fallback_items = [
                        item.name for item in menu
                        if item.category == customer.preference and item.is_available
                    ][:2]

                    if not fallback_items:
                        fallback_items = [item.name for item in menu if item.is_available][:2]

                    recommendations[customer_id] = AIRecommendation(
                        customer_id=customer_id,
                        recommended_items=fallback_items,
                        reasoning="Fallback recommendation due to AI error",
                        confidence="low"
                    )
            else:
                # Success - use AI recommendation
                recommendations[customer_id] = result

        return recommendations
