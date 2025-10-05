"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, Plus, X, CheckCircle2, ExternalLink } from "lucide-react";
import { createExperience, CreateExperienceResponse } from "@/lib/api-client";

interface CreateExperienceFormProps {
  onSuccess?: (response: CreateExperienceResponse) => void;
  onCancel?: () => void;
  patients?: string[];
}

export function CreateExperienceForm({ onSuccess, onCancel, patients = [] }: CreateExperienceFormProps) {
  const [selectedPatient, setSelectedPatient] = useState("");
  const [title, setTitle] = useState("");
  const [generalContext, setGeneralContext] = useState("");
  const [scenes, setScenes] = useState<string[]>([""]);
  const [topK, setTopK] = useState(3);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successResponse, setSuccessResponse] = useState<CreateExperienceResponse | null>(null);

  const addScene = () => {
    setScenes([...scenes, ""]);
  };

  const removeScene = (index: number) => {
    if (scenes.length > 1) {
      setScenes(scenes.filter((_, i) => i !== index));
    }
  };

  const updateScene = (index: number, value: string) => {
    const newScenes = [...scenes];
    newScenes[index] = value;
    setScenes(newScenes);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Filter out empty scenes
      const validScenes = scenes.filter(scene => scene.trim() !== "");
      
      if (validScenes.length === 0) {
        throw new Error("Please add at least one scene");
      }

      const response = await createExperience({
        title,
        general_context: generalContext,
        scenes: validScenes,
        top_k: topK,
      });

      setSuccessResponse(response);
      if (onSuccess) {
        onSuccess(response);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create experience");
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedPatient("");
    setTitle("");
    setGeneralContext("");
    setScenes([""]);
    setTopK(3);
    setError(null);
    setSuccessResponse(null);
  };

  if (successResponse) {
    return (
      <Card className="max-w-3xl mx-auto w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-600">
            <CheckCircle2 className="h-6 w-6" />
            Experience Created Successfully!
          </CardTitle>
          <CardDescription>
            Your memory experience has been created and is ready to share
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="bg-slate-50 rounded-lg p-6 space-y-4">
            <div>
              <Label className="text-sm font-semibold text-slate-600">Experience ID</Label>
              <p className="text-lg font-mono mt-1">{successResponse.experience_id}</p>
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600">Title</Label>
              <p className="text-lg mt-1">{successResponse.title}</p>
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600">Patient URL</Label>
              <div className="flex items-center gap-2 mt-1">
                <code className="flex-1 bg-white px-3 py-2 rounded border text-sm">
                  {successResponse.patient_url}
                </code>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e: React.MouseEvent) => {
                    e.preventDefault();
                    window.open(successResponse.patient_url, '_blank');
                  }}
                >
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600">Total Memories Found</Label>
              <p className="text-lg mt-1">{successResponse.total_memories}</p>
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600">Overall Narrative</Label>
              <p className="text-sm mt-1 text-slate-700 leading-relaxed">
                {successResponse.overall_narrative}
              </p>
            </div>
            
            <div>
              <Label className="text-sm font-semibold text-slate-600">Scenes</Label>
              <div className="mt-2 space-y-3">
                {successResponse.scenes.map((scene, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border">
                    <h4 className="font-semibold text-sm mb-2">{scene.scene}</h4>
                    <p className="text-sm text-slate-600 mb-2">{scene.ai_narrative}</p>
                    <p className="text-xs text-slate-500">
                      {scene.memories.length} memories found
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <Button onClick={resetForm} className="flex-1">
              Create Another Experience
            </Button>
            {onCancel && (
              <Button onClick={onCancel} variant="outline" className="flex-1">
                Back to Dashboard
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-3xl mx-auto w-full">
      <CardHeader>
        <CardTitle>Create New Experience</CardTitle>
        <CardDescription>
          Create a memory experience by providing a title, context, and specific scenes
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="patient-select">
              Select Patient <span className="text-red-500">*</span>
            </Label>
            <Select value={selectedPatient} onValueChange={setSelectedPatient}>
              <SelectTrigger id="patient-select">
                <SelectValue placeholder="Choose a patient" />
              </SelectTrigger>
              <SelectContent>
                {patients.map((patient) => (
                  <SelectItem key={patient} value={patient}>
                    {patient}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-500">
              Select the patient for this memory experience
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="title">
              Experience Title <span className="text-red-500">*</span>
            </Label>
            <Input
              id="title"
              placeholder="e.g., Day at the Beach with Anna"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              disabled={isLoading}
            />
            <p className="text-xs text-slate-500">
              A descriptive title for this memory experience
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="context">
              General Context <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="context"
              placeholder="e.g., me and Anna at the beach"
              value={generalContext}
              onChange={(e) => setGeneralContext(e.target.value)}
              required
              disabled={isLoading}
              rows={3}
              className="resize-none"
            />
            <p className="text-xs text-slate-500">
              Provide overall context about the experience
            </p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>
                Scenes <span className="text-red-500">*</span>
              </Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addScene}
                disabled={isLoading}
              >
                <Plus className="h-4 w-4 mr-1" />
                Add Scene
              </Button>
            </div>
            
            <div className="space-y-2">
              {scenes.map((scene, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    placeholder={`Scene ${index + 1}: e.g., holding hands on the beach`}
                    value={scene}
                    onChange={(e) => updateScene(index, e.target.value)}
                    disabled={isLoading}
                    className="flex-1"
                  />
                  {scenes.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeScene(index)}
                      disabled={isLoading}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-500">
              Add specific scenes or moments from the experience
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="topk">
              Number of Memories per Scene (top_k)
            </Label>
            <Input
              id="topk"
              type="number"
              min={1}
              max={10}
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value) || 3)}
              disabled={isLoading}
            />
            <p className="text-xs text-slate-500">
              How many relevant memories to retrieve for each scene (default: 3)
            </p>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              disabled={isLoading || !selectedPatient || !title.trim() || !generalContext.trim()}
              className="flex-1"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating Experience...
                </>
              ) : (
                "Create Experience"
              )}
            </Button>
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                Cancel
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
