"""
💀 PERSONALISATION N-ORGAN 💀

Main orchestrator for hyper-personalized customer re-engagement.

Architecture:
- N8N sends customer + menu data via HTTP POST
- Python processes with AI recommendations + message generation
- Returns formatted WhatsApp messages back to N8N
- N8N handles WhatsApp delivery via Ultramsg
"""

import time
import json
import csv
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

# Support both local and installed imports
try:
    from monarchs.systems.norgan_base import NOrganBase, StageResult
except ImportError:
    from norgan_base import NOrganBase, StageResult

# Support both direct and module imports
try:
    from .schemas import (
        PersonalisationRequest,
        PersonalisationResponse,
        PersonalisedMessage,
        ErrorResponse,
        CustomerInput
    )
    from .ai_engine import AIRecommendationEngine
    from .message_generator import MessageGenerator, MessageValidator
except ImportError:
    from schemas import (
        PersonalisationRequest,
        PersonalisationResponse,
        PersonalisedMessage,
        ErrorResponse,
        CustomerInput
    )
    from ai_engine import AIRecommendationEngine
    from message_generator import MessageGenerator, MessageValidator


class PersonalisationNOrgan(NOrganBase):
    """
    💀 PERSONALISATION N-ORGAN 💀

    Hybrid N8N + Python organ for customer re-engagement.

    Processing Pipeline:
    1. Receive customer + menu data from N8N
    2. Generate AI recommendations (DeepSeek)
    3. Generate personalized messages (friendly tone)
    4. Validate message quality
    5. Return formatted messages to N8N

    Golden Rule: Stateless. Zero memory. No hard-coded config.
    """

    def __init__(
        self,
        runs_dir: str = "./runs",
        deepseek_api_key: str = None
    ):
        """
        Initialize PersonalisationNOrgan

        Args:
            runs_dir: Directory for run artifacts
            deepseek_api_key: DeepSeek API key (reads from env if not provided)
        """
        super().__init__(runs_dir)

        # Initialize AI engine
        self.ai_engine = AIRecommendationEngine(api_key=deepseek_api_key)

        # Initialize message generator (client_name will be set per request)
        self.message_generator = None

        # Message validator
        self.validator = MessageValidator()

    async def process(
        self,
        request: PersonalisationRequest
    ) -> PersonalisationResponse:
        """
        Main processing pipeline

        Args:
            request: Validated request from N8N

        Returns:
            PersonalisationResponse with generated messages
        """
        start_time = time.time()

        print(f"\n💀 PERSONALISATION N-ORGAN PROCESSING 💀")
        print(f"   Customers: {len(request.customers)}")
        print(f"   Menu Items: {len(request.menu_items)}")
        print(f"   Client: {request.client_name}\n")

        # Initialize message generator with client name
        self.message_generator = MessageGenerator(client_name=request.client_name)

        # Track results
        generated_messages = []
        errors = []

        try:
            # STAGE 1: AI Recommendations
            print("   🧠 Stage 1: Generating AI recommendations...")
            stage_start = time.time()

            recommendations = await self.ai_engine.batch_recommend(
                customers=request.customers,
                menu=request.menu_items,
                client_name=request.client_name
            )

            stage_duration = time.time() - stage_start
            self._record_stage(StageResult(
                stage_name="ai_recommendations",
                success=True,
                input_count=len(request.customers),
                output_count=len(recommendations),
                duration=stage_duration
            ))
            print(f"   ✅ Generated {len(recommendations)} recommendations ({stage_duration:.2f}s)\n")

            # STAGE 2: Message Generation
            print("   📝 Stage 2: Generating personalized messages...")
            stage_start = time.time()

            messages_dict = self.message_generator.generate_batch_messages(
                customers=request.customers,
                recommendations=recommendations
            )

            stage_duration = time.time() - stage_start
            self._record_stage(StageResult(
                stage_name="message_generation",
                success=True,
                input_count=len(request.customers),
                output_count=len(messages_dict),
                duration=stage_duration
            ))
            print(f"   ✅ Generated {len(messages_dict)} messages ({stage_duration:.2f}s)\n")

            # STAGE 3: Message Validation & Formatting
            print("   🔍 Stage 3: Validating message quality...")
            stage_start = time.time()

            for customer in request.customers:
                try:
                    # Get generated message
                    message_text = messages_dict.get(customer.customer_id)
                    if not message_text:
                        errors.append(f"No message generated for {customer.customer_id}")
                        continue

                    # Validate message quality (with customer data for personalization check)
                    is_valid, validation_errors = self.validator.validate_message(message_text, customer)

                    if not is_valid:
                        error_msg = f"Invalid message for {customer.customer_id}: {', '.join(validation_errors)}"
                        errors.append(error_msg)
                        print(f"   ⚠️  {error_msg}")
                        continue

                    # Get recommendation for this customer
                    rec = recommendations.get(customer.customer_id)
                    recommended_items = rec.recommended_items if rec else []

                    # Create formatted message
                    generated_messages.append(
                        PersonalisedMessage(
                            customer_id=customer.customer_id,
                            to=customer.phone,
                            body=message_text,
                            platform="whatsapp",
                            recommended_items=recommended_items,
                            confidence=rec.confidence if rec else "low"
                        )
                    )

                except Exception as e:
                    error_msg = f"Error processing {customer.customer_id}: {str(e)}"
                    errors.append(error_msg)
                    print(f"   ❌ {error_msg}")

            stage_duration = time.time() - stage_start
            self._record_stage(StageResult(
                stage_name="validation_formatting",
                success=True,
                input_count=len(messages_dict),
                output_count=len(generated_messages),
                duration=stage_duration,
                error="; ".join(errors) if errors else None
            ))
            print(f"   ✅ Validated {len(generated_messages)} messages ({stage_duration:.2f}s)\n")

            # Calculate totals
            total_duration = time.time() - start_time
            total_processed = len(request.customers)
            total_succeeded = len(generated_messages)
            total_failed = total_processed - total_succeeded

            # Build response
            response = PersonalisationResponse(
                success=True,
                messages=generated_messages,
                total_processed=total_processed,
                total_succeeded=total_succeeded,
                total_failed=total_failed,
                errors=errors,
                processing_time_seconds=total_duration,
                metadata={
                    "client_name": request.client_name,
                    "campaign_type": request.campaign_type,
                    "menu_items_count": len(request.menu_items),
                    "stages": [
                        {
                            "name": stage.stage_name,
                            "duration": stage.duration,
                            "success": stage.success
                        }
                        for stage in self.stages
                    ]
                }
            )

            # SAVE MESSAGES TO FILES (Safety net backup)
            print("   💾 Saving messages to files...")
            self._save_messages_to_files(
                generated_messages=generated_messages,
                recommendations=recommendations,
                request=request,
                errors=errors
            )

            print(f"💀 PROCESSING COMPLETE 💀")
            print(f"   ✅ Success: {total_succeeded}/{total_processed}")
            print(f"   ⏱️  Total Time: {total_duration:.2f}s")
            if errors:
                print(f"   ⚠️  Errors: {len(errors)}")

            return response

        except Exception as e:
            # Critical error - return error response
            error_msg = f"Critical error in processing pipeline: {str(e)}"
            print(f"\n   ❌ {error_msg}")

            self._record_stage(StageResult(
                stage_name="processing_pipeline",
                success=False,
                input_count=len(request.customers),
                output_count=0,
                duration=time.time() - start_time,
                error=error_msg
            ))

            raise

    def _save_messages_to_files(
        self,
        generated_messages: List[PersonalisedMessage],
        recommendations: dict,
        request: PersonalisationRequest,
        errors: List[str]
    ):
        """
        Save generated messages to CSV and JSON files (Safety net backup)

        Args:
            generated_messages: Successfully generated messages
            recommendations: AI recommendations dict
            request: Original request
            errors: List of errors
        """
        if not self.run_folder:
            # Create run folder if not exists
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.run_id = f"run-{timestamp}"
            self.run_folder = self.runs_dir / self.run_id
            self.run_folder.mkdir(parents=True, exist_ok=True)

        # Save CSV (Easy to view in Excel/Sheets)
        csv_path = self.run_folder / "messages.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Header
            writer.writerow([
                "Timestamp",
                "Customer ID",
                "Customer Name",
                "Phone",
                "Last Order Items",
                "AI Recommendations",
                "Message Preview (First 100 chars)",
                "Full Message",
                "Status"
            ])

            # Data rows
            for msg in generated_messages:
                # Find customer data
                customer = next((c for c in request.customers if c.customer_id == msg.customer_id), None)

                writer.writerow([
                    datetime.now().isoformat(),
                    msg.customer_id,
                    customer.name if customer else "Unknown",
                    msg.to,
                    ", ".join(customer.last_order_items) if customer and customer.last_order_items else "",
                    ", ".join(msg.recommended_items),
                    msg.body[:100] + "..." if len(msg.body) > 100 else msg.body,
                    msg.body,
                    "Success"
                ])

        print(f"   ✅ Saved CSV: {csv_path}")

        # Save JSON (Full detailed data)
        json_data = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "client_name": request.client_name,
            "campaign_type": request.campaign_type,
            "total_customers": len(request.customers),
            "total_succeeded": len(generated_messages),
            "total_failed": len(request.customers) - len(generated_messages),
            "messages": [
                {
                    "customer_id": msg.customer_id,
                    "customer_name": next((c.name for c in request.customers if c.customer_id == msg.customer_id), "Unknown"),
                    "phone": msg.to,
                    "last_order_items": next((c.last_order_items for c in request.customers if c.customer_id == msg.customer_id), []),
                    "days_inactive": next((c.days_inactive for c in request.customers if c.customer_id == msg.customer_id), 0),
                    "preference": next((c.preference for c in request.customers if c.customer_id == msg.customer_id), "Unknown"),
                    "ai_recommendations": msg.recommended_items,
                    "recommendation_confidence": msg.confidence,
                    "message": msg.body,
                    "platform": msg.platform,
                    "status": "success"
                }
                for msg in generated_messages
            ],
            "errors": errors,
            "metadata": {
                "menu_items_count": len(request.menu_items),
                "processing_stages": [
                    {
                        "stage": stage.stage_name,
                        "duration": stage.duration,
                        "success": stage.success
                    }
                    for stage in self.stages
                ]
            }
        }

        json_path = self.run_folder / "messages.json"
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)

        print(f"   ✅ Saved JSON: {json_path}")
        print(f"   📁 Run folder: {self.run_folder}")

    async def run(self, data: Dict[str, Any]) -> PersonalisationResponse:
        """
        Run the personalisation pipeline (SystemBase interface)

        Args:
            data: Raw dict data from N8N

        Returns:
            PersonalisationResponse
        """
        # Validate and parse request
        try:
            request = PersonalisationRequest(**data)
        except Exception as e:
            raise ValueError(f"Invalid request schema: {str(e)}")

        # Process
        return await self.process(request)

    def __call__(self, data: Dict[str, Any]) -> PersonalisationResponse:
        """
        Synchronous callable interface (SystemBase)

        Args:
            data: Raw dict data from N8N

        Returns:
            PersonalisationResponse
        """
        import asyncio
        return asyncio.run(self.run(data))


