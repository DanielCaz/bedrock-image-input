import * as React from "react";
import { Outlet, createRootRoute } from "@tanstack/react-router";

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <React.Fragment>
      <div className="navbar bg-base-300 shadow-sm">
        <h1 className="btn btn-ghost text-xl">Bedrock Image</h1>
      </div>
      <Outlet />
    </React.Fragment>
  );
}
