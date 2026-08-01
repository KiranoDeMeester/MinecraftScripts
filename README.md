# Minecraft Mountain Miner Bot

An automated Minecraft bot built using **Mineflayer** and **Mineflayer Pathfinder** in Node.js. It mines a designated 3D mountain area layer-by-layer and automatically crafts pickaxes and shovels from raw inventory materials when tools break or run out.

---

## 🚀 Features
- **Automated Excavation**: Clears a specified bounding box `(minX, maxX, minY, maxY, minZ, maxZ)`.
- **Top-Down Layer Mining**: Prevents floating blocks and ensures the bot doesn't dig under itself or fall.
- **Dynamic Tool Selection**: Switches automatically between shovels (for dirt, sand, gravel) and pickaxes (for stone, granite, ores).
- **Auto-Crafting**: Detects missing tools and crafts replacement pickaxes/shovels (iron, stone, or wood) using wood, cobblestone, or iron ingots in inventory (and uses/places crafting tables as required).
- **Pathfinding**: Moves safely around terrain using A* pathfinding.

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- Node.js (v18+ recommended)
- A Minecraft Java Edition server (Local host, LAN world with cheats enabled, Paper, Spigot, or Vanilla)

### 2. Install Dependencies
In this directory, run:
```bash
npm install
```

### 3. Configuration
Open `bot.js` and edit the `CONFIG` object at the top of the file:
```js
const CONFIG = {
  host: 'localhost',       // Server IP address
  port: 25565,             // Server port
  username: 'MountainMiner',// Bot username
  version: false,          // Auto-detect or set e.g. '1.20.1'

  miningArea: {
    minX: 100, // Minimum X coordinate
    maxX: 150, // Maximum X coordinate
    minY: 64,  // Bottom Y coordinate (ground level)
    maxY: 110, // Top Y coordinate (mountain peak)
    minZ: 200, // Minimum Z coordinate
    maxZ: 250  // Maximum Z coordinate
  }
};
```

### 4. Running the Bot
Make sure your Minecraft server is running and the bot has inventory items (wood logs/planks, cobblestone, or iron ingots).

Start the script:
```bash
npm start
```
or
```bash
node bot.js
```

---

## 💡 Alternative Approaches

### 1. ComputerCraft: Tweaked (Lua Mining Turtles)
If you play with Minecraft mods, a **Mining Turtle** with a crafting module attached can be placed in-game. You can write a Lua script for the Turtle to dig a 3D box, drop off cobble/dirt into a chest behind it, and craft replacement diamond/iron pickaxes when durability expires.

### 2. Baritone (Client Mod)
If you prefer a client-side AI bot mod for Fabric/Forge, **Baritone** allows commands directly in chat:
- `#clear <x1> <y1> <z1> <x2> <y2> <z2>` - Clears out a defined volume.
- `#mine iron_ore diamond_ore` - Automatically mines target blocks and uses pathfinding to navigate caves.
