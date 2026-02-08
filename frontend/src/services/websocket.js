/**
 * OpenCngsm MCP v3.0 - WebSocket Client
 * Replaces REST API with WebSocket communication
 */

class WebSocketClient {
    constructor(url = 'ws://127.0.0.1:18789/ws') {
        this.url = url;
        this.ws = null;
        this.clientId = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.messageHandlers = new Map();
        this.eventHandlers = new Map();
        this.pendingMessages = new Map();
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.url);

                this.ws.onopen = () => {
                    console.log('✅ WebSocket connected');
                    this.reconnectAttempts = 0;
                    this.reconnectDelay = 1000;
                };

                this.ws.onmessage = (event) => {
                    this.handleMessage(JSON.parse(event.data));
                };

                this.ws.onerror = (error) => {
                    console.error('❌ WebSocket error:', error);
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log('🔌 WebSocket disconnected');
                    this.handleDisconnect();
                };

                // Wait for system message with client_id
                const systemHandler = (message) => {
                    if (message.type === 'system' && message.payload.event === 'connected') {
                        this.clientId = message.payload.client_id;
                        console.log(`🆔 Client ID: ${this.clientId}`);
                        this.off('system', systemHandler);
                        resolve(this.clientId);
                    }
                };
                this.on('system', systemHandler);

            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Disconnect from WebSocket server
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    /**
     * Handle incoming message
     */
    handleMessage(message) {
        const { type, id, payload } = message;

        console.log(`📨 Received ${type}:`, message);

        // Handle pong (heartbeat response)
        if (type === 'pong') {
            return;
        }

        // Handle heartbeat
        if (type === 'heartbeat') {
            return;
        }

        // Resolve pending message
        if (id && this.pendingMessages.has(id)) {
            const { resolve } = this.pendingMessages.get(id);
            this.pendingMessages.delete(id);
            resolve(payload);
        }

        // Call type-specific handlers
        if (this.messageHandlers.has(type)) {
            const handlers = this.messageHandlers.get(type);
            handlers.forEach(handler => handler(message));
        }

        // Call event handlers
        if (type === 'event' && payload.event) {
            if (this.eventHandlers.has(payload.event)) {
                const handlers = this.eventHandlers.get(payload.event);
                handlers.forEach(handler => handler(payload.data));
            }
        }
    }

    /**
     * Handle disconnection and attempt reconnect
     */
    handleDisconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connect().catch(error => {
                    console.error('Reconnection failed:', error);
                });
            }, this.reconnectDelay);

            // Exponential backoff
            this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000); // Max 30 seconds
        } else {
            console.error('❌ Max reconnection attempts reached');
        }
    }

    /**
     * Send message to server
     */
    send(type, payload, waitForResponse = false) {
        return new Promise((resolve, reject) => {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                reject(new Error('WebSocket not connected'));
                return;
            }

            const id = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            const message = {
                type,
                id,
                payload,
                timestamp: new Date().toISOString()
            };

            if (waitForResponse) {
                this.pendingMessages.set(id, { resolve, reject });

                // Timeout after 30 seconds
                setTimeout(() => {
                    if (this.pendingMessages.has(id)) {
                        this.pendingMessages.delete(id);
                        reject(new Error('Message timeout'));
                    }
                }, 30000);
            }

            this.ws.send(JSON.stringify(message));

            if (!waitForResponse) {
                resolve();
            }
        });
    }

    /**
     * Send user message to agent
     */
    async sendMessage(content, sessionId = 'main', userId = null) {
        const payload = {
            session_id: sessionId,
            content,
            user_id: userId || this.clientId,
            metadata: {}
        };

        return await this.send('message', payload, true);
    }

    /**
     * Execute command
     */
    async executeCommand(command, args = {}) {
        const payload = {
            command,
            args
        };

        return await this.send('command', payload, true);
    }

    /**
     * Get system status
     */
    async getStatus() {
        return await this.executeCommand('status');
    }

    /**
     * List sessions
     */
    async listSessions() {
        return await this.executeCommand('session.list');
    }

    /**
     * Create session
     */
    async createSession(sessionId, type = 'group') {
        return await this.executeCommand('session.create', { session_id: sessionId, type });
    }

    /**
     * Destroy session
     */
    async destroySession(sessionId) {
        return await this.executeCommand('session.destroy', { session_id: sessionId });
    }

    /**
     * Update presence
     */
    async updatePresence(status = 'online') {
        return await this.executeCommand('presence.update', { status });
    }

    /**
     * Subscribe to events
     */
    async subscribe(events) {
        return await this.send('subscribe', { events }, true);
    }

    /**
     * Register message handler
     */
    on(type, handler) {
        if (!this.messageHandlers.has(type)) {
            this.messageHandlers.set(type, []);
        }
        this.messageHandlers.get(type).push(handler);
    }

    /**
     * Unregister message handler
     */
    off(type, handler) {
        if (this.messageHandlers.has(type)) {
            const handlers = this.messageHandlers.get(type);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    /**
     * Register event handler
     */
    onEvent(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }

    /**
     * Unregister event handler
     */
    offEvent(event, handler) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    /**
     * Check if connected
     */
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// Export singleton instance
const wsClient = new WebSocketClient();

export default wsClient;
