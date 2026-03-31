const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const VoxSchema = new Schema({
  user_id: {
    type: String,
    required: true,
  },
  error: {
    type: String,
  },
  code: {
    type: String,
  },
});

const Vox = mongoose.model("Vox", VoxSchema);
module.exports.Vox = Vox;