# ============================================================================
# GUARDIAN ERROR HANDLING
# ============================================================================

class PersonalisationGuardian:
    """
    💀 4-LAYER GUARDIAN SYSTEM 💀

    Error handling for PersonalisationNOrgan.

    Layers:
    1. Per-customer: Individual failures don't break batch
    2. Retry: Exponential backoff for transient errors
    3. Fallback: Generic messages when AI fails
    4. Emergency: Always return something to N8N
    """

    @staticmethod
    async def safe_process(
        organ: PersonalisationNOrgan,
        request: PersonalisationRequest
    ) -> PersonalisationResponse:
        """
        Wrap processing with guardian protection

        Args:
            organ: PersonalisationNOrgan instance
            request: Validated request

        Returns:
            PersonalisationResponse (always succeeds, may have errors)
        """
        try:
            # Layer 1: Normal processing (per-customer failures handled internally)
            return await organ.process(request)

        except Exception as e:
            # Layer 4: Emergency fallback - return error response
            print(f"\n   🚨 GUARDIAN EMERGENCY FALLBACK 🚨")
            print(f"   Error: {str(e)}")

            return PersonalisationResponse(
                success=False,
                messages=[],
                total_processed=len(request.customers),
                total_succeeded=0,
                total_failed=len(request.customers),
                errors=[f"Critical failure: {str(e)}"],
                processing_time_seconds=0.0,
                metadata={
                    "emergency_fallback": True,
                    "error": str(e)
                }
            )
