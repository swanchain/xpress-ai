import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import apiClient from "@/services/apiClient";

function ReplyTweet({ availableCredits }) {
  const [topic, setTopic] = useState("");
  const [stance, setStance] = useState("");
  const [requirements, setRequirements] = useState("");
  const [tweetLoading, setTweetLoading] = useState(false);
  const [op, setOp] = useState("");
  const [reply, setReply] = useState("");

  const handleGenerate = async () => {
    // TODO: integrate tweet generation logic
    setTweetLoading(true);
    console.log("Generate Tweet", { topic, stance, requirements });
    try {
      if (availableCredits > 0 && topic) {
        const opReq = await apiClient.post(
          `/ai/get-tweet-content?tweet_url=${topic}`
        );

        setOp(opReq.data.tweet_content);

        const response = await apiClient.post(
          `/ai/generate-tweet-reply?tweet_url=${topic}`
        );

        setReply(response.data.reply_content);

        console.log("response", response.data);
      } else {
        console.log("no credits or no topic");
      }
    } catch (err) {
      console.log(err);
    }
  };

  const handlePost = () => {
    // TODO: integrate tweet posting logic
    console.log("Post Tweet", { topic, stance, requirements });
  };

  return (
    <div className="min-w-3/4 mx-auto bg-white rounded-2xl border-gray-200 border-1">
      <div>
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
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-4 focus:ring-gray-200 p-3 bg-gray-100"
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
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-4 focus:ring-gray-200 p-3 bg-gray-100"
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
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-4 focus:ring-gray-200 p-3 bg-gray-100"
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
      </div>

      <div
        className={`fixed inset-0 bg-black/50 flex items-start justify-center z-90 ${
          tweetLoading
            ? "opacity-100 pointer-events-auto"
            : "opacity-0 pointer-events-none"
        }`}
        onClick={() => {
          if (reply) {
            setTweetLoading(false);
            setReply("");
          }
        }}
      >
        <div
          className={`my-auto max-w-2/5 bg-[#f2f2f2] rounded-[20px] p-8 transition-all duration-300 ease-out tranform ${
            tweetLoading
              ? "translate-y-0 opacity-100"
              : "-translate-y-10 opacity-0"
          }`}
          onClick={(e) => {
            e.stopPropagation(); // Prevent click from bubbling to outer div
          }}
        >
          <h1 className="text-left font-bold text-2xl">Tweet</h1>
          {op ? (
            <div className="p-2 border-1 rounded-xl">
              <p className="text-left">{op}</p>
            </div>
          ) : (
            <div className="flex flex-row items-center gap-2 ">
              <svg
                className="animate-spin h-8 w-8 text-blue-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                />
              </svg>
              <h2 className="text-xl font-semibold text-gray-400 animate-pulse">
                Fetching Tweet...
              </h2>
            </div>
          )}
          {reply ? (
            <>
              <h1 className="mt-4 text-left font-bold text-2xl">Reply</h1>
              <p className=" text-left border-1 rounded-xl p-2">{reply}</p>

              <div className="mt-8 w-full flex">
                <button
                  className="black-btn w-full bg-[#76b291] "
                  onClick={() => {
                    // setPurchaseLoading(false);
                    // setTransactionHash("");
                  }}
                >
                  Send Tweet
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="flex flex-row items-center gap-2 my-4">
                <svg
                  className="animate-spin h-8 w-8 text-blue-600"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                  />
                </svg>
                <h2 className="text-xl font-semibold text-gray-400 animate-pulse">
                  Generating Reply...
                </h2>
              </div>
              {/* <p className=" text-gray-500">
                Please wait while we generate your tweet.
              </p> */}
              <div className="flex animate-pulse space-x-4">
                <div className="flex-1 space-y-6 py-1">
                  <div className="space-y-3">
                    <div className="grid grid-cols-3 gap-4">
                      <div className="col-span-2 h-2 rounded bg-gray-400"></div>
                      <div className="col-span-1 h-2 rounded bg-gray-400"></div>
                      <div className="col-span-1 h-2 rounded bg-gray-400"></div>
                      <div className="col-span-2 h-2 rounded bg-gray-400"></div>
                    </div>
                    <div className="h-2 rounded bg-gray-400"></div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
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
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none p-3 bg-gray-100 focus:ring-4 focus:ring-gray-200"
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
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none p-3 bg-gray-100 focus:ring-4 focus:ring-gray-200"
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
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none p-3 bg-gray-100 focus:ring-4 focus:ring-gray-200"
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

export default function TweetPage({ selectedTab, availableCredits }) {
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
          <CreateTweet availableCredits={availableCredits} />
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
          <ReplyTweet availableCredits={availableCredits} />
        </motion.div>
      )}
    </div>
  );
}
