import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

function ReplyTweet() {
  const [topic, setTopic] = useState("");
  const [stance, setStance] = useState("");
  const [requirements, setRequirements] = useState("");
  const handleGenerate = () => {
    // TODO: integrate tweet generation logic
    console.log("Generate Tweet", { topic, stance, requirements });
  };

  const handlePost = () => {
    // TODO: integrate tweet posting logic
    console.log("Post Tweet", { topic, stance, requirements });
  };

  return (
    <div className="min-w-3/4 mx-auto bg-white rounded-2xl border-gray-200 border-1">
      <form>
        <h2 className="font-medium text-xl mb-1 justify-start flex flex-row border-b-1 p-8 border-gray-200">
          Generate Reply
        </h2>
        <div className="space-y-6 p-8">
          <div>
            <label className=" font-medium mb-2 flex" htmlFor="topic">
              Tweet to Reply To
            </label>
            <input
              id="topic"
              type="text"
              placeholder="Paste Tweet URL..."
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-0 p-3 bg-gray-100"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>

          <div>
            <label className=" font-medium mb-2 flex gap-1" htmlFor="stance">
              Choose Sentiment
            </label>
            <select
              id="stance"
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-0 p-3 bg-gray-100"
              value={stance}
              onChange={(e) => setStance(e.target.value)}
            >
              <option value="">Choose Sentiment...</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>

          <div>
            <label
              className="flex font-medium mb-2 gap-1"
              htmlFor="requirements"
            >
              Additional Context{" "}
              <span className="text-gray-400"> (Optional)</span>
            </label>
            <textarea
              id="requirements"
              rows={3}
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-0 p-3 bg-gray-100"
              placeholder=""
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
            />
          </div>

          <div className="flex justify-between">
            <button onClick={handleGenerate} className="black-btn">
              Generate Tweet
            </button>
            <button onClick={handlePost} className="black-btn bg-[#76b291] ">
              Post Reply
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

function CreateTweet() {
  const [topic, setTopic] = useState("");
  const [stance, setStance] = useState("");
  const [requirements, setRequirements] = useState("");
  const handleGenerate = () => {
    // TODO: integrate tweet generation logic
    console.log("Generate Tweet", { topic, stance, requirements });
  };

  const handlePost = () => {
    // TODO: integrate tweet posting logic
    console.log("Post Tweet", { topic, stance, requirements });
  };

  return (
    <div className="min-w-3/4 mx-auto bg-white rounded-2xl border-gray-200 border-1">
      <form>
        <h2 className="font-medium text-xl mb-1 justify-start flex flex-row border-b-1 p-8 border-gray-200">
          Create New Tweet
        </h2>
        <div className="space-y-6 p-8">
          <div>
            <label className=" font-medium mb-2 flex" htmlFor="topic">
              Topic
            </label>
            <input
              id="topic"
              type="text"
              placeholder="What would you like to tweet about?"
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-0 p-3 bg-gray-100"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>

          <div>
            <label className=" font-medium mb-2 flex gap-1" htmlFor="stance">
              Stance <span className="text-gray-400"> (Optional)</span>
            </label>
            <select
              id="stance"
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-0 p-3 bg-gray-100"
              value={stance}
              onChange={(e) => setStance(e.target.value)}
            >
              <option value="">Choose stance...</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>

          <div>
            <label
              className="flex font-medium mb-2 gap-1"
              htmlFor="requirements"
            >
              Additional Requirements{" "}
              <span className="text-gray-400"> (Optional)</span>
            </label>
            <textarea
              id="requirements"
              rows={3}
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-0 p-3 bg-gray-100"
              placeholder=""
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
            />
          </div>

          <div className="flex justify-between ">
            <button onClick={handleGenerate} className="black-btn">
              Generate Tweet
            </button>
            <button onClick={handlePost} className="black-btn bg-[#76b291] ">
              Post Tweet
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

export default function TweetPage({ selectedTab }) {
  return (
    <div className="lg:min-w-3/4 mx-auto bg-white rounded-2xl">
      {selectedTab === "create" && (
        <motion.div
          key="create"
          initial={{ x: "-50%" }}
          animate={{ x: 0 }}
          transition={{ type: "tween", duration: 0.2 }}
          className=" inset-0"
        >
          <CreateTweet />
        </motion.div>
      )}
      {selectedTab === "reply" && (
        <motion.div
          key="reply"
          initial={{ x: "50%" }}
          animate={{ x: 0 }}
          transition={{ type: "tween", duration: 0.2 }}
          className=" inset-0"
        >
          <ReplyTweet />
        </motion.div>
      )}
    </div>
  );
}
