const crypto = require("crypto");
const { User } = require("../models/user");
const { mail } = require("../utils/mail");

module.exports.new = async (req, res) => {
  const { device_id, unverified_user_id, email } = req.body;

  if (!device_id || !unverified_user_id || !email) {
    return res
      .status(200)
      .json({ welcome: "You have reached landing", status: 200 });
  }

  // Generate secure 6-digit code
  const code = Math.floor(100000 + crypto.randomInt(900000)).toString();

  const checkUser = await User.findOne({ user_id: unverified_user_id });

  if (!checkUser) {
    // If user not already in DB create the user
    const newUser = new User({
      user_id: unverified_user_id,
      user_email: email,
      device_id,
      verify: false,
      code,
      codeCreatedAt: Date.now(),
    });
    await newUser.save();
  } else {
    // If the user is already in the DB update the code and codeCreatedAt
    await User.findOneAndUpdate(
      { user_id: unverified_user_id },
      { $set: { code: code, codeCreatedAt: Date.now() } },
    );
  }

  // Send code to user email
  mail(
    "voxMate email verification code: " + code,
    "Hello, \n\n" +
      "Welcome to voxMate.\n\n" +
      "To verify your email address, please enter the code below:\n\n" +
      code +
      "\n\n" +
      "The code will expire in 1 hour!",
    email,
  );

  res
    .status(200)
    .json({ success: true, welcome: "You have reached landing", status: 200 });
};

module.exports.verify = async (req, res) => {
  const { device_id, unverified_user_id, email, user_code } = req.body;

  if (!device_id || !unverified_user_id || !email || !user_code) {
    return res
      .status(200)
      .json({ welcome: "You have reached landing", status: 200 });
  }

  const checkUser = await User.findOne({ user_id: unverified_user_id });

  if (checkUser) {
    // Creating variables to check if the code has expired
    const now = new Date();
    const codeCreatedAt = new Date(checkUser["codeCreatedAt"]).getTime();
    const oneHour = 60 * 60 * 1000; // milliseconds
    if (now - codeCreatedAt > oneHour) {
      // Generate secure 6-digit code
      const code = Math.floor(100000 + crypto.randomInt(900000)).toString();
      // Add new code to DB
      await User.findOneAndUpdate(
        { user_id: unverified_user_id },
        { $set: { code: code, codeCreatedAt: new Date() } },
      );
      // Send code to user email
      mail(
        "voxMate email verification code: " + code,
        "Hello, \n\n" +
          "Welcome to voxMate.\n\n" +
          "To verify your email address, please enter the code below:\n\n" +
          code +
          "\n\n" +
          "The code will expire in 1 hour!",
        email,
      );
      return res.status(200).json({
        welcome: "You have reached landing",
        expired: true,
        status: 200,
      });
    }
    if (checkUser["code"] === user_code) {
      const api_token = crypto.randomBytes(32).toString("hex");
      await User.findOneAndUpdate(
        { user_id: unverified_user_id },
        {
          $set: {
            api_token: api_token,
            verify: true,
            code: null,
            codeCreatedAt: null,
          },
        },
      );
      return res.status(200).json({
        welcome: "You have reached landing",
        success: true,
        api_token: api_token,
        status: 200,
      });
    } else {
      return res.status(200).json({
        welcome: "You have reached landing",
        mismatch: true,
        status: 200,
      });
    }
  }

  res.status(200).json({ welcome: "You have reached landing", status: 200 });
};
