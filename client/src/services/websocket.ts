type WebSocketListener = (data: any) => void;

export class LiveWebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private listeners: Set<WebSocketListener> = new Set();
  private isIntentionalClose = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private statusListeners: Set<(connected: boolean) => void> = new Set();

  constructor(path: string) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    this.url = `${protocol}//${host}${path}`;
  }

  public connect() {
    this.isIntentionalClose = false;
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.notifyStatus(true);
      };

      this.ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.listeners.forEach((listener) => listener(parsed));
        } catch (e) {
          console.warn('Failed to parse WebSocket JSON payload', e);
        }
      };

      this.ws.onclose = () => {
        this.notifyStatus(false);
        if (!this.isIntentionalClose && this.reconnectAttempts < this.maxReconnectAttempts) {
          const timeout = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), 10000);
          this.reconnectAttempts++;
          setTimeout(() => this.connect(), timeout);
        }
      };

      this.ws.onerror = (err) => {
        console.error('WebSocket connection error', err);
        this.ws?.close();
      };
    } catch (e) {
      console.error('WebSocket instantiation error', e);
    }
  }

  public subscribe(listener: WebSocketListener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  public onStatusChange(callback: (connected: boolean) => void): () => void {
    this.statusListeners.add(callback);
    callback(this.ws?.readyState === WebSocket.OPEN);
    return () => {
      this.statusListeners.delete(callback);
    };
  }

  private notifyStatus(connected: boolean) {
    this.statusListeners.forEach((cb) => cb(connected));
  }

  public disconnect() {
    this.isIntentionalClose = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
