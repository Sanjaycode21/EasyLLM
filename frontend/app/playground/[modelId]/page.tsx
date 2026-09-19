import { ChatPlayground } from "@/components/chat/ChatPlayground";

export default function PlaygroundPage({ params }: { params: { modelId: string } }) {
  return (
    <div>
      <ChatPlayground modelId={params.modelId} />
    </div>
  );
}
