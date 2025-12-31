const express = require("express");
const http = require("http");
const path = require("path");
const WebSocket = require("ws");
const fs = require("fs");

const ROOM_CODE = process.env.ROOM_CODE || "1234"; // 起動時に環境変数で上書き推奨
const PORT = process.env.PORT || 3000;
const MAX_CLIENTS = parseInt(process.env.MAX_CLIENTS || "30", 10);
let userCounter = 0; // Auto-increment for USER_### assignment

/**
 * Format current date/time as YYYYMMDD_HHMMSS for filename
 */
function formatNowForFilename() {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  const hh = String(now.getHours()).padStart(2, "0");
  const min = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  return `${yyyy}${mm}${dd}_${hh}${min}${ss}`;
}

/**
 * Format timestamp (ms since epoch) as HH:MM:SS
 */
function formatTimeHHMMSS(ts) {
  const d = new Date(ts);
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  const ss = String(d.getSeconds()).padStart(2, "0");
  return `${hh}:${mm}:${ss}`;
}

/**
 * Escape string for safe CSV output
 * Always wraps in quotes and doubles internal quotes
 */
function csvEscape(str) {
  if (str == null) return '""';
  const s = String(str);
  return `"${s.replace(/"/g, '""')}"`;
}

const app = express();
app.use(express.static(path.join(__dirname, "public")));

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

/** 認証済みクライアントだけ入れる */
const authedClients = new Set();

// CSV Logging Setup
const LOG_DIR = path.join(__dirname, "chat_logs");
let logFilePath = null;

try {
  fs.mkdirSync(LOG_DIR, { recursive: true });
  const timestamp = formatNowForFilename();
  logFilePath = path.join(LOG_DIR, `${timestamp}_log.csv`);

  // Write CSV header
  fs.writeFileSync(logFilePath, "time,nickname,user_id,text\n", "utf-8");
  console.log(`CSV log initialized: ${logFilePath}`);
} catch (err) {
  console.error("Failed to initialize CSV log:", err.message);
  console.error("Chat will continue but messages will NOT be logged.");
  logFilePath = null;
}

/**
 * Append a chat message to the CSV log file
 */
function logChatToCSV(time, nickname, userId, text) {
  if (!logFilePath) return; // Logging disabled

  try {
    const line = `${csvEscape(time)},${csvEscape(nickname)},${csvEscape(userId)},${csvEscape(text)}\n`;
    fs.appendFileSync(logFilePath, line, "utf-8");
  } catch (err) {
    console.error("Failed to write to CSV log:", err.message);
  }
}

function broadcast(obj) {
  const msg = JSON.stringify(obj);
  for (const ws of authedClients) {
    if (ws.readyState === WebSocket.OPEN) ws.send(msg);
  }
}

wss.on("connection", (ws, req) => {
  ws.isAuthed = false;
  ws.nickname = "anon";
  ws.userId = null; // Will be assigned during auth

  ws.on("message", (data) => {
    let msg;
    try {
      msg = JSON.parse(data.toString("utf-8"));
    } catch {
      return;
    }

    // ① 最初に auth を要求
    if (!ws.isAuthed) {
      // Check room capacity first
      if (authedClients.size >= MAX_CLIENTS) {
        ws.send(JSON.stringify({ type: "error", message: "Room full" }));
        ws.close();
        return;
      }
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

      // Generate USER_### ID
      userCounter++;
      ws.userId = `USER_${String(userCounter).padStart(3, "0")}`;

      ws.isAuthed = true;
      ws.nickname = nickname;
      authedClients.add(ws);

      ws.send(JSON.stringify({ type: "ok", message: "authed", user_id: ws.userId }));
      broadcast({ type: "system", message: `${ws.userId} joined` });
      return;
    }

    // ② 認証後：チャット
    if (msg.type === "chat") {
      const text = String(msg.text || "").slice(0, 500);
      if (!text.trim()) return;

      const ts = Date.now();
      const timeStr = formatTimeHHMMSS(ts);

      // Log to CSV
      logChatToCSV(timeStr, ws.nickname, ws.userId, text);

      broadcast({
        type: "chat",
        user_id: ws.userId,
        nickname: ws.nickname, // Keep for CSV logging
        text,
        ts,
      });
    }
  });

  ws.on("close", () => {
    if (authedClients.has(ws)) {
      authedClients.delete(ws);
      broadcast({ type: "system", message: `${ws.userId} left` });
    }
  });
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`LAN chat server running on port ${PORT}`);
  console.log(`ROOM_CODE = ${ROOM_CODE}`);
  console.log(`Open: http://<server-lan-ip>:${PORT}`);
});
