const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const UserSchema = new Schema({
  user_id: {
    type: String,
    required: true,
  },
  user_email: {
    type: String,
    required: true,
  },
  device_id: {
    type: String,
    required: true,
  },
  verify: {
    type: Boolean,
    required: true,
  },
  code: {
    type: String,
  },
  codeCreatedAt: {
    type: Date,
    default: null,
  },
  api_token: {
    type: String,
  },
});

const User = mongoose.model("User", UserSchema);
module.exports.User = User;
