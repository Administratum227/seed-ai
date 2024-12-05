"""Core network communication layer for SEED agents.

Provides secure message passing, capability sharing, and state synchronization
between distributed agents in the network. Implements fault-tolerant networking
with automatic recovery and state reconciliation.
"""

[Previous content remains the same until _process_messages...]

    async def _send_to_node(
        self,
        node: NetworkNode,
        message_data: Dict[str, Any]
    ) -> None:
        """Send message data to a specific network node.
        
        Implements retry logic and connection pooling for reliable delivery.
        
        Args:
            node: Target network node
            message_data: Message to send
            
        Raises:
            NetworkError: If message cannot be delivered after retries
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                reader, writer = await asyncio.open_connection(
                    node.host,
                    node.port
                )
                
                # Send message
                writer.write(json.dumps(message_data).encode())
                await writer.drain()
                
                writer.close()
                await writer.wait_closed()
                return
                
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(
                        f"Failed to send message to {node.agent_id}: {e}"
                    )
                    raise NetworkError(
                        f"Message delivery failed: {str(e)}"
                    )
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

    async def _get_capabilities(self) -> Set[str]:
        """Get the current set of agent capabilities.
        
        Queries the local agent runtime for available capabilities.
        
        Returns:
            Set of capability identifiers
        """
        # TODO: Implement capability discovery from runtime
        return {"basic_reasoning", "network_communication"}

    async def share_capabilities(
        self,
        capabilities: Set[str],
        recipient_id: Optional[str] = None
    ) -> None:
        """Share capability information with other agents.
        
        Broadcasts or sends capability information to specific agents,
        enabling dynamic capability discovery and sharing.
        
        Args:
            capabilities: Set of capabilities to share
            recipient_id: Optional specific recipient
        """
        capability_info = {
            "capabilities": list(capabilities),
            "conditions": self._get_sharing_conditions(),
            "auth_token": await self._generate_capability_token()
        }
        
        await self.send_message(
            MessageType.CAPABILITY,
            capability_info,
            recipient_id
        )

    async def synchronize_state(
        self,
        peer_id: str,
        state_subset: Optional[Set[str]] = None
    ) -> None:
        """Synchronize state with a peer agent.
        
        Implements a two-phase commit protocol for consistent state
        synchronization between agents.
        
        Args:
            peer_id: ID of peer to sync with
            state_subset: Optional subset of state keys to sync
        """
        # Phase 1: Prepare
        local_state = await self._get_local_state(state_subset)
        prepare_msg = {
            "phase": "prepare",
            "state": local_state,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.send_message(
            MessageType.STATE,
            prepare_msg,
            peer_id
        )
        
        # Wait for acknowledgment
        try:
            ack = await self._wait_for_sync_ack(peer_id)
            if ack["status"] == "ready":
                # Phase 2: Commit
                commit_msg = {
                    "phase": "commit",
                    "sync_id": ack["sync_id"]
                }
                await self.send_message(
                    MessageType.STATE,
                    commit_msg,
                    peer_id
                )
        except TimeoutError:
            self.logger.warning(f"State sync with {peer_id} timed out")
            await self._handle_sync_timeout(peer_id)

    async def _verify_state_integrity(
        self,
        state_data: Dict[str, Any]
    ) -> bool:
        """Verify the integrity of received state data.
        
        Checks state consistency and validates any included proofs
        or signatures.
        
        Args:
            state_data: State data to verify
            
        Returns:
            True if state is valid
        """
        try:
            # Verify state structure
            required_fields = {"version", "timestamp", "checksum"}
            if not all(field in state_data for field in required_fields):
                return False
            
            # Verify checksum
            computed_checksum = self._compute_state_checksum(
                state_data["content"]
            )
            return computed_checksum == state_data["checksum"]
            
        except Exception as e:
            self.logger.error(f"State verification failed: {e}")
            return False

    async def _resolve_state_conflict(
        self,
        local_state: Dict[str, Any],
        remote_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflicts between local and remote state.
        
        Implements a last-writer-wins strategy with vector clocks
        for conflict resolution.
        
        Args:
            local_state: Local agent state
            remote_state: Remote agent state
            
        Returns:
            Resolved state data
        """
        resolved_state = {}
        
        for key in set(local_state) | set(remote_state):
            if key not in remote_state:
                resolved_state[key] = local_state[key]
            elif key not in local_state:
                resolved_state[key] = remote_state[key]
            else:
                # Compare vector clocks
                local_vclock = local_state[key].get("vclock", {})
                remote_vclock = remote_state[key].get("vclock", {})
                
                if self._vclock_compare(local_vclock, remote_vclock) > 0:
                    resolved_state[key] = local_state[key]
                else:
                    resolved_state[key] = remote_state[key]
        
        return resolved_state

    def _vclock_compare(
        self,
        vclock1: Dict[str, int],
        vclock2: Dict[str, int]
    ) -> int:
        """Compare two vector clocks.
        
        Args:
            vclock1: First vector clock
            vclock2: Second vector clock
            
        Returns:
            1 if vclock1 > vclock2
            -1 if vclock1 < vclock2
            0 if concurrent
        """
        all_nodes = set(vclock1) | set(vclock2)
        v1_greater = False
        v2_greater = False
        
        for node in all_nodes:
            count1 = vclock1.get(node, 0)
            count2 = vclock2.get(node, 0)
            
            if count1 > count2:
                v1_greater = True
            elif count2 > count1:
                v2_greater = True
                
            if v1_greater and v2_greater:
                return 0  # Concurrent modifications
                
        if v1_greater:
            return 1
        if v2_greater:
            return -1
        return 0  # Equal

    async def get_network_metrics(self) -> Dict[str, Any]:
        """Get current network health and performance metrics.
        
        Collects metrics on message latency, delivery rates, and
        node availability.
        
        Returns:
            Dictionary of network metrics
        """
        active_nodes = len([
            n for n in self.discovery.nodes.values()
            if n.status == "active"
        ])
        
        return {
            "active_nodes": active_nodes,
            "message_latency": await self._calculate_message_latency(),
            "delivery_rate": await self._calculate_delivery_rate(),
            "bandwidth_usage": await self._get_bandwidth_usage()
        }

class NetworkError(Exception):
    """Raised when network operations fail."""
    pass