/**
 * OpenCngsm v3.0 - Baileys WhatsApp Server
 * Node.js server for WhatsApp integration
 */
const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, downloadMediaMessage } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const upload = multer({ dest: 'uploads/' });

let sock;
let qrCode = null;
let isConnected = false;

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info');

    sock = makeWASocket({
        auth: state,
        printQRInTerminal: false
    });

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            qrCode = qr;
            qrcode.generate(qr, { small: true });
            console.log('📱 QR Code generated - scan with WhatsApp');
        }

        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('❌ Connection closed. Reconnecting:', shouldReconnect);

            if (shouldReconnect) {
                setTimeout(connectToWhatsApp, 3000);
            }

            isConnected = false;
        } else if (connection === 'open') {
            console.log('✅ WhatsApp connected');
            qrCode = null;
            isConnected = true;
        }
    });

    sock.ev.on('creds.update', saveCreds);

    // Message handler
    sock.ev.on('messages.upsert', async ({ messages }) => {
        const msg = messages[0];

        if (!msg.key.fromMe && msg.message) {
            const from = msg.key.remoteJid;
            const text = msg.message.conversation || msg.message.extendedTextMessage?.text || '';

            console.log(`📩 Message from ${from}: ${text}`);

            // Forward to Python callback (via webhook or polling)
            // For now, just log
        }
    });
}

// API Endpoints

app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        hasQR: qrCode !== null
    });
});

app.get('/qr', (req, res) => {
    res.json({ qr: qrCode });
});

app.post('/send', async (req, res) => {
    const { to, message } = req.body;

    if (!isConnected) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        await sock.sendMessage(to, { text: message });
        res.json({ success: true });
    } catch (error) {
        console.error('❌ Send error:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/typing', async (req, res) => {
    const { to } = req.body;

    if (!isConnected) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try:
    await sock.sendPresenceUpdate('composing', to);
    res.json({ success: true });
} catch (error) {
    res.status(500).json({ error: error.message });
}
});

app.post('/send-image', upload.single('image'), async (req, res) => {
    const { to, caption } = req.body;
    const imagePath = req.file.path;

    if (!isConnected) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try {
        const imageBuffer = fs.readFileSync(imagePath);

        await sock.sendMessage(to, {
            image: imageBuffer,
            caption: caption || ''
        });

        // Cleanup
        fs.unlinkSync(imagePath);

        res.json({ success: true });
    } catch (error) {
        console.error('❌ Send image error:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/send-video', upload.single('video'), async (req, res) => {
    const { to, caption } = req.body;
    const videoPath = req.file.path;

    if (!isConnected) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try:
    const videoBuffer = fs.readFileSync(videoPath);

    await sock.sendMessage(to, {
        video: videoBuffer,
        caption: caption || ''
    });

    // Cleanup
    fs.unlinkSync(videoPath);

    res.json({ success: true });
} catch (error) {
    console.error('❌ Send video error:', error);
    res.status(500).json({ error: error.message });
}
});

app.post('/send-voice', upload.single('audio'), async (req, res) => {
    const { to } = req.body;
    const audioPath = req.file.path;

    if (!isConnected) {
        return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    try:
    const audioBuffer = fs.readFileSync(audioPath);

    await sock.sendMessage(to, {
        audio: audioBuffer,
        ptt: true  // Push-to-talk (voice message)
    });

    // Cleanup
    fs.unlinkSync(audioPath);

    res.json({ success: true });
} catch (error) {
    console.error('❌ Send voice error:', error);
    res.status(500).json({ error: error.message });
}
});

// Start server
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`🚀 Baileys server running on port ${PORT}`);
    connectToWhatsApp();
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('🛑 Shutting down...');
    if (sock) {
        sock.end();
    }
    process.exit(0);
});
