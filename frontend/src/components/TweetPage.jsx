import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import apiClient from "@/services/apiClient";

function ReplyTweet({
  availableCredits,
  getUser,
  getTweetHistory,
  availableModels,
  betaVersion,
}) {
  const [url, setUrl] = useState("");
  const [stance, setStance] = useState("neutral");
  const [model, setModel] = useState(
    availableModels.length > 0 ? availableModels[0] : ""
  );
  const [requirements, setRequirements] = useState("");
  const [tweetLoading, setTweetLoading] = useState(false);
  const [op, setOp] = useState("");
  const [reply, setReply] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleGenerate = async () => {
    setErrorMessage("");
    setReply("");
    try {
      if (availableCredits <= 0) {
        setTweetLoading(false);
        setErrorMessage(
          "You don't have enough credits. Please purchase more credits."
        );
        return;
      }

      if (!url) {
        setTweetLoading(false);
        setErrorMessage("Tweet URL is required.");
        return;
      }

      if (!op) {
        const opReq = await apiClient.post(
          `/ai/get-tweet-content?tweet_url=${url}`
        );

        setOp(opReq.data.tweet_content);
      }

      const formData = new FormData();
      formData.append("tweet_url", url);
      if (stance) formData.append("choose_sentiment", stance);
      if (model) formData.append("model_name", model);
      if (requirements) formData.append("additional_context", requirements);

      const url =
        betaVersion == "v2"
          ? "/ai/v2/generate-tweet-reply"
          : "/ai/generate-tweet-reply";

      const response = await apiClient.post(url, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setReply(response.data.reply_content);

      // console.log("response", response.data);

      await getUser();
      setErrorMessage("");

      return response.data.reply_content;
    } catch (err) {
      console.log(err);
      setErrorMessage(
        err?.response?.data?.detail ||
          "Failed to generate reply. Please try again later."
      );
    }
  };

  const handlePost = async () => {
    let replyText = reply;
    if (!replyText) {
      replyText = await handleGenerate();
    }
    if (url) {
      const tweetId = url.split("/").pop(); // Extract tweet ID from the URL
      const replyUrl = `https://x.com/intent/tweet?in_reply_to=${encodeURIComponent(
        tweetId || ""
      )}&text=${encodeURIComponent(replyText || "")}`;

      // Create a popup in the center of the screen
      const width = 600;
      const height = 400;
      const left = (window.innerWidth - width) / 2;
      const top = (window.innerHeight - height) / 2;
      window.open(
        replyUrl,
        "_blank",
        `width=${width},height=${height},top=${top},left=${left}`
      );
    }
  };

  return (
    <div className="h-full w-full col-span-2  mx-auto bg-white rounded-2xl border-gray-200 border-1 flex flex-col">
      <div>
        <h2 className="font-medium text-xl mb-1 justify-start flex flex-row border-b-1 p-8 border-gray-200">
          Generate Reply
        </h2>
        <div className="space-y-6 p-8">
          <div>
            <label className=" font-medium mb-2 flex" htmlFor="url">
              Tweet to Reply To
            </label>
            <input
              id="url"
              type="text"
              placeholder="Paste Tweet URL..."
              className={`form-control w-full rounded-xl border-1 ${
                errorMessage ? "border-red-500" : "border-gray-200"
              } focus:outline-none focus:ring-4 focus:ring-gray-200 p-3 bg-gray-100`}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            {errorMessage && (
              <label className="text-sm text-red-500 flex">
                {errorMessage}
              </label>
            )}
          </div>

          <div>
            <label className=" font-medium mb-2 flex gap-1" htmlFor="stance">
              Model
            </label>
            <select
              id="ai-model"
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none p-3 bg-gray-100 focus:ring-4 focus:ring-gray-200"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              {availableModels.map((modelName) => (
                <option key={modelName} value={modelName}>
                  {modelName}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className=" font-medium mb-2 flex gap-1" htmlFor="stance">
              Stance (Optional)
            </label>
            <select
              id="stance"
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-4 focus:ring-gray-200 p-3 bg-gray-100"
              value={stance}
              onChange={(e) => setStance(e.target.value)}
            >
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
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none focus:ring-4 focus:ring-gray-200 p-3 bg-gray-100"
              placeholder=""
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
            />
          </div>

          <div className="flex justify-between">
            <button
              onClick={() => {
                setTweetLoading(true);
                handleGenerate();
              }}
              className="black-btn"
            >
              Generate Reply
            </button>
            <button
              onClick={handlePost}
              className="black-btn bg-[#76b291] hidden "
            >
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
          if (reply || errorMessage) {
            setTweetLoading(false);
            setErrorMessage("");
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

              <div className="mt-8 w-full flex gap-4">
                <button
                  className="black-btn w-full"
                  onClick={() => {
                    setReply("");
                    handleGenerate();
                  }}
                >
                  Regenerate
                </button>
                <button
                  className="black-btn w-full bg-[#76b291] "
                  onClick={handlePost}
                >
                  Post Reply
                </button>
              </div>
            </>
          ) : errorMessage ? (
            <div>{errorMessage}</div>
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

function CreateTweet({
  availableCredits,
  getUser,
  getTweetHistory,
  availableModels,
}) {
  const [topic, setTopic] = useState("");
  const [stance, setStance] = useState("neutral");
  const [model, setModel] = useState(
    availableModels.length > 0 ? availableModels[0] : ""
  );
  const [requirements, setRequirements] = useState("");
  const [tweetLoading, setTweetLoading] = useState(false);
  const [tweet, setTweet] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleGenerate = async () => {
    setErrorMessage("");
    setTweet("");
    try {
      if (availableCredits <= 0) {
        setTweetLoading(false);
        setErrorMessage(
          "You don't have enough credits. Please purchase more credits."
        );
        return;
      }

      if (!topic) {
        setErrorMessage("Topic is required.");
        setTweetLoading(false);
        return;
      }

      const formData = new FormData();
      formData.append("topic", topic);
      if (stance) formData.append("stance", stance);
      if (model) formData.append("model_name", model);
      if (requirements)
        formData.append("additional_requirements", requirements);

      const url =
        betaVersion == "v2" ? "/ai/v2/generate-tweet" : "/ai/generate-tweet";

      const response = await apiClient.post(url, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setTweet(response.data.tweet_content);

      // console.log("response", response.data);

      await getUser();
      setErrorMessage("");

      return response.data.tweet_content;
    } catch (err) {
      console.log(err);
      setErrorMessage(
        err?.response?.data?.detail ||
          "Failed to generate tweet. Please try again later."
      );
    }
  };

  const handlePost = async () => {
    let tweetText = tweet;
    if (!tweetText) {
      tweetText = await handleGenerate();
    }
    const tweetUrl = `https://x.com/intent/tweet?text=${encodeURIComponent(
      tweetText || ""
    )}`;

    // Create a popup in the center of the screen
    const width = 600;
    const height = 400;
    const left = (window.innerWidth - width) / 2;
    const top = (window.innerHeight - height) / 2;
    window.open(
      tweetUrl,
      "_blank",
      `width=${width},height=${height},top=${top},left=${left}`
    );
  };

  return (
    <div className="h-full w-full col-span-2 mx-auto bg-white rounded-2xl border-gray-200 border-1 flex flex-col">
      <div>
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
              className={`form-control w-full rounded-xl border-1 ${
                errorMessage ? "border-red-500" : "border-gray-200"
              } focus:outline-none p-3 bg-gray-100 focus:ring-4 focus:ring-gray-200`}
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
            {errorMessage && (
              <label className="text-sm text-red-500 flex">
                {errorMessage}
              </label>
            )}
          </div>

          <div>
            <label className=" font-medium mb-2 flex gap-1" htmlFor="stance">
              Model
            </label>
            <select
              id="ai-model"
              className="form-control w-full rounded-xl border-1 border-gray-200 focus:outline-none p-3 bg-gray-100 focus:ring-4 focus:ring-gray-200"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              {availableModels.map((modelName) => (
                <option key={modelName} value={modelName}>
                  {modelName}
                </option>
              ))}
            </select>
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

          <div className="flex justify-between">
            <button
              onClick={() => {
                setTweetLoading(true);
                handleGenerate();
              }}
              className="black-btn"
            >
              Generate Tweet
            </button>
            <button className="black-btn bg-[#76b291] hidden">
              Post Tweet
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
          if (tweet || errorMessage) {
            setErrorMessage("");
            setTweetLoading(false);
            setTweet("");
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
          {tweet ? (
            <>
              <p className=" text-left border-1 rounded-xl p-2">{tweet}</p>

              <div className="mt-8 w-full flex gap-4">
                <button
                  className="black-btn w-full"
                  onClick={() => {
                    setTweet("");
                    handleGenerate();
                  }}
                >
                  Regenerate
                </button>
                <button
                  className="black-btn w-full bg-[#76b291] "
                  onClick={handlePost}
                >
                  Post Tweet
                </button>
              </div>
            </>
          ) : errorMessage ? (
            <div>{errorMessage}</div>
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
                  Generating Tweet...
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

export default function TweetPage({
  selectedTab,
  availableCredits,
  getUser,
  tweetHistory,
  getTweetHistory,
  betaVersion,
}) {
  const [availableModels, setAvailableModels] = useState([]);

  useEffect(() => {
    fetchAIModels();
  }, []);

  async function fetchAIModels() {
    const response = await apiClient.get("/ai/get-all-available-model-names");
    setAvailableModels(response.data.model_names);
  }

  return (
    <div className="lg:min-w-2/3 lg:max-w-2/3  mx-auto rounded-2xl flex mt-20">
      {selectedTab === "create" && (
        <motion.div
          key="create"
          initial={{ x: "-50%" }}
          animate={{ x: 0 }}
          transition={{ type: "tween", duration: 0.2 }}
          className="grid grid-cols-3 w-full gap-8 items-stretch"
        >
          <CreateTweet
            availableCredits={availableCredits}
            getUser={getUser}
            getTweetHistory={getTweetHistory}
            availableModels={availableModels}
            betaVersion={betaVersion}
          />
          <RecentTweets tweetHistory={tweetHistory} />
        </motion.div>
      )}
      {selectedTab === "reply" && (
        <motion.div
          key="reply"
          initial={{ x: "50%" }}
          animate={{ x: 0 }}
          transition={{ type: "tween", duration: 0.2 }}
          className="grid grid-cols-3 w-full gap-8 items-stretch"
        >
          <ReplyTweet
            availableCredits={availableCredits}
            getUser={getUser}
            getTweetHistory={getTweetHistory}
            availableModels={availableModels}
            betaVersion={betaVersion}
          />
          <RecentTweets tweetHistory={tweetHistory} />
        </motion.div>
      )}
    </div>
  );
}

function RecentTweets({ tweetHistory }) {
  const [tweets, setTweets] = useState([]);

  useEffect(() => {
    const now = new Date();
    const relativeTweets = tweetHistory.map((tweet) => {
      const diffMs = now.getTime() - new Date(tweet.created_at).getTime();
      const diffMin = Math.floor(diffMs / 60000);

      let relativeTime = "";

      if (diffMin < 60) {
        relativeTime = `${diffMin}m`;
      } else if (diffMin < 1440) {
        const hours = Math.floor(diffMin / 60);
        relativeTime = `${hours}h`;
      } else if (diffMin < 43200) {
        // 30 * 24 * 60
        const days = Math.floor(diffMin / 1440);
        relativeTime = `${days}d`;
      } else if (diffMin < 525600) {
        // 12 * 30 * 24 * 60
        const months = Math.floor(diffMin / 43200);
        relativeTime = `${months}mo`;
      } else {
        const years = Math.floor(diffMin / 525600);
        relativeTime = `${years}y`;
      }

      return { ...tweet, relativeTime };
    });

    setTweets(relativeTweets);
  }, [tweetHistory]);

  return (
    <div className="w-full h-full col-span-1 mx-auto bg-white rounded-2xl border-gray-200 border-1 flex flex-col overflow-y-auto">
      <div className="flex w-full justify-between items center p-6">
        <h1 className="flex font-medium ">Recent Tweets</h1>
        <div className="text-gray-300">{tweets.length} tweets</div>
      </div>
      {tweets &&
        tweets.map((tweet, index) => (
          <div
            key={index}
            className="p-6 text-sm text-black/90 text-left border-t-1 border-gray-200"
          >
            <p className="">{tweet.text}</p>
            <p className="mt-2 text-gray-500">{tweet.relativeTime || ""}</p>
          </div>
        ))}
    </div>
  );
}
