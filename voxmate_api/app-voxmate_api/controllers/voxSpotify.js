const { Vox } = require("../models/vox.js");
const { User } = require("../models/user.js");
const mongoSanitize = require("express-mongo-sanitize");

module.exports.callback = async (req, res) => {
  const code = req.query.code;
  const error = req.query.error;

  const sanitizedState = mongoSanitize.sanitize(req.query.state, {
    replaceWith: "_",
  });
  const user = await User.findOne({ api_token: sanitizedState });

  if (!user) {
    return res.send(
      "There has been an error, please close the window and try again",
    );
  }

  if (code) {
    try {
      await Vox.findOneAndUpdate(
        { user_id: user.user_id },
        { code: code, error: null },
        { upsert: true, new: true },
      );
      return res.send(
        "Success, Spotify has logged you in. You can now close this window",
      );
    } catch (err) {
      console.error("Failed to save Vox:", err);
      return res.status(500).send("DB Error");
    }
  }

  if (error) {
    await Vox.findOneAndUpdate(
      { user_id: user.user_id },
      { error: error, code: null },
      { upsert: true, new: true },
    );
    return res.send("Error: " + error);
  }

  res.send("There has been an error, please close the window and try again");
};

module.exports.waiting = async (req, res) => {
  const api_token = req.body.state;

  if (!api_token) {
    return res
      .status(200)
      .json({ welcome: "You have reached landing", status: 200 });
  }

  const user = await User.findOne({ api_token: api_token });

  if (!user) {
    return res
      .status(200)
      .json({ welcome: "You have reached landing", user: true, status: 200 });
  }

  const vox = await Vox.findOne({ user_id: user["user_id"] });

  if (!vox) {
    return res
      .status(200)
      .json({ welcome: "You have reached landing", " vox": true, status: 200 });
  }

  let user_code = vox["code"];
  if (user_code) {
    return res.status(200).json({
      welcome: "You have reached landing",
      user_code: user_code,
      status: 200,
    });
  }

  let user_error = vox["error"];
  if (user_error) {
    return res.status(200).json({
      welcome: "You have reached landing",
      user_error: user_error,
      status: 200,
    });
  }

  return res
    .status(200)
    .json({ welcome: "You have reached landing", status: 200 });
};
