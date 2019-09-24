from enum import Enum
from dataclasses import dataclass
from datetime import datetime

MessageType = Enum('MessageType', 'INCOMING OUTGOING')

@dataclass
class Message:
    msg_type: MessageType
    destination: str
    sender: str
    text: str
    msg_id: str = None
    timestamp: datetime = datetime.now()