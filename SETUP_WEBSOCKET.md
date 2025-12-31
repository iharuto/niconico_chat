1. 

```bash
npm init -y

# Wrote to /Users/haruto/niconico_chat/package.json:

# {
#   "name": "niconico_chat",
#   "version": "1.0.0",
#   "description": "## Inspiration",
#   "main": "index.js",
#   "scripts": {
#     "test": "echo \"Error: no test specified\" && exit 1"
#   },
#   "keywords": [],
#   "author": "",
#   "license": "ISC"
# }
```

2.

```bash
npm i express ws

# added 66 packages, and audited 67 packages in 2s

# 22 packages are looking for funding
#   run `npm fund` for details

# found 0 vulnerabilities
```

3. create `server.js` and paste below

<details><summary> server.js contents </summary>

```js
const express = require("express");
const http = require("http");
const path = require("path");
const WebSocket = require("ws");

const ROOM_CODE = process.env.ROOM_CODE || "1234"; // 起動時に環境変数で上書き推奨
const PORT = process.env.PORT || 3000;

const app = express();
app.use(express.static(path.join(__dirname, "public")));

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

/** 認証済みクライアントだけ入れる */
const authedClients = new Set();

function broadcast(obj) {
  const msg = JSON.stringify(obj);
  for (const ws of authedClients) {
    if (ws.readyState === WebSocket.OPEN) ws.send(msg);
  }
}

wss.on("connection", (ws, req) => {
  ws.isAuthed = false;
  ws.nickname = "anon";

  ws.on("message", (data) => {
    let msg;
    try {
      msg = JSON.parse(data.toString("utf-8"));
    } catch {
      return;
    }

    // ① 最初に auth を要求
    if (!ws.isAuthed) {
      if (msg.type !== "auth") {
        ws.send(JSON.stringify({ type: "error", message: "Need auth first" }));
        ws.close();
        return;
      }
      const code = String(msg.code || "");
      const nickname = String(msg.nickname || "anon").slice(0, 24);

      if (code !== ROOM_CODE) {
        ws.send(JSON.stringify({ type: "error", message: "Room code invalid" }));
        ws.close();
        return;
      }

      ws.isAuthed = true;
      ws.nickname = nickname;
      authedClients.add(ws);

      ws.send(JSON.stringify({ type: "ok", message: "authed" }));
      broadcast({ type: "system", message: `${ws.nickname} joined` });
      return;
    }

    // ② 認証後：チャット
    if (msg.type === "chat") {
      const text = String(msg.text || "").slice(0, 500);
      if (!text.trim()) return;
      broadcast({
        type: "chat",
        nickname: ws.nickname,
        text,
        ts: Date.now(),
      });
    }
  });

  ws.on("close", () => {
    if (authedClients.has(ws)) {
      authedClients.delete(ws);
      broadcast({ type: "system", message: `${ws.nickname} left` });
    }
  });
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`LAN chat server running on port ${PORT}`);
  console.log(`ROOM_CODE = ${ROOM_CODE}`);
  console.log(`Open: http://<server-lan-ip>:${PORT}`);
});

```

</details>


4.

```bash
mkdir public
touch public/index.html
```

then paste below

<details><summary> index.html contents </summary>

```html
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>LAN Chat</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 20px; }
    #log { border: 1px solid #ccc; padding: 10px; height: 320px; overflow: auto; white-space: pre-wrap; }
    .row { margin: 8px 0; display: flex; gap: 8px; }
    input { padding: 6px; }
    button { padding: 6px 10px; }
    #chatBox { display:none; }
  </style>
</head>
<body>
  <h1>LAN Chat</h1>

  <div id="authBox">
    <div class="row">
      <input id="nickname" placeholder="Nickname" maxlength="24" />
      <input id="code" placeholder="Room code" />
      <button id="join">Join</button>
    </div>
    <div id="authMsg"></div>
  </div>

  <div id="chatBox">
    <div id="log"></div>
    <div class="row">
      <input id="text" placeholder="Message" style="flex:1" maxlength="500" />
      <button id="send">Send</button>
    </div>
  </div>

<script>
  let ws;

  const log = (line) => {
    const el = document.getElementById("log");
    el.textContent += line + "\n";
    el.scrollTop = el.scrollHeight;
  };

  const connect = () => {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${proto}://${location.host}`);

    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === "ok") {
        document.getElementById("authBox").style.display = "none";
        document.getElementById("chatBox").style.display = "block";
        log("[system] joined");
      } else if (msg.type === "error") {
        document.getElementById("authMsg").textContent = msg.message;
      } else if (msg.type === "system") {
        log(`[system] ${msg.message}`);
      } else if (msg.type === "chat") {
        const t = new Date(msg.ts).toLocaleTimeString();
        log(`[${t}] ${msg.nickname}: ${msg.text}`);
      }
    };

    ws.onclose = () => log("[system] disconnected");
  };

  document.getElementById("join").onclick = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) connect();

    const nickname = document.getElementById("nickname").value || "anon";
    const code = document.getElementById("code").value || "";

    // 接続が開くのを待って auth
    const sendAuth = () => ws.send(JSON.stringify({ type: "auth", nickname, code }));

    if (ws.readyState === WebSocket.OPEN) sendAuth();
    else ws.addEventListener("open", sendAuth, { once: true });
  };

  const sendChat = () => {
    const text = document.getElementById("text").value;
    document.getElementById("text").value = "";
    if (!text.trim()) return;
    ws.send(JSON.stringify({ type: "chat", text }));
  };

  document.getElementById("send").onclick = sendChat;
  document.getElementById("text").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChat();
  });
</script>
</body>
</html>

```

</details>