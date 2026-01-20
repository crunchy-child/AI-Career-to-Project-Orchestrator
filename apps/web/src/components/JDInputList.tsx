import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { JDInputItem } from "./JDInputItem";
import type { JDInput } from "@/types";

interface JDInputListProps {
  items: JDInput[];
  onAdd: () => void;
  onUpdate: (id: string, updates: Partial<JDInput>) => void;
  onRemove: (id: string) => void;
}

export function JDInputList({
  items,
  onAdd,
  onUpdate,
  onRemove,
}: JDInputListProps) {
  return (
    <div className="space-y-4">
      <Label className="text-lg font-semibold">Job Description</Label>
      <div className="space-y-3">
        {items.map((item) => (
          <JDInputItem
            key={item.id}
            item={item}
            onUpdate={onUpdate}
            onRemove={onRemove}
            canRemove={items.length > 1}
          />
        ))}
      </div>
      <Button variant="outline" onClick={onAdd} className="w-full">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="mr-2"
        >
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        Add JD Section
      </Button>
    </div>
  );
}
