#!/usr/bin/env python3
"""
WebSocket Manager for Real-Time Communication
Supports agent-to-agent messaging, workflow updates, and live notifications
"""
import json
import asyncio
import logging
from typing import Dict, Set, Any, Optional, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket message types."""
    AGENT_MESSAGE = "agent_message"
    WORKFLOW_UPDATE = "workflow_update"
    MEMORY_NOTIFICATION = "memory_notification"
    SKILL_EXECUTION = "skill_execution"
    EMERGENT_BEHAVIOR = "emergent_behavior"
    SYSTEM_ALERT = "system_alert"


class WebSocketManager:
    """
    Manages WebSocket connections and message routing.

    Features:
    - Multi-client connection management
    - Topic-based subscriptions
    - Agent-to-agent messaging
    - Live workflow status updates
    - Broadcast and targeted messaging
    """

    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}

        # Subscriptions: topic -> set of connection IDs
        self.subscriptions: Dict[str, Set[str]] = {}

        # Agent connections: agent_id -> connection_id
        self.agent_connections: Dict[str, str] = {}

        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Accept WebSocket connection and register it.

        Args:
            websocket: FastAPI WebSocket instance
            connection_id: Unique connection identifier
            metadata: Optional metadata (agent_id, user_id, etc.)
        """
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = metadata or {}

        # Register agent connection if agent_id provided
        if metadata and "agent_id" in metadata:
            self.agent_connections[metadata["agent_id"]] = connection_id

        logger.info(f"WebSocket connected: {connection_id} (total: {len(self.active_connections)})")

        # Send connection acknowledgment
        await self.send_personal_message(
            connection_id,
            {
                "type": "connection_ack",
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Connected to Dell-Boca-Boys orchestrator"
            }
        )

    async def disconnect(self, connection_id: str):
        """
        Disconnect and cleanup connection.

        Args:
            connection_id: Connection to disconnect
        """
        # Remove from active connections
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from subscriptions
        for topic in list(self.subscriptions.keys()):
            self.subscriptions[topic].discard(connection_id)
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]

        # Remove agent connection
        metadata = self.connection_metadata.get(connection_id, {})
        if "agent_id" in metadata:
            agent_id = metadata["agent_id"]
            if agent_id in self.agent_connections:
                del self.agent_connections[agent_id]

        # Remove metadata
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]

        logger.info(f"WebSocket disconnected: {connection_id} (remaining: {len(self.active_connections)})")

    async def send_personal_message(self, connection_id: str, message: Dict[str, Any]):
        """
        Send message to specific connection.

        Args:
            connection_id: Target connection
            message: Message data to send
        """
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                await self.disconnect(connection_id)
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                await self.disconnect(connection_id)

    async def send_agent_message(self, target_agent_id: str, message: Dict[str, Any]):
        """
        Send message to specific agent.

        Args:
            target_agent_id: Target agent ID
            message: Message to send
        """
        if target_agent_id in self.agent_connections:
            connection_id = self.agent_connections[target_agent_id]
            await self.send_personal_message(connection_id, {
                "type": MessageType.AGENT_MESSAGE.value,
                "timestamp": datetime.now().isoformat(),
                "data": message
            })
        else:
            logger.warning(f"Agent {target_agent_id} not connected")

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[Set[str]] = None):
        """
        Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
            exclude: Optional set of connection IDs to exclude
        """
        exclude = exclude or set()
        disconnected = []

        for connection_id, websocket in self.active_connections.items():
            if connection_id in exclude:
                continue

            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Cleanup disconnected clients
        for connection_id in disconnected:
            await self.disconnect(connection_id)

    async def subscribe(self, connection_id: str, topic: str):
        """
        Subscribe connection to topic.

        Args:
            connection_id: Connection to subscribe
            topic: Topic name
        """
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()

        self.subscriptions[topic].add(connection_id)
        logger.debug(f"Connection {connection_id} subscribed to '{topic}'")

        await self.send_personal_message(connection_id, {
            "type": "subscription_ack",
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        })

    async def unsubscribe(self, connection_id: str, topic: str):
        """Unsubscribe connection from topic."""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(connection_id)
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]

        logger.debug(f"Connection {connection_id} unsubscribed from '{topic}'")

    async def publish(self, topic: str, message: Dict[str, Any]):
        """
        Publish message to all subscribers of a topic.

        Args:
            topic: Topic to publish to
            message: Message to publish
        """
        if topic not in self.subscriptions:
            return

        disconnected = []
        subscribers = self.subscriptions[topic].copy()

        for connection_id in subscribers:
            if connection_id not in self.active_connections:
                disconnected.append(connection_id)
                continue

            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json({
                    "type": "topic_message",
                    "topic": topic,
                    "timestamp": datetime.now().isoformat(),
                    "data": message
                })
            except WebSocketDisconnect:
                disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Error publishing to {connection_id}: {e}")
                disconnected.append(connection_id)

        # Cleanup disconnected clients
        for connection_id in disconnected:
            await self.disconnect(connection_id)

    async def notify_workflow_update(self, workflow_id: str, status: str, data: Dict[str, Any]):
        """
        Notify subscribers of workflow status update.

        Args:
            workflow_id: Workflow identifier
            status: Workflow status
            data: Additional workflow data
        """
        topic = f"workflow:{workflow_id}"
        await self.publish(topic, {
            "workflow_id": workflow_id,
            "status": status,
            **data
        })

        # Also broadcast to general workflow topic
        await self.publish("workflows", {
            "workflow_id": workflow_id,
            "status": status,
            **data
        })

    async def notify_emergent_behavior(self, behavior_data: Dict[str, Any]):
        """Notify subscribers of emergent behavior detection."""
        await self.publish("emergent_behaviors", behavior_data)

    async def notify_memory_update(self, memory_type: str, agent_id: Optional[str], data: Dict[str, Any]):
        """Notify subscribers of memory system updates."""
        topic = f"memory:{memory_type}"
        if agent_id:
            topic = f"{topic}:{agent_id}"

        await self.publish(topic, data)

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics."""
        return {
            "active_connections": len(self.active_connections),
            "active_agents": len(self.agent_connections),
            "active_topics": len(self.subscriptions),
            "topics": {
                topic: len(subscribers)
                for topic, subscribers in self.subscriptions.items()
            }
        }


# Global WebSocket manager instance
ws_manager = WebSocketManager()
