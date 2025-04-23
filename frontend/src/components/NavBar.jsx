"use client";

import { useAppKitAccount } from "@reown/appkit/react";
import { useRouter } from "next/navigation";

export function Navbar() {
  const { address, isConnected } = useAppKitAccount();
  const router = useRouter();

  return (
    <nav className="flex items-center justify-between px-6 py-4 bg-black shadow-md">
      <div
        className="text-xl font-bold text-white"
        onClick={() => router.push("/")}
      >
        Xpress.ai
      </div>
      <div className="flex items-center gap-4">
        {isConnected && <w3m-network-button />}
        {isConnected ? (
          //   <div onClick={() => router.push("/account")} className="text-white">
          //     avatar
          //   </div>
          <w3m-button />
        ) : (
          <w3m-button />
        )}
      </div>
    </nav>
  );
}
