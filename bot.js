const mineflayer = require('mineflayer');
const { pathfinder, movements, goals } = require('mineflayer-pathfinder');
const Vec3 = require('vec3');
const dgram = require('dgram');

// ==========================================
// LAN PORT AUTO-DISCOVERY HELPERS
// ==========================================

function autoDiscoverLanPort() {
  return new Promise((resolve) => {
    console.log('[+] Auto-scanning for your Minecraft Singleplayer LAN server...');
    const socket = dgram.createSocket({ type: 'udp4', reuseAddr: true });

    const timeout = setTimeout(() => {
      try { socket.close(); } catch (e) {}
      resolve(null);
    }, 3500);

    socket.on('message', (msg) => {
      const str = msg.toString();
      const match = str.match(/\[AD\](\d+)\[\/AD\]/);
      if (match) {
        clearTimeout(timeout);
        const port = parseInt(match[1]);
        try { socket.close(); } catch (e) {}
        resolve(port);
      }
    });

    socket.on('error', () => {
      clearTimeout(timeout);
      try { socket.close(); } catch (e) {}
      resolve(null);
    });

    try {
      socket.bind(4445, () => {
        try {
          socket.addMembership('224.0.2.60');
        } catch (e) {}
      });
    } catch (e) {
      clearTimeout(timeout);
      resolve(null);
    }
  });
}

async function main() {
  const useMicrosoftAuth = process.argv.includes('ms') || process.argv.includes('microsoft');
  
  const portArg = process.argv.find(arg => !isNaN(arg) && arg !== 'bot.js' && arg !== 'ms' && arg !== 'microsoft');
  let targetPort = portArg ? parseInt(portArg) : null;

  if (!targetPort) {
    targetPort = await autoDiscoverLanPort();
  }

  if (targetPort) {
    console.log(`[SUCCESS] Found active Minecraft LAN server on Port ${targetPort}!`);
  } else {
    targetPort = 63471;
    console.log(`[!] Using default port ${targetPort}.`);
  }

  console.log(`[+] Authentication Mode: ${useMicrosoftAuth ? 'Microsoft Account' : 'Offline / Local'}`);

  // Use '1.21.11' which is the latest version supported by Mineflayer
  const chosenVersion = '1.21.11';
  console.log(`[+] Using Protocol Version: '${chosenVersion}'`);

  const CONFIG = {
    host: 'localhost',
    port: targetPort,
    username: 'MinerBot',
    auth: useMicrosoftAuth ? 'microsoft' : 'offline',
    version: chosenVersion,

    miningArea: {
      minX: 360,
      maxX: 395,
      minY: 125,
      maxY: 142,
      minZ: -350,
      maxZ: -320
    }
  };

  console.log(`[+] Starting Mineflayer bot connection...`);

  const bot = mineflayer.createBot({
    host: CONFIG.host,
    port: CONFIG.port,
    username: CONFIG.username,
    auth: CONFIG.auth,
    version: CONFIG.version
  });

  bot.loadPlugin(pathfinder);

  let mcData;
  let defaultMovements;
  let isEating = false;

  bot.once('spawn', () => {
    console.log(`\n[SUCCESS] ${bot.username} connected to your Singleplayer world!`);
    mcData = require('minecraft-data')(bot.version);
    
    defaultMovements = new movements(bot, mcData);
    defaultMovements.canDig = true;
    defaultMovements.allow1by1tunnels = true;
    defaultMovements.scafoldingBlocks = [];
    bot.pathfinder.setMovements(defaultMovements);

    console.log('[+] Bot connected! Teleport it to you in chat if needed: /tp MinerBot @p');
    console.log('[+] Starting mountain mining in 5 seconds...');
    setTimeout(() => startMiningLoop(bot, CONFIG.miningArea), 5000);
  });

  bot.on('health', async () => {
    if (bot.food < 15 && !isEating) {
      const bread = bot.inventory.items().find(i => i.name === 'bread');
      if (bread) {
        isEating = true;
        console.log('[EAT] Food low. Eating bread...');
        try {
          await bot.equip(bread, 'hand');
          await bot.consume();
          console.log('[EAT] Ate bread. Food level:', bot.food);
        } catch (err) {
        } finally {
          isEating = false;
        }
      }
    }
  });

  bot.on('kicked', reason => console.log('[KICKED]', reason));
  bot.on('error', err => {
    console.error('[ERROR]', err.message);
  });
}

function getToolCategory(blockName) {
  if (['dirt', 'grass_block', 'coarse_dirt', 'podzol', 'sand', 'gravel', 'clay'].includes(blockName)) {
    return 'shovel';
  }
  if (['stone', 'cobblestone', 'deepslate', 'granite', 'diorite', 'andesite', 'coal_ore', 'iron_ore'].includes(blockName)) {
    return 'pickaxe';
  }
  return 'any';
}

