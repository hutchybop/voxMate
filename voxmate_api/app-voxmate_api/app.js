if (process.env.NODE_ENV !== "production") {
  require("dotenv").config();
}

// External Imports
const express = require("express");
const path = require("path");
const ejsMate = require("ejs-mate");
const favicon = require("serve-favicon");
const helmet = require("helmet");
const { mongoose } = require("mongoose");
const mongoSanitize = require("express-mongo-sanitize");

// // Local imports
const users = require("./controllers/users");
const voxSpotify = require("./controllers/voxSpotify");

// Setting up express
const app = express();

// If in production, tells express about nginx proxy
if (process.env.NODE_ENV === "production") {
  app.set("trust proxy", 1);
}

// Setting up mongoose
const dbName = "voxMate_api";
const dbUrl =
  "mongodb+srv://hutch:" +
  process.env.MONGODB +
  "@hutchybop.kpiymrr.mongodb.net/" +
  dbName +
  "?retryWrites=true&w=majority&appName=hutchyBop";
mongoose.connect(dbUrl);
// Error Handling for the db connection
const db = mongoose.connection;
db.on("error", console.error.bind(console, "connection error:"));
db.once("open", () => {
  console.log("Database connected");
});

// Serve favicon from public/favicon directory
app.use(favicon(path.join(__dirname, "public", "favicon", "favicon.ico")));
// Handle favicon requests explicitly
app.use("/favicon.ico", (req, res) => {
  res.sendStatus(204); // No Content
});

// Setting up the app
app.engine("ejs", ejsMate); // Tells express to use ejsmate for rendering .ejs html files
app.set("view engine", "ejs"); // Sets ejs as the default engine
app.set("views", path.join(__dirname, "views")); // Forces express to look at views directory for .ejs files
app.use(express.urlencoded({ extended: true })); // Makes req.body available
app.use(express.json()); // Middleware to parse JSON bodies
app.use(express.static(path.join(__dirname, "/public"))); // Serves static files (css, js, imgaes) from public directory

// Global tracker middleware
const { getIpInfoMiddleware, trackRequest } = require("../../tracker/app-tracker/utils/tracker");
const { checkBlockedIP } = require("./utils/blockedIPMiddleware");
app.use(getIpInfoMiddleware);
app.use(trackRequest('voxmate_api'));

// Global blocking middleware (reads from tracker database)
app.use(checkBlockedIP);

// Instead of app.use(mongoSanitize()); req.query is now read only in express 5, So inline sanitation is required in the rest of the code
// Helps to stop mongo injection by not allowing certain characters in the query string
app.use((req, res, next) => {
  if (req.body)
    req.body = mongoSanitize.sanitize(req.body, { replaceWith: "_" });
  if (req.params)
    req.params = mongoSanitize.sanitize(req.params, { replaceWith: "_" });
  next();
});

// Setting up helmet to allow certain scripts/stylesheets
const scriptSrcUrls = [
  "https://stackpath.bootstrapcdn.com/",
  "https://cdnjs.cloudflare.com/",
  "https://cdn.jsdelivr.net",
  "https://code.jquery.com/",
  "https://www.google.com/recaptcha/api.js",
  "https://www.gstatic.com/recaptcha/releases/",
  "https://use.fontawesome.com/",
];
const styleSrcUrls = [
  "https://kit-free.fontawesome.com/",
  "https://stackpath.bootstrapcdn.com/",
  "https://fonts.googleapis.com/",
  "https://use.fontawesome.com/",
  "https://cdn.jsdelivr.net/",
  "https://cdnjs.cloudflare.com/",
  "https://fonts.gstatic.com",
  "https://www.gstatic.com/recaptcha/releases/",
];
const imgSrcUrls = [
  "https://www.gstatic.com/recaptcha/",
  "https://www.google.com/recaptcha/",
];
const connectSrcUrls = [
  "https://www.google.com/",
  "https://www.gstatic.com/recaptcha/",
];
const fontSrcUrls = [
  "https://cdnjs.cloudflare.com/",
  "https://fonts.gstatic.com",
  "https://fonts.googleapis.com/",
  "https://use.fontawesome.com/",
];
const frameSrcUrls = ["https://www.google.com", "https://www.recaptcha.net"];
// Function to configure helmet based on environment
function configureHelmet() {
  if (process.env.NODE_ENV === "production") {
    app.use(
      helmet({
        contentSecurityPolicy: {
          directives: {
            defaultSrc: ["'self'"],
            connectSrc: ["'self'", ...connectSrcUrls],
            scriptSrc: ["'self'", "'unsafe-inline'", ...scriptSrcUrls],
            styleSrc: ["'self'", "'unsafe-inline'", ...styleSrcUrls],
            workerSrc: ["'self'", "blob:"],
            objectSrc: ["'none'"],
            imgSrc: ["'self'", "blob:", "data:", ...imgSrcUrls],
            fontSrc: ["'self'", ...fontSrcUrls],
            frameSrc: ["'self'", ...frameSrcUrls],
            upgradeInsecureRequests: null, // Relax or adjust as necessary
            scriptSrcAttr: ["'self'", "'unsafe-inline'"], // Adjust based on your needs
          },
        },
        crossOriginOpenerPolicy: { policy: "same-origin" },
        originAgentCluster: true,
      }),
    );
  } else {
    app.use(
      helmet({
        contentSecurityPolicy: {
          directives: {
            defaultSrc: ["'self'", "*"],
            connectSrc: ["'self'", "*", ...connectSrcUrls],
            scriptSrc: [
              "'self'",
              "'unsafe-inline'",
              "'unsafe-eval'",
              "*",
              ...scriptSrcUrls,
            ],
            styleSrc: ["'self'", "'unsafe-inline'", "*", ...styleSrcUrls],
            workerSrc: ["'self'", "blob:"],
            objectSrc: ["'self'", "*"],
            imgSrc: ["'self'", "blob:", "data:", "*", ...imgSrcUrls],
            fontSrc: ["'self'", "*", ...fontSrcUrls],
            frameSrc: ["'self'", "*", ...frameSrcUrls],
            upgradeInsecureRequests: null,
            scriptSrcAttr: ["'self'", "'unsafe-inline'", "*"],
          },
        },
        crossOriginOpenerPolicy: { policy: "unsafe-none" }, // Relaxed for development
        originAgentCluster: false, // Disabled in development
        referrerPolicy: { policy: "no-referrer-when-downgrade" }, // Less strict referrer policy
        frameguard: false, // Disable clickjacking protection in development
        hsts: false, // Disable HTTP Strict Transport Security (HSTS) in development
        noSniff: false, // Allow MIME type sniffing in development
      }),
    );
  }
}
// Apply helmet configuration
configureHelmet();

app.use(async (req, res, next) => {
  // Middleware

  next();
});

// User routes
app.post("/new", users.new);
app.post("/verify", users.verify);
// voxSpotify routes
app.get("/voxSpotify/callback", voxSpotify.callback);
app.post("/voxSpotify/waiting", voxSpotify.waiting);

// Unknown (404) webpage error
// Uses the ExpressError to pass message (Page Not Found) and statusCode (404)
// to the error handler
app.use((req, res) => {
  res.status(404).json({ error: "Page not found", status: 404 });
});

// Start server on port using HTTP
const port = 3005;
app.listen(port, "0.0.0.0", () => {
  console.log(`Server running on port ${port} on all interfaces`);
});
