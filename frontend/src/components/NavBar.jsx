"use client";
import useConnectX from "@/hooks/useConnectX";
import TwitterIcon from "./TwitterIcon";
import CoinIcon from "./CoinIcon";
import { useDisconnect } from "@reown/appkit/react";
import PersonIcon from "./PersonIcon";
import ChevronDown from "./ChevronDown";
import { useEffect, useState } from "react";
import RobotIcon from "./RobotIcon";
import LogoutIcon from "./LogoutIcon";
import apiClient from "@/services/apiClient";
import CloseIcon from "./CloseIcon";
import Spinner from "./Spinner";

export default function Navbar({
  user,
  setUser,
  selectedTab,
  setSelectedTab,
  setShowModal,
  availableCredits,
}) {
  const { connectX } = useConnectX();
  const { disconnect } = useDisconnect();

  const logout = async () => {
    setUser(null);
    localStorage.removeItem("xpress_access_token");
    await disconnect();
    window.location.reload();
  };

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isAiInfoOpen, setIsAiInfoOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState("");
  const [aiDetails, setAiDetails] = useState({});

  // useEffect(() => {}, [])

  const getUserAIDetails = async () => {
    const response = await apiClient.get("/user/get-user-role-details");
    const details = response.data;
    const parsed = JSON.parse(details.personality_traits);

    setAiDetails({ ...details, parsed_personality_traits: parsed.traits });

    setRefreshError("");
    setIsDropdownOpen(false);
    setIsAiInfoOpen(true);
  };

  const refreshMyVibe = async () => {
    setRefreshError("");
    setIsRefreshing(true);
    try {
      const response = await apiClient.post("/ai-vibe/refresh-my-vibe");
      const details = response.data;
      const parsed = JSON.parse(details.personality_traits);

      setAiDetails({ ...details, parsed_personality_traits: parsed.traits });
    } catch (err) {
      console.log("err", err);
      setRefreshError(err.response?.data?.detail || err.message || "");
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="fixed top-0 left-0 right-0 h-16 bg-white/90 backdrop-blur border-b border-white/20 z-80">
      <div className="container mx-auto px-4 flex items-center justify-between h-full z-80">
        <div className="font-semibold text-xl flex items-center gap-x-2">
          <img src="/chat-bot.png" /> XpressAI
        </div>
        {user ? (
          <div className=" flex bg-black/5 p-1 rounded-[12px]">
            <button
              onClick={() => setSelectedTab("create")}
              className={`px-6 py-2 rounded-xl font-medium  ${
                selectedTab == "create" ? "bg-white" : "hover:bg-black/5"
              }`}
            >
              <span className="hidden sm:block">Create Tweet</span>
              <span className="sm:hidden">Tweet</span>
            </button>
            <button
              onClick={() => setSelectedTab("reply")}
              className={`px-6 py-2 rounded-xl font-medium  ${
                selectedTab == "reply" ? "bg-white" : "hover:bg-black/5"
              }`}
            >
              <span className="hidden sm:block">Generate Reply</span>
              <span className="sm:hidden">Reply</span>
            </button>
          </div>
        ) : (
          <></>
        )}
        <div className="flex items-center space-x-2">
          {user && (
            <button
              className="black-btn text-base"
              onClick={() => setShowModal(true)}
            >
              <span className="sm:flex flex-row justify-center items-center gap-x-2 hidden">
                <CoinIcon />{" "}
                <span className="ml-2">{availableCredits} Credits</span>
              </span>
              <span className="flex flex-row justify-center items-center sm:hidden">
                <CoinIcon /> <span className="ml-2">{availableCredits}</span>
              </span>
            </button>
          )}
          {/* {user && (
            <div className="hidden sm:block px-2 font-semibold">
              {user.x_screen_name}
            </div>
          )} */}
          {user ? (
            <div className="relative">
              <button
                className=" sm:px-6 sm:py-3 p-2 rounded-[12px] font-semibold hover:cursor-pointer text-base bg-gray-100 border-1 border-solid border-black text-black outline-black-1 hover:bg-gray-300 transition ease-in-out duration-300"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              >
                <span className="flex flex-row justify-center items-center gap-x-2">
                  <PersonIcon /> {user.x_screen_name} <ChevronDown />
                </span>
              </button>

              {isDropdownOpen && (
                <div className="absolute right-0 mt-3 lg:w-60 sm:w-fit bg-white/90 rounded-xl shadow-lg z-50">
                  <ul className=" text-gray-700 flex flex-col gap-1">
                    <li
                      onClick={getUserAIDetails}
                      className="p-4 m-2 hover:bg-gray-100 cursor-pointer rounded-xl flex items-center gap-2"
                    >
                      <RobotIcon /> View AI Character
                    </li>
                    <li className=" flex px-4 ">
                      <div className="w-full border-t-1 border-gray-300"></div>
                    </li>
                    <li
                      onClick={logout}
                      className="p-4 m-2 hover:bg-gray-100 cursor-pointer rounded-xl flex items-center gap-2"
                    >
                      <LogoutIcon /> Logout
                    </li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <button className="black-btn text-base" onClick={connectX}>
              <span className="flex flex-row justify-center items-center gap-x-2">
                <TwitterIcon /> Login with X
              </span>
            </button>
          )}
          {/* <button className="border border-dark text-dark px-4 py-2 rounded-xl font-medium hidden">
            Logout
          </button> */}
        </div>
      </div>

      <div
        className={`fixed inset-0 min-h-screen bg-black/50 flex items-start justify-center z-90 ${
          isAiInfoOpen
            ? "opacity-100 pointer-events-auto"
            : "opacity-0 pointer-events-none"
        }`}
        onClick={() => setIsAiInfoOpen(false)}
      >
        <div
          className={`text-display flex flex-col gap-4 my-auto w-2/5 h-2/3  bg-[#f2f2f2] rounded-[20px] p-10 transition-all duration-300 ease-out tranform overflow-y-auto ${
            isAiInfoOpen
              ? "translate-y-0 opacity-100"
              : "-translate-y-40 opacity-0"
          }`}
          onClick={(e) => {
            e.stopPropagation(); // Prevent click from bubbling to outer div
          }}
        >
          <div className="flex w-full justify-between items-center">
            <h1 className="font-semibold text-2xl">AI Character Details</h1>
            <div
              className="hover:cursor-pointer"
              onClick={() => setIsAiInfoOpen(false)}
            >
              <CloseIcon />
            </div>
          </div>
          {/* <div>
            <h1 className="font-semibold text-xl">Name</h1>
            <p className="py-2">{aiDetails.name || ""}</p>
          </div>

          <div>
            <h1 className="font-semibold text-xl">Model</h1>
            <p className="py-2">{aiDetails.model_name || ""}</p>
          </div> */}

          <div>
            <h1 className="font-semibold text-xl">Personality Traits</h1>
            <div className="py-2">
              {aiDetails && aiDetails.personality_traits ? (
                <div className="w-full flex flex-row flex-wrap gap-2">
                  {aiDetails.parsed_personality_traits.map((trait, i) => (
                    <div
                      className={`rounded-full p-2 bg-black/5 w-fit text-sm ${
                        isRefreshing ? "animate-pulse" : ""
                      }`}
                      key={i}
                    >
                      <span className={isRefreshing ? "opacity-0" : ""}>
                        {trait}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                ""
              )}
            </div>
          </div>

          <div>
            <h1 className="font-semibold text-xl">Background Story</h1>
            {isRefreshing ? (
              <div className="flex animate-pulse space-x-4 py-2">
                <div className="flex-1 space-y-6 py-1">
                  <div className="space-y-3">
                    <div className="grid grid-cols-3 gap-4">
                      <div className="col-span-2 h-2 rounded bg-black/5"></div>
                      <div className="col-span-1 h-2 rounded bg-black/5"></div>
                      <div className="col-span-2 h-2 rounded bg-black/5"></div>
                      <div className="col-span-1 h-2 rounded bg-black/5"></div>
                      <div className="col-span-1 h-2 rounded bg-black/5"></div>
                      <div className="col-span-2 h-2 rounded bg-black/5"></div>
                      <div className="col-span-1 h-2 rounded bg-black/5"></div>
                      <div className="col-span-2 h-2 rounded bg-black/5"></div>
                    </div>
                    <div className="h-2 rounded bg-black/5"></div>
                    <div className="h-2 rounded bg-black/5"></div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="py-2">{aiDetails.background_story || ""}</p>
            )}
          </div>

          <div>
            <h1 className="font-semibold text-xl">Category</h1>
            {isRefreshing ? (
              <div className="flex animate-pulse space-x-4 py-2">
                <div className="flex-1 space-y-6 py-1">
                  <div className="h-2 rounded bg-black/5"></div>
                </div>
              </div>
            ) : (
              <p className="py-2">{aiDetails.category || ""}</p>
            )}
          </div>

          <div className="flex items-center justify-end">
            <span className="flex-1 text-sm text-red-600">{refreshError}</span>
            {isRefreshing ? (
              <button className="black-btn hover:">
                <div className="flex flex-row items-center gap-2">
                  <Spinner />{" "}
                  <span className="animate-pulse">Refreshing...</span>
                </div>
              </button>
            ) : (
              <button onClick={refreshMyVibe} className="black-btn">
                Refresh My Vibe
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
