# 🎵 voxMate_api

A private Node.js API that manages Spotify user authentication and callback handling for the `voxMate` smart speaker app.

---

## 📘 Overview

This API acts as the secure backend bridge between Spotify’s OAuth2 flow and the `voxMate` clients. It manages login, token handling, and callback responses — all without a frontend.

---

## ✨ Features

- 🔐 Handles Spotify OAuth login and callback redirects  
- 🧠 Issues one-time auth codes securely to registered clients (e.g., Raspberry Pi devices)  
- 🖥️ Designed for headless use — no UI or static frontend  
- 🛡️ Uses security best practices (e.g., Helmet headers)

---

## 🧰 Technologies

- 🟩 Node.js  
- ⚙️ Express.js  
- 📦 dotenv  
- 🛡️ Helmet  
- 🎧 Spotify Web API

--