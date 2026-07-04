"use client";

import Sidebar from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import BriefingHero from "@/components/BriefingHero";
import TaskList from "@/components/TaskList";
import HabitRow from "@/components/HabitRow";
import GoalRow from "@/components/GoalRow";
import NotesGrid from "@/components/NotesGrid";
import VoiceOrb from "@/components/VoiceOrb";

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col pb-40">
        <TopBar />
        <main className="px-6 md:px-10 flex flex-col gap-6 max-w-5xl">
          <BriefingHero />
          <div className="grid md:grid-cols-2 gap-6">
            <TaskList />
            <div className="flex flex-col gap-6">
              <HabitRow />
              <GoalRow />
            </div>
          </div>
          <NotesGrid />
        </main>
      </div>
      <VoiceOrb />
    </div>
  );
}
