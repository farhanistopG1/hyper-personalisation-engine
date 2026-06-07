"""
💀 HYPER PERSONALISATION SCHEMAS 💀

Pydantic models for N8N ↔ Python communication.

Request: N8N sends customer + menu data
Response: Python returns personalized messages
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime


# ============================================================================
# REQUEST MODELS (N8N → Python)
# ============================================================================

class CustomerInput(BaseModel):
    """Single customer data from N8N"""
    customer_id: str = Field(..., description="Unique customer identifier")
    name: str = Field(..., description="Customer name")
    phone: str = Field(..., description="WhatsApp phone number (with country code)")
    last_order_date: str = Field(..., description="Date of last order (YYYY-MM-DD)")
    days_inactive: int = Field(..., description="Days since last order")
    preference: Literal["VEG", "NON-VEG"] = Field(..., description="Food preference")
    last_order_items: List[str] = Field(..., description="List of previously ordered items")
    total_orders: Optional[int] = Field(default=1, description="Total number of orders")

    @validator('phone')
    def validate_phone(cls, v):
        """Ensure phone number is valid"""
        if not v.strip():
            raise ValueError("Phone number cannot be empty")
        # Remove any spaces/dashes
        clean = v.replace(" ", "").replace("-", "")
        if not clean.isdigit():
            raise ValueError("Phone number must contain only digits")
        return clean

    @validator('days_inactive')
    def validate_inactive_days(cls, v):
        """Ensure days inactive is positive"""
        if v < 0:
            raise ValueError("Days inactive cannot be negative")
        return v


class MenuItem(BaseModel):
    """Single menu item from N8N"""
    item_id: str = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Dish name")
    category: Literal["VEG", "NON-VEG"] = Field(..., description="Food category")
    description: Optional[str] = Field(default="", description="Item description")
    price: Optional[float] = Field(default=None, description="Item price")
    is_available: bool = Field(default=True, description="Currently available")


class PersonalisationRequest(BaseModel):
    """Full request payload from N8N"""
    customers: List[CustomerInput] = Field(..., description="List of customers to personalize")
    menu_items: List[MenuItem] = Field(..., description="Available menu items")
    client_name: str = Field(default="Pizza Express", description="Client business name")
    campaign_type: str = Field(default="re-engagement", description="Campaign type")

    @validator('customers')
    def validate_customers_not_empty(cls, v):
        """Ensure at least one customer"""
        if not v:
            raise ValueError("Must provide at least one customer")
        return v

    @validator('menu_items')
    def validate_menu_not_empty(cls, v):
        """Ensure menu is not empty"""
        if not v:
            raise ValueError("Menu cannot be empty")
        return v


# ============================================================================
# RESPONSE MODELS (Python → N8N)
# ============================================================================

class PersonalisedMessage(BaseModel):
    """Single personalized message result"""
    customer_id: str = Field(..., description="Customer ID")
    to: str = Field(..., description="WhatsApp phone number")
    body: str = Field(..., description="Full WhatsApp message text")
    platform: Literal["whatsapp"] = Field(default="whatsapp", description="Messaging platform")
    recommended_items: List[str] = Field(..., description="AI-recommended dish names")
    confidence: Optional[str] = Field(default="medium", description="Recommendation confidence")

    @validator('body')
    def validate_message_not_empty(cls, v):
        """Ensure message is not empty"""
        if not v.strip():
            raise ValueError("Message body cannot be empty")
        return v


class PersonalisationResponse(BaseModel):
    """Full response payload to N8N"""
    success: bool = Field(..., description="Overall success status")
    messages: List[PersonalisedMessage] = Field(..., description="Generated messages")
    total_processed: int = Field(..., description="Total customers processed")
    total_succeeded: int = Field(..., description="Successfully generated messages")
    total_failed: int = Field(default=0, description="Failed generations")
    errors: List[str] = Field(default_factory=list, description="Error messages if any")
    processing_time_seconds: float = Field(..., description="Total processing time")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    @validator('total_succeeded')
    def validate_success_count(cls, v, values):
        """Ensure success count matches messages"""
        if 'messages' in values and v != len(values['messages']):
            raise ValueError("Success count must match number of messages")
        return v


class ErrorResponse(BaseModel):
    """Standardized error response"""
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error category")
    details: Optional[dict] = Field(default=None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# INTERNAL MODELS (Python-only, not sent to N8N)
# ============================================================================

class AIRecommendation(BaseModel):
    """AI-generated recommendation (internal)"""
    customer_id: str
    recommended_items: List[str]
    reasoning: str
    confidence: str = "medium"  # low, medium, high


class MessageTemplate(BaseModel):
    """Message template structure (internal)"""
    intro: str
    recommendation: str
    outro: str
    full_message: str
