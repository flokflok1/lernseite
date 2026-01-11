"""
IT Environments Domain - Value Objects

Immutable value objects for IT practice environments.

Value Objects:
- SandboxLanguage: Supported programming languages
- SandboxStatus: Execution status
- NetworkTopology: Network configuration
- TerminalSession: Terminal session state
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime, timedelta


class SandboxLanguageEnum(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    GO = "go"
    CPP = "cpp"
    CSHARP = "csharp"


class SandboxStatusEnum(str, Enum):
    """Sandbox execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class NetworkProtocolEnum(str, Enum):
    """Network protocols"""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"


@dataclass(frozen=True)
class SandboxLanguage:
    """Sandbox Language Value Object"""
    language: SandboxLanguageEnum
    version: str
    max_execution_time: int = 30  # seconds

    @staticmethod
    def python() -> 'SandboxLanguage':
        return SandboxLanguage(language=SandboxLanguageEnum.PYTHON, version="3.12", max_execution_time=30)

    @staticmethod
    def javascript() -> 'SandboxLanguage':
        return SandboxLanguage(language=SandboxLanguageEnum.JAVASCRIPT, version="20", max_execution_time=30)


@dataclass(frozen=True)
class SandboxExecution:
    """Sandbox Execution Result Value Object"""
    status: SandboxStatusEnum
    output: str
    error: Optional[str] = None
    execution_time_ms: int = 0

    def is_successful(self) -> bool:
        return self.status == SandboxStatusEnum.COMPLETED and not self.error


@dataclass(frozen=True)
class NetworkNode:
    """Network Node Value Object"""
    node_id: str
    node_type: str  # router, switch, host
    ip_address: str
    config: Dict

    def __post_init__(self):
        if not self.node_id or not self.ip_address:
            raise ValueError("node_id and ip_address are required")


@dataclass(frozen=True)
class NetworkTopology:
    """Network Topology Value Object"""
    topology_id: str
    nodes: List[NetworkNode]
    max_nodes: int = 20

    def __post_init__(self):
        if len(self.nodes) > self.max_nodes:
            raise ValueError(f"Maximum {self.max_nodes} nodes allowed")

    def node_count(self) -> int:
        return len(self.nodes)


@dataclass(frozen=True)
class TerminalSession:
    """Terminal Session Value Object"""
    session_id: str
    shell: str  # bash, zsh, sh
    max_duration_seconds: int = 1800  # 30 minutes
    started_at: datetime
    expires_at: datetime

    @staticmethod
    def create(session_id: str, shell: str = "bash", max_duration_seconds: int = 1800) -> 'TerminalSession':
        started = datetime.utcnow()
        expires = started + timedelta(seconds=max_duration_seconds)
        return TerminalSession(
            session_id=session_id,
            shell=shell,
            max_duration_seconds=max_duration_seconds,
            started_at=started,
            expires_at=expires
        )

    def is_expired(self, current_time: datetime) -> bool:
        return current_time > self.expires_at

    def remaining_seconds(self, current_time: datetime) -> int:
        if self.is_expired(current_time):
            return 0
        return int((self.expires_at - current_time).total_seconds())
