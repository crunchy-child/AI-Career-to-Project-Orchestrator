import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResumeInput } from "./ResumeInput";
import { JDInputList } from "./JDInputList";
import type { JDInput, AnalyzeResponse } from "@/types";
import { analyzeResume } from "@/lib/api";

function generateId(): string {
  return Math.random().toString(36).substring(2, 9);
}

function createEmptyJDInput(): JDInput {
  return {
    id: generateId(),
    category: "required",
    text: "",
  };
}

export function AnalyzeForm() {
  const [resumeText, setResumeText] = useState("");
  const [jdInputs, setJdInputs] = useState<JDInput[]>([createEmptyJDInput()]);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAddJDInput = () => {
    setJdInputs([...jdInputs, createEmptyJDInput()]);
  };

  const handleUpdateJDInput = (id: string, updates: Partial<JDInput>) => {
    setJdInputs(
      jdInputs.map((item) =>
        item.id === id ? { ...item, ...updates } : item
      )
    );
  };

  const handleRemoveJDInput = (id: string) => {
    if (jdInputs.length > 1) {
      setJdInputs(jdInputs.filter((item) => item.id !== id));
    }
  };

  const handleSubmit = async () => {
    if (!resumeText.trim()) {
      setError("Please enter your resume text.");
      return;
    }

    const hasJDText = jdInputs.some((item) => item.text.trim());
    if (!hasJDText) {
      setError("Please enter at least one JD section.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeResume({
        resume_text: resumeText,
        jd_inputs: jdInputs.filter((item) => item.text.trim()),
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>AI Career-to-Project Orchestrator</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <ResumeInput value={resumeText} onChange={setResumeText} />
          
          <div className="border-t pt-6">
            <JDInputList
              items={jdInputs}
              onAdd={handleAddJDInput}
              onUpdate={handleUpdateJDInput}
              onRemove={handleRemoveJDInput}
            />
          </div>

          {error && (
            <div className="p-4 bg-destructive/10 text-destructive rounded-lg">
              {error}
            </div>
          )}

          <Button
            onClick={handleSubmit}
            disabled={isLoading}
            className="w-full"
            size="lg"
          >
            {isLoading ? "Analyzing..." : "Analyze"}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Analysis Result</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-2xl font-bold">
                Match Score: {result.gap_summary.match_score}%
              </div>
              <div>
                <h4 className="font-semibold mb-2">Missing Keywords:</h4>
                <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
                  {JSON.stringify(result.gap_summary.validated_missing_keywords, null, 2)}
                </pre>
              </div>
              {result.gap_summary.notes && (
                <div>
                  <h4 className="font-semibold mb-2">Notes:</h4>
                  <p className="text-muted-foreground">{result.gap_summary.notes}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
