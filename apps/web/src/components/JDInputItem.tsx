import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { JDCategory, JDInput } from "@/types";

interface JDInputItemProps {
  item: JDInput;
  onUpdate: (id: string, updates: Partial<JDInput>) => void;
  onRemove: (id: string) => void;
  canRemove: boolean;
}

const CATEGORY_OPTIONS: { value: JDCategory; label: string }[] = [
  { value: "required", label: "Required" },
  { value: "preferred", label: "Preferred" },
  { value: "responsibility", label: "Responsibility" },
  { value: "context", label: "Context" },
];

export function JDInputItem({
  item,
  onUpdate,
  onRemove,
  canRemove,
}: JDInputItemProps) {
  return (
    <div className="flex gap-3 items-start p-4 border rounded-lg bg-card">
      <div className="w-40 shrink-0">
        <Select
          value={item.category}
          onValueChange={(value: JDCategory) =>
            onUpdate(item.id, { category: value })
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            {CATEGORY_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex-1">
        <Textarea
          placeholder="Paste JD section text here..."
          value={item.text}
          onChange={(e) => onUpdate(item.id, { text: e.target.value })}
          className="min-h-[100px] resize-y"
        />
      </div>
      {canRemove && (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onRemove(item.id)}
          className="shrink-0 text-destructive hover:text-destructive"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </Button>
      )}
    </div>
  );
}