function getBestTool(bot, category) {
  const items = bot.inventory.items();
  if (category === 'shovel') {
    return items.find(i => i.name.endsWith('_shovel'));
  }
  if (category === 'pickaxe') {
    const pickaxes = items.filter(i => i.name.endsWith('_pickaxe'));
    if (pickaxes.length === 0) return null;
    const tierOrder = { iron_pickaxe: 3, stone_pickaxe: 2, wooden_pickaxe: 1 };
    pickaxes.sort((a, b) => (tierOrder[b.name] || 0) - (tierOrder[a.name] || 0));
    return pickaxes[0];
  }
  return null;
}

async function craftToolIfNeeded(bot, category) {
  const mcData = require('minecraft-data')(bot.version);
  let existingTool = getBestTool(bot, category);
  if (existingTool) return existingTool;

  console.log(`[CRAFT] No ${category} found. Crafting replacement...`);

  const sticksItem = bot.inventory.items().find(i => i.name === 'stick');
  let stickCount = sticksItem ? sticksItem.count : 0;

  if (stickCount < 2) {
    const oakPlanks = bot.inventory.items().find(i => i.name.endsWith('_planks'));
    if (oakPlanks && oakPlanks.count >= 2) {
      console.log('[CRAFT] Crafting sticks from planks...');
      const stickRecipe = bot.recipesFor(mcData.itemsByName.stick.id, null, 1, null)[0];
      if (stickRecipe) {
        try {
          await bot.craft(stickRecipe, 1, null);
        } catch (e) {}
      }
    }
  }

  let craftingTableBlock = bot.findBlock({
    matching: block => block.name === 'crafting_table',
    maxDistance: 4
  });

  if (!craftingTableBlock) {
    const tableItem = bot.inventory.items().find(i => i.name === 'crafting_table');
    if (tableItem) {
      const placementRef = bot.blockAt(bot.entity.position.offset(0, -1, 1));
      if (placementRef && placementRef.name !== 'air') {
        try {
          await bot.equip(tableItem, 'hand');
          await bot.placeBlock(placementRef, new Vec3(0, 1, 0));
          await new Promise(r => setTimeout(r, 500));
          craftingTableBlock = bot.findBlock({
            matching: block => block.name === 'crafting_table',
            maxDistance: 4
          });
        } catch (e) {}
      }
    }
  }

  const targetItemName = category === 'pickaxe' ? 'stone_pickaxe' : 'stone_shovel';
  const targetItemData = mcData.itemsByName[targetItemName];

  if (targetItemData) {
    const recipes = bot.recipesFor(targetItemData.id, null, 1, craftingTableBlock);
    if (recipes.length > 0) {
      try {
        await bot.craft(recipes[0], 1, craftingTableBlock);
        console.log(`[CRAFT SUCCESS] Crafted 1x ${targetItemName}!`);
        return getBestTool(bot, category);
      } catch (err) {
        console.error(`[CRAFT ERROR] Failed crafting ${targetItemName}:`, err.message);
      }
    }
  }

  return null;
}

async function startMiningLoop(bot, miningArea) {
  const { minX, maxX, minY, maxY, minZ, maxZ } = miningArea;

  console.log(`\n==========================================`);
  console.log(`[START] Excavating Mountain Area!`);
  console.log(`==========================================\n`);

  for (let y = maxY; y >= minY; y--) {
    console.log(`\n>>> MINING LAYER Y = ${y} <<<`);
    let minedInLayer = 0;

    for (let x = minX; x <= maxX; x++) {
      for (let z = minZ; z <= maxZ; z++) {
        const blockPos = new Vec3(x, y, z);
        const block = bot.blockAt(blockPos);

        if (!block || ['air', 'cave_air', 'water', 'lava', 'bedrock'].includes(block.name)) {
          continue;
        }

        const category = getToolCategory(block.name);
        if (category !== 'any') {
          const tool = await craftToolIfNeeded(bot, category);
          if (tool) {
            try { await bot.equip(tool, 'hand'); } catch (e) {}
          }
        }

        const dist = bot.entity.position.distanceTo(blockPos);
        if (dist > 4.2) {
          try {
            await bot.pathfinder.goto(new goals.GoalNear(blockPos.x, blockPos.y, blockPos.z, 2));
          } catch (err) {
            continue;
          }
        }

        try {
          console.log(`[DIG] (${x}, ${y}, ${z}) -> ${block.name}`);
          await bot.dig(block);
          minedInLayer++;
        } catch (err) {
        }
      }
    }
    console.log(`[COMPLETED LAYER Y=${y}] Total blocks mined: ${minedInLayer}`);
  }

  console.log('\n[🎉 COMPLETE] Mountain clearing task finished!');
}

main();
