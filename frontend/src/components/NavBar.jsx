"use client";
import useConnectX from "@/hooks/useConnectX";
import TwitterIcon from "./TwitterIcon";
import CoinIcon from "./CoinIcon";

export default function Navbar({
  user,
  setUser,
  selectedTab,
  setSelectedTab,
  setShowModal,
}) {
  const { connectX } = useConnectX();

  const logout = () => {
    setUser(null);
    localStorage.removeItem("xpress_access_token");
    window.location.reload();
  };

  return (
    <nav className="fixed top-0 left-0 right-0 h-16 bg-white/90 backdrop-blur border-b border-white/20 z-80">
      <div className="container mx-auto px-4 flex items-center justify-between h-full z-80">
        <div className="font-semibold text-xl flex items-center gap-x-2">
          XpressAI
        </div>
        {user ? (
          <nav className=" flex bg-black/5 p-1 rounded-[12px]">
            <button
              onClick={() => setSelectedTab("create")}
              className={`px-6 py-2 rounded-xl font-medium  ${
                selectedTab == "create" ? "bg-white" : "hover:bg-black/5"
              }`}
            >
              Create Tweet
            </button>
            <button
              onClick={() => setSelectedTab("reply")}
              className={`px-6 py-2 rounded-xl font-medium  ${
                selectedTab == "reply" ? "bg-white" : "hover:bg-black/5"
              }`}
            >
              Generate Reply
            </button>
          </nav>
        ) : (
          <></>
        )}
        <div className="flex items-center space-x-2">
          {user && (
            <button
              className="black-btn text-base"
              onClick={() => setShowModal(true)}
            >
              <span className="flex flex-row justify-center items-center gap-x-2">
                <CoinIcon /> <span className="ml-2">5 Credits</span>
              </span>
            </button>
          )}
          {user && (
            <div className="px-2 font-semibold">{user.x_screen_name}</div>
          )}
          {user ? (
            <button
              className=" px-6 py-3 rounded-[12px] font-semibold hover:cursor-pointer text-base bg-white border-1 border-solid border-black text-black outline-black-1 hover:text-white hover:bg-black transition ease-in-out duration-300"
              onClick={logout}
            >
              <span className="flex flex-row justify-center items-center gap-x-2">
                Logout
              </span>
            </button>
          ) : (
            <button className="black-btn text-base" onClick={connectX}>
              <span className="flex flex-row justify-center items-center gap-x-2">
                <TwitterIcon /> Login with X
              </span>
            </button>
          )}
          <button className="border border-dark text-dark px-4 py-2 rounded-xl font-medium hidden">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
