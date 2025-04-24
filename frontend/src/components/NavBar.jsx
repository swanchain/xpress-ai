"use client";
import useConnectX from "@/hooks/useConnectX";
import TwitterIcon from "./TwitterIcon";

export default function Navbar({ user, setUser }) {
  const { connectX, verifyXConnection, connectLoad } = useConnectX();

  const logout = () => {
    localStorage.removeItem("xpress_access_token");
    window.location.reload();
  };

  return (
    <nav className="fixed top-0 left-0 right-0 h-16 bg-white/90 backdrop-blur border-b border-white/20 z-10">
      <div className="container mx-auto px-4 flex items-center justify-between h-full">
        <div className="font-semibold text-xl flex items-center gap-x-2">
          XpressAI
        </div>
        {user ? (
          <nav className="absolute left-1/2 transform -translate-x-1/2 flex bg-black/5 p-1 rounded-[12px]">
            <button className="px-6 py-2 rounded-xl font-medium hover:bg-black/5 active:bg-white shadow-sm">
              Create Tweet
            </button>
            <button className="px-6 py-2 rounded-xl font-medium text-black hover:bg-black/5">
              Generate Reply
            </button>
          </nav>
        ) : (
          <></>
        )}
        <div className="flex items-center space-x-2">
          {/* <button className="hidden md:flex items-center bg-dark text-white px-4 py-2 rounded-xl font-medium">
          🪙 <span className="ml-2">5 Credits</span>
        </button> */}
          {user ? (
            <div onClick={logout}>Logged in as {user.x_screen_name}</div>
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
