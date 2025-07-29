"""
连接管理器 - 处理持久化连接、心跳机制和会话管理
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """连接状态枚举"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class ConnectionInfo:
    """连接信息"""
    id: str
    state: ConnectionState
    created_at: float
    last_heartbeat: float
    protocol_version: str
    client_info: Dict
    error_count: int = 0


class ConnectionManager:
    """连接管理器"""
    
    def __init__(self, heartbeat_interval: int = 30, max_error_count: int = 3):
        """
        初始化连接管理器
        
        Args:
            heartbeat_interval: 心跳间隔（秒）
            max_error_count: 最大错误次数
        """
        self.connections: Dict[str, ConnectionInfo] = {}
        self.heartbeat_interval = heartbeat_interval
        self.max_error_count = max_error_count
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def start(self):
        """启动连接管理器"""
        if self._running:
            return
            
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("连接管理器已启动")
        
    async def stop(self):
        """停止连接管理器"""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
                
        # 清理所有连接
        for conn_id in list(self.connections.keys()):
            await self.disconnect(conn_id)
            
        logger.info("连接管理器已停止")
        
    async def connect(self, connection_id: str, protocol_version: str = "2.1", 
                     client_info: Optional[Dict] = None) -> bool:
        """
        建立新连接
        
        Args:
            connection_id: 连接ID
            protocol_version: 协议版本
            client_info: 客户端信息
            
        Returns:
            是否连接成功
        """
        if not self._is_supported_protocol(protocol_version):
            logger.error(f"不支持的协议版本: {protocol_version}")
            return False
            
        current_time = time.time()
        
        connection = ConnectionInfo(
            id=connection_id,
            state=ConnectionState.CONNECTED,
            created_at=current_time,
            last_heartbeat=current_time,
            protocol_version=protocol_version,
            client_info=client_info or {}
        )
        
        self.connections[connection_id] = connection
        logger.info(f"新连接已建立: {connection_id} (协议版本: {protocol_version})")
        
        return True
        
    async def disconnect(self, connection_id: str):
        """断开连接"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.state = ConnectionState.DISCONNECTED
            del self.connections[connection_id]
            logger.info(f"连接已断开: {connection_id}")
            
    async def heartbeat(self, connection_id: str) -> bool:
        """
        处理心跳
        
        Args:
            connection_id: 连接ID
            
        Returns:
            心跳是否成功
        """
        if connection_id not in self.connections:
            logger.warning(f"未找到连接: {connection_id}")
            return False
            
        connection = self.connections[connection_id]
        connection.last_heartbeat = time.time()
        connection.error_count = 0  # 重置错误计数
        
        logger.debug(f"心跳更新: {connection_id}")
        return True
        
    def get_connection(self, connection_id: str) -> Optional[ConnectionInfo]:
        """获取连接信息"""
        return self.connections.get(connection_id)
        
    def get_active_connections(self) -> Dict[str, ConnectionInfo]:
        """获取所有活跃连接"""
        return {
            conn_id: conn for conn_id, conn in self.connections.items()
            if conn.state == ConnectionState.CONNECTED
        }
        
    def get_connection_stats(self) -> Dict:
        """获取连接统计信息"""
        active_count = len([
            conn for conn in self.connections.values()
            if conn.state == ConnectionState.CONNECTED
        ])
        
        return {
            "total_connections": len(self.connections),
            "active_connections": active_count,
            "protocol_versions": list(set(
                conn.protocol_version for conn in self.connections.values()
            ))
        }
        
    async def _heartbeat_loop(self):
        """心跳检查循环"""
        while self._running:
            try:
                await self._check_connections()
                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳检查出错: {e}")
                await asyncio.sleep(5)  # 出错时短暂等待
                
    async def _check_connections(self):
        """检查连接状态"""
        current_time = time.time()
        timeout_threshold = self.heartbeat_interval * 2  # 超时阈值
        
        expired_connections = []
        
        for conn_id, connection in self.connections.items():
            if connection.state != ConnectionState.CONNECTED:
                continue
                
            # 检查是否超时
            if current_time - connection.last_heartbeat > timeout_threshold:
                connection.error_count += 1
                logger.warning(f"连接心跳超时: {conn_id} (错误次数: {connection.error_count})")
                
                # 超过最大错误次数，标记为断开
                if connection.error_count >= self.max_error_count:
                    connection.state = ConnectionState.ERROR
                    expired_connections.append(conn_id)
                    
        # 清理过期连接
        for conn_id in expired_connections:
            await self.disconnect(conn_id)
            
    def _is_supported_protocol(self, version: str) -> bool:
        """检查是否支持指定的协议版本"""
        supported_versions = ["2.0", "2.1", "2.2"]
        return version in supported_versions


# 全局连接管理器实例
connection_manager = ConnectionManager()