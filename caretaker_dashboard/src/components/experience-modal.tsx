"use client";
import { useState, useEffect } from "react";
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface ExperienceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ExperienceModal({ isOpen, onClose }: ExperienceModalProps) {
  const router = useRouter();
  const [isAnimating, setIsAnimating] = useState(false);
  
  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
    }
  }, [isOpen]);
  
  if (!isOpen) return null;
  
  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center transition-opacity duration-200 ${isAnimating ? 'opacity-100' : 'opacity-0'}`}>
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className={`relative z-50 w-full max-w-md aspect-square mx-4 transition-all duration-200 ease-out ${isAnimating ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}`}>
        <Card className="bg-white shadow-2xl h-full flex flex-col border-0">
          <CardHeader>
            <CardTitle>Add New Experience</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex items-center">
            <div className="grid grid-cols-1 gap-4 w-full">
              <div className="grid gap-2">
                <Label htmlFor="name">User Name</Label>
                <Input id="name" name="name" placeholder="e.g., Alex Johnson" />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="video">Video File</Label>
                <Input id="video" name="video" type="file" accept="video/*" />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="title">Video Title</Label>
                <Input id="title" name="title" placeholder="e.g., Morning Walk" />
              </div>
              
              <div className="flex gap-2">
                <Button
                  type="button"
                  onClick={() => {
                    onClose();
                    router.push('/face-naming');
                  }}
                  className="bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 hover:from-blue-600 hover:via-purple-600 hover:to-indigo-700 text-white flex-1 transition-all duration-150"
                >
                  Push to User Dashboard
                </Button>
                <Button type="button" variant="outline" onClick={onClose} className="transition-all duration-150">
                  Cancel
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}