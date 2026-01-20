import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

interface ResumeInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function ResumeInput({ value, onChange }: ResumeInputProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="resume" className="text-lg font-semibold">
        Resume
      </Label>
      <Textarea
        id="resume"
        placeholder="Paste your resume text here..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="min-h-[200px] resize-y"
      />
    </div>
  );
}
