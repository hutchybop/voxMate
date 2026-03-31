const { MongoClient } = require("mongodb");

const trackerDbUrl = process.env.MONGODB 
  ? `mongodb+srv://hutch:${encodeURIComponent(process.env.MONGODB)}@hutchybop.kpiymrr.mongodb.net/longrunnerTracker?retryWrites=true&w=majority`
  : "mongodb://localhost:27017/longrunnerTracker";

let client;
let blockedIPCache = new Set();
let lastCacheUpdate = 0;
const CACHE_TTL = 5 * 60 * 1000;

const getBlockedIPs = async () => {
  try {
    if (!client) {
      client = new MongoClient(trackerDbUrl);
      await client.connect();
    }
    
    const db = client.db();
    const blocked = await db.collection("blockedips").find().toArray();
    
    blockedIPCache = new Set();
    blocked.forEach((blockedDoc) => {
      if (blockedDoc.blockedIPArray && Array.isArray(blockedDoc.blockedIPArray)) {
        blockedDoc.blockedIPArray.forEach((ip) => {
          if (ip && typeof ip === "string") {
            blockedIPCache.add(ip.trim());
          }
        });
      }
    });

    lastCacheUpdate = Date.now();
    console.log(`Updated blocked IP cache with ${blockedIPCache.size} IPs`);
  } catch (error) {
    console.error("Error updating blocked IP cache:", error.message);
  }
};

const checkBlockedIP = async (req, res, next) => {
  try {
    if (Date.now() - lastCacheUpdate > CACHE_TTL) {
      await getBlockedIPs();
    }

    let ip = req.ipInfo?.ip || req.ip || req.ips || req.connection?.remoteAddress;

    if (ip && ip.includes("::ffff:")) {
      ip = ip.replace("::ffff:", "");
    }

    if (ip && blockedIPCache.has(ip)) {
      console.log(`Blocked IP attempted access: ${ip} to ${req.path}`);
      return res.status(403).send("Access Denied - Your IP has been blocked");
    }

    next();
  } catch (error) {
    console.error("Error in blocked IP middleware:", error.message);
    next();
  }
};

getBlockedIPs();

module.exports = { checkBlockedIP };
