import { createFileRoute } from "@tanstack/react-router";
import FormPresigned from "../components/FormPresigned";

export const Route = createFileRoute("/")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <main className="grid place-items-center pt-8 lg:pt-16">
      <FormPresigned />
    </main>
  );
}
