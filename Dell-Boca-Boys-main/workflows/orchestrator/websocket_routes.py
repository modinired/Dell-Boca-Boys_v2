#!/usr/bin/env python3
"""
WebSocket routes for Dell-Boca-Boys orchestrator
Real-time agent communication and workflow updates
"""
from fastapi import WebSocket, WebSocketDisconnect, Query
from core.websocket import ws_manager
import json
import logging
from typing import Optional
import uuid

logger = logging.getLogger(__name__)


async def websocket_endpoint(
    websocket: WebSocket,
    agent_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time communication.

    **Query Parameters:**
    - `agent_id`: Optional agent identifier for agent-to-agent messaging
    - `user_id`: Optional user identifier for user-specific updates

    **Connection:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws?agent_id=agent_001&user_id=user_123');
    ```

    **Message Format:**
    ```json
    {
      "action": "subscribe|unsubscribe|message",
      "topic": "workflows|memory:episodic|agent:agent_001",
      "data": {...}
    }
    ```

    **Supported Topics:**
    - `workflows` - All workflow updates
    - `workflow:<workflow_id>` - Specific workflow updates
    - `memory:<memory_type>` - Memory system updates
    - `agent:<agent_id>` - Agent-specific messages
    - `emergent_behaviors` - Emergent behavior notifications
    - `system_alerts` - System-wide alerts

    **Example Messages:**

    Subscribe to workflows:
    ```json
    {"action": "subscribe", "topic": "workflows"}
    ```

    Send agent message:
    ```json
    {
      "action": "message",
      "target_agent": "agent_002",
      "data": {"type": "collaboration_request", "task_id": "task_123"}
    }
    ```
    """
    connection_id = str(uuid.uuid4())
    metadata = {}

    if agent_id:
        metadata["agent_id"] = agent_id
    if user_id:
        metadata["user_id"] = user_id

    await ws_manager.connect(websocket, connection_id, metadata)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                action = message.get("action")

                if action == "subscribe":
                    topic = message.get("topic")
                    if topic:
                        await ws_manager.subscribe(connection_id, topic)

                elif action == "unsubscribe":
                    topic = message.get("topic")
                    if topic:
                        await ws_manager.unsubscribe(connection_id, topic)

                elif action == "message":
                    # Agent-to-agent messaging
                    target_agent = message.get("target_agent")
                    if target_agent:
                        await ws_manager.send_agent_message(
                            target_agent,
                            {
                                "from_agent": agent_id,
                                "data": message.get("data", {})
                            }
                        )

                elif action == "publish":
                    # Publish to topic (requires authorization in production)
                    topic = message.get("topic")
                    data = message.get("data", {})
                    if topic:
                        await ws_manager.publish(topic, data)

                elif action == "ping":
                    # Heartbeat
                    await ws_manager.send_personal_message(
                        connection_id,
                        {"type": "pong", "timestamp": message.get("timestamp")}
                    )

                else:
                    await ws_manager.send_personal_message(
                        connection_id,
                        {
                            "type": "error",
                            "message": f"Unknown action: {action}"
                        }
                    )

            except json.JSONDecodeError:
                await ws_manager.send_personal_message(
                    connection_id,
                    {"type": "error", "message": "Invalid JSON"}
                )

            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await ws_manager.send_personal_message(
                    connection_id,
                    {"type": "error", "message": str(e)}
                )

    except WebSocketDisconnect:
        await ws_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws_manager.disconnect(connection_id)
